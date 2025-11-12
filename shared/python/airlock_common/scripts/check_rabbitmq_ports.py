"""
Check RabbitMQ port configuration
Helps identify port mismatches between Docker and connection settings
"""
import sys
import os
import subprocess
import json

def check_docker_ports():
    """Check what ports RabbitMQ container is exposing"""
    print("Checking Docker container ports...")
    try:
        # Get container port mapping
        result = subprocess.run(
            ["docker", "port", "airlock-rabbitmq"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print("[WARN] Could not check Docker ports. Is RabbitMQ container running?")
            print(f"  Error: {result.stderr}")
            return None
        
        lines = result.stdout.strip().split('\n')
        ports = {}
        for line in lines:
            if '->' in line:
                parts = line.split('->')
                if len(parts) == 2:
                    container_port = parts[0].strip().split('/')[0]
                    host_mapping = parts[1].strip()
                    ports[container_port] = host_mapping
        
        print("[OK] Docker container ports:")
        for container_port, host_mapping in ports.items():
            print(f"  Container port {container_port} -> Host {host_mapping}")
        
        return ports
    except FileNotFoundError:
        print("[ERROR] Docker command not found. Is Docker installed?")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to check Docker ports: {e}")
        return None


def check_environment_variables():
    """Check environment variables for RabbitMQ connection"""
    print("\nChecking environment variables...")
    
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = os.getenv("RABBITMQ_PORT", "5672")
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "***")
    
    print(f"[OK] Environment variables:")
    print(f"  RABBITMQ_HOST = {host}")
    print(f"  RABBITMQ_PORT = {port}")
    print(f"  RABBITMQ_USER = {user}")
    print(f"  RABBITMQ_PASSWORD = {password}")
    
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }


def check_port_match(docker_ports, env_vars):
    """Check if environment port matches Docker exposed port"""
    print("\nChecking port configuration...")
    
    if not docker_ports:
        print("[WARN] Cannot verify port match - Docker ports not available")
        return False
    
    # Get AMQP port (5672) from Docker
    docker_amqp = docker_ports.get("5672")
    env_port = env_vars["port"]
    
    if not docker_amqp:
        print("[ERROR] Docker is not exposing AMQP port (5672)")
        print("  Check docker-compose.dev.yml - RabbitMQ should expose port 5672")
        return False
    
    # Extract host port from Docker mapping (e.g., "0.0.0.0:5672" -> "5672")
    docker_host_port = docker_amqp.split(':')[-1]
    
    print(f"  Docker exposes: {docker_amqp}")
    print(f"  Connection uses: localhost:{env_port}")
    
    if docker_host_port == env_port:
        print("[OK] Ports match!")
        return True
    else:
        print(f"[ERROR] Port mismatch!")
        print(f"  Docker exposes port {docker_host_port} on host")
        print(f"  Connection code uses port {env_port}")
        print(f"\n  Solution:")
        print(f"    Set RABBITMQ_PORT={docker_host_port} to match Docker")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("RabbitMQ Port Configuration Check")
    print("=" * 60)
    print()
    
    # Check Docker ports
    docker_ports = check_docker_ports()
    
    # Check environment variables
    env_vars = check_environment_variables()
    
    # Check port match
    if docker_ports:
        port_match = check_port_match(docker_ports, env_vars)
    else:
        port_match = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if not docker_ports:
        print("[ERROR] Cannot verify configuration - Docker container not accessible")
        print("\n  Make sure RabbitMQ is running:")
        print("    docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d rabbitmq")
        return 1
    
    if not port_match:
        print("[ERROR] Port configuration mismatch detected")
        print("\n  To fix:")
        print("    1. Check docker-compose.dev.yml exposes port 5672")
        print("    2. Set RABBITMQ_PORT to match the exposed host port")
        print("    3. Restart RabbitMQ container if needed")
        return 1
    
    print("[OK] Port configuration looks correct!")
    print("\n  Connection should work with:")
    print(f"    Host: {env_vars['host']}")
    print(f"    Port: {env_vars['port']}")
    print(f"    User: {env_vars['user']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

