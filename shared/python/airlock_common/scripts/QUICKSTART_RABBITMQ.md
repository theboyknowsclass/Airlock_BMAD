# RabbitMQ Setup Quick Start

## Prerequisites

1. **Install Python dependencies:**
   ```powershell
   cd shared/python/airlock_common
   pip install -r requirements.txt
   ```

2. **Start RabbitMQ:**
   ```powershell
   # From project root
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d rabbitmq
   ```

## Quick Test (PowerShell)

```powershell
# Test setup
cd shared/python/airlock_common
python scripts/test_rabbitmq_setup.py
```

This will check:
- ✓ Imports work correctly
- ✓ pika is installed
- ✓ Environment variables are set (or using defaults)
- ✓ RabbitMQ connection works

## Check Port Configuration

```powershell
# Check if ports are configured correctly
cd shared/python/airlock_common
python scripts/check_rabbitmq_ports.py
```

This will verify:
- Docker container exposes port 5672 for AMQP
- Environment variables match Docker configuration
- No port mismatches

## Get Credentials from .env.dev

```powershell
# Get credentials from .env.dev file
cd shared/python/airlock_common
.\scripts\get_rabbitmq_credentials.ps1

# Or set them automatically:
.\scripts\get_rabbitmq_credentials.ps1 | Invoke-Expression
```

This will read `.env.dev` and set `RABBITMQ_USER` and `RABBITMQ_PASSWORD` environment variables.

## Initialize RabbitMQ (PowerShell)

```powershell
# Option 1: Get credentials from .env.dev (recommended)
cd shared/python/airlock_common
.\scripts\get_rabbitmq_credentials.ps1 | Invoke-Expression

# Option 2: Set credentials manually
$env:RABBITMQ_HOST = "localhost"
$env:RABBITMQ_PORT = "5672"  # Must be 5672 to match Docker
$env:RABBITMQ_USER = "airlock"  # or value from .env.dev
$env:RABBITMQ_PASSWORD = "airlock"  # or value from .env.dev

# Initialize RabbitMQ
cd shared/python/airlock_common
python scripts/init_rabbitmq.py
```

## Verify in Management UI

1. Open http://localhost:15672 in browser
2. Login with credentials from `.env.dev`
3. Verify exchanges exist:
   - `package.events` (topic)
   - `workflow.events` (topic)
   - `check.events` (topic)
   - `dlx` (direct)
4. Verify dead letter queues exist:
   - `package.events.dlq`
   - `workflow.events.dlq`
   - `check.events.dlq`

## Troubleshooting

### Import Error: `List` is not defined
**Fixed!** The `List` import has been added to `package_request.py`.

### Import Error: `pika` not found
```powershell
pip install -r requirements.txt
```

### Connection Error: Cannot connect to RabbitMQ
1. Check if RabbitMQ is running:
   ```powershell
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev ps rabbitmq
   ```
2. Check if RabbitMQ is ready:
   ```powershell
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev exec rabbitmq rabbitmq-diagnostics ping
   ```
3. Verify environment variables are set correctly
4. Check firewall/port accessibility

### Authentication Error: ACCESS_REFUSED (403)
**Issue:** Credentials don't match RabbitMQ configuration.

**Solution:**
1. Check `.env.dev` for `RABBITMQ_USER` and `RABBITMQ_PASSWORD`
2. Set environment variables to match `.env.dev`:
   ```powershell
   $env:RABBITMQ_USER = "airlock"  # or value from .env.dev
   $env:RABBITMQ_PASSWORD = "airlock"  # or value from .env.dev
   ```
3. Check what credentials RabbitMQ is using:
   ```powershell
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev exec rabbitmq env | findstr RABBITMQ
   ```
4. Or check RabbitMQ container logs:
   ```powershell
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev logs rabbitmq
   ```

### Environment Variables Not Set
The script will use defaults if environment variables are not set:
- `RABBITMQ_HOST` → `localhost`
- `RABBITMQ_PORT` → `5672`
- `RABBITMQ_USER` → `guest`
- `RABBITMQ_PASSWORD` → `guest`

For production, set these in `.env.dev` file.

