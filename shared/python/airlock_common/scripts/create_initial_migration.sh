#!/bin/bash
# Script to create initial database migration
# Usage: ./scripts/create_initial_migration.sh

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "Error: alembic is not installed. Please install it first:"
    echo "  pip install alembic"
    exit 1
fi

# Create initial migration
echo "Creating initial migration..."
alembic revision --autogenerate -m "Initial schema"

echo "Migration created successfully!"
echo "To apply the migration, run: alembic upgrade head"

