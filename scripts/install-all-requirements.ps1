# Install all requirements.txt files from all services into a local .venv
# This script creates a virtual environment and installs all dependencies

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"

Write-Host "Installing all service requirements into .venv..." -ForegroundColor Green
Write-Host "  Project root: $ProjectRoot" -ForegroundColor Gray
Write-Host "  Virtual environment: $VenvPath" -ForegroundColor Gray
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.12 or later." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Virtual environment activation script not found" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to upgrade pip" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Pip upgraded" -ForegroundColor Green
Write-Host ""

# Find all requirements.txt files
$ServicesDir = Join-Path $ProjectRoot "services"
$RequirementsFiles = @()

# Find requirements.txt in services
if (Test-Path $ServicesDir) {
    $RequirementsFiles += Get-ChildItem -Path $ServicesDir -Filter "requirements.txt" -Recurse -File
}

# Find requirements.txt in shared/python/airlock_common
$SharedDir = Join-Path $ProjectRoot "shared\python\airlock_common"
if (Test-Path $SharedDir) {
    $SharedRequirements = Join-Path $SharedDir "requirements.txt"
    if (Test-Path $SharedRequirements) {
        $RequirementsFiles += Get-Item $SharedRequirements
    }
}

Write-Host "Found $($RequirementsFiles.Count) requirements.txt files:" -ForegroundColor Green
foreach ($reqFile in $RequirementsFiles) {
    $relativePath = $reqFile.FullName.Replace($ProjectRoot, "").TrimStart("\")
    Write-Host "  - $relativePath" -ForegroundColor Gray
}
Write-Host ""

# Install requirements from each file
$FailedFiles = @()
foreach ($reqFile in $RequirementsFiles) {
    $relativePath = $reqFile.FullName.Replace($ProjectRoot, "").TrimStart("\")
    Write-Host "Installing from $relativePath..." -ForegroundColor Yellow
    
    python -m pip install -r $reqFile.FullName --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Installed from $relativePath" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to install from $relativePath" -ForegroundColor Red
        $FailedFiles += $relativePath
    }
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Installation Summary" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

if ($FailedFiles.Count -eq 0) {
    Write-Host "[OK] All requirements installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Virtual environment: $VenvPath" -ForegroundColor Gray
    Write-Host "To activate: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "To deactivate: deactivate" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "[ERROR] Failed to install requirements from:" -ForegroundColor Red
    foreach ($file in $FailedFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    exit 1
}

