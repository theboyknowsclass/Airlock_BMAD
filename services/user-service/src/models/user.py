"""
User request/response models
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: str
    roles: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response model"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class UserUpdateRequest(BaseModel):
    """User update request model"""
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class UserRolesUpdateRequest(BaseModel):
    """User roles update request model"""
    roles: List[str] = Field(..., min_items=0)


class UserCreateRequest(BaseModel):
    """User create request model"""
    username: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    roles: List[str] = Field(default_factory=list)

