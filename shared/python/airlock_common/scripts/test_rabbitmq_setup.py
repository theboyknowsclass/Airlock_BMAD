"""
Test RabbitMQ setup script
Tests RabbitMQ connection and configuration without requiring database models
"""
import sys
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
shared_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, shared_dir)

def test_imports():
    """Test that messaging modules can be imported"""
    print("Testing imports...")
    try:
        from airlock_common.messaging.connection import get_rabbitmq_connection
        from airlock_common.messaging.exchanges import (
            PACKAGE_EVENTS_EXCHANGE,
            WORKFLOW_EVENTS_EXCHANGE,
            CHECK_EVENTS_EXCHANGE,
            DLX_EXCHANGE,
        )
        print("[OK] Messaging imports successful")
        return True
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False


def test_pika_installed():
    """Test that pika is installed"""
    print("\nTesting pika installation...")
    try:
        import pika
        print(f"[OK] pika installed (version: {pika.__version__ if hasattr(pika, '__version__') else 'unknown'})")
        return True
    except ImportError:
        print("[ERROR] pika not installed")
        print("\nPlease install pika:")
        print("  pip install pika>=1.3.2,<2.0.0")
        return False


def test_environment_variables():
    """Test that environment variables are set"""
    print("\nTesting environment variables...")
    required_vars = ["RABBITMQ_HOST", "RABBITMQ_PORT", "RABBITMQ_USER", "RABBITMQ_PASSWORD"]
    missing_vars = []
    defaults = {
        "RABBITMQ_HOST": "localhost",
        "RABBITMQ_PORT": "5672",
        "RABBITMQ_USER": "guest",
        "RABBITMQ_PASSWORD": "guest",
    }
    
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
            default_value = defaults.get(var, "not set")
            if "PASSWORD" in var:
                default_value = "*** (guest)"
            print(f"[WARN] {var} not set (will use default: {default_value})")
        else:
            # Mask password
            value = os.environ[var]
            if "PASSWORD" in var:
                value = "***" if value else "not set"
            print(f"[OK] {var} = {value}")
    
    if missing_vars:
        print(f"\n[WARN] Missing environment variables: {', '.join(missing_vars)}")
        print("Using defaults:")
        print("  RABBITMQ_HOST = localhost")
        print("  RABBITMQ_PORT = 5672")
        print("  RABBITMQ_USER = guest")
        print("  RABBITMQ_PASSWORD = guest")
        print("\n  Note: If RabbitMQ uses different credentials (from .env.dev), set:")
        print("    $env:RABBITMQ_USER = \"airlock\"  # or value from .env.dev")
        print("    $env:RABBITMQ_PASSWORD = \"airlock\"  # or value from .env.dev")
        return True  # Not a failure, just a warning
    
    return True


def test_rabbitmq_connection():
    """Test RabbitMQ connection"""
    print("\nTesting RabbitMQ connection...")
    
    # Show what credentials are being used
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = os.getenv("RABBITMQ_PORT", "5672")
    user = os.getenv("RABBITMQ_USER", "guest")
    password_set = "RABBITMQ_PASSWORD" in os.environ
    password_display = "***" if password_set else "guest (default)"
    
    print(f"  Connecting to: {host}:{port}")
    print(f"  Username: {user}")
    print(f"  Password: {password_display}")
    
    try:
        from airlock_common.messaging.connection import get_rabbitmq_connection
        
        with get_rabbitmq_connection() as conn:
            channel = conn.get_channel()
            # Try to declare a test queue
            channel.queue_declare(queue="test_connection", durable=False, auto_delete=True)
            channel.queue_delete(queue="test_connection")
            print("[OK] RabbitMQ connection successful")
            return True
    except Exception as e:
        error_str = str(e)
        print(f"[ERROR] RabbitMQ connection failed: {e}")
        
        # Check for authentication errors
        if "ACCESS_REFUSED" in error_str or "403" in error_str or "Login was refused" in error_str:
            print("\n[ERROR] Authentication failed!")
            print("  The credentials don't match RabbitMQ configuration.")
            print(f"\n  Current credentials:")
            print(f"    Username: {user}")
            print(f"    Password: {password_display}")
            print("\n  Solutions:")
            print("  1. Check .env.dev for RABBITMQ_USER and RABBITMQ_PASSWORD")
            print("  2. Set environment variables to match .env.dev:")
            print("     $env:RABBITMQ_USER = \"airlock\"  # or value from .env.dev")
            print("     $env:RABBITMQ_PASSWORD = \"airlock\"  # or value from .env.dev")
            print("  3. Or check RabbitMQ container logs:")
            print("     docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev logs rabbitmq")
            print("  4. Or check what credentials RabbitMQ is using:")
            print("     docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev exec rabbitmq env | findstr RABBITMQ")
        
        # Check for connection errors
        elif "connection refused" in error_str.lower() or "111" in error_str or "Connection refused" in error_str:
            print("\n[ERROR] Cannot connect to RabbitMQ!")
            print("  RabbitMQ may not be running or port is not exposed.")
            print("\n  Solutions:")
            print("  1. Start RabbitMQ:")
            print("     docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d rabbitmq")
            print("  2. Check if port is exposed:")
            print("     docker port airlock-rabbitmq")
            print("  3. Check port configuration:")
            print("     python scripts/check_rabbitmq_ports.py")
        else:
            print("\n[ERROR] Connection failed!")
            print("  Please check:")
            print("  1. RabbitMQ is running")
            print("  2. Port is exposed (5672)")
            print("  3. Credentials are correct (from .env.dev)")
        
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("RabbitMQ Setup Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Pika Installation", test_pika_installed),
        ("Environment Variables", test_environment_variables),
        ("RabbitMQ Connection", test_rabbitmq_connection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name} test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n[OK] All tests passed!")
        print("\nNext steps:")
        print("  1. Initialize RabbitMQ: python scripts/init_rabbitmq.py")
        print("  2. Verify in management UI: http://localhost:15672")
    else:
        print("\n[ERROR] Some tests failed. Please fix the issues above.")
        sys.exit(1)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

