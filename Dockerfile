FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Koyeb uses 8080 by default, but we'll use $PORT)
EXPOSE 8080

# Start command using shell form to expand $PORT
CMD gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:${PORT:-8080} run:app
