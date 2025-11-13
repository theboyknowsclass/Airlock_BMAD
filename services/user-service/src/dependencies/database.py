"""
Database dependencies for User Management Service
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from airlock_common.db.database import get_db_instance


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session
    
    Yields:
        AsyncSession: Database session
    """
    db = get_db_instance()
    async for session in db.get_session():
        yield session

