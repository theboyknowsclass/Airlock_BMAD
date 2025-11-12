# Airlock Production Docker Compose Script
# Runs production compose file only

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "down", "build", "logs", "ps", "restart", "stop", "start")]
    [string]$Command = "up",
    
    [switch]$Build,
    [switch]$Detached,
    [switch]$RemoveOrphans
)

$ErrorActionPreference = "Stop"

# Check if .env.prod exists
if (-not (Test-Path ".env.prod")) {
    Write-Host "Error: .env.prod file not found. Please create it with your production environment variables." -ForegroundColor Red
    exit 1
}

# Build docker-compose command
$composeArgs = @(
    "-f", "docker-compose.prod.yml",
    "--env-file", ".env.prod"
)

switch ($Command) {
    "up" {
        $composeArgs += "up"
        if ($Build) {
            $composeArgs += "--build"
        }
        if ($Detached) {
            $composeArgs += "-d"
        }
    }
    "down" {
        $composeArgs += "down"
        if ($RemoveOrphans) {
            $composeArgs += "--remove-orphans"
        }
    }
    "build" {
        $composeArgs += "build"
    }
    "logs" {
        $composeArgs += "logs", "-f"
    }
    "ps" {
        $composeArgs += "ps"
    }
    "restart" {
        $composeArgs += "restart"
    }
    "stop" {
        $composeArgs += "stop"
    }
    "start" {
        $composeArgs += "start"
    }
}

Write-Host "Running: docker compose $($composeArgs -join ' ')" -ForegroundColor Cyan
docker compose $composeArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Compose command failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

