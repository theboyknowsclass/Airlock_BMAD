#!/usr/bin/env python3
"""
Script to create FastAPI service scaffolding for all services
"""
import os
import shutil
from pathlib import Path

# Service configurations
SERVICES = [
    {
        "name": "api-gateway",
        "title": "API Gateway Service",
        "description": "Entry point for all client requests, handles token validation and request routing",
    },
    {
        "name": "auth-service",
        "title": "Authentication Service",
        "description": "OAuth integration with ADFS, token issuance and validation",
    },
    {
        "name": "user-service",
        "title": "User Management Service",
        "description": "User profile management and role assignment",
    },
    {
        "name": "api-key-service",
        "title": "API Key Service",
        "description": "API key generation, validation, and token issuance",
    },
    {
        "name": "submission-service",
        "title": "Package Submission Service",
        "description": "Accept package submissions and validate package format",
    },
    {
        "name": "workflow-service",
        "title": "Workflow Service",
        "description": "Workflow state management and orchestration",
    },
    {
        "name": "storage-service",
        "title": "Storage Integration Service",
        "description": "External artifact storage integration",
    },
    {
        "name": "registry-service",
        "title": "Registry Integration Service",
        "description": "NPM registry integration and package metadata handling",
    },
    {
        "name": "tracking-service",
        "title": "Tracking Service",
        "description": "Package usage tracking and inventory",
    },
]

AGENTS = [
    {
        "name": "trivy-agent",
        "title": "Trivy Scanner Agent",
        "description": "Trivy security scanning agent for package vulnerability detection",
    },
    {
        "name": "license-agent",
        "title": "License Check Agent",
        "description": "License validation agent for package license checking",
    },
    {
        "name": "review-agent",
        "title": "Manual Review Agent",
        "description": "Manual review agent for package approval workflow",
    },
]


def create_service_structure(service_path: Path, service_config: dict):
    """Create FastAPI service structure"""
    service_name = service_config["name"]
    title = service_config["title"]
    description = service_config["description"]
    
    src_dir = service_path / "src"
    src_dir.mkdir(exist_ok=True)
    
    # Create directories
    directories = [
        src_dir / "routers",
        src_dir / "models",
        src_dir / "services",
        src_dir / "dependencies",
        src_dir / "utils",
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
    
    # Create __init__.py files
    for directory in directories:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            if directory.name == "routers":
                # Routers __init__.py should import health
                init_file.write_text('"""\n{title} routers\n"""\nfrom . import health\n\n__all__ = ["health"]\n'.format(title=title))
            else:
                init_file.write_text('"""\n{description}\n"""\n'.format(description=description))
    
    # Create main.py if it doesn't exist
    main_file = src_dir / "main.py"
    if not main_file.exists():
        main_content = f'''"""
{title}
{description}
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import health
from .utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get service configuration from environment
SERVICE_NAME = os.getenv("SERVICE_NAME", "{service_name}")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"{{SERVICE_NAME}} service starting up")
    logger.info(f"Log level: {{LOG_LEVEL}}")
    yield
    # Shutdown
    logger.info(f"{{SERVICE_NAME}} service shutting down")


# Create FastAPI app
app = FastAPI(
    title="{title}",
    description="{description}",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {{exc}}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={{"detail": "Internal server error"}},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=LOG_LEVEL.lower(),
    )
'''
        main_file.write_text(main_content)
    
    # Create health router if it doesn't exist
    health_file = src_dir / "routers" / "health.py"
    if not health_file.exists():
        health_content = '''"""
Health check router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service health status
    """
    return HealthResponse(
        status="healthy",
        service="{}",
        timestamp=datetime.utcnow(),
    )


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe endpoint
    Returns 200 if service is alive
    """
    return {{"status": "alive"}}


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe endpoint
    Returns 200 if service is ready to accept traffic
    """
    return {{"status": "ready"}}
'''.format(service_name)
        health_file.write_text(health_content)
    
    # Create logging utility if it doesn't exist
    logging_file = src_dir / "utils" / "logging.py"
    if not logging_file.exists():
        logging_content = '''"""
Logging utilities
"""
import logging
import sys
import os
from typing import Optional


def setup_logging(log_level: Optional[str] = None):
    """
    Setup structured logging for the service
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   Defaults to LOG_LEVEL environment variable or INFO
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Set log levels for specific libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
'''
        logging_file.write_text(logging_content)
    
    # Update requirements.txt (always update)
    requirements_file = service_path / "requirements.txt"
    requirements_content = f"""# {title} Dependencies
fastapi==0.115.0
uvicorn[standard]==0.32.1
python-multipart==0.0.12
pydantic==2.10.4
pydantic-settings==2.7.1

"""
    requirements_file.write_text(requirements_content)
    
    # Update Dockerfile (always update)
    dockerfile = service_path / "Dockerfile"
    dockerfile_content = f'''# Multi-stage build for {title}
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    dockerfile.write_text(dockerfile_content)


def main():
    """Main function"""
    project_root = Path(__file__).parent.parent
    services_dir = project_root / "services"
    
    # Create scaffolding for all services
    for service_config in SERVICES:
        service_path = services_dir / service_config["name"]
        if service_path.exists():
            print(f"Creating scaffolding for {service_config['name']}...")
            create_service_structure(service_path, service_config)
            print(f"[OK] {service_config['name']} scaffolding created")
        else:
            print(f"[WARN] {service_config['name']} directory not found, skipping...")
    
    # Create scaffolding for all agents
    agents_dir = services_dir / "agents"
    for agent_config in AGENTS:
        agent_path = agents_dir / agent_config["name"]
        if agent_path.exists():
            print(f"Creating scaffolding for {agent_config['name']}...")
            create_service_structure(agent_path, agent_config)
            print(f"[OK] {agent_config['name']} scaffolding created")
        else:
            print(f"[WARN] {agent_config['name']} directory not found, skipping...")
    
    print("\n[OK] All service scaffolding created!")


if __name__ == "__main__":
    main()

