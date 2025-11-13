"""
Step definitions for JWT token validation feature
"""
import os
import sys
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import List, Optional

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
import jwt

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from pytest_bdd import given, when, then, parsers, scenario
from src.dependencies.auth import get_current_user, get_optional_user, UserContext
from airlock_common import JWTConfig, create_user_access_token, create_user_refresh_token
from src.config import settings

# Get feature file path
FEATURE_FILE = Path(__file__).parent.parent / "jwt_token_validation.feature"


# Create test app
app = FastAPI()


@app.get("/protected")
async def protected_endpoint(
    current_user: UserContext = Depends(get_current_user),
):
    """Test endpoint that requires authentication"""
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


@app.get("/optional")
async def optional_endpoint(
    current_user: Optional[UserContext] = Depends(get_optional_user),
):
    """Test endpoint with optional authentication"""
    if current_user:
        return {
            "authenticated": True,
            "user_id": current_user.user_id,
            "username": current_user.username,
            "roles": current_user.roles,
        }
    return {"authenticated": False}


# Test client fixture
@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def context():
    """Test context for storing state between steps"""
    return {}


# Given steps
@given("the authentication service is configured")
def auth_service_configured(context):
    """Verify authentication service is configured"""
    assert settings.JWT_SECRET_KEY is not None
    assert settings.JWT_ALGORITHM is not None


@given("JWT secret key is set")
def jwt_secret_key_set(context):
    """Verify JWT secret key is set"""
    assert settings.JWT_SECRET_KEY is not None


@given(parsers.parse('I have a valid access token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def valid_access_token_with_roles(context, user_id: str, username: str, roles: str):
    """Create a valid access token with specified user and roles"""
    roles_list = [r.strip() for r in roles.split(",")]
    jwt_config = JWTConfig(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        issuer=settings.JWT_ISSUER,
        access_token_expiry_minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES,
        refresh_token_expiry_days=settings.REFRESH_TOKEN_EXPIRY_DAYS,
    )
    token = create_user_access_token(
        config=jwt_config,
        user_id=user_id,
        username=username,
        roles=roles_list,
    )
    context["token"] = token
    context["expected_user_id"] = user_id
    context["expected_username"] = username
    context["expected_roles"] = roles_list


@given(parsers.parse('I have a valid access token for user "{user_id}" without roles'))
def valid_access_token_without_roles(context, user_id: str):
    """Create a valid access token without roles"""
    # Create token without roles by manually encoding
    now = datetime.now(UTC)
    exp_timestamp = int((now + timedelta(minutes=15)).timestamp())
    iat_timestamp = int(now.timestamp())
    
    claims = {
        "sub": user_id,
        "username": user_id,
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    
    token = jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    context["token"] = token
    context["expected_user_id"] = user_id
    context["expected_roles"] = ["submitter"]  # Should default to submitter


@given(parsers.parse('I have a valid refresh token for user "{user_id}"'))
def valid_refresh_token(context, user_id: str):
    """Create a valid refresh token"""
    jwt_config = JWTConfig(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        issuer=settings.JWT_ISSUER,
        access_token_expiry_minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES,
        refresh_token_expiry_days=settings.REFRESH_TOKEN_EXPIRY_DAYS,
    )
    token = create_user_refresh_token(
        config=jwt_config,
        user_id=user_id,
        username=user_id,
        roles=["submitter"],
    )
    context["token"] = token


@given(parsers.parse('I have an expired access token for user "{user_id}"'))
def expired_access_token(context, user_id: str):
    """Create an expired access token"""
    now = datetime.utcnow()
    exp_timestamp = int((now - timedelta(hours=1)).timestamp())
    iat_timestamp = int((now - timedelta(hours=2)).timestamp())
    
    claims = {
        "sub": user_id,
        "username": user_id,
        "roles": ["submitter"],
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    
    token = jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    context["token"] = token


@given(parsers.parse('I have a token signed with wrong secret key for user "{user_id}"'))
def token_with_wrong_secret(context, user_id: str):
    """Create a token signed with wrong secret key"""
    wrong_secret = "wrong-secret-key"
    now = datetime.utcnow()
    exp_timestamp = int((now + timedelta(minutes=15)).timestamp())
    iat_timestamp = int(now.timestamp())
    
    claims = {
        "sub": user_id,
        "username": user_id,
        "roles": ["submitter"],
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    
    token = jwt.encode(
        claims,
        wrong_secret,
        algorithm=settings.JWT_ALGORITHM,
    )
    context["token"] = token


@given("I have an access token without user ID")
def token_without_user_id(context):
    """Create an access token without user ID"""
    now = datetime.utcnow()
    exp_timestamp = int((now + timedelta(minutes=15)).timestamp())
    iat_timestamp = int(now.timestamp())
    
    claims = {
        "username": "testuser",
        "roles": ["submitter"],
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    
    token = jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    context["token"] = token


@given("I have no authentication token")
def no_token(context):
    """Set no token in context"""
    context["token"] = None


@given(parsers.parse('I have an invalid authentication token "{token}"'))
def invalid_token(context, token: str):
    """Set invalid token in context"""
    context["token"] = token


# When steps
@when("I make a request to a protected endpoint with the token")
def request_protected_endpoint_with_token(client, context):
    """Make request to protected endpoint with token"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get("/protected", headers=headers)


@when("I make a request to a protected endpoint")
def request_protected_endpoint(client, context):
    """Make request to protected endpoint without token"""
    context["response"] = client.get("/protected")


@when("I make a request to an optional authentication endpoint with the token")
def request_optional_endpoint_with_token(client, context):
    """Make request to optional endpoint with token"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get("/optional", headers=headers)


@when("I make a request to an optional authentication endpoint")
def request_optional_endpoint(client, context):
    """Make request to optional endpoint without token"""
    context["response"] = client.get("/optional")


# Then steps
@then(parsers.parse('the request should succeed with status {status_code:d}'))
def request_succeeds(context, status_code: int):
    """Verify request succeeded with expected status"""
    response = context["response"]
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.json()}"


@then(parsers.parse('the request should fail with status {status_code:d}'))
def request_fails(context, status_code: int):
    """Verify request failed with expected status"""
    response = context["response"]
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.json()}"


@then(parsers.parse('the request should fail with status {status_code1:d} or {status_code2:d}'))
def request_fails_with_either(context, status_code1: int, status_code2: int):
    """Verify request failed with one of expected status codes"""
    response = context["response"]
    assert response.status_code in [status_code1, status_code2], \
        f"Expected {status_code1} or {status_code2}, got {response.status_code}: {response.json()}"


@then(parsers.parse('the response should contain user_id "{user_id}"'))
def response_contains_user_id(context, user_id: str):
    """Verify response contains expected user ID"""
    response = context["response"]
    data = response.json()
    assert data["user_id"] == user_id, f"Expected user_id {user_id}, got {data.get('user_id')}"


@then(parsers.parse('the response should contain username "{username}"'))
def response_contains_username(context, username: str):
    """Verify response contains expected username"""
    response = context["response"]
    data = response.json()
    assert data["username"] == username, f"Expected username {username}, got {data.get('username')}"


@then(parsers.parse('the response should contain roles "{roles}"'))
def response_contains_roles(context, roles: str):
    """Verify response contains expected roles"""
    response = context["response"]
    data = response.json()
    expected_roles = [r.strip() for r in roles.split(",")]
    actual_roles = data["roles"]
    assert set(actual_roles) == set(expected_roles), \
        f"Expected roles {expected_roles}, got {actual_roles}"


@then("the response should indicate missing authentication")
def response_indicates_missing_auth(context):
    """Verify response indicates missing authentication"""
    response = context["response"]
    assert response.status_code in [401, 403]
    assert "detail" in response.json()


@then("the response should indicate invalid token")
def response_indicates_invalid_token(context):
    """Verify response indicates invalid token"""
    response = context["response"]
    assert response.status_code == 401
    assert "detail" in response.json()
    detail = response.json()["detail"].lower()
    assert "invalid" in detail or "expired" in detail or "token" in detail


@then(parsers.parse('the response should indicate "{message}"'))
def response_indicates_message(context, message: str):
    """Verify response contains expected message"""
    response = context["response"]
    assert response.status_code == 401
    assert "detail" in response.json()
    assert message in response.json()["detail"]


@then("the response should indicate expired or invalid token")
def response_indicates_expired_or_invalid(context):
    """Verify response indicates expired or invalid token"""
    response = context["response"]
    assert response.status_code == 401
    assert "detail" in response.json()
    detail = response.json()["detail"].lower()
    assert "expired" in detail or "invalid" in detail


@then("the response should indicate missing user ID")
def response_indicates_missing_user_id(context):
    """Verify response indicates missing user ID"""
    response = context["response"]
    assert response.status_code == 401
    assert "detail" in response.json()
    detail = response.json()["detail"].lower()
    assert "user id" in detail or "missing" in detail


@then("the response should indicate authenticated false")
def response_indicates_not_authenticated(context):
    """Verify response indicates not authenticated"""
    response = context["response"]
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False


@then("the response should indicate authenticated true")
def response_indicates_authenticated(context):
    """Verify response indicates authenticated"""
    response = context["response"]
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True


# Register scenarios from feature file
@scenario(FEATURE_FILE, "Valid access token is accepted")
def test_valid_access_token():
    pass


@scenario(FEATURE_FILE, "Request without token is rejected")
def test_request_without_token():
    pass


@scenario(FEATURE_FILE, "Invalid token is rejected")
def test_invalid_token():
    pass


@scenario(FEATURE_FILE, "Refresh token cannot be used for protected endpoints")
def test_refresh_token_rejected():
    pass


@scenario(FEATURE_FILE, "Expired token is rejected")
def test_expired_token():
    pass


@scenario(FEATURE_FILE, "Token with wrong secret key is rejected")
def test_wrong_secret():
    pass


@scenario(FEATURE_FILE, "Token with missing user ID is rejected")
def test_missing_user_id():
    pass


@scenario(FEATURE_FILE, "Token without roles defaults to submitter role")
def test_default_roles():
    pass


@scenario(FEATURE_FILE, "Optional endpoint accepts requests without token")
def test_optional_no_token():
    pass


@scenario(FEATURE_FILE, "Optional endpoint accepts requests with valid token")
def test_optional_valid_token():
    pass


@scenario(FEATURE_FILE, "Optional endpoint handles invalid token gracefully")
def test_optional_invalid_token():
    pass


@scenario(FEATURE_FILE, "User context is correctly extracted from token")
def test_user_context_extraction():
    pass

