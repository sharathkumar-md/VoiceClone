#!/bin/bash
# Render startup script

# We're already in the src directory thanks to rootDir in render.yaml
# Just run uvicorn directly with the api.main module
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
