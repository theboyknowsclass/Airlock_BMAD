Feature: API Key Service - Key Generation and Management
  As a system administrator
  I want to generate and manage API keys for programmatic access
  So that I can integrate Airlock with external systems

  Background:
    Given the API key service is configured
    And the database is available
    And I have a valid admin access token for user "admin-user" with username "admin" and roles "admin"

  Scenario: Admin can generate a new API key
    Given I have a valid admin access token
    When I create an API key with scopes "read-only", "read-write" and permissions "read", "write"
    Then the request should succeed with status 201
    And the response should contain a key field
    And the response should contain scopes "read-only", "read-write"
    And the response should contain permissions "read", "write"
    And the key should be a secure random string starting with "ak_"
    And the key should be stored hashed in the database

  Scenario: Admin can generate an API key with expiration
    Given I have a valid admin access token
    When I create an API key with scopes "read-only" and permissions "read" expiring in 30 days
    Then the request should succeed with status 201
    And the response should contain a key field
    And the response should contain an expires_at field
    And the expiration should be approximately 30 days from now

  Scenario: Admin can list all API keys
    Given I have a valid admin access token
    And an API key exists with scopes "read-only" and permissions "read"
    And an API key exists with scopes "read-write" and permissions "read", "write"
    When I request to list all API keys
    Then the request should succeed with status 200
    And the response should contain a list of API keys
    And the response should contain at least 2 keys
    And each key should not contain the plain text key
    And each key should contain id, scopes, permissions, created_at

  Scenario: Admin can view a specific API key
    Given I have a valid admin access token
    And an API key exists with scopes "read-only" and permissions "read"
    When I request to view the API key
    Then the request should succeed with status 200
    And the response should contain the API key id
    And the response should contain scopes "read-only"
    And the response should not contain the plain text key

  Scenario: Admin can revoke an API key
    Given I have a valid admin access token
    And an API key exists with scopes "read-only" and permissions "read"
    When I revoke the API key
    Then the request should succeed with status 204
    And the API key should be deleted from the database
    And when I request to view the API key
    Then the request should fail with status 404

  Scenario: Admin can rotate an API key
    Given I have a valid admin access token
    And an API key exists with scopes "read-only" and permissions "read"
    When I rotate the API key
    Then the request should succeed with status 200
    And the response should contain a new key field
    And the new key should be different from the original key
    And the old API key should be deleted from the database
    And the new API key should have the same scopes and permissions

  Scenario: Admin can rotate an API key with updated scopes
    Given I have a valid admin access token
    And an API key exists with scopes "read-only" and permissions "read"
    When I rotate the API key with new scopes "read-write", "admin" and new permissions "read", "write", "admin"
    Then the request should succeed with status 200
    And the response should contain a new key field
    And the new API key should have scopes "read-write", "admin"
    And the new API key should have permissions "read", "write", "admin"
    And the old API key should be deleted from the database

  Scenario: Non-admin cannot generate API keys
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I create an API key with scopes "read-only" and permissions "read"
    Then the request should fail with status 403
    And the response should indicate access denied

  Scenario: Non-admin cannot list API keys
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    When I request to list all API keys
    Then the request should fail with status 403
    And the response should indicate access denied

  Scenario: Non-admin cannot revoke API keys
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    And an API key exists with scopes "read-only" and permissions "read"
    When I revoke the API key
    Then the request should fail with status 403
    And the response should indicate access denied

  Scenario: Non-admin cannot rotate API keys
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    And an API key exists with scopes "read-only" and permissions "read"
    When I rotate the API key
    Then the request should fail with status 403
    And the response should indicate access denied

  Scenario: Viewing non-existent API key returns 404
    Given I have a valid admin access token
    When I request to view API key with ID 99999
    Then the request should fail with status 404
    And the response should indicate API key not found

  Scenario: Revoking non-existent API key returns 404
    Given I have a valid admin access token
    When I revoke API key with ID 99999
    Then the request should fail with status 404
    And the response should indicate API key not found

  Scenario: Rotating non-existent API key returns 404
    Given I have a valid admin access token
    When I rotate API key with ID 99999
    Then the request should fail with status 404
    And the response should indicate API key not found

  Scenario: Generated API keys are unique
    Given I have a valid admin access token
    When I create an API key with scopes "read-only" and permissions "read"
    And I create another API key with scopes "read-only" and permissions "read"
    Then the two keys should be different
    And both keys should be stored in the database

  Scenario: API key can be validated by hash
    Given I have a valid admin access token
    When I create an API key with scopes "read-only" and permissions "read"
    Then the key should be stored hashed in the database
    And the plain text key should match the stored hash when verified

