"""
User service for database operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from airlock_common.db.models.user import User
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations"""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize user service
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Get all users with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[User]: List of users
        """
        result = await self.session.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.id)
        )
        return list(result.scalars().all())
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            Optional[User]: User if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
        
        Returns:
            Optional[User]: User if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: Email address
        
        Returns:
            Optional[User]: User if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        username: str,
        email: str,
        roles: List[str] = None,
    ) -> User:
        """
        Create a new user
        
        Args:
            username: Username
            email: Email address
            roles: List of roles (default: empty list)
        
        Returns:
            User: Created user
        
        Raises:
            IntegrityError: If username or email already exists
        """
        if roles is None:
            roles = []
        
        user = User(
            username=username,
            email=email,
            roles=roles,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            username: New username (optional)
            email: New email (optional)
        
        Returns:
            Optional[User]: Updated user if found, None otherwise
        
        Raises:
            IntegrityError: If username or email already exists
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def update_user_roles(
        self,
        user_id: int,
        roles: List[str],
    ) -> Optional[User]:
        """
        Update user roles
        
        Args:
            user_id: User ID
            roles: New list of roles
        
        Returns:
            Optional[User]: Updated user if found, None otherwise
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.roles = roles
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if user was deleted, False if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.session.delete(user)
        await self.session.flush()
        return True

