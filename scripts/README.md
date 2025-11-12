# Service Testing Scripts

## Installation Script

### `install-all-requirements.ps1` (Windows) / `install-all-requirements.sh` (Linux/Mac)

Installs all requirements.txt files from all services into a local `.venv` virtual environment.

**Usage:**
```powershell
# Windows
.\scripts\install-all-requirements.ps1

# Linux/Mac
./scripts/install-all-requirements.sh
```

**What it does:**
1. Creates a `.venv` virtual environment if it doesn't exist
2. Activates the virtual environment
3. Upgrades pip
4. Finds all `requirements.txt` files in:
   - `services/` (all services and agents)
   - `shared/python/airlock_common/`
5. Installs all dependencies from all requirements.txt files

**Output:**
- Lists all requirements.txt files found
- Installs dependencies from each file
- Reports success or failure for each file
- Provides summary at the end

## Testing Scripts

### `test-service-simple.ps1`

Tests a FastAPI service by starting it and testing health endpoints.

**Usage:**
```powershell
# Test default service (api-gateway) on default port (8000)
.\scripts\test-service-simple.ps1

# Test specific service on specific port
.\scripts\test-service-simple.ps1 -ServiceName auth-service -Port 8001
```

**What it does:**
1. Checks if virtual environment exists
2. Checks if service exists
3. Checks if uvicorn is installed
4. Starts service in background using uvicorn
5. Tests health endpoints:
   - `/health` - Returns service health status
   - `/health/live` - Liveness probe
   - `/health/ready` - Readiness probe
6. Stops the service
7. Reports test results

**Parameters:**
- `-ServiceName` - Service name (default: api-gateway)
- `-Port` - Port number (default: 8000)

**Example:**
```powershell
# Test api-gateway
.\scripts\test-service-simple.ps1 -ServiceName api-gateway -Port 8000

# Test auth-service
.\scripts\test-service-simple.ps1 -ServiceName auth-service -Port 8001
```

## Manual Testing

### Activate Virtual Environment

```powershell
# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### Run a Service

```powershell
# From project root
python -m uvicorn services.api-gateway.src.main:app --host 0.0.0.0 --port 8000 --reload

# Or from service directory
cd services/api-gateway/src
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Test Health Endpoint

```powershell
# PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing

# Or curl
curl http://localhost:8000/health
```

### Expected Response

```json
{
  "status": "healthy",
  "service": "api-gateway",
  "timestamp": "2025-11-12T16:22:02"
}
```

## Troubleshooting

### Virtual Environment Not Found

**Error:** `[ERROR] Virtual environment not found`

**Solution:** Run `.\scripts\install-all-requirements.ps1` first

### Service Not Found

**Error:** `[ERROR] Service directory not found`

**Solution:** Check that the service name is correct and the service directory exists

### Port Already in Use

**Error:** `[ERROR] Health endpoint test failed`

**Solution:** Use a different port or stop the service using that port

### Import Errors

**Error:** `ImportError: attempted relative import with no known parent package`

**Solution:** Run the service using uvicorn from the project root:
```powershell
python -m uvicorn services.api-gateway.src.main:app --host 0.0.0.0 --port 8000
```

## Services Available

**Main Services:**
- api-gateway
- auth-service
- user-service
- api-key-service
- submission-service
- workflow-service
- storage-service
- registry-service
- tracking-service

**Agents:**
- trivy-agent
- license-agent
- review-agent

