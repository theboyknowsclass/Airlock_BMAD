"""
Pytest configuration for BDD tests
"""
import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# Set environment variables for testing
# Use Docker PostgreSQL database (same as development)
# When running tests from host, connect to localhost:5432 (exposed port)
# These can be overridden by .env.dev or environment variables
os.environ.setdefault("POSTGRES_HOST", os.getenv("POSTGRES_HOST", "localhost"))  # Use localhost for host machine
os.environ.setdefault("POSTGRES_PORT", os.getenv("POSTGRES_PORT", "5432"))
os.environ.setdefault("POSTGRES_DB", os.getenv("POSTGRES_DB", "airlock_dev"))
os.environ.setdefault("POSTGRES_USER", os.getenv("POSTGRES_USER", "airlock_dev"))
os.environ.setdefault("POSTGRES_PASSWORD", os.getenv("POSTGRES_PASSWORD", "dev_password_change_me"))
os.environ.setdefault("JWT_SECRET_KEY", os.getenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only"))
os.environ.setdefault("JWT_ALGORITHM", os.getenv("JWT_ALGORITHM", "HS256"))
os.environ.setdefault("JWT_ISSUER", os.getenv("JWT_ISSUER", "airlock-auth-service"))

