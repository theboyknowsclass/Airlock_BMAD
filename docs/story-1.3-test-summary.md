# Story 1.3: Test Summary

## ✅ What Can Be Tested Now

### 1. Model Tests (No Database Required) ✅

**Status**: ✅ Ready to run

**Tests Available**:
- Model imports - All 10 models can be imported
- Model structure - All models have correct columns
- Enum values - All enum values are correct
- Model relationships - All relationships are defined

**How to Run**:

**Option 1: Simple Test Script (No pytest required)**
```bash
cd shared/python/airlock_common
python scripts/test_models_simple.py
```

**Option 2: Python Import Test**
```bash
python -c "import sys; sys.path.insert(0, 'shared/python'); from airlock_common.db.models import User; print('✓ Model import successful')"
```

**Option 3: pytest (if installed)**
```bash
cd shared/python/airlock_common
pip install -r requirements.txt
pytest tests/test_models.py -v
```

### 2. Database Connection Tests (Requires Database) ⚠️

**Status**: ⚠️ Ready, but requires PostgreSQL running

**Tests Available**:
- Database connection - Connect to PostgreSQL
- Table creation - Create tables from models
- Table structure - Verify all tables exist
- Database URL generation - Generate database URLs

**How to Run**:

**Option 1: Using Docker (Recommended)**

1. **Create .env.dev file** in project root:
   ```bash
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=airlock
   POSTGRES_USER=airlock
   POSTGRES_PASSWORD=airlock
   ```

2. **Start PostgreSQL using Docker**:
   ```bash
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres
   ```

3. **Run tests**:
   ```bash
   cd shared/python/airlock_common
   python -m pytest tests/test_database_connection.py -v
   ```

**Option 2: Using Test Scripts**

**Linux/Mac**:
```bash
cd shared/python/airlock_common
./scripts/run_tests_with_docker.sh
```

**Windows**:
```powershell
cd shared\python\airlock_common
.\scripts\run_tests_with_docker.ps1
```

**Option 3: Manual Setup**

1. Start PostgreSQL:
   ```bash
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres
   ```

2. Set environment variables:
   ```bash
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export POSTGRES_DB=airlock
   export POSTGRES_USER=airlock
   export POSTGRES_PASSWORD=airlock
   ```

3. Run tests:
   ```bash
   cd shared/python/airlock_common
   python -m pytest tests/test_database_connection.py -v
   ```

## 🐳 Docker Database Testing

### Configuration

**docker-compose.dev.yml** extends `docker-compose.prod.yml` to expose PostgreSQL port for testing and local development:

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

- **From Host**: `localhost:5432` (exposed port)
- **From Docker**: `postgres:5432` (Docker network)

### Test Scripts

**Linux/Mac**: `scripts/run_tests_with_docker.sh`
- Starts PostgreSQL
- Waits for readiness
- Runs tests
- Stops PostgreSQL

**Windows**: `scripts/run_tests_with_docker.ps1`
- Same functionality as Linux/Mac script
- PowerShell compatible

## 📋 Test Coverage

### Model Tests (`test_models.py`)

- ✅ User model structure
- ✅ PackageSubmission model structure
- ✅ PackageRequest model structure
- ✅ Package model structure
- ✅ Workflow model structure
- ✅ CheckResult model structure
- ✅ AuditLog model structure
- ✅ APIKey model structure
- ✅ PackageUsage model structure
- ✅ LicenseAllowlist model structure
- ✅ Enum values
- ✅ Model relationships

### Database Connection Tests (`test_database_connection.py`)

- ⚠️ Database connection (requires database)
- ⚠️ Table creation (requires database)
- ⚠️ Table structure verification (requires database)
- ✅ Database URL generation (no database required)
- ✅ Database URL defaults (no database required)

## 🚀 Quick Start

### 1. Test Models (No Database)

```bash
cd shared/python/airlock_common
python scripts/test_models_simple.py
```

### 2. Test with Docker Database

**Step 1: Create .env.dev** (if not exists)
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=airlock
POSTGRES_USER=airlock
POSTGRES_PASSWORD=airlock
```

**Step 2: Start PostgreSQL**
```bash
# From project root
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres
```

**Step 3: Run tests**
```bash
cd shared/python/airlock_common
pip install -r requirements.txt
python -m pytest tests/ -v
```

**Or use test script**:
```bash
# Linux/Mac
cd shared/python/airlock_common
./scripts/run_tests_with_docker.sh

# Windows
cd shared\python\airlock_common
.\scripts\run_tests_with_docker.ps1
```

## 📝 Next Steps

1. **Run model tests** - Verify models are correct (no database required) ✅
2. **Create .env.dev** - Set up database configuration
3. **Start PostgreSQL** - Using Docker Compose
4. **Run database tests** - Test database connection and table creation
5. **Create migration** - Generate initial Alembic migration
6. **Apply migration** - Create tables in database

## 🔧 Troubleshooting

### Model Tests Not Running

**Issue**: Module not found
**Solution**: Ensure you're in the correct directory or set Python path:
```bash
python -c "import sys; sys.path.insert(0, 'shared/python'); from airlock_common.db.models import User"
```

### Database Tests Not Running

**Issue**: Connection refused
**Solution**: 
1. Ensure PostgreSQL is running: `docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev ps`
2. Check port is exposed: Verify `docker-compose.dev.yml` has port mapping
3. Check environment variables: Verify `.env.dev` has correct values

### PostgreSQL Not Starting

**Issue**: Container won't start
**Solution**:
1. Check logs: `docker-compose logs postgres`
2. Check port conflicts: Ensure port 5432 is not in use
3. Check environment variables: Verify `.env.dev` file exists

## 📚 Documentation

- **Testing Guide**: `docs/story-1.3-testing-guide.md`
- **Docker Testing Guide**: `docs/story-1.3-docker-testing-guide.md`
- **Implementation Summary**: `docs/story-1.3-implementation-summary.md`

## ✅ Summary

**What's Ready**:
- ✅ Model tests (no database required)
- ✅ Database connection utilities
- ✅ Docker test configuration
- ✅ Test scripts (Linux/Mac/Windows)
- ✅ Documentation

**What's Needed**:
- ⚠️ .env.dev file (for database configuration)
- ⚠️ PostgreSQL running (for database tests)
- ⚠️ pytest installed (optional, for pytest-based tests)

**Next Actions**:
1. Run model tests (no setup required) ✅
2. Create .env.dev file
3. Start PostgreSQL with Docker
4. Run database tests
5. Create and apply initial migration

