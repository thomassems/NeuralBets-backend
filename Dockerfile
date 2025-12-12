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

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]

# ============================================================================
# Bet Service
# ============================================================================
FROM base as bet-service

# Copy bet-service requirements and install
COPY bet-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy bet-service application code
COPY bet-service /app/

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')" || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "app:app"]

# ============================================================================
# Default target (builds bet-service if no target specified)
# ============================================================================
FROM bet-service

