"""
Database connection and session management
"""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.pool import NullPool, QueuePool

from .base import Base


class Database:
    """Database connection manager"""
    
    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_pre_ping: bool = True
    ):
        """
        Initialize database connection
        
        Args:
            database_url: PostgreSQL connection URL (asyncpg format)
            echo: Enable SQL query logging
            pool_size: Size of connection pool
            max_overflow: Maximum overflow connections
            pool_pre_ping: Enable connection health checks
        """
        self.database_url = database_url
        self.echo = echo
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=echo,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    
    async def create_tables(self):
        """Create all database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session
        
        Yields:
            AsyncSession: Database session
        """
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


def get_database_url() -> str:
    """
    Get database URL from environment variables
    
    Returns:
        str: Database connection URL in asyncpg format
    """
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "airlock")
    user = os.getenv("POSTGRES_USER", "airlock")
    password = os.getenv("POSTGRES_PASSWORD", "airlock")
    
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


def get_db() -> Database:
    """
    Get database instance
    
    Returns:
        Database: Database instance configured from environment variables
    """
    database_url = get_database_url()
    echo = os.getenv("DB_ECHO", "false").lower() == "true"
    pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    return Database(
        database_url=database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True
    )


# Global database instance (can be initialized per service)
_db_instance: Database | None = None


def get_db_instance() -> Database:
    """
    Get or create global database instance
    
    Returns:
        Database: Global database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = get_db()
    return _db_instance

