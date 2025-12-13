#!/bin/sh
# Entrypoint script that reads PORT from environment and starts Gunicorn

# Read PORT from environment, default to 5001 if not set
PORT=${PORT:-5001}

# Debug output
echo "=========================================="
echo "Starting NeuralBets Backend"
echo "PORT environment variable: ${PORT}"
echo "Working directory: $(pwd)"
echo "Python path: $(which python || echo 'NOT FOUND')"
echo "Gunicorn path: $(which gunicorn || echo 'NOT FOUND')"
echo "=========================================="

# Start Gunicorn (will fail if gunicorn not found, which is desired)
echo "Starting Gunicorn on 0.0.0.0:$PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app

