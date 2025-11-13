#!/bin/bash
# Script to run API Gateway BDD tests
# Usage: ./scripts/run_tests.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../../.." && pwd )"

echo "=========================================="
echo "Running API Gateway BDD Tests"
echo "=========================================="
echo ""

# Check if .env.dev exists
if [ ! -f "$PROJECT_DIR/.env.dev" ]; then
    echo "Warning: .env.dev file not found in project root"
    echo "Using default test configuration"
fi

# Load environment variables from .env.dev if it exists
if [ -f "$PROJECT_DIR/.env.dev" ]; then
    set -a
    source "$PROJECT_DIR/.env.dev"
    set +a
fi

# Set default values
export GATEWAY_URL=${GATEWAY_URL:-http://localhost}
export API_GATEWAY_PORT=${API_GATEWAY_PORT:-80}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-test-secret-key-for-testing-only}
export JWT_ALGORITHM=${JWT_ALGORITHM:-HS256}
export JWT_ISSUER=${JWT_ISSUER:-airlock-auth-service}

echo "Test Configuration:"
echo "  GATEWAY_URL: $GATEWAY_URL"
echo "  API_GATEWAY_PORT: $API_GATEWAY_PORT"
echo "  JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:10}..."
echo "  JWT_ALGORITHM: $JWT_ALGORITHM"
echo "  JWT_ISSUER: $JWT_ISSUER"
echo ""

# Change to API Gateway directory
cd "$SCRIPT_DIR/.."

# Check if gateway is accessible
echo "Checking gateway health..."
GATEWAY_BASE_URL="$GATEWAY_URL"
if [ "$API_GATEWAY_PORT" != "80" ]; then
    GATEWAY_BASE_URL="$GATEWAY_URL:$API_GATEWAY_PORT"
fi

max_attempts=30
for attempt in $(seq 1 $max_attempts); do
    if curl -f -s "$GATEWAY_BASE_URL/health" > /dev/null 2>&1; then
        echo "Gateway is ready!"
        break
    fi
    if [ $attempt -eq $max_attempts ]; then
        echo "Error: Gateway not accessible at $GATEWAY_BASE_URL"
        echo "Please ensure the gateway is running:"
        echo "  docker-compose up api-gateway"
        exit 1
    fi
    echo "Waiting for gateway... ($attempt/$max_attempts)"
    sleep 1
done

echo ""

# Install test dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing test dependencies..."
pip install -q -r requirements-test.txt

# Install shared library
echo "Installing shared library..."
cd "$PROJECT_DIR/shared/python/airlock_common"
pip install -q -e .

# Return to API Gateway directory
cd "$SCRIPT_DIR/.."

# Run tests
echo ""
echo "Running BDD tests..."
echo ""
pytest tests/features/ -v --tb=short

echo ""
echo "Tests completed!"

