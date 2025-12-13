# Multi-stage Dockerfile for NeuralBets Backend
# Builds all microservices in a single Dockerfile
# Use with: docker build --target <service-name> -t <image-name> .

# ============================================================================
# Base stage - Common dependencies and shared utilities
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install shared utilities first (used by all services)
COPY shared_utils /app/shared_utils
RUN pip install --no-cache-dir -e ./shared_utils

# ============================================================================
# User Service
# ============================================================================
FROM base as user-service

# Copy user-service requirements and install
COPY user-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy user-service application code
COPY user-service /app/

# Copy and make startup script executable (create one for user-service too)
RUN echo '#!/bin/sh\nset -e\nPORT=${PORT:-5000}\necho "Starting User Service on port $PORT"\nexec gunicorn --bind "0.0.0.0:$PORT" --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app' > /app/start.sh && \
    chmod +x /app/start.sh

# Set default port (Cloud Run will override with PORT env var)
ENV PORT=5000

# Expose port (Cloud Run uses PORT env var)
EXPOSE $PORT

# Health check (uses PORT env var)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c "python -c \"import urllib.request, os; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', '5000') + '/health')\"" || exit 1

# Run with startup script
CMD ["/app/start.sh"]

# ============================================================================
# Bet Service
# ============================================================================
FROM base as bet-service

# Copy bet-service requirements and install
COPY bet-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy bet-service application code
COPY bet-service /app/

# Copy and make startup script executable
COPY bet-service/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set default port (Cloud Run will override with PORT env var)
ENV PORT=5001

# Expose port (Cloud Run uses PORT env var)
EXPOSE $PORT

# Health check (uses PORT env var)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c "python -c \"import urllib.request, os; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', '5001') + '/health')\"" || exit 1

# Run with startup script that tests app import first
CMD ["/app/start.sh"]

# ============================================================================
# Default target (builds bet-service if no target specified)
# ============================================================================
FROM bet-service

