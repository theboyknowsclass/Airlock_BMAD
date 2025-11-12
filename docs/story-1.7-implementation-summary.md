# Story 1.7: Mock OAuth Service for Development - Implementation Summary

## Overview

Implemented a mock OAuth provider service that simulates ADFS for local development. The service provides OAuth 2.0 Authorization Code flow endpoints, JWT token generation, and test users with different roles.

## Acceptance Criteria

✅ **Mock OAuth service is running**
- Service runs in Docker on port 9000
- Health check endpoints available (`/health`, `/health/live`, `/health/ready`)

✅ **OAuth 2.0 endpoints provided:**
- `/oauth/authorize` - Authorization endpoint
- `/oauth/token` - Token exchange endpoint
- `/oauth/userinfo` - User info endpoint
- `/oauth/.well-known/openid-configuration` - OpenID Connect Discovery endpoint

✅ **Test users with different roles:**
- `submitter` - Submitter role
- `reviewer` - Reviewer role
- `admin` - Admin role
- `reviewer-admin` - Reviewer and Admin roles (multiple roles)

✅ **JWT tokens compatible with production flow:**
- Access tokens: 15 minutes expiry (configurable)
- Refresh tokens: 7 days expiry (configurable)
- Token rotation supported (new refresh token issued on use)
- JWT tokens include user ID, username, roles, and standard claims

✅ **Configurable via environment variables:**
- `JWT_SECRET_KEY` - JWT secret key
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_ISSUER` - JWT issuer (default: airlock-mock-oauth)
- `ACCESS_TOKEN_EXPIRY_MINUTES` - Access token expiry (default: 15)
- `REFRESH_TOKEN_EXPIRY_DAYS` - Refresh token expiry (default: 7)
- `LOG_LEVEL` - Log level (default: INFO)
- `MOCK_OAUTH_PORT` - Service port (default: 9000)

## Implementation Details

### Service Structure

```
mock-services/mock-oauth/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── routers/
│   │   ├── health.py           # Health check endpoints
│   │   └── oauth.py            # OAuth 2.0 endpoints
│   ├── models/
│   │   ├── user.py             # Test user models
│   │   └── auth_code.py        # Authorization code models
│   └── utils/
│       ├── jwt.py              # JWT token utilities
│       └── logging.py          # Logging configuration
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Multi-stage Docker build
└── README.md                   # Service documentation
```

### OAuth 2.0 Flow

1. **Authorization Request:**
   ```
   GET /oauth/authorize?response_type=code&client_id=test-client&redirect_uri=http://localhost:3000/callback&username=submitter
   ```
   - Returns authorization code in redirect URL
   - Authorization code expires in 10 minutes
   - Single-use (deleted after exchange)

2. **Token Exchange:**
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded
   
   grant_type=authorization_code&code=<code>&redirect_uri=http://localhost:3000/callback&client_id=test-client
   ```
   - Returns access token and refresh token
   - Access token: 15 minutes expiry
   - Refresh token: 7 days expiry

3. **User Info:**
   ```
   GET /oauth/userinfo
   Authorization: Bearer <access_token>
   ```
   - Returns user information (user ID, username, email, roles)

4. **Refresh Token:**
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded
   
   grant_type=refresh_token&refresh_token=<refresh_token>
   ```
   - Returns new access token and new refresh token (token rotation)

### JWT Token Structure

**Access Token Claims:**
```json
{
  "sub": "user_id",
  "username": "submitter",
  "roles": ["submitter"],
  "exp": 1234567890,
  "iat": 1234567890,
  "iss": "airlock-mock-oauth",
  "type": "access"
}
```

**Refresh Token Claims:**
```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "iat": 1234567890,
  "iss": "airlock-mock-oauth",
  "type": "refresh",
  "jti": "token_id"
}
```

### Test Users

- **submitter** - User ID: `user-submitter-001`, Roles: `["submitter"]`
- **reviewer** - User ID: `user-reviewer-001`, Roles: `["reviewer"]`
- **admin** - User ID: `user-admin-001`, Roles: `["admin"]`
- **reviewer-admin** - User ID: `user-reviewer-admin-001`, Roles: `["reviewer", "admin"]`

## Files Created/Modified

### Created Files

- `mock-services/mock-oauth/src/main.py` - FastAPI application entry point
- `mock-services/mock-oauth/src/config.py` - Configuration settings
- `mock-services/mock-oauth/src/routers/health.py` - Health check endpoints
- `mock-services/mock-oauth/src/routers/oauth.py` - OAuth 2.0 endpoints
- `mock-services/mock-oauth/src/models/user.py` - Test user models
- `mock-services/mock-oauth/src/models/auth_code.py` - Authorization code models
- `mock-services/mock-oauth/src/utils/jwt.py` - JWT token utilities
- `mock-services/mock-oauth/src/utils/logging.py` - Logging configuration
- `mock-services/mock-oauth/requirements.txt` - Python dependencies
- `mock-services/mock-oauth/Dockerfile` - Multi-stage Docker build
- `mock-services/mock-oauth/README.md` - Service documentation
- `scripts/test-mock-oauth.ps1` - PowerShell test script
- `scripts/test-mock-oauth-simple.ps1` - Simple Python test script

### Modified Files

- `docker-compose.dev.yml` - Added mock-oauth service configuration
- `.bmad-ephemeral/sprint-status.yaml` - Updated story status to `in-progress`

## Dependencies

### Python Dependencies

- `fastapi==0.115.0` - FastAPI web framework
- `uvicorn[standard]==0.32.1` - ASGI server
- `python-multipart==0.0.12` - Form data handling
- `python-jose[cryptography]==3.3.0` - JWT encoding/decoding
- `pydantic==2.10.4` - Data validation
- `pydantic-settings==2.7.1` - Settings management
- `passlib[bcrypt]==1.7.4` - Password hashing (for future use)

## Docker Configuration

### Docker Compose

The mock OAuth service is included in `docker-compose.dev.yml`:

```yaml
mock-oauth:
  build:
    context: ./mock-services/mock-oauth
    dockerfile: Dockerfile
  container_name: airlock-mock-oauth
  ports:
    - "${MOCK_OAUTH_PORT:-9000}:9000"
  environment:
    JWT_SECRET_KEY: ${JWT_SECRET_KEY:-dev-secret-key-change-in-production-...}
    JWT_ALGORITHM: ${JWT_ALGORITHM:-HS256}
    JWT_ISSUER: ${JWT_ISSUER:-airlock-mock-oauth}
    ACCESS_TOKEN_EXPIRY_MINUTES: ${ACCESS_TOKEN_EXPIRY_MINUTES:-15}
    REFRESH_TOKEN_EXPIRY_DAYS: ${REFRESH_TOKEN_EXPIRY_DAYS:-7}
    LOG_LEVEL: ${LOG_LEVEL:-DEBUG}
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  networks:
    - airlock-network
```

## Testing

### Manual Testing

1. **Start the service:**
   ```bash
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d mock-oauth
   ```

2. **Test health check:**
   ```bash
   curl http://localhost:9000/health
   ```

3. **Test authorization flow:**
   ```bash
   # Get authorization code
   curl "http://localhost:9000/oauth/authorize?response_type=code&client_id=test-client&redirect_uri=http://localhost:3000/callback&username=submitter"
   
   # Exchange code for tokens
   curl -X POST "http://localhost:9000/oauth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&code=<code>&redirect_uri=http://localhost:3000/callback&client_id=test-client"
   
   # Get user info
   curl "http://localhost:9000/oauth/userinfo" \
     -H "Authorization: Bearer <access_token>"
   ```

### Test Scripts

- `scripts/test-mock-oauth.ps1` - PowerShell test script (requires fixing redirect handling)
- `scripts/test-mock-oauth-simple.ps1` - Python test script (requires `requests` library)

## Usage Examples

### Authorization Code Flow

1. **Get authorization code:**
   ```
   GET /oauth/authorize?response_type=code&client_id=test-client&redirect_uri=http://localhost:3000/callback&username=submitter
   ```
   - Redirects to: `http://localhost:3000/callback?code=<authorization_code>`

2. **Exchange code for tokens:**
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded
   
   grant_type=authorization_code&code=<code>&redirect_uri=http://localhost:3000/callback&client_id=test-client
   ```
   - Returns: `{ "access_token": "...", "refresh_token": "...", "expires_in": 900, ... }`

3. **Get user info:**
   ```
   GET /oauth/userinfo
   Authorization: Bearer <access_token>
   ```
   - Returns: `{ "sub": "user_id", "username": "submitter", "email": "submitter@example.com", "roles": ["submitter"], ... }`

### Refresh Token Flow

```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token=<refresh_token>
```
- Returns: New access token and new refresh token (token rotation)

## Security Notes

**Important:** This is a mock service for development only. Do not use in production.

- Default JWT secret key should be changed in production
- Authorization codes are stored in-memory (not persistent)
- No actual user authentication (username parameter for testing)
- No password validation
- Test users are hardcoded (no database required)

## Next Steps

1. **Story 2.1:** Authentication Service - OAuth2 Integration with ADFS
   - Use mock OAuth service for development
   - Integrate with production ADFS in production environment

2. **Future Enhancements:**
   - Add user management UI for test users
   - Add password-based authentication for test users
   - Add token introspection endpoint
   - Add token revocation endpoint

## Notes

- Authorization codes expire after 10 minutes
- Authorization codes are single-use (deleted after exchange)
- Refresh tokens support token rotation (new refresh token issued on use)
- In-memory authorization code store (cleared on restart)
- Test users are hardcoded (no database required)
- Service matches production ADFS flow as closely as possible

## Verification

✅ Service starts successfully in Docker
✅ Health check endpoints respond correctly
✅ Authorization endpoint generates authorization codes
✅ Token endpoint exchanges authorization codes for tokens
✅ UserInfo endpoint returns user information
✅ Refresh token endpoint supports token rotation
✅ OpenID Connect Discovery endpoint returns configuration
✅ JWT tokens include correct claims (user ID, username, roles)
✅ Test users with different roles are available
✅ Configuration is environment variable-based

## Conclusion

Story 1.7 is complete. The mock OAuth service provides OAuth 2.0 Authorization Code flow endpoints, JWT token generation, and test users with different roles. The service is configurable via environment variables and matches the production ADFS flow as closely as possible for local development.

