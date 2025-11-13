"""
API Key authentication router
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..dependencies import get_db_session
from ..services import APIKeyService
from ..models import TokenResponse
from ..config import settings
from airlock_common import JWTConfig, create_api_key_access_token, create_api_key_refresh_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def authenticate_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key", description="API key for authentication"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Authenticate API key and issue JWT tokens
    
    Accepts API key in X-API-Key header, validates it, and returns JWT access and refresh tokens.
    The tokens include the API key's scopes and permissions.
    """
    # Check if API key header is provided
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Provide it in X-API-Key header.",
        )
    
    api_key_service = APIKeyService(session)
    
    try:
        # Find API key by plain text key (validates hash)
        api_key = await api_key_service.find_api_key_by_plain_key(x_api_key)
        
        if not api_key:
            logger.warning("API key authentication failed: key not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        
        # Check if key is expired
        if api_key_service.is_key_expired(api_key):
            logger.warning(f"API key authentication failed: key {api_key.id} is expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )
        
        # Parse scopes and permissions from JSON strings
        scopes = json.loads(api_key.scopes)
        permissions = json.loads(api_key.permissions)
        
        # Create JWT config and tokens
        jwt_config = JWTConfig(
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            issuer=settings.JWT_ISSUER,
            access_token_expiry_minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES,
            refresh_token_expiry_days=settings.REFRESH_TOKEN_EXPIRY_DAYS,
        )
        access_token = create_api_key_access_token(
            config=jwt_config,
            api_key_id=api_key.id,
            scopes=scopes,
            permissions=permissions,
        )
        refresh_token = create_api_key_refresh_token(
            config=jwt_config,
            api_key_id=api_key.id,
            scopes=scopes,
            permissions=permissions,
        )
        
        logger.info(f"API key {api_key.id} authenticated successfully")
        
        # Calculate expires_in (seconds)
        expires_in = settings.ACCESS_TOKEN_EXPIRY_MINUTES * 60
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate API key",
        )

