#!/usr/bin/env python3
"""
Fix routers/__init__.py files to properly import health
"""
from pathlib import Path

def fix_routers_init(service_path: Path, service_name: str):
    """Fix routers/__init__.py to import health"""
    routers_init = service_path / "src" / "routers" / "__init__.py"
    if routers_init.exists():
        content = routers_init.read_text()
        if "from . import health" not in content:
            routers_init.write_text(f'''"""
{service_name} routers
"""
from . import health

__all__ = ["health"]
''')


def main():
    """Main function"""
    project_root = Path(__file__).parent.parent
    services_dir = project_root / "services"
    
    # Fix all services
    services = [
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
    
    for service_name in services:
        service_path = services_dir / service_name
        if service_path.exists():
            fix_routers_init(service_path, service_name)
            print(f"[OK] Fixed {service_name}/src/routers/__init__.py")
    
    # Fix all agents
    agents_dir = services_dir / "agents"
    agents = ["trivy-agent", "license-agent", "review-agent"]
    
    for agent_name in agents:
        agent_path = agents_dir / agent_name
        if agent_path.exists():
            fix_routers_init(agent_path, agent_name)
            print(f"[OK] Fixed {agent_name}/src/routers/__init__.py")
    
    print("\n[OK] All routers/__init__.py files fixed!")


if __name__ == "__main__":
    main()

