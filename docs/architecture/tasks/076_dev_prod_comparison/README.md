# Dev vs Prod Environment Comparison Task

## 🎯 Objective

Identify and document discrepancies between development and production environments to stabilize new code launches and prevent deployment issues.

## 📋 Task Overview

**Task ID**: 076_dev_prod_comparison  
**Priority**: High - Critical for production stability  
**Estimated Duration**: 2-3 days  
**Status**: In Progress

## 🏗️ Infrastructure Context

### Production Environment

- **VM**: DigitalOcean Droplet at `165.227.38.1`
- **Domain**: ianleblanc.ca
- **SSH Access**: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1`
- **Project Directory**: `/home/deploy/ai_assistant`
- **Services**: Docker Compose with 15+ containers
- **Monitoring**: Prometheus, Grafana, Loki, Jaeger

### Development Environment

- **Local Machine**: macOS (darwin 23.2.0)
- **Project Directory**: `/Users/ianleblanc/Desktop/personal_assistant`
- **Services**: Local Docker containers or native services
- **Database**: Local PostgreSQL instance

## 🔍 Comparison Areas

### 1. Configuration Files

- [ ] Environment variables comparison
- [ ] Docker compose configurations
- [ ] Nginx configurations
- [ ] SSL certificate differences
- [ ] Database connection strings

### 2. Code Synchronization

- [ ] Git commit differences
- [ ] Uncommitted changes in dev
- [ ] Branch differences
- [ ] Dependency versions
- [ ] Package.json differences

### 3. Service Analysis

- [ ] Running services comparison
- [ ] Docker container status
- [ ] Service health checks
- [ ] Port configurations
- [ ] Resource usage

### 4. Database Analysis

- [ ] Schema comparison
- [ ] Migration status
- [ ] Data differences
- [ ] Index configurations
- [ ] User permissions

### 5. Performance Metrics

- [ ] Response times
- [ ] Error rates
- [ ] Resource utilization
- [ ] Log analysis
- [ ] SSL certificate status

## 🛠️ Tools and Scripts

### Environment Comparison Scripts

- `compare_env_files.sh` - Compare environment configurations
- `check_service_status.sh` - Compare running services
- `compare_database_schemas.sh` - Database schema analysis
- `analyze_logs.sh` - Log comparison and analysis

### Monitoring Scripts

- `check_resource_usage.sh` - Resource utilization comparison
- `test_api_endpoints.sh` - API endpoint testing
- `verify_ssl_certificates.sh` - SSL certificate verification

## 📊 Expected Deliverables

1. **Comprehensive Comparison Report** - Detailed analysis of all differences
2. **Automation Scripts** - Tools to automate future comparisons
3. **Stabilization Recommendations** - Actionable steps to stabilize deployments
4. **Enhanced Monitoring Setup** - Improved production monitoring
5. **Updated Documentation** - Deployment guides reflecting current state

## 🚨 Risk Assessment

### High Risk Areas

- **Database Migrations**: Potential data loss if schemas differ
- **Environment Variables**: Security risks if sensitive data differs
- **SSL Certificates**: Service interruption if certificates differ
- **API Keys**: Service failures if keys differ

### Mitigation Strategies

- **Backup Before Changes**: Always backup production before modifications
- **Staged Rollouts**: Test changes in staging environment first
- **Rollback Plans**: Prepare rollback procedures for each change
- **Enhanced Monitoring**: Monitor during and after changes

## 📈 Success Criteria

- [ ] Complete inventory of all differences between dev and prod
- [ ] Automated tools created for ongoing comparison
- [ ] Clear stabilization plan developed
- [ ] Enhanced production monitoring implemented
- [ ] Updated documentation reflecting current state

## 🔗 Related Documentation

- [Onboarding Guide](./onboarding.md) - Detailed task onboarding
- [Comparison Scripts](./scripts/) - Automation tools
- [Analysis Reports](./reports/) - Comparison results
- [Stabilization Plan](./stabilization_plan.md) - Action plan for stabilization

## 📞 Quick Reference

### Production Server Access

```bash
ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
cd /home/deploy/ai_assistant
```

### Key Monitoring Endpoints

- **Main Site**: https://ianleblanc.ca
- **API Health**: https://ianleblanc.ca/api/health
- **Grafana**: https://ianleblanc.ca:3000
- **Prometheus**: https://ianleblanc.ca:9090

---

**Created**: $(date)  
**Last Updated**: $(date)  
**Next Review**: After completion

