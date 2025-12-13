#!/bin/sh
set -e  # Exit on any error

# Read PORT from environment, default to 5001 if not set
PORT=${PORT:-5001}

# Debug output
echo "=========================================="
echo "Starting NeuralBets Backend"
echo "PORT environment variable: ${PORT}"
echo "Working directory: $(pwd)"
echo "Python path: $(which python3 || which python || echo 'NOT FOUND')"
echo "Gunicorn path: $(which gunicorn || echo 'NOT FOUND')"
echo "Listing /app directory:"
ls -la /app/ | head -20
echo "=========================================="

# Verify app.py exists
if [ ! -f /app/app.py ]; then
    echo "ERROR: app.py not found in /app/"
    exit 1
fi

# Verify gunicorn is available
if ! command -v gunicorn >/dev/null 2>&1; then
    echo "ERROR: gunicorn not found in PATH"
    echo "PATH: $PATH"
    exit 1
fi

# Start Gunicorn
echo "Starting Gunicorn on 0.0.0.0:$PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app

