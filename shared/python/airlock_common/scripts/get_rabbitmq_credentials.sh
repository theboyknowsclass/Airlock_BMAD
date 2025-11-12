#!/bin/bash
# Get RabbitMQ credentials from .env.dev file
# This script reads .env.dev and extracts RABBITMQ_USER and RABBITMQ_PASSWORD

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env.dev"

if [ ! -f "$ENV_FILE" ]; then
    echo "[ERROR] .env.dev file not found at: $ENV_FILE"
    echo "  Please create .env.dev file with RabbitMQ credentials"
    exit 1
fi

echo "Reading credentials from .env.dev..."
echo "  File: $ENV_FILE"
echo ""

# Read .env.dev file and extract credentials
RABBITMQ_USER=$(grep -E "^\s*RABBITMQ_USER\s*=" "$ENV_FILE" | sed 's/^[^=]*=\s*//' | tr -d '"' | tr -d "'" | xargs)
RABBITMQ_PASSWORD=$(grep -E "^\s*RABBITMQ_PASSWORD\s*=" "$ENV_FILE" | sed 's/^[^=]*=\s*//' | tr -d '"' | tr -d "'" | xargs)

if [ -n "$RABBITMQ_USER" ] && [ -n "$RABBITMQ_PASSWORD" ]; then
    echo "[OK] Found RabbitMQ credentials in .env.dev:"
    echo "  RABBITMQ_USER = $RABBITMQ_USER"
    echo "  RABBITMQ_PASSWORD = ***"
    echo ""
    echo "To use these credentials, run:"
    echo "  export RABBITMQ_USER=\"$RABBITMQ_USER\""
    echo "  export RABBITMQ_PASSWORD=\"$RABBITMQ_PASSWORD\""
    echo ""
    echo "Or set them automatically:"
    echo "  source <(./scripts/get_rabbitmq_credentials.sh)"
else
    echo "[WARN] RABBITMQ_USER or RABBITMQ_PASSWORD not found in .env.dev"
    echo "  Using defaults: guest/guest"
    echo ""
    echo "To set credentials, add to .env.dev:"
    echo "  RABBITMQ_USER=airlock"
    echo "  RABBITMQ_PASSWORD=airlock"
fi

# Output export commands to set environment variables
if [ -n "$RABBITMQ_USER" ] && [ -n "$RABBITMQ_PASSWORD" ]; then
    echo ""
    echo "# Set environment variables:"
    echo "export RABBITMQ_USER=\"$RABBITMQ_USER\""
    echo "export RABBITMQ_PASSWORD=\"$RABBITMQ_PASSWORD\""
fi

