"""
Dependencies for User Management Service
"""
from .database import get_db_session

# Import auth dependencies from auth-service
# Note: In production, this could be a shared library or service-to-service auth
# We use lazy import to avoid path conflicts during module loading
_auth_deps_loaded = False
get_current_user = None
require_admin = None
UserContext = None

def _load_auth_dependencies():
    """Lazy load auth dependencies to avoid import conflicts"""
    global _auth_deps_loaded, get_current_user, require_admin, UserContext
    if _auth_deps_loaded:
        return
    
    try:
        import sys
        from pathlib import Path
        
        # Get the project root
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent.parent
        auth_service_parent = project_root / "services" / "auth-service"
        
        # Temporarily add auth-service parent to path
        auth_service_parent_str = str(auth_service_parent.resolve())
        was_in_path = auth_service_parent_str in sys.path
        if not was_in_path:
            sys.path.insert(0, auth_service_parent_str)
        
        try:
            # Import using absolute path to avoid conflicts
            import importlib
            auth_module = importlib.import_module("src.dependencies.auth")
            get_current_user = auth_module.get_current_user
            require_admin = auth_module.require_admin
            UserContext = auth_module.UserContext
            _auth_deps_loaded = True
        finally:
            # Remove from path if we added it
            if not was_in_path and auth_service_parent_str in sys.path:
                sys.path.remove(auth_service_parent_str)
    except (ImportError, Exception) as e:
        # Fallback: create minimal auth dependencies if auth-service not available
        import logging
        logger = logging.getLogger(__name__)
        import traceback
        logger.warning(f"Could not import auth-service dependencies: {e}. Using fallback.")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        from fastapi import Depends, HTTPException, status
        from fastapi.security import HTTPBearer
        from typing import List, Optional
        
        security = HTTPBearer()
        
        class UserContext:
            """Minimal UserContext for testing"""
            def __init__(self, user_id: str, username: str, roles: List[str]):
                self.user_id = user_id
                self.username = username
                self.roles = roles
        
        async def get_current_user_fallback(
            credentials = Depends(security),
        ) -> UserContext:
            """Minimal auth for testing - raises error"""
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Authentication not configured. Please ensure auth-service dependencies are available.",
            )
        
        def require_admin_fallback():
            """Minimal admin requirement for testing"""
            async def admin_checker(current_user: UserContext = Depends(get_current_user_fallback)):
                return current_user
            return admin_checker
        
        get_current_user = get_current_user_fallback
        require_admin = require_admin_fallback
        UserContext = UserContext
        _auth_deps_loaded = True

# Load auth dependencies on first access
_load_auth_dependencies()

__all__ = [
    "get_db_session",
    "get_current_user",
    "require_admin",
    "UserContext",
]
