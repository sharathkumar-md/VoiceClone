#!/bin/bash
# Render startup script

# Change to the src directory where the api module is located
cd /opt/render/project/src || cd "$(dirname "$0")/src" || exit 1

# Run uvicorn from the src directory
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
