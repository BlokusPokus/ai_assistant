# Task 087: Production vs Development Config/Env Files Comparison - Checklist

## Pre-Task Setup

### SSH Access Verification

- [ ] Verify SSH key exists: `~/.ssh/do_personal_assistant`
- [ ] Test SSH connection: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1`
- [ ] Confirm access to production project directory: `/home/deploy/ai_assistant`
- [ ] Verify production server is accessible: `165.227.38.1`

### Local Environment Preparation

- [ ] Confirm local project directory exists: `/Users/ianleblanc/Desktop/personal_assistant`
- [ ] Verify local config files exist:
  - [ ] `config/development.env`
  - [ ] `config/production.env`
  - [ ] `config/env.example`
  - [ ] `config/test.env`
  - [ ] `docker/env.prod.example`
  - [ ] `docker/env.stage.example`

### Script Preparation

- [ ] Make comparison script executable: `chmod +x compare_config_files.sh`
- [ ] Make update script executable: `chmod +x update_prod_config.sh`
- [ ] Review scripts for correct paths and configurations

## Phase 1: Discovery and Comparison

### Production Environment Discovery

- [ ] Run SSH connection test
- [ ] Discover all environment files in production
- [ ] Document production environment information
- [ ] List all running containers and services

### Configuration Comparison

- [ ] Compare `config/development.env` vs production `config/production.env`
- [ ] Compare local `config/production.env` vs actual production `config/production.env`
- [ ] Compare `docker/env.prod.example` vs production `docker/.env.prod`
- [ ] Compare `docker/env.stage.example` vs production `docker/.env.stage` (if exists)
- [ ] Generate detailed diff reports for each comparison

### Missing Variables Analysis

- [ ] Extract variables present in dev but missing in prod
- [ ] Extract variables present in prod but missing in dev
- [ ] Document security implications of missing variables
- [ ] Prioritize variables by importance and impact

## Phase 2: Update and Synchronization

### Backup Strategy

- [ ] Create timestamped backup directory
- [ ] Backup all production environment files before changes
- [ ] Verify backup integrity
- [ ] Document backup locations

### Configuration Updates

- [ ] Review missing variables for production appropriateness
- [ ] Update OAuth redirect URIs for production domain
- [ ] Configure logging levels for production environment
- [ ] Add missing database configuration variables
- [ ] Add missing API keys and secrets
- [ ] Add missing service configuration variables

### Validation

- [ ] Validate updated configuration files syntax
- [ ] Check for duplicate variables
- [ ] Verify all required variables are present
- [ ] Test configuration file readability

## Phase 3: Service Management

### Service Restart (Optional)

- [ ] Stop production services gracefully
- [ ] Start production services with new configuration
- [ ] Monitor service startup logs
- [ ] Verify all containers are running
- [ ] Check service health endpoints

### Endpoint Testing

- [ ] Test main website: `https://ianleblanc.ca`
- [ ] Test API health endpoint: `https://ianleblanc.ca/api/health`
- [ ] Test authentication endpoints
- [ ] Test OAuth callback endpoints
- [ ] Monitor error logs for issues

## Phase 4: Documentation and Cleanup

### Documentation

- [ ] Create comprehensive comparison report
- [ ] Document all variables added/modified
- [ ] Create before/after comparison
- [ ] Update configuration guides
- [ ] Document any issues encountered

### Automation Scripts

- [ ] Test comparison script functionality
- [ ] Test update script functionality
- [ ] Create usage documentation for scripts
- [ ] Add scripts to version control

### Cleanup

- [ ] Remove temporary files
- [ ] Archive old backup files
- [ ] Update task status
- [ ] Close any open issues

## Quality Assurance

### Verification Steps

- [ ] All services are running correctly
- [ ] No error messages in logs
- [ ] All API endpoints responding
- [ ] OAuth flows working correctly
- [ ] Database connections stable
- [ ] Monitoring systems operational

### Rollback Preparation

- [ ] Backup files are accessible
- [ ] Rollback procedures documented
- [ ] Emergency contact information available
- [ ] Service restart procedures tested

## Success Criteria

### Primary Objectives

- [ ] All environment files compared via SSH
- [ ] Missing variables identified and documented
- [ ] Production configuration updated with missing variables
- [ ] All services validated and working
- [ ] Automation scripts created and tested

### Secondary Objectives

- [ ] Documentation updated
- [ ] Backup and rollback procedures tested
- [ ] Monitoring enhanced
- [ ] Future comparison process automated

## Risk Mitigation

### High-Risk Areas

- [ ] Database configuration changes
- [ ] API key and secret updates
- [ ] OAuth configuration modifications
- [ ] SSL/TLS settings changes

### Safety Measures

- [ ] Full backup before any changes
- [ ] Staged updates (one file at a time)
- [ ] Validation after each update
- [ ] Monitoring during and after changes
- [ ] Rollback plan ready

## Post-Task Activities

### Monitoring

- [ ] Monitor production logs for 24 hours
- [ ] Check service metrics and performance
- [ ] Verify all integrations working
- [ ] Monitor error rates and response times

### Documentation Updates

- [ ] Update deployment guides
- [ ] Update configuration documentation
- [ ] Create troubleshooting guides
- [ ] Update team knowledge base

### Process Improvement

- [ ] Review comparison process
- [ ] Identify areas for automation
- [ ] Create standard operating procedures
- [ ] Plan for regular configuration audits

---

## Notes

- **Safety First**: Always backup before making changes
- **Test Thoroughly**: Validate all functionality after updates
- **Monitor Closely**: Watch logs and metrics during updates
- **Document Everything**: Keep detailed records of all changes
- **Plan for Rollback**: Always have a rollback plan ready

## Emergency Contacts

- **Production Server**: 165.227.38.1
- **SSH Access**: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1`
- **Main Site**: https://ianleblanc.ca
- **API Health**: https://ianleblanc.ca/api/health
