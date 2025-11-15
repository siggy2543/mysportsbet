#!/bin/bash
# Flexible entrypoint script for sports betting backend

set -e

# If no arguments provided, default to gunicorn
if [ "$#" -eq 0 ]; then
    exec gunicorn app:app --config gunicorn.conf.py
fi

# If first argument is python, execute as is
if [ "$1" = "python" ]; then
    exec "$@"
fi

# If first argument looks like a celery command, execute as is
if [ "$1" = "celery" ] || [[ "$*" == *"celery"* ]]; then
    exec "$@"
fi

# If first argument is uvicorn, execute as is  
if [ "$1" = "uvicorn" ]; then
    exec "$@"
fi

# Otherwise, execute the command as provided
exec "$@"