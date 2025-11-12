# Simple test script for FastAPI services
# Tests if a service can be imported and started

param(
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "api-gateway",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

Write-Host "Testing service: $ServiceName" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Virtual environment not found. Run .\scripts\install-all-requirements.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if service exists
$ServicePath = Join-Path $ProjectRoot "services\$ServiceName\src\main.py"
if (-not (Test-Path $ServicePath)) {
    Write-Host "[ERROR] Service not found: $ServicePath" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Service found: $ServicePath" -ForegroundColor Green
Write-Host ""

# Test 1: Check if uvicorn is installed
Write-Host "Test 1: Checking if uvicorn is installed..." -ForegroundColor Yellow
try {
    & $PythonExe -c "import uvicorn; print('[OK] uvicorn is installed')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] uvicorn is not installed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to check uvicorn: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Check if service can be imported (skip - will test via uvicorn)
Write-Host "Test 2: Skipping import test (will test via uvicorn)..." -ForegroundColor Yellow
Write-Host "[OK] Test 2 skipped" -ForegroundColor Green

# Test 3: Start service and test health endpoint
Write-Host "Test 3: Starting service and testing health endpoint..." -ForegroundColor Yellow
Write-Host "  Starting service on port $Port..." -ForegroundColor Gray
Write-Host "  This may take a few seconds..." -ForegroundColor Gray
Write-Host ""

# Start service in background
$Job = Start-Job -ScriptBlock {
    param($PythonExe, $ProjectRoot, $ServiceName, $Port)
    Set-Location $ProjectRoot
    & $PythonExe -m uvicorn "services.$ServiceName.src.main:app" --host 0.0.0.0 --port $Port
} -ArgumentList $PythonExe, $ProjectRoot, $ServiceName, $Port

# Wait for service to start
Start-Sleep -Seconds 8

# Test health endpoint
try {
    $Response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -UseBasicParsing -ErrorAction Stop
    $Content = $Response.Content | ConvertFrom-Json
    
    Write-Host "[OK] Health endpoint responded!" -ForegroundColor Green
    Write-Host "  Status: $($Content.status)" -ForegroundColor Gray
    Write-Host "  Service: $($Content.service)" -ForegroundColor Gray
    Write-Host "  Timestamp: $($Content.timestamp)" -ForegroundColor Gray
    Write-Host ""
    
    # Test liveness endpoint
    $Response = Invoke-WebRequest -Uri "http://localhost:$Port/health/live" -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Liveness endpoint responded!" -ForegroundColor Green
    
    # Test readiness endpoint
    $Response = Invoke-WebRequest -Uri "http://localhost:$Port/health/ready" -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Readiness endpoint responded!" -ForegroundColor Green
    
} catch {
    Write-Host "[ERROR] Health endpoint test failed: $_" -ForegroundColor Red
    Write-Host "  Service may not have started correctly" -ForegroundColor Yellow
    Write-Host "  Check if port $Port is already in use" -ForegroundColor Yellow
    Stop-Job $Job
    Remove-Job $Job
    exit 1
}

# Stop the service
Write-Host ""
Write-Host "Stopping service..." -ForegroundColor Yellow
Stop-Job $Job
Remove-Job $Job
Write-Host "[OK] Service stopped" -ForegroundColor Green

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "All tests passed!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "Service $ServiceName is working correctly!" -ForegroundColor Green

exit 0

