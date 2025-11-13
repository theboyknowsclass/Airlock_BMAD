"""
Step definitions for JWT utilities BDD tests
"""
import os
import sys
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List

import pytest
import jwt
from jwt import InvalidTokenError, DecodeError, ExpiredSignatureError

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from pytest_bdd import given, when, then, parsers, scenario
from airlock_common import (
    JWTConfig,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_user_access_token,
    create_user_refresh_token,
    create_api_key_access_token,
    create_api_key_refresh_token,
)

# Context for storing test data
context: Dict[str, Any] = {}


@given("JWT configuration is set up")
def jwt_config_setup():
    """JWT configuration is set up"""
    pass


@given(parsers.parse('JWT secret key is "{secret_key}"'))
def jwt_secret_key(secret_key: str):
    """Set JWT secret key"""
    context["secret_key"] = secret_key


@given(parsers.parse('JWT algorithm is "{algorithm}"'))
def jwt_algorithm(algorithm: str):
    """Set JWT algorithm"""
    context["algorithm"] = algorithm


@given(parsers.parse('JWT issuer is "{issuer}"'))
def jwt_issuer(issuer: str):
    """Set JWT issuer"""
    context["issuer"] = issuer


@given(parsers.parse('access token expiry is {minutes:d} minutes'))
def access_token_expiry(minutes: int):
    """Set access token expiry"""
    context["access_token_expiry_minutes"] = minutes


@given(parsers.parse('refresh token expiry is {days:d} days'))
def refresh_token_expiry(days: int):
    """Set refresh token expiry"""
    context["refresh_token_expiry_days"] = days


def _get_jwt_config() -> JWTConfig:
    """Get or create JWT config from context"""
    if "jwt_config" not in context:
        context["jwt_config"] = JWTConfig(
            secret_key=context.get("secret_key", "test-secret-key"),
            algorithm=context.get("algorithm", "HS256"),
            issuer=context.get("issuer", "test-issuer"),
            access_token_expiry_minutes=context.get("access_token_expiry_minutes", 15),
            refresh_token_expiry_days=context.get("refresh_token_expiry_days", 7),
        )
    return context["jwt_config"]


@given("I want to create a user access token")
def want_to_create_user_access_token():
    """Want to create user access token"""
    pass


@given("I want to create a user refresh token")
def want_to_create_user_refresh_token():
    """Want to create user refresh token"""
    pass


@given("I want to create an API key access token")
def want_to_create_api_key_access_token():
    """Want to create API key access token"""
    pass


@given("I want to create an API key refresh token")
def want_to_create_api_key_refresh_token():
    """Want to create API key refresh token"""
    pass


@when(parsers.parse('I create an access token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def create_user_access_token_step(user_id: str, username: str, roles: str):
    """Create user access token"""
    roles_list = [r.strip() for r in roles.split(",")]
    config = _get_jwt_config()
    token = create_user_access_token(
        config=config,
        user_id=user_id,
        username=username,
        roles=roles_list,
    )
    context["token"] = token
    context["user_id"] = user_id
    context["username"] = username
    context["roles"] = roles_list


@when(parsers.parse('I create an access token for user "{user_id}" with username "{username}", roles "{roles}" and scope "{scope}"'))
def create_user_access_token_with_scope(user_id: str, username: str, roles: str, scope: str):
    """Create user access token with scope"""
    roles_list = [r.strip() for r in roles.split(",")]
    config = _get_jwt_config()
    token = create_user_access_token(
        config=config,
        user_id=user_id,
        username=username,
        roles=roles_list,
        scope=scope,
    )
    context["token"] = token
    context["user_id"] = user_id
    context["scope"] = scope


@when(parsers.parse('I create a refresh token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def create_user_refresh_token_step(user_id: str, username: str, roles: str):
    """Create user refresh token"""
    roles_list = [r.strip() for r in roles.split(",")]
    config = _get_jwt_config()
    token = create_user_refresh_token(
        config=config,
        user_id=user_id,
        username=username,
        roles=roles_list,
    )
    context["token"] = token
    context["user_id"] = user_id


@when(parsers.parse('I create an access token for API key ID {api_key_id:d} with scopes "{scopes}" and permissions "{permissions}"'))
def create_api_key_access_token_step(api_key_id: int, scopes: str, permissions: str):
    """Create API key access token"""
    scopes_list = [s.strip() for s in scopes.split(",")]
    permissions_list = [p.strip() for p in permissions.split(",")]
    config = _get_jwt_config()
    token = create_api_key_access_token(
        config=config,
        api_key_id=api_key_id,
        scopes=scopes_list,
        permissions=permissions_list,
    )
    context["token"] = token
    context["api_key_id"] = api_key_id
    context["scopes"] = scopes_list
    context["permissions"] = permissions_list


@when(parsers.parse('I create a refresh token for API key ID {api_key_id:d} with scopes "{scopes}" and permissions "{permissions}"'))
def create_api_key_refresh_token_step(api_key_id: int, scopes: str, permissions: str):
    """Create API key refresh token"""
    scopes_list = [s.strip() for s in scopes.split(",")]
    permissions_list = [p.strip() for p in permissions.split(",")]
    config = _get_jwt_config()
    token = create_api_key_refresh_token(
        config=config,
        api_key_id=api_key_id,
        scopes=scopes_list,
        permissions=permissions_list,
    )
    context["token"] = token
    context["api_key_id"] = api_key_id


@given(parsers.parse('I have created a user access token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def have_created_user_access_token(user_id: str, username: str, roles: str):
    """Have created user access token"""
    roles_list = [r.strip() for r in roles.split(",")]
    config = _get_jwt_config()
    token = create_user_access_token(
        config=config,
        user_id=user_id,
        username=username,
        roles=roles_list,
    )
    context["token"] = token


@given(parsers.parse('I have created a token with secret key "{secret_key}"'))
def have_created_token_with_secret(secret_key: str):
    """Have created token with specific secret"""
    config = JWTConfig(
        secret_key=secret_key,
        algorithm=context.get("algorithm", "HS256"),
        issuer=context.get("issuer", "test-issuer"),
        access_token_expiry_minutes=15,
        refresh_token_expiry_days=7,
    )
    token = create_user_access_token(
        config=config,
        user_id="test-user",
        username="testuser",
        roles=["admin"],
    )
    context["token"] = token
    context["wrong_secret_token"] = token


@given(parsers.parse('I have created an expired access token for user "{user_id}"'))
def have_created_expired_token(user_id: str):
    """Have created expired token"""
    config = JWTConfig(
        secret_key=context.get("secret_key", "test-secret-key"),
        algorithm=context.get("algorithm", "HS256"),
        issuer=context.get("issuer", "test-issuer"),
        access_token_expiry_minutes=-1,  # Expired
        refresh_token_expiry_days=7,
    )
    token = create_user_access_token(
        config=config,
        user_id=user_id,
        username="testuser",
        roles=["admin"],
    )
    context["token"] = token


@given(parsers.parse('I have created a token with issuer "{issuer}"'))
def have_created_token_with_issuer(issuer: str):
    """Have created token with specific issuer"""
    config = JWTConfig(
        secret_key=context.get("secret_key", "test-secret-key"),
        algorithm=context.get("algorithm", "HS256"),
        issuer=issuer,
        access_token_expiry_minutes=15,
        refresh_token_expiry_days=7,
    )
    token = create_user_access_token(
        config=config,
        user_id="test-user",
        username="testuser",
        roles=["admin"],
    )
    context["token"] = token


@given(parsers.parse('I have an invalid token string "{token_string}"'))
def have_invalid_token_string(token_string: str):
    """Have invalid token string"""
    context["token"] = token_string


@when("I decode the token")
def decode_token_step():
    """Decode the token"""
    config = _get_jwt_config()
    try:
        decoded = decode_token(context["token"], config)
        context["decoded_token"] = decoded
    except Exception as e:
        context["decode_error"] = e
        context["decoded_token"] = None


@when("I try to decode the token with correct secret key")
def try_decode_with_correct_secret():
    """Try to decode with correct secret"""
    config = _get_jwt_config()
    try:
        decoded = decode_token(context["token"], config)
        context["decoded_token"] = decoded
    except Exception as e:
        context["decode_error"] = e
        context["decoded_token"] = None


@when("I try to decode the token with correct issuer")
def try_decode_with_correct_issuer():
    """Try to decode with correct issuer"""
    config = _get_jwt_config()
    try:
        decoded = decode_token(context["token"], config)
        context["decoded_token"] = decoded
    except Exception as e:
        context["decode_error"] = e
        context["decoded_token"] = None


@when("I try to decode the token")
def try_decode_token():
    """Try to decode token"""
    config = _get_jwt_config()
    try:
        decoded = decode_token(context["token"], config)
        context["decoded_token"] = decoded
    except Exception as e:
        context["decode_error"] = e
        context["decoded_token"] = None


@then("the token should be a valid JWT")
def token_is_valid_jwt():
    """Token is valid JWT"""
    token = context.get("token")
    assert token is not None, "Token should exist"
    
    # Try to decode without verification to check structure
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        assert decoded is not None
    except Exception as e:
        pytest.fail(f"Token is not a valid JWT: {e}")


@then(parsers.parse('the token should contain claim "{claim}" with value "{value}"'))
def token_contains_claim_string(claim: str, value: str):
    """Token contains claim with string value"""
    token = context.get("token")
    assert token is not None
    
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert claim in decoded, f"Claim {claim} should be in token"
    assert decoded[claim] == value, f"Claim {claim} should be {value}, got {decoded[claim]}"


@then(parsers.parse('the token should contain claim "{claim}" with value {value:d}'))
def token_contains_claim_int(claim: str, value: int):
    """Token contains claim with integer value"""
    token = context.get("token")
    assert token is not None
    
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert claim in decoded, f"Claim {claim} should be in token"
    assert decoded[claim] == value, f"Claim {claim} should be {value}, got {decoded[claim]}"


@then(parsers.parse('the token should contain claim "{claim}" with value "{values}"'))
def token_contains_claim_list(claim: str, values: str):
    """Token contains claim with list value"""
    token = context.get("token")
    assert token is not None
    
    expected_list = [v.strip() for v in values.split(",")]
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert claim in decoded, f"Claim {claim} should be in token"
    actual_list = decoded[claim]
    assert isinstance(actual_list, list), f"Claim {claim} should be a list"
    assert set(actual_list) == set(expected_list), f"Claim {claim} should be {expected_list}, got {actual_list}"


@then(parsers.parse('the token should contain claim "{claim}"'))
def token_contains_claim(claim: str):
    """Token contains claim"""
    token = context.get("token")
    assert token is not None
    
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert claim in decoded, f"Claim {claim} should be in token"


@then(parsers.parse('the decoded token should contain claim "{claim}" with value "{value}"'))
def decoded_token_contains_claim_string(claim: str, value: str):
    """Decoded token contains claim with string value"""
    decoded = context.get("decoded_token")
    assert decoded is not None, "Token should be decoded"
    assert claim in decoded, f"Claim {claim} should be in decoded token"
    assert decoded[claim] == value, f"Claim {claim} should be {value}, got {decoded[claim]}"


@then(parsers.parse('the decoded token should contain claim "{claim}" with value "{values}"'))
def decoded_token_contains_claim_list(claim: str, values: str):
    """Decoded token contains claim with list value"""
    decoded = context.get("decoded_token")
    assert decoded is not None, "Token should be decoded"
    expected_list = [v.strip() for v in values.split(",")]
    assert claim in decoded, f"Claim {claim} should be in decoded token"
    actual_list = decoded[claim]
    assert isinstance(actual_list, list), f"Claim {claim} should be a list"
    assert set(actual_list) == set(expected_list), f"Claim {claim} should be {expected_list}, got {actual_list}"


@then(parsers.parse('decoding should fail with {error_type}'))
def decoding_should_fail(error_type: str):
    """Decoding should fail with specific error"""
    error = context.get("decode_error")
    assert error is not None, "Decoding should have failed"
    
    error_class_map = {
        "InvalidTokenError": InvalidTokenError,
        "DecodeError": DecodeError,
        "ExpiredSignatureError": ExpiredSignatureError,
    }
    
    expected_error = error_class_map.get(error_type)
    assert expected_error is not None, f"Unknown error type: {error_type}"
    assert isinstance(error, expected_error), f"Expected {error_type}, got {type(error).__name__}"


@then("the token expiry should be approximately 15 minutes from now")
def token_expiry_approximately_15_minutes():
    """Token expiry is approximately 15 minutes from now"""
    decoded = context.get("decoded_token")
    assert decoded is not None, "Token should be decoded"
    
    exp = decoded.get("exp")
    assert exp is not None, "Token should have exp claim"
    
    now = datetime.now(UTC)
    expected_exp = now + timedelta(minutes=15)
    
    # Allow 1 minute tolerance
    exp_dt = datetime.fromtimestamp(exp, UTC)
    diff = abs((exp_dt - expected_exp).total_seconds())
    assert diff < 60, f"Expiry should be approximately 15 minutes from now, got {diff} seconds difference"


@then("the token expiry should be approximately 7 days from now")
def token_expiry_approximately_7_days():
    """Token expiry is approximately 7 days from now"""
    decoded = context.get("decoded_token")
    assert decoded is not None, "Token should be decoded"
    
    exp = decoded.get("exp")
    assert exp is not None, "Token should have exp claim"
    
    now = datetime.now(UTC)
    expected_exp = now + timedelta(days=7)
    
    # Allow 1 hour tolerance
    exp_dt = datetime.fromtimestamp(exp, UTC)
    diff = abs((exp_dt - expected_exp).total_seconds())
    assert diff < 3600, f"Expiry should be approximately 7 days from now, got {diff} seconds difference"


@then("the token issued at time should be approximately now")
def token_iat_approximately_now():
    """Token iat is approximately now"""
    decoded = context.get("decoded_token")
    assert decoded is not None, "Token should be decoded"
    
    iat = decoded.get("iat")
    assert iat is not None, "Token should have iat claim"
    
    now = datetime.now(UTC)
    iat_dt = datetime.fromtimestamp(iat, UTC)
    
    # Allow 5 seconds tolerance
    diff = abs((iat_dt - now).total_seconds())
    assert diff < 5, f"IAT should be approximately now, got {diff} seconds difference"


@given("I want to use the convenience function")
def want_to_use_convenience_function():
    """Want to use convenience function"""
    pass


@when(parsers.parse('I call create_user_access_token for user "{user_id}" with username "{username}" and roles "{roles}"'))
def call_create_user_access_token(user_id: str, username: str, roles: str):
    """Call create_user_access_token"""
    roles_list = [r.strip() for r in roles.split(",")]
    config = _get_jwt_config()
    token = create_user_access_token(
        config=config,
        user_id=user_id,
        username=username,
        roles=roles_list,
    )
    context["token"] = token


@when(parsers.parse('I call create_api_key_access_token for API key ID {api_key_id:d} with scopes "{scopes}" and permissions "{permissions}"'))
def call_create_api_key_access_token(api_key_id: int, scopes: str, permissions: str):
    """Call create_api_key_access_token"""
    scopes_list = [s.strip() for s in scopes.split(",")]
    permissions_list = [p.strip() for p in permissions.split(",")]
    config = _get_jwt_config()
    token = create_api_key_access_token(
        config=config,
        api_key_id=api_key_id,
        scopes=scopes_list,
        permissions=permissions_list,
    )
    context["token"] = token

