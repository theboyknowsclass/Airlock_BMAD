# Testing Strategy

## Overview

This project uses two types of testing tools:

1. **Test Scripts** (`scripts/`) - Manual testing, diagnostics, setup verification
2. **Pytest Tests** (`tests/`) - Automated testing, CI/CD, structured assertions

## Test Scripts vs Pytest Tests

### Test Scripts (`scripts/`)

**Purpose:**
- Quick manual testing and diagnostics
- User-friendly output (print statements)
- Setup verification
- Can run without pytest
- Good for troubleshooting

**Files:**
- `test_models_simple.py` - Simple model testing (imports, basic structure)
- `test_database_setup.py` - Comprehensive database setup verification
- `test_rabbitmq_setup.py` - RabbitMQ setup verification (imports, connection, env vars)

**Usage:**
```bash
# Run directly (no pytest required)
python scripts/test_models_simple.py
python scripts/test_database_setup.py
python scripts/test_rabbitmq_setup.py
```

### Pytest Tests (`tests/`)

**Purpose:**
- Automated testing
- CI/CD integration
- Structured assertions
- Test coverage reporting
- Good for regression testing

**Files:**
- `test_models.py` - Comprehensive model testing (all models, relationships, enums)
- `test_database_connection.py` - Database connection and table creation tests
- `test_rabbitmq_connection.py` - RabbitMQ connection and URL generation tests
- `test_rabbitmq_init.py` - RabbitMQ initialization tests (exchanges, queues)

**Usage:**
```bash
# Run with pytest
pytest tests/test_models.py
pytest tests/test_database_connection.py
pytest tests/test_rabbitmq_connection.py -v -k "not integration"
pytest tests/test_rabbitmq_init.py -v -m integration
```

## Redundancy Analysis

### Models Testing

**Scripts:**
- `test_models_simple.py` - Tests 2 models (User, PackageSubmission), basic structure

**Tests:**
- `test_models.py` - Tests all 10 models, comprehensive structure, relationships, enums

**Recommendation:** Keep both. Script is for quick verification, pytest is for comprehensive testing.

### Database Testing

**Scripts:**
- `test_database_setup.py` - Tests models, database connection, table creation (comprehensive)

**Tests:**
- `test_database_connection.py` - Tests database connection, table creation (focused)

**Recommendation:** Keep both. Script is for setup verification, pytest is for automated testing.

### RabbitMQ Testing

**Scripts:**
- `test_rabbitmq_setup.py` - Tests imports, pika installation, env vars, connection (comprehensive)

**Tests:**
- `test_rabbitmq_connection.py` - Tests URL generation, connection, context manager (focused)
- `test_rabbitmq_init.py` - Tests RabbitMQ initialization (exchanges, queues)

**Recommendation:** Keep all. Script is for setup verification, pytest tests are for automated testing.

## When to Use Which

### Use Test Scripts When:
- Setting up the project for the first time
- Troubleshooting connection issues
- Verifying setup after changes
- Quick manual testing
- Don't have pytest installed

### Use Pytest Tests When:
- Running automated tests
- CI/CD pipelines
- Regression testing
- Test coverage reporting
- Need structured assertions

## Consolidation Opportunities

### Potential Redundancy

1. **`test_models_simple.py`** - Redundant with `test_models.py`
   - **Action:** Consider removing `test_models_simple.py` since `test_models.py` is more comprehensive
   - **Alternative:** Keep it as a lightweight script for quick verification

2. **`test_database_setup.py`** - Partially redundant with `test_database_connection.py`
   - **Action:** Keep both (script is more comprehensive, includes model testing)
   - **Note:** Script tests models + database, pytest tests focus on database only

3. **`test_rabbitmq_setup.py`** - Partially redundant with `test_rabbitmq_connection.py`
   - **Action:** Keep both (script is for setup verification, pytest is for automated testing)
   - **Note:** Script tests setup (imports, env vars), pytest tests functionality

## Recommendations

### Keep All Scripts For Now

**Reasons:**
1. Scripts serve a different purpose (manual testing, diagnostics)
2. User-friendly output (print statements)
3. Can run without pytest
4. Useful for troubleshooting
5. Quick verification during development

### Future Consolidation

**Consider:**
1. Removing `test_models_simple.py` if `test_models.py` covers all use cases
2. Keeping `test_database_setup.py` as it's comprehensive
3. Keeping `test_rabbitmq_setup.py` as it's useful for diagnostics
4. Adding documentation to clarify when to use which

## Test Coverage

### Models
- ✅ Script: Basic structure (2 models)
- ✅ Pytest: Comprehensive (10 models, relationships, enums)

### Database
- ✅ Script: Models + connection + tables
- ✅ Pytest: Connection + tables

### RabbitMQ
- ✅ Script: Setup verification (imports, env vars, connection)
- ✅ Pytest: Functionality (URL generation, connection, initialization)

## Running Tests

### Quick Verification (Scripts)
```bash
# Models
python scripts/test_models_simple.py

# Database
python scripts/test_database_setup.py

# RabbitMQ
python scripts/test_rabbitmq_setup.py
```

### Automated Testing (Pytest)
```bash
# All tests
pytest

# Models only
pytest tests/test_models.py

# Database only
pytest tests/test_database_connection.py

# RabbitMQ only (unit tests)
pytest tests/test_rabbitmq_connection.py -v -k "not integration"

# RabbitMQ only (integration tests)
pytest tests/test_rabbitmq_connection.py -v -m integration
pytest tests/test_rabbitmq_init.py -v -m integration
```

