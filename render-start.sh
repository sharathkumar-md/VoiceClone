#!/usr/bin/env bash
# Render start script
set -o errexit

# Render sets working dir to /opt/render/project/src/
# But our code has another src/ subdirectory, so we cd into it
# This way relative imports in the code will work correctly
cd src
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
