#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run all service tests in the Airlock project

.DESCRIPTION
    This script runs pytest for all services that have test suites configured.
    It supports running tests in parallel or sequentially, and can filter by service name.

.PARAMETER Services
    Optional list of service names to test. If not provided, tests all services with pytest.ini

.PARAMETER Sequential
    Run tests sequentially instead of in parallel (default: parallel)

.PARAMETER Verbose
    Show verbose output from pytest

.PARAMETER Coverage
    Generate coverage reports for each service and a combined report

.EXAMPLE
    .\scripts\run-all-tests.ps1
    Run all service tests in parallel

.EXAMPLE
    .\scripts\run-all-tests.ps1 -Services api-key-service,user-service
    Run tests only for api-key-service and user-service

.EXAMPLE
    .\scripts\run-all-tests.ps1 -Sequential -Verbose
    Run all tests sequentially with verbose output

.EXAMPLE
    .\scripts\run-all-tests.ps1 -Coverage
    Run all tests with coverage reports (HTML and terminal output)
#>

param(
    [string[]]$Services = @(),
    [switch]$Sequential,
    [switch]$Verbose,
    [switch]$Coverage
)

$ErrorActionPreference = "Stop"
$script:RootDir = Split-Path -Parent $PSScriptRoot

# Find all services with pytest.ini
function Get-TestableServices {
    $servicesDir = Join-Path $script:RootDir "services"
    $services = @()
    
    Get-ChildItem -Path $servicesDir -Directory | ForEach-Object {
        $pytestIni = Join-Path $_.FullName "pytest.ini"
        if (Test-Path $pytestIni) {
            $services += $_.Name
        }
    }
    
    return $services
}

# Run tests for a single service
function Invoke-ServiceTests {
    param(
        [string]$ServiceName,
        [bool]$Verbose,
        [bool]$Coverage
    )
    
    $serviceDir = Join-Path $script:RootDir "services" $ServiceName
    
    if (-not (Test-Path $serviceDir)) {
        Write-Warning "Service directory not found: $ServiceName"
        return @{ Service = $ServiceName; Success = $false; Message = "Directory not found" }
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Testing: $ServiceName" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Push-Location $serviceDir
    
    try {
        $pytestArgs = @("pytest", "tests/features/")
        
        if ($Verbose) {
            $pytestArgs += "-v"
        } else {
            $pytestArgs += "-q"
        }
        
        if ($Coverage) {
            $pytestArgs += "--cov=src"
            $pytestArgs += "--cov-report=html:htmlcov"
            $pytestArgs += "--cov-report=term-missing"
            $pytestArgs += "--cov-report=xml"
        }
        
        $pytestArgs += "--tb=short"
        
        $result = & python -m $pytestArgs 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "✓ $ServiceName tests passed" -ForegroundColor Green
            return @{ Service = $ServiceName; Success = $true; Output = $result }
        } else {
            Write-Host "✗ $ServiceName tests failed" -ForegroundColor Red
            return @{ Service = $ServiceName; Success = $false; Output = $result; ExitCode = $exitCode }
        }
    }
    catch {
        Write-Host "✗ Error running tests for $ServiceName : $_" -ForegroundColor Red
        return @{ Service = $ServiceName; Success = $false; Message = $_.Exception.Message }
    }
    finally {
        Pop-Location
    }
}

# Main execution
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "Airlock Service Test Runner" -ForegroundColor Magenta
Write-Host "========================================`n" -ForegroundColor Magenta

# Get list of services to test
$allServices = Get-TestableServices

if ($Services.Count -gt 0) {
    # Filter to requested services
    $servicesToTest = $allServices | Where-Object { $Services -contains $_ }
    
    if ($servicesToTest.Count -eq 0) {
        Write-Warning "No matching services found. Available services: $($allServices -join ', ')"
        exit 1
    }
} else {
    $servicesToTest = $allServices
}

Write-Host "Services to test: $($servicesToTest -join ', ')" -ForegroundColor Yellow
Write-Host "Mode: $(if ($Sequential) { 'Sequential' } else { 'Parallel' })`n" -ForegroundColor Yellow

$results = @()

if ($Sequential) {
    # Run tests sequentially
    foreach ($service in $servicesToTest) {
        $result = Invoke-ServiceTests -ServiceName $service -Verbose $Verbose -Coverage $Coverage
        $results += $result
    }
} else {
    # Run tests in parallel using jobs
    $jobs = @()
    
    foreach ($service in $servicesToTest) {
        $job = Start-Job -ScriptBlock {
            param($RootDir, $ServiceName, $Verbose, $Coverage)
            
            $serviceDir = Join-Path $RootDir "services" $ServiceName
            Push-Location $serviceDir
            
            try {
                $pytestArgs = @("pytest", "tests/features/")
                
                if ($Verbose) {
                    $pytestArgs += "-v"
                } else {
                    $pytestArgs += "-q"
                }
                
                if ($Coverage) {
                    $pytestArgs += "--cov=src"
                    $pytestArgs += "--cov-report=html:htmlcov"
                    $pytestArgs += "--cov-report=term-missing"
                    $pytestArgs += "--cov-report=xml"
                }
                
                $pytestArgs += "--tb=short"
                
                $output = & python -m $pytestArgs 2>&1 | Out-String
                $exitCode = $LASTEXITCODE
                
                return @{
                    Service = $ServiceName
                    Success = ($exitCode -eq 0)
                    Output = $output
                    ExitCode = $exitCode
                }
            }
            catch {
                return @{
                    Service = $ServiceName
                    Success = $false
                    Message = $_.Exception.Message
                }
            }
            finally {
                Pop-Location
            }
        } -ArgumentList $script:RootDir, $service, $Verbose, $Coverage
        
        $jobs += @{ Service = $service; Job = $job }
    }
    
    # Wait for all jobs and collect results
    Write-Host "Running tests in parallel...`n" -ForegroundColor Yellow
    
    foreach ($jobInfo in $jobs) {
        $result = Receive-Job -Job $jobInfo.Job -Wait
        Remove-Job -Job $jobInfo.Job
        
        if ($result.Success) {
            Write-Host "✓ $($jobInfo.Service) tests passed" -ForegroundColor Green
        } else {
            Write-Host "✗ $($jobInfo.Service) tests failed" -ForegroundColor Red
            if ($Verbose -and $result.Output) {
                Write-Host $result.Output
            }
        }
        
        $results += $result
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "Test Summary" -ForegroundColor Magenta
Write-Host "========================================`n" -ForegroundColor Magenta

$passed = @($results | Where-Object { $_.Success }).Count
$failed = @($results | Where-Object { -not $_.Success }).Count
$total = $results.Count

Write-Host "Total: $total | Passed: $passed | Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })

foreach ($result in $results) {
    $status = if ($result.Success) { "✓" } else { "✗" }
    $color = if ($result.Success) { "Green" } else { "Red" }
    Write-Host "  $status $($result.Service)" -ForegroundColor $color
}

if ($failed -gt 0) {
    Write-Host "`nFailed service details:" -ForegroundColor Yellow
    foreach ($result in ($results | Where-Object { -not $_.Success })) {
        Write-Host "`n--- $($result.Service) ---" -ForegroundColor Red
        if ($result.Output) {
            Write-Host $result.Output
        } elseif ($result.Message) {
            Write-Host $result.Message
        }
    }
    exit 1
} else {
    Write-Host "`nAll tests passed! ✓" -ForegroundColor Green
    
    if ($Coverage) {
        Write-Host "`n========================================" -ForegroundColor Magenta
        Write-Host "Coverage Reports Generated" -ForegroundColor Magenta
        Write-Host "========================================`n" -ForegroundColor Magenta
        
        foreach ($result in $results) {
            $serviceDir = Join-Path $script:RootDir "services" $result.Service
            $htmlcovPath = Join-Path $serviceDir "htmlcov" "index.html"
            
            if (Test-Path $htmlcovPath) {
                Write-Host "  $($result.Service): " -NoNewline -ForegroundColor Cyan
                Write-Host $htmlcovPath -ForegroundColor Yellow
            }
        }
        
        Write-Host "`nOpen the HTML files in your browser to view detailed coverage reports." -ForegroundColor Green
    }
    
    exit 0
}

