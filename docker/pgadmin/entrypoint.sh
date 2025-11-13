#!/bin/bash

# pgAdmin entrypoint script to auto-configure PostgreSQL server
# This ensures the server is available for all users

set -e

# Function to setup server via Python script
setup_server() {
    # Wait a bit for pgAdmin to start
    sleep 10
    
    # Run Python script to add server to database (will wait for user to be created)
    if [ -f /setup_server.py ]; then
        echo "Running server setup script (will wait for user to log in)..."
        python3 /setup_server.py &
    else
        echo "WARNING: Server setup script not found at /setup_server.py"
    fi
}

# Start setup in background (non-blocking)
setup_server &

# Call the original pgAdmin entrypoint
exec /entrypoint.sh "$@"

