-- JWT Validation Lua script for OpenResty
-- Validates JWT tokens and extracts user context

local jwt = require "resty.jwt"
local validators = require "resty.jwt-validators"
local cjson = require "cjson"

-- Get JWT secret from environment
local jwt_secret = os.getenv("JWT_SECRET_KEY")
local jwt_algorithm = os.getenv("JWT_ALGORITHM") or "HS256"
local jwt_issuer = os.getenv("JWT_ISSUER") or "airlock-auth-service"

if not jwt_secret then
    ngx.log(ngx.ERR, "JWT_SECRET_KEY environment variable not set")
    ngx.status = 500
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({error = {code = "CONFIGURATION_ERROR", message = "JWT configuration missing"}}))
    ngx.exit(500)
end

-- Get Authorization header
local auth_header = ngx.var.http_authorization

if not auth_header then
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.header["WWW-Authenticate"] = "Bearer"
    ngx.say(cjson.encode({error = {code = "UNAUTHORIZED", message = "Authorization header required"}}))
    ngx.exit(401)
end

-- Extract token from "Bearer <token>"
local token = string.match(auth_header, "Bearer%s+(.+)")

if not token then
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.header["WWW-Authenticate"] = "Bearer"
    ngx.say(cjson.encode({error = {code = "UNAUTHORIZED", message = "Invalid authorization header format. Expected: Bearer <token>"}}))
    ngx.exit(401)
end

-- Validate JWT
local jwt_obj = jwt:verify(jwt_secret, token)

if not jwt_obj.valid then
    local error_msg = "Invalid or expired token"
    if jwt_obj.reason then
        error_msg = jwt_obj.reason
    end
    
    ngx.log(ngx.WARN, "JWT validation failed: " .. (jwt_obj.reason or "unknown error"))
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.header["WWW-Authenticate"] = "Bearer"
    ngx.say(cjson.encode({error = {code = "UNAUTHORIZED", message = error_msg}}))
    ngx.exit(401)
end

-- Verify token type is access token (not refresh token)
local token_type = jwt_obj.payload.type
if token_type ~= "access" then
    ngx.log(ngx.WARN, "Invalid token type: " .. (token_type or "nil"))
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.header["WWW-Authenticate"] = "Bearer"
    ngx.say(cjson.encode({error = {code = "UNAUTHORIZED", message = "Invalid token type. Access token required."}}))
    ngx.exit(401)
end

-- Verify issuer (if configured)
if jwt_issuer and jwt_obj.payload.iss ~= jwt_issuer then
    ngx.log(ngx.WARN, "Token issuer mismatch. Expected: " .. jwt_issuer .. ", Got: " .. (jwt_obj.payload.iss or "nil"))
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.header["WWW-Authenticate"] = "Bearer"
    ngx.say(cjson.encode({error = {code = "UNAUTHORIZED", message = "Invalid token issuer"}}))
    ngx.exit(401)
end

-- Extract user context from token claims
local user_id = jwt_obj.payload.sub
local username = jwt_obj.payload.username or user_id
local roles = jwt_obj.payload.roles or {}
local scope = jwt_obj.payload.scope
local api_key_id = jwt_obj.payload.api_key_id
local auth_type = jwt_obj.payload.auth_type

-- Validate required claims
if not user_id then
    ngx.log(ngx.WARN, "Token missing user ID (sub claim)")
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.header["WWW-Authenticate"] = "Bearer"
    ngx.say(cjson.encode({error = {code = "UNAUTHORIZED", message = "Invalid token: missing user ID"}}))
    ngx.exit(401)
end

-- Set user context headers for downstream services
ngx.req.set_header("X-User-ID", user_id)
ngx.req.set_header("X-Username", username)

-- Forward roles as JSON array
if roles and #roles > 0 then
    ngx.req.set_header("X-Roles", cjson.encode(roles))
end

-- Forward scope if present
if scope then
    ngx.req.set_header("X-Scope", scope)
end

-- Forward API key context if present
if api_key_id then
    ngx.req.set_header("X-API-Key-ID", tostring(api_key_id))
end

if auth_type then
    ngx.req.set_header("X-Auth-Type", auth_type)
end

-- Log successful validation (optional, can be removed for production)
ngx.log(ngx.INFO, "JWT validated successfully for user: " .. user_id .. " (username: " .. username .. ")")

