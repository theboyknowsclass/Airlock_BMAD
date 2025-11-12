# Mock OAuth Service

Mock OAuth provider that simulates ADFS for local development.

## Overview

This service provides OAuth 2.0 Authorization Code flow endpoints for local development, allowing authentication features to be developed without external ADFS dependencies.

## Features

- OAuth 2.0 Authorization Code flow
- JWT token generation (access tokens and refresh tokens)
- Test users with different roles (Submitter, Reviewer, Admin)
- OpenID Connect UserInfo endpoint
- OpenID Connect Discovery endpoint
- Configurable via environment variables

## Endpoints

### OAuth 2.0 Endpoints

- `GET /oauth/authorize` - Authorization endpoint
- `POST /oauth/token` - Token exchange endpoint
- `GET /oauth/userinfo` - User info endpoint
- `GET /oauth/.well-known/openid-configuration` - OpenID Connect Discovery endpoint

### Health Check Endpoints

- `GET /health` - Health check endpoint
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe

## Test Users

The service provides the following test users:

- **submitter** - Submitter role
- **reviewer** - Reviewer role
- **admin** - Admin role
- **reviewer-admin** - Reviewer and Admin roles

## Usage

### Authorization Flow

1. **Get authorization code:**
   ```
   GET /oauth/authorize?response_type=code&client_id=test-client&redirect_uri=http://localhost:3000/callback&username=submitter
   ```

2. **Exchange authorization code for tokens:**
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded
   
   grant_type=authorization_code&code=<authorization_code>&redirect_uri=http://localhost:3000/callback&client_id=test-client
   ```

3. **Get user info:**
   ```
   GET /oauth/userinfo
   Authorization: Bearer <access_token>
   ```

### Refresh Token Flow

```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token=<refresh_token>
```

## Configuration

### Environment Variables

- `JWT_SECRET_KEY` - JWT secret key (default: dev-secret-key-change-in-production-...)
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_ISSUER` - JWT issuer (default: airlock-mock-oauth)
- `ACCESS_TOKEN_EXPIRY_MINUTES` - Access token expiry in minutes (default: 15)
- `REFRESH_TOKEN_EXPIRY_DAYS` - Refresh token expiry in days (default: 7)
- `LOG_LEVEL` - Log level (default: INFO)
- `SERVICE_NAME` - Service name (default: mock-oauth)
- `CORS_ORIGINS` - CORS origins (default: *)

## Token Structure

### Access Token Claims

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

### Refresh Token Claims

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

## Docker

### Build

```bash
docker build -t airlock-mock-oauth mock-services/mock-oauth
```

### Run

```bash
docker run -p 9000:9000 airlock-mock-oauth
```

### Docker Compose

The service is included in `docker-compose.dev.yml` and runs automatically with:

```bash
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up
```

## Testing

### Manual Testing

1. **Test authorization endpoint:**
   ```bash
   curl "http://localhost:9000/oauth/authorize?response_type=code&client_id=test-client&redirect_uri=http://localhost:3000/callback&username=submitter"
   ```

2. **Test token endpoint:**
   ```bash
   curl -X POST "http://localhost:9000/oauth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&code=<code>&redirect_uri=http://localhost:3000/callback&client_id=test-client"
   ```

3. **Test userinfo endpoint:**
   ```bash
   curl "http://localhost:9000/oauth/userinfo" \
     -H "Authorization: Bearer <access_token>"
   ```

## Notes

- Authorization codes expire after 10 minutes
- Authorization codes are single-use (deleted after exchange)
- Refresh tokens support token rotation (new refresh token issued on use)
- In-memory authorization code store (cleared on restart)
- Test users are hardcoded (no database required)

## Security

**Important:** This is a mock service for development only. Do not use in production.

- Default JWT secret key should be changed in production
- Authorization codes are stored in-memory (not persistent)
- No actual user authentication (username parameter for testing)
- No password validation

## License

MIT

