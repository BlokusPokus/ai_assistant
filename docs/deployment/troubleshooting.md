# Troubleshooting Guide

This guide provides comprehensive troubleshooting procedures for common issues in the Personal Assistant TDAH system.

## Table of Contents

- [Overview](#overview)
- [Quick Diagnostics](#quick-diagnostics)
- [Common Issues](#common-issues)
- [Service-Specific Troubleshooting](#service-specific-troubleshooting)
- [Database Issues](#database-issues)
- [Authentication Issues](#authentication-issues)
- [OAuth Integration Issues](#oauth-integration-issues)
- [SMS Router Issues](#sms-router-issues)
- [Performance Issues](#performance-issues)
- [Deployment Issues](#deployment-issues)
- [Monitoring Issues](#monitoring-issues)
- [Recovery Procedures](#recovery-procedures)
- [Prevention Strategies](#prevention-strategies)

## Overview

This troubleshooting guide covers:

- **Diagnostic Procedures**: Systematic approaches to identify issues
- **Common Problems**: Frequently encountered issues and solutions
- **Service-Specific**: Detailed troubleshooting for each service
- **Recovery Procedures**: Steps to restore service functionality
- **Prevention**: Strategies to avoid common issues

### Troubleshooting Methodology

1. **Identify the Problem**: Understand what's not working
2. **Gather Information**: Collect logs, metrics, and symptoms
3. **Isolate the Issue**: Determine which component is affected
4. **Apply Solution**: Implement the appropriate fix
5. **Verify Resolution**: Confirm the issue is resolved
6. **Document**: Record the issue and solution for future reference

## Quick Diagnostics

### System Health Check

```bash
# Check all services status
docker-compose ps

# Check service health
curl -f http://localhost:8000/health/overall

# Check database health
curl -f http://localhost:8000/health/database

# Check Redis health
docker-compose exec redis redis-cli ping

# Check logs for errors
docker-compose logs --tail=100 | grep -i error
```

### Quick Status Commands

```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Network connectivity
docker-compose exec api ping redis
docker-compose exec api ping postgres

# Port availability
netstat -tulpn | grep -E ":(8000|3001|5432|6379|9090|3000)"

# Disk space
df -h

# Memory usage
free -h
```

## Common Issues

### 1. Service Won't Start

**Symptoms**:

- Container exits immediately
- Service not responding
- Health checks failing

**Diagnosis**:

```bash
# Check container logs
docker-compose logs <service-name>

# Check container status
docker-compose ps

# Check resource usage
docker stats
```

**Solutions**:

```bash
# Restart specific service
docker-compose restart <service-name>

# Rebuild and restart
docker-compose up -d --build <service-name>

# Check for port conflicts
netstat -tulpn | grep :<port>

# Check disk space
df -h
```

### 2. Database Connection Issues

**Symptoms**:

- API returns database errors
- Health check fails
- Connection timeout errors

**Diagnosis**:

```bash
# Test database connection
docker-compose exec api python -c "
from personal_assistant.database.connection import get_db
print('Database connection test')
"

# Check database logs
docker-compose logs postgres

# Check connection pool
curl http://localhost:8000/health/database
```

**Solutions**:

```bash
# Restart database
docker-compose restart postgres

# Check database configuration
docker-compose exec postgres psql -U ianleblanc -d postgres -c "SELECT version();"

# Reset connection pool
docker-compose restart api
```

### 3. Redis Connection Issues

**Symptoms**:

- Cache not working
- Celery tasks failing
- Redis connection errors

**Diagnosis**:

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Check Redis memory
docker-compose exec redis redis-cli info memory
```

**Solutions**:

```bash
# Restart Redis
docker-compose restart redis

# Clear Redis cache
docker-compose exec redis redis-cli flushall

# Check Redis configuration
docker-compose exec redis redis-cli config get "*"
```

### 4. Frontend Not Loading

**Symptoms**:

- Frontend returns 404 or 500 errors
- Static assets not loading
- API calls failing

**Diagnosis**:

```bash
# Check frontend logs
docker-compose logs frontend

# Check nginx logs
docker-compose logs nginx

# Test frontend directly
curl http://localhost:3001

# Test API through nginx
curl http://localhost:8081/api/health/overall
```

**Solutions**:

```bash
# Restart frontend
docker-compose restart frontend

# Rebuild frontend
docker-compose up -d --build frontend

# Check nginx configuration
docker-compose exec nginx nginx -t
```

## Service-Specific Troubleshooting

### API Service

#### Common Issues

1. **High Memory Usage**:

   ```bash
   # Check memory usage
   docker stats personal_assistant_api

   # Check for memory leaks
   docker-compose exec api python -c "
   import psutil
   print(f'Memory usage: {psutil.virtual_memory().percent}%')
   "
   ```

2. **Slow Response Times**:

   ```bash
   # Check response times
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health/overall

   # Check database performance
   curl http://localhost:8000/health/database/performance
   ```

3. **Authentication Errors**:

   ```bash
   # Check authentication logs
   docker-compose logs api | grep -i auth

   # Test authentication endpoint
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password"}'
   ```

#### Debug Commands

```bash
# Check API logs
docker-compose logs -f api

# Execute commands in API container
docker-compose exec api bash

# Check Python environment
docker-compose exec api python --version
docker-compose exec api pip list

# Check environment variables
docker-compose exec api env | grep -E "(DB_|REDIS_|JWT_)"
```

### Frontend Service

#### Common Issues

1. **Build Failures**:

   ```bash
   # Check build logs
   docker-compose logs frontend

   # Check Node.js version
   docker-compose exec frontend node --version

   # Check npm packages
   docker-compose exec frontend npm list
   ```

2. **Hot Reload Not Working**:

   ```bash
   # Check volume mounts
   docker-compose exec frontend ls -la /app

   # Check file permissions
   docker-compose exec frontend ls -la /app/src
   ```

3. **API Connection Issues**:

   ```bash
   # Check API URL configuration
   docker-compose exec frontend env | grep VITE_API_URL

   # Test API connectivity
   docker-compose exec frontend curl http://api:8000/health/overall
   ```

#### Debug Commands

```bash
# Check frontend logs
docker-compose logs -f frontend

# Execute commands in frontend container
docker-compose exec frontend sh

# Check build process
docker-compose exec frontend npm run build

# Check development server
docker-compose exec frontend npm run dev
```

### Worker Service

#### Common Issues

1. **Tasks Not Processing**:

   ```bash
   # Check worker logs
   docker-compose logs worker

   # Check Celery status
   docker-compose exec worker celery -A personal_assistant.workers.celery_app inspect active
   ```

2. **Task Failures**:

   ```bash
   # Check failed tasks
   docker-compose exec worker celery -A personal_assistant.workers.celery_app inspect failed

   # Check task results
   docker-compose exec worker celery -A personal_assistant.workers.celery_app inspect stats
   ```

3. **Memory Issues**:

   ```bash
   # Check worker memory usage
   docker stats personal_assistant_worker

   # Check for memory leaks
   docker-compose exec worker python -c "
   import psutil
   print(f'Memory usage: {psutil.virtual_memory().percent}%')
   "
   ```

#### Debug Commands

```bash
# Check worker logs
docker-compose logs -f worker

# Execute commands in worker container
docker-compose exec worker bash

# Check Celery configuration
docker-compose exec worker celery -A personal_assistant.workers.celery_app inspect stats

# Check task queues
docker-compose exec worker celery -A personal_assistant.workers.celery_app inspect active_queues
```

## Database Issues

### PostgreSQL Issues

#### Connection Problems

```bash
# Check database status
docker-compose exec postgres pg_isready -U ianleblanc -d postgres

# Check database logs
docker-compose logs postgres

# Check connection count
docker-compose exec postgres psql -U ianleblanc -d postgres -c "
SELECT count(*) FROM pg_stat_activity;
"
```

#### Performance Issues

```bash
# Check slow queries
docker-compose exec postgres psql -U ianleblanc -d postgres -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# Check database size
docker-compose exec postgres psql -U ianleblanc -d postgres -c "
SELECT pg_size_pretty(pg_database_size('postgres'));
"

# Check table sizes
docker-compose exec postgres psql -U ianleblanc -d postgres -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

#### Recovery Procedures

```bash
# Restart database
docker-compose restart postgres

# Check database integrity
docker-compose exec postgres psql -U ianleblanc -d postgres -c "VACUUM ANALYZE;"

# Rebuild indexes
docker-compose exec postgres psql -U ianleblanc -d postgres -c "REINDEX DATABASE postgres;"
```

### Redis Issues

#### Connection Problems

```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Check Redis info
docker-compose exec redis redis-cli info
```

#### Performance Issues

```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Check Redis performance
docker-compose exec redis redis-cli info stats

# Check slow queries
docker-compose exec redis redis-cli slowlog get 10
```

#### Recovery Procedures

```bash
# Restart Redis
docker-compose restart redis

# Clear Redis cache
docker-compose exec redis redis-cli flushall

# Check Redis persistence
docker-compose exec redis redis-cli info persistence
```

## Authentication Issues

### JWT Token Issues

#### Token Validation Errors

```bash
# Check JWT configuration
docker-compose exec api python -c "
from personal_assistant.core.config import settings
print(f'JWT Secret: {settings.JWT_SECRET_KEY[:10]}...')
print(f'JWT Algorithm: {settings.JWT_ALGORITHM}')
print(f'JWT Expiration: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}')
"

# Test token generation
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

#### Token Refresh Issues

```bash
# Check refresh token endpoint
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"your_refresh_token"}'

# Check token storage
docker-compose exec api python -c "
from personal_assistant.database.models.auth_tokens import AuthToken
from personal_assistant.database.connection import get_db
db = next(get_db())
tokens = db.query(AuthToken).all()
print(f'Active tokens: {len(tokens)}')
"
```

### MFA Issues

#### TOTP Setup Problems

```bash
# Check MFA configuration
docker-compose exec api python -c "
from personal_assistant.database.models.mfa_models import MFAConfiguration
from personal_assistant.database.connection import get_db
db = next(get_db())
mfa_configs = db.query(MFAConfiguration).all()
print(f'MFA configurations: {len(mfa_configs)}')
"

# Test TOTP setup
curl -X POST http://localhost:8000/api/mfa/setup/totp \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json"
```

#### SMS MFA Issues

```bash
# Check SMS configuration
docker-compose exec api python -c "
from personal_assistant.core.config import settings
print(f'Twilio SID: {settings.TWILIO_ACCOUNT_SID}')
print(f'Twilio Token: {settings.TWILIO_AUTH_TOKEN[:10]}...')
"

# Test SMS MFA
curl -X POST http://localhost:8000/api/mfa/setup/sms \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+1234567890"}'
```

## OAuth Integration Issues

### Google OAuth Issues

#### Configuration Problems

```bash
# Check Google OAuth configuration
docker-compose exec api python -c "
from personal_assistant.core.config import settings
print(f'Google Client ID: {settings.GOOGLE_OAUTH_CLIENT_ID}')
print(f'Google Redirect URI: {settings.GOOGLE_OAUTH_REDIRECT_URI}')
"

# Test Google OAuth flow
curl -X GET "http://localhost:8000/api/oauth/initiate?provider=google"
```

#### Token Refresh Issues

```bash
# Check OAuth token storage
docker-compose exec api python -c "
from personal_assistant.database.models.oauth_models import OAuthIntegration
from personal_assistant.database.connection import get_db
db = next(get_db())
integrations = db.query(OAuthIntegration).all()
print(f'OAuth integrations: {len(integrations)}')
"

# Test token refresh
curl -X POST http://localhost:8000/api/oauth/integrations/1/refresh \
  -H "Authorization: Bearer your_token"
```

### Microsoft OAuth Issues

#### Configuration Problems

```bash
# Check Microsoft OAuth configuration
docker-compose exec api python -c "
from personal_assistant.core.config import settings
print(f'Microsoft Client ID: {settings.MICROSOFT_OAUTH_CLIENT_ID}')
print(f'Microsoft Redirect URI: {settings.MICROSOFT_OAUTH_REDIRECT_URI}')
"

# Test Microsoft OAuth flow
curl -X GET "http://localhost:8000/api/oauth/initiate?provider=microsoft"
```

### Notion OAuth Issues

#### Configuration Problems

```bash
# Check Notion OAuth configuration
docker-compose exec api python -c "
from personal_assistant.core.config import settings
print(f'Notion Client ID: {settings.NOTION_OAUTH_CLIENT_ID}')
print(f'Notion Redirect URI: {settings.NOTION_OAUTH_REDIRECT_URI}')
"

# Test Notion OAuth flow
curl -X GET "http://localhost:8000/api/oauth/initiate?provider=notion"
```

## SMS Router Issues

### Twilio Integration Issues

#### Configuration Problems

```bash
# Check Twilio configuration
docker-compose exec api python -c "
from personal_assistant.core.config import settings
print(f'Twilio SID: {settings.TWILIO_ACCOUNT_SID}')
print(f'Twilio Token: {settings.TWILIO_AUTH_TOKEN[:10]}...')
print(f'Twilio From: {settings.TWILIO_FROM_NUMBER}')
"

# Test Twilio connection
curl -X POST http://localhost:8000/api/sms-router/webhook/sms \
  -H "Content-Type: application/json" \
  -d '{"From":"+1234567890","Body":"Test message"}'
```

#### SMS Routing Issues

```bash
# Check SMS routing engine
curl http://localhost:8000/api/sms-router/webhook/stats

# Check phone mappings
curl -H "Authorization: Bearer your_token" \
  http://localhost:8000/api/sms-router/admin/phone-mappings
```

#### Webhook Issues

```bash
# Check webhook health
curl http://localhost:8000/api/sms-router/webhook/health

# Test webhook endpoint
curl -X POST http://localhost:8000/api/sms-router/webhook/sms \
  -H "Content-Type: application/json" \
  -d '{"From":"+1234567890","Body":"Test message"}'
```

## Performance Issues

### High Response Times

#### Database Performance

```bash
# Check database performance
curl http://localhost:8000/health/database/performance

# Check slow queries
docker-compose exec postgres psql -U ianleblanc -d postgres -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"
```

#### Cache Performance

```bash
# Check Redis performance
docker-compose exec redis redis-cli info stats

# Check cache hit rate
docker-compose exec redis redis-cli info memory
```

#### API Performance

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health/overall

# Check API metrics
curl http://localhost:8000/health/database/performance
```

### Memory Issues

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Check API memory
docker-compose exec api python -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
print(f'Available memory: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.2f} GB')
"
```

#### Memory Leaks

```bash
# Check for memory leaks
docker-compose exec api python -c "
import gc
import sys
print(f'Objects: {len(gc.get_objects())}')
print(f'Memory: {sys.getsizeof(gc.get_objects()) / 1024 / 1024:.2f} MB')
"
```

### CPU Issues

#### High CPU Usage

```bash
# Check CPU usage
docker stats

# Check process CPU usage
docker-compose exec api top -p 1
```

## Deployment Issues

### Docker Issues

#### Container Build Failures

```bash
# Check build logs
docker-compose build --no-cache

# Check Docker daemon
docker version

# Check disk space
df -h
```

#### Network Issues

```bash
# Check network connectivity
docker-compose exec api ping redis
docker-compose exec api ping postgres

# Check network configuration
docker network ls
docker network inspect personal_assistant_network
```

#### Volume Issues

```bash
# Check volume mounts
docker-compose exec api ls -la /app
docker-compose exec frontend ls -la /app

# Check volume permissions
docker-compose exec api ls -la /app/logs
```

### Environment Issues

#### Configuration Problems

```bash
# Check environment variables
docker-compose exec api env | grep -E "(DB_|REDIS_|JWT_)"

# Check configuration files
docker-compose exec api cat /app/config/development.env
```

#### SSL/TLS Issues

```bash
# Check SSL certificates
docker-compose exec nginx ls -la /etc/nginx/ssl

# Test SSL configuration
docker-compose exec nginx nginx -t
```

## Monitoring Issues

### Prometheus Issues

#### Scraping Problems

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus status
curl http://localhost:9090/-/healthy

# Check Prometheus logs
docker-compose logs prometheus
```

#### Metric Collection Issues

```bash
# Check metric endpoints
curl http://localhost:8000/health/database/performance

# Check Prometheus configuration
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml
```

### Grafana Issues

#### Dashboard Problems

```bash
# Check Grafana status
curl http://localhost:3000/api/health

# Check Grafana logs
docker-compose logs grafana

# Check datasource connection
curl http://localhost:3000/api/datasources
```

#### Data Source Issues

```bash
# Test Prometheus connection
curl http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up

# Check datasource configuration
curl http://localhost:3000/api/datasources/1
```

### Loki Issues

#### Log Ingestion Problems

```bash
# Check Loki status
curl http://localhost:3100/ready

# Check Loki logs
docker-compose logs loki

# Test log query
curl http://localhost:3100/api/prom/query?query={service="personal_assistant_api"}
```

## Recovery Procedures

### Service Recovery

#### Complete Service Restart

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

#### Individual Service Recovery

```bash
# Restart specific service
docker-compose restart <service-name>

# Rebuild and restart
docker-compose up -d --build <service-name>

# Check service health
curl http://localhost:8000/health/overall
```

### Data Recovery

#### Database Recovery

```bash
# Check database integrity
docker-compose exec postgres psql -U ianleblanc -d postgres -c "VACUUM ANALYZE;"

# Restore from backup (if available)
docker-compose exec postgres psql -U ianleblanc -d postgres < backup.sql
```

#### Redis Recovery

```bash
# Clear Redis cache
docker-compose exec redis redis-cli flushall

# Restart Redis
docker-compose restart redis
```

### Configuration Recovery

#### Environment Recovery

```bash
# Restore environment configuration
cp config/env.example config/development.env

# Restart services
docker-compose restart
```

#### SSL Certificate Recovery

```bash
# Regenerate SSL certificates
docker-compose exec nginx openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem

# Restart nginx
docker-compose restart nginx
```

## Prevention Strategies

### Monitoring and Alerting

1. **Set up comprehensive monitoring**:

   - Prometheus metrics collection
   - Grafana dashboards
   - Loki log aggregation
   - Health check endpoints

2. **Configure proactive alerting**:
   - Critical alerts for immediate attention
   - Warning alerts for potential issues
   - Info alerts for status updates

### Regular Maintenance

1. **Database maintenance**:

   - Regular VACUUM and ANALYZE
   - Index optimization
   - Query performance monitoring
   - Backup verification

2. **System maintenance**:
   - Regular security updates
   - Dependency updates
   - Resource monitoring
   - Log rotation

### Backup Strategies

1. **Database backups**:

   - Daily automated backups
   - Point-in-time recovery
   - Backup verification
   - Offsite storage

2. **Configuration backups**:
   - Environment configuration
   - SSL certificates
   - Docker configurations
   - Monitoring configurations

### Testing Procedures

1. **Regular testing**:

   - Health check testing
   - Performance testing
   - Security testing
   - Disaster recovery testing

2. **Monitoring validation**:
   - Alert testing
   - Dashboard validation
   - Metric accuracy
   - Log completeness

This comprehensive troubleshooting guide provides systematic approaches to identify, diagnose, and resolve issues in the Personal Assistant TDAH system, along with prevention strategies to minimize future problems.
