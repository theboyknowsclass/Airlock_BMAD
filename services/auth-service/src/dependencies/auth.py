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

