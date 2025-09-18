# Task 087: Production vs Development Config/Env Files Comparison

## Overview

This task focuses on comparing configuration and environment files between the production and development environments using direct SSH access to the production server. The goal is to identify missing variables that were manually added to production and ensure complete synchronization.

## Problem Statement

The production environment configuration was set up manually, which means some environment variables present in the development configuration might be missing from production. This could lead to:

- Service failures due to missing configuration
- Inconsistent behavior between environments
- Security vulnerabilities from misconfigured variables
- Deployment issues when promoting code from dev to prod

## Objectives

### Primary Goals

1. **Direct SSH Comparison**: Access production server via SSH to get accurate current configuration
2. **Missing Variables Identification**: Find variables present in dev but missing in prod
3. **Configuration Synchronization**: Update production with missing variables
4. **Security Review**: Ensure all sensitive variables are properly configured
5. **Documentation**: Document all differences and updates made

### Secondary Goals

1. **Automation**: Create scripts for ongoing comparison
2. **Validation**: Verify all services work after updates
3. **Backup Strategy**: Implement safe backup and rollback procedures

## Approach

### Phase 1: Discovery

- Connect to production server via SSH
- Locate all environment files
- Document current production state

### Phase 2: Comparison

- Compare local dev files with production files
- Identify missing variables
- Analyze differences and their impact

### Phase 3: Synchronization

- Backup production configuration
- Add missing variables to production
- Update values for production environment

### Phase 4: Validation

- Test all services after updates
- Verify API endpoints functionality
- Monitor logs for errors

## Files to Compare

### Local Development Files

- `config/development.env` (113 lines)
- `config/production.env` (103 lines)
- `config/env.example` (89 lines)
- `config/test.env`
- `docker/env.prod.example`
- `docker/env.stage.example`

### Production Files (via SSH)

- `/home/deploy/ai_assistant/config/production.env`
- `/home/deploy/ai_assistant/docker/.env.prod`
- `/home/deploy/ai_assistant/docker/.env.stage` (if exists)
- Any other environment files found

## Key Areas of Focus

### 1. Database Configuration

- Connection strings
- Credentials
- Pool settings

### 2. OAuth Configuration

- Client IDs and secrets
- Redirect URIs (localhost vs production domain)
- Tenant IDs

### 3. API Keys and Secrets

- Google API keys
- Twilio credentials
- Microsoft credentials
- Notion API keys
- Qdrant configuration

### 4. Logging Configuration

- Log levels
- Output destinations
- Structured logging settings

### 5. Service Configuration

- Celery/Redis settings
- Vector database URLs
- State management settings

## Expected Outcomes

1. **Complete Configuration Sync**: All necessary variables present in production
2. **Documented Differences**: Clear record of what was missing and what was added
3. **Automated Tools**: Scripts for ongoing comparison and updates
4. **Validated Functionality**: Confirmation that all services work correctly
5. **Updated Documentation**: Configuration guides reflect current state

## Success Criteria

- [ ] All environment files compared via SSH
- [ ] Missing variables identified and documented
- [ ] Production configuration updated with missing variables
- [ ] All services validated and working
- [ ] Automation scripts created
- [ ] Documentation updated
- [ ] Backup and rollback procedures tested

## Risk Mitigation

- **Backup Before Changes**: Always backup production before modifications
- **Staged Updates**: Update one file at a time and test
- **Rollback Plan**: Keep original files for quick rollback
- **Monitoring**: Watch logs and metrics during updates
- **Validation**: Test all critical functionality after updates

## Timeline

- **Day 1**: SSH connection, file discovery, and comparison
- **Day 2**: Updates, validation, and documentation

## Dependencies

- SSH access to production server (165.227.38.1)
- Current development environment
- Backup capabilities for production files

## Related Tasks

- Task 076: Dev vs Prod Comparison (broader scope)
- Task 075: Production VM Deployment
- Task 081: Production Deployment Microsoft OAuth
