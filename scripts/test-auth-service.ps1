# Test Authentication Service - OAuth2 Flow with Mock OAuth
# This script tests the complete OAuth2 authorization code flow

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Authentication Service" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$AUTH_SERVICE_URL = "http://localhost:8001"
$MOCK_OAUTH_URL = "http://localhost:9000"
$TEST_USERNAME = "submitter"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Yellow }
function Write-Step { Write-Host $args -ForegroundColor Cyan }

# Test helper function
function Invoke-GetRequest {
    param(
        [string]$Url
    )
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method GET -ErrorAction Stop
        return @{
            Success = $true
            Response = $response
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        return @{
            Success = $false
            StatusCode = $statusCode
            Error = $_.Exception.Message
        }
    }
}

# Test helper function for POST
function Invoke-PostRequest {
    param(
        [string]$Url,
        [hashtable]$Body
    )
    
    try {
        $formData = ($Body.Keys | ForEach-Object { "$_=$($Body[$_])" }) -join "&"
        $response = Invoke-RestMethod -Uri $Url -Method POST -Body $formData -ContentType "application/x-www-form-urlencoded" -ErrorAction Stop
        return @{
            Success = $true
            Response = $response
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $errorMessage = $_.Exception.Message
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            $errorMessage = "$errorMessage - $responseBody"
        } catch {
            # Ignore error reading response stream
        }
        return @{
            Success = $false
            StatusCode = $statusCode
            Error = $errorMessage
        }
    }
}

# Step 1: Check if services are running
Write-Step "Step 1: Checking if services are running..."

$authHealth = Invoke-GetRequest -Url "$AUTH_SERVICE_URL/health"
if (-not $authHealth.Success) {
    Write-Error "  [FAIL] Auth service is not running at $AUTH_SERVICE_URL"
    Write-Info "  Please start the services:"
    Write-Info "    docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d auth-service mock-oauth"
    exit 1
}
Write-Success "  [OK] Auth service is running"

$mockHealth = Invoke-GetRequest -Url "$MOCK_OAUTH_URL/health"
if (-not $mockHealth.Success) {
    Write-Error "  [FAIL] Mock OAuth service is not running at $MOCK_OAUTH_URL"
    Write-Info "  Please start the services:"
    Write-Info "    docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d mock-oauth"
    exit 1
}
Write-Success "  [OK] Mock OAuth service is running"
Write-Host ""

# Step 2: Test login endpoint - get authorization URL
Write-Step "Step 2: Testing login endpoint (get authorization URL)..."

$loginUrl = "$AUTH_SERVICE_URL/api/v1/auth/login?username=$TEST_USERNAME"
$loginResponse = Invoke-GetRequest -Url $loginUrl

if (-not $loginResponse.Success) {
    Write-Error "  [FAIL] Login endpoint failed: $($loginResponse.Error)"
    Write-Info "  Status code: $($loginResponse.StatusCode)"
    exit 1
}

$authUrl = $loginResponse.Response.authorization_url
$state = $loginResponse.Response.state

if (-not $authUrl) {
    Write-Error "  [FAIL] No authorization URL in response"
    exit 1
}

Write-Success "  [OK] Authorization URL received"
Write-Info "  Authorization URL: $($authUrl.Substring(0, [Math]::Min(100, $authUrl.Length)))..."
Write-Info "  State: $state"
Write-Host ""

# Step 3: Follow authorization URL to get authorization code
Write-Step "Step 3: Following authorization URL to get authorization code..."

# Replace Docker internal hostname with localhost for host-based access
# The auth service returns URLs with 'mock-oauth' (Docker service name)
# but we need to use 'localhost' when accessing from the host machine
$authUrl = $authUrl -replace 'http://mock-oauth:', 'http://localhost:'
Write-Info "  Updated URL for host access: $($authUrl.Substring(0, [Math]::Min(100, $authUrl.Length)))..."

# Extract redirect_uri from authorization URL to understand the flow
# The mock OAuth will redirect back to the auth service callback with a code

# Make request to authorization endpoint and handle redirect
try {
    # Create HTTP request manually to capture redirect headers
    $request = [System.Net.HttpWebRequest]::Create($authUrl)
    $request.Method = "GET"
    $request.AllowAutoRedirect = $false
    
    try {
        $response = $request.GetResponse()
        $statusCode = [int]$response.StatusCode
        $statusCodeEnum = $response.StatusCode
        
        # Check if this is a redirect (302, 307, 308)
        if ($statusCode -eq 302 -or $statusCode -eq 307 -or $statusCode -eq 308 -or $statusCodeEnum -eq "Redirect") {
            $location = $response.Headers["Location"]
            if ($location) {
                $locationString = $location.ToString()
                
                Write-Success "  [OK] Redirect received from mock OAuth"
                Write-Info "  Redirect location: $($locationString.Substring(0, [Math]::Min(150, $locationString.Length)))..."
                
                # Extract code from redirect URL
                if ($locationString -match "code=([^&]+)") {
                    $authCode = $matches[1]
                    Write-Success "  [OK] Authorization code received"
                    Write-Info "  Authorization code: $($authCode.Substring(0, [Math]::Min(50, $authCode.Length)))..."
                } else {
                    Write-Error "  [FAIL] No authorization code in redirect URL"
                    Write-Info "  Redirect URL: $locationString"
                    exit 1
                }
            } else {
                Write-Error "  [FAIL] Redirect received but no Location header"
                exit 1
            }
        } else {
            Write-Error "  [FAIL] Expected redirect but got status code: $statusCode ($statusCodeEnum)"
            exit 1
        }
        $response.Close()
    } catch {
        $webException = $_.Exception
        if ($webException.Response) {
            $httpResponse = $webException.Response
            $statusCode = [int]$httpResponse.StatusCode
            if ($statusCode -eq 302 -or $statusCode -eq 307 -or $statusCode -eq 308) {
                $location = $httpResponse.Headers["Location"]
                if ($location) {
                    $locationString = $location.ToString()
                    
                    Write-Success "  [OK] Redirect received from mock OAuth"
                    Write-Info "  Redirect location: $($locationString.Substring(0, [Math]::Min(150, $locationString.Length)))..."
                    
                    # Extract code from redirect URL
                    if ($locationString -match "code=([^&]+)") {
                        $authCode = $matches[1]
                        Write-Success "  [OK] Authorization code received"
                        Write-Info "  Authorization code: $($authCode.Substring(0, [Math]::Min(50, $authCode.Length)))..."
                    } else {
                        Write-Error "  [FAIL] No authorization code in redirect URL"
                        Write-Info "  Redirect URL: $locationString"
                        exit 1
                    }
                } else {
                    Write-Error "  [FAIL] Redirect received but no Location header"
                    exit 1
                }
            } else {
                Write-Error "  [FAIL] Authorization request failed with status code: $statusCode"
                Write-Info "  Error: $($webException.Message)"
            }
            $httpResponse.Close()
        } else {
            Write-Error "  [FAIL] Authorization request failed: $($webException.Message)"
            exit 1
        }
    }
} catch {
    Write-Error "  [FAIL] Failed to create request: $($_.Exception.Message)"
    exit 1
}
Write-Host ""

# Step 4: Test callback endpoint - exchange code for tokens
Write-Step "Step 4: Testing callback endpoint (exchange code for tokens)..."

if (-not $authCode) {
    Write-Error "  [FAIL] No authorization code available"
    exit 1
}

$callbackUrl = "$AUTH_SERVICE_URL/api/v1/auth/callback?code=$authCode&state=$state"

# The callback should redirect, so we need to handle that
try {
    $request = [System.Net.HttpWebRequest]::Create($callbackUrl)
    $request.Method = "GET"
    $request.AllowAutoRedirect = $false
    
    try {
        $response = $request.GetResponse()
        $statusCode = [int]$response.StatusCode
        $statusCodeEnum = $response.StatusCode
        
        # Check if this is a redirect (302, 307, 308)
        if ($statusCode -eq 302 -or $statusCode -eq 307 -or $statusCode -eq 308 -or $statusCodeEnum -eq "Redirect") {
            $location = $response.Headers["Location"]
            if ($location) {
                $locationString = $location.ToString()
                
                Write-Success "  [OK] Callback redirect received"
                Write-Info "  Redirect location: $($locationString.Substring(0, [Math]::Min(200, $locationString.Length)))..."
                
                # Extract tokens from redirect URL
                if ($locationString -match "access_token=([^&]+)") {
                    $accessToken = $matches[1]
                    Write-Success "  [OK] Access token received"
                    Write-Info "  Access token: $($accessToken.Substring(0, [Math]::Min(50, $accessToken.Length)))..."
                } else {
                    Write-Error "  [FAIL] No access token in redirect URL"
                    Write-Info "  Redirect URL: $locationString"
                    exit 1
                }
                
                if ($locationString -match "refresh_token=([^&]+)") {
                    $refreshToken = $matches[1]
                    Write-Success "  [OK] Refresh token received"
                    Write-Info "  Refresh token: $($refreshToken.Substring(0, [Math]::Min(50, $refreshToken.Length)))..."
                } else {
                    Write-Error "  [FAIL] No refresh token in redirect URL"
                    Write-Info "  Redirect URL: $locationString"
                    exit 1
                }
            } else {
                Write-Error "  [FAIL] Redirect received but no Location header"
                exit 1
            }
        } else {
            Write-Error "  [FAIL] Expected redirect but got status code: $statusCode ($statusCodeEnum)"
            exit 1
        }
        $response.Close()
    } catch {
        $webException = $_.Exception
        if ($webException.Response) {
            $httpResponse = $webException.Response
            $statusCode = [int]$httpResponse.StatusCode
            if ($statusCode -eq 302 -or $statusCode -eq 307 -or $statusCode -eq 308) {
                $location = $httpResponse.Headers["Location"]
                if ($location) {
                    $locationString = $location.ToString()
                    
                    Write-Success "  [OK] Callback redirect received"
                    Write-Info "  Redirect location: $($locationString.Substring(0, [Math]::Min(200, $locationString.Length)))..."
                    
                    # Extract tokens from redirect URL
                    if ($locationString -match "access_token=([^&]+)") {
                        $accessToken = $matches[1]
                        Write-Success "  [OK] Access token received"
                        Write-Info "  Access token: $($accessToken.Substring(0, [Math]::Min(50, $accessToken.Length)))..."
                    } else {
                        Write-Error "  [FAIL] No access token in redirect URL"
                        Write-Info "  Redirect URL: $locationString"
                        exit 1
                    }
                    
                    if ($locationString -match "refresh_token=([^&]+)") {
                        $refreshToken = $matches[1]
                        Write-Success "  [OK] Refresh token received"
                        Write-Info "  Refresh token: $($refreshToken.Substring(0, [Math]::Min(50, $refreshToken.Length)))..."
                    } else {
                        Write-Error "  [FAIL] No refresh token in redirect URL"
                        Write-Info "  Redirect URL: $locationString"
                        exit 1
                    }
                } else {
                    Write-Error "  [FAIL] Redirect received but no Location header"
                    exit 1
                }
            } else {
                Write-Error "  [FAIL] Callback request failed with status code: $statusCode"
                Write-Info "  Error: $($webException.Message)"
                # Try to read error response
                try {
                    $reader = New-Object System.IO.StreamReader($httpResponse.GetResponseStream())
                    $errorBody = $reader.ReadToEnd()
                    Write-Info "  Error body: $errorBody"
                } catch {
                    # Ignore error reading response stream
                }
                exit 1
            }
            $httpResponse.Close()
        } else {
            Write-Error "  [FAIL] Callback request failed: $($webException.Message)"
            exit 1
        }
    }
} catch {
    Write-Error "  [FAIL] Failed to create callback request: $($_.Exception.Message)"
    exit 1
}
Write-Host ""

# Step 5: Decode and verify JWT token
Write-Step "Step 5: Decoding and verifying JWT token..."

if (-not $accessToken) {
    Write-Error "  [FAIL] No access token available"
    exit 1
}

# Decode JWT token (without verification for testing)
try {
    $tokenParts = $accessToken.Split('.')
    if ($tokenParts.Length -ne 3) {
        Write-Error "  [FAIL] Invalid JWT token format"
        exit 1
    }
    
    # Decode payload (base64url)
    $payload = $tokenParts[1]
    # Add padding if needed
    $padding = 4 - ($payload.Length % 4)
    if ($padding -ne 4) {
        $payload = $payload + ("=" * $padding)
    }
    $payload = $payload.Replace('-', '+').Replace('_', '/')
    $payloadBytes = [System.Convert]::FromBase64String($payload)
    $payloadJson = [System.Text.Encoding]::UTF8.GetString($payloadBytes)
    $payloadObj = $payloadJson | ConvertFrom-Json
    
    Write-Success "  [OK] JWT token decoded successfully"
    Write-Info "  User ID: $($payloadObj.sub)"
    Write-Info "  Username: $($payloadObj.username)"
    Write-Info "  Roles: $($payloadObj.roles -join ', ')"
    Write-Info "  Token type: $($payloadObj.type)"
    Write-Info "  Issuer: $($payloadObj.iss)"
    
    # Verify token claims
    if ($payloadObj.type -ne "access") {
        Write-Error "  [FAIL] Invalid token type: $($payloadObj.type)"
        exit 1
    }
    
    if (-not $payloadObj.sub) {
        Write-Error "  [FAIL] No user ID in token"
        exit 1
    }
    
    if (-not $payloadObj.roles -or $payloadObj.roles.Count -eq 0) {
        Write-Error "  [FAIL] No roles in token"
        exit 1
    }
    
    Write-Success "  [OK] Token claims verified"
} catch {
    Write-Error "  [FAIL] Failed to decode token: $($_.Exception.Message)"
    exit 1
}
Write-Host ""

# Step 6: Test token refresh endpoint
Write-Step "Step 6: Testing token refresh endpoint..."

if (-not $refreshToken) {
    Write-Error "  [FAIL] No refresh token available"
    exit 1
}

$refreshResponse = Invoke-PostRequest -Url "$AUTH_SERVICE_URL/api/v1/auth/token" -Body @{
    grant_type = "refresh_token"
    refresh_token = $refreshToken
}

if (-not $refreshResponse.Success) {
    Write-Error "  [FAIL] Token refresh failed: $($refreshResponse.Error)"
    Write-Info "  Status code: $($refreshResponse.StatusCode)"
    exit 1
}

$newAccessToken = $refreshResponse.Response.access_token
$newRefreshToken = $refreshResponse.Response.refresh_token

if (-not $newAccessToken -or -not $newRefreshToken) {
    Write-Error "  [FAIL] No tokens in refresh response"
    exit 1
}

Write-Success "  [OK] Tokens refreshed successfully"
Write-Info "  New access token: $($newAccessToken.Substring(0, [Math]::Min(50, $newAccessToken.Length)))..."
Write-Info "  New refresh token: $($newRefreshToken.Substring(0, [Math]::Min(50, $newRefreshToken.Length)))..."

# Verify token rotation (new refresh token should be different)
if ($newRefreshToken -eq $refreshToken) {
    Write-Error "  [FAIL] Refresh token was not rotated (same token returned)"
    exit 1
}

Write-Success "  [OK] Token rotation verified (new refresh token is different)"
Write-Host ""

# Step 7: Test logout endpoint
Write-Step "Step 7: Testing logout endpoint..."

$logoutResponse = Invoke-PostRequest -Url "$AUTH_SERVICE_URL/api/v1/auth/logout" -Body @{}

if (-not $logoutResponse.Success) {
    Write-Error "  [FAIL] Logout endpoint failed: $($logoutResponse.Error)"
    exit 1
}

Write-Success "  [OK] Logout endpoint works"
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "All tests passed!"
Write-Host ""
Write-Info "Tested endpoints:"
Write-Info "  - GET /api/v1/auth/login"
Write-Info "  - GET /api/v1/auth/callback"
Write-Info "  - POST /api/v1/auth/token"
Write-Info "  - POST /api/v1/auth/logout"
Write-Host ""
Write-Info "OAuth2 flow:"
Write-Info "  1. Login endpoint returns authorization URL"
Write-Info "  2. Authorization URL redirects to mock OAuth"
Write-Info "  3. Mock OAuth redirects back with authorization code"
Write-Info "  4. Callback endpoint exchanges code for JWT tokens"
Write-Info "  5. JWT tokens include user ID, username, and roles"
Write-Info "  6. Token refresh endpoint rotates refresh tokens"
Write-Host ""
