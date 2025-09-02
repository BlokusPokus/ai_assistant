# 🚀 CI/CD Pipeline Quick Start Guide

## 📋 Quick Overview

The Personal Assistant TDAH CI/CD pipeline automates testing, security scanning, and deployment across three environments: development, staging, and production.

## 🎯 What Happens When You Push Code

### 1. **Push to `develop` branch**

```
Code Push → CI Pipeline → Tests → Security → Auto Deploy to Dev
```

- **Time**: ~25-35 minutes
- **Deployment**: Automatic to development
- **Approval**: None required

### 2. **Push to `main` branch**

```
Code Push → CI Pipeline → Tests → Security → Ready for Staging
```

- **Time**: ~25-35 minutes
- **Deployment**: Manual to staging (requires approval)
- **Approval**: Required for staging and production

## 🔧 Pipeline Components

### **CI Pipeline** (ci.yml)

- ✅ Code quality checks (linting, formatting, type checking)
- ✅ Unit tests (2-3 minutes)
- ✅ Integration tests (5-8 minutes)
- ✅ End-to-end tests (10-15 minutes)
- ✅ Performance tests (15-20 minutes)
- ✅ Docker image building
- ✅ Security scanning

### **Test Pipeline** (test.yml)

- ✅ Parallel test execution
- ✅ Test result caching
- ✅ Coverage analysis
- ✅ Performance benchmarking

### **Security Pipeline** (security.yml)

- ✅ Dependency vulnerability scanning
- ✅ Code security analysis
- ✅ Container security scanning
- ✅ Secret detection
- ✅ License compliance

### **Deployment Pipelines**

- ✅ **Development**: Auto-deploy on `develop` push
- ✅ **Staging**: Manual deploy with approval gate
- ✅ **Production**: Manual deploy with blue-green strategy

## 🌍 Environment Details

| Environment     | URL                                          | Deployment | Approval | Rollback   |
| --------------- | -------------------------------------------- | ---------- | -------- | ---------- |
| **Development** | `http://dev.personal-assistant.com:8000`     | Automatic  | None     | Automatic  |
| **Staging**     | `http://staging.personal-assistant.com:8001` | Manual     | Required | Automatic  |
| **Production**  | `http://personal-assistant.com`              | Manual     | Required | Blue-Green |

## 🚀 How to Deploy

### **Development Deployment**

```bash
# Just push to develop branch
git push origin develop
# Deployment happens automatically
```

### **Staging Deployment**

1. Go to GitHub Actions
2. Select "Deploy to Staging" workflow
3. Click "Run workflow"
4. Approve in GitHub environment settings
5. Monitor deployment progress

### **Production Deployment**

1. Go to GitHub Actions
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Approve in GitHub environment settings
5. Monitor blue-green deployment

## 🛡️ Quality Gates

### **Code Quality**

- Black formatting check
- isort import sorting
- Flake8 linting
- MyPy type checking
- Frontend linting

### **Test Coverage**

- Minimum: 85% overall
- Unit tests: >90%
- Integration tests: >80%
- E2E tests: >70%

### **Security**

- No critical vulnerabilities
- No high-severity code issues
- No secrets in codebase
- License compliance

### **Performance**

- API response time: <2 seconds
- Database queries: <500ms
- Memory usage: <512MB
- CPU usage: <80%

## 📊 Monitoring & Health Checks

### **Health Endpoints**

- `/health/overall` - System health
- `/health/database` - Database status
- `/health/database/pool` - Connection pool
- `/metrics` - Prometheus metrics

### **Monitoring Stack**

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Loki**: Log aggregation
- **Structured Logging**: JSON format with correlation IDs

## 🔧 Troubleshooting

### **Pipeline Failed?**

1. Check GitHub Actions logs
2. Look for specific error messages
3. Fix the issue locally
4. Push the fix

### **Deployment Failed?**

1. Check health endpoints
2. Review service logs
3. Automatic rollback should trigger
4. Manual rollback if needed

### **Health Checks Failing?**

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Test health endpoint
curl -f http://localhost:8000/health/overall
```

## 📈 Success Metrics

### **Pipeline Performance**

- CI Pipeline: 25-35 minutes
- Test Execution: 15-25 minutes
- Deployment: 5-10 minutes
- Rollback: <5 minutes

### **Quality Metrics**

- Test Coverage: >85%
- Code Quality: >90%
- Security Score: >95%
- Performance: >90%

## 🎯 Best Practices

### **Before Committing**

- Run linting: `black src/ && isort src/`
- Run tests: `pytest tests/unit/`
- Check security: `safety check && bandit -r src/`

### **Commit Messages**

- Use conventional commits: `feat:`, `fix:`, `chore:`
- Be descriptive and clear
- Reference issues when applicable

### **Pull Requests**

- Ensure all tests pass
- Request code review
- Update documentation if needed
- Test locally before pushing

## 🆘 Getting Help

### **Documentation**

- Full guide: `docs/CI_CD_PIPELINE_GUIDE.md`
- Workflow files: `.github/workflows/`
- Configuration: `config/` directory

### **Support**

- **Issues**: Create GitHub issue
- **Security**: security@personal-assistant.com
- **General**: ianleblanc@personal-assistant.com

### **Resources**

- GitHub Actions: Actions tab in repository
- Test Results: Codecov dashboard
- Security: GitHub Security tab
- Monitoring: Grafana dashboards

---

## 🎉 Quick Commands

```bash
# Check pipeline status
gh run list

# View latest run
gh run view

# Download logs
gh run download

# Rerun failed workflow
gh run rerun

# Check health
curl -f http://localhost:8000/health/overall

# View metrics
curl -f http://localhost:8000/metrics
```

---

_This quick start guide gets you up and running with the CI/CD pipeline. For detailed information, see the full [CI/CD Pipeline Guide](CI_CD_PIPELINE_GUIDE.md)._
