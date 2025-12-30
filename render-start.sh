#!/usr/bin/env bash
# Render start script
set -o errexit

# Change to src directory and run uvicorn
cd src
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
