# Test Mock OAuth Service
# Tests OAuth 2.0 endpoints for mock OAuth service

param(
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "http://localhost:9000",
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "submitter",
    
    [Parameter(Mandatory=$false)]
    [string]$ClientId = "test-client",
    
    [Parameter(Mandatory=$false)]
    [string]$RedirectUri = "http://localhost:3000/callback"
)

$ErrorActionPreference = "Stop"

Write-Host "Testing Mock OAuth Service..." -ForegroundColor Green
Write-Host "  Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host "  Username: $Username" -ForegroundColor Gray
Write-Host "  Client ID: $ClientId" -ForegroundColor Gray
Write-Host "  Redirect URI: $RedirectUri" -ForegroundColor Gray
Write-Host ""

# Test 1: Health check
Write-Host "Test 1: Health check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "[OK] Health check passed: $($content.status)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Get authorization code
Write-Host "Test 2: Get authorization code..." -ForegroundColor Yellow
try {
    # URL encode the redirect_uri
    $encodedRedirectUri = [System.Web.HttpUtility]::UrlEncode($RedirectUri)
    $authUrl = "$BaseUrl/oauth/authorize?response_type=code&client_id=$ClientId&redirect_uri=$encodedRedirectUri&username=$Username"
    
    # Follow redirect (allow 1 redirect) to get the authorization code
    try {
        $response = Invoke-WebRequest -Uri $authUrl -UseBasicParsing -MaximumRedirection 1 -ErrorAction Stop
        $finalUrl = $response.BaseResponse.ResponseUri.ToString()
        
        if ($finalUrl -match "code=([^&]+)") {
            $authCode = $matches[1]
            Write-Host "[OK] Authorization code received: $($authCode.Substring(0, 20))..." -ForegroundColor Green
        } else {
            Write-Host "[ERROR] No authorization code in redirect URL: $finalUrl" -ForegroundColor Red
            exit 1
        }
    } catch {
        # If we get an exception, try to extract the code from the exception
        $errorMessage = $_.Exception.Message
        if ($errorMessage -match "code=([^&]+)") {
            $authCode = $matches[1]
            Write-Host "[OK] Authorization code received from exception: $($authCode.Substring(0, 20))..." -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Failed to extract authorization code: $errorMessage" -ForegroundColor Red
            Write-Host "  Trying alternative method..." -ForegroundColor Gray
            
            # Alternative: Use HttpClient to handle redirects manually
            try {
                $httpClient = New-Object System.Net.Http.HttpClient
                $httpClient.MaxRedirects = 1
                $httpResponse = $httpClient.GetAsync($authUrl).Result
                $finalUrl = $httpResponse.RequestMessage.RequestUri.ToString()
                
                if ($finalUrl -match "code=([^&]+)") {
                    $authCode = $matches[1]
                    Write-Host "[OK] Authorization code received: $($authCode.Substring(0, 20))..." -ForegroundColor Green
                } else {
                    Write-Host "[ERROR] No authorization code in final URL: $finalUrl" -ForegroundColor Red
                    exit 1
                }
            } catch {
                Write-Host "[ERROR] Alternative method also failed: $_" -ForegroundColor Red
                exit 1
            }
        }
    }
} catch {
    Write-Host "[ERROR] Authorization failed: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Exchange authorization code for tokens
Write-Host "Test 3: Exchange authorization code for tokens..." -ForegroundColor Yellow
try {
    $tokenUrl = "$BaseUrl/oauth/token"
    $body = @{
        grant_type = "authorization_code"
        code = $authCode
        redirect_uri = $RedirectUri
        client_id = $ClientId
    }
    
    $response = Invoke-WebRequest -Uri $tokenUrl -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -UseBasicParsing -ErrorAction Stop
    $tokenResponse = $response.Content | ConvertFrom-Json
    
    if ($tokenResponse.access_token) {
        $script:accessToken = $tokenResponse.access_token
        $script:refreshToken = $tokenResponse.refresh_token
        Write-Host "[OK] Tokens received" -ForegroundColor Green
        Write-Host "  Access token: $($script:accessToken.Substring(0, 30))..." -ForegroundColor Gray
        Write-Host "  Refresh token: $($script:refreshToken.Substring(0, 30))..." -ForegroundColor Gray
        Write-Host "  Expires in: $($tokenResponse.expires_in) seconds" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] No access token in response" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Token exchange failed: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "  Response: $responseBody" -ForegroundColor Gray
    }
    exit 1
}

# Test 4: Get user info
Write-Host "Test 4: Get user info..." -ForegroundColor Yellow
try {
    $userInfoUrl = "$BaseUrl/oauth/userinfo"
    $headers = @{
        Authorization = "Bearer $script:accessToken"
    }
    
    $response = Invoke-WebRequest -Uri $userInfoUrl -Headers $headers -UseBasicParsing -ErrorAction Stop
    $userInfo = $response.Content | ConvertFrom-Json
    
    Write-Host "[OK] User info received" -ForegroundColor Green
    Write-Host "  User ID: $($userInfo.sub)" -ForegroundColor Gray
    Write-Host "  Username: $($userInfo.username)" -ForegroundColor Gray
    Write-Host "  Email: $($userInfo.email)" -ForegroundColor Gray
    Write-Host "  Roles: $($userInfo.roles -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] User info failed: $_" -ForegroundColor Red
    exit 1
}

# Test 5: Refresh token
Write-Host "Test 5: Refresh token..." -ForegroundColor Yellow
try {
    $tokenUrl = "$BaseUrl/oauth/token"
    $body = @{
        grant_type = "refresh_token"
        refresh_token = $script:refreshToken
    }
    
    $response = Invoke-WebRequest -Uri $tokenUrl -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -UseBasicParsing -ErrorAction Stop
    $tokenResponse = $response.Content | ConvertFrom-Json
    
    if ($tokenResponse.access_token) {
        $newAccessToken = $tokenResponse.access_token
        $newRefreshToken = $tokenResponse.refresh_token
        Write-Host "[OK] Tokens refreshed" -ForegroundColor Green
        Write-Host "  New access token: $($newAccessToken.Substring(0, 30))..." -ForegroundColor Gray
        Write-Host "  New refresh token: $($newRefreshToken.Substring(0, 30))..." -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] No access token in refresh response" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Token refresh failed: $_" -ForegroundColor Red
    exit 1
}

# Test 6: OpenID Connect Discovery
Write-Host "Test 6: OpenID Connect Discovery..." -ForegroundColor Yellow
try {
    $discoveryUrl = "$BaseUrl/oauth/.well-known/openid-configuration"
    $response = Invoke-WebRequest -Uri $discoveryUrl -UseBasicParsing -ErrorAction Stop
    $discovery = $response.Content | ConvertFrom-Json
    
    Write-Host "[OK] OpenID Connect Discovery received" -ForegroundColor Green
    Write-Host "  Issuer: $($discovery.issuer)" -ForegroundColor Gray
    Write-Host "  Authorization endpoint: $($discovery.authorization_endpoint)" -ForegroundColor Gray
    Write-Host "  Token endpoint: $($discovery.token_endpoint)" -ForegroundColor Gray
    Write-Host "  UserInfo endpoint: $($discovery.userinfo_endpoint)" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] OpenID Connect Discovery failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "All tests passed!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "Mock OAuth Service is working correctly!" -ForegroundColor Green

exit 0
