"""
OAuth2 client service for OAuth provider integration
"""
import secrets
import logging
from typing import Optional, Dict, Any
import httpx
from urllib.parse import urlencode, parse_qs, urlparse

from ..config import settings

logger = logging.getLogger(__name__)


class OAuth2Client:
    """OAuth2 client for OAuth providers (ADFS, Mock OAuth, etc.)"""
    
    def __init__(self):
        """Initialize OAuth2 client"""
        # OAuth2 provider URLs come from environment variables
        self.authorization_url = settings.OAUTH2_AUTHORIZATION_URL
        self.token_url = settings.OAUTH2_TOKEN_URL
        self.userinfo_url = settings.OAUTH2_USERINFO_URL
        self.issuer = settings.OAUTH2_ISSUER
        
        self.client_id = settings.OAUTH2_CLIENT_ID
        self.client_secret = settings.OAUTH2_CLIENT_SECRET
        self.redirect_uri = settings.OAUTH2_REDIRECT_URI
        
        # Validate required configuration
        if not self.authorization_url:
            raise ValueError("OAUTH2_AUTHORIZATION_URL environment variable is required")
        if not self.token_url:
            raise ValueError("OAUTH2_TOKEN_URL environment variable is required")
        if not self.userinfo_url:
            raise ValueError("OAUTH2_USERINFO_URL environment variable is required")
        if not self.client_id:
            raise ValueError("OAUTH2_CLIENT_ID environment variable is required")
        if not self.redirect_uri:
            raise ValueError("OAUTH2_REDIRECT_URI environment variable is required")
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """
        Get OAuth2 authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
        
        Returns:
            Tuple of (authorization_url, state_token)
        """
        if not state:
            state_token = secrets.token_urlsafe(32)
        else:
            state_token = state
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email",
            "state": state_token,
        }
        
        url = f"{self.authorization_url}?{urlencode(params)}"
        return url, state_token
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens
        
        Args:
            code: Authorization code
        
        Returns:
            Token response with access_token, refresh_token, etc.
        
        Raises:
            Exception: If token exchange fails
        """
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
            }
            
            # Add client_secret if provided
            if self.client_secret:
                data["client_secret"] = self.client_secret
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Token exchange failed: {e.response.text}")
                raise Exception(f"Token exchange failed: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Token exchange error: {e}")
                raise
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from OAuth provider
        
        Args:
            access_token: Access token from OAuth provider
        
        Returns:
            User information (sub, username, email, roles, etc.)
        
        Raises:
            Exception: If user info request fails
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            
            try:
                response = await client.get(
                    self.userinfo_url,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"User info request failed: {e.response.text}")
                raise Exception(f"User info request failed: {e.response.status_code}")
            except Exception as e:
                logger.error(f"User info request error: {e}")
                raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Token response with new access_token and refresh_token
        
        Raises:
            Exception: If token refresh fails
        """
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
            
            # Add client_secret if provided
            if self.client_secret:
                data["client_secret"] = self.client_secret
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Token refresh failed: {e.response.text}")
                raise Exception(f"Token refresh failed: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Token refresh error: {e}")
                raise


# Global OAuth2 client instance
oauth2_client = OAuth2Client()

