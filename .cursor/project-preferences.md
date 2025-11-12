# Project Preferences and Memories

This file documents project-specific preferences and development practices for the Airlock BMAD project.

## Testing Approach

**BDD Testing (Behavior-Driven Development)**
- **Preference**: Always write tests in BDD format using Gherkin feature files
- **Framework**: pytest-bdd with Cucumber/Gherkin syntax
- **Location**: Feature files in `services/{service-name}/features/*.feature`
- **Step Definitions**: Step definitions in `services/{service-name}/features/steps/*_steps.py`
- **Pattern**: Follow the existing pattern established in `auth-service` (see `services/auth-service/features/`)

**BDD Test Structure:**
- Feature files use Gherkin syntax (Given/When/Then)
- Step definitions use pytest-bdd decorators
- Tests serve as living documentation
- All acceptance criteria should be testable via BDD scenarios

**Example Reference:**
- `services/auth-service/features/rbac.feature` - RBAC BDD tests
- `services/auth-service/features/jwt_token_validation.feature` - JWT validation BDD tests
- `services/auth-service/features/steps/rbac_steps.py` - RBAC step definitions

---

*Last updated: 2025-01-XX*
*This preference applies to all new test implementations in this project.*

