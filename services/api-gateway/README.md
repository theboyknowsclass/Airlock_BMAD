# API Gateway Service (OpenResty/Nginx)

Pure Nginx-based API gateway using OpenResty for JWT validation, rate limiting, and request routing.

## Features

- **JWT Validation**: Validates JWT tokens using Lua scripts and `lua-resty-jwt`
- **Rate Limiting**: Per-IP rate limiting with configurable zones
- **Request Routing**: Routes requests to appropriate microservices based on URL path
- **User Context Forwarding**: Extracts user context from JWT and forwards via headers
- **CORS Support**: Configurable CORS headers
- **Health Checks**: Built-in health check endpoint

## Architecture

```
Client Request
    ↓
Nginx/OpenResty Gateway
    ├── JWT Validation (Lua)
    ├── Rate Limiting
    ├── Request Routing
    └── User Context Extraction
    ↓
Backend Microservices
```

## Configuration

### Environment Variables

- `JWT_SECRET_KEY`: Secret key for JWT validation (required)
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `JWT_ISSUER`: JWT issuer claim to validate (default: airlock-auth-service)

### Rate Limiting

- **API endpoints**: 100 requests/second per IP (burst: 20)
- **Auth endpoints**: 10 requests/second per IP (burst: 5)

### Routing

- `/api/v1/auth/*` → `auth-service`
- `/api/v1/users/*` → `user-service`
- `/api/v1/packages/*` → `submission-service`
- `/api/v1/workflows/*` → `workflow-service`
- `/api/v1/storage/*` → `storage-service`
- `/api/v1/registry/*` → `registry-service`
- `/api/v1/tracking/*` → `tracking-service`
- `/api/v1/api-keys/*` → `api-key-service` (requires admin role)
- `/` → `frontend` (static files)

## JWT Validation

The gateway validates JWT tokens and extracts:
- User ID (`sub` claim) → `X-User-ID` header
- Username → `X-Username` header
- Roles → `X-Roles` header (JSON array)
- Scope → `X-Scope` header
- API Key ID → `X-API-Key-ID` header (if present)
- Auth Type → `X-Auth-Type` header (if present)

## Protected Endpoints

Most API endpoints require JWT authentication. Exceptions:
- `/health` - Health check (no auth)
- `/api/v1/auth/login` - OAuth login
- `/api/v1/auth/callback` - OAuth callback
- `/api/v1/auth/token` - Token refresh
- `/api/v1/api-keys/auth/token` - API key authentication

## Development

### Building

```bash
docker build -t airlock-api-gateway ./services/api-gateway
```

### Testing Configuration

```bash
docker run --rm -it \
  -e JWT_SECRET_KEY=test-secret \
  -e JWT_ALGORITHM=HS256 \
  -e JWT_ISSUER=airlock-auth-service \
  airlock-api-gateway \
  /usr/local/openresty/bin/openresty -t
```

### Viewing Logs

```bash
docker logs airlock-api-gateway
```

## Dependencies

- OpenResty (Nginx + Lua)
- lua-resty-jwt (via opm)

## Notes

- Uses OpenResty's `alpine-fat` image to include `opm` for package management
- Lua scripts are located in `/usr/local/openresty/nginx/lua/`
- Nginx configuration is in `/usr/local/openresty/nginx/conf/`

