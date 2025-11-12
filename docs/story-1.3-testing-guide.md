# Story 1.3: Testing Guide

## What Can Be Tested Now

### ✅ Tests That Don't Require a Database

These tests can be run immediately without any setup:

1. **Model Imports** - Verify all models can be imported
2. **Model Structure** - Verify models have correct columns and relationships
3. **Enum Values** - Verify enum values are correct
4. **Database URL Generation** - Verify database URL is generated correctly

### ⚠️ Tests That Require a Database

These tests require PostgreSQL to be running:

1. **Database Connection** - Test that we can connect to PostgreSQL
2. **Table Creation** - Test that tables can be created from models
3. **Table Structure** - Verify that all expected tables exist
4. **Migration Generation** - Generate initial Alembic migration

## Running Tests

### Option 1: Run Test Script (Recommended)

The test script can be run without any database setup:

```bash
cd shared/python/airlock_common
python scripts/test_database_setup.py
```

This will:
- ✅ Test model imports (no database required)
- ✅ Test model structure (no database required)
- ✅ Test database URL generation (no database required)
- ⚠️ Test database connection (skipped if database not available)

### Option 2: Run Pytest Tests

#### Install Dependencies

```bash
cd shared/python/airlock_common
pip install -r requirements.txt
```

#### Run Model Tests (No Database Required)

```bash
pytest tests/test_models.py -v
```

#### Run Database Connection Tests (Requires Database)

```bash
# Start PostgreSQL first
docker-compose up postgres

# Set environment variables (or use defaults)
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=airlock
export POSTGRES_USER=airlock
export POSTGRES_PASSWORD=airlock

# Run database tests
pytest tests/test_database_connection.py -v
```

#### Run All Tests

```bash
pytest tests/ -v
```

## What's Missing for Full Testing

To fully test Story 1.3, you need:

1. **PostgreSQL Running** - Start PostgreSQL via Docker Compose:
   ```bash
   docker-compose up postgres
   ```

2. **Initial Migration** - Create the initial Alembic migration:
   ```bash
   cd shared/python/airlock_common
   alembic revision --autogenerate -m "Initial schema"
   ```

3. **Apply Migration** - Apply the migration to create tables:
   ```bash
   alembic upgrade head
   ```

4. **Environment Variables** - Set database connection variables (or use defaults)

## Current Test Coverage

### ✅ Model Tests (`test_models.py`)

- [x] User model structure
- [x] PackageSubmission model structure
- [x] PackageRequest model structure
- [x] Package model structure
- [x] Workflow model structure
- [x] CheckResult model structure
- [x] AuditLog model structure
- [x] APIKey model structure
- [x] PackageUsage model structure
- [x] LicenseAllowlist model structure
- [x] Enum values
- [x] Model relationships

### ⚠️ Database Connection Tests (`test_database_connection.py`)

- [ ] Database connection (requires database)
- [ ] Table creation (requires database)
- [ ] Database URL generation (works without database)
- [ ] Database URL defaults (works without database)

## Recommended Testing Workflow

### Step 1: Test Models (No Database Required)

```bash
cd shared/python/airlock_common
python scripts/test_database_setup.py
```

This will test:
- ✅ Model imports
- ✅ Model structure
- ✅ Database URL generation

### Step 2: Start PostgreSQL

```bash
# From project root
docker-compose up postgres
```

### Step 3: Test Database Connection

```bash
cd shared/python/airlock_common
python scripts/test_database_setup.py
```

This will now also test:
- ✅ Database connection
- ✅ Table creation
- ✅ Table structure

### Step 4: Create Initial Migration

```bash
cd shared/python/airlock_common
alembic revision --autogenerate -m "Initial schema"
```

### Step 5: Apply Migration

```bash
alembic upgrade head
```

### Step 6: Verify Migration

```bash
# Check that tables were created
pytest tests/test_database_connection.py -v
```

## Test Results

### Without Database

When running tests without a database, you should see:

```
============================================================
Database Setup Test
============================================================

Testing model imports...
  ✓ User (users)
  ✓ PackageSubmission (package_submissions)
  ✓ PackageRequest (package_requests)
  ✓ Package (packages)
  ✓ Workflow (workflows)
  ✓ CheckResult (check_results)
  ✓ AuditLog (audit_logs)
  ✓ APIKey (api_keys)
  ✓ PackageUsage (package_usage)
  ✓ LicenseAllowlist (license_allowlist)
✓ All models imported successfully

Testing model structure...
  ✓ User model structure correct
  ✓ PackageSubmission model structure correct
  ✓ All expected tables have models

Testing database URL generation...
  ✓ Database URL: postgresql+asyncpg://airlock:****@localhost:5432/airlock

Testing database connection...
  ⚠ Missing environment variables: ...
  ⚠ Using defaults (localhost:5432/airlock)
  ⚠ Database connection test skipped - start PostgreSQL to test

============================================================
✓ Model tests passed!
⚠ Database connection test skipped (database not available)
============================================================
```

### With Database

When running tests with a database, you should see:

```
============================================================
Database Setup Test
============================================================

Testing model imports...
  ✓ User (users)
  ✓ PackageSubmission (package_submissions)
  ... (all models)

Testing model structure...
  ✓ User model structure correct
  ✓ PackageSubmission model structure correct
  ✓ All expected tables have models

Testing database URL generation...
  ✓ Database URL: postgresql+asyncpg://airlock:****@localhost:5432/airlock

Testing database connection...
  ✓ Database connection created
  ✓ Database connection successful
  Testing table creation...
  ✓ Tables created successfully
    ✓ Table users exists
    ✓ Table package_submissions exists
    ✓ Table package_requests exists
    ✓ Table packages exists
    ✓ Table workflows exists
    ✓ Table check_results exists
    ✓ Table audit_logs exists
    ✓ Table api_keys exists
    ✓ Table package_usage exists
    ✓ Table license_allowlist exists
  ✓ Tables dropped successfully

============================================================
✓ All tests passed!
============================================================
```

## Next Steps

1. **Run model tests** - Verify models are correct (no database required)
2. **Start PostgreSQL** - If you want to test database connection
3. **Create migration** - Generate initial Alembic migration
4. **Apply migration** - Create tables in database
5. **Verify tables** - Confirm all tables were created correctly

## Conclusion

**You can test the models now without a database!** The model tests verify:
- All models can be imported
- Models have correct structure
- Models have correct relationships
- Enum values are correct

**To test database connection**, you need:
- PostgreSQL running (via Docker Compose)
- Environment variables set (or use defaults)
- Run the test script again

The test suite is designed to work both with and without a database, so you can verify the models are correct before setting up the database.

