#!/usr/bin/env python3
"""
Update all services requirements.txt and Dockerfile
"""
from pathlib import Path

SERVICES = [
    "api-gateway",
    "auth-service",
    "user-service",
    "api-key-service",
    "submission-service",
    "workflow-service",
    "storage-service",
    "registry-service",
    "tracking-service",
]

AGENTS = [
    "trivy-agent",
    "license-agent",
    "review-agent",
]

REQUIREMENTS_TEMPLATE = """# {title} Dependencies
fastapi==0.115.0
uvicorn[standard]==0.32.1
python-multipart==0.0.12
pydantic==2.10.4
pydantic-settings==2.7.1

"""

DOCKERFILE_TEMPLATE = """# Multi-stage build for {title}
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
"""


def update_service(service_path: Path, service_config: dict):
    """Update service requirements.txt and Dockerfile"""
    title = service_config["title"]
    
    # Update requirements.txt
    requirements_file = service_path / "requirements.txt"
    requirements_file.write_text(REQUIREMENTS_TEMPLATE.format(title=title))
    print(f"[OK] Updated {service_config['name']}/requirements.txt")
    
    # Update Dockerfile
    dockerfile = service_path / "Dockerfile"
    dockerfile.write_text(DOCKERFILE_TEMPLATE.format(title=title))
    print(f"[OK] Updated {service_config['name']}/Dockerfile")


def main():
    """Main function"""
    project_root = Path(__file__).parent.parent
    services_dir = project_root / "services"
    
    service_configs = [
        {"name": name, "title": name.replace("-", " ").title().replace(" ", " ")}
        for name in SERVICES
    ]
    
    agent_configs = [
        {"name": name, "title": name.replace("-", " ").title().replace(" ", " ")}
        for name in AGENTS
    ]
    
    # Update all services
    for service_config in service_configs:
        service_path = services_dir / service_config["name"]
        if service_path.exists():
            # Get proper title
            title_map = {
                "api-gateway": "API Gateway Service",
                "auth-service": "Authentication Service",
                "user-service": "User Management Service",
                "api-key-service": "API Key Service",
                "submission-service": "Package Submission Service",
                "workflow-service": "Workflow Service",
                "storage-service": "Storage Integration Service",
                "registry-service": "Registry Integration Service",
                "tracking-service": "Tracking Service",
            }
            service_config["title"] = title_map.get(service_config["name"], service_config["title"])
            update_service(service_path, service_config)
    
    # Update all agents
    agents_dir = services_dir / "agents"
    for agent_config in agent_configs:
        agent_path = agents_dir / agent_config["name"]
        if agent_path.exists():
            # Get proper title
            title_map = {
                "trivy-agent": "Trivy Scanner Agent",
                "license-agent": "License Check Agent",
                "review-agent": "Manual Review Agent",
            }
            agent_config["title"] = title_map.get(agent_config["name"], agent_config["title"])
            update_service(agent_path, agent_config)
    
    print("\n[OK] All services updated!")


if __name__ == "__main__":
    main()

