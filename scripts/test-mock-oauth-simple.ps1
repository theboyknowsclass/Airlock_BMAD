# Simple test for Mock OAuth Service
# Uses Python to test OAuth endpoints

param(
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "http://localhost:9000"
)

Write-Host "Testing Mock OAuth Service..." -ForegroundColor Green
Write-Host "  Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host ""

# Test using Python requests (more reliable for redirects)
$testScript = @"
import requests
import sys

base_url = "$BaseUrl"

# Test 1: Health check
print("Test 1: Health check...")
try:
    response = requests.get(f"{base_url}/health")
    response.raise_for_status()
    data = response.json()
    print(f"[OK] Health check passed: {data['status']}")
except Exception as e:
    print(f"[ERROR] Health check failed: {e}")
    sys.exit(1)

# Test 2: Get authorization code
print("Test 2: Get authorization code...")
try:
    auth_url = f"{base_url}/oauth/authorize"
    params = {
        "response_type": "code",
        "client_id": "test-client",
        "redirect_uri": "http://localhost:3000/callback",
        "username": "submitter"
    }
    response = requests.get(auth_url, params=params, allow_redirects=False)
    
    if response.status_code == 302:
        location = response.headers.get("Location", "")
        if "code=" in location:
            auth_code = location.split("code=")[1].split("&")[0]
            print(f"[OK] Authorization code received: {auth_code[:20]}...")
        else:
            print(f"[ERROR] No authorization code in redirect: {location}")
            sys.exit(1)
    else:
        print(f"[ERROR] Unexpected status code: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Authorization failed: {e}")
    sys.exit(1)

# Test 3: Exchange authorization code for tokens
print("Test 3: Exchange authorization code for tokens...")
try:
    token_url = f"{base_url}/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": "http://localhost:3000/callback",
        "client_id": "test-client"
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    token_response = response.json()
    
    if "access_token" in token_response:
        access_token = token_response["access_token"]
        refresh_token = token_response["refresh_token"]
        print(f"[OK] Tokens received")
        print(f"  Access token: {access_token[:30]}...")
        print(f"  Refresh token: {refresh_token[:30]}...")
        print(f"  Expires in: {token_response['expires_in']} seconds")
    else:
        print(f"[ERROR] No access token in response")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Token exchange failed: {e}")
    sys.exit(1)

# Test 4: Get user info
print("Test 4: Get user info...")
try:
    userinfo_url = f"{base_url}/oauth/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(userinfo_url, headers=headers)
    response.raise_for_status()
    user_info = response.json()
    
    print(f"[OK] User info received")
    print(f"  User ID: {user_info['sub']}")
    print(f"  Username: {user_info['username']}")
    print(f"  Email: {user_info['email']}")
    print(f"  Roles: {', '.join(user_info['roles'])}")
except Exception as e:
    print(f"[ERROR] User info failed: {e}")
    sys.exit(1)

# Test 5: Refresh token
print("Test 5: Refresh token...")
try:
    token_url = f"{base_url}/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    token_response = response.json()
    
    if "access_token" in token_response:
        new_access_token = token_response["access_token"]
        new_refresh_token = token_response["refresh_token"]
        print(f"[OK] Tokens refreshed")
        print(f"  New access token: {new_access_token[:30]}...")
        print(f"  New refresh token: {new_refresh_token[:30]}...")
    else:
        print(f"[ERROR] No access token in refresh response")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Token refresh failed: {e}")
    sys.exit(1)

# Test 6: OpenID Connect Discovery
print("Test 6: OpenID Connect Discovery...")
try:
    discovery_url = f"{base_url}/oauth/.well-known/openid-configuration"
    response = requests.get(discovery_url)
    response.raise_for_status()
    discovery = response.json()
    
    print(f"[OK] OpenID Connect Discovery received")
    print(f"  Issuer: {discovery['issuer']}")
    print(f"  Authorization endpoint: {discovery['authorization_endpoint']}")
    print(f"  Token endpoint: {discovery['token_endpoint']}")
    print(f"  UserInfo endpoint: {discovery['userinfo_endpoint']}")
except Exception as e:
    print(f"[ERROR] OpenID Connect Discovery failed: {e}")
    sys.exit(1)

print("")
print("=" * 60)
print("All tests passed!")
print("=" * 60)
print("")
print("Mock OAuth Service is working correctly!")
"@

# Run the test script
try {
    python -c $testScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host "All tests passed!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Tests failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error running test script: $_" -ForegroundColor Red
    Write-Host "Make sure Python and requests library are installed:" -ForegroundColor Yellow
    Write-Host "  pip install requests" -ForegroundColor Gray
    exit 1
}

