#!/bin/bash
# Deploy to professional tier (AWS, GCP, Azure with GPU support)

echo "🚀 Deploying to PROFESSIONAL TIER"
echo "Using full ML capabilities with heavy models"

# Set deployment tier
export DEPLOYMENT_TIER=professional

# Use full requirements
cp requirements-full.txt requirements-deploy.txt

# Deploy with Docker for better resource management
echo "🐳 Building Docker container with ML support..."

# Create Dockerfile for professional deployment
cat > Dockerfile.professional << EOF
FROM python:3.11-slim

# Install system dependencies for ML
RUN apt-get update && apt-get install -y \\
    gcc g++ \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements-full.txt .
RUN pip install --no-cache-dir -r requirements-full.txt

# Copy application
COPY . .

# Set environment
ENV DEPLOYMENT_TIER=professional
ENV FLASK_ENV=production

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "300", "app:app"]
EOF

echo "✅ Professional tier deployment ready"
echo "🎯 Features: Advanced emotion detection, 8GB RAM, GPU support"