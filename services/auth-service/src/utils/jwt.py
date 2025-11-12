"""
JWT token utilities for Authentication Service
"""
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from jose import jwt, JWTError
import logging

from ..config import settings

logger = logging.getLogger(__name__)


def create_access_token(
    user_id: str,
    username: str,
    roles: List[str],
    scope: Optional[str] = None,
) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User ID
        username: Username
        roles: List of user roles
        scope: Optional scope
    
    Returns:
        JWT access token
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES)
    
    # Convert datetime to timestamp for JWT
    exp_timestamp = int(expires_at.timestamp())
    iat_timestamp = int(now.timestamp())
    
    claims: Dict[str, Any] = {
        "sub": user_id,
        "username": username,
        "roles": roles,
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    
    if scope:
        claims["scope"] = scope
    
    token = jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return token


def create_refresh_token(
    user_id: str,
    username: str,
    roles: List[str],
    scope: Optional[str] = None,
) -> str:
    """
    Create JWT refresh token
    
    Args:
        user_id: User ID
        username: Username
        roles: List of user roles
        scope: Optional scope
    
    Returns:
        JWT refresh token
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
    
    # Generate unique token ID for rotation tracking
    token_id = secrets.token_urlsafe(32)
    
    # Convert datetime to timestamp for JWT
    exp_timestamp = int(expires_at.timestamp())
    iat_timestamp = int(now.timestamp())
    
    claims: Dict[str, Any] = {
        "sub": user_id,
        "username": username,
        "roles": roles,
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": settings.JWT_ISSUER,
        "type": "refresh",
        "jti": token_id,  # Token ID for rotation tracking
    }
    
    if scope:
        claims["scope"] = scope
    
    token = jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return token


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token
    
    Returns:
        Decoded token claims
    
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": True, "verify_exp": True},
        )
        return payload
    except JWTError as e:
        logger.error(f"Failed to decode token: {e}")
        raise JWTError(f"Invalid token: {e}")

