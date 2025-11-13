"""
Pytest configuration for API Gateway BDD tests
"""
import os
import sys
import time
from typing import Dict, Any
import requests
import pytest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "shared" / "python"))

# Set default environment variables for testing
os.environ.setdefault("JWT_SECRET_KEY", os.getenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only"))
os.environ.setdefault("JWT_ALGORITHM", os.getenv("JWT_ALGORITHM", "HS256"))
os.environ.setdefault("JWT_ISSUER", os.getenv("JWT_ISSUER", "airlock-auth-service"))

# Gateway configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost")
GATEWAY_PORT = os.getenv("API_GATEWAY_PORT", "80")
GATEWAY_BASE_URL = f"{GATEWAY_URL}:{GATEWAY_PORT}" if GATEWAY_PORT != "80" else GATEWAY_URL


@pytest.fixture(scope="session")
def gateway_url():
    """Get gateway URL"""
    return GATEWAY_BASE_URL


@pytest.fixture(scope="session")
def wait_for_gateway(gateway_url):
    """Wait for gateway to be ready"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{gateway_url}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    pytest.fail(f"Gateway not ready after {max_attempts} attempts")


@pytest.fixture
def context():
    """Test context for storing state between steps"""
    return {
        "token": None,
        "response": None,
        "request_count": 0,
        "responses": [],
    }


@pytest.fixture
def http_client(gateway_url, wait_for_gateway):
    """HTTP client for making requests to gateway"""
    return requests.Session()


