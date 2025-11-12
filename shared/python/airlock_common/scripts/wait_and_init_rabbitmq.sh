#!/bin/bash
# RabbitMQ initialization script
# Waits for RabbitMQ to be ready, then configures exchanges and queues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Add shared directory to Python path
export PYTHONPATH="$SHARED_DIR:$PYTHONPATH"

# Run initialization script
python3 "$SCRIPT_DIR/init_rabbitmq.py"

