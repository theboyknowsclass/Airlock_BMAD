#!/bin/bash
# Docker Compose Tear Down Script (Bash)
# Stops and removes all containers, networks, and optionally volumes

set -e

VOLUMES=false
IMAGES=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --volumes)
            VOLUMES=true
            shift
            ;;
        --images)
            IMAGES=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--volumes] [--images]"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "Docker Compose Tear Down"
echo "========================================"
echo ""

if [ "$VOLUMES" = true ]; then
    echo "⚠️  WARNING: This will remove volumes (data will be lost)!"
    echo ""
fi

if [ "$IMAGES" = true ]; then
    echo "⚠️  WARNING: This will remove images!"
    echo ""
fi

read -p "Continue? (y/N) " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Stopping and removing containers..."

# Build docker compose command
COMPOSE_CMD="docker compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev down"

if [ "$VOLUMES" = true ]; then
    COMPOSE_CMD="$COMPOSE_CMD --volumes"
fi

if [ "$IMAGES" = true ]; then
    COMPOSE_CMD="$COMPOSE_CMD --rmi all"
fi

eval $COMPOSE_CMD

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Containers stopped and removed successfully!"
    
    if [ "$VOLUMES" = true ]; then
        echo "✅ Volumes removed"
    fi
    
    if [ "$IMAGES" = true ]; then
        echo "✅ Images removed"
    fi
else
    echo ""
    echo "❌ Error during tear down"
    exit 1
fi

echo ""
echo "Cleanup complete!"

