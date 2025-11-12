# Setup Frontend React Application
# This script initializes a React + TypeScript application with Vite and all required dependencies

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "Setting up Frontend React Application..." -ForegroundColor Green
Write-Host "  Project root: $ProjectRoot" -ForegroundColor Gray
Write-Host "  Frontend directory: $FrontendDir" -ForegroundColor Gray
Write-Host ""

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 24.x or later." -ForegroundColor Red
    exit 1
}

# Check if npm is available
try {
    $npmVersion = npm --version 2>&1
    Write-Host "[OK] npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] npm not found. Please install npm." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if frontend directory exists
if (-not (Test-Path $FrontendDir)) {
    Write-Host "Creating frontend directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $FrontendDir -Force | Out-Null
    Write-Host "[OK] Frontend directory created" -ForegroundColor Green
}

# Change to frontend directory
Set-Location $FrontendDir

# Check if package.json exists and has dependencies
$PackageJsonPath = Join-Path $FrontendDir "package.json"
$HasDependencies = $false

if (Test-Path $PackageJsonPath) {
    $packageJson = Get-Content $PackageJsonPath | ConvertFrom-Json
    if ($packageJson.dependencies -and ($packageJson.dependencies.PSObject.Properties.Count -gt 0)) {
        $HasDependencies = $true
    }
}

# Initialize Vite React + TypeScript app if needed
if (-not (Test-Path (Join-Path $FrontendDir "vite.config.ts")) -and -not $HasDependencies) {
    Write-Host "Initializing Vite React + TypeScript application..." -ForegroundColor Yellow
    Write-Host "  This may take a few minutes..." -ForegroundColor Gray
    
    # Check if src directory has files
    $SrcDir = Join-Path $FrontendDir "src"
    if (Test-Path $SrcDir) {
        $srcFiles = Get-ChildItem -Path $SrcDir -Recurse -File
        if ($srcFiles.Count -eq 0) {
            Write-Host "  src directory is empty, initializing Vite app..." -ForegroundColor Gray
            # Initialize Vite app (non-interactive)
            npm create vite@latest . -- --template react-ts --yes
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[ERROR] Failed to initialize Vite app" -ForegroundColor Red
                exit 1
            }
            Write-Host "[OK] Vite app initialized" -ForegroundColor Green
        } else {
            Write-Host "  src directory has files, skipping Vite initialization" -ForegroundColor Gray
        }
    } else {
        Write-Host "  src directory does not exist, initializing Vite app..." -ForegroundColor Gray
        # Initialize Vite app (non-interactive)
        npm create vite@latest . -- --template react-ts --yes
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to initialize Vite app" -ForegroundColor Red
            exit 1
        }
        Write-Host "[OK] Vite app initialized" -ForegroundColor Green
    }
} else {
    Write-Host "[OK] Vite app already initialized" -ForegroundColor Green
}

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take several minutes..." -ForegroundColor Gray
Write-Host ""

# Core dependencies
$CoreDependencies = @(
    "react@^19.2.0",
    "react-dom@^19.2.0",
    "@mui/material@latest",
    "@mui/icons-material@latest",
    "@emotion/react@latest",
    "@emotion/styled@latest",
    "@tanstack/react-router@latest",
    "@tanstack/react-query@latest",
    "@tanstack/react-table@latest",
    "zustand@latest",
    "react-hook-form@latest",
    "axios@latest",
    "@tanstack/material-react-table@latest"
)

# Dev dependencies
$DevDependencies = @(
    "@types/react@^19.2.0",
    "@types/react-dom@^19.2.0",
    "@vitejs/plugin-react@latest",
    "typescript@latest",
    "vite@latest",
    "@storybook/react@latest",
    "@storybook/react-vite@latest",
    "@storybook/addon-essentials@latest",
    "@storybook/addon-interactions@latest",
    "@storybook/addon-a11y@latest",
    "@storybook/test@latest",
    "@cucumber/cucumber@latest",
    "@testing-library/react@latest",
    "@testing-library/jest-dom@latest",
    "@testing-library/user-event@latest",
    "msw@latest",
    "@axe-core/react@latest",
    "axe-core@latest",
    "vitest@latest",
    "@vitest/ui@latest",
    "jsdom@latest"
)

# Install core dependencies
Write-Host "Installing core dependencies..." -ForegroundColor Yellow
foreach ($dep in $CoreDependencies) {
    Write-Host "  Installing $dep..." -ForegroundColor Gray
    npm install $dep --save
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Failed to install $dep" -ForegroundColor Yellow
    }
}

Write-Host ""

# Install dev dependencies
Write-Host "Installing dev dependencies..." -ForegroundColor Yellow
foreach ($dep in $DevDependencies) {
    Write-Host "  Installing $dep..." -ForegroundColor Gray
    npm install $dep --save-dev
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Failed to install $dep" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
if (Test-Path (Join-Path $FrontendDir "node_modules")) {
    Write-Host "[OK] node_modules directory exists" -ForegroundColor Green
} else {
    Write-Host "[ERROR] node_modules directory not found" -ForegroundColor Red
    exit 1
}

if (Test-Path (Join-Path $FrontendDir "package.json")) {
    Write-Host "[OK] package.json exists" -ForegroundColor Green
} else {
    Write-Host "[ERROR] package.json not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Frontend Setup Complete!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Configure TypeScript with strict mode" -ForegroundColor Gray
Write-Host "  2. Set up path aliases in vite.config.ts" -ForegroundColor Gray
Write-Host "  3. Configure Material UI theme" -ForegroundColor Gray
Write-Host "  4. Set up TanStack Router" -ForegroundColor Gray
Write-Host "  5. Set up React Query" -ForegroundColor Gray
Write-Host "  6. Set up Zustand" -ForegroundColor Gray
Write-Host "  7. Configure Axios" -ForegroundColor Gray
Write-Host "  8. Set up Storybook" -ForegroundColor Gray
Write-Host "  9. Set up BDD testing (Cucumber.js)" -ForegroundColor Gray
Write-Host "  10. Set up accessibility testing (axe-core)" -ForegroundColor Gray
Write-Host "  11. Create atomic design pattern structure" -ForegroundColor Gray
Write-Host "  12. Test application: npm run dev" -ForegroundColor Gray
Write-Host ""

exit 0

