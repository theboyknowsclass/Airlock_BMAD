Feature: OAuth2 Integration with ADFS
  As a user
  I want to authenticate using my organization's ADFS credentials
  So that I can securely access the Airlock system

  Background:
    Given the authentication service is configured
    And OAuth2 provider endpoints are configured
    And a mock OAuth2 provider is available

  Scenario: User initiates login flow
    Given I am a user wanting to authenticate
    When I request to initiate login
    Then I should receive an authorization URL
    And the authorization URL should contain the OAuth2 provider URL
    And the authorization URL should contain required OAuth2 parameters
    And I should receive a state token for CSRF protection

  # Note: OAuth2 callback tests require complex async mocking and are better tested via integration tests
  # These scenarios test the token refresh and login initiation which are more testable

  Scenario: User refreshes access token with valid refresh token
    Given I have a valid refresh token
    When I request to refresh my access token
    Then I should receive a new JWT access token
    And I should receive a new JWT refresh token (token rotation)
    And the new access token should contain my user ID
    And the new access token should contain my roles
    And the response should indicate token type "Bearer"
    And the response should indicate expiration time

  Scenario: User refreshes access token with invalid refresh token
    Given I have an invalid refresh token
    When I request to refresh my access token
    Then the request should fail with status 401
    And I should receive an error message

  Scenario: User refreshes access token with wrong grant type
    Given I want to refresh my access token
    When I request token refresh with grant type "client_credentials"
    Then the request should fail with status 400
    And I should receive error message "Only 'refresh_token' grant type is supported"

  Scenario: User refreshes access token without providing refresh token
    Given I want to refresh my access token
    When I request token refresh without refresh_token parameter
    Then the request should fail with status 400
    And I should receive error message "refresh_token is required"

  Scenario: User logs out
    Given I am an authenticated user
    When I request to log out
    Then the request should succeed with status 200
    And I should receive a logout confirmation message

  # Note: OAuth2 callback error handling tests require complex async mocking
  # These are better tested via integration tests with actual mock OAuth service

  Scenario: Login flow supports username parameter for mock OAuth providers
    Given I am a user wanting to authenticate
    When I request to initiate login with username "testuser"
    Then I should receive an authorization URL
    And the authorization URL should contain username parameter "testuser"

