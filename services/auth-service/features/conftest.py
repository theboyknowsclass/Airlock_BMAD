"""
Pytest configuration for BDD tests
"""
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# Set minimal environment variables for OAuth2Client initialization in tests
os.environ.setdefault("OAUTH2_AUTHORIZATION_URL", "http://mock-oauth.example.com/authorize")
os.environ.setdefault("OAUTH2_TOKEN_URL", "http://mock-oauth.example.com/token")
os.environ.setdefault("OAUTH2_USERINFO_URL", "http://mock-oauth.example.com/userinfo")
os.environ.setdefault("OAUTH2_CLIENT_ID", "test-client")
os.environ.setdefault("OAUTH2_REDIRECT_URI", "http://localhost:8001/api/v1/auth/callback")
os.environ.setdefault("FRONTEND_CALLBACK_URI", "http://localhost:3000/auth/callback")

