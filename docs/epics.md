# Airlock - Epic Breakdown

**Author:** BMad
**Date:** 2025-11-12
**Project Level:** Level 3-4
**Target Scale:** Multiple thousands of packages, quite a few users, low request volume

---

## Overview

This document provides the complete epic and story breakdown for Airlock, decomposing the requirements from the [PRD](./PRD.md) into implementable stories organized by value-delivering epics.

**Epic Structure:**
1. **Foundation & Infrastructure** - Establish project foundation and core infrastructure
2. **Authentication & Authorization** - Secure access control system
3. **Package Request Submission & Processing** - Enable package-lock.json submission and dependency extraction
4. **Automated Security Checks Framework** - Extensible automated checks system
5. **Approval Workflow System** - Event-driven approval workflow orchestration
6. **Package Tracking & Lock-Down** - Package usage tracking and version control
7. **External Integrations** - Artifact storage and registry integrations
8. **Frontend Application** - User-facing web interface

---

## Epic 1: Foundation & Infrastructure

**Goal:** Establish the foundational project structure, Docker infrastructure, core services scaffolding, database setup, and development environment to enable all subsequent development work.

### Story 1.1: Project Structure and Repository Setup

As a developer,
I want a well-organized project structure with all service directories and configuration files,
So that I have a clear foundation for implementing all services.

**Acceptance Criteria:**

**Given** I am starting a greenfield project
**When** I initialize the repository structure
**Then** I have the following directory structure:
- `services/` directory with subdirectories for all 11 microservices
- `frontend/` directory for React application
- `mock-services/` directory for development mocks
- `shared/` directory for shared code
- `tests/` directory for integration/E2E tests
- `docs/` directory for documentation
- `.env.example` file with environment variable templates
- `README.md` with project overview

**And** All service directories have placeholder `Dockerfile` and `requirements.txt` (or `package.json` for frontend)

**Prerequisites:** None (this is the first story)

**Technical Notes:**
- Follow architecture document project structure
- Create all service directories: api-gateway, auth-service, user-service, api-key-service, submission-service, workflow-service, agents (trivy-agent, license-agent, review-agent), storage-service, registry-service, tracking-service, frontend
- Include mock-services/mock-oauth directory
- Set up shared/python/airlock_common and shared/types directories

---

### Story 1.2: Docker Compose Configuration (Production and Development)

As a developer,
I want Docker Compose configurations for both production and development,
So that I can run the system in different environments with appropriate configurations.

**Acceptance Criteria:**

**Given** I have the project structure set up
**When** I examine the Docker Compose configuration
**Then** I have:
- `docker-compose.prod.yml` - Production-ready configuration with all services
- `docker-compose.dev.yml` - Development configuration that extends prod and adds mocks
- `.env.prod` - Production environment variables
- `.env.dev` - Development environment variables

**And** Production configuration includes:
- PostgreSQL database
- RabbitMQ message broker
- All 11 microservices (with basic FastAPI apps)
- Frontend service (with basic React app)
- Production-ready settings (no mocks, proper networking, health checks)

**And** Development configuration:
- Extends `docker-compose.prod.yml` using `extends` or `include`
- Adds mock OAuth service
- Adds development-specific settings (hot reload volumes, exposed ports)
- Uses `.env.dev` for environment variables

**And** All environment-specific variables are in `.env` files (not hardcoded)
**And** Only differences between prod and dev are in the dev file (mainly mocks)
**And** Services can communicate with each other via Docker network
**And** Ports are properly exposed for local development
**And** Production configuration is ready for deployment

**Prerequisites:** Story 1.1

**Technical Notes:**
- Use architecture document service definitions
- Configure service dependencies (e.g., services depend on PostgreSQL and RabbitMQ)
- Set up health checks for services
- Production: Use `docker-compose -f docker-compose.prod.yml --env-file .env.prod up`
- Development: Use `docker-compose -f docker-compose.dev.yml --env-file .env.dev up`
- Configure volumes for development (hot reload) in dev file only
- Expose management UIs (RabbitMQ management on 15672) in dev file
- Keep prod configuration minimal and production-ready
- All variable differences should be in environment files, not compose files

---

### Story 1.3: PostgreSQL Database Setup and Schema Foundation

As a developer,
I want a PostgreSQL database with initial schema structure,
So that I can store application data from the start.

**Acceptance Criteria:**

**Given** I have Docker Compose running
**When** I initialize the database
**Then** PostgreSQL is running and accessible
**And** I have database migration system set up (Alembic or similar)
**And** Initial schema includes tables for:
- Users (id, username, email, roles, created_at, updated_at)
- Package Submissions (id, user_id, project_name, package_lock_json, status, created_at, updated_at)
- Package Requests (id, submission_id, package_name, package_version, status, created_at, updated_at)
- Packages (id, name, version, status, metadata, fetched_at, created_at, updated_at) - for fetched/approved packages
- Workflows (id, package_request_id, status, current_stage, created_at, updated_at)
- Check Results (id, workflow_id, check_type, status, results, created_at)
- Audit Logs (id, user_id, action, resource_type, resource_id, details, timestamp)
- API Keys (id, key_hash, scopes, permissions, created_at, expires_at)
- Package Usage (id, package_request_id, project_name, created_at) - tracks which projects use approved packages

**And** Database connection is configurable via environment variables

**Prerequisites:** Story 1.2

**Technical Notes:**
- Use SQLAlchemy for ORM
- Set up Alembic for migrations
- Create initial migration with base schema
- Configure asyncpg for async database access
- Set up database connection pooling
- Package Submissions table stores package-lock.json submissions
- Package Requests table stores individual dependency requests (one per dependency from package-lock.json)
- Packages table stores fetched package data (from NPM registry)
- Package Usage links approved package requests to projects

---

### Story 1.4: RabbitMQ Message Broker Setup

As a developer,
I want RabbitMQ configured for event-driven communication,
So that services can communicate asynchronously via events.

**Acceptance Criteria:**

**Given** I have Docker Compose running
**When** I start RabbitMQ
**Then** RabbitMQ is running and accessible
**And** Management UI is available on port 15672
**And** I have exchanges configured for:
- `package.events` exchange for package-related events
- `workflow.events` exchange for workflow-related events
- `check.events` exchange for check-related events

**And** Dead letter queues are configured for failed messages
**And** Connection is configurable via environment variables

**Prerequisites:** Story 1.2

**Technical Notes:**
- Configure RabbitMQ with management plugin
- Set up exchanges and queues as per architecture
- Configure message persistence
- Set up dead letter queues for error handling

---

### Story 1.5: Core FastAPI Service Scaffolding

As a developer,
I want basic FastAPI service scaffolding for all backend services,
So that I have a consistent foundation for implementing service logic.

**Acceptance Criteria:**

**Given** I have the project structure
**When** I create a new service
**Then** Each service has:
- `src/main.py` with FastAPI app instance
- `src/routers/` directory for route handlers
- `src/models/` directory for data models
- `src/services/` directory for business logic
- `src/dependencies/` directory for FastAPI dependencies
- `src/utils/` directory for utility functions
- `requirements.txt` with FastAPI and core dependencies
- `Dockerfile` with multi-stage build

**And** All services follow the same structure pattern
**And** Services can start and respond to health check endpoints

**Prerequisites:** Story 1.1

**Technical Notes:**
- Use architecture document code organization patterns
- Include FastAPI, uvicorn, python-multipart in requirements
- Set up health check endpoint (`/health`)
- Configure CORS appropriately
- Set up structured logging

---

### Story 1.6: Frontend React Application Setup

As a developer,
I want a React + TypeScript application with Vite and all required dependencies,
So that I have a foundation for building the frontend UI.

**Acceptance Criteria:**

**Given** I have the project structure
**When** I initialize the frontend application
**Then** I have:
- React + TypeScript application created with Vite
- Material UI installed and configured
- React Query set up for data fetching
- TanStack Router configured for routing
- Zustand set up for state management
- React Hook Form installed
- Axios configured for API calls
- Storybook set up for component testing
- BDD testing tools (Cucumber.js) configured
- Accessibility testing tools (axe-core) configured

**And** Application starts successfully with `npm run dev`
**And** Basic routing structure is in place
**And** Material UI theme is configured
**And** Atomic design pattern structure is set up:
- `src/components/atoms/` - Basic building blocks (buttons, inputs, labels)
- `src/components/molecules/` - Simple component groups (form fields, search bars)
- `src/components/organisms/` - Complex UI sections (forms, data tables, navigation)
- `src/components/templates/` - Page layouts (dashboard layout, form layout)
- `src/pages/` - Full page components

**Prerequisites:** Story 1.1

**Technical Notes:**
- Use `npm create vite@latest frontend -- --template react-ts`
- Install all dependencies from PRD technology stack
- Configure Vite for development and production builds
- Set up TypeScript with strict mode
- Configure path aliases for imports
- Organize components using atomic design pattern
- Atoms: Smallest components (Button, Input, Label, Icon)
- Molecules: Simple combinations (FormField, SearchBar, Card)
- Organisms: Complex sections (DataTable, Navigation, Form)
- Templates: Page layouts (DashboardLayout, FormLayout)
- Pages: Full page components (HomePage, SubmissionPage)
- **Test File Organization (Co-located):**
  - Component unit tests: `component.test.ts` or `component.test.tsx` next to component file
  - Service mocks: `service.mock.ts` next to service file
  - Storybook stories: `component.stories.tsx` next to component file
  - All test files in same subfolder as the component/service they test
  - Example structure:
    ```
    components/atoms/Button/
      Button.tsx
      Button.test.tsx
      Button.stories.tsx
    services/api/
      packageService.ts
      packageService.mock.ts
      packageService.test.ts
    ```

---

### Story 1.7: Mock OAuth Service for Development

As a developer,
I want a mock OAuth provider that simulates ADFS for local development,
So that I can develop authentication features without external dependencies.

**Acceptance Criteria:**

**Given** I have Docker Compose running
**When** I start the mock OAuth service
**Then** Mock OAuth service is running
**And** It provides OAuth 2.0 endpoints:
- `/authorize` - Authorization endpoint
- `/token` - Token exchange endpoint
- `/userinfo` - User info endpoint

**And** It supports test users with different roles (Submitter, Reviewer, Admin)
**And** It issues JWT tokens compatible with production flow
**And** It can be configured via environment variables

**Prerequisites:** Story 1.2

**Technical Notes:**
- Implement OAuth 2.0 Authorization Code flow
- Use FastAPI for the mock service
- Create test users with different roles
- Issue JWT tokens with proper claims
- Match production ADFS flow as closely as possible

---

### Story 1.8: Shared Libraries and Common Utilities

As a developer,
I want shared libraries for common functionality,
So that I can reuse code across services without duplication.

**Acceptance Criteria:**

**Given** I have the project structure
**When** I set up shared libraries
**Then** I have:
- `shared/python/airlock_common/` package with:
  - Common data models
  - Utility functions
  - Constants and configuration helpers
- `shared/types/` directory with:
  - Shared TypeScript types/interfaces
  - API contract types

**And** Shared Python package can be imported by all services
**And** Shared TypeScript types can be imported by frontend
**And** Package structure follows Python/TypeScript best practices

**Prerequisites:** Story 1.1

**Technical Notes:**
- Set up Python package with proper `__init__.py` files
- Configure package for installation in development mode
- Create shared types for API contracts
- Document shared utilities

---

## Epic 2: Authentication & Authorization

**Goal:** Implement secure authentication and authorization system with ADFS integration, RBAC, and API key management to protect all system resources.

### Story 2.1: Authentication Service - OAuth2 Integration with ADFS

As a user,
I want to authenticate using my organization's ADFS credentials,
So that I can securely access the Airlock system.

**Acceptance Criteria:**

**Given** I am a user with ADFS credentials
**When** I attempt to log in
**Then** I am redirected to ADFS for authentication
**And** After successful ADFS authentication, I receive JWT access token (15 min expiry) and refresh token (7 days, stateless)
**And** Tokens include my user ID and roles in claims
**And** In development, mock OAuth service provides the same flow

**Prerequisites:** Story 1.2, Story 1.7

**Technical Notes:**
- Implement OAuth 2.0 Authorization Code flow
- Use FastAPI OAuth2 integration
- Configure ADFS endpoints via environment variables
- Use python-jose for JWT encoding/decoding
- Implement stateless refresh token rotation
- Support both production ADFS and development mock

---

### Story 2.2: JWT Token Validation and User Context Extraction

As a service,
I want to validate JWT tokens and extract user context,
So that I can enforce authorization on protected endpoints.

**Acceptance Criteria:**

**Given** A request includes a JWT token in Authorization header
**When** The token is validated
**Then** Token signature is verified
**And** Token expiration is checked
**And** User ID and roles are extracted from token claims
**And** Invalid or expired tokens return 401 Unauthorized
**And** User context is available to endpoint handlers via FastAPI dependency

**Prerequisites:** Story 2.1

**Technical Notes:**
- Create FastAPI dependency for token validation
- Extract user context (user_id, roles) from JWT claims
- Handle token expiration gracefully
- Return appropriate error responses

---

### Story 2.3: Role-Based Access Control (RBAC) Implementation

As a system administrator,
I want to enforce role-based access control on all endpoints,
So that users can only access resources appropriate for their role.

**Acceptance Criteria:**

**Given** I have defined roles (Submitter, Reviewer, Admin)
**When** A user attempts to access an endpoint
**Then** Their role is checked against endpoint requirements
**And** Submitters can only access submission endpoints
**And** Reviewers can access approval workflow endpoints
**And** Admins can access all endpoints
**And** Unauthorized access returns 403 Forbidden

**Prerequisites:** Story 2.2

**Technical Notes:**
- Create RBAC dependency decorator/function
- Define role permissions for each endpoint
- Implement role checking logic
- Use FastAPI dependencies for role enforcement

---

### Story 2.4: User Management Service - User Profiles and Roles

As a system administrator,
I want to manage user profiles and assign roles,
So that I can control access to system resources.

**Acceptance Criteria:**

**Given** I am an admin user
**When** I access user management endpoints
**Then** I can view all users
**And** I can assign roles to users (Submitter, Reviewer, Admin)
**And** I can update user profiles
**And** User role changes are reflected in subsequent authentication tokens
**And** All user management actions are logged in audit trail

**Prerequisites:** Story 1.3, Story 2.3

**Technical Notes:**
- Implement user management endpoints
- Store user profiles in database
- Support role assignment
- Integrate with audit logging

---

### Story 2.5: API Key Service - Key Generation and Management

As a developer,
I want to generate and manage API keys for programmatic access,
So that I can integrate Airlock with external systems.

**Acceptance Criteria:**

**Given** I am an admin user
**When** I generate an API key
**Then** A secure API key is generated
**And** Key is hashed before storage in database
**And** Key has associated scopes/permissions (read-only, read-write, admin)
**And** I can view all API keys
**And** I can revoke API keys
**And** I can rotate API keys

**Prerequisites:** Story 1.3, Story 2.3

**Technical Notes:**
- Implement API key generation with secure random generation
- Hash keys using bcrypt or similar
- Store keys in database with scopes
- Implement key revocation and rotation

---

### Story 2.6: API Key Authentication and Token Issuance

As a system,
I want to authenticate API key requests and issue tokens,
So that API keys can be used for programmatic access.

**Acceptance Criteria:**

**Given** A request includes an API key in X-API-Key header
**When** The API key is validated
**Then** Key is looked up in database (by hash)
**And** Key validity is checked (not revoked, not expired)
**And** JWT token is issued with key's scopes/permissions
**And** Token follows same structure as user authentication tokens
**And** Invalid keys return 401 Unauthorized

**Prerequisites:** Story 2.5, Story 2.2

**Technical Notes:**
- Implement API key validation endpoint
- Issue JWT tokens for valid API keys
- Include scopes in token claims
- Handle key expiration and revocation

---

### Story 2.7: API Gateway - Token Validation and Request Routing

As a system,
I want an API Gateway that validates tokens and routes requests,
So that all services receive authenticated and authorized requests.

**Acceptance Criteria:**

**Given** A client request arrives at the API Gateway
**When** The request is processed
**Then** Token is validated (if authentication required)
**And** User context is extracted from token
**And** Request is routed to appropriate microservice
**And** User context is forwarded to downstream services
**And** Unauthenticated requests to protected endpoints return 401
**And** Rate limiting is applied

**Prerequisites:** Story 2.2, Story 1.5

**Technical Notes:**
- Implement API Gateway service
- Integrate token validation
- Route requests to microservices
- Forward user context via headers
- Implement basic rate limiting

---

## Epic 3: Package Request Submission & Processing

**Goal:** Enable users to submit package-lock.json files from consuming projects, which are processed to extract dependencies and create package requests for approval.

### Story 3.1: Package Request Submission Service - Accept package-lock.json Submissions

As a submitter,
I want to submit a package-lock.json file from my project,
So that all dependencies can be processed and requested for approval.

**Acceptance Criteria:**

**Given** I am an authenticated user with Submitter role
**When** I submit a package-lock.json file
**Then** File is received and validated (valid package-lock.json format)
**And** Project name and version are extracted from package-lock.json root fields (`name`, `version`)
**And** Submission is recorded in database with extracted project name and version
**And** I receive confirmation with submission ID
**And** File is queued for processing

**Prerequisites:** Story 2.7, Story 1.3

**Technical Notes:**
- Implement package-lock.json submission endpoint
- Accept JSON file upload
- Validate package-lock.json schema/structure
- Extract project name and version from package-lock.json root fields:
  - `name` field (required) - project name
  - `version` field (required) - project version
- Store submission record with extracted project name and version
- Queue for dependency extraction

---

### Story 3.2: Package-lock.json Processing and Dependency Extraction

As a system,
I want to process package-lock.json files and extract all dependencies,
So that each dependency can become a package request.

**Acceptance Criteria:**

**Given** A valid package-lock.json has been submitted
**When** Processing runs
**Then** package-lock.json is parsed correctly
**And** All dependencies are extracted (including nested dependencies)
**And** Each dependency is identified by name and version
**And** Dependency tree structure is preserved
**And** Processing results are stored

**Prerequisites:** Story 3.1

**Technical Notes:**
- Parse package-lock.json JSON structure
- Extract project name and version from root fields (already extracted in Story 3.1, but validate)
- Extract all packages from `packages` or `dependencies` section
- Handle nested dependencies correctly
- Extract package name and version for each dependency
- Store dependency list with submission

---

### Story 3.3: Package Request Creation from Dependencies

As a system,
I want to create package requests for each extracted dependency,
So that each package can go through the approval workflow.

**Acceptance Criteria:**

**Given** Dependencies have been extracted from package-lock.json
**When** Package requests are created
**Then** A package request is created for each unique dependency (name + version)
**And** Each request is linked to the original submission/project
**And** Duplicate requests (same package already requested) are handled appropriately
**And** Package requests are stored in database
**And** Each request is queued for workflow processing

**Prerequisites:** Story 3.2

**Technical Notes:**
- Create Package Request records for each dependency
- Link requests to submission/project
- Handle deduplication (check if package already requested/approved)
- Store request status (pending, in-workflow, approved, rejected)
- Queue requests for workflow

---

### Story 3.4: Package Request Event Publishing

As a system,
I want to publish package request events,
So that workflow agents can pick up package requests for processing.

**Acceptance Criteria:**

**Given** Package requests have been created
**When** Requests are ready for workflow
**Then** `package.requested` event is published to RabbitMQ for each request
**And** Event includes package name, version, and request ID
**And** Workflow service receives the events
**And** Workflows are created for each package request

**Prerequisites:** Story 3.3, Story 1.4

**Technical Notes:**
- Publish events to RabbitMQ
- Use package.events exchange
- Include package name, version, and request ID in event payload
- Ensure event delivery reliability
- Handle batch processing of multiple requests

---

## Epic 4: Automated Security Checks Framework

**Goal:** Build an extensible framework for automated security checks with Trivy scanning and license validation as initial implementations.

### Story 4.1: Extensible Checks Framework Architecture

As a system architect,
I want an extensible framework for automated checks,
So that new checks can be added without major code changes.

**Acceptance Criteria:**

**Given** I have the checks framework
**When** I register a new check
**Then** Check can be registered via configuration
**And** Check can be enabled/disabled
**And** Check execution order can be configured
**And** Check results follow standard format
**And** Check failures are handled gracefully

**Prerequisites:** Story 1.4, Story 1.5

**Technical Notes:**
- Design check interface/contract
- Implement check registration mechanism
- Create check configuration management
- Define standard check result format
- Implement check execution framework

---

### Story 4.2: Trivy Scanner Agent Implementation

As a security team,
I want package requests automatically scanned for vulnerabilities using Trivy,
So that security issues are detected before approval.

**Acceptance Criteria:**

**Given** A package has been fetched for a package request
**When** Trivy scan is triggered
**Then** Trivy scanner processes the package (tarball or files)
**And** Vulnerability scan results are generated
**And** Results include CVE IDs, severity levels, and descriptions
**And** Results are stored in database
**And** `check.trivy.completed` event is published
**And** Packages with high/critical vulnerabilities are flagged

**Prerequisites:** Story 4.1, Story 3.4, Story 7.2 (NPM registry integration to fetch package)

**Technical Notes:**
- Integrate Trivy scanner (CLI or library)
- Process package tarball (fetched from NPM registry)
- Parse Trivy JSON output
- Store results in Check Results table
- Support configurable severity thresholds

---

### Story 4.3: License Check Agent Implementation

As a security team,
I want package requests automatically checked against license allowlist,
So that only approved licenses are used.

**Acceptance Criteria:**

**Given** A package has been fetched for a package request
**When** License check is triggered
**Then** License information is extracted from package metadata (package.json)
**And** License is validated against configured allowlist
**And** License check results are stored
**And** `check.license.completed` event is published
**And** Packages with non-approved licenses are flagged
**And** Complex license expressions (AND, OR) are handled correctly

**Prerequisites:** Story 4.1, Story 3.4, Story 7.2 (NPM registry integration to fetch package)

**Technical Notes:**
- Extract license from package.json (from fetched package)
- Parse SPDX license identifiers
- Validate against allowlist (from database)
- Support license expressions
- Store check results

---

### Story 4.4: Check Configuration Management

As a system administrator,
I want to configure automated checks,
So that I can enable/disable checks and adjust settings.

**Acceptance Criteria:**

**Given** I am an admin user
**When** I access check configuration
**Then** I can view all available checks
**And** I can enable/disable checks
**And** I can configure check settings (e.g., severity thresholds for Trivy)
**And** I can update license allowlist
**And** Configuration changes are persisted
**And** Configuration is used by check agents

**Prerequisites:** Story 4.1, Story 2.3

**Technical Notes:**
- Implement check configuration endpoints
- Store configuration in database
- Support check-specific settings
- Manage license allowlist
- Apply configuration to check execution

---

## Epic 5: Approval Workflow System

**Goal:** Implement event-driven approval workflow system that orchestrates automated checks and manual review processes.

### Story 5.1: Workflow Service - Workflow State Management

As a system,
I want to manage workflow state for package request approvals,
So that package requests progress through approval stages correctly.

**Acceptance Criteria:**

**Given** A package request has been created
**When** Workflow is created
**Then** Workflow record is created in database
**And** Workflow tracks current stage (requested, fetching, validating, checking, reviewing, approved/rejected)
**And** Workflow state can be updated as stages complete
**And** Workflow history is maintained
**And** Workflow can be queried by ID
**And** Workflow is linked to package request

**Prerequisites:** Story 1.3, Story 3.4

**Technical Notes:**
- Implement workflow state machine
- Store workflow in database
- Link workflow to package request (name + version)
- Track workflow stages
- Maintain workflow history
- Support workflow queries

---

### Story 5.2: Event-Driven Workflow Orchestration

As a system,
I want to orchestrate workflow stages via events,
So that workflow agents can process package requests asynchronously.

**Acceptance Criteria:**

**Given** A workflow has been created for a package request
**When** Events are published
**Then** Workflow service listens to relevant events
**And** Workflow state is updated based on events
**And** Next stage is triggered when previous stage completes
**And** Workflow progresses: package fetch → validation → checks → manual review
**And** Workflow completion triggers final events

**Prerequisites:** Story 5.1, Story 1.4

**Technical Notes:**
- Implement event listeners in workflow service
- Update workflow state based on events
- Trigger next workflow stages
- Handle event ordering and idempotency
- First stage: fetch package from NPM registry (if not already available)

---

### Story 5.3: Manual Review Interface and Approval/Rejection

As a reviewer,
I want to review package requests and make approval decisions,
So that package requests can be approved or rejected with justification.

**Acceptance Criteria:**

**Given** I am a reviewer and a package request is ready for review
**When** I access the review interface
**Then** I can see package request details (name, version, requesting project)
**And** I can see package details (fetched from NPM registry) and automated check results
**And** I can approve the package request with optional comments
**And** I can reject the package request with required justification
**And** I can override automated check failures with justification
**And** My decision is recorded in audit trail
**And** `workflow.approved` or `workflow.rejected` event is published

**Prerequisites:** Story 5.2, Story 4.2, Story 4.3

**Technical Notes:**
- Implement review endpoints
- Display package request and package information
- Show which project(s) are requesting the package
- Support approval/rejection with comments
- Support check override with justification
- Publish workflow completion events

---

### Story 5.4: Workflow Notification System

As a user,
I want to be notified of workflow state changes,
So that I know when my package is approved or rejected.

**Acceptance Criteria:**

**Given** A workflow state changes (approved/rejected)
**When** Notification is triggered
**Then** Submitter is notified of the decision
**And** Notification includes package details and decision reason
**And** Notifications can be delivered via multiple channels (in-app, email - future)
**And** Notification delivery is logged

**Prerequisites:** Story 5.3

**Technical Notes:**
- Implement notification service/endpoint
- Store notification preferences
- Send notifications on workflow completion
- Log notification delivery
- Support future notification channels

---

## Epic 6: Package Tracking & Lock-Down

**Goal:** Track approved package usage across the organization and prevent unauthorized package upgrades.

### Story 6.1: Package Tracking Service - Usage Tracking

As a system administrator,
I want to track where approved packages are used,
So that I have visibility into package usage across the organization.

**Acceptance Criteria:**

**Given** A package request has been approved
**When** Package is approved for use
**Then** Usage is recorded (package name, version, requesting project/application)
**And** Usage records are stored in database
**And** I can query which projects use a specific package
**And** I can query which packages are used in a project
**And** Usage history is maintained
**And** Multiple projects can use the same approved package

**Prerequisites:** Story 5.3, Story 1.3

**Technical Notes:**
- Implement usage tracking endpoints
- Store usage records in Package Usage table
- Link approved packages to projects that requested them
- Support usage queries
- Track version information
- Handle multiple projects using same package

---

### Story 6.2: Package Lock-Down Mechanism

As a system,
I want to lock approved package versions,
So that automatic upgrades cannot introduce vulnerabilities.

**Acceptance Criteria:**

**Given** A package has been approved
**When** Package version is locked
**Then** Approved version is recorded
**And** Automatic upgrades are prevented
**And** Version lock is enforced at package installation time
**And** Lock status is visible in tracking dashboard

**Prerequisites:** Story 6.1

**Technical Notes:**
- Implement version locking mechanism
- Store approved versions
- Prevent automatic upgrades
- Enforce locks during package operations

---

### Story 6.3: Upgrade Request Workflow

As a developer,
I want to request package upgrades,
So that I can use newer versions when needed (through approval).

**Acceptance Criteria:**

**Given** I want to upgrade a package version
**When** I submit an upgrade request
**Then** Upgrade request is created
**And** Request triggers approval workflow for new version
**And** Existing version remains locked until new version is approved
**And** I can track upgrade request status

**Prerequisites:** Story 6.2, Story 5.1

**Technical Notes:**
- Implement upgrade request endpoint
- Create workflow for upgrade requests
- Link upgrade requests to original packages
- Track upgrade request status

---

### Story 6.4: Package Tracking Dashboard

As a user,
I want to view package usage and tracking information,
So that I can understand package inventory and usage.

**Acceptance Criteria:**

**Given** I am an authenticated user
**When** I access the tracking dashboard
**Then** I can see all approved packages
**And** I can see package usage by project
**And** I can search and filter packages
**And** I can view package versions and lock status
**And** I can export package inventory reports

**Prerequisites:** Story 6.1, Story 6.2

**Technical Notes:**
- Implement tracking dashboard endpoints
- Support search and filtering
- Generate reports
- Display usage information

---

## Epic 7: External Integrations

**Goal:** Integrate with external artifact storage and NPM registry for package storage and distribution.

### Story 7.1: Artifact Storage Integration Service

As a system,
I want to integrate with external artifact storage,
So that approved packages can be stored securely.

**Acceptance Criteria:**

**Given** A package has been approved
**When** Package storage is triggered
**Then** Package is transferred to configured artifact storage
**And** Storage connection is authenticated securely
**And** Package integrity is maintained during transfer
**And** Storage operations support retry on failure
**And** `package.stored` event is published on success

**Prerequisites:** Story 5.3, Story 1.5

**Technical Notes:**
- Implement storage integration service
- Support configurable storage backends
- Secure credential management
- Implement retry logic
- Verify package integrity

---

### Story 7.2: NPM Registry Integration Service

As a system,
I want to integrate with NPM registry,
So that I can fetch packages for processing and publish approved packages.

**Acceptance Criteria:**

**Given** I have a package request (name + version)
**When** I need to fetch the package
**Then** I can fetch package tarball from NPM registry
**And** I can fetch package metadata (package.json) from registry
**And** Package is stored temporarily for processing (Trivy scan, etc.)
**And** I can publish approved packages to registry (if needed)
**And** Registry authentication is handled if required
**And** Rate limits are respected
**And** `package.fetched` event is published on success

**Prerequisites:** Story 3.4, Story 1.5

**Technical Notes:**
- Implement NPM registry integration
- Fetch package tarball by name and version
- Fetch package.json metadata
- Support public and private registries
- Handle registry authentication
- Implement rate limiting
- Follow NPM registry protocols
- Store fetched packages temporarily for processing

---

### Story 7.3: Storage and Registry Configuration Management

As a system administrator,
I want to configure external storage and registry connections,
So that I can connect to different environments.

**Acceptance Criteria:**

**Given** I am an admin user
**When** I configure storage or registry
**Then** I can set connection details (URLs, credentials)
**And** Credentials are stored securely (encrypted)
**And** Configuration is validated before saving
**And** I can test connections
**And** Configuration is used by integration services

**Prerequisites:** Story 7.1, Story 7.2, Story 2.3

**Technical Notes:**
- Implement configuration endpoints
- Secure credential storage
- Validate configuration
- Test connection functionality

---

## Epic 8: Frontend Application

**Goal:** Build a comprehensive React-based web application providing user interfaces for all system capabilities with full accessibility compliance.

### Story 8.1: Frontend Authentication and Routing

As a user,
I want to log in and navigate the application,
So that I can access system features based on my role.

**Acceptance Criteria:**

**Given** I am a user
**When** I access the application
**Then** I am redirected to login if not authenticated
**And** After login, I can navigate to different sections
**And** Routes are protected based on my role
**And** Navigation shows only features I can access
**And** I can log out securely

**Prerequisites:** Story 1.6, Story 2.1

**Technical Notes:**
- Implement authentication flow in React
- Set up TanStack Router with protected routes
- Store tokens securely (HTTP-only cookies preferred)
- Implement role-based route protection
- Handle token refresh

---

### Story 8.2: Package Request Submission UI

As a submitter,
I want to submit package-lock.json files through a web interface,
So that I can request approval for all my project's dependencies.

**Acceptance Criteria:**

**Given** I am a logged-in submitter
**When** I access the submission page
**Then** I can upload a package-lock.json file
**And** Project name and version are automatically extracted from package-lock.json
**And** I can see the extracted project name and version
**And** I can see extracted dependencies after upload
**And** I can submit the package-lock.json
**And** I receive confirmation with submission ID
**And** I can see status of all package requests created from my submission
**And** Form validation prevents invalid submissions
**And** UI is accessible (keyboard navigable, screen reader friendly)

**Prerequisites:** Story 8.1, Story 3.1

**Technical Notes:**
- Implement package-lock.json submission form
- Use React Hook Form for form management
- Handle JSON file uploads
- Extract project name and version from package-lock.json root fields (`name`, `version`)
- Display extracted project name and version (read-only, auto-populated)
- Display extracted dependencies list
- Show submission status and package request statuses
- Use atomic design pattern:
  - Atoms: Button, Input, Label components
  - Molecules: FormField, FileUpload components
  - Organisms: SubmissionForm component
  - Template: FormLayout template
  - Page: PackageSubmissionPage
- Ensure WCAG AA compliance

---

### Story 8.3: Approval Workflow UI

As a reviewer,
I want to review package requests and make approval decisions,
So that I can efficiently process approval requests.

**Acceptance Criteria:**

**Given** I am a logged-in reviewer
**When** I access the approval workflow interface
**Then** I can see pending package requests for review
**And** I can view package request details (name, version, requesting project)
**And** I can view package details (fetched from NPM) and automated check results
**And** I can approve or reject package requests with comments
**And** I can override check failures with justification
**And** UI clearly shows check results and status
**And** UI shows which project(s) are requesting each package
**And** UI is accessible and keyboard navigable

**Prerequisites:** Story 8.1, Story 5.3

**Technical Notes:**
- Implement approval workflow interface
- Display package request and package information
- Show requesting project information
- Support approval/rejection actions
- Show workflow status clearly
- Use atomic design pattern:
  - Atoms: Button, Badge, Icon components
  - Molecules: CheckResultCard, PackageInfoCard components
  - Organisms: ApprovalForm, WorkflowStatusDisplay components
  - Template: DashboardLayout template
  - Page: ApprovalWorkflowPage
- Ensure accessibility compliance

---

### Story 8.4: Package Tracking Dashboard UI

As a user,
I want to view package tracking information,
So that I can see package usage and inventory.

**Acceptance Criteria:**

**Given** I am a logged-in user
**When** I access the tracking dashboard
**Then** I can see all approved packages
**And** I can search and filter packages
**And** I can see package usage by project
**And** I can view package versions and lock status
**And** I can export reports
**And** UI is responsive and accessible

**Prerequisites:** Story 8.1, Story 6.4

**Technical Notes:**
- Implement tracking dashboard
- Use React Query for data fetching
- Support search and filtering
- Display usage information
- Use atomic design pattern:
  - Atoms: Input, Button, Badge components
  - Molecules: SearchBar, FilterBar, PackageCard components
  - Organisms: PackageTable, UsageChart components
  - Template: DashboardLayout template
  - Page: PackageTrackingPage
- Ensure responsive design

---

### Story 8.5: Admin Configuration UI

As an administrator,
I want to configure system settings through the UI,
So that I can manage the system without using APIs directly.

**Acceptance Criteria:**

**Given** I am a logged-in admin
**When** I access admin configuration
**Then** I can manage users and roles
**And** I can configure automated checks
**And** I can manage license allowlist
**And** I can configure storage and registry connections
**And** I can view audit logs
**And** All admin functions are accessible

**Prerequisites:** Story 8.1, Story 2.4, Story 4.4, Story 7.3

**Technical Notes:**
- Implement admin configuration interface
- Support all admin operations
- Ensure proper authorization
- Provide clear UI for configuration
- Use atomic design pattern:
  - Atoms: Button, Input, Select, Switch components
  - Molecules: ConfigField, UserCard, CheckConfigCard components
  - Organisms: UserManagementTable, CheckConfigForm components
  - Template: DashboardLayout template
  - Page: AdminConfigurationPage
- Ensure accessibility

---

### Story 8.6: Frontend Accessibility Compliance and Testing

As a user with accessibility needs,
I want the application to be fully accessible,
So that I can use all features regardless of my abilities.

**Acceptance Criteria:**

**Given** I am using the application
**When** I navigate with keyboard only
**Then** All functionality is accessible via keyboard
**And** Focus indicators are clearly visible
**And** Screen reader announces all content correctly
**And** Color contrast meets WCAG AA standards
**And** Application works at 50% to 200% zoom
**And** Automated accessibility tests (axe-core, Pa11y) pass
**And** Lighthouse accessibility score is ≥ 90

**Prerequisites:** Story 8.1, Story 8.2, Story 8.3, Story 8.4, Story 8.5

**Technical Notes:**
- Ensure all components are accessible (atoms, molecules, organisms, templates)
- Use Material UI accessibility features
- Add ARIA labels where needed
- Test atomic components in Storybook for accessibility
- Build accessibility from atoms up (accessible atoms → accessible molecules → accessible organisms)
- Test with screen readers (NVDA, JAWS, VoiceOver)
- Run automated accessibility tests in CI/CD
- Manual accessibility testing on all features
- Atomic design ensures accessibility is built from the ground up

---

### Story 8.7: Frontend BDD Testing Implementation

As a developer,
I want BDD tests for the frontend,
So that tests serve as living documentation and ensure quality.

**Acceptance Criteria:**

**Given** I have frontend features implemented
**When** I run BDD tests
**Then** Feature files (Gherkin) exist for all major user flows
**And** Step definitions are implemented (Cucumber.js)
**And** Component tests use Storybook with BDD scenarios
**And** E2E tests cover critical flows (Playwright/Cypress with Cucumber)
**And** All tests pass
**And** Tests are readable and serve as documentation

**Prerequisites:** Story 8.1, Story 8.2, Story 8.3, Story 8.4, Story 8.5

**Technical Notes:**
- Write Gherkin feature files for user flows
- Implement Cucumber.js step definitions
- Create Storybook stories with BDD scenarios for atomic components
- Test atoms, molecules, organisms in Storybook
- Set up E2E tests with Playwright/Cypress
- Integrate BDD tests in CI/CD
- Atomic design pattern supports component-level BDD testing
- **Test File Organization:**
  - Component unit tests: `component.test.tsx` co-located with component
  - Storybook stories: `component.stories.tsx` co-located with component
  - Service mocks: `service.mock.ts` co-located with service
  - All test files in same subfolder as the file they test

---

## Summary

**Total Epics:** 8
**Total Stories:** 47

**Epic Breakdown:**
- **Epic 1:** Foundation & Infrastructure - 8 stories
- **Epic 2:** Authentication & Authorization - 7 stories
- **Epic 3:** Package Submission & Validation - 4 stories
- **Epic 4:** Automated Security Checks Framework - 4 stories
- **Epic 5:** Approval Workflow System - 4 stories
- **Epic 6:** Package Tracking & Lock-Down - 4 stories
- **Epic 7:** External Integrations - 3 stories
- **Epic 8:** Frontend Application - 7 stories

**Story Characteristics:**
- All stories are vertically sliced (complete functionality)
- Stories are sequentially ordered (no forward dependencies)
- Stories are sized for single-session completion
- All stories include BDD-style acceptance criteria
- Technical notes provide implementation guidance

**Coverage:**
- ✅ All 8 functional requirements (FR1-FR8) are covered
- ✅ All non-functional requirements are addressed
- ✅ Foundation epic establishes infrastructure for all work
- ✅ Authentication epic enables protected features
- ✅ Package request submission processes package-lock.json files
- ✅ Each dependency becomes a separate package request
- ✅ Core package management features are complete
- ✅ Frontend provides comprehensive UI for all features

**Important Workflow Note:**
- Users submit package-lock.json files from consuming projects
- System extracts all dependencies from package-lock.json
- Each dependency (name + version) becomes a separate package request
- Package requests go through workflow: fetch from NPM → validate → automated checks → manual review → approval/rejection

**Next Steps:**
1. Review epic structure and story breakdown
2. Proceed to `sprint-planning` workflow to create sprint status tracking
3. Use `create-story` workflow to generate detailed implementation plans for individual stories

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._

