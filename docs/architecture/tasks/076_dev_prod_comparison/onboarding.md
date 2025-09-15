# Dev vs Prod Environment Comparison Task - Onboarding

## Task Overview

**Task ID**: 076_dev_prod_comparison  
**Objective**: Identify and document discrepancies between development and production environments to stabilize new code launches  
**Priority**: High - Critical for production stability

## Context Analysis

### Current Infrastructure Status

**Production Environment:**

- **VM**: DigitalOcean Droplet at `165.227.38.1`
- **Domain**: ianleblanc.ca
- **SSH Access**: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1`
- **Project Directory**: `/home/deploy/ai_assistant`
- **Services**: Docker Compose with 15+ containers
- **Monitoring**: Prometheus, Grafana, Loki, Jaeger

**Development Environment:**

- **Local Machine**: macOS (darwin 23.2.0)
- **Project Directory**: `/Users/ianleblanc/Desktop/personal_assistant`
- **Services**: Local Docker containers or native services
- **Database**: Local PostgreSQL instance

### Key Configuration Files Identified

**Environment Configurations:**

- `config/development.env` - Local development settings
- `config/production.env` - Production environment settings
- `docker/env.prod.example` - Docker production template
- `docker/docker-compose.dev.yml` - Development Docker setup
- `docker/docker-compose.prod.yml` - Production Docker setup

**Deployment Configuration:**

- `docker/deploy.sh` - Deployment automation script
- `docs/architecture/tasks/075_production_vm_deployment/DEPLOYMENT_GUIDE.md` - Production deployment guide

## Critical Differences Already Identified

### 1. Environment Variables

- **Debug Settings**: Dev has `DEBUG=true`, Prod has `DEBUG=false`
- **Log Levels**: Dev uses `DEBUG` level, Prod uses `INFO/WARNING`
- **Database URLs**: Different connection strings and credentials
- **OAuth Redirect URIs**: Dev uses `localhost:8000`, Prod uses `ianleblanc.ca`

### 2. Docker Configuration

- **Ports**: Dev uses `8080:80`, Prod uses `80:80`
- **SSL**: Different SSL certificate paths
- **Resource Limits**: Prod has memory/CPU limits, Dev doesn't
- **Health Checks**: Different configurations

### 3. Database Configuration

- **Users**: Dev uses `ianleblanc`, Prod uses `prod_user`
- **Passwords**: Different password configurations
- **Pool Settings**: Different connection pool sizes

## Task Scope

### Primary Objectives

1. **Environment Comparison**: Systematic comparison of all configuration files
2. **Code Synchronization**: Identify code differences between dev and prod
3. **Dependency Analysis**: Compare package versions and dependencies
4. **Database Schema**: Compare database schemas and migrations
5. **Service Status**: Compare running services and their configurations
6. **Performance Metrics**: Compare resource usage and performance

### Secondary Objectives

1. **Automation Scripts**: Create scripts to automate comparison process
2. **Documentation**: Document all discrepancies found
3. **Recommendations**: Provide recommendations for stabilization
4. **Monitoring**: Set up monitoring for future deployments

## Methodology

### Phase 1: Configuration Comparison

- Compare all environment files line by line
- Identify missing or different variables
- Document security implications of differences

### Phase 2: Code Synchronization

- Compare Git commits between dev and prod
- Identify uncommitted changes in dev
- Check for configuration drift

### Phase 3: Service Analysis

- Compare running services on both environments
- Analyze Docker container configurations
- Check service health and status

### Phase 4: Database Analysis

- Compare database schemas
- Check migration status
- Analyze data differences

### Phase 5: Performance Comparison

- Compare resource usage
- Analyze response times
- Check error rates and logs

## Tools and Scripts Needed

### SSH Connection Scripts

```bash
# Connect to production server
ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
```

### Environment Comparison Scripts

- Script to compare environment files
- Script to check service status
- Script to compare database schemas
- Script to analyze logs

### Monitoring Scripts

- Script to check resource usage
- Script to test API endpoints
- Script to verify SSL certificates

## Expected Deliverables

1. **Comprehensive Comparison Report**: Detailed analysis of all differences
2. **Automation Scripts**: Tools to automate future comparisons
3. **Stabilization Recommendations**: Actionable steps to stabilize deployments
4. **Monitoring Setup**: Enhanced monitoring for production stability
5. **Documentation**: Updated deployment guides with findings

## Risk Assessment

### High Risk Areas

- **Database Migrations**: Potential data loss if schemas differ
- **Environment Variables**: Security risks if sensitive data differs
- **SSL Certificates**: Service interruption if certificates differ
- **API Keys**: Service failures if keys differ

### Mitigation Strategies

- **Backup Before Changes**: Always backup production before modifications
- **Staged Rollouts**: Test changes in staging environment first
- **Rollback Plans**: Prepare rollback procedures for each change
- **Monitoring**: Enhanced monitoring during and after changes

## Success Criteria

1. **Complete Inventory**: All differences between dev and prod documented
2. **Automated Tools**: Scripts created for ongoing comparison
3. **Stabilization Plan**: Clear roadmap for stabilizing deployments
4. **Monitoring Enhancement**: Improved production monitoring
5. **Documentation**: Updated guides reflecting current state

## Next Steps

1. **Connect to Production**: Establish SSH connection to production server
2. **Gather Current State**: Document current production environment
3. **Run Comparisons**: Execute systematic comparison scripts
4. **Analyze Results**: Identify critical discrepancies
5. **Create Action Plan**: Develop stabilization strategy

## Resources

### Production Server Access

- **IP**: 165.227.38.1
- **SSH Key**: ~/.ssh/do_personal_assistant
- **User**: deploy
- **Project Path**: /home/deploy/ai_assistant

### Key Documentation

- Production Deployment Guide: `docs/architecture/tasks/075_production_vm_deployment/DEPLOYMENT_GUIDE.md`
- Configuration Guide: `config/README.md`
- Production Checklist: `config/PRODUCTION_CHECKLIST.md`

### Monitoring Endpoints

- **Main Site**: https://ianleblanc.ca
- **API Health**: https://ianleblanc.ca/api/health
- **Grafana**: https://ianleblanc.ca:3000
- **Prometheus**: https://ianleblanc.ca:9090

---

**Task Created**: $(date)  
**Status**: Ready for execution  
**Estimated Duration**: 2-3 days  
**Dependencies**: SSH access to production server, current dev environment

