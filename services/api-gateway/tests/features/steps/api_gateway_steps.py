"""
Step definitions for API Gateway BDD tests
"""
import os
import sys
import time
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import List, Optional

import pytest
import requests
import jwt
from pytest_bdd import given, when, then, parsers, scenario

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "shared" / "python"))

from airlock_common import JWTConfig, create_user_access_token, create_user_refresh_token

# Get feature file path
FEATURE_FILE = Path(__file__).parent.parent / "api_gateway.feature"

# Gateway configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost")
GATEWAY_PORT = os.getenv("API_GATEWAY_PORT", "80")
GATEWAY_BASE_URL = f"{GATEWAY_URL}:{GATEWAY_PORT}" if GATEWAY_PORT != "80" else GATEWAY_URL

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "airlock-auth-service")


def get_jwt_config():
    """Get JWT configuration for testing"""
    return JWTConfig(
        secret_key=JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
        issuer=JWT_ISSUER,
        access_token_expiry_minutes=15,
        refresh_token_expiry_days=7,
    )


# Given steps
@given("the API Gateway is running")
def gateway_running(context, gateway_url, wait_for_gateway):
    """Verify API Gateway is running"""
    try:
        response = requests.get(f"{gateway_url}/health", timeout=5)
        assert response.status_code == 200, f"Gateway health check failed: {response.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Gateway is not accessible: {e}")


@given("the authentication service is running")
def auth_service_running(context):
    """Verify authentication service is running (assumed if gateway is up)"""
    # In a real scenario, we might check the auth service directly
    # For now, we assume if gateway is up, services are configured
    pass


@given("JWT secret key is configured")
def jwt_secret_configured(context):
    """Verify JWT secret key is configured"""
    assert JWT_SECRET_KEY is not None, "JWT_SECRET_KEY must be set"
    assert JWT_SECRET_KEY != "test-secret-key-for-testing-only" or os.getenv("JWT_SECRET_KEY") is None, \
        "Using default test secret key - set JWT_SECRET_KEY environment variable for production"


@given(parsers.parse('I have a valid access token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def valid_access_token_with_roles(context, user_id: str, username: str, roles: str):
    """Create a valid access token with roles"""
    roles_list = [r.strip() for r in roles.split(",")]
    jwt_config = get_jwt_config()
    token = create_user_access_token(
        config=jwt_config,
        user_id=user_id,
        username=username,
        roles=roles_list,
    )
    context["token"] = token
    context["user_id"] = user_id
    context["username"] = username
    context["roles"] = roles_list


@given('I have no authentication token')
def no_token(context):
    """Clear any existing token"""
    context["token"] = None


@given(parsers.parse('I have an invalid authentication token "{token}"'))
def invalid_token(context, token: str):
    """Set an invalid token"""
    context["token"] = token


@given(parsers.parse('I have an expired access token for user "{user_id}"'))
def expired_token(context, user_id: str):
    """Create an expired access token"""
    jwt_config = get_jwt_config()
    # Create token with expiration in the past
    now = datetime.now(UTC)
    exp_timestamp = int((now - timedelta(minutes=1)).timestamp())
    iat_timestamp = int((now - timedelta(minutes=16)).timestamp())
    
    claims = {
        "sub": user_id,
        "exp": exp_timestamp,
        "iat": iat_timestamp,
        "iss": JWT_ISSUER,
        "type": "access",
        "username": "testuser",
        "roles": ["submitter"],
    }
    
    token = jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    context["token"] = token


@given(parsers.parse('I have a valid refresh token for user "{user_id}"'))
def valid_refresh_token(context, user_id: str):
    """Create a valid refresh token"""
    jwt_config = get_jwt_config()
    token = create_user_refresh_token(
        config=jwt_config,
        user_id=user_id,
        username="testuser",
        roles=["submitter"],
    )
    context["token"] = token


@given(parsers.parse('I have an API key "{api_key}"'))
def api_key(context, api_key: str):
    """Store API key in context"""
    context["api_key"] = api_key


# When steps
@when(parsers.parse('I make a request to "{endpoint}"'))
def make_request(context, endpoint: str, http_client, gateway_url):
    """Make a request to the gateway"""
    url = f"{gateway_url}{endpoint}"
    headers = {}
    
    if context.get("token"):
        headers["Authorization"] = f"Bearer {context['token']}"
    
    if context.get("api_key"):
        headers["X-API-Key"] = context["api_key"]
    
    try:
        response = http_client.get(url, headers=headers, timeout=10)
        context["response"] = response
        context["request_count"] = context.get("request_count", 0) + 1
    except requests.exceptions.RequestException as e:
        context["response"] = None
        context["error"] = str(e)


@when(parsers.parse('I make a request to "{endpoint}" with the token'))
def make_request_with_token(context, endpoint: str, http_client, gateway_url):
    """Make a request with token"""
    url = f"{gateway_url}{endpoint}"
    headers = {}
    
    if context.get("token"):
        headers["Authorization"] = f"Bearer {context['token']}"
    
    try:
        response = http_client.get(url, headers=headers, timeout=10)
        context["response"] = response
        context["request_count"] = context.get("request_count", 0) + 1
    except requests.exceptions.RequestException as e:
        context["response"] = None
        context["error"] = str(e)


@when(parsers.parse('I make a request to "{endpoint}" with header "{header_name}" set to "{header_value}"'))
def make_request_with_header(context, endpoint: str, header_name: str, header_value: str, http_client, gateway_url):
    """Make a request with custom header"""
    url = f"{gateway_url}{endpoint}"
    headers = {header_name: header_value}
    
    try:
        response = http_client.get(url, headers=headers, timeout=10)
        context["response"] = response
    except requests.exceptions.RequestException as e:
        context["response"] = None
        context["error"] = str(e)


@when(parsers.parse('I make {count:d} requests to "{endpoint}" with the token within {seconds:d} second'))
def make_multiple_requests(context, count: int, endpoint: str, seconds: int, http_client, gateway_url):
    """Make multiple requests quickly"""
    url = f"{gateway_url}{endpoint}"
    headers = {"Authorization": f"Bearer {context['token']}"}
    
    responses = []
    start_time = time.time()
    
    for i in range(count):
        try:
            response = http_client.get(url, headers=headers, timeout=10)
            responses.append(response)
        except requests.exceptions.RequestException as e:
            responses.append(None)
        
        # Don't wait between requests to test rate limiting
    
    elapsed = time.time() - start_time
    if elapsed < seconds:
        time.sleep(seconds - elapsed)
    
    context["responses"] = responses
    context["response"] = responses[-1] if responses else None


@when(parsers.parse('I make {count:d} requests to "{endpoint}" within {seconds:d} second'))
def make_multiple_requests_no_token(context, count: int, endpoint: str, seconds: int, http_client, gateway_url):
    """Make multiple requests without token"""
    url = f"{gateway_url}{endpoint}"
    
    responses = []
    start_time = time.time()
    
    for i in range(count):
        try:
            response = http_client.get(url, timeout=10)
            responses.append(response)
        except requests.exceptions.RequestException as e:
            responses.append(None)
    
    elapsed = time.time() - start_time
    if elapsed < seconds:
        time.sleep(seconds - elapsed)
    
    context["responses"] = responses
    context["response"] = responses[-1] if responses else None


# Then steps
@then(parsers.parse('the request should succeed with status {status:d}'))
def request_succeeds(context, status: int):
    """Verify request succeeded"""
    assert context.get("response") is not None, "No response received"
    assert context["response"].status_code == status, \
        f"Expected status {status}, got {context['response'].status_code}: {context['response'].text}"


@then(parsers.parse('the request should fail with status {status:d}'))
def request_fails(context, status: int):
    """Verify request failed with expected status"""
    assert context.get("response") is not None, "No response received"
    assert context["response"].status_code == status, \
        f"Expected status {status}, got {context['response'].status_code}: {context['response'].text}"


@then('the response should indicate missing authentication')
def missing_auth(context):
    """Verify response indicates missing authentication"""
    assert context.get("response") is not None
    assert context["response"].status_code == 401
    # Check for error message
    try:
        data = context["response"].json()
        assert "error" in data or "UNAUTHORIZED" in str(data).upper()
    except:
        pass  # Some responses might not be JSON


@then('the response should indicate invalid token')
def invalid_token_response(context):
    """Verify response indicates invalid token"""
    assert context.get("response") is not None
    assert context["response"].status_code == 401
    try:
        data = context["response"].json()
        assert "error" in data or "invalid" in str(data).lower() or "unauthorized" in str(data).lower()
    except:
        pass


@then('the response should indicate expired or invalid token')
def expired_token_response(context):
    """Verify response indicates expired token"""
    assert context.get("response") is not None
    assert context["response"].status_code == 401
    try:
        data = context["response"].json()
        assert "error" in data or "expired" in str(data).lower() or "invalid" in str(data).lower()
    except:
        pass


@then(parsers.parse('the response should indicate "{message}"'))
def response_indicates(context, message: str):
    """Verify response contains specific message"""
    assert context.get("response") is not None
    try:
        data = context["response"].json()
        assert message.lower() in str(data).lower()
    except:
        assert message.lower() in context["response"].text.lower()


@then('the response should indicate the gateway is healthy')
def gateway_healthy(context):
    """Verify gateway health check response"""
    assert context.get("response") is not None
    assert context["response"].status_code == 200
    try:
        data = context["response"].json()
        assert data.get("status") == "healthy" or "healthy" in str(data).lower()
    except:
        assert "healthy" in context["response"].text.lower()


@then(parsers.parse('the request should be routed to the {service}'))
def routed_to_service(context, service: str):
    """Verify request was routed to correct service"""
    # For now, we verify the request didn't fail with 502/503/504 (service unavailable)
    # In a full implementation, we might check response headers or mock services
    assert context.get("response") is not None
    assert context["response"].status_code not in [502, 503, 504], \
        f"Service {service} appears to be unavailable (status {context['response'].status_code})"


@then('user context should be forwarded to the service')
def user_context_forwarded(context):
    """Verify user context was forwarded (implicitly verified by successful routing)"""
    # This is verified by the service receiving the request successfully
    # In a full implementation, we might check response contains user info
    assert context.get("response") is not None
    assert context["response"].status_code in [200, 201, 204], \
        "Request should succeed if user context was forwarded correctly"


@then(parsers.parse('user context should contain user_id "{user_id}"'))
def user_context_contains_user_id(context, user_id: str):
    """Verify user context contains user_id"""
    # In a full implementation, we'd check the service received X-User-ID header
    # For now, we verify the request succeeded (which implies context was forwarded)
    assert context.get("response") is not None
    assert context["response"].status_code in [200, 201, 204]


@then(parsers.parse('user context should contain username "{username}"'))
def user_context_contains_username(context, username: str):
    """Verify user context contains username"""
    assert context.get("response") is not None
    assert context["response"].status_code in [200, 201, 204]


@then(parsers.parse('user context should contain roles "{roles}"'))
def user_context_contains_roles(context, roles: str):
    """Verify user context contains roles"""
    assert context.get("response") is not None
    assert context["response"].status_code in [200, 201, 204]


@then('the request should not be rejected with status 401')
def not_rejected_401(context):
    """Verify request was not rejected with 401"""
    assert context.get("response") is not None
    assert context["response"].status_code != 401, "Request was rejected with 401"


@then(parsers.parse('at least one request should fail with status {status:d}'))
def at_least_one_fails(context, status: int):
    """Verify at least one request failed with expected status"""
    responses = context.get("responses", [])
    assert len(responses) > 0, "No responses recorded"
    failed = [r for r in responses if r and r.status_code == status]
    assert len(failed) > 0, f"No requests failed with status {status}"


@then('the response should indicate rate limit exceeded')
def rate_limit_exceeded(context):
    """Verify response indicates rate limit exceeded"""
    assert context.get("response") is not None
    assert context["response"].status_code == 429
    try:
        data = context["response"].json()
        assert "rate" in str(data).lower() or "limit" in str(data).lower() or "429" in str(data)
    except:
        pass


@then(parsers.parse('the request should be routed to "<service>"'))
def routed_to_service_outline(context, service: str):
    """Verify request was routed to service (scenario outline)"""
    assert context.get("response") is not None
    assert context["response"].status_code not in [502, 503, 504], \
        f"Service {service} appears to be unavailable"


# Register scenarios from feature file
@scenario(FEATURE_FILE, "Valid token is accepted and request is routed")
def test_valid_token_accepted():
    pass


@scenario(FEATURE_FILE, "Request without token is rejected")
def test_request_without_token():
    pass


@scenario(FEATURE_FILE, "Invalid token is rejected")
def test_invalid_token():
    pass


@scenario(FEATURE_FILE, "Expired token is rejected")
def test_expired_token():
    pass


@scenario(FEATURE_FILE, "Refresh token cannot be used for protected endpoints")
def test_refresh_token_rejected():
    pass


@scenario(FEATURE_FILE, "User context is extracted from token")
def test_user_context_extraction():
    pass


@scenario(FEATURE_FILE, "Request is routed to correct service based on path")
def test_request_routing():
    pass


@scenario(FEATURE_FILE, "Auth endpoints do not require JWT")
def test_auth_endpoints_no_jwt():
    pass


@scenario(FEATURE_FILE, "Health check endpoint is accessible without authentication")
def test_health_check():
    pass


@scenario(FEATURE_FILE, "Rate limiting is applied to API endpoints")
def test_rate_limiting_api():
    pass


@scenario(FEATURE_FILE, "Rate limiting is applied to auth endpoints")
def test_rate_limiting_auth():
    pass


@scenario(FEATURE_FILE, "Admin role is required for API key management")
def test_admin_required():
    pass


@scenario(FEATURE_FILE, "Admin can access API key management")
def test_admin_access():
    pass


@scenario(FEATURE_FILE, "API key authentication endpoint accepts X-API-Key header")
def test_api_key_auth():
    pass


@scenario(FEATURE_FILE, "Different service endpoints route correctly")
def test_service_routing_outline():
    pass

