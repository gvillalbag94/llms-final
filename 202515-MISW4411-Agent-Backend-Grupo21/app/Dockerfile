# Use official lightweight Python 3.11-slim image
FROM python:3.11-slim

# Install system dependencies needed for ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Forzar UTF-8 en Python y en el sistema
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Create and set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install requirements in one layer
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (this layer will be rebuilt only when code changes)
COPY . .

# Expose the port where FastAPI will run
EXPOSE 8000

# Default command con timeouts extendidos para permitir respuestas largas del RAG
# --timeout-keep-alive: tiempo para mantener conexiones keep-alive (5 minutos)
# --timeout-graceful-shutdown: tiempo para apagar graciosamente (30 segundos)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "300"]