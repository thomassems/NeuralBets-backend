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

# Expose the internal port of the application
EXPOSE 5001

# Command to run the application using Gunicorn (production WSGI server)
# It binds to 0.0.0.0 on port 5000 and runs the Flask app 'app:app'
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]