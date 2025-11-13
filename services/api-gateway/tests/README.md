# API Gateway BDD Tests

BDD tests for the Nginx/OpenResty API Gateway using pytest-bdd.

## Test Structure

- `features/api_gateway.feature` - Gherkin feature file with test scenarios
- `features/steps/api_gateway_steps.py` - Step definitions
- `features/conftest.py` - Pytest configuration and fixtures

## Running Tests

### Prerequisites

1. **Docker services running**: The gateway and backend services must be running
2. **Environment variables**: Set JWT configuration

### Option 1: Run against Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d

# Wait for services to be ready
sleep 10

# Run tests
cd services/api-gateway
pip install -r requirements-test.txt
pytest tests/features/ -v
```

### Option 2: Run with test script

```bash
# From project root
cd services/api-gateway
./scripts/run_tests.sh
```

### Option 3: Run specific scenarios

```bash
# Run specific feature
pytest tests/features/api_gateway.feature -v

# Run specific scenario
pytest tests/features/api_gateway.feature::test_valid_token_is_accepted -v
```

## Environment Variables

Required for tests:
- `JWT_SECRET_KEY` - Must match gateway configuration
- `JWT_ALGORITHM` - Default: HS256
- `JWT_ISSUER` - Default: airlock-auth-service
- `GATEWAY_URL` - Default: http://localhost
- `API_GATEWAY_PORT` - Default: 80

## Test Scenarios

The tests cover:
- ✅ JWT token validation
- ✅ Request routing to services
- ✅ User context forwarding
- ✅ Rate limiting
- ✅ Admin role validation
- ✅ Health check endpoint
- ✅ Auth endpoints (no JWT required)

## Notes

- Tests make HTTP requests to the running gateway
- Tests assume backend services are running and accessible
- For full integration testing, all services should be running
- Tests verify gateway behavior, not backend service logic

