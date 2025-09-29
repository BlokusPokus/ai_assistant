# Comprehensive Manual Configuration Comparison Task - Onboarding

## Task Overview

**Task ID**: 093_comprehensive_config_comparison  
**Objective**: Conduct thorough manual comparison of all configuration files and environment variables between development and production environments  
**Priority**: High - Critical for production stability and configuration consistency  
**Method**: Manual review and analysis without automated scripts

## Context Analysis

### Current Infrastructure Status

**Production Environment:**

- **VM**: DigitalOcean Droplet at `165.227.38.1`
- **Domain**: ianleblanc.ca
- **SSH Access**: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1`
- **Project Directory**: `/home/deploy/ai_assistant`
- **Configuration**: Manually configured with potential inconsistencies
- **Services**: Docker Compose with 15+ containers, monitoring stack

**Development Environment:**

- **Local Machine**: macOS (darwin 23.2.0)
- **Project Directory**: `/Users/ianleblanc/Desktop/personal_assistant`
- **Configuration**: Multiple environment files with different purposes
- **Services**: Local development setup with Docker containers

### Key Configuration Files Identified

**Local Development Files:**

- `config/development.env` - Development settings (113+ lines)
- `config/production.env` - Production template (103+ lines)
- `config/env.example` - Configuration template (89+ lines)
- `config/test.env` - Test environment settings
- `docker/env.prod.example` - Docker production template
- `docker/env.stage.example` - Docker staging template
- `docker/docker-compose.dev.yml` - Development Docker setup
- `docker/docker-compose.prod.yml` - Production Docker setup
- `docker/docker-compose.stage.yml` - Staging Docker setup

**Production Files (via SSH):**

- `/home/deploy/ai_assistant/config/production.env` - Actual production settings
- `/home/deploy/ai_assistant/docker/.env.prod` - Docker production environment
- `/home/deploy/ai_assistant/docker/.env.stage` - Docker staging environment
- Additional configuration files as discovered

**Service-Specific Configurations:**

- Nginx configurations (`docker/nginx/conf.d/`)
- Monitoring configurations (`docker/monitoring/`)
- Database schemas (`database/schemas/`)
- Application configs (`src/personal_assistant/config/`)

## Critical Configuration Areas

### 1. Environment Variables Analysis

**Development Environment (`config/development.env`):**

- `DEBUG=true`, `LOG_LEVEL=DEBUG`, `ENVIRONMENT=development`
- Database: `postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres`
- OAuth Redirect URIs: `http://localhost:8000/api/v1/oauth/callback`
- Twilio: `TWILIO_FROM_NUMBER=+18198039358`
- Microsoft OAuth: Client ID `8a0cac21-315f-4b82-bb09-1980d664bdbe`
- Notion: Full configuration with API keys
- Logging: Verbose DEBUG levels across all modules

**Production Environment (`config/production.env`):**

- `DEBUG=false`, `LOG_LEVEL=INFO`, `ENVIRONMENT=production`
- Database: `postgresql+asyncpg://prod_user:prod_password@postgres:5432/personal_assistant_prod`
- OAuth Redirect URIs: `https://ianleblanc.ca/api/v1/oauth/callback`
- Twilio: `TWILIO_PHONE_NUMBER=+18737002185`
- Microsoft OAuth: Different client ID `efb0e831-6a4d-42f6-8340-e12e49fa3568`
- Notion: Same configuration as dev
- Logging: INFO/WARNING levels for production

### 2. Potential Configuration Issues

Based on initial analysis, potential issues include:

**Missing Variables:**

- `GEMINI_API_KEY` (production has it, dev doesn't)
- `TWILIO_PHONE_NUMBER` (production has it, dev doesn't)
- `MICROSOFT_TENANT_ID` (production has it, dev doesn't)
- Various logging configuration variables
- State management settings
- Vector database configurations

**Inconsistent Variables:**

- Different Microsoft OAuth client IDs between environments
- Different Twilio phone numbers
- Different database connection strings
- Different OAuth redirect URIs

**Security Concerns:**

- API keys and secrets in configuration files
- Database credentials exposure
- OAuth client secrets management

## Task Scope

### Primary Objectives

1. **Complete Configuration Audit**: Manually review every configuration file in both environments
2. **Discrepancy Identification**: Find variables present in one environment but missing in another
3. **Security Review**: Ensure all sensitive variables are properly configured and secured
4. **Documentation**: Create comprehensive documentation of all differences found
5. **Validation**: Verify that all configurations are correct and functional

### Secondary Objectives

1. **Standardization**: Establish consistent configuration patterns across environments
2. **Best Practices**: Document configuration best practices for future reference
3. **Maintenance Guide**: Create guidelines for ongoing configuration management

## Methodology

### Phase 1: Discovery and Documentation

1. **Local Environment Audit**

   - Catalog all configuration files in development environment
   - Document current settings and their purposes
   - Identify configuration patterns and standards

2. **Production Environment Audit**
   - Connect to production server via SSH
   - Discover all configuration files
   - Document current production state
   - Note any custom or additional configurations

### Phase 2: Systematic Comparison

1. **File-by-File Analysis**

   - Compare each configuration file between environments
   - Document differences in structure and content
   - Identify missing variables or configurations

2. **Variable-by-Variable Review**

   - Cross-reference all environment variables
   - Check for inconsistencies in values
   - Verify environment-appropriate settings

3. **Security Assessment**
   - Review sensitive variables and credentials
   - Ensure proper security configurations
   - Check for exposed secrets or weak settings

### Phase 3: Analysis and Documentation

1. **Difference Analysis**

   - Categorize differences by type and impact
   - Identify critical vs. non-critical discrepancies
   - Assess potential risks and issues

2. **Recommendation Development**
   - Propose solutions for identified issues
   - Suggest standardization improvements
   - Create action plan for configuration updates

### Phase 4: Validation and Testing

1. **Configuration Validation**

   - Verify that all configurations are syntactically correct
   - Test critical configurations for functionality
   - Ensure no breaking changes are introduced

2. **Documentation Review**
   - Ensure all findings are properly documented
   - Create comprehensive comparison reports
   - Update configuration guides and documentation

## Tools and Resources Needed

### SSH Connection

```bash
# Connect to production server
ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1

# Navigate to project directory
cd /home/deploy/ai_assistant
```

### File Comparison Tools

- Manual file comparison (no automated scripts)
- Text editors for configuration review
- Documentation tools for reporting

### Access Requirements

- SSH access to production server
- Access to all external service accounts
- Understanding of all application services

## Expected Deliverables

1. **Comprehensive Comparison Report**: Detailed analysis of all configuration differences
2. **Configuration Inventory**: Complete catalog of all configuration files and variables
3. **Security Assessment**: Review of security-related configurations
4. **Recommendations Document**: Actionable recommendations for configuration improvements
5. **Updated Documentation**: Revised configuration guides and best practices
6. **Validation Report**: Confirmation of configuration correctness and functionality

## Risk Assessment

### High Risk Areas

- **Database Configuration**: Wrong database URLs could cause data loss
- **API Keys**: Incorrect keys could break integrations
- **OAuth Configuration**: Wrong redirect URIs could break authentication
- **SSL/TLS Settings**: Incorrect settings could break HTTPS

### Mitigation Strategies

- **Thorough Documentation**: Document all changes and their rationale
- **Validation Testing**: Test all configurations before implementation
- **Backup Procedures**: Maintain backups of all configuration files
- **Gradual Implementation**: Implement changes incrementally with testing

## Success Criteria

1. **Complete Comparison**: All configuration files compared and documented
2. **Discrepancies Identified**: All differences found and categorized
3. **Security Review**: All security-related configurations reviewed
4. **Documentation Updated**: Configuration guides reflect current state
5. **Validation Complete**: All configurations verified as correct and functional

## Next Steps

1. **Connect to Production**: Establish SSH connection to production server
2. **Discover Files**: Find all configuration files in production
3. **Run Comparison**: Execute systematic comparison
4. **Identify Discrepancies**: Document all differences found
5. **Security Review**: Assess security-related configurations
6. **Create Documentation**: Generate comprehensive reports
7. **Validate Findings**: Verify all configurations are correct

## Resources

### Production Server Access

- **IP**: 165.227.38.1
- **SSH Key**: ~/.ssh/do_personal_assistant
- **User**: deploy
- **Project Path**: /home/deploy/ai_assistant

### Key Documentation

- Configuration Guide: `config/README.md`
- Docker Setup: `docker/README.md`
- Production Checklist: `config/PRODUCTION_CHECKLIST.md`
- Previous Comparison: `docs/architecture/tasks/087_prod_dev_config_comparison/`

### Monitoring Endpoints

- **Main Site**: https://ianleblanc.ca
- **API Health**: https://ianleblanc.ca/api/health
- **Grafana**: https://ianleblanc.ca:3000
- **Prometheus**: https://ianleblanc.ca:9090

---

**Task Created**: $(date)  
**Status**: Ready for execution  
**Estimated Duration**: 3-4 days  
**Dependencies**: SSH access to production server, current dev environment, understanding of all services

## Critical Notes

- **Manual Review**: This task focuses on manual comparison without automated scripts
- **Comprehensive Scope**: Covers all configuration layers, not just environment files
- **Security Focus**: Special attention to security-related configurations
- **Documentation Priority**: Thorough documentation of all findings is essential
- **Validation Required**: All configurations must be validated for correctness
