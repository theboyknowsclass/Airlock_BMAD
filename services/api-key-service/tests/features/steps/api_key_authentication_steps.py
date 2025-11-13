"""
Step definitions for API Key Authentication feature
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, UTC

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

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

# Import from api-key-service
from src.main import app
from src.config import settings

# Import shared fixtures from api_key_management_steps
# Use absolute import to avoid relative import issues
import api_key_management_steps
db_engine = api_key_management_steps.db_engine
db_session = api_key_management_steps.db_session
context = api_key_management_steps.context
client = api_key_management_steps.client
run_async = api_key_management_steps.run_async

# Get feature file path
FEATURE_FILE = Path(__file__).parent.parent / "api_key_authentication.feature"


# Given steps
@given("the API key service is configured")
def api_key_service_configured():
    """API key service is configured"""
    pass


@given("the database is available")
def database_available():
    """Database is available"""
    pass


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


@given("the API key is not expired")
def api_key_not_expired(context):
    """API key is not expired"""
    # Key was just created, so it's not expired
    pass


@given("an API key exists with scopes \"read-only\" and permissions \"read\" that is expired")
def expired_api_key_exists(client: AsyncClient, context, db_session: AsyncSession):
    """Create an expired API key"""
    from src.services.api_key_service import APIKeyService
    from airlock_common.db.models.api_key import APIKey
    from sqlalchemy import update
    
    # Create API key with expiration in the past
    api_key_service = APIKeyService(db_session)
    api_key, plain_key = run_async(api_key_service.create_api_key(
        scopes=["read-only"],
        permissions=["read"],
        expires_in_days=1,
    ))
    
    # Manually set expiration to past
    expired_time = datetime.now(UTC) - timedelta(days=1)
    stmt = update(APIKey).where(APIKey.id == api_key.id).values(expires_at=expired_time)
    run_async(db_session.execute(stmt))
    run_async(db_session.commit())
    run_async(db_session.refresh(api_key))
    
    context["api_key_id"] = api_key.id
    context["api_key_plain"] = plain_key
    context["api_key"] = api_key


@given("the API key is revoked")
def api_key_revoked(context, db_session: AsyncSession):
    """Revoke the API key"""
    from src.services.api_key_service import APIKeyService
    
    api_key_service = APIKeyService(db_session)
    run_async(api_key_service.revoke_api_key(context["api_key_id"]))


@given("another API key exists with scopes \"read-write\" and permissions \"read\", \"write\"")
def another_api_key_exists(client: AsyncClient, context, db_session: AsyncSession):
    """Create another API key"""
    from src.services.api_key_service import APIKeyService
    
    api_key_service = APIKeyService(db_session)
    api_key, plain_key = run_async(api_key_service.create_api_key(
        scopes=["read-write"],
        permissions=["read", "write"],
    ))
    
    context["api_key_2_id"] = api_key.id
    context["api_key_2_plain"] = plain_key
    context["api_key_2"] = api_key


# When steps
@when("I authenticate with the API key")
def authenticate_with_api_key(client: AsyncClient, context):
    """Authenticate with API key"""
    api_key = context.get("api_key_plain")
    if not api_key:
        raise ValueError("API key not found in context")
    
    async def _authenticate():
        response = await client.post(
            "/api/v1/auth/token",
            headers={"X-API-Key": api_key},
        )
        context["response"] = response
        if response.status_code == 200:
            context["token_response"] = response.json()
    
    run_async(_authenticate())


@when(parsers.parse('I authenticate with API key "{api_key}"'))
def authenticate_with_specific_key(client: AsyncClient, context, api_key: str):
    """Authenticate with specific API key"""
    async def _authenticate():
        response = await client.post(
            "/api/v1/auth/token",
            headers={"X-API-Key": api_key},
        )
        context["response"] = response
    
    run_async(_authenticate())


@when("I authenticate without providing an API key")
def authenticate_without_key(client: AsyncClient, context):
    """Authenticate without API key"""
    async def _authenticate():
        response = await client.post(
            "/api/v1/auth/token",
        )
        context["response"] = response
    
    run_async(_authenticate())


@when("I authenticate with the expired API key")
def authenticate_with_expired_key(client: AsyncClient, context):
    """Authenticate with expired API key"""
    api_key = context.get("api_key_plain")
    async def _authenticate():
        response = await client.post(
            "/api/v1/auth/token",
            headers={"X-API-Key": api_key},
        )
        context["response"] = response
    
    run_async(_authenticate())


@when("I authenticate with the revoked API key")
def authenticate_with_revoked_key(client: AsyncClient, context):
    """Authenticate with revoked API key"""
    api_key = context.get("api_key_plain")
    async def _authenticate():
        response = await client.post(
            "/api/v1/auth/token",
            headers={"X-API-Key": api_key},
        )
        context["response"] = response
    
    run_async(_authenticate())


@when("I authenticate with the first API key")
def authenticate_with_first_key(client: AsyncClient, context):
    """Authenticate with first API key"""
    api_key = context.get("api_key_plain")
    async def _authenticate():
        response = await client.post(
            "/api/v1/auth/token",
            headers={"X-API-Key": api_key},
        )
        context["response_1"] = response
        if response.status_code == 200:
            context["token_response_1"] = response.json()
    
    run_async(_authenticate())


@when("I authenticate with the second API key")
def authenticate_with_second_key(client: AsyncClient, context):
    """Authenticate with second API key"""
    api_key = context.get("api_key_2_plain")
    async def _authenticate():
        response = await client.post(
            "/api/v1/auth/token",
            headers={"X-API-Key": api_key},
        )
        context["response_2"] = response
        if response.status_code == 200:
            context["token_response_2"] = response.json()
    
    run_async(_authenticate())


# Then steps
@then("the request should succeed with status 200")
def request_succeeds(context):
    """Request succeeded"""
    response = context.get("response")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


@then("the request should fail with status 401")
def request_fails_401(context):
    """Request failed with 401"""
    response = context.get("response")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


@then("the response should contain an access_token field")
def response_contains_access_token(context):
    """Response contains access_token"""
    token_response = context.get("token_response")
    assert token_response is not None, "Token response not found"
    assert "access_token" in token_response, "access_token not in response"


@then("the response should contain a refresh_token field")
def response_contains_refresh_token(context):
    """Response contains refresh_token"""
    token_response = context.get("token_response")
    assert "refresh_token" in token_response, "refresh_token not in response"


@then(parsers.parse('the response should contain token_type "{token_type}"'))
def response_contains_token_type(context, token_type: str):
    """Response contains token_type"""
    token_response = context.get("token_response")
    assert token_response["token_type"] == token_type, f"Expected token_type {token_type}, got {token_response.get('token_type')}"


@then("the response should contain an expires_in field")
def response_contains_expires_in(context):
    """Response contains expires_in"""
    token_response = context.get("token_response")
    assert "expires_in" in token_response, "expires_in not in response"
    assert isinstance(token_response["expires_in"], int), "expires_in should be an integer"


@then("the access token should be a valid JWT")
def access_token_is_valid_jwt(context):
    """Access token is valid JWT"""
    token_response = context.get("token_response")
    access_token = token_response["access_token"]
    
    try:
        decoded = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        context["decoded_token"] = decoded
    except Exception as e:
        pytest.fail(f"Access token is not a valid JWT: {e}")


@then(parsers.parse('the access token should contain the API key\'s scopes'))
def access_token_contains_scopes(context):
    """Access token contains scopes"""
    decoded_token = context.get("decoded_token")
    api_key = context.get("api_key")
    
    expected_scopes = json.loads(api_key.scopes)
    token_scopes = decoded_token.get("scopes", [])
    
    assert set(token_scopes) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {token_scopes}"


@then(parsers.parse('the access token should contain the API key\'s permissions'))
def access_token_contains_permissions(context):
    """Access token contains permissions"""
    decoded_token = context.get("decoded_token")
    api_key = context.get("api_key")
    
    expected_permissions = json.loads(api_key.permissions)
    token_permissions = decoded_token.get("permissions", [])
    
    assert set(token_permissions) == set(expected_permissions), f"Expected permissions {expected_permissions}, got {token_permissions}"


@then(parsers.parse('the access token should have auth_type "api_key"'))
def access_token_has_auth_type(context):
    """Access token has auth_type"""
    decoded_token = context.get("decoded_token")
    assert decoded_token.get("auth_type") == "api_key", f"Expected auth_type 'api_key', got {decoded_token.get('auth_type')}"


@then("the response should indicate invalid API key")
def response_indicates_invalid_key(context):
    """Response indicates invalid key"""
    response = context.get("response")
    detail = response.json().get("detail", "").lower()
    assert "invalid" in detail or "not found" in detail, f"Response should indicate invalid key: {response.text}"


@then("the response should indicate API key is required")
def response_indicates_key_required(context):
    """Response indicates key required"""
    response = context.get("response")
    detail = response.json().get("detail", "").lower()
    assert "required" in detail, f"Response should indicate key required: {response.text}"


@then("the response should indicate API key has expired")
def response_indicates_expired(context):
    """Response indicates expired"""
    response = context.get("response")
    detail = response.json().get("detail", "").lower()
    assert "expired" in detail, f"Response should indicate expired: {response.text}"


@then("the access token should contain sub claim")
def access_token_contains_sub(context):
    """Access token contains sub"""
    token_response = context.get("token_response")
    if not token_response:
        pytest.fail("Token response not found in context")
    
    access_token = token_response["access_token"]
    decoded_token = jwt.decode(
        access_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    context["decoded_token"] = decoded_token
    assert "sub" in decoded_token, "sub claim not in token"


@then("the access token should contain exp claim")
def access_token_contains_exp(context):
    """Access token contains exp"""
    decoded_token = context.get("decoded_token")
    assert "exp" in decoded_token, "exp claim not in token"


@then("the access token should contain iat claim")
def access_token_contains_iat(context):
    """Access token contains iat"""
    decoded_token = context.get("decoded_token")
    assert "iat" in decoded_token, "iat claim not in token"


@then("the access token should contain iss claim")
def access_token_contains_iss(context):
    """Access token contains iss"""
    decoded_token = context.get("decoded_token")
    assert "iss" in decoded_token, "iss claim not in token"


@then(parsers.parse('the access token should contain type "{token_type}"'))
def access_token_contains_type(context, token_type: str):
    """Access token contains type"""
    decoded_token = context.get("decoded_token")
    assert decoded_token.get("type") == token_type, f"Expected type {token_type}, got {decoded_token.get('type')}"


@then("the access token should contain api_key_id claim")
def access_token_contains_api_key_id(context):
    """Access token contains api_key_id"""
    decoded_token = context.get("decoded_token")
    assert "api_key_id" in decoded_token, "api_key_id claim not in token"


@then(parsers.parse('the access token should contain scopes "{scopes}"'))
def access_token_contains_specific_scopes(context, scopes: str):
    """Access token contains specific scopes"""
    token_response = context.get("token_response")
    if not token_response:
        pytest.fail("Token response not found in context")
    
    access_token = token_response["access_token"]
    decoded_token = jwt.decode(
        access_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    context["decoded_token"] = decoded_token
    expected_scopes = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    token_scopes = decoded_token.get("scopes", [])
    assert set(token_scopes) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {token_scopes}"


@then(parsers.parse('the access token should contain permissions "{permissions}"'))
def access_token_contains_specific_permissions(context, permissions: str):
    """Access token contains specific permissions"""
    decoded_token = context.get("decoded_token")
    expected_permissions = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    token_permissions = decoded_token.get("permissions", [])
    assert set(token_permissions) == set(expected_permissions), f"Expected permissions {expected_permissions}, got {token_permissions}"


@then(parsers.parse('the refresh token should contain scopes "{scopes}"'))
def refresh_token_contains_scopes(context, scopes: str):
    """Refresh token contains scopes"""
    token_response = context.get("token_response")
    refresh_token = token_response["refresh_token"]
    
    decoded = jwt.decode(
        refresh_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    
    expected_scopes = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    token_scopes = decoded.get("scopes", [])
    assert set(token_scopes) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {token_scopes}"


@then(parsers.parse('the refresh token should contain permissions "{permissions}"'))
def refresh_token_contains_permissions(context, permissions: str):
    """Refresh token contains permissions"""
    token_response = context.get("token_response")
    refresh_token = token_response["refresh_token"]
    
    decoded = jwt.decode(
        refresh_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    
    expected_permissions = [p.strip().strip('"').strip("'") for p in permissions.split(",")]
    token_permissions = decoded.get("permissions", [])
    assert set(token_permissions) == set(expected_permissions), f"Expected permissions {expected_permissions}, got {token_permissions}"


@then("the two access tokens should be different")
def tokens_are_different(context):
    """Tokens are different"""
    token_response_1 = context.get("token_response_1")
    token_response_2 = context.get("token_response_2")
    
    assert token_response_1["access_token"] != token_response_2["access_token"], "Tokens should be different"


@then(parsers.parse('the first token should contain scopes "{scopes}"'))
def first_token_contains_scopes(context, scopes: str):
    """First token contains scopes"""
    token_response_1 = context.get("token_response_1")
    access_token = token_response_1["access_token"]
    
    decoded = jwt.decode(
        access_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    
    expected_scopes = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    token_scopes = decoded.get("scopes", [])
    assert set(token_scopes) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {token_scopes}"


@then(parsers.parse('the second token should contain scopes "{scopes}"'))
def second_token_contains_scopes(context, scopes: str):
    """Second token contains scopes"""
    token_response_2 = context.get("token_response_2")
    access_token = token_response_2["access_token"]
    
    decoded = jwt.decode(
        access_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    
    expected_scopes = [s.strip().strip('"').strip("'") for s in scopes.split(",")]
    token_scopes = decoded.get("scopes", [])
    assert set(token_scopes) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {token_scopes}"


# Scenario registrations
@scenario(FEATURE_FILE, "Valid API key can authenticate and receive tokens")
def test_valid_api_key_authenticates():
    pass


@scenario(FEATURE_FILE, "Valid API key with expiration can authenticate")
def test_valid_api_key_with_expiration():
    pass


@scenario(FEATURE_FILE, "Invalid API key returns 401")
def test_invalid_api_key_returns_401():
    pass


@scenario(FEATURE_FILE, "Missing API key header returns 401")
def test_missing_api_key_returns_401():
    pass


@scenario(FEATURE_FILE, "Expired API key returns 401")
def test_expired_api_key_returns_401():
    pass


@scenario(FEATURE_FILE, "Revoked API key cannot authenticate")
def test_revoked_api_key_cannot_authenticate():
    pass


@scenario(FEATURE_FILE, "Token structure matches user authentication tokens")
def test_token_structure_matches():
    pass


@scenario(FEATURE_FILE, "Tokens include correct scopes and permissions")
def test_tokens_include_scopes_permissions():
    pass


@scenario(FEATURE_FILE, "Different API keys receive different tokens")
def test_different_keys_different_tokens():
    pass
