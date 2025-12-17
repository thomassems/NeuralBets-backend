# Use the official Python base image
FROM python:3.11-slim

# Set environment variables for the application
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy shared_utils first (needed for editable install)
COPY shared_utils /app/shared_utils

# Copy the requirements file and install dependencies first for layer caching
COPY user-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY user-service /app/

# Expose the internal port Cloud Run will send traffic to
EXPOSE 8080

# Use Cloud Run provided PORT if set, default to 8080 locally
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} app:app"]