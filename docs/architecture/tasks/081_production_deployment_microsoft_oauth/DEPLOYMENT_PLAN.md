# Production Deployment Plan - Microsoft OAuth Final Branch

## 🎯 **Deployment Overview**

**Target**: Deploy `microsoft_oauth_final` branch to production at `ianleblanc.ca`  
**Duration**: 2-3 days  
**Risk Level**: HIGH (Database migration + OAuth configuration)  
**Rollback Strategy**: Full database backup + service rollback

## 📊 **Current State Analysis**

### **Production Environment**

- **Domain**: `ianleblanc.ca`
- **Server**: DigitalOcean Droplet (165.227.38.1)
- **Database**: PostgreSQL (0 tables - empty)
- **Services**: Docker Compose (15+ containers)
- **SSL**: Let's Encrypt certificates
- **Monitoring**: Prometheus, Grafana, Loki

### **Development Environment**

- **Database**: PostgreSQL (43 tables - complete)
- **OAuth**: Google, Microsoft, Notion providers
- **Testing**: 50+ OAuth test cases
- **Security**: Token encryption, user isolation
- **Features**: Complete functionality

### **Gap Analysis**

- ❌ **Database Schema**: 0 vs 43 tables
- ❌ **OAuth Configuration**: No production OAuth setup
- ❌ **User Authentication**: Cannot login/signup
- ❌ **Core Features**: Non-functional due to missing schema

## 🚀 **Deployment Strategy**

### **Approach**: Complete Schema Migration + Code Deployment

- **Database**: Single complete schema migration
- **Code**: Full branch deployment
- **OAuth**: Configure all providers
- **Monitoring**: Enable full observability

### **Benefits**

- ✅ Guaranteed schema consistency
- ✅ Single migration, no dependency issues
- ✅ Fast deployment
- ✅ Complete feature parity

### **Risks**

- ❌ Skips individual migration history
- ❌ No granular rollback per feature
- ❌ Complex OAuth configuration

## 📋 **Detailed Deployment Steps**

### **Phase 1: Pre-Deployment Preparation (Day 0)**

#### **1.1 Environment Validation**

```bash
# Connect to production server
ssh -i ~/.ssh/do_personal_assistant deploy@165.227.38.1
cd /home/deploy/ai_assistant

# Verify current state
docker-compose -f docker/docker-compose.prod.yml ps
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod -c "\dt"
```

#### **1.2 Create Full Backup**

```bash
# Create comprehensive backup
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_dump -U personal_assistant_prod personal_assistant_prod > backup_before_deployment_$(date +%Y%m%d_%H%M%S).sql

# Backup configuration files
cp -r docker/ backup_config_$(date +%Y%m%d_%H%M%S)/
cp -r config/ backup_config_$(date +%Y%m%d_%H%M%S)/
```

#### **1.3 Prepare OAuth Credentials**

```bash
# Ensure OAuth secrets are configured in production environment
# Google OAuth: GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET
# Microsoft OAuth: MICROSOFT_OAUTH_CLIENT_ID, MICROSOFT_OAUTH_CLIENT_SECRET
# Notion OAuth: NOTION_OAUTH_CLIENT_ID, NOTION_OAUTH_CLIENT_SECRET
```

### **Phase 2: Database Reset (Day 1)**

#### **2.1 Reset Database Schema**

```bash
# Drop all existing tables to start fresh
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U prod_user -d personal_assistant_prod -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO prod_user;
GRANT ALL ON SCHEMA public TO public;
"
```

#### **2.2 Apply Complete Schema Migration**

```bash
# Apply the complete schema migration
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
import asyncio
from src.personal_assistant.database.migrations.manager import migration_manager

async def apply_complete_schema():
    # Get pending migrations
    pending = await migration_manager.get_pending_migrations()
    complete_schema = [m for m in pending if m.migration_name == '000_complete_schema_migration']

    if complete_schema:
        print(f'Applying migration: {complete_schema[0].migration_name}')
        result = await migration_manager.apply_migration(complete_schema[0], 'production_deployment')
        print(f'Migration result: {result}')
    else:
        print('Complete schema migration not found')

asyncio.run(apply_complete_schema())
"
```

#### **2.2 Verify Schema Creation**

```bash
# Check tables were created
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod -c "\dt"

# Should show 43 tables
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

#### **2.3 Create Admin User**

```bash
# Create initial admin user
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
import asyncio
from src.personal_assistant.database.models.users import User
from src.personal_assistant.database.session import _get_session_factory

async def create_admin():
    session_factory = _get_session_factory()
    async with session_factory() as db:
        # Check if admin already exists
        existing_admin = await db.execute(
            'SELECT id FROM users WHERE username = :username',
            {'username': 'admin'}
        )
        if existing_admin.fetchone():
            print('Admin user already exists')
            return

        admin = User(
            email='admin@ianleblanc.ca',
            username='admin',
            password_hash='\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.8K2',  # 'admin123'
            is_active=True,
            is_admin=True,
            email_verified=True
        )
        db.add(admin)
        await db.commit()
        print('Admin user created successfully!')

asyncio.run(create_admin())
"
```

### **Phase 3: Code Deployment (Day 1-2)**

#### **3.1 Deploy Latest Code**

```bash
# Pull latest changes from main branch (microsoft_oauth_final merged)
git fetch origin
git checkout main
git pull origin main

# Verify branch and latest commits
git branch
git log --oneline -5
```

#### **3.2 Manual OAuth Environment Update**

```bash
# Update OAuth environment variables manually on droplet
# Edit the production environment file
nano docker/.env.prod

# Update the following OAuth variables:
# GOOGLE_OAUTH_CLIENT_ID=your_new_google_client_id
# GOOGLE_OAUTH_CLIENT_SECRET=your_new_google_client_secret
# MICROSOFT_OAUTH_CLIENT_ID=your_new_microsoft_client_id
# MICROSOFT_OAUTH_CLIENT_SECRET=your_new_microsoft_client_secret
# NOTION_OAUTH_CLIENT_ID=your_new_notion_client_id
# NOTION_OAUTH_CLIENT_SECRET=your_new_notion_client_secret

# Verify the changes
grep -E "OAUTH.*CLIENT" docker/.env.prod
```

#### **3.3 Restart Services**

```bash
# Restart all services to apply new code
docker-compose -f docker/docker-compose.prod.yml down
docker-compose -f docker/docker-compose.prod.yml up -d

# Wait for services to start
sleep 30

# Check service health
docker-compose -f docker/docker-compose.prod.yml ps
```

#### **3.4 Test Core Functionality**

```bash
# Test API health endpoint
curl -X GET https://ianleblanc.ca/api/health

# Test login endpoint
curl -X POST https://ianleblanc.ca/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test frontend
curl -X GET https://ianleblanc.ca/
```

### **Phase 4: OAuth Configuration (Day 2)**

#### **4.1 Configure Google OAuth**

```bash
# Verify Google OAuth configuration
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
from src.personal_assistant.config.settings import settings
print(f'Google OAuth Client ID: {settings.GOOGLE_OAUTH_CLIENT_ID}')
print(f'Google OAuth Redirect URI: {settings.GOOGLE_OAUTH_REDIRECT_URI}')
"
```

#### **4.2 Configure Microsoft OAuth**

```bash
# Verify Microsoft OAuth configuration
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
from src.personal_assistant.config.settings import settings
print(f'Microsoft OAuth Client ID: {settings.MICROSOFT_OAUTH_CLIENT_ID}')
print(f'Microsoft OAuth Redirect URI: {settings.MICROSOFT_OAUTH_REDIRECT_URI}')
"
```

#### **4.3 Test OAuth Endpoints**

```bash
# Test OAuth provider endpoints
curl -X GET https://ianleblanc.ca/api/oauth/providers

# Test Google OAuth initiation
curl -X POST https://ianleblanc.ca/api/oauth/google/authorize \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Test Microsoft OAuth initiation
curl -X POST https://ianleblanc.ca/api/oauth/microsoft/authorize \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

#### **4.4 End-to-End OAuth Testing**

```bash
# Test complete OAuth flow
# 1. Initiate OAuth authorization
# 2. Complete OAuth callback
# 3. Verify token storage
# 4. Test token usage in agent tools

# Run OAuth test suite
docker-compose -f docker/docker-compose.prod.yml exec api python -m pytest tests/oauth/ -v
```

### **Phase 5: Monitoring & Validation (Day 3)**

#### **5.1 Enable Monitoring**

```bash
# Verify monitoring services are running
docker-compose -f docker/docker-compose.prod.yml ps | grep -E "(prometheus|grafana|loki)"

# Check monitoring endpoints
curl -X GET https://ianleblanc.ca/monitoring/prometheus/targets
curl -X GET https://ianleblanc.ca/monitoring/grafana/
```

#### **5.2 Performance Testing**

```bash
# Test API performance
curl -w "@curl-format.txt" -X GET https://ianleblanc.ca/api/health

# Test OAuth performance
time curl -X POST https://ianleblanc.ca/api/oauth/google/authorize \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

#### **5.3 Security Validation**

```bash
# Test token encryption
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
from src.personal_assistant.oauth.services.token_service import TokenService
service = TokenService()
test_token = 'test_token_123'
encrypted = service.encrypt_token(test_token)
decrypted = service.decrypt_token(encrypted)
print(f'Token encryption test: {test_token == decrypted}')
"

# Test user isolation
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
# Test that users cannot access other users' OAuth data
# This should be validated through the OAuth test suite
"
```

#### **5.4 Comprehensive Testing**

```bash
# Run full test suite
docker-compose -f docker/docker-compose.prod.yml exec api python -m pytest tests/oauth/ -v
docker-compose -f docker/docker-compose.prod.yml exec api python -m pytest tests/security_oauth/ -v
docker-compose -f docker/docker-compose.prod.yml exec api python -m pytest tests/e2e_oauth/ -v

# Test frontend functionality
curl -X GET https://ianleblanc.ca/
curl -X GET https://ianleblanc.ca/api/health
```

## 🔄 **Rollback Procedures**

### **Emergency Rollback**

```bash
# 1. Stop current services
docker-compose -f docker/docker-compose.prod.yml down

# 2. Restore database from backup
docker-compose -f docker/docker-compose.prod.yml up -d postgres
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod < backup_before_deployment_YYYYMMDD_HHMMSS.sql

# 3. Restore previous code
git checkout main  # or previous working branch
git pull origin main

# 4. Restart services
docker-compose -f docker/docker-compose.prod.yml up -d

# 5. Verify rollback
curl -X GET https://ianleblanc.ca/api/health
```

### **Partial Rollback**

```bash
# Rollback specific components if needed
# Database only
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod < backup_before_deployment_YYYYMMDD_HHMMSS.sql

# Code only
git checkout main
git pull origin main
docker-compose -f docker/docker-compose.prod.yml restart api frontend
```

## 📊 **Success Metrics**

### **Functional Metrics**

- ✅ **Database**: 43 tables created successfully
- ✅ **Authentication**: Admin login working
- ✅ **OAuth**: Google and Microsoft OAuth functional
- ✅ **API**: All endpoints responding < 200ms
- ✅ **Frontend**: UI loading and functional

### **Security Metrics**

- ✅ **Token Encryption**: All tokens encrypted at rest
- ✅ **User Isolation**: Cross-user access prevented
- ✅ **HTTPS**: All communications encrypted
- ✅ **CSRF Protection**: State validation working

### **Performance Metrics**

- ✅ **Response Times**: API < 200ms, OAuth < 2s
- ✅ **Concurrent Users**: Support 50+ users
- ✅ **Database**: Query performance within limits
- ✅ **Monitoring**: All metrics flowing

## ⚠️ **Risk Mitigation**

### **Database Migration Risks**

- **Mitigation**: Full backup before migration
- **Monitoring**: Watch migration logs closely
- **Rollback**: Immediate database restore capability

### **OAuth Configuration Risks**

- **Mitigation**: Test OAuth flows in staging first
- **Monitoring**: Monitor OAuth endpoint health
- **Rollback**: Disable OAuth providers if needed

### **Service Dependency Risks**

- **Mitigation**: Staged deployment with health checks
- **Monitoring**: Service health monitoring
- **Rollback**: Service-by-service rollback capability

## 📋 **Post-Deployment Checklist**

### **Immediate (Day 3)**

- [ ] All services running and healthy
- [ ] Database schema complete (43 tables)
- [ ] Admin user can login
- [ ] OAuth providers configured
- [ ] API endpoints responding
- [ ] Frontend loading correctly

### **Short-term (Week 1)**

- [ ] Monitor system performance
- [ ] Watch for error logs
- [ ] Test OAuth flows with real users
- [ ] Validate security measures
- [ ] Update documentation

### **Long-term (Month 1)**

- [ ] Performance optimization
- [ ] Security audit
- [ ] User feedback collection
- [ ] Feature enhancements
- [ ] Monitoring improvements

## 🎯 **Expected Outcome**

After successful deployment:

- ✅ **Production Environment**: Fully functional at `ianleblanc.ca`
- ✅ **OAuth Integration**: Google and Microsoft OAuth working
- ✅ **User Authentication**: Complete login/signup functionality
- ✅ **Database**: 43 tables with proper schema
- ✅ **Security**: Token encryption and user isolation active
- ✅ **Monitoring**: Full observability and alerting
- ✅ **Performance**: Optimized for production load

The Personal Assistant application will be **production-ready** with comprehensive OAuth integration, enabling users to connect their Google and Microsoft accounts for enhanced functionality.

**Status**: 🚀 **READY FOR EXECUTION**
