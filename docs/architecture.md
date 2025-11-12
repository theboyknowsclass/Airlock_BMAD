# Airlock - Architecture Document

**Author:** BMad
**Date:** 2025-11-12
**Version:** 1.1
**Version Verification Date:** 2025-11-12

---

## Executive Summary

Airlock is architected as a microservices-based, event-driven system using FastAPI (Python) for backend services, Celery for workflow processing, RabbitMQ for event messaging, and React + TypeScript for the frontend. The architecture emphasizes security-first design with external ADFS authentication, stateless JWT tokens, and comprehensive audit trails.

---

## Authentication & Authorization Architecture

### Authentication Strategy

**External Identity Provider:** ADFS (Active Directory Federation Services)
- Production: Integrate with external ADFS service using OAuth 2.0 / OpenID Connect
- Development: Mock OAuth provider service for local development
- Authentication flow: OAuth 2.0 Authorization Code flow (or appropriate ADFS flow)

**Token Strategy:**
- **Access Tokens:** JWT, short-lived (15 minutes)
- **Refresh Tokens:** Stateless JWT, long-lived (7 days)
- **Token Storage:** Stateless (no server-side storage)
- **Token Rotation:** Refresh tokens rotate on use (security best practice)

**Implementation:**
- FastAPI OAuth2 integration with external ADFS
- `python-jose[cryptography]` for JWT encoding/decoding
- `passlib[bcrypt]` for password hashing (if needed for local accounts)
- `python-multipart` for form data handling
- FastAPI dependencies for token validation and RBAC
- OAuth2 Authorization Code flow (or ADFS-supported flow)

**Development Mock:**
- Mock OAuth provider service (`mock-services/mock-oauth/`)
- Simulates ADFS OAuth endpoints
- Provides test users with different roles
- Same OAuth2 flow as production for consistency

### Authorization Strategy

**Model:** Role-Based Access Control (RBAC)

**Roles:**
- **Submitter:** Can submit packages for approval
- **Reviewer:** Can approve/reject packages in workflow
- **Admin:** Full system access, user management, configuration

**Implementation:**
- JWT tokens include user ID and roles
- FastAPI dependencies enforce RBAC on endpoints
- API Gateway validates tokens before routing
- Each microservice enforces its own authorization rules

### API Key Management

**Approach:** Separate API Key Service

**Implementation:**
- Dedicated service for API key management
- API keys are separate from user accounts
- Keys have their own scopes/permissions (read-only, read-write, admin)
- Key generation, rotation, and revocation
- Keys authenticate via API key header: `X-API-Key: <key>`
- API Key Service validates key and issues JWT token (similar to user auth flow)

**Service:** API Key Service (separate microservice)
- Generates and manages API keys
- Validates API key requests
- Issues JWT tokens for API keys (with scopes in token claims)
- Key scoping and permission management
- Key storage in database (hashed keys)

**API Key Flow:**
1. Client sends request with `X-API-Key` header
2. API Gateway forwards to API Key Service for validation
3. API Key Service validates key and issues JWT token
4. Token includes scopes/permissions for the key
5. Request proceeds with API key's permissions

---

## Technology Stack

### Backend Services

**Framework:** FastAPI (Python)
- Version: 0.115.0 (verified 2025-11-12)
- Async/await support
- Auto-generated OpenAPI documentation
- Type hints and validation

**Workflow Processing:** Celery
- Version: 5.4.0 (verified 2025-11-12)
- Task queue for workflow agents
- Supports retries and error handling
- Flower for monitoring

**Message Broker:** RabbitMQ
- Version: 3.13.0 (verified 2025-11-12, Docker image: `rabbitmq:3.13-management`)
- Event-driven communication
- Reliable message delivery
- Management UI available

**Authentication Libraries:**
- `python-jose[cryptography]`: 3.3.0 (verified 2025-11-12) - JWT handling
- `passlib[bcrypt]`: 1.7.4 (verified 2025-11-12) - Password hashing (if needed)
- `python-multipart`: 0.0.12 (verified 2025-11-12) - Form data handling

**Database Libraries:**
- `SQLAlchemy`: 2.0.36 (verified 2025-11-12) - ORM
- `asyncpg`: 0.30.0 (verified 2025-11-12) - Async PostgreSQL driver
- `alembic`: 1.13.2 (verified 2025-11-12) - Database migrations

**Testing Libraries (Backend):**
- `pytest`: 8.3.3 (verified 2025-11-12) - Testing framework
- `pytest-bdd`: 7.1.1 (verified 2025-11-12) - BDD testing for Python
- `httpx`: 0.27.2 (verified 2025-11-12) - Async HTTP client for testing

### Frontend Application

**Framework:** React + TypeScript
- React: 19.2.0 (verified 2025-11-12)
- TypeScript: Latest from npm (verified 2025-11-12)
- Build Tool: Vite (latest from npm, verified 2025-11-12)

**UI Library:** Material UI (MUI)
- Version: Latest from npm (verified 2025-11-12)
- Accessibility features built-in

**State Management:**
- Zustand: Latest from npm (verified 2025-11-12) - Global state
- React Query (TanStack Query): Latest from npm (verified 2025-11-12) - Server state / data fetching

**Routing:** TanStack Router
- Version: Latest from npm (verified 2025-11-12)
- Type-safe routing

**Forms:** React Hook Form
- Version: Latest from npm (verified 2025-11-12)
- Form validation

**HTTP Client:** Axios
- Version: Latest from npm (verified 2025-11-12)

**Testing:**
- Storybook: Latest from npm (verified 2025-11-12) - Component testing
- Cucumber.js: Latest from npm (verified 2025-11-12) - BDD testing
- MSW: Latest from npm (verified 2025-11-12) - API mocking
- axe-core: Latest from npm (verified 2025-11-12) - Accessibility testing
- Pa11y: Latest from npm (verified 2025-11-12) - Accessibility linting
- Lighthouse: Latest from npm (verified 2025-11-12) - Accessibility audits

**Note:** All frontend libraries use the latest version available from npm as of the verification date. Install with `npm install <package>@latest` or check npm registry for current version.

### Database

**Recommendation:** PostgreSQL

**Rationale:**
- Reliable, ACID-compliant relational database
- Excellent for audit trails and compliance requirements
- Strong security features
- Good performance for our scale (multiple thousands of packages)
- Well-supported with Python (SQLAlchemy, asyncpg)
- Works well in Docker

**Version:** 16.3 (verified 2025-11-12, Docker image: `postgres:16-alpine`)

**Alternative Consideration:** 
- If document-based storage needed: MongoDB
- If simple key-value: Redis (for caching/sessions, not primary storage)

**Decision:** PostgreSQL for primary data storage

### Containerization

**Docker:**
- All services containerized
- Docker Compose for local development
- Multi-stage builds for optimization

---

## Microservices Architecture

### Service Boundaries

1. **API Gateway Service**
   - Entry point for all client requests
   - Token validation
   - Request routing
   - Rate limiting

2. **Authentication Service**
   - OAuth integration with ADFS
   - Token issuance (access + refresh)
   - Token validation
   - User context extraction

3. **User Management Service**
   - User profile management
   - Role assignment
   - User account operations

4. **API Key Service**
   - API key generation
   - API key validation
   - Key scoping and permissions
   - Key rotation and revocation
   - Token issuance for API keys

5. **Package Submission Service**
   - Accept package submissions
   - Validate package format
   - Queue packages for workflow

6. **Workflow Service**
   - Workflow state management
   - Workflow orchestration
   - Approval/rejection handling

7. **Workflow Agents (Multiple)**
   - Trivy Scanner Agent
   - License Check Agent
   - [Future: Additional check agents]
   - Manual Review Agent

8. **Storage Integration Service**
   - External artifact storage integration
   - Package transfer
   - Storage configuration

9. **Registry Integration Service**
   - NPM registry integration
   - Package metadata handling
   - [Future: NuGet, Pip, Docker integrations]

10. **Tracking Service**
   - Package usage tracking
   - Package inventory
   - Reporting

11. **Frontend Service**
    - React application
    - Static assets
    - Served via web server (nginx or similar)

---

## Event-Driven Architecture

### Message Flow

**Event Types:**
- `package.submitted` - Package submitted for approval
- `package.validated` - Package validation complete
- `check.trivy.completed` - Trivy scan complete
- `check.license.completed` - License check complete
- `workflow.approved` - Package approved
- `workflow.rejected` - Package rejected
- `package.stored` - Package stored in artifact storage
- `package.published` - Package published to registry

**Workflow Stages:**
1. Package submission → `package.submitted` event
2. Validation agent → `package.validated` event
3. Trivy agent → `check.trivy.completed` event
4. License agent → `check.license.completed` event
5. Manual review → `workflow.approved` or `workflow.rejected` event
6. Storage agent → `package.stored` event
7. Registry agent → `package.published` event

**Message Broker:** RabbitMQ
- Exchanges and queues for event routing
- Consumer groups for workflow agents
- Dead letter queues for failed messages

---

## Project Structure

```
airlock/
├── docker-compose.yml          # Local development orchestration
├── .env.example                # Environment variables template
├── README.md
│
├── services/
│   ├── api-gateway/           # API Gateway service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── main.py
│   │
│   ├── auth-service/          # Authentication service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── main.py
│   │       ├── auth/
│   │       │   ├── oauth.py
│   │       │   ├── jwt.py
│   │       │   └── dependencies.py
│   │       └── models/
│   │
│   ├── user-service/           # User management service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │
│   ├── api-key-service/        # API key management service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │
│   ├── submission-service/     # Package submission service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │
│   ├── workflow-service/       # Workflow orchestration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │
│   ├── agents/                 # Workflow agents
│   │   ├── trivy-agent/
│   │   │   ├── Dockerfile
│   │   │   ├── requirements.txt
│   │   │   └── src/
│   │   ├── license-agent/
│   │   │   ├── Dockerfile
│   │   │   ├── requirements.txt
│   │   │   └── src/
│   │   └── review-agent/
│   │       ├── Dockerfile
│   │       ├── requirements.txt
│   │       └── src/
│   │
│   ├── storage-service/        # Artifact storage integration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │
│   ├── registry-service/       # Registry integration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │
│   └── tracking-service/       # Package tracking
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│
├── frontend/                    # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── components/
│       │   ├── atoms/           # Basic building blocks
│       │   │   └── Button/
│       │   │       ├── Button.tsx
│       │   │       ├── Button.test.tsx
│       │   │       └── Button.stories.tsx
│       │   ├── molecules/      # Simple component groups
│       │   │   └── FormField/
│       │   │       ├── FormField.tsx
│       │   │       ├── FormField.test.tsx
│       │   │       └── FormField.stories.tsx
│       │   ├── organisms/      # Complex UI sections
│       │   │   └── DataTable/
│       │   │       ├── DataTable.tsx
│       │   │       ├── DataTable.test.tsx
│       │   │       └── DataTable.stories.tsx
│       │   └── templates/      # Page layouts
│       │       └── DashboardLayout/
│       │           ├── DashboardLayout.tsx
│       │           ├── DashboardLayout.test.tsx
│       │           └── DashboardLayout.stories.tsx
│       ├── pages/              # Full page components
│       │   └── HomePage/
│       │       ├── HomePage.tsx
│       │       └── HomePage.test.tsx
│       ├── hooks/
│       │   └── usePackageData/
│       │       ├── usePackageData.ts
│       │       └── usePackageData.test.ts
│       ├── store/
│       │   └── packageStore/
│       │       ├── packageStore.ts
│       │       └── packageStore.test.ts
│       ├── api/
│       │   └── packageService/
│       │       ├── packageService.ts
│       │       ├── packageService.mock.ts
│       │       └── packageService.test.ts
│       └── features/
│
├── mock-services/               # Development mocks
│   └── mock-oauth/             # Mock ADFS/OAuth provider
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│
├── shared/                      # Shared code/libraries
│   ├── python/
│   │   └── airlock_common/     # Common Python utilities
│   └── types/                   # Shared TypeScript types
│
├── tests/                       # Integration/E2E tests
│   ├── features/                # BDD feature files
│   │   ├── api/
│   │   ├── frontend/
│   │   └── e2e/
│   └── steps/                   # Step definitions
│
└── docs/                        # Documentation
    ├── architecture.md
    ├── PRD.md
    └── technical/
```

---

## Decision Summary

| Category | Decision | Version | Verified | Affects Epics | Rationale |
| -------- | -------- | ------- | -------- | ------------- | --------- |
| Backend Framework | FastAPI | 0.115.0 | 2025-11-12 | All backend | Modern async support, auto-docs, high performance |
| Workflow Engine | Celery | 5.4.0 | 2025-11-12 | Workflow epics | Mature Python task queue, good for workflows |
| Message Broker | RabbitMQ | 3.13.0 | 2025-11-12 | Event-driven epics | Reliable, well-documented, good tooling |
| Frontend Framework | React | 19.2.0 | 2025-11-12 | Frontend epics | Modern, type-safe, large ecosystem |
| Frontend Framework | TypeScript | Latest from npm | 2025-11-12 | Frontend epics | Type safety, modern features |
| Build Tool | Vite | Latest from npm | 2025-11-12 | Frontend epics | Fast, modern, great DX |
| UI Library | Material UI | Latest from npm | 2025-11-12 | Frontend epics | Accessibility built-in, professional components |
| State Management | Zustand | Latest from npm | 2025-11-12 | Frontend epics | Lightweight, simple global state |
| State Management | React Query | Latest from npm | 2025-11-12 | Frontend epics | Server state management |
| Routing | TanStack Router | Latest from npm | 2025-11-12 | Frontend epics | Type-safe routing |
| Forms | React Hook Form | Latest from npm | 2025-11-12 | Frontend epics | Form validation and management |
| HTTP Client | Axios | Latest from npm | 2025-11-12 | Frontend epics | HTTP requests |
| Testing | Storybook | Latest from npm | 2025-11-12 | Frontend epics | Component testing |
| Testing | Cucumber.js | Latest from npm | 2025-11-12 | All epics | BDD testing framework |
| Testing | MSW | Latest from npm | 2025-11-12 | Frontend epics | API mocking |
| Testing | axe-core | Latest from npm | 2025-11-12 | Frontend epics | Accessibility testing |
| Authentication | ADFS + OAuth2 | External | - | All epics | Enterprise standard, external IdP |
| Token Strategy | Stateless JWT | - | - | All epics | Scalable, no server-side storage needed |
| JWT Library | python-jose | 3.3.0 | 2025-11-12 | All epics | JWT encoding/decoding |
| Database | PostgreSQL | 16.3 | 2025-11-12 | All data epics | Reliable, ACID-compliant, good for audit trails |
| ORM | SQLAlchemy | 2.0.36 | 2025-11-12 | All data epics | Python ORM |
| DB Driver | asyncpg | 0.30.0 | 2025-11-12 | All data epics | Async PostgreSQL driver |
| Migrations | Alembic | 1.13.2 | 2025-11-12 | All data epics | Database migrations |
| Testing (Backend) | pytest | 8.3.3 | 2025-11-12 | All backend epics | Testing framework |
| Testing (Backend) | pytest-bdd | 7.1.1 | 2025-11-12 | All backend epics | BDD testing for Python |
| API Key Service | Separate Service | - | - | API access epics | Independent management, flexible scoping |
| Testing Approach | BDD/Cucumber | - | - | All epics | Living documentation, readable tests |
| Containerization | Docker | Latest stable | - | All epics | Consistent environments, cloud/on-prem |
| Runtime | Node.js | 24.x | 2025-11-12 | Frontend epics | JavaScript runtime |
| Runtime | Python | 3.12.7 | 2025-11-12 | All backend | Python runtime |

---

## Implementation Patterns

### Naming Conventions

**Python (Backend):**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**TypeScript (Frontend):**
- Files: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- Components: `PascalCase`
- Functions/Variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types/Interfaces: `PascalCase` (with `I` prefix for interfaces if needed)

**API Endpoints:**
- REST: `/api/v1/{resource}` (plural nouns)
- Route params: `{resource_id}` (snake_case)
- Query params: `snake_case`

**Database:**
- Tables: `snake_case` (plural)
- Columns: `snake_case`
- Foreign keys: `{table}_id`

### Code Organization

**Backend Services:**
- `src/main.py` - FastAPI app entry point
- `src/routers/` - API route handlers
- `src/models/` - Data models
- `src/services/` - Business logic
- `src/dependencies/` - FastAPI dependencies (auth, DB, etc.)
- `src/utils/` - Utility functions
- `tests/` - Test files (co-located or separate)

**Frontend (Atomic Design Pattern):**
- `src/components/atoms/` - Basic building blocks (Button, Input, Label, Icon, Badge)
  - Smallest, indivisible components
  - No business logic, pure presentation
  - Highly reusable
  - Test files co-located: `Button.test.tsx`, `Button.stories.tsx` next to `Button.tsx`
- `src/components/molecules/` - Simple component groups (FormField, SearchBar, Card, FileUpload)
  - Combinations of atoms
  - Simple functionality
  - Reusable across features
  - Test files co-located: `FormField.test.tsx`, `FormField.stories.tsx` next to `FormField.tsx`
- `src/components/organisms/` - Complex UI sections (DataTable, Navigation, Form, ApprovalForm)
  - Complex combinations of molecules and atoms
  - Feature-specific functionality
  - May include business logic
  - Test files co-located: `DataTable.test.tsx`, `DataTable.stories.tsx` next to `DataTable.tsx`
- `src/components/templates/` - Page layouts (DashboardLayout, FormLayout, AuthLayout)
  - Page structure and layout
  - Placeholder for organisms
  - No real content, just structure
  - Test files co-located: `DashboardLayout.test.tsx`, `DashboardLayout.stories.tsx` next to `DashboardLayout.tsx`
- `src/pages/` - Full page components (HomePage, SubmissionPage, ApprovalPage)
  - Complete pages using templates
  - Connect to data and state
  - Route-level components
  - Test files co-located: `HomePage.test.tsx` next to `HomePage.tsx`
- `src/features/` - Feature modules (package submission, approval, etc.)
- `src/api/` - API client code
  - Service files with co-located mocks: `packageService.ts`, `packageService.mock.ts`, `packageService.test.ts`
- `src/hooks/` - Custom React hooks
  - Test files co-located: `usePackageData.test.ts` next to `usePackageData.ts`
- `src/store/` - Zustand stores
  - Test files co-located: `packageStore.test.ts` next to `packageStore.ts`
- `src/types/` - TypeScript types
- `src/utils/` - Utility functions
  - Test files co-located: `formatDate.test.ts` next to `formatDate.ts`

**Test File Naming Convention:**
- Component unit tests: `{ComponentName}.test.tsx` or `{ComponentName}.test.ts`
- Service mocks: `{ServiceName}.mock.ts`
- Storybook stories: `{ComponentName}.stories.tsx`
- All test files are co-located in the same directory as the file they test

**Tests:**
- `features/` - Gherkin feature files
- `steps/` - Step definitions
- Organized by domain (api/, frontend/, e2e/)

### Error Handling

**Backend:**
- Standardized error response format:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable message",
      "details": {}
    }
  }
  ```
- HTTP status codes: 400, 401, 403, 404, 409, 500, 503
- Exception hierarchy for different error types
- Logging of all errors with context

**Frontend:**
- React Query error handling
- User-friendly error messages
- Error boundaries for component errors
- Toast notifications for user feedback

### Logging Strategy

**Format:** Structured JSON logging
**Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
**Fields:**
- Timestamp
- Service name
- Log level
- Message
- Context (user_id, request_id, etc.)
- Stack traces for errors

**Backend:** Python `logging` module with JSON formatter
**Frontend:** Console logging in dev, structured logging service in prod

### Date/Time Handling

**Backend:**
- Store: UTC in database (PostgreSQL `TIMESTAMP WITH TIME ZONE`)
- Library: `datetime` with `zoneinfo` (Python 3.9+) or `pytz`
- API: ISO 8601 format strings (`YYYY-MM-DDTHH:MM:SSZ`)
- Always convert to UTC before storing

**Frontend:**
- Library: `date-fns` for date manipulation
- Display: User's local timezone (automatic conversion)
- API: ISO 8601 format strings
- Store timestamps as ISO strings, display with timezone conversion

### Authentication Pattern

**Backend:**
- FastAPI dependency: `get_current_user(token: str = Depends(oauth2_scheme))`
- RBAC dependency: `require_role(role: str)` decorator/dependency
- Token validation in API Gateway before routing
- User context passed via headers or request state

**Frontend:**
- Store tokens: HTTP-only cookies (preferred) or secure storage
- Axios interceptors for token injection
- Automatic token refresh on 401 responses
- React Query handles authentication state

### API Response Format

**Standard Success Response:**
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-12T10:00:00Z"
  }
}
```

**Paginated Response:**
```json
{
  "data": [ ... ],
  "meta": {
    "timestamp": "2025-11-12T10:00:00Z",
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

---

## Security Architecture

### Authentication Flow

1. User authenticates with ADFS (OAuth 2.0)
2. ADFS returns authorization code
3. Authentication service exchanges code for tokens
4. Authentication service issues JWT access token (15 min) and refresh token (7 days, stateless)
5. Client stores tokens securely
6. API Gateway validates access token on each request
7. Refresh token used to get new access token when expired

### Authorization Flow

1. API Gateway validates JWT token
2. Extracts user ID and roles from token claims
3. Forwards request with user context to microservice
4. Microservice dependency checks user role against endpoint requirements
5. Request proceeds or returns 403 Forbidden

### Token Structure

**Access Token Claims:**
```json
{
  "sub": "user_id",
  "roles": ["submitter", "reviewer"],
  "exp": 1234567890,
  "iat": 1234567890,
  "iss": "airlock-auth-service"
}
```

**Refresh Token Claims:**
```json
{
  "sub": "user_id",
  "type": "refresh",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "token_id",  // For rotation tracking
  "iss": "airlock-auth-service"
}
```

**Token Rotation:**
- When refresh token is used, issue new access token AND new refresh token
- Old refresh token becomes invalid (stateless - validated via jti claim)
- Prevents token reuse attacks

### API Key Management

**Approach:** Separate API Key Service (see Authentication & Authorization Architecture section above for details)

---

## Data Architecture

**Database:** PostgreSQL

**Rationale:**
- Reliable, ACID-compliant relational database
- Excellent for audit trails and compliance requirements
- Strong security features
- Good performance for our scale
- Well-supported with Python (SQLAlchemy, asyncpg)
- Works well in Docker

**Data Models:**
- **Users** - User accounts, roles, profiles
- **Packages** - Package metadata, versions, status
- **Workflows** - Workflow state, stages, history
- **Check Results** - Trivy scan results, license check results, other automated checks
- **Audit Logs** - All operations, approvals, rejections, user actions
- **API Keys** - API key records, scopes, permissions (hashed keys)
- **Package Usage** - Tracking which packages are used where
- **Workflow Agents** - Agent status, check configurations

---

## API Contracts

### Request/Response Format

**Standard Response:**
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-12T10:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### Authentication Headers

**Access Token:**
```
Authorization: Bearer <jwt_access_token>
```

**API Key (if applicable):**
```
X-API-Key: <api_key>
```

---

## Development Environment

### Prerequisites

- Docker & Docker Compose (latest stable)
- Node.js 24.x (verified 2025-11-12) - for frontend development
- Python 3.12.7 (verified 2025-11-12) - for backend development (optional, Docker preferred)

### Local Development Setup

**Start all services:**
```bash
docker-compose up
```

**Services:**
- API Gateway: http://localhost:8000
- Frontend: http://localhost:3000
- RabbitMQ Management: http://localhost:15672
- Mock OAuth Provider: http://localhost:8001
- [Other services as configured]

### Mock Services

**Mock OAuth Provider:**
- Simulates ADFS for local development
- Provides OAuth 2.0 endpoints
- Test users and roles
- Located in `mock-services/mock-oauth/`

---

## Deployment Architecture

### Docker-Based Deployment

**All services containerized:**
- Each service has its own Dockerfile
- Multi-stage builds for optimization
- Environment variables for configuration
- Health checks configured

### Environment Configuration

**Environment Variables:**
- Database connection strings
- RabbitMQ connection
- ADFS OAuth configuration
- External artifact storage configuration
- JWT secret keys
- Service URLs

**Configuration Files:**
- `.env` for local development
- Environment-specific configs for deployment
- No hardcoded values

### Cloud/On-Prem Agnostic

- Works in both cloud and on-prem environments
- Docker Compose for simple deployments
- Kubernetes-ready (if needed in future)
- No cloud-specific dependencies

---

## Testing Architecture

### BDD Testing Structure

**Feature Files:**
```
features/
  api/
    package_submission.feature
    approval_workflow.feature
  frontend/
    package_submission_ui.feature
  e2e/
    complete_approval_flow.feature
```

**Step Definitions:**
- Python: `features/steps/` (pytest-bdd or behave)
- TypeScript: `features/steps/` (Cucumber.js)

**Test Execution:**
- Unit tests: Fast, isolated
- Integration tests: With test database, RabbitMQ
- Component tests: Storybook
- E2E tests: Playwright/Cypress with Cucumber

---

## Architecture Decision Records (ADRs)

### ADR-001: Microservices Architecture with Event-Driven Workflows

**Status:** Accepted

**Context:**
Airlock requires independent scaling of workflow agents, API services, and integration components. The system needs asynchronous approval workflows where different agents pick up work at different stages.

**Decision:**
Adopt microservices architecture with event-driven communication using RabbitMQ and Celery for workflow processing.

**Consequences:**
- **Positive:** Independent scaling, clear service boundaries, flexible workflow orchestration
- **Negative:** Operational complexity, distributed system debugging challenges
- **Neutral:** Learning curve for event-driven patterns

---

### ADR-002: FastAPI + Celery + RabbitMQ Technology Stack

**Status:** Accepted

**Context:**
Need modern Python framework with async support, mature workflow processing, and reliable messaging for event-driven architecture.

**Decision:**
Use FastAPI for API services, Celery for workflow agents, and RabbitMQ for event messaging.

**Consequences:**
- **Positive:** Modern async support, mature tooling, excellent documentation
- **Negative:** Multiple services to manage
- **Neutral:** Good Python ecosystem support

---

### ADR-003: External ADFS Authentication with Stateless JWT

**Status:** Accepted

**Context:**
Enterprise requirement for ADFS integration. Need scalable authentication without server-side token storage.

**Decision:**
Integrate with external ADFS using OAuth 2.0. Use stateless JWT tokens with refresh token rotation.

**Consequences:**
- **Positive:** Enterprise standard, scalable, no token storage overhead
- **Negative:** Dependency on external ADFS service
- **Neutral:** Mock service needed for development

---

### ADR-004: Separate API Key Service

**Status:** Accepted

**Context:**
Need programmatic API access separate from user accounts, with flexible scoping.

**Decision:**
Implement dedicated API Key Service as separate microservice.

**Consequences:**
- **Positive:** Independent management, flexible scoping, clear separation
- **Negative:** Additional service to maintain
- **Neutral:** More services in architecture

---

### ADR-005: PostgreSQL for Primary Data Storage

**Status:** Accepted

**Context:**
Need reliable database for audit trails, compliance, and structured data with relationships.

**Decision:**
Use PostgreSQL as primary database for all services.

**Consequences:**
- **Positive:** ACID compliance, excellent for audit trails, strong security
- **Negative:** Relational model may be restrictive for some use cases
- **Neutral:** Well-supported with Python

---

### ADR-006: BDD Testing with Cucumber/Gherkin

**Status:** Accepted

**Context:**
Need readable, maintainable tests that serve as living documentation.

**Decision:**
Use BDD approach with Cucumber/Gherkin for all test levels.

**Consequences:**
- **Positive:** Living documentation, readable by non-technical stakeholders
- **Negative:** Additional abstraction layer
- **Neutral:** Feature files require maintenance

---

## Version Information

**Version Verification Date:** 2025-11-12

**Backend Technologies:** Specific versions are specified for backend technologies (Python, FastAPI, Celery, etc.) to ensure stability and reproducibility.

**Frontend Technologies:** 
- Node.js: 24.x (specific minor version to be determined at implementation)
- React: 19.2.0 (React does not use LTS releases)
- All other frontend libraries: Latest from npm as of verification date. Install with `npm install <package>@latest` or check npm registry for current version at implementation time.

When updating versions in the future, verify compatibility between all components and update this document accordingly.

## Next Steps

1. ✅ **Technology Versions Specified** - All starting versions documented above
2. ✅ **Epic Breakdown** - Completed (see epics.md)
3. **Project Initialization** - Set up project structure per architecture
4. **Mock OAuth Service** - Implement mock ADFS/OAuth provider for development

---

_Generated by BMAD Decision Architecture Workflow v1.3.2_
_Date: 2025-11-12_
_For: BMad_

