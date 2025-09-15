# 🚀 Bloop Personal Assistant - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying future versions of the Bloop Personal Assistant application to the production DigitalOcean VM at `ianleblanc.ca`.

## Prerequisites

- DigitalOcean droplet running at `165.227.38.1`
- SSH access with key `~/.ssh/do_personal_assistant`
- Domain `ianleblanc.ca` configured with DNS records
- SSL certificates installed and working

## 🏗️ Infrastructure Status

- **VM**: DigitalOcean Droplet (2 vCPU, 4GB RAM, 80GB SSD)
- **Domain**: ianleblanc.ca
- **SSL**: Let's Encrypt certificates (auto-renewal configured)
- **Services**: Docker Compose with 15+ containers
- **Monitoring**: Prometheus, Grafana, Loki, Jaeger

---

## 📋 Pre-Deployment Checklist

### 1. Local Development

- [ ] Code changes tested locally
- [ ] All tests passing
- [ ] Frontend builds successfully (`npm run build`)
- [ ] No sensitive data in code (use environment variables)
- [ ] Database migrations tested locally
- [ ] **Database backup created before deployment**
- [ ] **Migration rollback tested locally**

### 2. Code Repository

- [ ] Changes committed to Git
- [ ] Pushed to GitHub repository
- [ ] No secrets in commit history
- [ ] Environment files excluded from Git

### 3. Environment Configuration

- [ ] Update `config/production.env` with new variables if needed
- [ ] Update `docker/.env.prod` with new secrets if needed
- [ ] Verify all API keys and credentials are current

---

## 🚀 Deployment Process

### Step 1: Connect to Production Server

```bash
# SSH into the production server
ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1

# Navigate to project directory
cd /home/deploy/ai_assistant
```

### Step 2: Pull Latest Code

```bash
# Pull latest changes from GitHub
git pull origin main

# Verify you're on the correct branch
git branch
git log --oneline -5
```

### Step 3: Update Environment Files (if needed)

```bash
# If new environment variables were added, update them
nano config/production.env
nano docker/.env.prod

# Copy production env to docker env (docker-compose looks for .env by default)
cp docker/.env.prod docker/.env
```

### Step 4: Database Migrations

```bash
# Navigate to docker directory
cd docker

# CRITICAL: Create backup before migration
docker exec personal_assistant_postgres_prod pg_dump -U prod_user personal_assistant_prod > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

# Run database migrations
docker exec personal_assistant_api_prod python -m alembic upgrade head

# Verify database schema
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod -c "\dt"

# Verify migration was successful
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod -c "SELECT * FROM migration_history ORDER BY applied_at DESC LIMIT 5;"
```

### Step 5: Build Frontend (if frontend changes)

```bash
# Navigate to frontend directory
cd /home/deploy/ai_assistant/src/apps/frontend

# Install dependencies (if package.json changed)
npm install

# Build frontend for production
npx vite build

# Copy built files to nginx directory
cp -r dist/* /home/deploy/ai_assistant/docker/nginx/html/
```

### Step 6: Rebuild and Restart Services

```bash
# Navigate to docker directory
cd /home/deploy/ai_assistant/docker

# Rebuild containers (if code changes)
docker-compose -f docker-compose.prod.yml build

# Restart services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

### Step 7: Verify Deployment

```bash
# Test frontend
curl -k https://ianleblanc.ca/ | head -10

# Test API health
curl -k https://ianleblanc.ca/api/health

# Test static assets
curl -k https://ianleblanc.ca/assets/index-*.js | head -5

# Test images
curl -k https://ianleblanc.ca/image.png

# Check service logs
docker logs personal_assistant_api_prod --tail 20
docker logs personal_assistant_nginx_prod --tail 20
```

---

## 🔧 Common Issues & Solutions

### Frontend Not Loading

**Problem**: Website shows nginx default page or 404 errors
**Solution**:

```bash
# Check if frontend files exist
ls -la /home/deploy/ai_assistant/docker/nginx/html/

# Rebuild and copy frontend
cd /home/deploy/ai_assistant/src/apps/frontend
npx vite build
cp -r dist/* /home/deploy/ai_assistant/docker/nginx/html/

# Restart nginx
cd /home/deploy/ai_assistant/docker
docker-compose -f docker-compose.prod.yml restart nginx
```

### Assets 404 Errors

**Problem**: JavaScript/CSS files return 404
**Solution**:

```bash
# Check nginx configuration
docker exec personal_assistant_nginx_prod cat /etc/nginx/conf.d/ssl.conf | grep -A 5 "location /assets/"

# Reload nginx configuration
docker exec personal_assistant_nginx_prod nginx -s reload
```

### Database Connection Issues

**Problem**: API returns database errors
**Solution**:

```bash
# Check database status
docker exec personal_assistant_postgres_prod pg_isready -U prod_user

# Run migrations
docker exec personal_assistant_api_prod python -m alembic upgrade head

# Check database tables
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod -c "\dt"
```

### Service Health Issues

**Problem**: Services showing as unhealthy
**Solution**:

```bash
# Check service logs
docker logs personal_assistant_api_prod --tail 50
docker logs personal_assistant_redis_prod --tail 20

# Restart specific service
docker-compose -f docker-compose.prod.yml restart api
```

---

## 🔄 Rollback Procedure

### Quick Rollback (if recent deployment)

```bash
# Revert to previous commit
git log --oneline -5
git reset --hard HEAD~1

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Database Rollback

```bash
# Check migration history
docker exec personal_assistant_api_prod python -m alembic history

# Rollback to previous migration
docker exec personal_assistant_api_prod python -m alembic downgrade -1
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Check resource usage
docker stats --no-stream

# Check disk space
df -h
```

### Log Monitoring

```bash
# API logs
docker logs personal_assistant_api_prod -f

# Nginx logs
docker logs personal_assistant_nginx_prod -f

# Database logs
docker logs personal_assistant_postgres_prod -f
```

### Backup Procedures

```bash
# Database backup
docker exec personal_assistant_postgres_prod pg_dump -U prod_user personal_assistant_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d_%H%M%S).tar.gz /home/deploy/ai_assistant/
```

---

## 🗄️ Database Safety & Data Protection

### Data Persistence Guarantees

**Your data is protected by:**

- ✅ **Persistent Docker volumes** - Data survives container restarts
- ✅ **Automated health checks** - Early problem detection
- ✅ **Resource limits** - Prevents system overload
- ✅ **Migration safety** - Checksums, rollbacks, transactions
- ✅ **Network isolation** - Security from external threats

### Safe Migration Process

```bash
# 1. ALWAYS backup before migration
docker exec personal_assistant_postgres_prod pg_dump -U prod_user personal_assistant_prod > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

# 2. Test migration locally first (if possible)
# 3. Apply migration
docker exec personal_assistant_api_prod python -m alembic upgrade head

# 4. Verify migration success
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod -c "SELECT * FROM migration_history ORDER BY applied_at DESC LIMIT 5;"

# 5. Test application functionality
curl -k https://ianleblanc.ca/api/health
```

### Automated Backups

```bash
# Setup daily automated backup (run once)
echo "0 2 * * * cd /home/deploy/ai_assistant && docker exec personal_assistant_postgres_prod pg_dump -U prod_user personal_assistant_prod > backups/daily_backup_\$(date +\%Y\%m\%d).sql" | crontab -

# Manual backup
docker exec personal_assistant_postgres_prod pg_dump -U prod_user personal_assistant_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Disaster Recovery

#### If Database Container Crashes:

```bash
# Check container status
docker ps -a | grep postgres

# Restart if needed (data is preserved in persistent volume)
docker-compose -f docker-compose.prod.yml restart postgres

# Verify data integrity
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod -c "SELECT COUNT(*) FROM users;"
```

#### If Database Data is Corrupted:

```bash
# Stop application
docker-compose -f docker-compose.prod.yml stop api

# Restore from backup
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod < latest_backup.sql

# Restart application
docker-compose -f docker-compose.prod.yml start api
```

#### If Entire VM is Lost:

```bash
# 1. Create new VM
# 2. Restore from GitHub (code)
# 3. Restore from backup (data)
# 4. Reconfigure environment
```

### Database Health Monitoring

```bash
# Check database health
docker exec personal_assistant_postgres_prod pg_isready -U prod_user

# Check database size
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod -c "SELECT pg_size_pretty(pg_database_size('personal_assistant_prod'));"

# Check active connections
docker exec personal_assistant_postgres_prod psql -U prod_user -d personal_assistant_prod -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'personal_assistant_prod';"
```

---

## 🔐 Security Considerations

### Environment Variables

- Never commit `.env` files to Git
- Use `scp` to transfer sensitive files
- Rotate API keys regularly
- Monitor for exposed secrets

### SSL Certificates

- Certificates auto-renew via Let's Encrypt
- Monitor certificate expiration
- Test HTTPS endpoints after deployment

### Access Control

- Use SSH keys for server access
- Limit root access
- Monitor failed login attempts

---

## 📞 Emergency Contacts & Resources

### DigitalOcean Resources

- **Droplet IP**: 165.227.38.1
- **Domain**: ianleblanc.ca
- **SSH Key**: `~/.ssh/do_personal_assistant`

### Service URLs

- **Main Site**: https://ianleblanc.ca
- **API Docs**: https://ianleblanc.ca/api/docs (requires auth)
- **Grafana**: https://ianleblanc.ca:3000
- **Prometheus**: https://ianleblanc.ca:9090

### Monitoring

- **Grafana Dashboard**: Port 3000
- **Prometheus Metrics**: Port 9090
- **Jaeger Tracing**: Port 16686

---

## ✅ Post-Deployment Verification

### Functional Tests

- [ ] Website loads correctly
- [ ] OAuth login works (Google/Microsoft)
- [ ] API endpoints respond
- [ ] Database queries work
- [ ] Static assets load
- [ ] SSL certificate valid

### Performance Tests

- [ ] Page load times acceptable
- [ ] API response times < 2s
- [ ] Database queries optimized
- [ ] Memory usage stable

### Security Tests

- [ ] HTTPS redirects working
- [ ] No sensitive data exposed
- [ ] Authentication required for protected endpoints
- [ ] CORS configured correctly

---

## 📝 Deployment Log Template

```
Deployment Date: [DATE]
Deployed By: [NAME]
Version: [GIT_COMMIT_HASH]
Changes: [BRIEF_DESCRIPTION]

Pre-deployment:
- [ ] Code tested locally
- [ ] Database migrations verified
- [ ] Environment variables updated

Deployment Steps:
- [ ] Code pulled from Git
- [ ] Database migrations run
- [ ] Frontend built and deployed
- [ ] Services restarted
- [ ] Health checks passed

Post-deployment:
- [ ] Website functional
- [ ] API responding
- [ ] OAuth working
- [ ] Monitoring active

Issues Encountered:
[DESCRIBE_ANY_ISSUES]

Resolution:
[DESCRIBE_HOW_ISSUES_WERE_RESOLVED]
```

---

## 🎯 Quick Reference Commands

```bash
# Connect to server
ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1

# Navigate to project
cd /home/deploy/ai_assistant

# Pull latest code
git pull origin main

# Run migrations
cd docker && docker exec personal_assistant_api_prod python -m alembic upgrade head

# Build frontend
cd ../src/apps/frontend && npx vite build && cp -r dist/* ../../docker/nginx/html/

# Restart services
cd ../../docker && docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# Test deployment
curl -k https://ianleblanc.ca/ | head -5
```

---

_Last Updated: September 13, 2025_
_Version: 1.0_
