# Script to run API Gateway BDD tests (PowerShell)
# Usage: .\scripts\run_tests.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Write-Host "=========================================="
Write-Host "Running API Gateway BDD Tests"
Write-Host "=========================================="
Write-Host ""

# Check if .env.dev exists
$EnvFile = Join-Path $ProjectDir ".env.dev"
if (-not (Test-Path $EnvFile)) {
    Write-Host "Warning: .env.dev file not found in project root"
    Write-Host "Using default test configuration"
} else {
    # Load environment variables from .env.dev
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Set default values
if (-not $env:GATEWAY_URL) { $env:GATEWAY_URL = "http://localhost" }
if (-not $env:API_GATEWAY_PORT) { $env:API_GATEWAY_PORT = "80" }
if (-not $env:JWT_SECRET_KEY) { $env:JWT_SECRET_KEY = "test-secret-key-for-testing-only" }
if (-not $env:JWT_ALGORITHM) { $env:JWT_ALGORITHM = "HS256" }
if (-not $env:JWT_ISSUER) { $env:JWT_ISSUER = "airlock-auth-service" }

Write-Host "Test Configuration:"
Write-Host "  GATEWAY_URL: $env:GATEWAY_URL"
Write-Host "  API_GATEWAY_PORT: $env:API_GATEWAY_PORT"
Write-Host "  JWT_SECRET_KEY: $($env:JWT_SECRET_KEY.Substring(0, [Math]::Min(10, $env:JWT_SECRET_KEY.Length)))..."
Write-Host "  JWT_ALGORITHM: $env:JWT_ALGORITHM"
Write-Host "  JWT_ISSUER: $env:JWT_ISSUER"
Write-Host ""

# Change to API Gateway directory
Set-Location $ScriptDir\..

# Check if gateway is accessible
Write-Host "Checking gateway health..."
$GatewayBaseUrl = $env:GATEWAY_URL
if ($env:API_GATEWAY_PORT -ne "80") {
    $GatewayBaseUrl = "$($env:GATEWAY_URL):$($env:API_GATEWAY_PORT)"
}

$maxAttempts = 30
$attempt = 0
$gatewayReady = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "$GatewayBaseUrl/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "Gateway is ready!"
            $gatewayReady = $true
            break
        }
    } catch {
        # Continue trying
    }
    $attempt++
    Write-Host "Waiting for gateway... ($attempt/$maxAttempts)"
    Start-Sleep -Seconds 1
}

if (-not $gatewayReady) {
    Write-Host "Error: Gateway not accessible at $GatewayBaseUrl"
    Write-Host "Please ensure the gateway is running:"
    Write-Host "  docker-compose up api-gateway"
    exit 1
}

Write-Host ""

# Install test dependencies
Write-Host "Installing test dependencies..."
pip install -q -r requirements-test.txt

# Install shared library
Write-Host "Installing shared library..."
Set-Location "$ProjectDir\shared\python\airlock_common"
pip install -q -e .

# Return to API Gateway directory
Set-Location "$ScriptDir\.."

# Run tests
Write-Host ""
Write-Host "Running BDD tests..."
Write-Host ""
pytest tests/features/ -v --tb=short

Write-Host ""
Write-Host "Tests completed!"

