# Airlock Common

Shared Python utilities and models for the Airlock project.

## Installation

This package is installed as part of the Airlock project. To install it in development mode:

```bash
cd shared/python
pip install -e airlock_common
```

## Database Models

This package provides SQLAlchemy models for:

- `User` - User accounts and roles
- `PackageSubmission` - Package-lock.json submissions
- `PackageRequest` - Individual package requests from submissions
- `Package` - Fetched package data from NPM registry
- `Workflow` - Approval workflow state
- `CheckResult` - Automated check results (Trivy, license, etc.)
- `AuditLog` - Audit trail of all operations
- `APIKey` - API key management
- `PackageUsage` - Package usage tracking
- `LicenseAllowlist` - License allowlist for validation

## Database Migrations

Database migrations are managed using Alembic. To create a new migration:

```bash
cd shared/python/airlock_common
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

To rollback migrations:

```bash
alembic downgrade -1
```

## Database Connection

The database connection is configured via environment variables:

- `POSTGRES_HOST` - PostgreSQL host (default: localhost)
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `POSTGRES_DB` - Database name (default: airlock)
- `POSTGRES_USER` - Database user (default: airlock)
- `POSTGRES_PASSWORD` - Database password (default: airlock)
- `DB_ECHO` - Enable SQL query logging (default: false)
- `DB_POOL_SIZE` - Connection pool size (default: 5)
- `DB_MAX_OVERFLOW` - Maximum overflow connections (default: 10)

## Usage

```python
from airlock_common import get_db, User, PackageSubmission

# Get database instance
db = get_db()

# Use database session
async with db.get_session() as session:
    # Query users
    users = await session.execute(select(User))
    # ...
```

## Requirements

- Python >= 3.11
- PostgreSQL >= 16
- SQLAlchemy >= 2.0.0
- asyncpg >= 0.29.0
- Alembic >= 1.13.0

