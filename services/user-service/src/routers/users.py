"""
User management router
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session, get_current_user, require_admin, UserContext
from ..services import UserService, AuditService
from ..models import (
    UserResponse,
    UserListResponse,
    UserUpdateRequest,
    UserRolesUpdateRequest,
    UserCreateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    List all users (admin only)
    
    Returns paginated list of all users in the system.
    """
    user_service = UserService(session)
    users = await user_service.get_all_users(skip=skip, limit=limit)
    
    # Get total count (simplified - in production, use count query)
    all_users = await user_service.get_all_users(skip=0, limit=10000)
    total = len(all_users)
    
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get user by ID (admin only)
    
    Returns user details including roles.
    """
    user_service = UserService(session)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Create a new user (admin only)
    
    Creates a new user with specified username, email, and roles.
    """
    user_service = UserService(session)
    audit_service = AuditService(session)
    
    # Check if username or email already exists
    existing_user = await user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username '{user_data.username}' already exists",
        )
    
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_data.email}' already exists",
        )
    
    try:
        user = await user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            roles=user_data.roles,
        )
        
        # Log audit action
        await audit_service.log_action(
            user_id=int(current_user.user_id) if current_user.user_id.isdigit() else None,
            action="user.created",
            resource_type="user",
            resource_id=user.id,
            details={
                "username": user.username,
                "email": user.email,
                "roles": user.roles,
            },
        )
        
        return UserResponse.model_validate(user)
    
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update user profile (admin only)
    
    Updates user username and/or email.
    """
    user_service = UserService(session)
    audit_service = AuditService(session)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    
    # Check for conflicts if updating username or email
    if user_data.username and user_data.username != user.username:
        existing_user = await user_service.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with username '{user_data.username}' already exists",
            )
    
    if user_data.email and user_data.email != user.email:
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{user_data.email}' already exists",
            )
    
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            username=user_data.username,
            email=user_data.email,
        )
        
        # Log audit action
        await audit_service.log_action(
            user_id=int(current_user.user_id) if current_user.user_id.isdigit() else None,
            action="user.updated",
            resource_type="user",
            resource_id=user_id,
            details={
                "username": updated_user.username if updated_user else None,
                "email": updated_user.email if updated_user else None,
                "updated_fields": {
                    "username": user_data.username is not None,
                    "email": user_data.email is not None,
                },
            },
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        
        return UserResponse.model_validate(updated_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@router.post("/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: int,
    roles_data: UserRolesUpdateRequest,
    current_user: UserContext = Depends(require_admin()),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update user roles (admin only)
    
    Updates the roles assigned to a user. Role changes will be reflected
    in subsequent authentication tokens when the user logs in again.
    """
    user_service = UserService(session)
    audit_service = AuditService(session)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    
    old_roles = user.roles.copy()
    
    try:
        updated_user = await user_service.update_user_roles(
            user_id=user_id,
            roles=roles_data.roles,
        )
        
        # Log audit action
        await audit_service.log_action(
            user_id=int(current_user.user_id) if current_user.user_id.isdigit() else None,
            action="user.roles_updated",
            resource_type="user",
            resource_id=user_id,
            details={
                "username": user.username,
                "old_roles": old_roles,
                "new_roles": roles_data.roles,
            },
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        
        logger.info(
            f"User {user_id} roles updated from {old_roles} to {roles_data.roles} "
            f"by admin user {current_user.user_id}"
        )
        
        return UserResponse.model_validate(updated_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user roles",
        )

