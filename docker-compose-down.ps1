# Docker Compose Tear Down Script (PowerShell)
# Stops and removes all containers, networks, and optionally volumes

param(
    [switch]$Volumes,
    [switch]$Images
)

Write-Host "========================================"
Write-Host "Docker Compose Tear Down"
Write-Host "========================================"
Write-Host ""

if ($Volumes) {
    Write-Host "⚠️  WARNING: This will remove volumes (data will be lost)!" -ForegroundColor Yellow
    Write-Host ""
}

if ($Images) {
    Write-Host "⚠️  WARNING: This will remove images!" -ForegroundColor Yellow
    Write-Host ""
}

$confirm = Read-Host "Continue? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Aborted."
    exit 0
}

Write-Host ""
Write-Host "Stopping and removing containers..."

# Stop and remove containers, networks
$composeArgs = @(
    "-f", "docker-compose.prod.yml",
    "-f", "docker-compose.dev.yml",
    "--env-file", ".env.dev",
    "down"
)

if ($Volumes) {
    $composeArgs += "--volumes"
}

if ($Images) {
    $composeArgs += "--rmi", "all"
}

docker compose $composeArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Containers stopped and removed successfully!" -ForegroundColor Green
    
    if ($Volumes) {
        Write-Host "✅ Volumes removed" -ForegroundColor Green
    }
    
    if ($Images) {
        Write-Host "✅ Images removed" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "❌ Error during tear down" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Cleanup complete!"

