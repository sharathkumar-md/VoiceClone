#!/bin/bash
# Render startup script

# Change to the src directory where api module lives
cd src || exit 1

# Run uvicorn from src directory
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
