"""
API Key request/response models
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class APIKeyCreateRequest(BaseModel):
    """API key creation request model"""
    scopes: List[str] = Field(..., description="List of scopes (e.g., read-only, read-write, admin)")
    permissions: List[str] = Field(..., description="List of permissions")
    expires_in_days: Optional[int] = Field(None, ge=1, description="Expiration in days (None = no expiration)")


class APIKeyResponse(BaseModel):
    """API key response model"""
    id: int
    scopes: List[str]
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeyWithKeyResponse(BaseModel):
    """API key response model including the plain text key (only returned on creation/rotation)"""
    id: int
    key: str  # Plain text key (only shown once)
    scopes: List[str]
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """API key list response model"""
    keys: List[APIKeyResponse]
    total: int
    skip: int
    limit: int


class APIKeyRotateRequest(BaseModel):
    """API key rotation request model"""
    scopes: Optional[List[str]] = Field(None, description="New scopes (if None, uses existing)")
    permissions: Optional[List[str]] = Field(None, description="New permissions (if None, uses existing)")
    expires_in_days: Optional[int] = Field(None, ge=1, description="New expiration in days (if None, uses existing)")

