Feature: Role-Based Access Control (RBAC) Implementation
  As a system administrator
  I want to enforce role-based access control on all endpoints
  So that users can only access resources appropriate for their role

  Background:
    Given the authentication service is configured
    And JWT secret key is set

  Scenario: Submitter can access submission endpoint
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I make a request to a submitter-only endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: Submitter cannot access reviewer endpoint
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I make a request to a reviewer-only endpoint with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required role: reviewer"

  Scenario: Submitter cannot access admin endpoint
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I make a request to an admin-only endpoint with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required role: admin"

  Scenario: Reviewer can access reviewer endpoint
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    When I make a request to a reviewer-only endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: Reviewer cannot access submission endpoint
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    When I make a request to a submitter-only endpoint with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required role: submitter"

  Scenario: Reviewer cannot access admin endpoint
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    When I make a request to an admin-only endpoint with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required role: admin"

  Scenario: Admin can access all endpoints
    Given I have a valid access token for user "admin-user" with username "admin" and roles "admin"
    When I make a request to a submitter-only endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: Admin can access reviewer endpoint
    Given I have a valid access token for user "admin-user" with username "admin" and roles "admin"
    When I make a request to a reviewer-only endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: Admin can access admin endpoint
    Given I have a valid access token for user "admin-user" with username "admin" and roles "admin"
    When I make a request to an admin-only endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: User with multiple roles can access any of their role endpoints
    Given I have a valid access token for user "multi-role-user" with username "multiuser" and roles "submitter", "reviewer"
    When I make a request to a submitter-only endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: User with multiple roles can access reviewer endpoint
    Given I have a valid access token for user "multi-role-user" with username "multiuser" and roles "submitter", "reviewer"
    When I make a request to a reviewer-only endpoint with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: User with multiple roles cannot access admin endpoint
    Given I have a valid access token for user "multi-role-user" with username "multiuser" and roles "submitter", "reviewer"
    When I make a request to an admin-only endpoint with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required role: admin"

  Scenario: Endpoint requiring any role accepts user with one matching role
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    When I make a request to an endpoint requiring any role "reviewer", "admin" with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: Endpoint requiring any role accepts user with multiple matching roles
    Given I have a valid access token for user "admin-user" with username "admin" and roles "admin", "reviewer"
    When I make a request to an endpoint requiring any role "reviewer", "admin" with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: Endpoint requiring any role rejects user with no matching roles
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I make a request to an endpoint requiring any role "reviewer", "admin" with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required one of roles: reviewer, admin"

  Scenario: Endpoint requiring all roles accepts user with all required roles
    Given I have a valid access token for user "admin-reviewer-user" with username "adminreviewer" and roles "admin", "reviewer"
    When I make a request to an endpoint requiring all roles "admin", "reviewer" with the token
    Then the request should succeed with status 200
    And the response should indicate access granted

  Scenario: Endpoint requiring all roles rejects user missing one required role
    Given I have a valid access token for user "reviewer-user" with username "reviewer" and roles "reviewer"
    When I make a request to an endpoint requiring all roles "admin", "reviewer" with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required all roles: admin, reviewer"

  Scenario: Endpoint requiring all roles rejects user missing multiple required roles
    Given I have a valid access token for user "submitter-user" with username "submitter" and roles "submitter"
    When I make a request to an endpoint requiring all roles "admin", "reviewer" with the token
    Then the request should fail with status 403
    And the response should indicate "Access denied. Required all roles: admin, reviewer"

  Scenario: Unauthenticated request to role-protected endpoint is rejected
    Given I have no authentication token
    When I make a request to a submitter-only endpoint
    Then the request should fail with status 401 or 403
    And the response should indicate missing authentication

  Scenario Outline: Role-based access control enforces correct permissions
    Given I have a valid access token for user "<user_id>" with username "<username>" and roles "<roles>"
    When I make a request to an endpoint requiring role "<required_role>" with the token
    Then the request should <result> with status <status_code>
    And if the request failed, the response should indicate access denied

    Examples:
      | user_id      | username   | roles                    | required_role | result | status_code |
      | user-1       | submitter1 | submitter                | submitter     | succeed | 200         |
      | user-2       | submitter2 | submitter                | reviewer      | fail    | 403         |
      | user-3       | reviewer1  | reviewer                 | reviewer      | succeed | 200         |
      | user-4       | reviewer2  | reviewer                 | admin         | fail    | 403         |
      | user-5       | admin1     | admin                    | admin         | succeed | 200         |
      | user-6       | admin2     | admin                    | submitter     | succeed | 200         |
      | user-7       | multi1     | submitter, reviewer     | submitter     | succeed | 200         |
      | user-8       | multi2     | submitter, reviewer     | reviewer      | succeed | 200         |
      | user-9       | multi3     | submitter, reviewer     | admin         | fail    | 403         |

