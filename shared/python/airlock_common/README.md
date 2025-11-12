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

## Utility Functions

This package provides utility functions for common operations:

### Logging

```python
from airlock_common import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO")

# Get logger
logger = get_logger(__name__)
logger.info("Hello, world!")
```

### Error Handling

```python
from airlock_common import (
    AirlockError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ServiceUnavailableError,
)

# Raise custom error
raise ValidationError("Invalid input", details={"field": "email"})
```

### Validation

```python
from airlock_common import validate_email, validate_url, validate_uuid

# Validate email
if validate_email(email):
    # Process email
    pass

# Validate URL
if validate_url(url):
    # Process URL
    pass

# Validate UUID
if validate_uuid(uuid_string):
    # Process UUID
    pass
```

### Configuration Helpers

```python
from airlock_common import get_env, get_env_int, get_env_bool, get_env_list

# Get environment variable
database_url = get_env("DATABASE_URL", default="localhost")

# Get environment variable as integer
port = get_env_int("PORT", default=8000)

# Get environment variable as boolean
debug = get_env_bool("DEBUG", default=False)

# Get environment variable as list
allowed_origins = get_env_list("ALLOWED_ORIGINS", default=["*"])
```

## Constants

This package provides constants for API endpoints, status codes, and error codes:

```python
from airlock_common import (
    API_VERSION,
    API_PREFIX,
    HEALTH_ENDPOINT,
    HTTP_STATUS_OK,
    HTTP_STATUS_NOT_FOUND,
    ERROR_CODE_VALIDATION_ERROR,
    ROLE_SUBMITTER,
    ROLE_REVIEWER,
    ROLE_ADMIN,
    ROLES,
)

# Use constants
health_url = f"{API_PREFIX}{HEALTH_ENDPOINT}"
if status_code == HTTP_STATUS_OK:
    # Process success
    pass
```

## Requirements

- Python >= 3.11
- PostgreSQL >= 16
- SQLAlchemy >= 2.0.0
- asyncpg >= 0.29.0
- Alembic >= 1.13.0

