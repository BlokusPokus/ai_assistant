# Production Deployment Checklist

## 🎯 Pre-Deployment Preparation

### **Infrastructure Requirements**

- [ ] **VM Provisioned**: 4 vCPUs, 8GB RAM, 100GB SSD, Ubuntu 22.04 LTS
- [ ] **Domain Registered**: Domain name purchased and configured
- [ ] **DNS Configured**: A records pointing to VM public IP
- [ ] **Firewall Configured**: Ports 22, 80, 443 open
- [ ] **SSH Access**: Key-based authentication set up

### **Account Setup**

- [ ] **Google Cloud Console**: Account access with billing enabled
- [ ] **Microsoft Azure**: Account access with subscription
- [ ] **Twilio Account**: SMS service account configured
- [ ] **VM Provider**: DigitalOcean/AWS/GCP account with payment method

## 🚀 Phase 1: Server Setup (Day 1)

### **1.1 Initial Server Configuration**

- [ ] **Connect to VM**: `ssh root@YOUR_VM_IP` successful
- [ ] **System Update**: `apt update && apt upgrade -y` completed
- [ ] **Essential Packages**: curl, wget, git, ufw, fail2ban installed
- [ ] **Firewall Setup**: UFW configured and enabled
- [ ] **Non-root User**: Deploy user created with sudo access
- [ ] **SSH Hardening**: Root login disabled, key-only authentication

### **1.2 Docker Installation**

- [ ] **Docker Installed**: Docker CE latest version installed
- [ ] **Docker Compose**: Docker Compose v2 installed
- [ ] **User Permissions**: Deploy user added to docker group
- [ ] **Docker Service**: Docker service enabled and running
- [ ] **Test Installation**: `docker --version` and `docker-compose --version` work

### **1.3 Application Code Deployment**

- [ ] **Repository Cloned**: Application code cloned to `/home/deploy/personal_assistant`
- [ ] **Permissions Set**: Proper ownership for deploy user
- [ ] **Directory Structure**: All required directories present
- [ ] **Git Branch**: Correct branch checked out (main/production)

## 🔒 Phase 2: SSL and Domain (Day 2)

### **2.1 Domain Verification**

- [ ] **DNS Propagation**: `nslookup yourdomain.com` resolves to VM IP
- [ ] **WWW Subdomain**: `nslookup www.yourdomain.com` resolves correctly
- [ ] **HTTP Access**: `curl -I http://yourdomain.com` returns response
- [ ] **Domain Ownership**: Domain control verified

### **2.2 SSL Certificate Setup**

- [ ] **Certbot Installed**: Let's Encrypt certbot installed
- [ ] **Certificate Generated**: SSL certificate for domain and www subdomain
- [ ] **Certificate Files**: Cert and key files accessible in correct locations
- [ ] **Auto-renewal**: Cron job for automatic certificate renewal configured
- [ ] **SSL Test**: `openssl s_client -connect yourdomain.com:443` successful

### **2.3 Nginx SSL Configuration**

- [ ] **SSL Files Copied**: Certificates copied to nginx SSL directory
- [ ] **Permissions Set**: Correct permissions on certificate files
- [ ] **Configuration Updated**: Nginx SSL configuration points to certificates
- [ ] **SSL Grade**: SSLLabs test shows grade A or higher

## 🔧 Phase 3: Environment Configuration (Day 3)

### **3.1 Production Environment Variables**

- [ ] **Environment File**: `docker/.env.prod` created from template
- [ ] **Database Credentials**: Strong passwords generated and set
- [ ] **Redis Password**: Secure Redis password configured
- [ ] **JWT Secret**: Cryptographically secure JWT secret generated
- [ ] **API Keys**: All required API keys configured (Google, Twilio, etc.)
- [ ] **OAuth Credentials**: Client IDs and secrets configured
- [ ] **Domain Variables**: Production domain URLs set correctly

### **3.2 Security Configuration**

- [ ] **Encryption Keys**: 32-character encryption key generated
- [ ] **Session Security**: Secure session configuration
- [ ] **CORS Settings**: Production CORS settings configured
- [ ] **Debug Mode**: DEBUG=false in production environment
- [ ] **Log Levels**: Appropriate log levels for production

## 🎨 Phase 4: Frontend Build (Day 3)

### **4.1 Node.js Setup**

- [ ] **Node.js Installed**: Node.js 20.x installed
- [ ] **NPM Updated**: Latest npm version
- [ ] **Version Verification**: Node and npm versions confirmed

### **4.2 Frontend Build Process**

- [ ] **Dependencies Installed**: `npm ci` completed successfully
- [ ] **Build Successful**: `npm run build` completed without errors
- [ ] **Static Files**: Built files present in `dist/` directory
- [ ] **Files Copied**: Static files copied to nginx directory
- [ ] **Index.html Present**: Main index.html file accessible

### **4.3 Nginx Static Configuration**

- [ ] **Static Location**: Nginx configured to serve static files
- [ ] **Fallback Route**: SPA fallback to index.html configured
- [ ] **Cache Headers**: Appropriate cache headers for static assets
- [ ] **Compression**: Gzip compression enabled for static files

## 🗄️ Phase 5: Database Setup (Day 4)

### **5.1 PostgreSQL Deployment**

- [ ] **Container Started**: PostgreSQL container running and healthy
- [ ] **Health Check**: Database health check passing
- [ ] **Connection Test**: Can connect to database from API container
- [ ] **Logs Clean**: No errors in PostgreSQL logs

### **5.2 Database Migration**

- [ ] **API Container**: API container started successfully
- [ ] **Migration Run**: `alembic upgrade head` completed successfully
- [ ] **Tables Created**: All required tables present in database
- [ ] **Indexes Created**: Database indexes properly created
- [ ] **Admin User**: Admin user created successfully

### **5.3 Database Backup**

- [ ] **Backup Script**: Database backup script created
- [ ] **Backup Test**: Manual backup test successful
- [ ] **Cron Job**: Automated backup cron job configured
- [ ] **Backup Directory**: Backup storage directory created with proper permissions

## 🔐 Phase 6: OAuth Configuration (Day 4-5)

### **6.1 Google OAuth Setup**

- [ ] **Project Created**: Google Cloud project created or selected
- [ ] **APIs Enabled**: Calendar, Gmail, Drive APIs enabled
- [ ] **Consent Screen**: OAuth consent screen configured
- [ ] **Credentials Created**: OAuth 2.0 client credentials created
- [ ] **Redirect URIs**: Correct redirect URIs configured
- [ ] **Environment Variables**: Google OAuth variables set in .env.prod

### **6.2 Microsoft OAuth Setup**

- [ ] **App Registered**: Azure AD app registration created
- [ ] **Permissions Set**: Microsoft Graph API permissions configured
- [ ] **Client Secret**: Client secret generated and stored
- [ ] **Redirect URIs**: Correct redirect URIs configured
- [ ] **Environment Variables**: Microsoft OAuth variables set in .env.prod

### **6.3 OAuth Testing**

- [ ] **Google Flow**: Google OAuth authorization flow tested
- [ ] **Microsoft Flow**: Microsoft OAuth authorization flow tested
- [ ] **Callback URLs**: OAuth callback URLs accessible
- [ ] **Token Exchange**: Authorization code to token exchange working

## 🚀 Phase 7: Full Stack Deployment (Day 5-6)

### **7.1 Complete Application Stack**

- [ ] **All Services**: All Docker services started successfully
- [ ] **Health Checks**: All containers showing healthy status
- [ ] **Service Dependencies**: Inter-service communication working
- [ ] **Logs Clean**: No critical errors in any service logs

### **7.2 Service Verification**

- [ ] **API Health**: API health endpoint returning 200 OK
- [ ] **Frontend Loading**: Frontend accessible via HTTPS
- [ ] **Database Connection**: API successfully connecting to database
- [ ] **Redis Connection**: API successfully connecting to Redis
- [ ] **Celery Workers**: All Celery workers running and processing tasks

### **7.3 External Access Testing**

- [ ] **HTTPS Access**: `curl -f https://yourdomain.com/` successful
- [ ] **API Access**: `curl -f https://yourdomain.com/api/health/overall` successful
- [ ] **Static Assets**: CSS, JS, images loading correctly
- [ ] **No Mixed Content**: All assets served over HTTPS

## 📊 Phase 8: Monitoring Setup (Day 6)

### **8.1 Monitoring Services**

- [ ] **Prometheus**: Prometheus container running and collecting metrics
- [ ] **Grafana**: Grafana accessible with admin credentials
- [ ] **Loki**: Loki container running for log aggregation
- [ ] **Jaeger**: Jaeger running for distributed tracing

### **8.2 Dashboard Configuration**

- [ ] **Grafana Login**: Can access Grafana with admin password
- [ ] **Data Sources**: Prometheus and Loki data sources configured
- [ ] **Dashboards**: Pre-built dashboards imported and working
- [ ] **Alerts**: Basic alerting rules configured

### **8.3 Log Management**

- [ ] **Log Collection**: Loki collecting logs from all services
- [ ] **Log Retention**: Log retention policy configured (30 days)
- [ ] **Log Access**: Can view and search logs through Grafana

## 🧪 Phase 9: Testing and Validation (Day 7)

### **9.1 Functionality Testing**

- [ ] **User Registration**: New user registration working
- [ ] **User Login**: User authentication working
- [ ] **MFA Setup**: Multi-factor authentication functional
- [ ] **Dashboard Access**: User dashboard loading correctly
- [ ] **OAuth Connections**: Users can connect Google and Microsoft accounts

### **9.2 Performance Testing**

- [ ] **Page Load Speed**: Homepage loads in < 2 seconds
- [ ] **API Response Time**: API responses < 200ms (P95)
- [ ] **Database Performance**: Database queries < 100ms (P95)
- [ ] **Resource Usage**: CPU and memory usage within acceptable limits

### **9.3 Security Testing**

- [ ] **SSL Grade**: SSL Labs test shows A or A+ grade
- [ ] **Security Headers**: All security headers present
- [ ] **Vulnerability Scan**: No critical vulnerabilities found
- [ ] **Authentication**: Proper authentication required for protected endpoints

## 🔄 Phase 10: Final Verification (Day 7)

### **10.1 End-to-End Testing**

- [ ] **Complete User Flow**: Full user registration to OAuth connection flow
- [ ] **SMS Functionality**: SMS routing and responses working
- [ ] **Email Integration**: Email sending and receiving (if configured)
- [ ] **Calendar Sync**: Calendar synchronization working
- [ ] **Error Handling**: Proper error messages for various failure scenarios

### **10.2 Backup and Recovery**

- [ ] **Database Backup**: Automated backups working correctly
- [ ] **Backup Restoration**: Can restore from backup successfully
- [ ] **Configuration Backup**: System configuration documented
- [ ] **Disaster Recovery**: Recovery procedures documented

### **10.3 Documentation**

- [ ] **Deployment Notes**: Deployment process documented
- [ ] **Configuration Details**: All configuration changes recorded
- [ ] **Access Credentials**: All passwords and keys securely stored
- [ ] **Maintenance Guide**: Ongoing maintenance procedures documented

## ✅ Post-Deployment Tasks

### **Immediate (Day 1 after deployment)**

- [ ] **User Acceptance Testing**: Stakeholder testing completed
- [ ] **Performance Monitoring**: 24-hour performance metrics reviewed
- [ ] **Error Monitoring**: No critical errors in logs
- [ ] **Backup Verification**: First automated backup completed successfully

### **Short Term (Week 1)**

- [ ] **Security Audit**: External security audit scheduled/completed
- [ ] **Performance Optimization**: Performance bottlenecks identified and addressed
- [ ] **User Feedback**: Initial user feedback collected and addressed
- [ ] **Documentation Update**: All documentation updated with final configuration

### **Long Term (Month 1)**

- [ ] **Capacity Planning**: Resource usage trends analyzed
- [ ] **Scaling Strategy**: Scaling plan developed based on usage
- [ ] **Disaster Recovery Test**: Full disaster recovery procedure tested
- [ ] **Security Review**: Comprehensive security review completed

## 🚨 Rollback Plan

### **If Deployment Fails**

- [ ] **Stop Services**: `docker-compose -f docker/docker-compose.prod.yml down`
- [ ] **Restore Previous Version**: Revert to previous working configuration
- [ ] **Database Rollback**: Restore database from last known good backup
- [ ] **DNS Rollback**: Point domain to previous working server (if applicable)
- [ ] **Notify Stakeholders**: Communicate rollback and next steps

### **Emergency Contacts**

- [ ] **Technical Lead**: Contact information documented
- [ ] **Infrastructure Team**: On-call contact information
- [ ] **Domain Provider**: Support contact for DNS issues
- [ ] **VM Provider**: Support contact for infrastructure issues

## 📋 Sign-off Checklist

### **Technical Sign-off**

- [ ] **Infrastructure Team**: Infrastructure deployment approved
- [ ] **Security Team**: Security configuration approved
- [ ] **Development Team**: Application functionality verified
- [ ] **QA Team**: Testing completed and passed

### **Business Sign-off**

- [ ] **Product Owner**: Functionality meets requirements
- [ ] **Stakeholders**: User acceptance criteria met
- [ ] **Operations Team**: Monitoring and maintenance procedures in place
- [ ] **Final Approval**: Go-live approval received

---

**Deployment Date**: ******\_\_\_******  
**Deployed By**: ******\_\_\_******  
**Reviewed By**: ******\_\_\_******  
**Approved By**: ******\_\_\_******

This checklist ensures a comprehensive and systematic approach to deploying the Personal Assistant TDAH application in production with full OAuth integration capabilities.
