# Production vs Development Config/Env Files Comparison Task - Onboarding

## Task Overview

**Task ID**: 087_prod_dev_config_comparison  
**Objective**: Compare config/env files between production and development environments via SSH to identify missing variables and discrepancies  
**Priority**: High - Critical for production stability and deployment consistency  
**Method**: Direct SSH access to production server for accurate comparison

## Context Analysis

### Current Infrastructure Status

**Production Environment:**

- **VM**: DigitalOcean Droplet at `165.227.38.1`
- **Domain**: ianleblanc.ca
- **SSH Access**: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1`
- **Project Directory**: `/home/deploy/ai_assistant`
- **Environment Files**: Manually configured variables (may be missing some)
- **Services**: Docker Compose with production configuration

**Development Environment:**

- **Local Machine**: macOS (darwin 23.2.0)
- **Project Directory**: `/Users/ianleblanc/Desktop/personal_assistant`
- **Environment Files**: `config/development.env`, `config/production.env`, `config/env.example`
- **Services**: Local development setup

### Key Configuration Files Identified

**Local Development Files:**

- `config/development.env` - Local development settings (113 lines)
- `config/production.env` - Production environment template (103 lines)
- `config/env.example` - Example configuration template (89 lines)
- `config/test.env` - Test environment settings
- `docker/env.prod.example` - Docker production template
- `docker/env.stage.example` - Docker staging template

**Production Files (via SSH):**

- `/home/deploy/ai_assistant/config/production.env` - Actual production settings
- `/home/deploy/ai_assistant/docker/.env.prod` - Docker production environment
- `/home/deploy/ai_assistant/docker/.env.stage` - Docker staging environment (if exists)

## Critical Differences Already Identified

### 1. Environment Variables Analysis

**Development Environment (`config/development.env`):**

- `DEBUG=true`, `LOG_LEVEL=DEBUG`, `ENVIRONMENT=development`
- Database: `postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres`
- OAuth Redirect URIs: `http://localhost:8000/api/v1/oauth/callback`
- Twilio: `TWILIO_FROM_NUMBER=+18198039358`
- Microsoft OAuth: Multiple client IDs (8a0cac21-315f-4b82-bb09-1980d664bdbe)
- Notion: Full configuration with API keys
- Logging: Verbose DEBUG levels across all modules

**Production Environment (`config/production.env`):**

- `DEBUG=false`, `LOG_LEVEL=INFO`, `ENVIRONMENT=production`
- Database: `postgresql+asyncpg://prod_user:prod_password@postgres:5432/personal_assistant_prod`
- OAuth Redirect URIs: `https://ianleblanc.ca/api/v1/oauth/callback`
- Twilio: `TWILIO_FROM_NUMBER=+18737002185`
- Microsoft OAuth: Different client ID (efb0e831-6a4d-42f6-8340-e12e49fa3568)
- Notion: Same configuration as dev
- Logging: INFO/WARNING levels for production

### 2. Potential Missing Variables

Based on the existing comparison report from task 076, production may be missing:

- `GEMINI_API_KEY` (production has it, dev doesn't)
- `TWILIO_PHONE_NUMBER` (production has it, dev doesn't)
- `MICROSOFT_TENANT_ID` (production has it, dev doesn't)
- Various logging configuration variables
- State management settings
- Vector database configurations

## Task Scope

### Primary Objectives

1. **SSH-Based Comparison**: Direct comparison of production files via SSH
2. **Missing Variables Identification**: Find variables present in dev but missing in prod
3. **Configuration Synchronization**: Update production with missing variables
4. **Security Review**: Ensure sensitive variables are properly configured
5. **Documentation**: Document all differences and updates made

### Secondary Objectives

1. **Automation Scripts**: Create scripts for ongoing comparison
2. **Validation**: Verify all services work after updates
3. **Backup Strategy**: Backup production config before changes
4. **Rollback Plan**: Prepare rollback procedures

## Methodology

### Phase 1: SSH Connection and File Discovery

1. **Connect to Production Server**

   ```bash
   ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
   ```

2. **Locate All Environment Files**

   - Find all `.env` files in production
   - Check Docker environment files
   - Identify any custom configuration files

3. **Document Current Production State**
   - List all environment variables
   - Check file permissions and ownership
   - Document any custom configurations

### Phase 2: Systematic Comparison

1. **File-by-File Comparison**

   - Compare `config/production.env` (local) vs production
   - Compare `config/development.env` vs production
   - Compare Docker environment files
   - Check for any additional production-specific files

2. **Variable Analysis**
   - Identify variables present in dev but missing in prod
   - Identify variables present in prod but missing in dev
   - Flag sensitive variables that need special handling
   - Check for deprecated or unused variables

### Phase 3: Update and Synchronization

1. **Backup Production Configuration**

   - Create timestamped backup of all production env files
   - Document current state before changes

2. **Update Missing Variables**

   - Add missing variables to production
   - Ensure proper values for production environment
   - Update OAuth redirect URIs for production domain
   - Configure logging levels appropriately

3. **Validation**
   - Test configuration changes
   - Verify services restart properly
   - Check API endpoints functionality
   - Monitor logs for errors

### Phase 4: Documentation and Automation

1. **Document Changes**

   - Create detailed comparison report
   - Document all variables added/modified
   - Create before/after comparison

2. **Create Automation Scripts**
   - Script for ongoing comparison
   - Script for safe configuration updates
   - Script for validation and testing

## Tools and Scripts Needed

### SSH Connection Scripts

```bash
#!/bin/bash
# connect_to_prod.sh
ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
```

### Environment Comparison Scripts

```bash
#!/bin/bash
# compare_env_files.sh
# Compare local development.env with production env files
# Generate detailed diff reports
```

### Configuration Update Scripts

```bash
#!/bin/bash
# update_prod_config.sh
# Safely update production configuration files
# Include backup and validation steps
```

## Expected Deliverables

1. **Comprehensive Comparison Report**: Detailed analysis of all differences
2. **Updated Production Configuration**: Production env files with missing variables
3. **Automation Scripts**: Tools for ongoing comparison and updates
4. **Documentation**: Updated configuration guides
5. **Validation Report**: Confirmation that all services work after updates

## Risk Assessment

### High Risk Areas

- **Database Configuration**: Wrong database URLs could cause data loss
- **API Keys**: Incorrect keys could break integrations
- **OAuth Configuration**: Wrong redirect URIs could break authentication
- **SSL/TLS Settings**: Incorrect settings could break HTTPS

### Mitigation Strategies

- **Backup Before Changes**: Always backup production before modifications
- **Staged Updates**: Update one file at a time and test
- **Rollback Plan**: Keep original files for quick rollback
- **Monitoring**: Watch logs and metrics during updates
- **Validation**: Test all critical functionality after updates

## Success Criteria

1. **Complete Comparison**: All environment files compared and documented
2. **Missing Variables Added**: All necessary variables added to production
3. **Services Functional**: All services work correctly after updates
4. **Documentation Updated**: Configuration guides reflect current state
5. **Automation Ready**: Scripts created for ongoing maintenance

## Next Steps

1. **Connect to Production**: Establish SSH connection to production server
2. **Discover Files**: Find all environment files in production
3. **Run Comparison**: Execute systematic comparison
4. **Identify Missing Variables**: Document what needs to be added
5. **Update Production**: Safely add missing variables
6. **Validate Changes**: Test all services and functionality
7. **Document Results**: Create comprehensive report

## Resources

### Production Server Access

- **IP**: 165.227.38.1
- **SSH Key**: ~/.ssh/do_personal_assistant
- **User**: deploy
- **Project Path**: /home/deploy/ai_assistant

### Key Documentation

- Previous Comparison: `docs/architecture/tasks/076_dev_prod_comparison/`
- Production Deployment: `docs/architecture/tasks/075_production_vm_deployment/`
- Configuration Guide: `config/README.md`

### Monitoring Endpoints

- **Main Site**: https://ianleblanc.ca
- **API Health**: https://ianleblanc.ca/api/health
- **Grafana**: https://ianleblanc.ca:3000
- **Prometheus**: https://ianleblanc.ca:9090

---

**Task Created**: $(date)  
**Status**: Ready for execution  
**Estimated Duration**: 1-2 days  
**Dependencies**: SSH access to production server, current dev environment

## Critical Notes

- **Manual Configuration**: Production variables were added manually, so some may be missing
- **SSH Required**: Must use SSH to get accurate production configuration
- **Safety First**: Always backup before making changes
- **Test Thoroughly**: Validate all functionality after updates
