#!/bin/bash
# Render startup script

# Get the script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to src directory where all the Python modules are located
cd "${SCRIPT_DIR}/src" || exit 1

# Run uvicorn from the src directory
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
