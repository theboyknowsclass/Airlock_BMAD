# Script to create initial database migration
# Usage: .\scripts\create_initial_migration.ps1

$ErrorActionPreference = "Stop"

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

# Change to project directory
Set-Location $ProjectDir

# Check if alembic is installed
try {
    $null = Get-Command alembic -ErrorAction Stop
} catch {
    Write-Host "Error: alembic is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "  pip install alembic" -ForegroundColor Yellow
    exit 1
}

# Create initial migration
Write-Host "Creating initial migration..." -ForegroundColor Green
alembic revision --autogenerate -m "Initial schema"

Write-Host "Migration created successfully!" -ForegroundColor Green
Write-Host "To apply the migration, run: alembic upgrade head" -ForegroundColor Yellow

