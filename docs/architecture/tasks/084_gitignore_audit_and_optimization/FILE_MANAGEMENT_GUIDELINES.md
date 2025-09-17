# Task 084: File Management Guidelines

## Overview

This document provides comprehensive guidelines for managing files in the personal assistant repository, ensuring security, maintainability, and proper version control practices.

## File Classification System

### 🔴 CRITICAL - Never Commit

**Definition**: Files containing sensitive data that must never be committed
**Examples**:

- JWT tokens and session data
- API keys and secrets
- Database credentials
- SSL certificates
- Production reset scripts

**Action**: Always add to .gitignore immediately

### 🟡 SENSITIVE - Environment Specific

**Definition**: Files that vary by environment and may contain sensitive data
**Examples**:

- Database schemas
- Configuration files with secrets
- Environment-specific scripts
- Backup files

**Action**: Add to .gitignore, use templates instead

### 🟢 SAFE - Can Be Committed

**Definition**: Files that are safe to commit and share
**Examples**:

- Source code
- Documentation
- Configuration templates
- Test files
- Build scripts

**Action**: Commit normally

## .gitignore Best Practices

### 1. Organization

- **Group related patterns** with clear comments
- **Use specific patterns** when possible
- **Order from specific to general**
- **Document non-obvious exclusions**

### 2. Pattern Guidelines

```bash
# Good: Specific and clear
cookies.txt
*.env
node_modules/

# Bad: Too broad or unclear
*
temp/
```

### 3. Testing Patterns

```bash
# Test if pattern works
git check-ignore <file_path>

# Check what's being ignored
git status --ignored
```

## Common File Types and Handling

### Authentication and Session Files

**Pattern**: `cookies.txt`, `*.cookies`, `session_*.txt`
**Reason**: Contains active tokens and session data
**Action**: Always ignore

### Database Files

**Pattern**: `*schema*.txt`, `*schema*.sql`, `reset_*_schema.sql`
**Reason**: May contain sensitive production data
**Action**: Always ignore

### Environment Files

**Pattern**: `*.env`, `config/*.env`
**Reason**: Contains secrets and configuration
**Action**: Always ignore, use `.env.example` instead

### Node.js Files

**Pattern**: `node_modules/`, `package-lock.json`, `yarn.lock`
**Reason**: Large dependency files, should be installed locally
**Action**: Always ignore

### Log Files

**Pattern**: `*.log`, `logs/`
**Reason**: May contain sensitive information
**Action**: Always ignore

### Backup Files

**Pattern**: `*.backup`, `*.bak`, `*backup*.sql`
**Reason**: May contain sensitive data
**Action**: Always ignore

### Temporary Files

**Pattern**: `*.tmp`, `*.temp`, `*.swp`, `*.swo`, `*~`
**Reason**: Editor and system temporary files
**Action**: Always ignore

## Development Workflow

### 1. Before Adding Files

**Checklist**:

- [ ] Is this file sensitive?
- [ ] Does it contain secrets or credentials?
- [ ] Is it environment-specific?
- [ ] Should it be in version control?

### 2. Adding New Files

**Process**:

1. **Classify** the file using the classification system
2. **Check** if it matches existing .gitignore patterns
3. **Add** to .gitignore if sensitive
4. **Test** the pattern works correctly
5. **Commit** only safe files

### 3. Handling Sensitive Files

**If you accidentally add sensitive files**:

1. **Stop** - Don't commit
2. **Add** to .gitignore immediately
3. **Remove** from staging: `git reset HEAD <file>`
4. **Verify** it's ignored: `git status`
5. **Commit** .gitignore changes

## Security Checklist

### Daily Checks

- [ ] No sensitive files in staging area
- [ ] .gitignore covers new file types
- [ ] No secrets in commit messages
- [ ] Environment files properly ignored

### Weekly Checks

- [ ] Review recent commits for sensitive data
- [ ] Check for new file types that need ignoring
- [ ] Verify .gitignore effectiveness
- [ ] Update team on any changes

### Monthly Checks

- [ ] Comprehensive security scan
- [ ] Review .gitignore for optimization
- [ ] Check repository size and bloat
- [ ] Update security procedures

## Team Responsibilities

### Developers

- **Understand** file classification system
- **Follow** development workflow
- **Report** security concerns immediately
- **Participate** in security training

### Security Team

- **Monitor** repository for security issues
- **Maintain** .gitignore and security procedures
- **Conduct** regular security audits
- **Provide** security training and guidance

### DevOps Team

- **Implement** automated security checks
- **Monitor** CI/CD for security issues
- **Maintain** secure deployment practices
- **Support** incident response procedures

## Tools and Automation

### Pre-commit Hooks

**Purpose**: Automatically detect sensitive data before commits
**Implementation**:

```bash
# Install pre-commit
pip install pre-commit

# Add to .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
```

### Security Scanning

**Tools**:

- `git-secrets` - AWS secrets detection
- `truffleHog` - High entropy string detection
- `detect-secrets` - Comprehensive secret detection

### Repository Monitoring

**Metrics**:

- Repository size growth
- New file types added
- Sensitive pattern detection
- Unusual commit patterns

## Incident Response

### If Sensitive Data is Committed

**Immediate Actions**:

1. **Assess** scope of exposure
2. **Rotate** compromised credentials
3. **Remove** from repository history
4. **Notify** security team
5. **Document** incident

### Repository Cleanup

**Steps**:

1. **Identify** sensitive files in history
2. **Use** `git filter-branch` or BFG to remove
3. **Force push** cleaned history
4. **Notify** team of changes
5. **Update** procedures to prevent recurrence

## Best Practices Summary

### Do's

- ✅ **Always** check file sensitivity before committing
- ✅ **Use** specific .gitignore patterns
- ✅ **Test** .gitignore patterns before committing
- ✅ **Document** non-obvious exclusions
- ✅ **Regular** security scans and audits
- ✅ **Train** team on security practices

### Don'ts

- ❌ **Never** commit sensitive files
- ❌ **Don't** use overly broad .gitignore patterns
- ❌ **Don't** ignore security warnings
- ❌ **Don't** commit without reviewing changes
- ❌ **Don't** store secrets in code or config files
- ❌ **Don't** ignore .gitignore effectiveness

## Conclusion

Proper file management is essential for repository security and maintainability. By following these guidelines, the team can ensure that sensitive data remains protected while maintaining efficient development workflows.

**Key Takeaways**:

1. **Security First**: Always consider file sensitivity
2. **Clear Classification**: Use the color-coded system
3. **Regular Monitoring**: Ongoing security vigilance
4. **Team Training**: Shared understanding and responsibility
5. **Automation**: Tools to support manual processes

Remember: **When in doubt, don't commit**. It's always better to be cautious and ask for guidance than to accidentally expose sensitive data.
