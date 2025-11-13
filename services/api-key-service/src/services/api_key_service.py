"""
API Key service for key generation, hashing, storage, and management
"""
import secrets
import bcrypt
import json
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from airlock_common.db.models.api_key import APIKey

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for API key management operations"""
    
    # API key prefix for identification
    KEY_PREFIX = "ak_"  # "ak" for "API Key"
    
    # Key length (excluding prefix)
    KEY_LENGTH = 32  # 32 bytes = 64 hex characters
    
    def __init__(self, session: AsyncSession):
        """
        Initialize API key service
        
        Args:
            session: Database session
        """
        self.session = session
    
    def _generate_key(self) -> str:
        """
        Generate a secure random API key
        
        Returns:
            str: Generated API key with prefix
        """
        # Generate random bytes and convert to hex
        random_bytes = secrets.token_bytes(self.KEY_LENGTH)
        key_suffix = random_bytes.hex()
        return f"{self.KEY_PREFIX}{key_suffix}"
    
    def _hash_key(self, key: str) -> str:
        """
        Hash an API key using bcrypt
        
        Args:
            key: Plain text API key
            
        Returns:
            str: Hashed key
        """
        # Use bcrypt to hash the key
        # bcrypt expects bytes, so encode the key
        key_bytes = key.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(key_bytes, salt)
        return hashed.decode('utf-8')
    
    def _verify_key(self, key: str, key_hash: str) -> bool:
        """
        Verify an API key against its hash
        
        Args:
            key: Plain text API key
            key_hash: Hashed key from database
            
        Returns:
            bool: True if key matches hash
        """
        try:
            key_bytes = key.encode('utf-8')
            hash_bytes = key_hash.encode('utf-8')
            return bcrypt.checkpw(key_bytes, hash_bytes)
        except Exception as e:
            logger.error(f"Error verifying key: {e}")
            return False
    
    async def create_api_key(
        self,
        scopes: List[str],
        permissions: List[str],
        expires_in_days: Optional[int] = None,
    ) -> tuple[APIKey, str]:
        """
        Create a new API key
        
        Args:
            scopes: List of scopes (e.g., ["read-only", "read-write", "admin"])
            permissions: List of permissions
            expires_in_days: Optional expiration in days (None = no expiration)
        
        Returns:
            tuple: (APIKey model, plain_text_key)
        """
        # Generate new key
        plain_key = self._generate_key()
        key_hash = self._hash_key(plain_key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key record
        api_key = APIKey(
            key_hash=key_hash,
            scopes=json.dumps(scopes),
            permissions=json.dumps(permissions),
            expires_at=expires_at,
        )
        
        self.session.add(api_key)
        await self.session.flush()
        await self.session.refresh(api_key)
        
        logger.info(f"Created API key with ID {api_key.id}")
        
        return api_key, plain_key
    
    async def get_all_api_keys(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[APIKey]:
        """
        Get all API keys with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[APIKey]: List of API keys
        """
        stmt = select(APIKey).offset(skip).limit(limit).order_by(APIKey.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_api_key_by_id(self, key_id: int) -> Optional[APIKey]:
        """
        Get API key by ID
        
        Args:
            key_id: API key ID
        
        Returns:
            Optional[APIKey]: API key if found, None otherwise
        """
        stmt = select(APIKey).where(APIKey.id == key_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_api_key_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """
        Find API key by hash (for validation)
        
        Args:
            key_hash: Hashed key
        
        Returns:
            Optional[APIKey]: API key if found, None otherwise
        """
        stmt = select(APIKey).where(APIKey.key_hash == key_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_api_key_by_plain_key(self, plain_key: str) -> Optional[APIKey]:
        """
        Find API key by plain text key (for validation)
        
        This method checks all keys in the database to find a match.
        In production, this should be optimized with an index or different approach.
        
        Args:
            plain_key: Plain text API key
        
        Returns:
            Optional[APIKey]: API key if found and valid, None otherwise
        """
        # Get all keys (in production, this should be optimized)
        stmt = select(APIKey)
        result = await self.session.execute(stmt)
        all_keys = result.scalars().all()
        
        # Check each key hash
        for api_key in all_keys:
            if self._verify_key(plain_key, api_key.key_hash):
                return api_key
        
        return None
    
    async def revoke_api_key(self, key_id: int) -> bool:
        """
        Revoke an API key by deleting it
        
        Args:
            key_id: API key ID
        
        Returns:
            bool: True if key was revoked, False if not found
        """
        api_key = await self.get_api_key_by_id(key_id)
        if not api_key:
            return False
        
        await self.session.delete(api_key)
        await self.session.flush()
        
        logger.info(f"Revoked API key with ID {key_id}")
        return True
    
    async def rotate_api_key(
        self,
        key_id: int,
        scopes: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> tuple[Optional[APIKey], Optional[str]]:
        """
        Rotate an API key (revoke old, create new)
        
        Args:
            key_id: Existing API key ID
            scopes: New scopes (if None, uses existing scopes)
            permissions: New permissions (if None, uses existing permissions)
            expires_in_days: New expiration in days (if None, uses existing expiration)
        
        Returns:
            tuple: (New APIKey model, plain_text_key) or (None, None) if old key not found
        """
        old_key = await self.get_api_key_by_id(key_id)
        if not old_key:
            return None, None
        
        # Use existing values if not provided
        if scopes is None:
            scopes = json.loads(old_key.scopes)
        if permissions is None:
            permissions = json.loads(old_key.permissions)
        if expires_in_days is None and old_key.expires_at:
            # Calculate days until expiration
            days_until_expiry = (old_key.expires_at - datetime.utcnow()).days
            expires_in_days = max(1, days_until_expiry) if days_until_expiry > 0 else None
        
        # Revoke old key
        await self.revoke_api_key(key_id)
        
        # Create new key
        new_key, plain_key = await self.create_api_key(
            scopes=scopes,
            permissions=permissions,
            expires_in_days=expires_in_days,
        )
        
        logger.info(f"Rotated API key: revoked {key_id}, created {new_key.id}")
        
        return new_key, plain_key
    
    def is_key_expired(self, api_key: APIKey) -> bool:
        """
        Check if an API key is expired
        
        Args:
            api_key: API key model
        
        Returns:
            bool: True if expired, False otherwise
        """
        if api_key.expires_at is None:
            return False
        
        return datetime.utcnow() > api_key.expires_at
    
    def is_key_valid(self, api_key: APIKey) -> bool:
        """
        Check if an API key is valid (not expired)
        
        Args:
            api_key: API key model
        
        Returns:
            bool: True if valid, False otherwise
        """
        return not self.is_key_expired(api_key)

