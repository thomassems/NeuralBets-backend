#!/bin/sh
# Entrypoint script that reads PORT from environment and starts Gunicorn

PORT=${PORT:-5001}
echo "Starting server on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app

