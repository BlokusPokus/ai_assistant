# Task 093: Comprehensive Manual Configuration Comparison - Report

## Executive Summary

This report documents the comprehensive manual comparison of configuration files between development and production environments for the Personal Assistant application. The analysis reveals significant discrepancies due to manual configuration management, with production having additional variables that were manually added from development environment.

**Key Findings:**

- Production has been manually updated with development variables (timestamps show additions on Sep 18, 2025)
- Multiple environment files exist in production with overlapping configurations
- Several critical discrepancies identified in OAuth configurations and service settings
- Security concerns with exposed credentials and inconsistent configurations

## Configuration Files Analyzed

### Development Environment Files

- `config/development.env` (113 lines)
- `config/production.env` (103 lines)
- `config/env.example` (89 lines)
- `config/test.env`
- `docker/env.prod.example`
- `docker/env.stage.example`

### Production Environment Files (via SSH)

- `/home/deploy/ai_assistant/config/production.env` (4001 bytes)
- `/home/deploy/ai_assistant/.env.prod` (2877 bytes)
- `/home/deploy/ai_assistant/docker/.env` (2264 bytes)
- Multiple backup files with timestamps

## Critical Differences Identified

### 1. Environment Variables Discrepancies

#### Missing Variables in Development

**Production has these variables that development lacks:**

- `GEMINI_API_KEY` - Present in production, missing in development ✅
- `TWILIO_PHONE_NUMBER` - Production: `+18737002185`, Development: Not present✅
- `MICROSOFT_TENANT_ID` - Production: `common`, Development: Not present
- `ENCRYPTION_KEY` - Production: `b5943407b4c52efb3b2d186d13bd0e8a`, Development: Not present
- `DOMAIN_NAME` - Production: `ianleblanc.ca`, Development: Not present
- `FRONTEND_URL` - Production: `https://ianleblanc.ca`, Development: Not present
- `BACKEND_URL` - Production: `https://ianleblanc.ca/api`, Development: Not present

#### Missing Variables in Production

**Development has these variables that production lacks:**

- `GEMINI_MODEL` - Development: Commented out, Production: Not present
- Several logging configuration variables that were manually added to production

#### Inconsistent Values

**Variables with different values between environments:**

1. **Database Configuration**

User: this is normal, we use local db in dev

- Development: `postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres`
- Production: `postgresql+asyncpg://prod_user:prod_password@postgres:5432/personal_assistant_prod`

2. **Twilio Configuration**

User: this is fine, just delete the extra one in prod

- Development: `TWILIO_FROM_NUMBER=+18198039358`
- Production: `TWILIO_FROM_NUMBER=+18737002185` (also has `TWILIO_PHONE_NUMBER=+18737002185`)

3. **OAuth Redirect URIs**
   User: this is fine

   - Development: `http://localhost:8000/api/v1/oauth/callback`
   - Production: `https://ianleblanc.ca/api/v1/oauth/callback`

4. **Microsoft OAuth Client Secret**
   User: this is fine

   - Development: `***REDACTED***`
   - Production: `***REDACTED***`

5. **Debug Settings**
   - Development: `DEBUG=true`, `LOG_LEVEL=DEBUG`
   - Production: `DEBUG=true` (inconsistently set), `LOG_LEVEL=INFO`

### 2. Multiple Environment Files in Production

**Production has multiple overlapping environment files:**

- `/home/deploy/ai_assistant/config/production.env` - Main production config
- `/home/deploy/ai_assistant/.env.prod` - Docker production config
- `/home/deploy/ai_assistant/docker/.env` - Docker environment config

**Issues identified:**

- Duplicate variables across files with different values
- Inconsistent OAuth configurations
- Mixed development and production settings

### 3. Security Concerns

#### Exposed Credentials

- API keys and secrets are visible in configuration files
- Database passwords are hardcoded
- JWT secrets are exposed
- OAuth client secrets are visible

#### Inconsistent Security Settings

- Production has `DEBUG=true` in some configurations
- Mixed log levels between development and production
- Inconsistent encryption key management

### 4. Service Configuration Differences

#### Redis Configuration

- Development: `redis://:redis_password@localhost:6379/0`
- Production: `redis://:redis_password@redis:6379/0` (uses container name)

#### Vector Database Configuration

- Development: `VECTOR_DB_URL=http://localhost:6333`
- Production: Uses Qdrant cloud service with API key

#### Monitoring Configuration

- **Both environments have identical monitoring configurations** ✅
- **Shared config files**: `docker/monitoring/prometheus.yml`, `docker/monitoring/loki-config.yaml`
- **Services**: Prometheus, Grafana, Loki configured in both `docker-compose.dev.yml` and `docker-compose.prod.yml`
- **Only differences**: Container names (`_dev` vs `_prod`) and data volume names

## Detailed Analysis by Category

### Database Configuration

| Variable     | Development                                                        | Production                                                                           | Status                  |
| ------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ----------------------- |
| DATABASE_URL | `postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres` | `postgresql+asyncpg://prod_user:prod_password@postgres:5432/personal_assistant_prod` | ✅ Different (expected) |
| REAL_DB_URL  | Same as DATABASE_URL                                               | Same as DATABASE_URL                                                                 | ✅ Consistent           |

### OAuth Configuration

| Service                 | Development                                                                | Production                                                                 | Status                  |
| ----------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ----------------------- |
| Microsoft Client ID     | `8a0cac21-315f-4b82-bb09-1980d664bdbe`                                     | `8a0cac21-315f-4b82-bb09-1980d664bdbe`                                     | ✅ Consistent           |
| Microsoft Client Secret | `***REDACTED***`                                 | `***REDACTED***`                                 | ❌ Different            |
| Microsoft Redirect URI  | `http://localhost:8000/api/v1/oauth/callback`                              | `https://ianleblanc.ca/api/v1/oauth/callback`                              | ✅ Different (expected) |
| Google Client ID        | `270689464547-4vu8spg0hpdov27hem11ec2e9plpcpjj.apps.googleusercontent.com` | `270689464547-4vu8spg0hpdov27hem11ec2e9plpcpjj.apps.googleusercontent.com` | ✅ Consistent           |
| Google Redirect URI     | `http://localhost:8000/api/v1/oauth/callback`                              | `https://ianleblanc.ca/api/oauth/google/callback`                          | ❌ Different path       |

### External Services

| Service             | Development                               | Production                                | Status            |
| ------------------- | ----------------------------------------- | ----------------------------------------- | ----------------- |
| Twilio From Number  | `+18198039358`                            | `+18737002185`                            | ❌ Different      |
| Twilio Phone Number | Not present                               | `+18737002185`                            | ❌ Missing in dev |
| YouTube API Key     | `AIzaSyBQoBmWZKGdbeG8pevllj6_VKljpT0XtsU` | `AIzaSyBQoBmWZKGdbeG8pevllj6_VKljpT0XtsU` | ✅ Consistent     |
| Qdrant API Key      | Present                                   | Present                                   | ✅ Consistent     |
| Qdrant URL          | Present                                   | Present                                   | ✅ Consistent     |

### Application Settings

| Variable    | Development   | Production              | Status                     |
| ----------- | ------------- | ----------------------- | -------------------------- |
| DEBUG       | `true`        | `true` (inconsistently) | ❌ Should be false in prod |
| LOG_LEVEL   | `DEBUG`       | `INFO`                  | ✅ Different (expected)    |
| ENVIRONMENT | `development` | `production`            | ✅ Different (expected)    |

## Configuration Questions Answered

### 1. **MICROSOFT_TENANT_ID**

- **Purpose**: Required for Microsoft OAuth authentication to specify Azure AD tenant
- **Value**: `common` accepts users from any Azure AD tenant
- **Need in Dev**: **YES** - Required for Microsoft Calendar integration (see calendar_error_handler.py)
- **Action**: ✅ **ADDED** `MICROSOFT_TENANT_ID=common` to development environment

### 2. **DOMAIN_NAME, FRONTEND_URL, BACKEND_URL in Development**

- **Purpose**: Used for OAuth redirect URIs and CORS configuration
- **Need in Dev**: **NO** - Development uses localhost, these are production-specific
- **Recommendation**: Keep these only in production, not needed in development

### 3. **Multiple Environment Files in Production**

**Production Files Analysis:**

- `/home/deploy/ai_assistant/config/production.env` - **Main application config** (4001 bytes) ✅ **PRIMARY**
- `/home/deploy/ai_assistant/.env.prod` - **Docker production config** (2877 bytes)
- `/home/deploy/ai_assistant/docker/.env` - **Docker environment config** (2264 bytes)

**Recommendation**: Use `/home/deploy/ai_assistant/config/production.env` as the **single source of truth** for application configuration.

## File Usage Analysis

### **How Configuration Files Are Used**

**Application Code (Python):**

- **Uses**: `config/production.env`
- **How**: Loads `config/{ENVIRONMENT}.env` via `settings.py` (line 31)
- **Since**: `ENVIRONMENT=production`, it loads `config/production.env`
- **Volume Mount**: `/home/deploy/ai_assistant/config` → `/app/config` (read-only)

**Docker Containers:**

- **Uses**: `docker/.env.prod` (via `env_file` directive in docker-compose.prod.yml)
- **How**: Docker Compose loads `docker/.env.prod` as environment variables
- **Override**: Docker environment variables **override** the config file values
- **Priority**: Docker env vars > config file values

### **Conflict Resolution Priority**

1. **Docker environment variables** (from `docker/.env.prod`) - **HIGHEST PRIORITY**
2. **Config file** (`config/production.env`) - **FALLBACK**

### **Conflicts Found & Fixed**

- `TWILIO_FROM_NUMBER`: Fixed from `+18198039358` → `+18737002185` ✅
- `JWT_SECRET_KEY`: Fixed from placeholder → real key ✅

## Changes Implemented

### ✅ **Production Changes Applied**

1. **Added**: `GEMINI_MODEL=gemini-2.5-flash` to production environment
2. **Removed**: Duplicate `TWILIO_PHONE_NUMBER` from production environment
3. **Fixed Conflicts**: Updated `config/production.env` to match working Docker values:
   - `TWILIO_FROM_NUMBER`: `+18198039358` → `+18737002185`
   - `JWT_SECRET_KEY`: placeholder → real key
4. **Backup**: Created backup of production config before changes

### ✅ **Development Changes Applied**

1. **Added**: `MICROSOFT_TENANT_ID=common` to development environment
2. **Confirmed**: `GEMINI_API_KEY` and `GEMINI_MODEL` already present

## Recommendations

### Critical Issues (Immediate Action Required)

1. **Fix Microsoft OAuth Client Secret Mismatch**

   - Development and production have different Microsoft OAuth client secrets
   - This will cause authentication failures
   - **Action**: Verify which secret is correct and update accordingly

2. **Fix Google OAuth Redirect URI Path Mismatch**

   - Development: `/api/v1/oauth/callback`
   - Production: `/api/oauth/google/callback`
   - **Action**: Standardize the OAuth callback paths

3. **Fix Twilio Phone Number Inconsistency**

   - Development and production use different Twilio phone numbers
   - **Action**: Verify which number should be used and standardize

4. **Remove DEBUG=true from Production**
   - Production has `DEBUG=true` which is a security risk
   - **Action**: Set `DEBUG=false` in all production configurations

### Important Issues (Action Required Soon)

1. **Consolidate Production Environment Files**

   - Multiple overlapping environment files in production
   - **Action**: Consolidate into single source of truth

2. **Add Missing Variables to Development**

   - Several production variables are missing from development
   - **Action**: Add missing variables to development environment

3. **Standardize OAuth Configurations**
   - Inconsistent OAuth configurations across files
   - **Action**: Create single OAuth configuration template

### Security Improvements

1. **Implement Environment Variable Encryption**

   - Sensitive data is currently stored in plain text
   - **Action**: Implement encryption for sensitive variables

2. **Remove Hardcoded Credentials**

   - API keys and secrets are hardcoded
   - **Action**: Move to secure credential management system

3. **Implement Configuration Validation**
   - No validation of configuration consistency
   - **Action**: Add configuration validation scripts

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)

1. Fix Microsoft OAuth client secret mismatch
2. Fix Google OAuth redirect URI path mismatch
3. Fix Twilio phone number inconsistency
4. Remove DEBUG=true from production

### Phase 2: Configuration Consolidation (Within 1 week)

1. Consolidate production environment files
2. Add missing variables to development
3. Standardize OAuth configurations
4. Implement configuration validation

### Phase 3: Security Improvements (Within 2 weeks)

1. Implement environment variable encryption
2. Move to secure credential management
3. Add configuration monitoring
4. Implement automated configuration validation

## Validation Steps

### After Each Change

1. Test OAuth authentication flows
2. Verify SMS functionality with Twilio
3. Check application startup and logging
4. Validate all API endpoints
5. Test database connectivity

### Final Validation

1. Complete end-to-end testing
2. Verify all services are functional
3. Check monitoring and logging
4. Validate security configurations
5. Document final configuration state

## Conclusion

The manual configuration comparison revealed significant discrepancies between development and production environments. The production environment has been manually updated with development variables, leading to inconsistencies and potential security issues.

**Priority Actions:**

1. Fix OAuth configuration mismatches
2. Remove DEBUG mode from production
3. Consolidate production environment files
4. Implement proper configuration management

**Success Metrics:**

- All OAuth flows working correctly
- No DEBUG mode in production
- Single source of truth for environment variables
- Automated configuration validation in place

This analysis provides the foundation for implementing a robust configuration management system that ensures consistency and security across all environments.
