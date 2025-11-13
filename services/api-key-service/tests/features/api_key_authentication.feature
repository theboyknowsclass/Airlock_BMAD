Feature: API Key Authentication and Token Issuance
  As a system
  I want to authenticate API key requests and issue tokens
  So that API keys can be used for programmatic access

  Background:
    Given the API key service is configured
    And the database is available

  Scenario: Valid API key can authenticate and receive tokens
    Given an API key exists with scopes "read-only", "read-write" and permissions "read", "write"
    When I authenticate with the API key
    Then the request should succeed with status 200
    And the response should contain an access_token field
    And the response should contain a refresh_token field
    And the response should contain token_type "Bearer"
    And the response should contain an expires_in field
    And the access token should be a valid JWT
    And the access token should contain the API key's scopes
    And the access token should contain the API key's permissions
    And the access token should have auth_type "api_key"

  Scenario: Valid API key with expiration can authenticate
    Given an API key exists with scopes "read-only" and permissions "read" expiring in 30 days
    And the API key is not expired
    When I authenticate with the API key
    Then the request should succeed with status 200
    And the response should contain an access_token field
    And the response should contain a refresh_token field

  Scenario: Invalid API key returns 401
    When I authenticate with API key "invalid-key-12345"
    Then the request should fail with status 401
    And the response should indicate invalid API key

  Scenario: Missing API key header returns 401
    When I authenticate without providing an API key
    Then the request should fail with status 401
    And the response should indicate API key is required

  Scenario: Expired API key returns 401
    Given an API key exists with scopes "read-only" and permissions "read" that is expired
    When I authenticate with the expired API key
    Then the request should fail with status 401
    And the response should indicate API key has expired

  Scenario: Revoked API key cannot authenticate
    Given an API key exists with scopes "read-only" and permissions "read"
    And the API key is revoked
    When I authenticate with the revoked API key
    Then the request should fail with status 401
    And the response should indicate invalid API key

  Scenario: Token structure matches user authentication tokens
    Given an API key exists with scopes "read-only", "read-write" and permissions "read", "write"
    When I authenticate with the API key
    Then the access token should contain sub claim
    And the access token should contain exp claim
    And the access token should contain iat claim
    And the access token should contain iss claim
    And the access token should contain type "access"
    And the access token should contain api_key_id claim

  Scenario: Tokens include correct scopes and permissions
    Given an API key exists with scopes "admin" and permissions "read", "write", "admin"
    When I authenticate with the API key
    Then the access token should contain scopes "admin"
    And the access token should contain permissions "read", "write", "admin"
    And the refresh token should contain scopes "admin"
    And the refresh token should contain permissions "read", "write", "admin"

  Scenario: Different API keys receive different tokens
    Given an API key exists with scopes "read-only" and permissions "read"
    And another API key exists with scopes "read-write" and permissions "read", "write"
    When I authenticate with the first API key
    And I authenticate with the second API key
    Then the two access tokens should be different
    And the first token should contain scopes "read-only"
    And the second token should contain scopes "read-write"

