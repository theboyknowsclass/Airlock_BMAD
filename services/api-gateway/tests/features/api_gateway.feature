Feature: API Gateway - Token Validation and Request Routing
  As a system
  I want an API Gateway that validates tokens and routes requests
  So that all services receive authenticated and authorized requests

  Background:
    Given the API Gateway is running
    And the authentication service is running
    And JWT secret key is configured

  Scenario: Valid token is accepted and request is routed
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter"
    When I make a request to "/api/v1/users" with the token
    Then the request should succeed with status 200
    And the request should be routed to the user service
    And user context should be forwarded to the service

  Scenario: Request without token is rejected
    Given I have no authentication token
    When I make a request to "/api/v1/users"
    Then the request should fail with status 401
    And the response should indicate missing authentication

  Scenario: Invalid token is rejected
    Given I have an invalid authentication token "invalid-token"
    When I make a request to "/api/v1/users" with the token
    Then the request should fail with status 401
    And the response should indicate invalid token

  Scenario: Expired token is rejected
    Given I have an expired access token for user "test-user-123"
    When I make a request to "/api/v1/users" with the token
    Then the request should fail with status 401
    And the response should indicate expired or invalid token

  Scenario: Refresh token cannot be used for protected endpoints
    Given I have a valid refresh token for user "test-user-123"
    When I make a request to "/api/v1/users" with the token
    Then the request should fail with status 401
    And the response should indicate "Invalid token type. Access token required."

  Scenario: User context is extracted from token
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter", "reviewer"
    When I make a request to "/api/v1/users" with the token
    Then the request should succeed with status 200
    And user context should contain user_id "test-user-123"
    And user context should contain username "testuser"
    And user context should contain roles "submitter", "reviewer"

  Scenario: Request is routed to correct service based on path
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter"
    When I make a request to "/api/v1/packages" with the token
    Then the request should be routed to the submission service
    When I make a request to "/api/v1/workflows" with the token
    Then the request should be routed to the workflow service
    When I make a request to "/api/v1/tracking" with the token
    Then the request should be routed to the tracking service

  Scenario: Auth endpoints do not require JWT
    Given I have no authentication token
    When I make a request to "/api/v1/auth/login"
    Then the request should be routed to the auth service
    And the request should not be rejected with status 401

  Scenario: Health check endpoint is accessible without authentication
    Given I have no authentication token
    When I make a request to "/health"
    Then the request should succeed with status 200
    And the response should indicate the gateway is healthy

  Scenario: Rate limiting is applied to API endpoints
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter"
    When I make 101 requests to "/api/v1/users" with the token within 1 second
    Then at least one request should fail with status 429
    And the response should indicate rate limit exceeded

  Scenario: Rate limiting is applied to auth endpoints
    Given I have no authentication token
    When I make 11 requests to "/api/v1/auth/login" within 1 second
    Then at least one request should fail with status 429
    And the response should indicate rate limit exceeded

  Scenario: Admin role is required for API key management
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter"
    When I make a request to "/api/v1/api-keys" with the token
    Then the request should fail with status 403
    And the response should indicate "Admin role required"

  Scenario: Admin can access API key management
    Given I have a valid access token for user "admin-user" with username "admin" and roles "admin"
    When I make a request to "/api/v1/api-keys" with the token
    Then the request should be routed to the api-key service
    And the request should not be rejected with status 403

  Scenario: API key authentication endpoint accepts X-API-Key header
    Given I have an API key "test-api-key-123"
    When I make a request to "/api/v1/api-keys/auth/token" with header "X-API-Key" set to "test-api-key-123"
    Then the request should be routed to the api-key service
    And the request should not be rejected with status 401

  Scenario Outline: Different service endpoints route correctly
    Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter"
    When I make a request to "<endpoint>" with the token
    Then the request should be routed to "<service>"

    Examples:
      | endpoint              | service            |
      | /api/v1/users         | user-service       |
      | /api/v1/packages      | submission-service |
      | /api/v1/workflows     | workflow-service   |
      | /api/v1/storage       | storage-service    |
      | /api/v1/registry      | registry-service   |
      | /api/v1/tracking      | tracking-service   |

