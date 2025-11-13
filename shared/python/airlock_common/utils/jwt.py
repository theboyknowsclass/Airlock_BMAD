"""
Shared JWT token utilities for Airlock services

This module provides common JWT token creation and validation functions
that can be used across all Airlock services to avoid code duplication.
"""
import secrets
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Optional, Union
import jwt
from jwt import InvalidTokenError, DecodeError, ExpiredSignatureError
import logging

logger = logging.getLogger(__name__)


class JWTConfig:
    """Configuration for JWT operations"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        issuer: str = "airlock",
        access_token_expiry_minutes: int = 15,
        refresh_token_expiry_days: int = 7,
    ):
        """
        Initialize JWT configuration
        
        Args:
            secret_key: JWT secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            issuer: JWT issuer identifier
            access_token_expiry_minutes: Access token expiry in minutes
            refresh_token_expiry_days: Refresh token expiry in days
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.access_token_expiry_minutes = access_token_expiry_minutes
        self.refresh_token_expiry_days = refresh_token_expiry_days


def create_access_token(
    config: JWTConfig,
    subject: str,
    username: Optional[str] = None,
    roles: Optional[List[str]] = None,
    scopes: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    scope: Optional[str] = None,  # Legacy OAuth2 scope parameter
    api_key_id: Optional[int] = None,
    auth_type: Optional[str] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token
    
    Supports both user-based and API key-based tokens.
    
    Args:
        config: JWT configuration
        subject: Token subject (user_id or "api-key-{id}")
        username: Username (for user tokens)
        roles: List of roles (for user tokens)
        scopes: List of scopes (for API key tokens)
        permissions: List of permissions (for API key tokens)
        scope: Legacy OAuth2 scope string (for user tokens)
        api_key_id: API key ID (for API key tokens)
        auth_type: Authentication type ("api_key" or None for user)
        additional_claims: Additional custom claims to include
    
    Returns:
        JWT access token string
    """
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=config.access_token_expiry_minutes)
    
    # Convert datetime to timestamp for JWT
    exp_timestamp = int(expires_at.timestamp())
    iat_timestamp = int(now.timestamp())
    
    claims: Dict[str, Any] = {
        "sub": subject,
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": config.issuer,
        "type": "access",
    }
    
    # Add user-specific claims
    if username:
        claims["username"] = username
    if roles:
        claims["roles"] = roles
    if scope:
        claims["scope"] = scope
    
    # Add API key-specific claims
    if api_key_id is not None:
        claims["api_key_id"] = api_key_id
    if scopes:
        claims["scopes"] = scopes
    if permissions:
        claims["permissions"] = permissions
    if auth_type:
        claims["auth_type"] = auth_type
    
    # Add any additional claims
    if additional_claims:
        claims.update(additional_claims)
    
    token = jwt.encode(
        claims,
        config.secret_key,
        algorithm=config.algorithm,
    )
    
    return token


def create_refresh_token(
    config: JWTConfig,
    subject: str,
    username: Optional[str] = None,
    roles: Optional[List[str]] = None,
    scopes: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    scope: Optional[str] = None,  # Legacy OAuth2 scope parameter
    api_key_id: Optional[int] = None,
    auth_type: Optional[str] = None,
    include_jti: bool = True,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create JWT refresh token
    
    Supports both user-based and API key-based tokens.
    
    Args:
        config: JWT configuration
        subject: Token subject (user_id or "api-key-{id}")
        username: Username (for user tokens)
        roles: List of roles (for user tokens)
        scopes: List of scopes (for API key tokens)
        permissions: List of permissions (for API key tokens)
        scope: Legacy OAuth2 scope string (for user tokens)
        api_key_id: API key ID (for API key tokens)
        auth_type: Authentication type ("api_key" or None for user)
        include_jti: Whether to include JTI (token ID) for rotation tracking
        additional_claims: Additional custom claims to include
    
    Returns:
        JWT refresh token string
    """
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=config.refresh_token_expiry_days)
    
    # Generate unique token ID for rotation tracking
    if include_jti:
        token_id = secrets.token_urlsafe(32)
    
    # Convert datetime to timestamp for JWT
    exp_timestamp = int(expires_at.timestamp())
    iat_timestamp = int(now.timestamp())
    
    claims: Dict[str, Any] = {
        "sub": subject,
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": config.issuer,
        "type": "refresh",
    }
    
    # Add JTI for token rotation
    if include_jti:
        claims["jti"] = token_id
    
    # Add user-specific claims
    if username:
        claims["username"] = username
    if roles:
        claims["roles"] = roles
    if scope:
        claims["scope"] = scope
    
    # Add API key-specific claims
    if api_key_id is not None:
        claims["api_key_id"] = api_key_id
    if scopes:
        claims["scopes"] = scopes
    if permissions:
        claims["permissions"] = permissions
    if auth_type:
        claims["auth_type"] = auth_type
    
    # Add any additional claims
    if additional_claims:
        claims.update(additional_claims)
    
    token = jwt.encode(
        claims,
        config.secret_key,
        algorithm=config.algorithm,
    )
    
    return token


def decode_token(
    token: str,
    config: JWTConfig,
    verify_iss: bool = True,
) -> Dict[str, Any]:
    """
    Decode and validate JWT token
    
    This is the common token decoding function used across all services.
    
    Args:
        token: JWT token string
        config: JWT configuration
        verify_iss: Whether to verify issuer (default: True)
    
    Returns:
        Decoded token claims
    
    Raises:
        InvalidTokenError: If token is invalid
        DecodeError: If token cannot be decoded
        ExpiredSignatureError: If token is expired
    """
    try:
        payload = jwt.decode(
            token,
            config.secret_key,
            algorithms=[config.algorithm],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": verify_iss,
            },
            issuer=config.issuer if verify_iss else None,
        )
        return payload
    except (InvalidTokenError, DecodeError, ExpiredSignatureError) as e:
        logger.warning(f"Token decode failed: {e}")
        raise


# Convenience functions for common token types

def create_user_access_token(
    config: JWTConfig,
    user_id: str,
    username: str,
    roles: List[str],
    scope: Optional[str] = None,
) -> str:
    """
    Create access token for a user
    
    Convenience function for user-based authentication.
    
    Args:
        config: JWT configuration
        user_id: User ID
        username: Username
        roles: List of user roles
        scope: Optional OAuth2 scope
    
    Returns:
        JWT access token
    """
    return create_access_token(
        config=config,
        subject=user_id,
        username=username,
        roles=roles,
        scope=scope,
    )


def create_user_refresh_token(
    config: JWTConfig,
    user_id: str,
    username: Optional[str] = None,
    roles: Optional[List[str]] = None,
    scope: Optional[str] = None,
) -> str:
    """
    Create refresh token for a user
    
    Convenience function for user-based authentication.
    
    Args:
        config: JWT configuration
        user_id: User ID
        username: Username (optional, for token rotation)
        roles: List of user roles (optional, for token rotation)
        scope: Optional OAuth2 scope
    
    Returns:
        JWT refresh token
    """
    return create_refresh_token(
        config=config,
        subject=user_id,
        username=username,
        roles=roles,
        scope=scope,
    )


def create_api_key_access_token(
    config: JWTConfig,
    api_key_id: int,
    scopes: List[str],
    permissions: List[str],
) -> str:
    """
    Create access token for an API key
    
    Convenience function for API key-based authentication.
    
    Args:
        config: JWT configuration
        api_key_id: API key ID
        scopes: List of scopes
        permissions: List of permissions
    
    Returns:
        JWT access token
    """
    subject = f"api-key-{api_key_id}"
    return create_access_token(
        config=config,
        subject=subject,
        api_key_id=api_key_id,
        scopes=scopes,
        permissions=permissions,
        auth_type="api_key",
    )


def create_api_key_refresh_token(
    config: JWTConfig,
    api_key_id: int,
    scopes: List[str],
    permissions: List[str],
) -> str:
    """
    Create refresh token for an API key
    
    Convenience function for API key-based authentication.
    
    Args:
        config: JWT configuration
        api_key_id: API key ID
        scopes: List of scopes
        permissions: List of permissions
    
    Returns:
        JWT refresh token
    """
    subject = f"api-key-{api_key_id}"
    return create_refresh_token(
        config=config,
        subject=subject,
        api_key_id=api_key_id,
        scopes=scopes,
        permissions=permissions,
        auth_type="api_key",
        include_jti=False,  # API keys don't need JTI for rotation
    )

