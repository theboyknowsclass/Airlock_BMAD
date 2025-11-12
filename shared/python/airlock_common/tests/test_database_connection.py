"""
Tests for database connection
These tests require a database connection
"""
import pytest
import os
import asyncio
from sqlalchemy import text

from airlock_common import get_db, Base
from airlock_common.db.database import get_database_url


# Check if database is available
DATABASE_AVAILABLE = os.getenv("POSTGRES_HOST") is not None or os.getenv("CI") is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database not available")
async def test_database_connection():
    """Test that database connection works"""
    db = get_db()
    
    try:
        # Test connection by executing a simple query
        async with db.get_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        print("✓ Database connection successful")
    finally:
        await db.close()


@pytest.mark.asyncio
@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database not available")
async def test_create_tables():
    """Test that tables can be created"""
    db = get_db()
    
    try:
        # Create all tables
        await db.create_tables()
        print("✓ Tables created successfully")
        
        # Verify tables exist by querying information_schema
        async with db.get_session() as session:
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                "users",
                "package_submissions",
                "package_requests",
                "packages",
                "workflows",
                "check_results",
                "audit_logs",
                "api_keys",
                "package_usage",
                "license_allowlist",
            ]
            
            for table in expected_tables:
                assert table in tables, f"Table {table} not found"
        
        print("✓ All expected tables exist")
        
        # Clean up - drop tables
        await db.drop_tables()
        print("✓ Tables dropped successfully")
        
    finally:
        await db.close()


@pytest.mark.asyncio
@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database not available")
async def test_database_url_generation():
    """Test that database URL is generated correctly"""
    url = get_database_url()
    
    assert url.startswith("postgresql+asyncpg://")
    assert "@" in url
    assert "/" in url
    
    # Check that it contains expected components
    assert "postgresql+asyncpg://" in url
    print(f"✓ Database URL generated: {url.split('@')[1] if '@' in url else url}")


def test_database_url_defaults():
    """Test that database URL uses correct defaults"""
    # Save original environment
    original_env = {
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }
    
    try:
        # Clear environment variables
        for key in original_env:
            if key in os.environ:
                del os.environ[key]
        
        # Get URL with defaults
        url = get_database_url()
        
        assert "airlock:airlock@localhost:5432/airlock" in url
        print("✓ Database URL uses correct defaults")
        
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value

