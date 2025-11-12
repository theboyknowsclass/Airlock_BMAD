# RabbitMQ Port Configuration

## Ports Explained

RabbitMQ uses two ports:

1. **Port 5672** (AMQP) - For client connections (messaging)
   - This is the port your Python scripts use to connect to RabbitMQ
   - Used by pika library to publish/consume messages

2. **Port 15672** (Management UI) - For web interface
   - This is the port for the RabbitMQ management web UI
   - Used to view exchanges, queues, connections, etc.

## Docker Compose Configuration

### Production (`docker-compose.prod.yml`)
- **No ports exposed** - Services communicate via Docker network
- Services use `RABBITMQ_HOST=rabbitmq` (service name)
- Services use `RABBITMQ_PORT=5672` (container port)

### Development (`docker-compose.dev.yml`)
- **Port 5672 exposed** - For host machine connections
  - Mapping: `${RABBITMQ_PORT:-5672}:5672`
  - Host port: From `RABBITMQ_PORT` env var (default: 5672)
  - Container port: 5672 (always)
  
- **Port 15672 exposed** - For management UI
  - Mapping: `${RABBITMQ_MANAGEMENT_PORT:-15672}:15672`
  - Host port: From `RABBITMQ_MANAGEMENT_PORT` env var (default: 15672)
  - Container port: 15672 (always)

## Connection from Host Machine

When running scripts from the host machine (like `init_rabbitmq.py`):

```powershell
# Set environment variables for HOST ports
$env:RABBITMQ_HOST = "localhost"
$env:RABBITMQ_PORT = "5672"  # Must match the exposed host port
$env:RABBITMQ_USER = "airlock"
$env:RABBITMQ_PASSWORD = "airlock"

# Connect to RabbitMQ
python scripts/init_rabbitmq.py
```

## Connection from Docker Services

When services run inside Docker:

```yaml
# In docker-compose.prod.yml
environment:
  - RABBITMQ_HOST=rabbitmq  # Service name (Docker network)
  - RABBITMQ_PORT=5672      # Container port (not host port)
  - RABBITMQ_USER=${RABBITMQ_USER}
  - RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
```

## Troubleshooting

### Port Already in Use

If port 5672 is already in use on your host machine:

1. **Change host port in .env.dev:**
   ```bash
   RABBITMQ_PORT=5673
   ```

2. **Update docker-compose.dev.yml:**
   ```yaml
   rabbitmq:
     ports:
       - "${RABBITMQ_PORT:-5672}:5672"
   ```

3. **Update connection script:**
   ```powershell
   $env:RABBITMQ_PORT = "5673"  # Match the host port
   ```

### Connection Refused

If you get "connection refused" errors:

1. **Check if port is exposed:**
   ```powershell
   docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev ps rabbitmq
   ```

2. **Check port mapping:**
   ```powershell
   docker port airlock-rabbitmq
   ```
   Should show:
   - `5672/tcp -> 0.0.0.0:5672` (or your configured host port)
   - `15672/tcp -> 0.0.0.0:15672` (or your configured host port)

3. **Verify environment variables:**
   ```powershell
   $env:RABBITMQ_HOST  # Should be "localhost" for host connections
   $env:RABBITMQ_PORT  # Should match the exposed host port
   ```

### Port Mismatch

**Common mistake:** Using container port (5672) when host port is different.

**Solution:** Always use the **host port** when connecting from the host machine.

Example:
- Docker exposes: `5673:5672` (host port 5673 → container port 5672)
- Connection from host: `RABBITMQ_PORT=5673` (use host port)
- Connection from Docker: `RABBITMQ_PORT=5672` (use container port)

## Verification

### Check Exposed Ports

```powershell
# Check Docker container ports
docker port airlock-rabbitmq

# Should show:
# 5672/tcp -> 0.0.0.0:5672
# 15672/tcp -> 0.0.0.0:15672
```

### Test Connection

```powershell
# Test AMQP port (5672)
Test-NetConnection -ComputerName localhost -Port 5672

# Test Management UI port (15672)
Test-NetConnection -ComputerName localhost -Port 15672
```

### Verify in Management UI

1. Open http://localhost:15672 in browser
2. Login with credentials
3. Check "Connections" tab - should show active connections on port 5672

