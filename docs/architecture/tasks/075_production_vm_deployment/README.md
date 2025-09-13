# Task 075: Production VM Deployment

## 🎯 Task Overview

**Task ID**: 075  
**Status**: 🚀 Ready to Start  
**Effort**: 5-7 days  
**Priority**: CRITICAL - Required for OAuth integration with Google and Microsoft

## 🎯 Objective

Deploy the Personal Assistant TDAH application on a production VM with a real domain name to enable OAuth integration with Google and Microsoft services. This deployment will serve as the foundation for user registration and authentication with external services.

## 📋 Background

The application is currently fully developed and tested locally, but requires a production environment with a real domain name to:

1. **Enable OAuth Integration**: Google and Microsoft OAuth require valid redirect URIs with real domains
2. **SSL/TLS Certificates**: OAuth providers require HTTPS endpoints
3. **Production Testing**: Validate the full stack in a production environment
4. **User Access**: Provide a live application for users to interact with

## 🏗️ Current System Status

Based on the technical roadmap and infrastructure analysis:

### ✅ **Completed Infrastructure**

- **Docker Containerization**: Multi-environment containers (dev/staging/prod) ✅
- **Nginx Reverse Proxy**: TLS 1.3, HTTP/2, security headers ✅
- **Database**: PostgreSQL 15 with connection pooling ✅
- **Caching**: Redis with session management ✅
- **Monitoring Stack**: Prometheus, Grafana, Loki, Jaeger ✅
- **Background Workers**: Celery with multiple specialized queues ✅
- **Frontend**: React 18 + TypeScript + Vite build system ✅
- **API**: FastAPI with 15 endpoints, authentication, RBAC ✅
- **SMS System**: Multi-user SMS routing with Twilio ✅

### 🚀 **Ready for Deployment**

- Production-hardened containers with non-root users
- Health checks and restart policies
- Resource limits and monitoring
- Security scanning and compliance
- 99%+ test coverage
- CI/CD pipeline automation

## 🎯 Scope

### **In Scope**

1. **VM Setup and Configuration**
2. **Domain and DNS Configuration**
3. **SSL Certificate Setup (Let's Encrypt)**
4. **Docker Production Deployment**
5. **Environment Configuration**
6. **OAuth Provider Registration**
7. **Database Migration and Setup**
8. **Monitoring and Logging Configuration**
9. **Backup and Recovery Setup**
10. **Security Hardening**

### **Out of Scope**

- Application code changes (already complete)
- New feature development
- Load balancing (single VM deployment)
- CDN setup (future enhancement)

## 📋 Requirements

### **Functional Requirements**

- [ ] Application accessible via HTTPS on custom domain
- [ ] OAuth integration working with Google and Microsoft
- [ ] User registration and authentication functional
- [ ] SMS routing system operational
- [ ] Database persistence and backups
- [ ] Monitoring dashboards accessible

### **Non-Functional Requirements**

- [ ] 99.5%+ uptime
- [ ] < 2 second page load times
- [ ] SSL/TLS security grade A
- [ ] Automated backups every 6 hours
- [ ] Log retention for 30 days
- [ ] Resource monitoring and alerting

## 🛠️ Technical Implementation

### **Phase 1: Infrastructure Setup (Day 1-2)**

#### **1.1 VM Provisioning and Initial Setup**

```bash
# VM Requirements:
# - 4 vCPUs, 8GB RAM, 100GB SSD
# - Ubuntu 22.04 LTS
# - Public IP address
# - Firewall: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

#### **1.2 Domain and DNS Configuration**

```bash
# DNS Records Required:
# A record: yourdomain.com -> VM_PUBLIC_IP
# CNAME: www.yourdomain.com -> yourdomain.com
# MX record: (optional for email)
```

#### **1.3 Initial Server Hardening**

```bash
# Security basics
sudo apt update && sudo apt upgrade -y
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### **Phase 2: SSL and Domain Setup (Day 2)**

#### **2.1 Let's Encrypt SSL Certificate**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Generate SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### **2.2 Nginx SSL Configuration**

- Update nginx SSL configuration with real certificates
- Configure automatic certificate renewal
- Test SSL grade with SSLLabs

### **Phase 3: Application Deployment (Day 3-4)**

#### **3.1 Code Deployment**

```bash
# Clone repository
git clone https://github.com/yourusername/personal_assistant.git
cd personal_assistant

# Checkout production branch
git checkout main  # or production branch
```

#### **3.2 Environment Configuration**

```bash
# Create production environment file
cp docker/env.prod.example docker/.env.prod

# Configure all required variables:
# - Database credentials
# - Redis password
# - JWT secret keys
# - API keys (Google, Twilio, etc.)
# - OAuth client IDs and secrets
```

#### **3.3 Frontend Build and Deployment**

```bash
# Build frontend for production
cd src/apps/frontend
npm install
npm run build

# Copy built assets to nginx static directory
sudo cp -r dist/* /var/www/html/
```

#### **3.4 Database Setup**

```bash
# Start PostgreSQL container
docker-compose -f docker/docker-compose.prod.yml up -d postgres

# Run database migrations
docker-compose -f docker/docker-compose.prod.yml exec api python -m alembic upgrade head

# Create admin user
docker-compose -f docker/docker-compose.prod.yml exec api python scripts/create_admin_user.py
```

### **Phase 4: OAuth Configuration (Day 4-5)**

#### **4.1 Google OAuth Setup**

1. **Google Cloud Console**:

   - Create new project or use existing
   - Enable Google Calendar API, Gmail API, Drive API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     - `https://yourdomain.com/api/oauth/google/callback`
     - `https://yourdomain.com/oauth/google/callback`

2. **Environment Variables**:
   ```bash
   GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
   GOOGLE_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/google/callback
   ```

#### **4.2 Microsoft OAuth Setup**

1. **Azure App Registration**:

   - Register new application in Azure AD
   - Add Microsoft Graph API permissions
   - Add authorized redirect URIs:
     - `https://yourdomain.com/api/oauth/microsoft/callback`
     - `https://yourdomain.com/oauth/microsoft/callback`

2. **Environment Variables**:
   ```bash
   MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_client_id
   MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_client_secret
   MICROSOFT_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/microsoft/callback
   ```

### **Phase 5: Full Stack Deployment (Day 5-6)**

#### **5.1 Complete Application Stack**

```bash
# Deploy all services
docker-compose -f docker/docker-compose.prod.yml up -d

# Verify all services are healthy
docker-compose -f docker/docker-compose.prod.yml ps
docker-compose -f docker/docker-compose.prod.yml logs
```

#### **5.2 Nginx Configuration Update**

```bash
# Update nginx to serve frontend and proxy API
# Configuration already exists in docker/nginx/conf.d/
```

### **Phase 6: Monitoring and Backup Setup (Day 6-7)**

#### **6.1 Monitoring Configuration**

```bash
# Access monitoring services:
# Grafana: https://yourdomain.com:3000
# Prometheus: https://yourdomain.com:9090
# Jaeger: https://yourdomain.com:16686
```

#### **6.2 Backup Configuration**

```bash
# Setup automated database backups
# Script already exists in scripts/backup_database.sh
crontab -e
# Add: 0 */6 * * * /path/to/backup_database.sh
```

## 🔧 Configuration Files

### **Production Environment Variables**

```bash
# Database
PROD_DB_USER=prod_user
PROD_DB_PASSWORD=secure_production_password
DATABASE_URL=postgresql+asyncpg://prod_user:secure_password@postgres:5432/personal_assistant_prod

# Redis
PROD_REDIS_PASSWORD=secure_redis_password
REDIS_URL=redis://:secure_redis_password@redis:6379/0

# Application
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=your_very_long_and_secure_jwt_secret_key

# API Keys
GOOGLE_API_KEY=your_google_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/google/callback

MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_oauth_client_id
MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_oauth_client_secret
MICROSOFT_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/microsoft/callback

# Monitoring
PROD_GRAFANA_PASSWORD=secure_grafana_password
```

## 🧪 Testing Strategy

### **Deployment Testing**

1. **Infrastructure Tests**:

   - [ ] VM accessibility and SSH access
   - [ ] Domain DNS resolution
   - [ ] SSL certificate validity
   - [ ] Firewall configuration

2. **Application Tests**:

   - [ ] Docker containers health checks
   - [ ] Database connectivity
   - [ ] Redis connectivity
   - [ ] API endpoint accessibility
   - [ ] Frontend loading and functionality

3. **OAuth Integration Tests**:

   - [ ] Google OAuth flow complete
   - [ ] Microsoft OAuth flow complete
   - [ ] Redirect URIs working
   - [ ] Token storage and refresh

4. **End-to-End Tests**:
   - [ ] User registration flow
   - [ ] Authentication with MFA
   - [ ] SMS routing functionality
   - [ ] Dashboard accessibility
   - [ ] OAuth provider connections

## 📊 Success Criteria

### **Technical Metrics**

- [ ] Application accessible at https://yourdomain.com
- [ ] SSL/TLS grade A (SSLLabs test)
- [ ] All Docker containers healthy
- [ ] Database migrations completed
- [ ] OAuth flows functional for Google and Microsoft
- [ ] Monitoring dashboards accessible
- [ ] Backup system operational

### **Performance Metrics**

- [ ] Page load time < 2 seconds
- [ ] API response time < 200ms (P95)
- [ ] Database query time < 100ms (P95)
- [ ] 99.5%+ uptime (24 hours post-deployment)

### **Security Metrics**

- [ ] SSL certificate valid and auto-renewing
- [ ] All security headers present
- [ ] No critical vulnerabilities (security scan)
- [ ] Proper firewall configuration
- [ ] Non-root container execution

## 🚨 Risk Assessment

### **High Risk**

- **Domain/DNS Issues**: Ensure domain is properly configured before OAuth setup
- **SSL Certificate Problems**: Test Let's Encrypt automation thoroughly
- **OAuth Configuration**: Redirect URIs must match exactly

### **Medium Risk**

- **Database Migration**: Test migrations on staging environment first
- **Resource Constraints**: Monitor VM resources during deployment
- **Service Dependencies**: Ensure proper startup order

### **Mitigation Strategies**

- **Staging Environment**: Test full deployment on staging first
- **Rollback Plan**: Keep previous version available for quick rollback
- **Monitoring**: Implement comprehensive health checks
- **Documentation**: Document all configuration changes

## 📋 Dependencies

### **External Dependencies**

- [ ] VM provider account (AWS, GCP, DigitalOcean, etc.)
- [ ] Domain name registration
- [ ] Google Cloud Console access
- [ ] Microsoft Azure account
- [ ] Twilio account (for SMS)

### **Internal Dependencies**

- [x] Docker containerization complete
- [x] Production environment configurations
- [x] Database migration scripts
- [x] Frontend build system
- [x] OAuth provider implementations
- [x] Monitoring stack configuration

## 🎯 Next Steps After Deployment

1. **OAuth Provider Testing**: Verify Google and Microsoft integrations
2. **User Acceptance Testing**: Test full user workflows
3. **Performance Optimization**: Monitor and optimize based on real usage
4. **Security Audit**: Conduct security assessment
5. **Documentation**: Update deployment and operations documentation

## 📝 Notes

- This deployment will enable the OAuth functionality required for Google and Microsoft integrations
- The infrastructure is production-ready with comprehensive monitoring and security
- All application components are already developed and tested
- Focus is on deployment and configuration, not development

## 🔗 Related Tasks

- **Task 041**: OAuth Connection UI Implementation ✅ Complete
- **Task 043**: OAuth Manager Service ✅ Complete
- **Task 044**: OAuth Settings Management ✅ Complete
- **Task 069**: User-Specific Email/Outlook Integration (depends on this deployment)

---

**Prepared by**: AI Architecture Team  
**Review Required**: Infrastructure Team, Security Team  
**Estimated Completion**: 1 week
