Feature: JWT Token Validation and User Context Extraction
  As a service
  I want to validate JWT tokens and extract user context
  So that I can enforce authorization on protected endpoints

  Background:
    Given the authentication service is configured
    And JWT secret key is set

  Scenario: Valid access token is accepted
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter", "reviewer"
    When I make a request to a protected endpoint with the token
    Then the request should succeed with status 200
    And the response should contain user_id "test-user-123"
    And the response should contain username "testuser"
    And the response should contain roles "submitter", "reviewer"

  Scenario: Request without token is rejected
    Given I have no authentication token
    When I make a request to a protected endpoint
    Then the request should fail with status 401 or 403
    And the response should indicate missing authentication

  Scenario: Invalid token is rejected
    Given I have an invalid authentication token "invalid-token"
    When I make a request to a protected endpoint with the token
    Then the request should fail with status 401
    And the response should indicate invalid token

  Scenario: Refresh token cannot be used for protected endpoints
    Given I have a valid refresh token for user "test-user-123"
    When I make a request to a protected endpoint with the token
    Then the request should fail with status 401
    And the response should indicate "Invalid token type. Access token required."

  Scenario: Expired token is rejected
    Given I have an expired access token for user "test-user-123"
    When I make a request to a protected endpoint with the token
    Then the request should fail with status 401
    And the response should indicate expired or invalid token

  Scenario: Token with wrong secret key is rejected
    Given I have a token signed with wrong secret key for user "test-user-123"
    When I make a request to a protected endpoint with the token
    Then the request should fail with status 401
    And the response should indicate invalid token

  Scenario: Token with missing user ID is rejected
    Given I have an access token without user ID
    When I make a request to a protected endpoint with the token
    Then the request should fail with status 401
    And the response should indicate missing user ID

  Scenario: Token without roles defaults to submitter role
    Given I have a valid access token for user "test-user-123" without roles
    When I make a request to a protected endpoint with the token
    Then the request should succeed with status 200
    And the response should contain roles "submitter"

  Scenario: Optional endpoint accepts requests without token
    Given I have no authentication token
    When I make a request to an optional authentication endpoint
    Then the request should succeed with status 200
    And the response should indicate authenticated false

  Scenario: Optional endpoint accepts requests with valid token
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter"
    When I make a request to an optional authentication endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate authenticated true
    And the response should contain user_id "test-user-123"

  Scenario: Optional endpoint handles invalid token gracefully
    Given I have an invalid authentication token "invalid-token"
    When I make a request to an optional authentication endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate authenticated false

  Scenario Outline: User context is correctly extracted from token
    Given I have a valid access token for user "<user_id>" with username "<username>" and roles "<roles>"
    When I make a request to a protected endpoint with the token
    Then the request should succeed with status 200
    And the response should contain user_id "<user_id>"
    And the response should contain username "<username>"
    And the response should contain roles "<roles>"

    Examples:
      | user_id      | username   | roles                    |
      | user-456     | john_doe   | admin, reviewer          |
      | user-789     | jane_smith | submitter                |
      | user-101     | admin_user | admin, reviewer, submitter |

