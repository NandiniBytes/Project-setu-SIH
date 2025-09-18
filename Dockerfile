# Project Setu - Healthcare Terminology Integration Platform
# Multi-stage Docker build for production deployment

FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY project_setu/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/cache

# Copy data files
COPY CodeSystem-NAMASTE.json /app/data/
COPY Combined_ConceptMap.json /app/data/
COPY *.xls /app/data/

# Set proper permissions
RUN chmod +x /app/project_setu/run_fastapi.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash setu
RUN chown -R setu:setu /app
USER setu

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "project_setu/run_fastapi.py"]
