# Story 1.3: Docker Database Testing Guide

## Overview

This guide explains how to run database tests against the Docker PostgreSQL container.

## Prerequisites

1. **Docker and Docker Compose** - Installed and running
2. **.env.dev file** - Created in project root with database configuration
3. **Python dependencies** - Installed (see below)

## Setup

### 1. Create .env.dev File

Create a `.env.dev` file in the project root with the following variables:

```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=airlock
POSTGRES_USER=airlock
POSTGRES_PASSWORD=airlock

# Other environment variables (add as needed)
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=airlock
RABBITMQ_PASSWORD=airlock
# ... etc
```

### 2. Install Python Dependencies

```bash
cd shared/python/airlock_common
pip install -r requirements.txt
```

### 3. Verify Docker Compose Configuration

The `docker-compose.dev.yml` file extends `docker-compose.prod.yml` to expose PostgreSQL port for testing and local development.

## Running Tests

### Option 1: Using Test Scripts (Recommended)

#### Linux/Mac

```bash
cd shared/python/airlock_common
./scripts/run_tests_with_docker.sh
```

#### Windows

```powershell
cd shared\python\airlock_common
.\scripts\run_tests_with_docker.ps1
```

These scripts will:
1. Load environment variables from `.env.dev`
2. Start PostgreSQL container
3. Wait for PostgreSQL to be ready
4. Run all tests
5. Stop PostgreSQL container (optional)

### Option 2: Manual Testing

#### Step 1: Start PostgreSQL

```bash
# From project root
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres
```

#### Step 2: Wait for PostgreSQL to be Ready

```bash
# Check if PostgreSQL is ready
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev exec postgres pg_isready -U airlock
```

#### Step 3: Set Environment Variables

```bash
# Linux/Mac
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=airlock
export POSTGRES_USER=airlock
export POSTGRES_PASSWORD=airlock

# Windows PowerShell
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_DB = "airlock"
$env:POSTGRES_USER = "airlock"
$env:POSTGRES_PASSWORD = "airlock"
```

#### Step 4: Run Tests

```bash
cd shared/python/airlock_common
python -m pytest tests/ -v
```

Or use the simple test script (no pytest required):

```bash
python scripts/test_models_simple.py
```

#### Step 5: Stop PostgreSQL (Optional)

```bash
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev stop postgres
```

## Test Categories

### Model Tests (No Database Required)

These tests verify model structure and can run without a database:

```bash
cd shared/python/airlock_common
python scripts/test_models_simple.py
```

Or with pytest:

```bash
python -m pytest tests/test_models.py -v
```

### Database Connection Tests (Requires Database)

These tests require PostgreSQL to be running:

```bash
# Start PostgreSQL first
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres

# Run database tests
python -m pytest tests/test_database_connection.py -v
```

## Docker Configuration

### docker-compose.dev.yml

The `docker-compose.dev.yml` file extends `docker-compose.prod.yml` to expose PostgreSQL port for testing and local development:

```yaml
services:
  postgres:
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
```

### Why Expose Port?

- **Testing from host**: Tests run on the host machine, not in Docker
- **Local development**: Developers can connect to database from their local machine
- **CI/CD**: Some CI systems need port exposure for testing

### Network Configuration

PostgreSQL is on the `airlock-network` Docker network, but we also expose port 5432 so:
- **Inside Docker**: Services connect via `postgres:5432` (Docker network)
- **From Host**: Tests connect via `localhost:5432` (exposed port)

## Environment Variables

### Required Variables

- `POSTGRES_HOST` - Database host (use `localhost` for testing from host)
- `POSTGRES_PORT` - Database port (default: `5432`)
- `POSTGRES_DB` - Database name (default: `airlock`)
- `POSTGRES_USER` - Database user (default: `airlock`)
- `POSTGRES_PASSWORD` - Database password (default: `airlock`)

### Connection from Host vs Docker

- **From Host Machine**: Use `POSTGRES_HOST=localhost`
- **From Docker Container**: Use `POSTGRES_HOST=postgres` (Docker service name)

## Troubleshooting

### PostgreSQL Not Ready

If PostgreSQL doesn't become ready:

```bash
# Check logs
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev logs postgres

# Check if container is running
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev ps

# Restart PostgreSQL
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev restart postgres
```

### Connection Refused

If you get "connection refused" errors:

1. **Check if port is exposed**: Verify `docker-compose.dev.yml` has port mapping
2. **Check if PostgreSQL is running**: `docker-compose ps`
3. **Check firewall**: Ensure port 5432 is not blocked
4. **Check environment variables**: Verify `POSTGRES_HOST` and `POSTGRES_PORT` are correct

### Port Already in Use

If port 5432 is already in use:

1. **Change port in .env.dev**: Set `POSTGRES_PORT=5433` (or another port)
2. **Update docker-compose.dev.yml**: Change port mapping to match (or use environment variable)
3. **Update tests**: Ensure tests use the correct port

### Tests Timeout

If tests timeout waiting for PostgreSQL:

1. **Increase timeout**: Edit test scripts to increase wait time
2. **Check PostgreSQL logs**: Look for startup errors
3. **Check resources**: Ensure Docker has enough resources allocated

## Best Practices

### 1. Use Test Scripts

Use the provided test scripts instead of manual setup:
- Automatic environment variable loading
- Automatic PostgreSQL startup/shutdown
- Better error handling

### 2. Keep Database Clean

Tests should clean up after themselves:
- Drop tables after tests
- Use transaction rollback
- Use test database (separate from development)

### 3. Use Environment Variables

Don't hardcode database credentials:
- Use `.env.dev` for development
- Use environment variables in CI/CD
- Never commit secrets to version control

### 4. Test Isolation

Ensure tests don't interfere with each other:
- Use transactions that rollback
- Use unique test data
- Clean up after each test

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Database Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: airlock
          POSTGRES_USER: airlock
          POSTGRES_PASSWORD: airlock
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd shared/python/airlock_common
          pip install -r requirements.txt
      
      - name: Run tests
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
          POSTGRES_DB: airlock
          POSTGRES_USER: airlock
          POSTGRES_PASSWORD: airlock
        run: |
          cd shared/python/airlock_common
          python -m pytest tests/ -v
```

## Summary

### Quick Start

1. **Create .env.dev** with database configuration
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run test script**: `./scripts/run_tests_with_docker.sh` (Linux/Mac) or `.\scripts\run_tests_with_docker.ps1` (Windows)

### Test Without Database

```bash
python scripts/test_models_simple.py
```

### Test With Database

```bash
# Start PostgreSQL
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres

# Run tests
python -m pytest tests/ -v

# Stop PostgreSQL
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev stop postgres
```

## Next Steps

1. **Create .env.dev** file with database configuration
2. **Run model tests** (no database required)
3. **Start PostgreSQL** using Docker Compose
4. **Run database tests** against Docker PostgreSQL
5. **Create initial migration** using Alembic
6. **Apply migration** to create tables

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)

