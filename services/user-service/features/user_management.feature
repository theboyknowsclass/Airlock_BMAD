Feature: User Management Service - User Profiles and Roles
  As a system administrator
  I want to manage user profiles and assign roles
  So that I can control access to system resources

  Background:
    Given the user management service is configured
    And the database is available
    And I have a valid admin access token for user "admin-user" with username "admin" and roles "admin"

  Scenario: Admin can list all users
    Given I have a valid admin access token
    When I request to list all users
    Then the request should succeed with status 200
    And the response should contain a list of users

  Scenario: Admin can view a specific user
    Given I have a valid admin access token
    And a user exists with username "testuser" and email "test@example.com"
    When I request to view user with username "testuser"
    Then the request should succeed with status 200
    And the response should contain username "testuser"
    And the response should contain email "test@example.com"

  Scenario: Admin can create a new user
    Given I have a valid admin access token
    When I create a user with username "newuser", email "newuser@example.com", and roles "submitter"
    Then the request should succeed with status 201
    And the response should contain username "newuser"
    And the response should contain email "newuser@example.com"
    And the response should contain roles "submitter"
    And an audit log entry should be created for action "user.created"

  Scenario: Admin can update user profile
    Given I have a valid admin access token
    And a user exists with username "testuser" and email "test@example.com"
    When I update user "testuser" with email "updated@example.com"
    Then the request should succeed with status 200
    And the response should contain email "updated@example.com"
    And an audit log entry should be created for action "user.updated"

  Scenario: Admin can assign roles to a user
    Given I have a valid admin access token
    And a user exists with username "testuser" and roles "submitter"
    When I update user "testuser" roles to "reviewer", "submitter"
    Then the request should succeed with status 200
    And the response should contain roles "reviewer", "submitter"
    And an audit log entry should be created for action "user.roles_updated"

  Scenario: Admin can update user roles to empty list
    Given I have a valid admin access token
    And a user exists with username "testuser" and roles "submitter", "reviewer"
    When I update user "testuser" roles to empty list
    Then the request should succeed with status 200
    And the response should contain roles ""
    And an audit log entry should be created for action "user.roles_updated"

  Scenario: Non-admin cannot list users
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I request to list all users
    Then the request should fail with status 403
    And the response should indicate access denied

  Scenario: Non-admin cannot create users
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I create a user with username "newuser", email "newuser@example.com", and roles "submitter"
    Then the request should fail with status 403
    And the response should indicate access denied

  Scenario: Non-admin cannot update user roles
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    And a user exists with username "testuser"
    When I update user "testuser" roles to "admin"
    Then the request should fail with status 403
    And the response should indicate access denied

  Scenario: Cannot create user with duplicate username
    Given I have a valid admin access token
    And a user exists with username "existinguser" and email "existing@example.com"
    When I create a user with username "existinguser", email "different@example.com", and roles "submitter"
    Then the request should fail with status 409
    And the response should indicate username already exists

  Scenario: Cannot create user with duplicate email
    Given I have a valid admin access token
    And a user exists with username "user1" and email "existing@example.com"
    When I create a user with username "user2", email "existing@example.com", and roles "submitter"
    Then the request should fail with status 409
    And the response should indicate email already exists

  Scenario: Cannot update user to duplicate username
    Given I have a valid admin access token
    And a user exists with username "user1" and email "user1@example.com"
    And a user exists with username "user2" and email "user2@example.com"
    When I update user "user1" with username "user2"
    Then the request should fail with status 409
    And the response should indicate username already exists

  Scenario: Cannot update user to duplicate email
    Given I have a valid admin access token
    And a user exists with username "user1" and email "user1@example.com"
    And a user exists with username "user2" and email "user2@example.com"
    When I update user "user1" with email "user2@example.com"
    Then the request should fail with status 409
    And the response should indicate email already exists

  Scenario: Viewing non-existent user returns 404
    Given I have a valid admin access token
    When I request to view user with ID 99999
    Then the request should fail with status 404
    And the response should indicate user not found

  Scenario: Updating non-existent user returns 404
    Given I have a valid admin access token
    When I update user with ID 99999 with email "test@example.com"
    Then the request should fail with status 404
    And the response should indicate user not found

  Scenario: Updating roles for non-existent user returns 404
    Given I have a valid admin access token
    When I update user with ID 99999 roles to "admin"
    Then the request should fail with status 404
    And the response should indicate user not found

  Scenario: All user management actions are logged in audit trail
    Given I have a valid admin access token
    And a user exists with username "testuser" and email "test@example.com"
    When I update user "testuser" roles to "admin"
    Then an audit log entry should be created for action "user.roles_updated"
    And the audit log should contain resource_type "user"
    And the audit log should contain the user ID
    And the audit log should contain old roles and new roles

