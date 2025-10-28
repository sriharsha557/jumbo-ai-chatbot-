# Jumbo Chatbot - Production Deployment Guide

## 🏗️ Architecture Overview

The Jumbo Chatbot is built with a **stateless, microservices-ready architecture**:

- **Stateless Backend**: No conversation state stored in memory
- **Versioned APIs**: `/api/v1/` for future compatibility
- **Environment Separation**: Dev, Test, Staging, Production
- **Monitoring & Logging**: Structured logs, metrics, health checks
- **Security**: JWT authentication, CORS, rate limiting

## 🌍 Environment Setup

### 1. Development Environment

```bash
# Clone repository
git clone <your-repo>
cd jumbo-chatbot

# Copy environment file
cp .env.development .env

# Edit .env with your credentials
nano .env

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### 2. Testing Environment

```bash
# Use testing environment
export ENVIRONMENT=testing

# Copy test environment file
cp .env.testing .env

# Run tests
pytest tests/

# Run with test environment
python app.py
```

### 3. Production Environment

```bash
# Use production environment
export ENVIRONMENT=production

# Copy production environment file
cp .env.production .env

# Edit with production credentials
nano .env

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:create_app()
```

## 🐳 Docker Deployment

### Local Development with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Services available:
# - API: http://localhost:5000
# - Redis: localhost:6379
# - Nginx: http://localhost:80
```

### Production Docker Deployment

```bash
# Build production image
docker build -t jumbo-chatbot:latest .

# Run production container
docker run -d \
  --name jumbo-chatbot \
  -p 5000:5000 \
  --env-file .env.production \
  jumbo-chatbot:latest
```

## ☁️ Cloud Deployment Options

### 1. Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Railway Configuration:**
- Set environment variables in Railway dashboard
- Use Railway's PostgreSQL addon or external Supabase
- Enable health checks on `/health`

### 2. Heroku Deployment

```bash
# Install Heroku CLI
# Create Heroku app
heroku create jumbo-chatbot-api

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set SECRET_KEY=your-secret-key
# ... set all production variables

# Deploy
git push heroku main
```

**Procfile:**
```
web: gunicorn --bind 0.0.0.0:$PORT app:create_app()
```

### 3. AWS/GCP/Azure Deployment

**Container Services:**
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances

**Configuration:**
- Use container registry (ECR, GCR, ACR)
- Set environment variables in service configuration
- Configure load balancer with health checks
- Enable auto-scaling based on CPU/memory

## 🗄️ Database Setup

### Supabase Configuration

1. **Create Supabase Projects:**
   - Development: `jumbo-chatbot-dev`
   - Testing: `jumbo-chatbot-test`
   - Production: `jumbo-chatbot-prod`

2. **Run Database Schema:**
   ```sql
   -- Execute supabase_schema.sql in each environment
   -- Enable Row Level Security
   -- Configure authentication settings
   ```

3. **Environment Variables:**
   ```bash
   # Development
   SUPABASE_URL=https://your-dev-project.supabase.co
   SUPABASE_ANON_KEY=your-dev-anon-key
   
   # Production
   SUPABASE_URL=https://your-prod-project.supabase.co
   SUPABASE_ANON_KEY=your-prod-anon-key
   ```

## 🔐 Security Configuration

### 1. Environment Variables

**Required for Production:**
```bash
SECRET_KEY=your-256-bit-secret-key
SUPABASE_URL=your-production-supabase-url
SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
GROQ_API_KEY=your-groq-api-key
```

### 2. CORS Configuration

```bash
# Production domains only
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Rate Limiting

Nginx configuration includes:
- Auth endpoints: 5 requests/second
- API endpoints: 10 requests/second
- Burst handling with queuing

## 📊 Monitoring Setup

### 1. Health Checks

```bash
# Health check endpoint
curl http://your-domain/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "checks": {
    "database": {"status": "healthy"},
    "llm_service": {"status": "healthy"}
  }
}
```

### 2. Metrics Collection

```bash
# Metrics endpoint (if enabled)
curl http://your-domain/metrics

# Response includes:
{
  "metrics": {
    "uptime_seconds": 3600,
    "requests_total": 1500,
    "error_rate": 0.5,
    "active_users_count": 25
  }
}
```

### 3. Error Tracking

**Sentry Integration:**
```bash
# Set Sentry DSN
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Automatic error tracking and performance monitoring
```

### 4. Logging

**Structured JSON Logs:**
```json
{
  "timestamp": "2025-01-01T00:00:00Z",
  "level": "INFO",
  "message": "Message processed successfully",
  "user_id": "user-123",
  "scenario": "conversational_summarizer",
  "duration_ms": 250
}
```

## 🚀 Performance Optimization

### 1. Horizontal Scaling

```bash
# Multiple workers with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 app:create_app()

# Docker Swarm scaling
docker service scale jumbo-chatbot=3

# Kubernetes scaling
kubectl scale deployment jumbo-chatbot --replicas=3
```

### 2. Caching Strategy

**Redis Configuration:**
```bash
# Production Redis
REDIS_URL=redis://your-redis-cluster:6379
REDIS_PASSWORD=your-redis-password

# Cache conversation context
# Cache user profiles
# Session management
```

### 3. Database Optimization

- Connection pooling
- Read replicas for analytics
- Proper indexing on frequently queried fields
- Query optimization

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        run: railway up --service production
```

## 📋 Environment Checklist

### Development ✅
- [x] Local database setup
- [x] Environment variables configured
- [x] Hot reload enabled
- [x] Debug logging enabled

### Testing ✅
- [x] Separate test database
- [x] Test environment variables
- [x] Automated test suite
- [x] CI/CD integration

### Staging ✅
- [x] Production-like environment
- [x] Performance testing
- [x] Security testing
- [x] Load testing

### Production ✅
- [x] Production database
- [x] All secrets configured
- [x] Monitoring enabled
- [x] Error tracking active
- [x] Backup strategy
- [x] Scaling configuration
- [x] Security hardening

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check Supabase URL and keys
   curl -H "apikey: $SUPABASE_ANON_KEY" "$SUPABASE_URL/rest/v1/"
   ```

2. **Authentication Issues**
   ```bash
   # Verify JWT secret matches Supabase
   # Check token expiration
   # Validate CORS settings
   ```

3. **Performance Issues**
   ```bash
   # Check metrics endpoint
   # Monitor database query performance
   # Review error logs
   ```

### Support

- Check `/health` endpoint for service status
- Review structured logs for error details
- Monitor metrics for performance insights
- Use Sentry for error tracking and debugging

## 🎯 Next Steps

1. **Set up monitoring dashboards** (Grafana, DataDog)
2. **Implement automated backups**
3. **Configure alerting** (PagerDuty, Slack)
4. **Set up load testing** (Artillery, k6)
5. **Implement blue-green deployment**