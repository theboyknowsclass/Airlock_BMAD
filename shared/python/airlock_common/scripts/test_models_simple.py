#!/usr/bin/env python3
"""
Simple test script for models (no pytest required)
Tests that all models can be imported and have correct structure
"""
import os
import sys
from sqlalchemy import inspect

# Add parent directory to path so we can import airlock_common
script_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.dirname(script_dir)
python_dir = os.path.dirname(package_dir)
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

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


def test_models():
    """Test that all models can be imported and have correct structure"""
    print("=" * 60)
    print("Testing Database Models")
    print("=" * 60)
    print()
    
    models = [
        ("User", User, "users"),
        ("PackageSubmission", PackageSubmission, "package_submissions"),
        ("PackageRequest", PackageRequest, "package_requests"),
        ("Package", Package, "packages"),
        ("Workflow", Workflow, "workflows"),
        ("CheckResult", CheckResult, "check_results"),
        ("AuditLog", AuditLog, "audit_logs"),
        ("APIKey", APIKey, "api_keys"),
        ("PackageUsage", PackageUsage, "package_usage"),
        ("LicenseAllowlist", LicenseAllowlist, "license_allowlist"),
    ]
    
    print("Testing model imports...")
    for model_name, model_class, table_name in models:
        try:
            assert hasattr(model_class, "__tablename__"), f"{model_name} missing __tablename__"
            assert model_class.__tablename__ == table_name, f"{model_name} table name mismatch"
            print(f"  ✓ {model_name} ({table_name})")
        except Exception as e:
            print(f"  ✗ {model_name}: {e}")
            return False
    
    print()
    print("Testing model structure...")
    
    # Test User model
    try:
        mapper = inspect(User)
        user_columns = [col.key for col in mapper.columns]
        required_columns = ["id", "username", "email", "roles", "created_at", "updated_at"]
        for col in required_columns:
            assert col in user_columns, f"User model missing column: {col}"
        print("  ✓ User model structure correct")
    except Exception as e:
        print(f"  ✗ User model structure: {e}")
        return False
    
    # Test PackageSubmission model
    try:
        mapper = inspect(PackageSubmission)
        submission_columns = [col.key for col in mapper.columns]
        required_columns = ["id", "user_id", "project_name", "project_version", "package_lock_json", "status", "created_at", "updated_at"]
        for col in required_columns:
            assert col in submission_columns, f"PackageSubmission model missing column: {col}"
        print("  ✓ PackageSubmission model structure correct")
    except Exception as e:
        print(f"  ✗ PackageSubmission model structure: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✓ All model tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)

