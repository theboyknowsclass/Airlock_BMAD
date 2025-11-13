# Pure Nginx API Gateway Implementation

## Overview

This implementation replaces the FastAPI-based API gateway with a pure Nginx/OpenResty solution. This provides:

- **Better Performance**: Nginx handles high concurrency efficiently
- **Lower Resource Usage**: No Python runtime overhead
- **Industry Standard**: Nginx is the most common reverse proxy/gateway solution
- **On-Prem Friendly**: No external dependencies, works in air-gapped environments

## Architecture

### Components

1. **OpenResty**: Nginx with Lua support for JWT validation
2. **lua-resty-jwt**: Lua library for JWT validation
3. **Nginx Configuration**: Routing, rate limiting, CORS
4. **Lua Scripts**: JWT validation and user context extraction

### Request Flow

```
Client Request
    ↓
Nginx Gateway (port 80)
    ├── Health Check? → Return 200
    ├── Auth Endpoint? → Route to auth-service (no JWT)
    ├── API Key Auth? → Route to api-key-service (no JWT)
    ├── Protected Endpoint? → Validate JWT → Route to service
    └── Frontend? → Route to frontend
```

## JWT Validation

### Standard Validation (`validate_jwt.lua`)

Validates:
- Token signature (using JWT_SECRET_KEY)
- Token expiration
- Token type (must be "access")
- Issuer (if JWT_ISSUER configured)
- Required claims (sub/user_id)

Extracts and forwards:
- `X-User-ID`: User ID from `sub` claim
- `X-Username`: Username from token
- `X-Roles`: JSON array of roles
- `X-Scope`: OAuth scope (if present)
- `X-API-Key-ID`: API key ID (if API key token)
- `X-Auth-Type`: Authentication type (if present)

### Admin Validation (`validate_jwt_admin.lua`)

Same as standard validation, plus:
- Checks for "admin" role in token
- Returns 403 if user is not admin

## Rate Limiting

### Zones

- **api_limit**: 100 req/s per IP (burst: 20)
  - Applied to: `/api/v1/*` endpoints (except auth)
  
- **auth_limit**: 10 req/s per IP (burst: 5)
  - Applied to: `/api/v1/auth/*` endpoints

### Configuration

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/s;
```

## Routing

### Service Mapping

| Path Pattern | Service | Auth Required |
|-------------|---------|---------------|
| `/health` | Gateway (local) | No |
| `/` | frontend | No |
| `/api/v1/auth/*` | auth-service | No (for login/callback/token) |
| `/api/v1/api-keys/auth/token` | api-key-service | No (uses X-API-Key) |
| `/api/v1/api-keys/*` | api-key-service | Yes (Admin) |
| `/api/v1/users/*` | user-service | Yes |
| `/api/v1/packages/*` | submission-service | Yes |
| `/api/v1/workflows/*` | workflow-service | Yes |
| `/api/v1/storage/*` | storage-service | Yes |
| `/api/v1/registry/*` | registry-service | Yes |
| `/api/v1/tracking/*` | tracking-service | Yes |

## Environment Variables

Required:
- `JWT_SECRET_KEY`: Secret for JWT validation

Optional:
- `JWT_ALGORITHM`: Algorithm (default: HS256)
- `JWT_ISSUER`: Issuer to validate (default: airlock-auth-service)

## Error Handling

### Error Responses

All errors return JSON:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

### Error Codes

- `UNAUTHORIZED` (401): Missing/invalid JWT token
- `FORBIDDEN` (403): Insufficient permissions (e.g., not admin)
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `CONFIGURATION_ERROR` (500): Missing configuration
- `INTERNAL_SERVER_ERROR` (500): Gateway error

## CORS Configuration

Currently configured for development (allows all origins). For production:

```nginx
add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
```

## Testing

### Test JWT Validation

```bash
# Valid token
curl -H "Authorization: Bearer <valid-jwt>" http://localhost/api/v1/users

# Invalid token
curl -H "Authorization: Bearer invalid" http://localhost/api/v1/users

# Missing token
curl http://localhost/api/v1/users
```

### Test Rate Limiting

```bash
# Send 101 requests quickly
for i in {1..101}; do curl http://localhost/api/v1/users; done
# 101st request should return 429
```

### Test Routing

```bash
# Should route to auth-service
curl http://localhost/api/v1/auth/login

# Should route to user-service (with JWT)
curl -H "Authorization: Bearer <jwt>" http://localhost/api/v1/users
```

## Migration from FastAPI Gateway

### Changes Required

1. **Remove FastAPI gateway code**: The `src/` directory is no longer needed
2. **Update Docker Compose**: Already updated to use new gateway
3. **Update environment variables**: Only JWT-related vars needed
4. **Update health checks**: Changed from port 8000 to port 80

### Backend Services

No changes required! Backend services receive the same headers:
- `X-User-ID`
- `X-Username`
- `X-Roles`
- `X-Scope`
- etc.

## Performance Considerations

### Advantages

- **Lower Latency**: No Python overhead
- **Higher Throughput**: Nginx handles 10k+ concurrent connections
- **Lower Memory**: ~10-20MB vs ~50-100MB for Python

### Limitations

- **Per-IP Rate Limiting**: Not per-user (would require Redis)
- **No Distributed Rate Limiting**: Each gateway instance has its own limits
- **Lua Learning Curve**: Custom logic requires Lua knowledge

## Future Enhancements

1. **Per-User Rate Limiting**: Use Redis to track per-user limits
2. **Distributed Rate Limiting**: Share rate limit state across instances
3. **Request/Response Transformation**: Add Lua scripts for payload modification
4. **Advanced Routing**: Service discovery, load balancing algorithms
5. **Metrics/Monitoring**: Export metrics to Prometheus

## Troubleshooting

### JWT Validation Fails

1. Check `JWT_SECRET_KEY` matches auth-service
2. Check `JWT_ISSUER` matches token issuer
3. Check token is not expired
4. Check token type is "access" (not "refresh")

### Routing Not Working

1. Check service names in `nginx.conf` match Docker service names
2. Check services are running: `docker ps`
3. Check network connectivity: `docker network inspect airlock-network`

### Rate Limiting Too Aggressive

Adjust in `nginx.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=200r/s;
```

### Logs

View Nginx logs:
```bash
docker logs airlock-api-gateway
```

Logs include:
- Access logs: Request/response details
- Error logs: JWT validation failures, configuration errors

