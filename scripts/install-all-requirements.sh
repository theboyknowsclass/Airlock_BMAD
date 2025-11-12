#!/bin/bash
# Install all requirements.txt files from all services into a local .venv
# This script creates a virtual environment and installs all dependencies

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

echo "Installing all service requirements into .venv..."
echo "  Project root: $PROJECT_ROOT"
echo "  Virtual environment: $VENV_PATH"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found. Please install Python 3.12 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "[OK] Python found: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
    echo "[OK] Virtual environment created"
else
    echo "[OK] Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "[OK] Pip upgraded"
echo ""

# Find all requirements.txt files
REQUIREMENTS_FILES=()

# Find requirements.txt in services
if [ -d "$PROJECT_ROOT/services" ]; then
    while IFS= read -r -d '' file; do
        REQUIREMENTS_FILES+=("$file")
    done < <(find "$PROJECT_ROOT/services" -name "requirements.txt" -type f -print0)
fi

# Find requirements.txt in shared/python/airlock_common
SHARED_REQUIREMENTS="$PROJECT_ROOT/shared/python/airlock_common/requirements.txt"
if [ -f "$SHARED_REQUIREMENTS" ]; then
    REQUIREMENTS_FILES+=("$SHARED_REQUIREMENTS")
fi

echo "Found ${#REQUIREMENTS_FILES[@]} requirements.txt files:"
for req_file in "${REQUIREMENTS_FILES[@]}"; do
    RELATIVE_PATH="${req_file#$PROJECT_ROOT/}"
    echo "  - $RELATIVE_PATH"
done
echo ""

# Install requirements from each file
FAILED_FILES=()
for req_file in "${REQUIREMENTS_FILES[@]}"; do
    RELATIVE_PATH="${req_file#$PROJECT_ROOT/}"
    echo "Installing from $RELATIVE_PATH..."
    
    if pip install -r "$req_file" --quiet; then
        echo "[OK] Installed from $RELATIVE_PATH"
    else
        echo "[ERROR] Failed to install from $RELATIVE_PATH"
        FAILED_FILES+=("$RELATIVE_PATH")
    fi
done

echo ""
echo "============================================================"
echo "Installation Summary"
echo "============================================================"

if [ ${#FAILED_FILES[@]} -eq 0 ]; then
    echo "[OK] All requirements installed successfully!"
    echo ""
    echo "Virtual environment: $VENV_PATH"
    echo "To activate: source .venv/bin/activate"
    echo "To deactivate: deactivate"
    exit 0
else
    echo "[ERROR] Failed to install requirements from:"
    for file in "${FAILED_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

