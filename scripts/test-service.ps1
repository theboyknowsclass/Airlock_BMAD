# Test a FastAPI service
# Usage: .\scripts\test-service.ps1 -ServiceName api-gateway -Port 8000

param(
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "api-gateway",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8000,
    
    [Parameter(Mandatory=$false)]
    [switch]$QuickTest
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"

Write-Host "Testing service: $ServiceName" -ForegroundColor Green
Write-Host "  Port: $Port" -ForegroundColor Gray
Write-Host ""

# Activate virtual environment
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Virtual environment not found. Run .\scripts\install-all-requirements.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if service directory exists
$ServiceDir = Join-Path $ProjectRoot "services\$ServiceName"
if (-not (Test-Path $ServiceDir)) {
    Write-Host "[ERROR] Service directory not found: $ServiceDir" -ForegroundColor Red
    exit 1
}

# Check if main.py exists
$MainFile = Join-Path $ServiceDir "src\main.py"
if (-not (Test-Path $MainFile)) {
    Write-Host "[ERROR] main.py not found: $MainFile" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Service directory found: $ServiceDir" -ForegroundColor Green
Write-Host "[OK] main.py found: $MainFile" -ForegroundColor Green
Write-Host ""

# Quick test: Check if uvicorn can import the app
if ($QuickTest) {
    Write-Host "Running quick test (import check)..." -ForegroundColor Yellow
    $ServiceSrcDir = Join-Path $ServiceDir "src"
    
    try {
        # Test if uvicorn can import the app
        Push-Location $ServiceSrcDir
        $env:PYTHONPATH = $ServiceSrcDir
        python -c "import uvicorn; from main import app; print('[OK] App can be imported')"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Import test failed" -ForegroundColor Red
            Pop-Location
            exit 1
        }
        Pop-Location
        Write-Host "[OK] Quick test passed!" -ForegroundColor Green
        exit 0
    } catch {
        Write-Host "[ERROR] Quick test failed: $_" -ForegroundColor Red
        Pop-Location
        exit 1
    }
}

# Full test: Start service and test health endpoint
Write-Host "Starting service on port $Port..." -ForegroundColor Yellow
Write-Host "  Service will start in background" -ForegroundColor Gray
Write-Host "  Health check URL: http://localhost:$Port/health" -ForegroundColor Gray
Write-Host ""
Write-Host "To test the service:" -ForegroundColor Cyan
Write-Host "  1. Wait for service to start (5-10 seconds)" -ForegroundColor Gray
Write-Host "  2. Open: http://localhost:$Port/health" -ForegroundColor Gray
Write-Host "  3. Or run: curl http://localhost:$Port/health" -ForegroundColor Gray
Write-Host "  4. Or run: Invoke-WebRequest -Uri http://localhost:$Port/health" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop the service: Press Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Start the service
$ServiceSrcDir = Join-Path $ServiceDir "src"
Push-Location $ServiceSrcDir

try {
    $env:PYTHONPATH = $ServiceSrcDir
    uvicorn main:app --host 0.0.0.0 --port $Port --reload
} catch {
    Write-Host "[ERROR] Failed to start service: $_" -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}
