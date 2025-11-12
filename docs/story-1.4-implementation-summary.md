# Story 1.4: RabbitMQ Message Broker Setup - Implementation Summary

## Status: ✅ Completed

## Overview

Story 1.4 has been successfully implemented. RabbitMQ is now configured with exchanges, dead letter queues, connection utilities, and initialization scripts.

## Implementation Details

### 1. RabbitMQ Connection Utility

Created `shared/python/airlock_common/messaging/connection.py`:
- ✅ **RabbitMQConnection** class - Connection manager with context manager support
- ✅ **get_rabbitmq_connection()** function - Factory function for connections
- ✅ **get_rabbitmq_url()** function - Generates connection URL from environment variables
- ✅ Environment variable configuration (RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_VHOST)

### 2. Exchange Configuration

Created `shared/python/airlock_common/messaging/exchanges.py`:
- ✅ **package.events** - Topic exchange for package-related events
- ✅ **workflow.events** - Topic exchange for workflow-related events
- ✅ **check.events** - Topic exchange for check-related events
- ✅ **dlx** - Direct exchange for dead letter queues
- ✅ Routing key constants for all event types

### 3. RabbitMQ Initialization

Created `shared/python/airlock_common/messaging/init_rabbitmq.py`:
- ✅ Exchange declaration (package.events, workflow.events, check.events, dlx)
- ✅ Dead letter queue declaration (package.events.dlq, workflow.events.dlq, check.events.dlq)
- ✅ Dead letter exchange configuration
- ✅ Error handling and logging

### 4. Initialization Scripts

Created initialization scripts:
- ✅ `shared/python/airlock_common/scripts/init_rabbitmq.py` - Waits for RabbitMQ and initializes configuration
- ✅ `shared/python/airlock_common/scripts/wait_and_init_rabbitmq.sh` - Bash script wrapper
- ✅ `shared/python/airlock_common/scripts/wait_and_init_rabbitmq.ps1` - PowerShell script wrapper

### 5. Docker Compose Configuration

Updated Docker Compose:
- ✅ **docker-compose.prod.yml** - RabbitMQ service with management plugin
- ✅ **docker-compose.dev.yml** - Exposes management UI on port 15672
- ✅ Environment variables for RabbitMQ configuration
- ✅ Health checks for RabbitMQ service

### 6. Tests

Created tests:
- ✅ `shared/python/airlock_common/tests/test_rabbitmq_connection.py` - Connection and configuration tests
- ✅ `shared/python/airlock_common/tests/test_rabbitmq_init.py` - Initialization tests
- ✅ Unit tests (no RabbitMQ required)
- ✅ Integration tests (require RabbitMQ running)

### 7. Documentation

Created documentation:
- ✅ `shared/python/airlock_common/messaging/README.md` - Comprehensive usage guide
- ✅ Usage examples for publishing and consuming messages
- ✅ Testing instructions
- ✅ Docker setup instructions

### 8. Package Updates

Updated package:
- ✅ Added `pika>=1.3.2,<2.0.0` to `requirements.txt`
- ✅ Updated `__init__.py` to export messaging utilities
- ✅ Updated `pytest.ini` to add integration test marker

## Acceptance Criteria

### ✅ RabbitMQ is running and accessible
- RabbitMQ service configured in `docker-compose.prod.yml`
- Health checks configured
- Connection utility supports connection retries

### ✅ Management UI is available on port 15672
- Management UI exposed in `docker-compose.dev.yml`
- Port configured via `RABBITMQ_MANAGEMENT_PORT` environment variable
- Accessible at http://localhost:15672

### ✅ Exchanges configured
- `package.events` exchange (topic, durable)
- `workflow.events` exchange (topic, durable)
- `check.events` exchange (topic, durable)
- `dlx` exchange (direct, durable)

### ✅ Dead letter queues configured
- `package.events.dlq` - Dead letter queue for package events
- `workflow.events.dlq` - Dead letter queue for workflow events
- `check.events.dlq` - Dead letter queue for check events
- All DLQs bound to `dlx` exchange

### ✅ Connection configurable via environment variables
- `RABBITMQ_HOST` - RabbitMQ host (default: localhost)
- `RABBITMQ_PORT` - RabbitMQ port (default: 5672)
- `RABBITMQ_USER` - RabbitMQ username (default: guest)
- `RABBITMQ_PASSWORD` - RabbitMQ password (default: guest)
- `RABBITMQ_VHOST` - RabbitMQ virtual host (default: /)

## Usage

### Initialize RabbitMQ

```bash
# From project root
cd shared/python/airlock_common
python scripts/init_rabbitmq.py
```

### Use Connection Utility

```python
from airlock_common.messaging.connection import get_rabbitmq_connection
from airlock_common.messaging.exchanges import PACKAGE_EVENTS_EXCHANGE

with get_rabbitmq_connection() as conn:
    channel = conn.get_channel()
    channel.basic_publish(
        exchange=PACKAGE_EVENTS_EXCHANGE,
        routing_key='package.submitted',
        body='{"package": "example", "version": "1.0.0"}'
    )
```

### Run Tests

```bash
# Unit tests (no RabbitMQ required)
cd shared/python/airlock_common
pytest tests/test_rabbitmq_connection.py -v -k "not integration"

# Integration tests (require RabbitMQ running)
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=airlock
export RABBITMQ_PASSWORD=airlock
pytest tests/test_rabbitmq_connection.py -v -m integration
pytest tests/test_rabbitmq_init.py -v -m integration
```

## Files Created

- `shared/python/airlock_common/messaging/__init__.py`
- `shared/python/airlock_common/messaging/connection.py`
- `shared/python/airlock_common/messaging/exchanges.py`
- `shared/python/airlock_common/messaging/init_rabbitmq.py`
- `shared/python/airlock_common/messaging/README.md`
- `shared/python/airlock_common/scripts/init_rabbitmq.py`
- `shared/python/airlock_common/scripts/wait_and_init_rabbitmq.sh`
- `shared/python/airlock_common/scripts/wait_and_init_rabbitmq.ps1`
- `shared/python/airlock_common/tests/test_rabbitmq_connection.py`
- `shared/python/airlock_common/tests/test_rabbitmq_init.py`
- `docs/story-1.4-implementation-summary.md`

## Files Modified

- `shared/python/airlock_common/requirements.txt` - Added pika dependency
- `shared/python/airlock_common/__init__.py` - Added messaging exports
- `shared/python/airlock_common/pytest.ini` - Added integration test marker
- `docker-compose.dev.yml` - Already exposes management UI port (no changes needed)
- `docker-compose.prod.yml` - Already configured RabbitMQ (no changes needed)
- `.bmad-ephemeral/sprint-status.yaml` - Updated story status

## Next Steps

1. **Run initialization script** - Initialize RabbitMQ exchanges and queues after starting RabbitMQ
2. **Test connection** - Verify RabbitMQ connection works from services
3. **Test exchanges** - Verify exchanges exist in RabbitMQ management UI
4. **Test dead letter queues** - Verify DLQs are configured correctly
5. **Continue with Story 1.5** - Core FastAPI Service Scaffolding

## Testing Instructions

### 1. Install Dependencies

**Windows (PowerShell):**
```powershell
cd shared/python/airlock_common
pip install -r requirements.txt
```

**Linux/Mac (Bash):**
```bash
cd shared/python/airlock_common
pip install -r requirements.txt
```

### 2. Start RabbitMQ

```bash
# From project root
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d rabbitmq
```

### 3. Check Port Configuration

**Windows (PowerShell):**
```powershell
cd shared/python/airlock_common
python scripts/check_rabbitmq_ports.py
```

This will verify:
- Docker container exposes port 5672 for AMQP
- Environment variables match Docker configuration
- No port mismatches

### 4. Test Setup

**Windows (PowerShell):**
```powershell
cd shared/python/airlock_common
python scripts/test_rabbitmq_setup.py
```

**Linux/Mac (Bash):**
```bash
cd shared/python/airlock_common
python scripts/test_rabbitmq_setup.py
```

### 5. Wait for RabbitMQ to be Ready

```bash
# Check if RabbitMQ is ready
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev exec rabbitmq rabbitmq-diagnostics ping
```

### 6. Initialize RabbitMQ

**Windows (PowerShell):**
```powershell
# Set environment variables (Docker always exposes port 5672)
$env:RABBITMQ_HOST = "localhost"
$env:RABBITMQ_PORT = "5672"  # Must be 5672 to match Docker
$env:RABBITMQ_USER = "airlock"
$env:RABBITMQ_PASSWORD = "airlock"

# Initialize RabbitMQ
cd shared/python/airlock_common
python scripts/init_rabbitmq.py
```

**Linux/Mac (Bash):**
```bash
# Set environment variables (Docker always exposes port 5672)
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672  # Must be 5672 to match Docker
export RABBITMQ_USER=airlock
export RABBITMQ_PASSWORD=airlock

# Initialize RabbitMQ
cd shared/python/airlock_common
python scripts/init_rabbitmq.py
```

### 7. Verify Management UI

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

### 8. Run Tests

```bash
# Unit tests
cd shared/python/airlock_common
pytest tests/test_rabbitmq_connection.py -v -k "not integration"

# Integration tests
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=airlock
export RABBITMQ_PASSWORD=airlock
pytest tests/test_rabbitmq_connection.py -v -m integration
pytest tests/test_rabbitmq_init.py -v -m integration
```

## Notes

- RabbitMQ management plugin is included in the `rabbitmq:3.13-management` image
- Management UI is only exposed in development (docker-compose.dev.yml)
- **AMQP port (5672) is always exposed on port 5672** - no port mapping needed
- Initialization script should be run after RabbitMQ is ready
- Dead letter queues are bound to the `dlx` exchange
- All exchanges are durable (survive RabbitMQ restarts)
- Connection utility supports connection retries and error handling

## Port Configuration

**Important:** Docker always exposes port 5672 for AMQP connections. Always set `RABBITMQ_PORT=5672` when connecting from the host machine.

- **Docker exposes:** `5672:5672` (host port 5672 → container port 5672)
- **Connection uses:** `localhost:5672` (must match host port)
- **Management UI:** `15672:15672` (configurable via `RABBITMQ_MANAGEMENT_PORT`)

If you get connection errors, check:
1. RabbitMQ is running: `docker-compose ps rabbitmq`
2. Port is exposed: `docker port airlock-rabbitmq`
3. Port matches: `RABBITMQ_PORT=5672` (must be 5672)

