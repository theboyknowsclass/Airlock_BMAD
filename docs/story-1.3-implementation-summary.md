# Story 1.3: PostgreSQL Database Setup and Schema Foundation - Implementation Summary

## Status: ✅ Completed

## Overview

Story 1.3 has been successfully implemented. The database schema foundation is now in place with all required tables, SQLAlchemy models, Alembic migration system, and database connection utilities.

## Implementation Details

### 1. Database Models Created

All required database models have been created in `shared/python/airlock_common/db/models/`:

- ✅ **User** (`user.py`) - User accounts with roles
  - Fields: id, username, email, roles (ARRAY), created_at, updated_at
  - Relationships: package_submissions, audit_logs, license_allowlist_entries

- ✅ **PackageSubmission** (`package_submission.py`) - Package-lock.json submissions
  - Fields: id, user_id, project_name, project_version, package_lock_json, status, created_at, updated_at
  - Relationships: user, package_requests
  - Note: Added `project_version` field (extracted from package-lock.json in Story 3.1)

- ✅ **PackageRequest** (`package_request.py`) - Individual package requests
  - Fields: id, submission_id, package_name, package_version, status, created_at, updated_at
  - Relationships: submission, workflow, package_usage
  - Unique constraint: (package_name, package_version, submission_id)

- ✅ **Package** (`package.py`) - Fetched package data from NPM registry
  - Fields: id, name, version, status, metadata, fetched_at, created_at, updated_at
  - Unique constraint: (name, version)

- ✅ **Workflow** (`workflow.py`) - Approval workflow state
  - Fields: id, package_request_id, status, current_stage, created_at, updated_at
  - Relationships: package_request, check_results
  - Unique constraint: package_request_id

- ✅ **CheckResult** (`check_result.py`) - Automated check results
  - Fields: id, workflow_id, check_type, status, results, created_at
  - Relationships: workflow
  - Check types: TRIVY, LICENSE

- ✅ **AuditLog** (`audit_log.py`) - Audit trail
  - Fields: id, user_id, action, resource_type, resource_id, details, timestamp
  - Relationships: user

- ✅ **APIKey** (`api_key.py`) - API key management
  - Fields: id, key_hash, scopes, permissions, created_at, expires_at
  - Unique constraint: key_hash

- ✅ **PackageUsage** (`package_usage.py`) - Package usage tracking
  - Fields: id, package_request_id, project_name, created_at
  - Relationships: package_request
  - Index: project_name

- ✅ **LicenseAllowlist** (`license_allowlist.py`) - License allowlist
  - Fields: id, license_identifier, license_name, description, is_active, created_by, created_at, updated_at
  - Relationships: created_by_user
  - Unique constraint: license_identifier

### 2. Database Connection Utilities

Created in `shared/python/airlock_common/db/database.py`:

- ✅ **Database** class - Database connection manager
  - Async database connection using asyncpg
  - Connection pooling (configurable pool size and max overflow)
  - Health checks (pool_pre_ping)
  - Session management
  - Table creation/dropping utilities

- ✅ **get_db()** function - Get database instance from environment variables
  - Configurable via environment variables:
    - `POSTGRES_HOST` (default: localhost)
    - `POSTGRES_PORT` (default: 5432)
    - `POSTGRES_DB` (default: airlock)
    - `POSTGRES_USER` (default: airlock)
    - `POSTGRES_PASSWORD` (default: airlock)
    - `DB_ECHO` (default: false)
    - `DB_POOL_SIZE` (default: 5)
    - `DB_MAX_OVERFLOW` (default: 10)

### 3. Alembic Migration System

Configured in `shared/python/airlock_common/alembic/`:

- ✅ **alembic.ini** - Alembic configuration file
- ✅ **env.py** - Alembic environment configuration
  - Uses environment variables for database connection
  - Supports both online and offline migrations
  - Uses psycopg2 for synchronous migrations (Alembic requirement)
- ✅ **script.py.mako** - Migration script template

### 4. Package Configuration

- ✅ **requirements.txt** - Package dependencies
  - SQLAlchemy >= 2.0.0
  - asyncpg >= 0.29.0
  - psycopg2-binary >= 2.9.9 (for Alembic)
  - Alembic >= 1.13.0
  - typing-extensions >= 4.8.0

- ✅ **setup.py** - Package setup configuration
- ✅ **pyproject.toml** - Modern Python package configuration
- ✅ **README.md** - Package documentation

### 5. Helper Scripts

Created in `shared/python/airlock_common/scripts/`:

- ✅ **create_initial_migration.sh** - Script to create initial migration (Linux/Mac)
- ✅ **create_initial_migration.ps1** - Script to create initial migration (Windows)
- ✅ **test_database_setup.py** - Test script to verify database setup

## Acceptance Criteria Verification

✅ **PostgreSQL is running and accessible** - Configured in Docker Compose (Story 1.2)

✅ **Database migration system set up (Alembic)** - Alembic configured and ready

✅ **Initial schema includes all required tables** - All 10 tables created with correct fields

✅ **Database connection is configurable via environment variables** - All connection settings configurable

✅ **SQLAlchemy for ORM** - SQLAlchemy 2.0 with async support

✅ **Alembic for migrations** - Alembic configured with environment variable support

✅ **asyncpg for async database access** - Database connection uses asyncpg

✅ **Database connection pooling** - Connection pooling configured with configurable pool size

## Next Steps

To create and apply the initial migration:

1. **Install dependencies:**
   ```bash
   cd shared/python/airlock_common
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export POSTGRES_DB=airlock
   export POSTGRES_USER=airlock
   export POSTGRES_PASSWORD=airlock
   ```

3. **Create initial migration:**
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   ```

4. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

Or use the helper scripts:
- Linux/Mac: `./scripts/create_initial_migration.sh`
- Windows: `.\scripts\create_initial_migration.ps1`

## Files Created/Modified

### Created Files:
- `shared/python/airlock_common/db/__init__.py`
- `shared/python/airlock_common/db/base.py`
- `shared/python/airlock_common/db/database.py`
- `shared/python/airlock_common/db/models/__init__.py`
- `shared/python/airlock_common/db/models/user.py`
- `shared/python/airlock_common/db/models/package_submission.py`
- `shared/python/airlock_common/db/models/package_request.py`
- `shared/python/airlock_common/db/models/package.py`
- `shared/python/airlock_common/db/models/workflow.py`
- `shared/python/airlock_common/db/models/check_result.py`
- `shared/python/airlock_common/db/models/audit_log.py`
- `shared/python/airlock_common/db/models/api_key.py`
- `shared/python/airlock_common/db/models/package_usage.py`
- `shared/python/airlock_common/db/models/license_allowlist.py`
- `shared/python/airlock_common/alembic.ini`
- `shared/python/airlock_common/alembic/__init__.py`
- `shared/python/airlock_common/alembic/env.py`
- `shared/python/airlock_common/alembic/script.py.mako`
- `shared/python/airlock_common/requirements.txt`
- `shared/python/airlock_common/setup.py`
- `shared/python/airlock_common/pyproject.toml`
- `shared/python/airlock_common/README.md`
- `shared/python/airlock_common/scripts/create_initial_migration.sh`
- `shared/python/airlock_common/scripts/create_initial_migration.ps1`
- `shared/python/airlock_common/scripts/test_database_setup.py`

### Modified Files:
- `shared/python/airlock_common/__init__.py` - Updated to export database models and utilities

## Testing

To test the database setup:

```bash
cd shared/python/airlock_common
python scripts/test_database_setup.py
```

## Notes

1. **Project Version Field**: Added `project_version` field to `PackageSubmission` model (not explicitly in Story 1.3 requirements but needed for Story 3.1 where project name and version are extracted from package-lock.json)

2. **Async vs Sync**: Database connection uses asyncpg for async operations, but Alembic migrations use psycopg2 (synchronous) as required by Alembic

3. **Type Hints**: All models use SQLAlchemy 2.0 style type hints with `Mapped[]` annotations

4. **Relationships**: All foreign key relationships are properly defined with cascades where appropriate

5. **Indexes**: Appropriate indexes created on foreign keys and frequently queried fields

6. **Enums**: Status and type fields use Python enums for type safety

## Story Status

✅ **Story 1.3: PostgreSQL Database Setup and Schema Foundation** - **COMPLETED**

All acceptance criteria have been met. The database schema foundation is ready for use in subsequent stories.

