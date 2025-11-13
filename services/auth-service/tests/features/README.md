# BDD Tests for Authentication Service

This directory contains Behavior-Driven Development (BDD) tests written in Gherkin format using pytest-bdd.

## Structure

```
features/
├── jwt_token_validation.feature    # Gherkin feature file
├── steps/
│   └── jwt_token_validation_steps.py  # Step definitions
└── conftest.py                      # Pytest configuration
```

## Running Tests

### Run all BDD tests:
```bash
cd services/auth-service
python -m pytest features/ -v
```

### Run specific feature:
```bash
python -m pytest features/steps/jwt_token_validation_steps.py -v
```

### Run with coverage:

**Terminal report:**
```bash
python -m pytest features/ --cov=src --cov-report=term-missing
```

**HTML report:**
```bash
python -m pytest features/ --cov=src --cov-report=html
```
Then open `htmlcov/index.html` in your browser.

**XML report (for CI/CD):**
```bash
python -m pytest features/ --cov=src --cov-report=xml
```

**All reports:**
```bash
python -m pytest features/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
```

### Coverage Configuration

Coverage settings are configured in `.coveragerc`:
- Source directory: `src/`
- Excludes test files and common patterns
- HTML output: `htmlcov/`
- XML output: `coverage.xml`

## Feature Files

Feature files are written in Gherkin syntax and describe the behavior of the system in business-readable language. Each scenario follows the Given-When-Then format:

- **Given**: Sets up the initial state
- **When**: Describes the action being tested
- **Then**: Verifies the expected outcome

## Step Definitions

Step definitions in `features/steps/` implement the actual test logic for each Gherkin step. They use pytest-bdd decorators (`@given`, `@when`, `@then`) to map Gherkin steps to Python functions.

## Example

```gherkin
Scenario: Valid access token is accepted
  Given I have a valid access token for user "test-user-123" with username "testuser" and roles "submitter", "reviewer"
  When I make a request to a protected endpoint with the token
  Then the request should succeed with status 200
  And the response should contain user_id "test-user-123"
```

This scenario is implemented by step definitions that:
1. Create a valid JWT token
2. Make an HTTP request to the protected endpoint
3. Verify the response status and content

## Test Coverage

### JWT Token Validation Feature
- ✅ Valid access token acceptance
- ✅ Missing token rejection
- ✅ Invalid token rejection
- ✅ Refresh token rejection (access tokens only)
- ✅ Expired token rejection
- ✅ Wrong secret key rejection
- ✅ Missing user ID handling
- ✅ Default role assignment
- ✅ Optional authentication endpoints
- ✅ User context extraction
- ✅ Parameterized scenarios (Scenario Outline)

### OAuth2 Integration Feature
- ✅ Login flow initiation
- ✅ Token refresh with valid refresh token
- ✅ Token refresh with invalid refresh token
- ✅ Token refresh error handling (wrong grant type, missing token)
- ✅ Logout endpoint
- ✅ Username parameter support for mock OAuth providers

**Note:** OAuth2 callback scenarios (code exchange) require complex async mocking and are better tested via integration tests with the actual mock OAuth service. These are documented but not included in unit BDD tests.

## Current Coverage

Running all BDD tests with coverage:
```bash
python -m pytest features/ --cov=src --cov-report=term-missing --cov-report=html
```

**Coverage Results:**
- JWT Validation (`dependencies/auth.py`): 89.29%
- JWT Utils (`utils/jwt.py`): 94.29%
- Auth Router (`routers/auth.py`): 63.00%
- OAuth2 Service (`services/oauth2.py`): 32.91% (callback flows tested via integration)
- **Overall Service**: 60.17%

