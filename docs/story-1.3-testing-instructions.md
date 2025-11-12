# Story 1.3: Testing Instructions

## ✅ What's Ready to Test

### 1. Model Tests (No Database Required) ✅

**Status**: Ready - All models can be tested without a database

**Tests Available**:
- Model imports - Verify all 10 models can be imported
- Model structure - Verify all models have correct columns
- Enum values - Verify all enum values are correct
- Model relationships - Verify all relationships are defined

**How to Run**:

**Option 1: Install Package and Run Tests**

```bash
# From project root
cd shared/python/airlock_common

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run simple test script (no pytest required)
python scripts/test_models_simple.py
```

**Option 2: Run with pytest (if installed)**

```bash
cd shared/python/airlock_common
pip install -r requirements.txt
pytest tests/test_models.py -v
```

**Option 3: Manual Python Test**

```bash
cd shared/python/airlock_common

# Install dependencies first
pip install sqlalchemy asyncpg psycopg2-binary

# Run Python test
python -c "
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from airlock_common.db.models import User, PackageSubmission
print('✓ Models imported successfully')
"
```

### 2. Database Connection Tests (Requires Database) ⚠️

**Status**: Ready, but requires PostgreSQL running

**How to Test Against Docker Database**:

#### Step 1: Create .env.dev File

Create `.env.dev` in project root:

```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=airlock
POSTGRES_USER=airlock
POSTGRES_PASSWORD=airlock
```

#### Step 2: Start PostgreSQL with Docker

**Option A: Using docker-compose.dev.yml (Exposes Port)**

```bash
# From project root
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres
```

**Option B: Manual Docker Command**

```bash
docker run -d \
  --name airlock-postgres \
  -e POSTGRES_DB=airlock \
  -e POSTGRES_USER=airlock \
  -e POSTGRES_PASSWORD=airlock \
  -p 5432:5432 \
  postgres:16-alpine
```

#### Step 3: Wait for PostgreSQL to be Ready

```bash
# Check if PostgreSQL is ready
docker exec airlock-postgres pg_isready -U airlock

# Or wait for health check
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev ps
```

#### Step 4: Set Environment Variables

**Linux/Mac**:
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=airlock
export POSTGRES_USER=airlock
export POSTGRES_PASSWORD=airlock
```

**Windows PowerShell**:
```powershell
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_DB = "airlock"
$env:POSTGRES_USER = "airlock"
$env:POSTGRES_PASSWORD = "airlock"
```

#### Step 5: Run Database Tests

```bash
cd shared/python/airlock_common

# Install dependencies
pip install -r requirements.txt

# Run database tests
python -m pytest tests/test_database_connection.py -v
```

#### Step 6: Stop PostgreSQL (Optional)

```bash
# Stop PostgreSQL
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev stop postgres

# Or if using manual Docker
docker stop airlock-postgres
docker rm airlock-postgres
```

## 🐳 Docker Database Testing Configuration

### docker-compose.dev.yml

The `docker-compose.dev.yml` file extends `docker-compose.prod.yml` to expose PostgreSQL port for testing and local development:

```yaml
services:
  postgres:
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
```

### Why Expose Port?

- **Testing from host**: Tests run on host machine, not in Docker
- **Local development**: Developers can connect from local machine
- **CI/CD**: Some CI systems need port exposure

### Connection Details

- **From Host Machine**: `localhost:5432` (exposed port)
- **From Docker Container**: `postgres:5432` (Docker network name)

## 📋 Test Scripts

### Linux/Mac: `scripts/run_tests_with_docker.sh`

This script:
1. Loads environment variables from `.env.dev`
2. Starts PostgreSQL container
3. Waits for PostgreSQL to be ready
4. Runs all tests
5. Stops PostgreSQL container

**Usage**:
```bash
cd shared/python/airlock_common
./scripts/run_tests_with_docker.sh
```

### Windows: `scripts/run_tests_with_docker.ps1`

Same functionality as Linux/Mac script, but for Windows PowerShell.

**Usage**:
```powershell
cd shared\python\airlock_common
.\scripts\run_tests_with_docker.ps1
```

## 🚀 Quick Start

### Test Models (No Database)

```bash
cd shared/python/airlock_common
pip install -r requirements.txt
python scripts/test_models_simple.py
```

### Test with Docker Database

```bash
# 1. Create .env.dev file in project root
# 2. Start PostgreSQL
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres

# 3. Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=airlock
export POSTGRES_USER=airlock
export POSTGRES_PASSWORD=airlock

# 4. Run tests
cd shared/python/airlock_common
pip install -r requirements.txt
python -m pytest tests/test_database_connection.py -v

# 5. Stop PostgreSQL
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev stop postgres
```

## ✅ Summary

### What Can Be Tested Now

1. **Model Tests** ✅
   - No database required
   - Can run immediately
   - Tests model structure, enums, relationships

2. **Database Connection Tests** ⚠️
   - Requires PostgreSQL running
   - Can test against Docker database
   - Tests connection, table creation, table structure

### What's Needed

1. **Dependencies**: Install `pip install -r requirements.txt`
2. **.env.dev file**: Create with database configuration
3. **PostgreSQL**: Start using Docker Compose
4. **Environment Variables**: Set for database connection

### Next Steps

1. ✅ Run model tests (no setup required)
2. ⚠️ Create .env.dev file
3. ⚠️ Start PostgreSQL with Docker
4. ⚠️ Run database tests
5. ⚠️ Create initial Alembic migration
6. ⚠️ Apply migration to create tables

## 📚 Documentation

- **Testing Guide**: `docs/story-1.3-testing-guide.md`
- **Docker Testing Guide**: `docs/story-1.3-docker-testing-guide.md`
- **Test Summary**: `docs/story-1.3-test-summary.md`
- **Implementation Summary**: `docs/story-1.3-implementation-summary.md`

