"""
Authentication router
OAuth2 integration with ADFS and token issuance
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

from ..services.oauth2 import oauth2_client
from ..utils.jwt import create_access_token, create_refresh_token, decode_token
from ..config import settings
from ..dependencies import get_current_user, UserContext


class UnauthorizedError(Exception):
    """Unauthorized error"""
    pass

logger = logging.getLogger(__name__)
router = APIRouter()


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: str
    scope: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response model"""
    authorization_url: str
    state: str


@router.get("/login")
async def login(
    username: Optional[str] = Query(None, description="Username parameter (for mock OAuth providers)"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
):
    """
    Initiate OAuth2 login flow
    Redirects to OAuth provider for authentication
    """
    try:
        # Get authorization URL
        auth_url, state_token = oauth2_client.get_authorization_url(state=state)
        
        # Append username parameter if provided (useful for mock OAuth providers)
        if username:
            separator = "&" if "?" in auth_url else "?"
            auth_url = f"{auth_url}{separator}username={username}"
        
        # Store state in session (in production, use secure session storage)
        # For now, we'll return it in the response
        return JSONResponse(
            status_code=200,
            content={
                "authorization_url": auth_url,
                "state": state_token,
            },
        )
    except Exception as e:
        logger.error(f"Login initiation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Login initiation failed: {str(e)}",
        )


@router.get("/callback")
async def callback(
    code: str = Query(..., description="Authorization code"),
    state: Optional[str] = Query(None, description="State parameter"),
):
    """
    OAuth2 callback endpoint
    Exchanges authorization code for tokens and issues JWT tokens
    """
    try:
        # Exchange authorization code for tokens from OAuth provider
        token_response = await oauth2_client.exchange_code_for_tokens(code)
        provider_access_token = token_response.get("access_token")
        
        if not provider_access_token:
            raise UnauthorizedError("No access token in OAuth provider response")
        
        # Get user information from OAuth provider
        user_info = await oauth2_client.get_user_info(provider_access_token)
        
        # Extract user information
        user_id = user_info.get("sub")
        username = user_info.get("username") or user_info.get("preferred_username") or user_info.get("email")
        email = user_info.get("email")
        roles = user_info.get("roles", [])
        
        if not user_id:
            raise UnauthorizedError("No user ID in OAuth provider response")
        
        # If roles are not in user_info, set default role (submitter)
        # In production, roles would come from ADFS claims or user database
        if not roles:
            roles = ["submitter"]
        
        # Ensure username is set
        if not username:
            username = user_id
        
        # Issue JWT tokens (access token and refresh token)
        access_token = create_access_token(
            user_id=user_id,
            username=username or user_id,
            roles=roles,
            scope=token_response.get("scope"),
        )
        refresh_token = create_refresh_token(
            user_id=user_id,
            username=username,
            roles=roles,
            scope=token_response.get("scope"),
        )
        
        logger.info(f"Generated tokens for user: {username} ({user_id})")
        
        # Redirect to frontend with tokens
        # In production, tokens would be stored in HTTP-only cookies
        # For now, we'll return them in the response
        redirect_url = f"{settings.FRONTEND_CALLBACK_URI}?access_token={access_token}&refresh_token={refresh_token}"
        if state:
            redirect_url += f"&state={state}"
        
        return RedirectResponse(url=redirect_url, status_code=302)
    
    except UnauthorizedError as e:
        logger.error(f"Authorization failed: {e}")
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Callback processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Callback processing failed: {str(e)}",
        )


@router.post("/token", response_model=TokenResponse)
async def token(
    grant_type: str = Form(..., description="Grant type (must be 'refresh_token')"),
    refresh_token: Optional[str] = Form(None, description="Refresh token"),
):
    """
    Token endpoint for refreshing access tokens
    Supports refresh token grant type for token rotation
    """
    if grant_type != "refresh_token":
        raise HTTPException(
            status_code=400,
            detail="Only 'refresh_token' grant type is supported",
        )
    
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="refresh_token is required",
        )
    
    try:
        # Decode and validate refresh token
        token_data = decode_token(refresh_token)
        
        # Check token type
        if token_data.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        
        # Get user ID from token
        user_id = token_data.get("sub")
        if not user_id:
            raise UnauthorizedError("No user ID in token")
        
        # Get user information from OAuth provider (to get latest roles)
        # For now, we'll use the roles from the refresh token
        # In production, we might want to refresh user info from ADFS
        roles = token_data.get("roles", ["submitter"])
        username = token_data.get("username", user_id)
        
        # Create new tokens (token rotation)
        access_token = create_access_token(
            user_id=user_id,
            username=username,
            roles=roles,
            scope=token_data.get("scope"),
        )
        new_refresh_token = create_refresh_token(
            user_id=user_id,
            username=username,
            roles=roles,
            scope=token_data.get("scope"),
        )
        
        logger.info(f"Refreshed tokens for user: {username} ({user_id})")
        
        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRY_MINUTES * 60,
            refresh_token=new_refresh_token,
            scope=token_data.get("scope"),
        )
    
    except UnauthorizedError as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Token refresh failed: {str(e)}",
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint
    In a stateless JWT system, logout is handled client-side
    This endpoint can be used for logging/logging out events
    """
    # In a stateless JWT system, logout is handled client-side
    # by removing tokens from storage
    # This endpoint can be used for audit logging
    return JSONResponse(
        status_code=200,
        content={"message": "Logged out successfully"},
    )


class UserInfoResponse(BaseModel):
    """User info response model"""
    user_id: str
    username: str
    roles: list[str]
    scope: Optional[str] = None


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: UserContext = Depends(get_current_user),
):
    """
    Get current user information
    Protected endpoint that requires valid JWT token
    Demonstrates usage of get_current_user dependency
    """
    return UserInfoResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        roles=current_user.roles,
        scope=current_user.scope,
    )

