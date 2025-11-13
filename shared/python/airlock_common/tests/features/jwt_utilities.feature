Feature: JWT Token Utilities
  As a developer
  I want to create and validate JWT tokens using shared utilities
  So that all services use consistent token handling

  Background:
    Given JWT configuration is set up
    And JWT secret key is "test-secret-key-123456789012345678901234567890"
    And JWT algorithm is "HS256"
    And JWT issuer is "test-issuer"
    And access token expiry is 15 minutes
    And refresh token expiry is 7 days

  Scenario: Create user access token with all claims
    Given I want to create a user access token
    When I create an access token for user "user-123" with username "testuser" and roles "admin", "reviewer"
    Then the token should be a valid JWT
    And the token should contain claim "sub" with value "user-123"
    And the token should contain claim "username" with value "testuser"
    And the token should contain claim "roles" with value "admin", "reviewer"
    And the token should contain claim "type" with value "access"
    And the token should contain claim "iss" with value "test-issuer"
    And the token should contain claim "exp"
    And the token should contain claim "iat"

  Scenario: Create user access token with scope
    Given I want to create a user access token
    When I create an access token for user "user-456" with username "testuser2", roles "submitter" and scope "read write"
    Then the token should be a valid JWT
    And the token should contain claim "sub" with value "user-456"
    And the token should contain claim "scope" with value "read write"
    And the token should contain claim "roles" with value "submitter"

  Scenario: Create user refresh token
    Given I want to create a user refresh token
    When I create a refresh token for user "user-789" with username "testuser3" and roles "admin"
    Then the token should be a valid JWT
    And the token should contain claim "sub" with value "user-789"
    And the token should contain claim "type" with value "refresh"
    And the token should contain claim "jti"
    And the token should contain claim "username" with value "testuser3"
    And the token should contain claim "roles" with value "admin"

  Scenario: Create API key access token
    Given I want to create an API key access token
    When I create an access token for API key ID 42 with scopes "read-only", "read-write" and permissions "read", "write"
    Then the token should be a valid JWT
    And the token should contain claim "sub" with value "api-key-42"
    And the token should contain claim "api_key_id" with value 42
    And the token should contain claim "scopes" with value "read-only", "read-write"
    And the token should contain claim "permissions" with value "read", "write"
    And the token should contain claim "auth_type" with value "api_key"
    And the token should contain claim "type" with value "access"

  Scenario: Create API key refresh token
    Given I want to create an API key refresh token
    When I create a refresh token for API key ID 99 with scopes "read-only" and permissions "read"
    Then the token should be a valid JWT
    And the token should contain claim "sub" with value "api-key-99"
    And the token should contain claim "api_key_id" with value 99
    And the token should contain claim "type" with value "refresh"
    And the token should contain claim "auth_type" with value "api_key"

  Scenario: Decode valid token
    Given I have created a user access token for user "user-123" with username "testuser" and roles "admin"
    When I decode the token
    Then the decoded token should contain claim "sub" with value "user-123"
    And the decoded token should contain claim "username" with value "testuser"
    And the decoded token should contain claim "roles" with value "admin"
    And the decoded token should contain claim "type" with value "access"

  Scenario: Decode token with wrong secret key fails
    Given I have created a token with secret key "wrong-secret"
    When I try to decode the token with correct secret key
    Then decoding should fail with InvalidTokenError

  Scenario: Decode expired token fails
    Given I have created an expired access token for user "user-123"
    When I try to decode the token
    Then decoding should fail with ExpiredSignatureError

  Scenario: Decode token with wrong issuer fails
    Given I have created a token with issuer "wrong-issuer"
    When I try to decode the token with correct issuer
    Then decoding should fail with InvalidTokenError

  Scenario: Decode invalid token string fails
    Given I have an invalid token string "not-a-valid-jwt-token"
    When I try to decode the token
    Then decoding should fail with DecodeError

  Scenario: Token expiry times are correct
    Given I want to create a user access token
    When I create an access token for user "user-123" with username "testuser" and roles "admin"
    And I decode the token
    Then the token expiry should be approximately 15 minutes from now
    And the token issued at time should be approximately now

  Scenario: Refresh token expiry is correct
    Given I want to create a user refresh token
    When I create a refresh token for user "user-123" with username "testuser" and roles "admin"
    And I decode the token
    Then the token expiry should be approximately 7 days from now

  Scenario: Convenience function creates user access token
    Given I want to use the convenience function
    When I call create_user_access_token for user "user-123" with username "testuser" and roles "admin"
    Then the token should be a valid JWT
    And the token should contain claim "sub" with value "user-123"
    And the token should contain claim "username" with value "testuser"

  Scenario: Convenience function creates API key access token
    Given I want to use the convenience function
    When I call create_api_key_access_token for API key ID 42 with scopes "read-only" and permissions "read"
    Then the token should be a valid JWT
    And the token should contain claim "sub" with value "api-key-42"
    And the token should contain claim "api_key_id" with value 42
    And the token should contain claim "auth_type" with value "api_key"

