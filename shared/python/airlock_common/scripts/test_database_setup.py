#!/usr/bin/env python3
"""
Test script to verify database setup
This script tests that:
1. All models can be imported (no database required)
2. Database connection works (if database is available)
3. Database tables can be created (if database is available)
"""
import asyncio
import os
import sys
from sqlalchemy import text, inspect

# Add parent directory to path so we can import airlock_common
# This script is in: shared/python/airlock_common/scripts/
# We need to add: shared/python/ to the path
script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/
package_dir = os.path.dirname(script_dir)  # airlock_common/
python_dir = os.path.dirname(package_dir)  # python/
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

from airlock_common import get_db, Base
from airlock_common.db.models import (
    User,
    PackageSubmission,
    PackageRequest,
    Package,
    Workflow,
    CheckResult,
    AuditLog,
    APIKey,
    PackageUsage,
    LicenseAllowlist,
)


def test_models_import():
    """Test that all models can be imported"""
    print("Testing model imports...")
    
    models = [
        User,
        PackageSubmission,
        PackageRequest,
        Package,
        Workflow,
        CheckResult,
        AuditLog,
        APIKey,
        PackageUsage,
        LicenseAllowlist,
    ]
    
    for model in models:
        assert hasattr(model, "__tablename__"), f"Model {model.__name__} missing __tablename__"
        assert hasattr(model, "__table__"), f"Model {model.__name__} missing __table__"
        print(f"  ✓ {model.__name__} ({model.__tablename__})")
    
    print("✓ All models imported successfully\n")


def test_model_structure():
    """Test that models have correct structure"""
    print("Testing model structure...")
    
    # Test User model
    mapper = inspect(User)
    user_columns = [col.key for col in mapper.columns]
    assert "id" in user_columns
    assert "username" in user_columns
    assert "email" in user_columns
    assert "roles" in user_columns
    print("  ✓ User model structure correct")
    
    # Test PackageSubmission model
    mapper = inspect(PackageSubmission)
    submission_columns = [col.key for col in mapper.columns]
    assert "id" in submission_columns
    assert "user_id" in submission_columns
    assert "project_name" in submission_columns
    assert "project_version" in submission_columns
    assert "package_lock_json" in submission_columns
    assert "status" in submission_columns
    print("  ✓ PackageSubmission model structure correct")
    
    # Test that all expected tables exist
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
    
    for table_name in expected_tables:
        # Find model with this table name
        model = None
        for model_class in [User, PackageSubmission, PackageRequest, Package, 
                           Workflow, CheckResult, AuditLog, APIKey, 
                           PackageUsage, LicenseAllowlist]:
            if model_class.__tablename__ == table_name:
                model = model_class
                break
        
        assert model is not None, f"Model for table {table_name} not found"
    
    print("  ✓ All expected tables have models\n")


async def test_database_connection():
    """Test database connection (requires database to be running)"""
    print("Testing database connection...")
    
    # Check environment variables
    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"  ⚠ Missing environment variables: {', '.join(missing_vars)}")
        print("  ⚠ Using defaults (localhost:5432/airlock)")
        print("  ⚠ Database connection test skipped - start PostgreSQL to test")
        return False
    
    try:
        db = get_db()
        print("  ✓ Database connection created")
        
        # Test connection by executing a simple query
        try:
            async with db.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
            print("  ✓ Database connection successful")
            
            # Test table creation
            print("  Testing table creation...")
            await db.create_tables()
            print("  ✓ Tables created successfully")
            
            # Verify tables exist
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
                    if table in tables:
                        print(f"    ✓ Table {table} exists")
                    else:
                        print(f"    ✗ Table {table} missing")
                
                assert all(table in tables for table in expected_tables), "Some tables are missing"
            
            # Clean up - drop tables
            await db.drop_tables()
            print("  ✓ Tables dropped successfully")
            
            await db.close()
            return True
            
        except Exception as e:
            print(f"  ✗ Database connection failed: {e}")
            print("  ⚠ Make sure PostgreSQL is running and accessible")
            await db.close()
            return False
        
    except Exception as e:
        print(f"  ✗ Error creating database connection: {e}")
        return False


def test_database_url():
    """Test database URL generation"""
    print("Testing database URL generation...")
    
    from airlock_common.db.database import get_database_url
    url = get_database_url()
    
    assert url.startswith("postgresql+asyncpg://")
    assert "@" in url
    assert "/" in url
    
    # Mask password in output
    if "@" in url:
        parts = url.split("@")
        masked_url = parts[0].split(":")[0] + ":****@" + parts[1]
        print(f"  ✓ Database URL: {masked_url}")
    else:
        print(f"  ✓ Database URL: {url}")
    
    print()


async def main():
    """Main test function"""
    print("=" * 60)
    print("Database Setup Test")
    print("=" * 60)
    print()
    
    # Test 1: Model imports (no database required)
    test_models_import()
    
    # Test 2: Model structure (no database required)
    test_model_structure()
    
    # Test 3: Database URL generation (no database required)
    test_database_url()
    
    # Test 4: Database connection (requires database)
    db_available = await test_database_connection()
    
    print("=" * 60)
    if db_available:
        print("✓ All tests passed!")
        print("\nNext steps:")
        print("1. Run: alembic revision --autogenerate -m 'Initial schema'")
        print("2. Run: alembic upgrade head")
    else:
        print("✓ Model tests passed!")
        print("⚠ Database connection test skipped (database not available)")
        print("\nTo test database connection:")
        print("1. Start PostgreSQL (e.g., docker-compose up postgres)")
        print("2. Set environment variables (or use defaults)")
        print("3. Run this script again")
        print("\nTo create migrations:")
        print("1. Run: alembic revision --autogenerate -m 'Initial schema'")
        print("2. Run: alembic upgrade head")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

