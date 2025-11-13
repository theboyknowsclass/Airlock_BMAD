"""
Step definitions for API Key Management feature
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import delete, select

# Add src to path for imports
api_key_service_src = os.path.join(os.path.dirname(__file__), '../../../')
if api_key_service_src not in sys.path:
    sys.path.insert(0, api_key_service_src)

# Add shared/python to path for airlock_common
shared_python_path = os.path.join(
    os.path.dirname(__file__), 
    '../../../../..', 
    'shared', 
    'python'
)
if os.path.exists(shared_python_path):
    sys.path.insert(0, shared_python_path)

from pytest_bdd import given, when, then, parsers, scenario

# Import models
from airlock_common.db.models.api_key import APIKey
from airlock_common.db.base import Base as TestBase

# Import from api-key-service
from src.main import app

# Import JWT utilities from auth-service
auth_service_path = Path(__file__).parent.parent.parent.parent / "auth-service" / "src"
if str(auth_service_path) not in sys.path:
    sys.path.insert(0, str(auth_service_path))

try:
    from utils.jwt import create_access_token
    from config import settings as auth_settings
except ImportError:
    # Fallback: create minimal JWT token creation for testing
    import jwt
    import os
    
    class AuthSettings:
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
        JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        JWT_ISSUER = os.getenv("JWT_ISSUER", "airlock-auth-service")
    
    auth_settings = AuthSettings()
    
    def create_access_token(user_id: str, username: str, roles: list):
        """Create access token for testing"""
        from datetime import datetime, timedelta, UTC
        now = datetime.now(UTC)
        exp = now + timedelta(minutes=15)
        claims = {
            "sub": user_id,
            "username": username,
            "roles": roles,
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
            "iss": auth_settings.JWT_ISSUER,
            "type": "access",
        }
        return jwt.encode(claims, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM)

# Get feature file path
FEATURE_FILE = Path(__file__).parent.parent / "api_key_management.feature"

# Test database setup
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'airlock_dev')}:{os.getenv('POSTGRES_PASSWORD', 'dev_password_change_me')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'airlock_dev')}"
)


def run_async(coro):
    """Helper to run async code in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@pytest.fixture(scope="function")
async def db_engine():
    """Create a test database engine using PostgreSQL from Docker"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=False,
        echo=False,
    )
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        def create_tables(sync_conn):
            from airlock_common.db.models import APIKey
            try:
                TestBase.metadata.create_all(sync_conn, checkfirst=True)
            except Exception as e:
                error_str = str(e).lower()
                if "already exists" in error_str or "duplicate" in error_str:
                    pass
                else:
                    raise
        
        await conn.run_sync(create_tables)
    
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Create a test database session with transaction rollback for isolation"""
    async_session_maker = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Clean up any existing test data before starting
    async with async_session_maker() as cleanup_session:
        await cleanup_session.execute(delete(APIKey))
        await cleanup_session.commit()
    
    # Create session for the test
    async with async_session_maker() as session:
        yield session
        # Clean up after test
        try:
            await session.rollback()
            async with async_session_maker() as cleanup_session:
                await cleanup_session.execute(delete(APIKey))
                await cleanup_session.commit()
        except Exception:
            pass


@pytest.fixture
def context():
    """Test context for storing state between steps"""
    return {}


@pytest.fixture
async def client(db_session, context):
    """Create async test client with database and auth dependency overrides"""
    from src.dependencies.database import get_db_session
    from typing import AsyncGenerator
    from fastapi import Depends
    from fastapi.security import HTTPBearer
    
    # Override database
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    # Override auth dependencies for testing
    test_context = context
    
    async def mock_get_current_user(
        credentials = Depends(HTTPBearer(auto_error=False)),
    ):
        """Mock auth that reads token from test context"""
        from src.dependencies import UserContext
        from fastapi import HTTPException, status
        
        token = test_context.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        
        # Get user info from context (set by Given steps) or decode token
        user_info = test_context.get("user_info", {})
        if not user_info:
            # Decode token to get user info
            import jwt
            try:
                claims = jwt.decode(
                    token, 
                    auth_settings.JWT_SECRET_KEY, 
                    algorithms=[auth_settings.JWT_ALGORITHM]
                )
                user_info = {
                    "user_id": claims.get("sub"),
                    "username": claims.get("username"),
                    "roles": claims.get("roles", []),
                }
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
        
        return UserContext(
            user_id=user_info.get("user_id", test_context.get("user_id", "test-user-id")),
            username=user_info.get("username", test_context.get("username", "test-user")),
            roles=user_info.get("roles", test_context.get("roles", [])),
        )
    
    # Create admin checker that uses the mock_get_current_user
    async def mock_admin_checker(current_user = Depends(mock_get_current_user)):
        if "admin" not in current_user.roles:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Required role: admin",
            )
        return current_user
    
    from src.dependencies import get_current_user, require_admin
    from src.routers import api_keys
    
    # Override auth dependencies
    import src.dependencies as deps_module
    
    # Store original functions
    orig_get_current_user = deps_module.get_current_user
    orig_require_admin = deps_module.require_admin
    
    # Override at module level
    deps_module.get_current_user = mock_get_current_user
    
    def mock_require_admin():
        return mock_admin_checker
    
    deps_module.require_admin = mock_require_admin
    
    # Override dependencies in FastAPI
    app.dependency_overrides[orig_get_current_user] = mock_get_current_user
    
    # Get the dependency function that require_admin() returns and override it
    # The router endpoints use Depends(require_admin()), so we need to override
    # the result of calling require_admin()
    admin_dependency = mock_require_admin()
    
    # Set FastAPI dependency overrides
    app.dependency_overrides[orig_get_current_user] = mock_get_current_user
    app.dependency_overrides[orig_require_admin] = mock_require_admin
    
    # Also override the dependency function returned by require_admin()
    # This is what's actually used in Depends(require_admin())
    # We need to find all endpoints that use require_admin() and override their dependencies
    # Override the dependency for each endpoint that uses require_admin()
    for route in api_keys.router.routes:
        if hasattr(route, 'dependant') and route.dependant:
            # Check if this route uses require_admin
            for dep in route.dependant.dependencies:
                if dep.call == orig_require_admin:
                    # Override this specific dependency
                    app.dependency_overrides[dep.call] = mock_require_admin
                elif hasattr(dep, 'call') and callable(dep.call):
                    # Check if it's the result of calling require_admin()
                    try:
                        # If it's a function that was returned by require_admin(), override it
                        if dep.call == admin_dependency or (hasattr(dep.call, '__name__') and 'admin' in dep.call.__name__.lower()):
                            app.dependency_overrides[dep.call] = admin_dependency
                    except:
                        pass
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()
    # Restore original functions
    import src.dependencies as deps_module
    deps_module.get_current_user = orig_get_current_user
    deps_module.require_admin = orig_require_admin


# Given steps
@given("the API key service is configured")
def api_key_service_configured():
    """API key service is configured"""
    pass


@given("the database is available")
def database_available():
    """Database is available"""
    pass


@given(parsers.parse('I have a valid admin access token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def valid_admin_token(context, user_id: str, username: str, roles: str):
    """Create admin access token"""
    roles_list = [r.strip() for r in roles.split(",")]
    token = create_access_token(user_id, username, roles_list)
    context["token"] = token
    context["user_id"] = user_id
    context["username"] = username
    context["roles"] = roles_list
    context["user_info"] = {
        "user_id": user_id,
        "username": username,
        "roles": roles_list,
    }


@given("I have a valid admin access token")
def valid_admin_token_simple(context):
    """Create admin access token (simple)"""
    token = create_access_token("admin-user", "admin", ["admin"])
    context["token"] = token
    context["user_info"] = {
        "user_id": "admin-user",
        "username": "admin",
        "roles": ["admin"],
    }


@given(parsers.parse('I have a valid access token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def valid_access_token(context, user_id: str, username: str, roles: str):
    """Create access token"""
    roles_list = [r.strip() for r in roles.split(",")]
    token = create_access_token(user_id, username, roles_list)
    context["token"] = token
    context["user_id"] = user_id
    context["username"] = username
    context["roles"] = roles_list
    context["user_info"] = {
        "user_id": user_id,
        "username": username,
        "roles": roles_list,
    }


@given(parsers.parse('an API key exists with scopes "{scopes}" and permissions "{permissions}"'))
def api_key_exists(client: AsyncClient, context, db_session: AsyncSession, scopes: str, permissions: str):
    """Create an API key in the database"""
    from src.services.api_key_service import APIKeyService
    
    scopes_list = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    permissions_list = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    
    api_key_service = APIKeyService(db_session)
    api_key, plain_key = run_async(api_key_service.create_api_key(
        scopes=scopes_list,
        permissions=permissions_list,
    ))
    
    context["api_key_id"] = api_key.id
    context["api_key_plain"] = plain_key
    context["api_key"] = api_key


@given(parsers.parse('an API key exists with scopes "{scopes}" and permissions "{permissions}" expiring in {days:d} days'))
def api_key_exists_with_expiration(client: AsyncClient, context, db_session: AsyncSession, scopes: str, permissions: str, days: int):
    """Create an API key with expiration"""
    from src.services.api_key_service import APIKeyService
    
    scopes_list = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    permissions_list = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    
    api_key_service = APIKeyService(db_session)
    api_key, plain_key = run_async(api_key_service.create_api_key(
        scopes=scopes_list,
        permissions=permissions_list,
        expires_in_days=days,
    ))
    
    context["api_key_id"] = api_key.id
    context["api_key_plain"] = plain_key
    context["api_key"] = api_key


# When steps
@when(parsers.parse('I create an API key with scopes "{scopes}" and permissions "{permissions}"'))
def create_api_key(client: AsyncClient, context, scopes: str, permissions: str):
    """Create an API key"""
    scopes_list = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    permissions_list = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {
        "scopes": scopes_list,
        "permissions": permissions_list,
    }
    response = run_async(client.post("/api/v1/keys", json=data, headers=headers))
    context["response"] = response
    if response.status_code == 201:
        context["created_key"] = response.json()


@when(parsers.parse('I create an API key with scopes "{scopes}" and permissions "{permissions}" expiring in {days:d} days'))
def create_api_key_with_expiration(client: AsyncClient, context, scopes: str, permissions: str, days: int):
    """Create an API key with expiration"""
    scopes_list = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    permissions_list = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {
        "scopes": scopes_list,
        "permissions": permissions_list,
        "expires_in_days": days,
    }
    response = run_async(client.post("/api/v1/keys", json=data, headers=headers))
    context["response"] = response
    if response.status_code == 201:
        context["created_key"] = response.json()


@when("I request to list all API keys")
def list_api_keys(client: AsyncClient, context):
    """List all API keys"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = run_async(client.get("/api/v1/keys", headers=headers))
    context["response"] = response


@when("I request to view the API key")
def view_api_key(client: AsyncClient, context):
    """View a specific API key"""
    key_id = context.get("api_key_id")
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = run_async(client.get(f"/api/v1/keys/{key_id}", headers=headers))
    context["response"] = response


@when(parsers.parse('I request to view API key with ID {key_id:d}'))
def view_api_key_by_id(client: AsyncClient, context, key_id: int):
    """View API key by ID"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = run_async(client.get(f"/api/v1/keys/{key_id}", headers=headers))
    context["response"] = response


@when("I revoke the API key")
def revoke_api_key(client: AsyncClient, context):
    """Revoke an API key"""
    key_id = context.get("api_key_id")
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = run_async(client.delete(f"/api/v1/keys/{key_id}", headers=headers))
    context["response"] = response


@when(parsers.parse('I revoke API key with ID {key_id:d}'))
def revoke_api_key_by_id(client: AsyncClient, context, key_id: int):
    """Revoke API key by ID"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = run_async(client.delete(f"/api/v1/keys/{key_id}", headers=headers))
    context["response"] = response


@when("I rotate the API key")
def rotate_api_key(client: AsyncClient, context):
    """Rotate an API key"""
    key_id = context.get("api_key_id")
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {}
    response = run_async(client.post(f"/api/v1/keys/{key_id}/rotate", json=data, headers=headers))
    context["response"] = response
    if response.status_code == 200:
        context["rotated_key"] = response.json()


@when(parsers.parse('I rotate API key with ID {key_id:d}'))
def rotate_api_key_by_id(client: AsyncClient, context, key_id: int):
    """Rotate API key by ID"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {}
    response = run_async(client.post(f"/api/v1/keys/{key_id}/rotate", json=data, headers=headers))
    context["response"] = response


@when(parsers.parse('I rotate the API key with new scopes "{scopes}" and new permissions "{permissions}"'))
def rotate_api_key_with_updates(client: AsyncClient, context, scopes: str, permissions: str):
    """Rotate API key with updated scopes and permissions"""
    key_id = context.get("api_key_id")
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    scopes_list = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    permissions_list = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    
    data = {
        "scopes": scopes_list,
        "permissions": permissions_list,
    }
    response = run_async(client.post(f"/api/v1/keys/{key_id}/rotate", json=data, headers=headers))
    context["response"] = response
    if response.status_code == 200:
        context["rotated_key"] = response.json()


@when("I create another API key with scopes \"read-only\" and permissions \"read\"")
def create_another_api_key(client: AsyncClient, context):
    """Create another API key"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {
        "scopes": ["read-only"],
        "permissions": ["read"],
    }
    response = run_async(client.post("/api/v1/keys", json=data, headers=headers))
    context["response"] = response
    if response.status_code == 201:
        context["created_key_2"] = response.json()


# Then steps
@then(parsers.parse('the request should succeed with status {status_code:d}'))
def request_succeeds(context, status_code: int):
    """Check request succeeded"""
    response = context["response"]
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.text}"


@then(parsers.parse('the request should fail with status {status_code:d}'))
def request_fails(context, status_code: int):
    """Check request failed"""
    response = context["response"]
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.text}"


@then("the response should contain a key field")
def response_contains_key(context):
    """Check response contains key field"""
    response = context["response"]
    data = response.json()
    assert "key" in data, f"Response should contain 'key' field: {data}"
    assert data["key"], "Key should not be empty"
    context["returned_key"] = data["key"]


@then(parsers.parse('the response should contain scopes "{scopes}"'))
def response_contains_scopes(context, scopes: str):
    """Check response contains scopes"""
    response = context["response"]
    data = response.json()
    expected_scopes = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    if "keys" in data:  # List response
        # Check first key
        assert len(data["keys"]) > 0, "Response should contain at least one key"
        actual_scopes = data["keys"][0]["scopes"]
    else:  # Single key response
        actual_scopes = data["scopes"]
    assert set(actual_scopes) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {actual_scopes}"


@then(parsers.parse('the response should contain permissions "{permissions}"'))
def response_contains_permissions(context, permissions: str):
    """Check response contains permissions"""
    response = context["response"]
    data = response.json()
    expected_permissions = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    if "keys" in data:  # List response
        actual_permissions = data["keys"][0]["permissions"]
    else:  # Single key response
        actual_permissions = data["permissions"]
    assert set(actual_permissions) == set(expected_permissions), f"Expected permissions {expected_permissions}, got {actual_permissions}"


@then("the key should be a secure random string starting with \"ak_\"")
def key_is_secure_random(context):
    """Check key is secure random string"""
    key = context.get("returned_key") or context.get("created_key", {}).get("key")
    assert key, "Key should be present"
    assert key.startswith("ak_"), f"Key should start with 'ak_', got: {key[:10]}..."
    assert len(key) > 10, "Key should be reasonably long"


@then("the key should be stored hashed in the database")
def key_stored_hashed(context, db_session: AsyncSession):
    """Check key is stored hashed"""
    from src.services.api_key_service import APIKeyService
    
    api_key_service = APIKeyService(db_session)
    key_id = context.get("api_key_id") or context.get("created_key", {}).get("id")
    assert key_id, "Key ID should be present"
    
    api_key = run_async(api_key_service.get_api_key_by_id(key_id))
    assert api_key, "API key should exist in database"
    assert api_key.key_hash, "Key should be hashed"
    # Hash should be different from plain key
    plain_key = context.get("returned_key") or context.get("created_key", {}).get("key")
    if plain_key:
        assert api_key.key_hash != plain_key, "Key should be hashed, not stored as plain text"


@then("the response should contain an expires_at field")
def response_contains_expires_at(context):
    """Check response contains expires_at"""
    response = context["response"]
    data = response.json()
    assert "expires_at" in data, "Response should contain 'expires_at' field"
    assert data["expires_at"], "expires_at should not be None"


@then(parsers.parse('the expiration should be approximately {days:d} days from now'))
def expiration_approximately(context, days: int):
    """Check expiration is approximately correct"""
    from datetime import datetime, timedelta, timezone
    response = context["response"]
    data = response.json()
    expires_at_str = data["expires_at"]
    expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
    # Make now timezone-aware for comparison
    now = datetime.now(timezone.utc)
    expected_expiry = now + timedelta(days=days)
    
    # Allow 1 hour tolerance
    diff = abs((expires_at - expected_expiry).total_seconds())
    assert diff < 3600, f"Expiration should be approximately {days} days from now, got {expires_at}"


@then("the response should contain a list of API keys")
def response_contains_list(context):
    """Check response contains list"""
    response = context["response"]
    data = response.json()
    assert "keys" in data, "Response should contain 'keys' field"
    assert isinstance(data["keys"], list), "Keys should be a list"


@then(parsers.parse('the response should contain at least {count:d} keys'))
def response_contains_count(context, count: int):
    """Check response contains at least N keys"""
    response = context["response"]
    data = response.json()
    assert len(data["keys"]) >= count, f"Response should contain at least {count} keys, got {len(data['keys'])}"


@then("each key should not contain the plain text key")
def keys_no_plain_text(context):
    """Check keys don't contain plain text"""
    response = context["response"]
    data = response.json()
    for key in data["keys"]:
        assert "key" not in key, "Keys in list should not contain plain text 'key' field"


@then("each key should contain id, scopes, permissions, created_at")
def keys_contain_fields(context):
    """Check keys contain required fields"""
    response = context["response"]
    data = response.json()
    for key in data["keys"]:
        assert "id" in key, "Key should contain 'id'"
        assert "scopes" in key, "Key should contain 'scopes'"
        assert "permissions" in key, "Key should contain 'permissions'"
        assert "created_at" in key, "Key should contain 'created_at'"


@then("the response should contain the API key id")
def response_contains_id(context):
    """Check response contains ID"""
    response = context["response"]
    data = response.json()
    assert "id" in data, "Response should contain 'id' field"
    context["viewed_key_id"] = data["id"]


@then("the response should not contain the plain text key")
def response_no_plain_text(context):
    """Check response doesn't contain plain text key"""
    response = context["response"]
    data = response.json()
    assert "key" not in data, "Response should not contain plain text 'key' field"


@then("the API key should be deleted from the database")
def api_key_deleted(context, db_session: AsyncSession):
    """Check API key is deleted"""
    from src.services.api_key_service import APIKeyService
    
    api_key_service = APIKeyService(db_session)
    key_id = context.get("api_key_id")
    assert key_id, "Key ID should be present"
    
    api_key = run_async(api_key_service.get_api_key_by_id(key_id))
    assert api_key is None, "API key should be deleted from database"


@then("the response should contain a new key field")
def response_contains_new_key(context):
    """Check response contains new key"""
    response = context["response"]
    data = response.json()
    assert "key" in data, "Response should contain 'key' field"
    context["new_key"] = data["key"]


@then("the new key should be different from the original key")
def new_key_different(context):
    """Check new key is different"""
    original_key = context.get("api_key_plain")
    new_key = context.get("new_key") or context.get("rotated_key", {}).get("key")
    assert original_key, "Original key should be present"
    assert new_key, "New key should be present"
    assert original_key != new_key, "New key should be different from original"


@then("the new API key should have the same scopes and permissions")
def new_key_same_scopes_permissions(context):
    """Check new key has same scopes/permissions"""
    response = context["response"]
    data = response.json()
    original_key = context.get("api_key")
    
    if original_key:
        original_scopes = json.loads(original_key.scopes)
        original_permissions = json.loads(original_key.permissions)
        assert set(data["scopes"]) == set(original_scopes), "New key should have same scopes"
        assert set(data["permissions"]) == set(original_permissions), "New key should have same permissions"


@then(parsers.parse('the new API key should have scopes "{scopes}"'))
def new_key_has_scopes(context, scopes: str):
    """Check new key has scopes"""
    response = context["response"]
    data = response.json()
    expected_scopes = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    assert set(data["scopes"]) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {data['scopes']}"


@then(parsers.parse('the new API key should have permissions "{permissions}"'))
def new_key_has_permissions(context, permissions: str):
    """Check new key has permissions"""
    response = context["response"]
    data = response.json()
    expected_permissions = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    assert set(data["permissions"]) == set(expected_permissions), f"Expected permissions {expected_permissions}, got {data['permissions']}"


@then("the response should indicate access denied")
def response_access_denied(context):
    """Check response indicates access denied"""
    response = context["response"]
    data = response.json()
    assert "detail" in data, "Response should contain 'detail' field"
    detail = data["detail"].lower()
    assert "access denied" in detail or "required role" in detail, f"Response should indicate access denied, got: {data['detail']}"


@then(parsers.parse('the response should indicate API key not found'))
def response_key_not_found(context):
    """Check response indicates key not found"""
    response = context["response"]
    data = response.json()
    assert "detail" in data, "Response should contain 'detail' field"
    detail = data["detail"].lower()
    assert "not found" in detail, f"Response should indicate not found, got: {data['detail']}"


@then("the two keys should be different")
def two_keys_different(context):
    """Check two keys are different"""
    key1 = context.get("created_key", {}).get("key")
    key2 = context.get("created_key_2", {}).get("key")
    assert key1, "First key should be present"
    assert key2, "Second key should be present"
    assert key1 != key2, "Two keys should be different"


@then("both keys should be stored in the database")
def both_keys_stored(context, db_session: AsyncSession):
    """Check both keys are stored"""
    from src.services.api_key_service import APIKeyService
    
    api_key_service = APIKeyService(db_session)
    key1_id = context.get("created_key", {}).get("id")
    key2_id = context.get("created_key_2", {}).get("id")
    
    assert key1_id, "First key ID should be present"
    assert key2_id, "Second key ID should be present"
    
    key1 = run_async(api_key_service.get_api_key_by_id(key1_id))
    key2 = run_async(api_key_service.get_api_key_by_id(key2_id))
    
    assert key1, "First key should be stored in database"
    assert key2, "Second key should be stored in database"


@then("the plain text key should match the stored hash when verified")
def key_matches_hash(context, db_session: AsyncSession):
    """Check plain text key matches hash"""
    from src.services.api_key_service import APIKeyService
    
    api_key_service = APIKeyService(db_session)
    key_id = context.get("created_key", {}).get("id")
    plain_key = context.get("created_key", {}).get("key")
    
    assert key_id, "Key ID should be present"
    assert plain_key, "Plain key should be present"
    
    api_key = run_async(api_key_service.get_api_key_by_id(key_id))
    assert api_key, "API key should exist in database"
    
    # Verify key matches hash
    is_valid = api_key_service._verify_key(plain_key, api_key.key_hash)
    assert is_valid, "Plain text key should match stored hash"


@then("when I request to view the API key")
def then_request_view_api_key(client: AsyncClient, context):
    """Request to view the API key (after revoke)"""
    key_id = context.get("api_key_id")
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = run_async(client.get(f"/api/v1/keys/{key_id}", headers=headers))
    context["response"] = response


@then("the old API key should be deleted from the database")
def old_api_key_deleted(context, db_session: AsyncSession):
    """Check old API key is deleted after rotation"""
    from src.services.api_key_service import APIKeyService
    
    api_key_service = APIKeyService(db_session)
    old_key_id = context.get("api_key_id")
    assert old_key_id, "Old key ID should be present"
    
    old_key = run_async(api_key_service.get_api_key_by_id(old_key_id))
    assert old_key is None, "Old API key should be deleted from database after rotation"


# Register scenarios
@scenario(FEATURE_FILE, "Admin can generate a new API key")
def test_admin_generate_api_key():
    pass


@scenario(FEATURE_FILE, "Admin can generate an API key with expiration")
def test_admin_generate_api_key_with_expiration():
    pass


@scenario(FEATURE_FILE, "Admin can list all API keys")
def test_admin_list_api_keys():
    pass


@scenario(FEATURE_FILE, "Admin can view a specific API key")
def test_admin_view_api_key():
    pass


@scenario(FEATURE_FILE, "Admin can revoke an API key")
def test_admin_revoke_api_key():
    pass


@scenario(FEATURE_FILE, "Admin can rotate an API key")
def test_admin_rotate_api_key():
    pass


@scenario(FEATURE_FILE, "Admin can rotate an API key with updated scopes")
def test_admin_rotate_api_key_with_updates():
    pass


@scenario(FEATURE_FILE, "Non-admin cannot generate API keys")
def test_non_admin_cannot_generate():
    pass


@scenario(FEATURE_FILE, "Non-admin cannot list API keys")
def test_non_admin_cannot_list():
    pass


@scenario(FEATURE_FILE, "Non-admin cannot revoke API keys")
def test_non_admin_cannot_revoke():
    pass


@scenario(FEATURE_FILE, "Non-admin cannot rotate API keys")
def test_non_admin_cannot_rotate():
    pass


@scenario(FEATURE_FILE, "Viewing non-existent API key returns 404")
def test_view_nonexistent_api_key():
    pass


@scenario(FEATURE_FILE, "Revoking non-existent API key returns 404")
def test_revoke_nonexistent_api_key():
    pass


@scenario(FEATURE_FILE, "Rotating non-existent API key returns 404")
def test_rotate_nonexistent_api_key():
    pass


@scenario(FEATURE_FILE, "Generated API keys are unique")
def test_generated_keys_unique():
    pass


@scenario(FEATURE_FILE, "API key can be validated by hash")
def test_api_key_validated_by_hash():
    pass

