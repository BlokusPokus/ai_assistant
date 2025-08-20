# 🐳 Docker Containerization - Personal Assistant TDAH

This directory contains the Docker configuration for the Personal Assistant TDAH project with support for multiple environments.

## 📁 Files Overview

- **`Dockerfile`** - Multi-stage Dockerfile optimized for production
- **`docker-compose.dev.yml`** - Development environment (hot reload, debugging)
- **`docker-compose.stage.yml`** - Staging environment (production-like testing)
- **`docker-compose.prod.yml`** - Production environment (high availability, security)
- **`env.stage.example`** - Staging environment variables template
- **`env.prod.example`** - Production environment variables template
- **`monitoring/`** - Monitoring stack configurations

## 🚀 Quick Start

### Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Staging Environment

```bash
# Copy environment template
cp env.stage.example .env.stage
# Edit .env.stage with your values

# Start staging environment
docker-compose -f docker-compose.stage.yml --env-file .env.stage up -d

# View logs
docker-compose -f docker-compose.stage.yml logs -f

# Stop services
docker-compose -f docker-compose.stage.yml down
```

### Production Environment

```bash
# Copy environment template
cp env.prod.example .env.prod
# Edit .env.prod with your secure values

# Start production environment
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## 🔧 Service Ports

### Development

- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### Staging

- **API**: http://localhost:8001
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380
- **Prometheus**: http://localhost:9091
- **Grafana**: http://localhost:3001

### Production

- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Loki**: http://localhost:3100
- **Jaeger**: http://localhost:16686

## 🏗️ Architecture

### Development Environment

- Single API service with hot reload
- Basic monitoring stack
- Development tools and debugging enabled
- Local volume mounts for code changes

### Staging Environment

- Production-like configuration
- Different ports to avoid conflicts
- Test data and configurations
- Performance testing capabilities

### Production Environment

- High availability with resource limits
- Advanced monitoring (Loki, Jaeger)
- Security hardening
- Resource management and scaling
- Backup volume configuration

## 🔒 Security Features

- **Non-root containers**: All services run as non-root users
- **Network isolation**: Separate networks for each environment
- **Secret management**: Environment variables for sensitive data
- **Health checks**: Comprehensive health monitoring
- **Resource limits**: CPU and memory constraints

## 📊 Monitoring & Observability

### Metrics Collection

- **Prometheus**: System and application metrics
- **Grafana**: Dashboards and visualization
- **Custom metrics**: Application-specific performance data

### Logging

- **Loki**: Log aggregation and querying
- **Structured logging**: JSON format for easy parsing
- **Log retention**: Configurable retention policies

### Tracing

- **Jaeger**: Distributed tracing for microservices
- **Request tracking**: End-to-end request flow
- **Performance analysis**: Bottleneck identification

## 🚨 Health Checks

All services include health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/overall"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

## 🔄 Service Dependencies

Services start in the correct order:

1. **Database Layer**: PostgreSQL and Redis
2. **Application Layer**: API, Workers, Scheduler
3. **Monitoring Layer**: Prometheus, Grafana, Loki, Jaeger

## 📈 Performance Optimization

### Database

- Connection pooling with configurable sizes
- Query performance monitoring
- Index usage analysis
- Table bloat detection

### Redis

- Memory limits and eviction policies
- Persistence configuration
- Connection pooling

### Application

- Worker scaling and concurrency
- Task queue management
- Resource monitoring

## 🛠️ Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure no other services use the required ports
2. **Permission Issues**: Check file permissions for mounted volumes
3. **Memory Issues**: Adjust resource limits in docker-compose files
4. **Database Connection**: Verify database credentials and network connectivity

### Debug Commands

```bash
# Check service status
docker-compose -f docker-compose.dev.yml ps

# View service logs
docker-compose -f docker-compose.dev.yml logs api

# Access container shell
docker exec -it personal_assistant_api_dev /bin/bash

# Check resource usage
docker stats
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Monitoring Stack Documentation](https://prometheus.io/docs/)
- [Security Hardening Guide](https://docs.docker.com/engine/security/)

## 🎯 Next Steps

After containerization is complete:

1. **Task 2.2.3**: Configure Nginx reverse proxy
2. **Task 2.3**: Develop API endpoints
3. **Task 2.4**: Build user interface
4. **Production Deployment**: Deploy to production servers
