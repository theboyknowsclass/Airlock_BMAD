"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from ..utils.jwt import decode_token
from ..config import settings
import logging

try:
    from airlock_common.constants.roles import ROLE_SUBMITTER, ROLE_REVIEWER, ROLE_ADMIN
except ImportError:
    # Fallback if shared library is not available
    ROLE_SUBMITTER = "submitter"
    ROLE_REVIEWER = "reviewer"
    ROLE_ADMIN = "admin"

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()


class UserContext:
    """
    User context extracted from JWT token
    """
    def __init__(
        self,
        user_id: str,
        username: str,
        roles: List[str],
        scope: Optional[str] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.roles = roles
        self.scope = scope
    
    def __repr__(self) -> str:
        return f"<UserContext(user_id={self.user_id}, username={self.username}, roles={self.roles})>"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserContext:
    """
    FastAPI dependency to validate JWT token and extract user context
    
    Extracts token from Authorization header, validates signature and expiration,
    and returns user context with user_id, username, and roles.
    
    Args:
        credentials: HTTP Bearer token credentials from Authorization header
    
    Returns:
        UserContext: User context extracted from token claims
    
    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or missing
    """
    token = credentials.credentials
    
    if not token:
        logger.warning("No token provided in Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode and validate token (signature and expiration are checked)
        token_data = decode_token(token)
        
        # Verify token type is access token (not refresh token)
        token_type = token_data.get("type")
        if token_type != "access":
            logger.warning(f"Invalid token type: {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Access token required.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user information from token claims
        user_id = token_data.get("sub")
        username = token_data.get("username")
        roles = token_data.get("roles", [])
        scope = token_data.get("scope")
        
        # Validate required claims
        if not user_id:
            logger.warning("No user ID in token claims")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not username:
            # Fallback to user_id if username is not present
            username = user_id
        
        if not roles:
            # Default to submitter role if no roles specified
            roles = ["submitter"]
            logger.warning(f"No roles in token for user {user_id}, defaulting to submitter")
        
        # Create and return user context
        user_context = UserContext(
            user_id=user_id,
            username=username,
            roles=roles,
            scope=scope,
        )
        
        logger.debug(f"Authenticated user: {username} ({user_id}) with roles: {roles}")
        return user_context
        
    except HTTPException:
        # Re-raise HTTPException to preserve specific error messages
        raise
    except JWTError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[UserContext]:
    """
    Optional authentication dependency
    
    Similar to get_current_user but returns None if no token is provided.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Bearer token credentials
    
    Returns:
        UserContext if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """
    FastAPI dependency factory to require a specific role
    
    Creates a dependency that checks if the user has the required role.
    Raises 403 Forbidden if the user doesn't have the role.
    
    Args:
        required_role: The role that is required (e.g., "submitter", "reviewer", "admin")
    
    Returns:
        Dependency function that validates role and returns UserContext
    
    Example:
        @router.get("/submission")
        async def submission_endpoint(
            user: UserContext = Depends(require_role("submitter"))
        ):
            ...
    """
    async def role_checker(
        current_user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        """
        Check if user has the required role
        
        Args:
            current_user: User context from authentication
        
        Returns:
            UserContext if user has required role
        
        Raises:
            HTTPException: 403 Forbidden if user doesn't have required role
        """
        user_roles = current_user.roles or []
        
        # Admins can access all endpoints
        if ROLE_ADMIN in user_roles:
            logger.debug(
                f"User {current_user.user_id} ({current_user.username}) "
                f"has admin role, granting access to endpoint requiring role '{required_role}'"
            )
            return current_user
        
        if required_role not in user_roles:
            logger.warning(
                f"User {current_user.user_id} ({current_user.username}) "
                f"attempted to access endpoint requiring role '{required_role}'. "
                f"User has roles: {user_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )
        
        logger.debug(
            f"User {current_user.user_id} ({current_user.username}) "
            f"has required role '{required_role}'"
        )
        return current_user
    
    return role_checker


def require_any_role(*required_roles: str):
    """
    FastAPI dependency factory to require at least one of the specified roles
    
    Creates a dependency that checks if the user has at least one of the required roles.
    Raises 403 Forbidden if the user doesn't have any of the roles.
    
    Args:
        *required_roles: One or more roles that are acceptable
    
    Returns:
        Dependency function that validates role and returns UserContext
    
    Example:
        @router.get("/workflow")
        async def workflow_endpoint(
            user: UserContext = Depends(require_any_role("reviewer", "admin"))
        ):
            ...
    """
    async def role_checker(
        current_user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        """
        Check if user has at least one of the required roles
        
        Args:
            current_user: User context from authentication
        
        Returns:
            UserContext if user has at least one required role
        
        Raises:
            HTTPException: 403 Forbidden if user doesn't have any required role
        """
        user_roles = current_user.roles or []
        
        # Admins can access all endpoints
        if ROLE_ADMIN in user_roles:
            logger.debug(
                f"User {current_user.user_id} ({current_user.username}) "
                f"has admin role, granting access to endpoint requiring one of roles {required_roles}"
            )
            return current_user
        
        required_roles_set = set(required_roles)
        user_roles_set = set(user_roles)
        
        if not required_roles_set.intersection(user_roles_set):
            logger.warning(
                f"User {current_user.user_id} ({current_user.username}) "
                f"attempted to access endpoint requiring one of roles {required_roles}. "
                f"User has roles: {user_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required one of roles: {', '.join(required_roles)}",
            )
        
        logger.debug(
            f"User {current_user.user_id} ({current_user.username}) "
            f"has at least one required role from {required_roles}"
        )
        return current_user
    
    return role_checker


def require_all_roles(*required_roles: str):
    """
    FastAPI dependency factory to require all of the specified roles
    
    Creates a dependency that checks if the user has all of the required roles.
    Raises 403 Forbidden if the user doesn't have all roles.
    
    Args:
        *required_roles: One or more roles that are all required
    
    Returns:
        Dependency function that validates role and returns UserContext
    
    Example:
        @router.get("/admin-only")
        async def admin_endpoint(
            user: UserContext = Depends(require_all_roles("admin", "reviewer"))
        ):
            ...
    """
    async def role_checker(
        current_user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        """
        Check if user has all of the required roles
        
        Args:
            current_user: User context from authentication
        
        Returns:
            UserContext if user has all required roles
        
        Raises:
            HTTPException: 403 Forbidden if user doesn't have all required roles
        """
        user_roles = current_user.roles or []
        
        # Admins can access all endpoints
        if ROLE_ADMIN in user_roles:
            logger.debug(
                f"User {current_user.user_id} ({current_user.username}) "
                f"has admin role, granting access to endpoint requiring all roles {required_roles}"
            )
            return current_user
        
        required_roles_set = set(required_roles)
        user_roles_set = set(user_roles)
        
        if not required_roles_set.issubset(user_roles_set):
            missing_roles = required_roles_set - user_roles_set
            logger.warning(
                f"User {current_user.user_id} ({current_user.username}) "
                f"attempted to access endpoint requiring all roles {required_roles}. "
                f"User has roles: {user_roles}. Missing: {missing_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required all roles: {', '.join(required_roles)}. "
                       f"Missing: {', '.join(missing_roles)}",
            )
        
        logger.debug(
            f"User {current_user.user_id} ({current_user.username}) "
            f"has all required roles: {required_roles}"
        )
        return current_user
    
    return role_checker


# Convenience functions for common role requirements
def require_submitter():
    """Convenience function to require submitter role"""
    return require_role(ROLE_SUBMITTER)


def require_reviewer():
    """Convenience function to require reviewer role"""
    return require_role(ROLE_REVIEWER)


def require_admin():
    """Convenience function to require admin role"""
    return require_role(ROLE_ADMIN)

