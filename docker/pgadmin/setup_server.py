#!/usr/bin/env python3
"""
Script to automatically add PostgreSQL server to pgAdmin
This runs after pgAdmin initializes to add the server to the database
"""
import os
import sys
import time
import sqlite3
from pathlib import Path

# Wait for pgAdmin to initialize
max_wait = 60
wait_count = 0
pgadmin_db = Path("/var/lib/pgadmin/pgadmin4.db")

while not pgadmin_db.exists() and wait_count < max_wait:
    time.sleep(1)
    wait_count += 1

if not pgadmin_db.exists():
    print(f"ERROR: pgAdmin database not found at {pgadmin_db} after {max_wait} seconds")
    sys.exit(1)

# Get configuration from environment
pgadmin_email = os.getenv("PGADMIN_DEFAULT_EMAIL", "admin@airlock.dev")
postgres_host = os.getenv("POSTGRES_HOST", "postgres")
postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
postgres_db = os.getenv("POSTGRES_DB", "airlock_dev")
postgres_user = os.getenv("POSTGRES_USER", "airlock_dev")
postgres_password = os.getenv("POSTGRES_PASSWORD", "dev_password_change_me")

# Wait for any user to be created (pgAdmin creates default user on first startup)
max_user_wait = 60  # Wait up to 1 minute for pgAdmin to initialize
user_wait_count = 0

try:
    conn = sqlite3.connect(str(pgadmin_db))
    cursor = conn.cursor()
    
    # Wait for any user to exist (pgAdmin creates a default user)
    user_result = None
    while not user_result and user_wait_count < max_user_wait:
        # Try to find the specified user first
        cursor.execute("SELECT id, email FROM user WHERE email = ?", (pgadmin_email,))
        user_result = cursor.fetchone()
        
        # If not found, get the first user (default pgAdmin user)
        if not user_result:
            cursor.execute("SELECT id, email FROM user ORDER BY id LIMIT 1")
            user_result = cursor.fetchone()
        
        if not user_result:
            time.sleep(2)
            user_wait_count += 2
            # Reconnect to get fresh data
            conn.close()
            conn = sqlite3.connect(str(pgadmin_db))
            cursor = conn.cursor()
    
    if not user_result:
        print(f"WARNING: No users found in pgAdmin database after {max_user_wait} seconds.")
        print("Please log in to pgAdmin first, then the server will be added automatically.")
        sys.exit(0)
    
    user_id, actual_email = user_result
    print(f"Found user: {actual_email} (ID: {user_id})")
    
    # If the user email doesn't match, try to find or create the desired user
    if actual_email != pgadmin_email:
        # Check if desired user exists
        cursor.execute("SELECT id FROM user WHERE email = ?", (pgadmin_email,))
        desired_user = cursor.fetchone()
        
        if desired_user:
            user_id = desired_user[0]
            print(f"Using user: {pgadmin_email} (ID: {user_id})")
        else:
            # Create the desired user (pgAdmin will create it on first login, but we can pre-create it)
            print(f"Note: User {pgadmin_email} doesn't exist yet. Server will be added for {actual_email}.")
            print(f"After logging in as {pgadmin_email}, the server will be available.")
    
    # Check if server already exists for this user
    cursor.execute(
        "SELECT id FROM server WHERE user_id = ? AND name = ?",
        (user_id, "Airlock PostgreSQL")
    )
    existing = cursor.fetchone()
    
    if existing:
        print(f"Server 'Airlock PostgreSQL' already exists for user ID {user_id}")
        sys.exit(0)
    
    # Get the next server ID
    cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM server WHERE user_id = ?", (user_id,))
    server_id = cursor.fetchone()[0]
    
    # Insert server configuration
    # pgAdmin stores SSL settings in connection_params as JSON
    import json
    connection_params = {
        "sslmode": "prefer"
    }
    
    # pgAdmin encrypts passwords, so we'll leave it empty and set save_password=0
    # This way pgAdmin will prompt for the password on first connection
    # The user can then save it if they want
    cursor.execute("""
        INSERT INTO server (id, user_id, servergroup_id, name, host, port, maintenance_db, 
                          username, password, comment, connection_params, save_password)
        VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        server_id,
        user_id,
        "Airlock PostgreSQL",
        postgres_host,
        postgres_port,
        postgres_db,
        postgres_user,
        "",  # Empty password - user will be prompted (pgAdmin encrypts passwords)
        "Airlock development database - Username: airlock_dev, Password: dev_password_change_me",
        json.dumps(connection_params)
    ))
    
    conn.commit()
    print(f"Successfully added server 'Airlock PostgreSQL' for user {pgadmin_email}")
    
except Exception as e:
    print(f"ERROR: Failed to add server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    conn.close()

