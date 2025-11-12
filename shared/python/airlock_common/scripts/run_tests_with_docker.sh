#!/bin/bash
# Script to run tests against Docker PostgreSQL
# Usage: ./scripts/run_tests_with_docker.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../../../../.." && pwd )"

echo "=========================================="
echo "Running Tests with Docker PostgreSQL"
echo "=========================================="
echo ""

# Check if .env.dev exists
if [ ! -f "$PROJECT_DIR/.env.dev" ]; then
    echo "Error: .env.dev file not found in project root"
    echo "Please create .env.dev with database configuration"
    exit 1
fi

# Load environment variables from .env.dev
set -a
source "$PROJECT_DIR/.env.dev"
set +a

# Set default values if not set
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_DB=${POSTGRES_DB:-airlock}
export POSTGRES_USER=${POSTGRES_USER:-airlock}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-airlock}

echo "Database Configuration:"
echo "  POSTGRES_HOST: $POSTGRES_HOST"
echo "  POSTGRES_PORT: $POSTGRES_PORT"
echo "  POSTGRES_DB: $POSTGRES_DB"
echo "  POSTGRES_USER: $POSTGRES_USER"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Start PostgreSQL in background
echo "Starting PostgreSQL..."
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
timeout=60
counter=0
while ! docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev exec -T postgres pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; do
    sleep 1
    counter=$((counter + 1))
    if [ $counter -ge $timeout ]; then
        echo "Error: PostgreSQL did not become ready within $timeout seconds"
        docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev logs postgres
        exit 1
    fi
done

echo "PostgreSQL is ready!"
echo ""

# Run tests
echo "Running tests..."
cd "$PROJECT_DIR/shared/python"
python -m pytest airlock_common/tests/ -v

# Capture exit code
TEST_EXIT_CODE=$?

# Stop PostgreSQL (optional - comment out to keep running)
echo ""
echo "Stopping PostgreSQL..."
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev stop postgres

# Exit with test exit code
exit $TEST_EXIT_CODE

