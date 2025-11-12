# Tests for airlock_common

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio
   ```

2. (Optional) Start PostgreSQL for database tests:
   ```bash
   docker-compose up postgres
   ```

### Running All Tests

```bash
pytest
```

### Running Specific Tests

```bash
# Test models only (no database required)
pytest tests/test_models.py

# Test database connection (requires database)
pytest tests/test_database_connection.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=airlock_common --cov-report=html
```

### Running Test Script

The test script can be run directly:

```bash
python scripts/test_database_setup.py
```

This script:
- Tests model imports (no database required)
- Tests model structure (no database required)
- Tests database URL generation (no database required)
- Tests database connection (requires database)
- Tests table creation (requires database)

## Test Categories

### Model Tests (`test_models.py`)

These tests don't require a database connection and test:
- Model structure (columns, relationships)
- Enum values
- Model relationships

### Database Connection Tests (`test_database_connection.py`)

These tests require a database connection and test:
- Database connection
- Table creation
- Database URL generation

## Environment Variables

For database tests, set these environment variables (or use defaults):

- `POSTGRES_HOST` (default: localhost)
- `POSTGRES_PORT` (default: 5432)
- `POSTGRES_DB` (default: airlock)
- `POSTGRES_USER` (default: airlock)
- `POSTGRES_PASSWORD` (default: airlock)

## Continuous Integration

Tests are designed to work in CI environments:
- Model tests always run (no database required)
- Database tests are skipped if database is not available
- Tests use pytest markers to categorize tests

