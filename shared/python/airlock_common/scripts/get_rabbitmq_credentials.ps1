# Get RabbitMQ credentials from .env.dev file
# This script reads .env.dev and extracts RABBITMQ_USER and RABBITMQ_PASSWORD

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
# Get project root (3 levels up: scripts -> airlock_common -> python -> shared -> project root)
$SharedDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $SharedDir)
$EnvFile = Join-Path $ProjectRoot ".env.dev"

if (-not (Test-Path $EnvFile)) {
    Write-Host "[ERROR] .env.dev file not found at: $EnvFile" -ForegroundColor Red
    Write-Host "  Please create .env.dev file with RabbitMQ credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host "Reading credentials from .env.dev..." -ForegroundColor Green
Write-Host "  File: $EnvFile" -ForegroundColor Gray
Write-Host ""

# Read .env.dev file
$envContent = Get-Content $EnvFile

$rabbitmqUser = $null
$rabbitmqPassword = $null

foreach ($line in $envContent) {
    # Skip comments and empty lines
    if ($line -match "^\s*#" -or $line -match "^\s*$") {
        continue
    }
    
    # Extract RABBITMQ_USER
    if ($line -match "^\s*RABBITMQ_USER\s*=\s*(.+)$") {
        $rabbitmqUser = $matches[1].Trim()
    }
    
    # Extract RABBITMQ_PASSWORD
    if ($line -match "^\s*RABBITMQ_PASSWORD\s*=\s*(.+)$") {
        $rabbitmqPassword = $matches[1].Trim()
    }
}

if ($rabbitmqUser -and $rabbitmqPassword) {
    Write-Host "[OK] Found RabbitMQ credentials in .env.dev:" -ForegroundColor Green
    Write-Host "  RABBITMQ_USER = $rabbitmqUser" -ForegroundColor Gray
    Write-Host "  RABBITMQ_PASSWORD = ***" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To use these credentials, run:" -ForegroundColor Yellow
    Write-Host "  `$env:RABBITMQ_USER = `"$rabbitmqUser`"" -ForegroundColor Cyan
    Write-Host "  `$env:RABBITMQ_PASSWORD = `"$rabbitmqPassword`"" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or set them automatically:" -ForegroundColor Yellow
    Write-Host "  .\scripts\get_rabbitmq_credentials.ps1 | Invoke-Expression" -ForegroundColor Cyan
} else {
    Write-Host "[WARN] RABBITMQ_USER or RABBITMQ_PASSWORD not found in .env.dev" -ForegroundColor Yellow
    Write-Host "  Using defaults: guest/guest" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To set credentials, add to .env.dev:" -ForegroundColor Yellow
    Write-Host "  RABBITMQ_USER=airlock" -ForegroundColor Cyan
    Write-Host "  RABBITMQ_PASSWORD=airlock" -ForegroundColor Cyan
}

# Output PowerShell commands to set environment variables
if ($rabbitmqUser -and $rabbitmqPassword) {
    Write-Host ""
    Write-Host "# Set environment variables (for host connections):" -ForegroundColor Gray
    Write-Output "`$env:RABBITMQ_HOST = `"localhost`"  # Use localhost when connecting from host machine"
    Write-Output "`$env:RABBITMQ_PORT = `"5672`"  # Port 5672 is always exposed"
    Write-Output "`$env:RABBITMQ_USER = `"$rabbitmqUser`""
    Write-Output "`$env:RABBITMQ_PASSWORD = `"$rabbitmqPassword`""
}

