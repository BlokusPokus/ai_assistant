# Task 087: Implementation Guide - Production vs Development Config/Env Files Comparison

## Quick Start

### 1. Run the Comparison Script

```bash
cd /Users/ianleblanc/Desktop/personal_assistant/docs/architecture/tasks/087_prod_dev_config_comparison
./compare_config_files.sh
```

This will:

- Connect to production server via SSH
- Discover all environment files in production
- Compare local dev files with production files
- Generate detailed reports in `comparison_results/` directory

### 2. Review the Results

Check the generated files:

- `comparison_results/summary.txt` - High-level summary
- `comparison_results/detailed_analysis.txt` - Detailed differences
- `comparison_results/*_missing_variables.txt` - Missing variables analysis
- `comparison_results/prod_env_info.txt` - Production environment info

### 3. Update Production Configuration (if needed)

```bash
./update_prod_config.sh
```

This will:

- Backup production files
- Add missing variables to production
- Validate updated configuration
- Optionally restart services

## Detailed Implementation Steps

### Step 1: Environment Preparation

1. **Verify SSH Access**

   ```bash
   ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
   ```

2. **Check Local Files**

   ```bash
   ls -la /Users/ianleblanc/Desktop/personal_assistant/config/
   ls -la /Users/ianleblanc/Desktop/personal_assistant/docker/
   ```

3. **Make Scripts Executable**
   ```bash
   chmod +x compare_config_files.sh
   chmod +x update_prod_config.sh
   ```

### Step 2: Run Comparison

1. **Execute Comparison Script**

   ```bash
   ./compare_config_files.sh
   ```

2. **Review Output**

   - Check for SSH connection success
   - Review discovered production files
   - Examine comparison results

3. **Analyze Results**
   - Open `comparison_results/summary.txt`
   - Review missing variables files
   - Check detailed analysis

### Step 3: Update Production (if needed)

1. **Review Missing Variables**

   ```bash
   cat comparison_results/*_missing_variables.txt
   ```

2. **Update Production Configuration**

   ```bash
   ./update_prod_config.sh
   ```

3. **Follow Interactive Prompts**
   - Confirm each update
   - Choose whether to restart services
   - Monitor validation results

### Step 4: Validation

1. **Test Endpoints**

   - https://ianleblanc.ca
   - https://ianleblanc.ca/api/health
   - https://ianleblanc.ca/api/v1/auth/status

2. **Check Service Status**

   ```bash
   ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
   cd /home/deploy/ai_assistant
   docker-compose ps
   ```

3. **Monitor Logs**
   ```bash
   docker-compose logs -f
   ```

## Expected Results

### Comparison Results

The comparison script will generate:

1. **Summary Report** (`summary.txt`)

   - List of files compared
   - High-level differences found
   - Links to detailed analysis

2. **Detailed Analysis** (`detailed_analysis.txt`)

   - Line-by-line differences
   - Context for each change
   - Timestamps and file paths

3. **Missing Variables Analysis** (`*_missing_variables.txt`)

   - Variables in dev but missing in prod
   - Variables in prod but missing in dev
   - Recommended values for production

4. **Production Environment Info** (`prod_env_info.txt`)
   - System information
   - Running containers
   - Environment files metadata

### Update Results

The update script will create:

1. **Backup Files** (`backups/YYYYMMDD_HHMMSS/`)

   - Original production files
   - Timestamped backups
   - Update logs

2. **Update Logs** (`update_log_*.txt`)

   - Variables added
   - Variables skipped
   - Validation results

3. **Validation Reports** (`validation_log_*.txt`)
   - Configuration syntax check
   - Duplicate variable detection
   - Variable count summary

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**

   ```
   ERROR: Failed to connect to production server
   ```

   - Check SSH key exists: `ls -la ~/.ssh/do_personal_assistant`
   - Test connection: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1`
   - Verify server is accessible: `ping 165.227.38.1`

2. **Production File Not Found**

   ```
   WARNING: Production env file not found
   ```

   - Check file path in production
   - Verify file permissions
   - Confirm file exists: `ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1 "ls -la /home/deploy/ai_assistant/config/"`

3. **Update Script Fails**

   ```
   ERROR: Failed to update production file
   ```

   - Check SSH connection
   - Verify file permissions
   - Review update logs in backup directory

4. **Services Won't Start**
   ```
   ERROR: docker-compose up failed
   ```
   - Check configuration syntax
   - Review service logs
   - Verify all required variables present

### Recovery Procedures

1. **Rollback Configuration**

   ```bash
   # Find backup files
   ls -la backups/*/

   # Restore from backup
   scp -i ~/.ssh/do_personal_assistant backups/YYYYMMDD_HHMMSS/production.env_backup_* deploy@165.227.38.1:/home/deploy/ai_assistant/config/production.env
   ```

2. **Restart Services**

   ```bash
   ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
   cd /home/deploy/ai_assistant
   docker-compose down
   docker-compose up -d
   ```

3. **Check Service Status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## Security Considerations

### Sensitive Variables

The following variables contain sensitive information and require special handling:

- `DATABASE_URL` - Database credentials
- `GOOGLE_API_KEY` - Google API access
- `TWILIO_AUTH_TOKEN` - Twilio authentication
- `MICROSOFT_CLIENT_SECRET` - Microsoft OAuth secret
- `NOTION_API_KEY` - Notion API access
- `JWT_SECRET_KEY` - JWT signing key

### Best Practices

1. **Never log sensitive values**
2. **Use environment-specific values**
3. **Rotate secrets regularly**
4. **Monitor access logs**
5. **Use least privilege principle**

## Automation and Maintenance

### Regular Comparison

Set up a cron job for regular comparison:

```bash
# Add to crontab
0 2 * * * /Users/ianleblanc/Desktop/personal_assistant/docs/architecture/tasks/087_prod_dev_config_comparison/compare_config_files.sh
```

### Monitoring

Monitor the following for configuration drift:

1. **Environment Variables**

   - Count of variables
   - Missing required variables
   - Unexpected variables

2. **Service Health**

   - API endpoint responses
   - Service startup success
   - Error log patterns

3. **Security**
   - Sensitive variable exposure
   - Unauthorized access attempts
   - Configuration changes

## Success Metrics

### Primary Success Criteria

- [ ] All environment files compared successfully
- [ ] Missing variables identified and documented
- [ ] Production configuration updated (if needed)
- [ ] All services running correctly
- [ ] No errors in logs

### Secondary Success Criteria

- [ ] Automation scripts working
- [ ] Documentation updated
- [ ] Team trained on process
- [ ] Monitoring enhanced
- [ ] Future comparisons automated

## Next Steps

After completing this task:

1. **Document Lessons Learned**
2. **Update Deployment Procedures**
3. **Create Regular Audit Schedule**
4. **Enhance Monitoring**
5. **Plan for Configuration Management**

---

## Support

For issues or questions:

1. **Check Troubleshooting Section**
2. **Review Log Files**
3. **Test SSH Connection**
4. **Verify File Permissions**
5. **Contact System Administrator**

## Resources

- **Production Server**: 165.227.38.1
- **SSH Key**: ~/.ssh/do_personal_assistant
- **Project Directory**: /home/deploy/ai_assistant
- **Main Site**: https://ianleblanc.ca
- **API Health**: https://ianleblanc.ca/api/health
