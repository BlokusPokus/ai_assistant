# Deployment Guide

This guide covers the complete deployment process for the Personal Assistant TDAH system across multiple environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Quick Start](#quick-start)
- [Development Deployment](#development-deployment)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Health Checks](#health-checks)
- [Monitoring Setup](#monitoring-setup)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

## Overview

The Personal Assistant TDAH system supports deployment across three environments:

- **Development**: Local development with hot reloading and debugging
- **Staging**: Pre-production testing environment with production-like configuration
- **Production**: Live deployment with security hardening and high availability

### Architecture Overview

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_API[API:8000]
        DEV_FRONTEND[Frontend:3001]
        DEV_DB[(PostgreSQL)]
        DEV_REDIS[(Redis)]
    end

    subgraph "Staging Environment"
        STAGE_API[API:8001]
        STAGE_FRONTEND[Frontend:3002]
        STAGE_DB[(PostgreSQL)]
        STAGE_REDIS[(Redis)]
    end

    subgraph "Production Environment"
        PROD_API[API:443]
        PROD_FRONTEND[Frontend:443]
        PROD_DB[(PostgreSQL)]
        PROD_REDIS[(Redis)]
        PROD_MONITORING[Monitoring Stack]
    end
```

## Prerequisites

### System Requirements

- **Docker**: 20.10+ with Docker Compose 2.0+
- **Memory**: 8GB+ RAM available
- **Storage**: 20GB+ disk space
- **Network**: Internet connectivity for external services

### External Services

- **PostgreSQL**: Database server (local or cloud)
- **Redis**: Cache and message broker
- **Twilio**: SMS service provider
- **OAuth Providers**: Google, Microsoft, Notion, YouTube
- **Domain**: SSL certificate and domain configuration (production)

### Development Tools

- **Node.js**: 18+ for frontend development
- **Python**: 3.11+ for backend development
- **Git**: Version control
- **VS Code**: Recommended IDE with extensions

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd personal_assistant
```

### 2. Environment Configuration

```bash
# Copy environment templates
cp config/env.example config/development.env
cp docker/env.stage.example docker/.env.stage
cp docker/env.prod.example docker/.env.prod

# Edit configuration files
nano config/development.env
nano docker/.env.stage
nano docker/.env.prod
```

### 3. Required Environment Variables

#### Development Environment

```bash
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=15

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here_32_chars_minimum
ENCRYPTION_KEY=your_32_character_encryption_key_here

# External APIs
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_gemini_api_key
```

#### Production Environment

```bash
# Database
PROD_DB_USER=prod_user
PROD_DB_PASSWORD=your_secure_production_password_here_32chars_min

# Redis
PROD_REDIS_PASSWORD=your_secure_redis_password_here_32chars_min

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here_32_chars_minimum
ENCRYPTION_KEY=your_32_character_encryption_key_here

# Domain
DOMAIN_NAME=your-domain.com
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://your-domain.com/api
```

## Quick Start

### Development Environment

```bash
# Start development environment
cd docker
docker-compose -f docker-compose.dev.yml up -d

# Check service status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Access Applications

- **Frontend**: http://localhost:3001
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

## Development Deployment

### Prerequisites

- Local PostgreSQL running on port 5432
- Redis running on port 6379
- Environment variables configured

### Steps

1. **Start Services**:

   ```bash
   cd docker
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Run Database Migrations**:

   ```bash
   docker-compose -f docker-compose.dev.yml exec api python -m alembic upgrade head
   ```

3. **Verify Deployment**:
   ```bash
   curl http://localhost:8000/health/overall
   curl http://localhost:3001
   ```

### Development Features

- **Hot Reloading**: Frontend automatically reloads on changes
- **Debug Mode**: Enhanced logging and error messages
- **Volume Mounting**: Source code mounted for live editing
- **Development SSL**: Self-signed certificates for HTTPS testing

## Staging Deployment

### Prerequisites

- Staging environment variables configured
- Different ports to avoid conflicts with development
- Production-like configuration

### Steps

1. **Configure Environment**:

   ```bash
   cp docker/env.stage.example docker/.env.stage
   # Edit .env.stage with staging values
   ```

2. **Start Staging Environment**:

   ```bash
   cd docker
   docker-compose -f docker-compose.stage.yml --env-file .env.stage up -d
   ```

3. **Run Migrations**:

   ```bash
   docker-compose -f docker-compose.stage.yml exec api python -m alembic upgrade head
   ```

4. **Verify Deployment**:
   ```bash
   curl http://localhost:8001/health/overall
   curl http://localhost:3002
   ```

### Staging Features

- **Production-like Configuration**: Similar to production setup
- **Performance Testing**: Load testing and optimization
- **Integration Testing**: End-to-end testing with external services
- **Staging SSL**: Valid SSL certificates for testing

## Production Deployment

### Prerequisites

- Production environment variables configured
- SSL certificates obtained and configured
- Domain name configured
- Production database and Redis instances
- Monitoring and alerting setup

### Steps

1. **Configure Environment**:

   ```bash
   cp docker/env.prod.example docker/.env.prod
   # Edit .env.prod with production values
   ```

2. **SSL Certificate Setup**:

   ```bash
   # Place SSL certificates in docker/nginx/ssl/prod/
   cp your-cert.pem docker/nginx/ssl/prod/cert.pem
   cp your-key.pem docker/nginx/ssl/prod/key.pem
   ```

3. **Start Production Environment**:

   ```bash
   cd docker
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

4. **Run Migrations**:

   ```bash
   docker-compose -f docker-compose.prod.yml exec api python -m alembic upgrade head
   ```

5. **Verify Deployment**:
   ```bash
   curl https://your-domain.com/health/overall
   curl https://your-domain.com
   ```

### Production Features

- **High Availability**: Multiple replicas and load balancing
- **Security Hardening**: Non-root containers, security headers
- **Performance Optimization**: Resource limits and monitoring
- **Production SSL**: Valid SSL certificates with HTTP/2
- **Comprehensive Monitoring**: Prometheus, Grafana, Loki

## Health Checks

### Service Health Endpoints

```bash
# Overall system health
curl http://localhost:8000/health/overall

# Database health
curl http://localhost:8000/health/database

# Performance metrics
curl http://localhost:8000/health/database/performance

# Redis health
docker-compose exec redis redis-cli ping
```

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

echo "Checking Personal Assistant System Health..."

# Check API health
if curl -f http://localhost:8000/health/overall > /dev/null 2>&1; then
    echo "✅ API: Healthy"
else
    echo "❌ API: Unhealthy"
fi

# Check frontend
if curl -f http://localhost:3001 > /dev/null 2>&1; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy"
fi

# Check database
if curl -f http://localhost:8000/health/database > /dev/null 2>&1; then
    echo "✅ Database: Healthy"
else
    echo "❌ Database: Unhealthy"
fi

# Check Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
fi
```

## Monitoring Setup

### Prometheus Configuration

```yaml
# docker/monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "personal_assistant_api"
    static_configs:
      - targets: ["api:8000"]
    metrics_path: "/health/database/performance"
    scrape_interval: 30s
```

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin)

- **System Dashboard**: Infrastructure metrics
- **Application Dashboard**: API performance
- **Business Dashboard**: User engagement
- **SMS Dashboard**: SMS routing metrics
- **OAuth Dashboard**: OAuth integration metrics
- **Task Dashboard**: Background task processing

### Log Aggregation

```bash
# View application logs
docker-compose logs -f api

# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**:

   ```bash
   # Check port usage
   netstat -tulpn | grep :8000

   # Kill process using port
   sudo kill -9 $(lsof -t -i:8000)
   ```

2. **Database Connection Issues**:

   ```bash
   # Check database status
   docker-compose exec postgres pg_isready -U username -d database_name

   # Test connection
   docker-compose exec api python -c "from personal_assistant.database.connection import get_db; print('DB OK')"
   ```

3. **Redis Connection Issues**:

   ```bash
   # Check Redis status
   docker-compose exec redis redis-cli ping

   # Check Redis info
   docker-compose exec redis redis-cli info
   ```

4. **SSL Certificate Issues**:

   ```bash
   # Check certificate validity
   openssl x509 -in docker/nginx/ssl/prod/cert.pem -text -noout

   # Test SSL connection
   curl -k https://localhost:443/health/overall
   ```

### Debug Commands

```bash
# Check container status
docker-compose ps

# Check resource usage
docker stats

# Execute commands in containers
docker-compose exec api bash
docker-compose exec frontend sh

# Check logs for errors
docker-compose logs | grep -i error
```

## Rollback Procedures

### Service Rollback

```bash
# Stop current services
docker-compose down

# Start previous version
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Verify rollback
curl https://your-domain.com/health/overall
```

### Database Rollback

```bash
# Rollback to previous migration
docker-compose exec api python -m alembic downgrade -1

# Rollback to specific revision
docker-compose exec api python -m alembic downgrade <revision_id>
```

### Configuration Rollback

```bash
# Restore previous configuration
cp config/backup/development.env config/development.env

# Restart services
docker-compose restart
```

## Best Practices

### Security

- Use strong passwords and secrets
- Regularly update dependencies
- Monitor security vulnerabilities
- Implement proper access controls
- Use HTTPS in production

### Performance

- Monitor resource usage
- Optimize database queries
- Implement caching strategies
- Use connection pooling
- Monitor response times

### Maintenance

- Regular backups
- Monitor logs and metrics
- Update dependencies regularly
- Test deployments in staging
- Document changes and procedures

### Monitoring

- Set up comprehensive alerting
- Monitor key performance indicators
- Track business metrics
- Monitor security events
- Regular health checks

This deployment guide provides comprehensive instructions for deploying the Personal Assistant TDAH system across all environments, ensuring reliable and secure operation.
