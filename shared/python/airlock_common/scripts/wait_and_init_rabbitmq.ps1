# RabbitMQ initialization script
# Waits for RabbitMQ to be ready, then configures exchanges and queues

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SharedDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Add shared directory to Python path
$env:PYTHONPATH = "$SharedDir;$env:PYTHONPATH"

# Run initialization script
python "$ScriptDir\init_rabbitmq.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: RabbitMQ initialization failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

