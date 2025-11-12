#!/usr/bin/env python3
"""
Test script to verify all airlock_common imports work correctly
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all imports from airlock_common"""
    print("Testing airlock_common imports...")
    
    try:
        # Test utility imports
        from airlock_common import (
            setup_logging,
            get_logger,
            validate_email,
            validate_url,
            validate_uuid,
            get_env,
            get_env_int,
            get_env_bool,
            get_env_list,
        )
        print("[OK] Utility imports successful")
        
        # Test error imports
        from airlock_common import (
            AirlockError,
            ValidationError,
            NotFoundError,
            UnauthorizedError,
            ForbiddenError,
            ConflictError,
            ServiceUnavailableError,
        )
        print("[OK] Error imports successful")
        
        # Test constants imports
        from airlock_common import (
            API_VERSION,
            API_PREFIX,
            HEALTH_ENDPOINT,
            HTTP_STATUS_OK,
            HTTP_STATUS_CREATED,
            HTTP_STATUS_BAD_REQUEST,
            HTTP_STATUS_UNAUTHORIZED,
            HTTP_STATUS_FORBIDDEN,
            HTTP_STATUS_NOT_FOUND,
            HTTP_STATUS_CONFLICT,
            HTTP_STATUS_INTERNAL_SERVER_ERROR,
            HTTP_STATUS_SERVICE_UNAVAILABLE,
            ERROR_CODE_VALIDATION_ERROR,
            ERROR_CODE_NOT_FOUND,
            ERROR_CODE_UNAUTHORIZED,
            ERROR_CODE_FORBIDDEN,
            ERROR_CODE_CONFLICT,
            ERROR_CODE_INTERNAL_SERVER_ERROR,
            ERROR_CODE_SERVICE_UNAVAILABLE,
            ROLE_SUBMITTER,
            ROLE_REVIEWER,
            ROLE_ADMIN,
            ROLES,
        )
        print("[OK] Constants imports successful")
        
        # Test database imports
        from airlock_common import (
            get_db,
            Database,
            Base,
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
        print("[OK] Database imports successful")
        
        # Test messaging imports (may be None if pika not installed)
        from airlock_common import (
            get_rabbitmq_connection,
            RabbitMQConnection,
            PACKAGE_EVENTS_EXCHANGE,
            WORKFLOW_EVENTS_EXCHANGE,
            CHECK_EVENTS_EXCHANGE,
            DLX_EXCHANGE,
        )
        print("[OK] Messaging imports successful")
        
        # Test utility functions
        print("\nTesting utility functions...")
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False
        print("[OK] validate_email works")
        
        assert validate_url("https://example.com") == True
        assert validate_url("invalid-url") == False
        print("[OK] validate_url works")
        
        assert validate_uuid("123e4567-e89b-12d3-a456-426614174000") == True
        assert validate_uuid("invalid-uuid") == False
        print("[OK] validate_uuid works")
        
        # Test constants
        print("\nTesting constants...")
        print(f"  API_VERSION: {API_VERSION}")
        print(f"  API_PREFIX: {API_PREFIX}")
        print(f"  ROLE_SUBMITTER: {ROLE_SUBMITTER}")
        print(f"  HTTP_STATUS_OK: {HTTP_STATUS_OK}")
        print(f"  ERROR_CODE_VALIDATION_ERROR: {ERROR_CODE_VALIDATION_ERROR}")
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

