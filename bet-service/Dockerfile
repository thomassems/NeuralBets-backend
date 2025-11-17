# Use the official Python base image
FROM python:3.11-slim

# Set environment variables for the application
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first for layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the internal port of the application
EXPOSE 5001

# Command to run the application using Gunicorn (production WSGI server)
# It binds to 0.0.0.0 on port 5001 and runs the Flask app 'app:app'
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]