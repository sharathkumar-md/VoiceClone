#!/bin/bash
# Render startup script

# Add src directory to PYTHONPATH so imports work correctly
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Change to the src directory where api module lives
cd src || exit 1

# Run uvicorn from src directory with explicit PYTHONPATH
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
