# Airlock Development Rebuild Script
# Rebuilds services when code changes - useful during development

param(
    [Parameter(Position=0)]
    [string]$Service = "",
    
    [switch]$NoCache
)

$ErrorActionPreference = "Stop"

# Check if .env.dev exists
if (-not (Test-Path ".env.dev")) {
    Write-Host "Error: .env.dev file not found. Please create it with your development environment variables." -ForegroundColor Red
    exit 1
}

# Build docker-compose command
$composeArgs = @(
    "-f", "docker-compose.prod.yml",
    "-f", "docker-compose.dev.yml",
    "--env-file", ".env.dev"
)

if ($Service) {
    Write-Host "Rebuilding service: $Service" -ForegroundColor Cyan
    $composeArgs += "build"
    if ($NoCache) {
        $composeArgs += "--no-cache"
    }
    $composeArgs += $Service
} else {
    Write-Host "Rebuilding all services..." -ForegroundColor Cyan
    $composeArgs += "build"
    if ($NoCache) {
        $composeArgs += "--no-cache"
    }
}

Write-Host "Running: docker compose $($composeArgs -join ' ')" -ForegroundColor Cyan
docker compose $composeArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Compose build failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

# After rebuild, restart the service(s)
if ($Service) {
    Write-Host "`nRestarting service: $Service" -ForegroundColor Cyan
    docker compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev restart $Service
} else {
    Write-Host "`nRestarting all services..." -ForegroundColor Cyan
    docker compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev restart
}

Write-Host "`nRebuild complete!" -ForegroundColor Green

