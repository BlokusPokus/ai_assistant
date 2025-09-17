# Docker Configuration Guide

This guide covers Docker configuration, containerization strategies, and best practices for the Personal Assistant TDAH system.

## Table of Contents

- [Overview](#overview)
- [Docker Architecture](#docker-architecture)
- [Dockerfile Configuration](#dockerfile-configuration)
- [Docker Compose Environments](#docker-compose-environments)
- [Container Optimization](#container-optimization)
- [Security Considerations](#security-considerations)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

## Overview

The Personal Assistant system uses Docker for containerization across multiple environments:

- **Development**: Hot reloading and debugging
- **Staging**: Production-like testing
- **Production**: High availability and security

### Benefits

- **Consistency**: Identical environments across all stages
- **Isolation**: Each service runs in its own container
- **Scalability**: Easy horizontal scaling
- **Portability**: Deploy anywhere Docker runs
- **Security**: Container-level isolation

## Docker Architecture

### Service Architecture

```mermaid
graph TB
    subgraph "Docker Network: personal_assistant_network"
        subgraph "Application Layer"
            API[Personal Assistant API<br/>Port: 8000]
            FRONTEND[React Frontend<br/>Port: 3001]
            WORKER[Celery Worker]
            SCHEDULER[Celery Beat]
        end

        subgraph "Data Layer"
            DB[(PostgreSQL<br/>Port: 5432)]
            REDIS[(Redis<br/>Port: 6379)]
        end

        subgraph "Monitoring Layer"
            PROM[Prometheus<br/>Port: 9090]
            GRAF[Grafana<br/>Port: 3000]
            LOKI[Loki<br/>Port: 3100]
        end

        subgraph "Proxy Layer"
            NGINX[Nginx Reverse Proxy<br/>Ports: 80, 443]
        end
    end

    subgraph "External Services"
        TWILIO[Twilio SMS]
        GOOGLE[Google APIs]
        MICROSOFT[Microsoft Graph]
        NOTION[Notion API]
    end

    NGINX --> API
    NGINX --> FRONTEND
    API --> DB
    API --> REDIS
    WORKER --> REDIS
    SCHEDULER --> REDIS
    API --> TWILIO
    API --> GOOGLE
    API --> MICROSOFT
    API --> NOTION
```

### Container Specifications

| Service        | Image       | Ports   | Resources | Purpose                        |
| -------------- | ----------- | ------- | --------- | ------------------------------ |
| **nginx**      | Custom      | 80, 443 | 256MB RAM | Reverse proxy, SSL termination |
| **frontend**   | Node.js 18  | 3001    | 512MB RAM | React development server       |
| **api**        | Python 3.11 | 8000    | 1GB RAM   | FastAPI application            |
| **worker**     | Python 3.11 | -       | 512MB RAM | Background task processing     |
| **scheduler**  | Python 3.11 | -       | 256MB RAM | Scheduled task management      |
| **redis**      | Redis 7     | 6379    | 256MB RAM | Caching and message broker     |
| **prometheus** | Prometheus  | 9090    | 512MB RAM | Metrics collection             |
| **grafana**    | Grafana     | 3000    | 512MB RAM | Metrics visualization          |
| **loki**       | Loki        | 3100    | 256MB RAM | Log aggregation                |

## Dockerfile Configuration

### Multi-Stage Dockerfile

**File**: `docker/Dockerfile`

```dockerfile
# Multi-stage Dockerfile for Personal Assistant TDAH
# Optimized for production with security hardening

# ===== STAGE 1: Build Environment =====
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===== STAGE 2: Production Runtime =====
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    ENVIRONMENT="production"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies (minimal set)
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/overall || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "apps.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===== STAGE 3: Development (optional) =====
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

# Switch back to app user
USER appuser
```

### Frontend Dockerfile

**File**: `src/apps/frontend/Dockerfile.dev`

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3001

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]
```

## Docker Compose Environments

### Development Environment

**File**: `docker/docker-compose.dev.yml`

```yaml
version: "3.8"

services:
  # Nginx Reverse Proxy - Development
  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    container_name: personal_assistant_nginx_dev
    ports:
      - "8081:80"
      - "8445:443"
    volumes:
      - ./nginx/ssl/dev:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    depends_on:
      - api
    networks:
      - personal_assistant_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Frontend Development Server
  frontend:
    build:
      context: ../src/apps/frontend
      dockerfile: Dockerfile.dev
    container_name: personal_assistant_frontend_dev
    ports:
      - "3001:3001"
    volumes:
      - ../src/apps/frontend:/app:ro
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - api
    networks:
      - personal_assistant_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis Cache and Queue
  redis:
    image: redis:7-alpine
    container_name: personal_assistant_redis
    command: redis-server --appendonly yes --requirepass redis_password
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 30s
    restart: unless-stopped
    networks:
      - personal_assistant_network

  # Personal Assistant API
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: development
    container_name: personal_assistant_api
    env_file:
      - ../config/development.env
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - REAL_DB_URL=postgresql+asyncpg://ianleblanc:password@host.docker.internal:5432/postgres
      - DATABASE_URL=postgresql+asyncpg://ianleblanc:password@host.docker.internal:5432/postgres
      - CELERY_BROKER_URL=redis://:redis_password@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:redis_password@redis:6379/0
      - REDIS_URL=redis://:redis_password@redis:6379/0
    volumes:
      - ../src:/app/src:ro
      - ../config:/app/config:ro
      - ../logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/overall"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
    networks:
      - personal_assistant_network

volumes:
  redis_data:
    driver: local

networks:
  personal_assistant_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Production Environment

**File**: `docker/docker-compose.prod.yml`

```yaml
version: "3.8"

services:
  # Nginx Reverse Proxy - Production
  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    container_name: personal_assistant_nginx_prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl/prod:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    depends_on:
      - api
    networks:
      - personal_assistant_prod_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
        reservations:
          memory: 256M
          cpus: "0.25"

  # PostgreSQL Database - Production
  postgres:
    image: postgres:15-alpine
    container_name: personal_assistant_postgres_prod
    environment:
      POSTGRES_DB: personal_assistant_prod
      POSTGRES_USER: ${PROD_DB_USER}
      POSTGRES_PASSWORD: ${PROD_DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "pg_isready -U ${PROD_DB_USER} -d personal_assistant_prod",
        ]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
        reservations:
          memory: 1G
          cpus: "0.5"

  # Personal Assistant API - Production
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: personal_assistant_api_prod
    env_file:
      - docker/.env.prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    volumes:
      - ../logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/overall"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
        reservations:
          memory: 1G
          cpus: "0.5"

volumes:
  postgres_data_prod:
    driver: local
  redis_data_prod:
    driver: local

networks:
  personal_assistant_prod_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16
```

## Container Optimization

### Image Optimization

1. **Multi-stage Builds**: Separate build and runtime stages
2. **Layer Caching**: Optimize Docker layer caching
3. **Minimal Base Images**: Use slim/alpine variants
4. **Dependency Optimization**: Install only necessary packages

### Resource Optimization

```yaml
# Resource limits example
deploy:
  resources:
    limits:
      memory: 1G
      cpus: "0.5"
    reservations:
      memory: 512M
      cpus: "0.25"
```

### Performance Tuning

```yaml
# Performance optimizations
environment:
  - DB_POOL_SIZE=20
  - DB_MAX_OVERFLOW=30
  - DB_POOL_TIMEOUT=30
  - DB_POOL_RECYCLE=3600
  - DB_POOL_PRE_PING=true
```

## Security Considerations

### Container Security

1. **Non-root User**: All containers run as non-root user
2. **Read-only Filesystems**: Use read-only mounts where possible
3. **Resource Limits**: Set memory and CPU limits
4. **Network Isolation**: Services communicate through internal network
5. **Secrets Management**: Use Docker secrets or environment files

### Security Configuration

```yaml
# Security example
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - CHOWN
  - SETGID
  - SETUID
read_only: true
```

### SSL/TLS Configuration

```nginx
# Nginx SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

## Performance Tuning

### Database Performance

```yaml
# PostgreSQL optimization
environment:
  - POSTGRES_SHARED_BUFFERS=256MB
  - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
  - POSTGRES_MAINTENANCE_WORK_MEM=64MB
  - POSTGRES_CHECKPOINT_COMPLETION_TARGET=0.9
```

### Redis Performance

```yaml
# Redis optimization
command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD} --maxmemory 1gb --maxmemory-policy allkeys-lru
```

### Application Performance

```yaml
# Application optimization
environment:
  - WORKERS=4
  - WORKER_CLASS=uvicorn.workers.UvicornWorker
  - WORKER_CONNECTIONS=1000
  - MAX_REQUESTS=1000
  - MAX_REQUESTS_JITTER=100
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**:

   ```bash
   docker-compose logs <service-name>
   docker-compose ps
   ```

2. **Port Conflicts**:

   ```bash
   netstat -tulpn | grep :8000
   ```

3. **Memory Issues**:

   ```bash
   docker stats
   ```

4. **Network Issues**:
   ```bash
   docker network ls
   docker network inspect personal_assistant_network
   ```

### Debug Commands

```bash
# View container logs
docker-compose logs -f

# Execute commands in container
docker-compose exec api bash

# Check container resource usage
docker stats

# Inspect container configuration
docker inspect <container-name>

# Check network connectivity
docker-compose exec api ping redis
```

### Performance Debugging

```bash
# Check container performance
docker stats --no-stream

# Monitor resource usage
docker-compose exec api top

# Check disk usage
docker system df

# Clean up unused resources
docker system prune
```

## Best Practices

### Development

1. **Use Development Compose**: Always use `docker-compose.dev.yml` for development
2. **Volume Mounting**: Mount source code for hot reloading
3. **Environment Variables**: Use `.env` files for configuration
4. **Health Checks**: Implement comprehensive health checks
5. **Logging**: Use structured logging for debugging

### Production

1. **Security**: Run containers as non-root users
2. **Resource Limits**: Set appropriate CPU and memory limits
3. **Monitoring**: Implement comprehensive monitoring
4. **Backups**: Regular database and volume backups
5. **Updates**: Regular security updates and patches

### Maintenance

1. **Image Updates**: Regularly update base images
2. **Dependency Updates**: Keep dependencies current
3. **Security Scanning**: Regular vulnerability scans
4. **Performance Monitoring**: Continuous performance monitoring
5. **Documentation**: Keep documentation updated

This Docker configuration guide provides comprehensive instructions for containerizing and deploying the Personal Assistant TDAH system with optimal performance, security, and maintainability.
