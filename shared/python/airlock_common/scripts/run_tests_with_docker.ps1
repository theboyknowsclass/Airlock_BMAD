# Script to run tests against Docker PostgreSQL
# Usage: .\scripts\run_tests_with_docker.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir)))

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running Tests with Docker PostgreSQL" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env.dev exists
$EnvFile = Join-Path $ProjectDir ".env.dev"
if (-not (Test-Path $EnvFile)) {
    Write-Host "Error: .env.dev file not found in project root" -ForegroundColor Red
    Write-Host "Please create .env.dev with database configuration" -ForegroundColor Yellow
    exit 1
}

# Load environment variables from .env.dev
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Set default values if not set
if (-not $env:POSTGRES_HOST) { $env:POSTGRES_HOST = "localhost" }
if (-not $env:POSTGRES_PORT) { $env:POSTGRES_PORT = "5432" }
if (-not $env:POSTGRES_DB) { $env:POSTGRES_DB = "airlock" }
if (-not $env:POSTGRES_USER) { $env:POSTGRES_USER = "airlock" }
if (-not $env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD = "airlock" }

Write-Host "Database Configuration:" -ForegroundColor Green
Write-Host "  POSTGRES_HOST: $env:POSTGRES_HOST"
Write-Host "  POSTGRES_PORT: $env:POSTGRES_PORT"
Write-Host "  POSTGRES_DB: $env:POSTGRES_DB"
Write-Host "  POSTGRES_USER: $env:POSTGRES_USER"
Write-Host ""

# Change to project directory
Set-Location $ProjectDir

# Start PostgreSQL in background
Write-Host "Starting PostgreSQL..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d postgres

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Green
$timeout = 60
$counter = 0
$ready = $false

while (-not $ready -and $counter -lt $timeout) {
    Start-Sleep -Seconds 1
    $counter++
    
    try {
        $result = docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev exec -T postgres pg_isready -U $env:POSTGRES_USER 2>&1
        if ($LASTEXITCODE -eq 0) {
            $ready = $true
        }
    } catch {
        # Continue waiting
    }
}

if (-not $ready) {
    Write-Host "Error: PostgreSQL did not become ready within $timeout seconds" -ForegroundColor Red
    docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev logs postgres
    exit 1
}

Write-Host "PostgreSQL is ready!" -ForegroundColor Green
Write-Host ""

# Run tests
Write-Host "Running tests..." -ForegroundColor Green
Set-Location "$ProjectDir\shared\python"
python -m pytest airlock_common/tests/ -v

# Capture exit code
$TestExitCode = $LASTEXITCODE

# Stop PostgreSQL (optional - comment out to keep running)
Write-Host ""
Write-Host "Stopping PostgreSQL..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev stop postgres

# Exit with test exit code
exit $TestExitCode

