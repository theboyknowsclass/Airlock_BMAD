"""
Step definitions for RBAC feature
"""
import os
import sys
from pathlib import Path
from typing import List, Optional

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from pytest_bdd import given, when, then, parsers, scenario
from src.dependencies.auth import (
    get_current_user,
    UserContext,
    require_role,
    require_any_role,
    require_all_roles,
    require_submitter,
    require_reviewer,
    require_admin,
)
from src.utils.jwt import create_access_token
from src.config import settings

# Get feature file path
FEATURE_FILE = Path(__file__).parent.parent / "rbac.feature"


# Create test app with RBAC-protected endpoints
app = FastAPI()


@app.get("/submission")
async def submission_endpoint(
    current_user: UserContext = Depends(require_submitter()),
):
    """Test endpoint that requires submitter role"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


@app.get("/review")
async def review_endpoint(
    current_user: UserContext = Depends(require_reviewer()),
):
    """Test endpoint that requires reviewer role"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


@app.get("/admin")
async def admin_endpoint(
    current_user: UserContext = Depends(require_admin()),
):
    """Test endpoint that requires admin role"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


@app.get("/any-role")
async def any_role_endpoint(
    current_user: UserContext = Depends(require_any_role("reviewer", "admin")),
):
    """Test endpoint that requires any of reviewer or admin roles"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


@app.get("/all-roles")
async def all_roles_endpoint(
    current_user: UserContext = Depends(require_all_roles("admin", "reviewer")),
):
    """Test endpoint that requires all of admin and reviewer roles"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


# We'll use a different approach for custom role endpoint
# Create endpoints for each role used in scenario outline
@app.get("/custom-role/submitter")
async def custom_submitter_endpoint(
    current_user: UserContext = Depends(require_role("submitter")),
):
    """Test endpoint that requires submitter role"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


@app.get("/custom-role/reviewer")
async def custom_reviewer_endpoint(
    current_user: UserContext = Depends(require_role("reviewer")),
):
    """Test endpoint that requires reviewer role"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


@app.get("/custom-role/admin")
async def custom_admin_endpoint(
    current_user: UserContext = Depends(require_role("admin")),
):
    """Test endpoint that requires admin role"""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.roles,
    }


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
    # Parse roles, removing quotes and whitespace
    roles_list = [r.strip().strip('"').strip("'") for r in roles.split(",")]
    # Filter out empty strings
    roles_list = [r for r in roles_list if r]
    token = create_access_token(
        user_id=user_id,
        username=username,
        roles=roles_list,
    )
    context["token"] = token
    context["expected_user_id"] = user_id
    context["expected_username"] = username
    context["expected_roles"] = roles_list


@given("I have no authentication token")
def no_token(context):
    """Set no token in context"""
    context["token"] = None


# When steps
@when("I make a request to a submitter-only endpoint with the token")
def request_submitter_endpoint_with_token(client, context):
    """Make request to submitter-only endpoint with token"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get("/submission", headers=headers)


@when("I make a request to a reviewer-only endpoint with the token")
def request_reviewer_endpoint_with_token(client, context):
    """Make request to reviewer-only endpoint with token"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get("/review", headers=headers)


@when("I make a request to an admin-only endpoint with the token")
def request_admin_endpoint_with_token(client, context):
    """Make request to admin-only endpoint with token"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get("/admin", headers=headers)


@when(parsers.parse('I make a request to an endpoint requiring any role "{roles}" with the token'))
def request_any_role_endpoint_with_token(client, context, roles: str):
    """Make request to endpoint requiring any of the specified roles"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get("/any-role", headers=headers)


@when(parsers.parse('I make a request to an endpoint requiring all roles "{roles}" with the token'))
def request_all_roles_endpoint_with_token(client, context, roles: str):
    """Make request to endpoint requiring all of the specified roles"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get("/all-roles", headers=headers)


@when(parsers.parse('I make a request to an endpoint requiring role "{required_role}" with the token'))
def request_custom_role_endpoint_with_token(client, context, required_role: str):
    """Make request to endpoint requiring a specific role (for scenario outline)"""
    token = context.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    context["response"] = client.get(f"/custom-role/{required_role}", headers=headers)


@when("I make a request to a submitter-only endpoint")
def request_submitter_endpoint(client, context):
    """Make request to submitter-only endpoint without token"""
    context["response"] = client.get("/submission")


# Then steps
@then(parsers.parse('the request should succeed with status {status_code:d}'))
def request_succeeds(context, status_code: int):
    """Verify request succeeded with expected status"""
    response = context["response"]
    assert response.status_code == status_code, \
        f"Expected {status_code}, got {response.status_code}: {response.json()}"


@then(parsers.parse('the request should fail with status {status_code:d}'))
def request_fails(context, status_code: int):
    """Verify request failed with expected status"""
    response = context["response"]
    assert response.status_code == status_code, \
        f"Expected {status_code}, got {response.status_code}: {response.json()}"


@then(parsers.parse('the request should fail with status {status_code1:d} or {status_code2:d}'))
def request_fails_with_either(context, status_code1: int, status_code2: int):
    """Verify request failed with one of expected status codes"""
    response = context["response"]
    assert response.status_code in [status_code1, status_code2], \
        f"Expected {status_code1} or {status_code2}, got {response.status_code}: {response.json()}"


@then("the response should indicate access granted")
def response_indicates_access_granted(context):
    """Verify response indicates access was granted"""
    response = context["response"]
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Access granted" in data["message"] or data["message"] == "Access granted"


@then(parsers.parse('the response should indicate "{message}"'))
def response_indicates_message(context, message: str):
    """Verify response contains expected message"""
    response = context["response"]
    data = response.json()
    assert "detail" in data
    assert message in data["detail"]


@then("the response should indicate missing authentication")
def response_indicates_missing_auth(context):
    """Verify response indicates missing authentication"""
    response = context["response"]
    assert response.status_code in [401, 403]
    assert "detail" in response.json()


@then("if the request failed, the response should indicate access denied")
def response_indicates_access_denied_if_failed(context):
    """Verify response indicates access denied if request failed"""
    response = context["response"]
    if response.status_code != 200:
        data = response.json()
        assert "detail" in data
        assert "Access denied" in data["detail"] or "denied" in data["detail"].lower()


@then(parsers.parse('the request should <result> with status <status_code>'))
def request_result_with_status(context, result: str, status_code: int):
    """Verify request result and status code (for scenario outline)"""
    response = context["response"]
    if result == "succeed":
        assert response.status_code == status_code, \
            f"Expected {status_code}, got {response.status_code}: {response.json()}"
    else:  # fail
        assert response.status_code == status_code, \
            f"Expected {status_code}, got {response.status_code}: {response.json()}"


# Register scenarios from feature file
@scenario(FEATURE_FILE, "Submitter can access submission endpoint")
def test_submitter_can_access_submission():
    pass


@scenario(FEATURE_FILE, "Submitter cannot access reviewer endpoint")
def test_submitter_cannot_access_reviewer():
    pass


@scenario(FEATURE_FILE, "Submitter cannot access admin endpoint")
def test_submitter_cannot_access_admin():
    pass


@scenario(FEATURE_FILE, "Reviewer can access reviewer endpoint")
def test_reviewer_can_access_reviewer():
    pass


@scenario(FEATURE_FILE, "Reviewer cannot access submission endpoint")
def test_reviewer_cannot_access_submission():
    pass


@scenario(FEATURE_FILE, "Reviewer cannot access admin endpoint")
def test_reviewer_cannot_access_admin():
    pass


@scenario(FEATURE_FILE, "Admin can access all endpoints")
def test_admin_can_access_submission():
    pass


@scenario(FEATURE_FILE, "Admin can access reviewer endpoint")
def test_admin_can_access_reviewer():
    pass


@scenario(FEATURE_FILE, "Admin can access admin endpoint")
def test_admin_can_access_admin():
    pass


@scenario(FEATURE_FILE, "User with multiple roles can access any of their role endpoints")
def test_multi_role_can_access_submitter():
    pass


@scenario(FEATURE_FILE, "User with multiple roles can access reviewer endpoint")
def test_multi_role_can_access_reviewer():
    pass


@scenario(FEATURE_FILE, "User with multiple roles cannot access admin endpoint")
def test_multi_role_cannot_access_admin():
    pass


@scenario(FEATURE_FILE, "Endpoint requiring any role accepts user with one matching role")
def test_any_role_one_matching():
    pass


@scenario(FEATURE_FILE, "Endpoint requiring any role accepts user with multiple matching roles")
def test_any_role_multiple_matching():
    pass


@scenario(FEATURE_FILE, "Endpoint requiring any role rejects user with no matching roles")
def test_any_role_no_matching():
    pass


@scenario(FEATURE_FILE, "Endpoint requiring all roles accepts user with all required roles")
def test_all_roles_all_present():
    pass


@scenario(FEATURE_FILE, "Endpoint requiring all roles rejects user missing one required role")
def test_all_roles_missing_one():
    pass


@scenario(FEATURE_FILE, "Endpoint requiring all roles rejects user missing multiple required roles")
def test_all_roles_missing_multiple():
    pass


@scenario(FEATURE_FILE, "Unauthenticated request to role-protected endpoint is rejected")
def test_unauthenticated_rejected():
    pass


@scenario(FEATURE_FILE, "Role-based access control enforces correct permissions")
def test_rbac_enforces_permissions():
    pass

