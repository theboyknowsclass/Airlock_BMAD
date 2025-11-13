"""
API Key management router
"""
import json
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session, get_current_user, require_admin, UserContext
from ..services import APIKeyService
from ..models import (
    APIKeyCreateRequest,
    APIKeyResponse,
    APIKeyListResponse,
    APIKeyWithKeyResponse,
    APIKeyRotateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/keys", tags=["api-keys"])


@router.post("", response_model=APIKeyWithKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreateRequest,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Create a new API key (admin only)
    
    Generates a secure API key, hashes it, and stores it in the database.
    The plain text key is returned only once - store it securely.
    """
    api_key_service = APIKeyService(session)
    
    try:
        api_key, plain_key = await api_key_service.create_api_key(
            scopes=key_data.scopes,
            permissions=key_data.permissions,
            expires_in_days=key_data.expires_in_days,
        )
        
        logger.info(
            f"Admin user {current_user.user_id} created API key with ID {api_key.id}"
        )
        
        return APIKeyWithKeyResponse(
            id=api_key.id,
            key=plain_key,
            scopes=json.loads(api_key.scopes),
            permissions=json.loads(api_key.permissions),
            created_at=api_key.created_at,
            expires_at=api_key.expires_at,
        )
    
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        )


@router.get("", response_model=APIKeyListResponse)
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    List all API keys (admin only)
    
    Returns paginated list of all API keys in the system.
    Note: Plain text keys are never returned - only metadata.
    """
    api_key_service = APIKeyService(session)
    
    try:
        api_keys = await api_key_service.get_all_api_keys(skip=skip, limit=limit)
        
        # Get total count (simplified - in production, use count query)
        all_keys = await api_key_service.get_all_api_keys(skip=0, limit=10000)
        total = len(all_keys)
        
        return APIKeyListResponse(
            keys=[
                APIKeyResponse(
                    id=key.id,
                    scopes=json.loads(key.scopes),
                    permissions=json.loads(key.permissions),
                    created_at=key.created_at,
                    expires_at=key.expires_at,
                )
                for key in api_keys
            ],
            total=total,
            skip=skip,
            limit=limit,
        )
    
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys",
        )


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: int,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get API key by ID (admin only)
    
    Returns API key metadata (not the plain text key).
    """
    api_key_service = APIKeyService(session)
    
    api_key = await api_key_service.get_api_key_by_id(key_id)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with ID {key_id} not found",
        )
    
    return APIKeyResponse(
        id=api_key.id,
        scopes=json.loads(api_key.scopes),
        permissions=json.loads(api_key.permissions),
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Revoke an API key (admin only)
    
    Permanently deletes the API key from the database.
    """
    api_key_service = APIKeyService(session)
    
    success = await api_key_service.revoke_api_key(key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with ID {key_id} not found",
        )
    
    logger.info(
        f"Admin user {current_user.user_id} revoked API key with ID {key_id}"
    )


@router.post("/{key_id}/rotate", response_model=APIKeyWithKeyResponse)
async def rotate_api_key(
    key_id: int,
    rotate_data: APIKeyRotateRequest,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Rotate an API key (admin only)
    
    Revokes the old API key and creates a new one with the same or updated
    scopes/permissions. The new plain text key is returned only once.
    """
    api_key_service = APIKeyService(session)
    
    try:
        new_key, plain_key = await api_key_service.rotate_api_key(
            key_id=key_id,
            scopes=rotate_data.scopes,
            permissions=rotate_data.permissions,
            expires_in_days=rotate_data.expires_in_days,
        )
        
        if not new_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key with ID {key_id} not found",
            )
        
        logger.info(
            f"Admin user {current_user.user_id} rotated API key: "
            f"revoked {key_id}, created {new_key.id}"
        )
        
        return APIKeyWithKeyResponse(
            id=new_key.id,
            key=plain_key,
            scopes=json.loads(new_key.scopes),
            permissions=json.loads(new_key.permissions),
            created_at=new_key.created_at,
            expires_at=new_key.expires_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rotating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rotate API key",
        )

