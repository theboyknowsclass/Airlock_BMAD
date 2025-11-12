"""
OAuth 2.0 endpoints
Implements Authorization Code flow for mock OAuth provider
"""
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

from ..models.user import TestUser, get_user_by_username, get_user_by_id
from ..models.auth_code import AuthCode, AuthCodeStore
from ..utils.jwt import create_access_token, create_refresh_token, decode_token
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Store for authorization codes (in-memory, cleared on restart)
auth_code_store = AuthCodeStore()


class TokenResponse(BaseModel):
    """OAuth 2.0 token response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class UserInfoResponse(BaseModel):
    """OpenID Connect UserInfo response"""
    sub: str  # user_id
    username: str
    email: str
    roles: List[str]
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None


@router.get("/authorize")
async def authorize(
    response_type: str = Query(..., description="Response type (must be 'code')"),
    client_id: str = Query(..., description="Client ID"),
    redirect_uri: str = Query(..., description="Redirect URI"),
    scope: Optional[str] = Query(None, description="Requested scopes"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    username: Optional[str] = Query(None, description="Username for authentication (mock only)"),
):
    """
    OAuth 2.0 Authorization endpoint
    In production, this would redirect to ADFS login page
    For mock, we accept username as query parameter and issue authorization code
    """
    # Validate response_type
    if response_type != "code":
        raise HTTPException(
            status_code=400,
            detail="Invalid response_type. Only 'code' is supported.",
        )

    # Validate client_id (for mock, we accept any client_id)
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="client_id is required",
        )

    # For mock service, we accept username as query parameter
    # In production, this would be handled by ADFS login page
    if not username:
        # Return a simple login form response
        # In a real implementation, this would redirect to ADFS
        return JSONResponse(
            status_code=200,
            content={
                "message": "Mock OAuth - Please provide username",
                "available_users": [
                    {"username": "submitter", "role": "Submitter"},
                    {"username": "reviewer", "role": "Reviewer"},
                    {"username": "admin", "role": "Admin"},
                    {"username": "reviewer-admin", "role": "Reviewer, Admin"},
                ],
                "usage": "Add ?username=submitter (or reviewer, admin, reviewer-admin) to authorize",
            },
        )

    # Get user by username
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=f"User '{username}' not found. Available users: submitter, reviewer, admin, reviewer-admin",
        )

    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    code_data = AuthCode(
        code=auth_code,
        user_id=user.user_id,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        expires_at=datetime.utcnow() + timedelta(minutes=10),  # Code expires in 10 minutes
    )
    auth_code_store.store(code_data)

    logger.info(f"Generated authorization code for user: {user.username}")

    # Redirect to redirect_uri with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/token", response_model=TokenResponse)
async def token(
    grant_type: str = Form(..., description="Grant type (must be 'authorization_code' or 'refresh_token')"),
    code: Optional[str] = Form(None, description="Authorization code"),
    redirect_uri: Optional[str] = Form(None, description="Redirect URI"),
    client_id: Optional[str] = Form(None, description="Client ID"),
    refresh_token: Optional[str] = Form(None, description="Refresh token"),
):
    """
    OAuth 2.0 Token endpoint
    Exchanges authorization code for access token and refresh token
    """
    if grant_type == "authorization_code":
        if not code:
            raise HTTPException(
                status_code=400,
                detail="code is required for authorization_code grant type",
            )

        # Retrieve authorization code
        auth_code = auth_code_store.get(code)
        if not auth_code:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired authorization code",
            )

        # Validate redirect_uri if provided
        if redirect_uri and auth_code.redirect_uri != redirect_uri:
            raise HTTPException(
                status_code=400,
                detail="redirect_uri does not match",
            )

        # Check if code has expired
        if auth_code.expires_at < datetime.utcnow():
            auth_code_store.delete(code)
            raise HTTPException(
                status_code=400,
                detail="Authorization code has expired",
            )

        # Get user
        user = get_user_by_id(auth_code.user_id)
        if not user:
            raise HTTPException(
                status_code=400,
                detail="User not found",
            )

        # Delete used authorization code (single-use)
        auth_code_store.delete(code)

        # Create tokens
        access_token = create_access_token(
            user_id=user.user_id,
            username=user.username,
            roles=user.roles,
            scope=auth_code.scope,
        )
        refresh_token = create_refresh_token(
            user_id=user.user_id,
            scope=auth_code.scope,
        )

        logger.info(f"Generated tokens for user: {user.username}")

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRY_MINUTES * 60,
            refresh_token=refresh_token,
            scope=auth_code.scope,
        )

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(
                status_code=400,
                detail="refresh_token is required for refresh_token grant type",
            )

        # Decode and validate refresh token
        try:
            token_data = decode_token(refresh_token)
        except Exception as e:
            logger.error(f"Failed to decode refresh token: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        # Check token type
        if token_data.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
            )

        # Get user
        user_id = token_data.get("sub")
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        # Create new tokens (token rotation)
        access_token = create_access_token(
            user_id=user.user_id,
            username=user.username,
            roles=user.roles,
            scope=token_data.get("scope"),
        )
        new_refresh_token = create_refresh_token(
            user_id=user.user_id,
            scope=token_data.get("scope"),
        )

        logger.info(f"Refreshed tokens for user: {user.username}")

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRY_MINUTES * 60,
            refresh_token=new_refresh_token,
            scope=token_data.get("scope"),
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported grant_type: {grant_type}",
        )


@router.get("/userinfo", response_model=UserInfoResponse)
async def userinfo(request: Request):
    """
    OpenID Connect UserInfo endpoint
    Returns user information based on access token
    """
    # Get Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required",
        )

    # Extract token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
        )

    token = authorization.replace("Bearer ", "")

    # Decode and validate token
    try:
        token_data = decode_token(token)
    except Exception as e:
        logger.error(f"Failed to decode token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    # Get user
    user_id = token_data.get("sub")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return UserInfoResponse(
        sub=user.user_id,
        username=user.username,
        email=user.email,
        roles=user.roles,
        name=user.name,
        given_name=user.given_name,
        family_name=user.family_name,
    )


@router.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request):
    """
    OpenID Connect Discovery endpoint
    Returns OpenID Connect configuration
    """
    base_url = str(request.base_url).rstrip("/")
    return {
        "issuer": f"{base_url}/oauth",
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "jwks_uri": f"{base_url}/oauth/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email"],
    }
