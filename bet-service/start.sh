#!/bin/sh

# Read PORT from environment, default to 5001 if not set
PORT=${PORT:-5001}

echo "=========================================="
echo "NeuralBets Backend Startup"
echo "=========================================="
echo "PORT environment variable: ${PORT}"
echo "Working directory: $(pwd)"
echo "Python version: $(python3 --version 2>&1 || python --version 2>&1)"
echo "Gunicorn: $(which gunicorn || echo 'NOT FOUND')"
echo ""

# Test if we can import the app before starting Gunicorn
echo "Testing app import..."
if python3 -c "import app; print('[start] ✓ App imported successfully')" 2>&1; then
    echo "[start] App import test PASSED"
else
    echo "[start] ✗ App import test FAILED"
    echo "[start] Full error output:"
    python3 -c "import app" 2>&1 || true
    echo "[start] Exiting due to import failure"
    exit 1
fi

echo ""
echo "=========================================="
echo "Starting Gunicorn on 0.0.0.0:${PORT}"
echo "=========================================="

# Start Gunicorn - use exec to replace shell process
exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    app:app

