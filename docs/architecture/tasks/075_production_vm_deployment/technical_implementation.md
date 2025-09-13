# Technical Implementation Guide - Production VM Deployment

## 🏗️ Infrastructure Architecture

### **System Overview**

```
Internet
    ↓
[Domain: yourdomain.com]
    ↓
[Cloudflare/DNS Provider]
    ↓
[VM Public IP]
    ↓
[Nginx Reverse Proxy] ← SSL/TLS Termination
    ↓
[Docker Network: personal_assistant_prod_network]
    ↓
┌─────────────────────────────────────────────────────────┐
│                     Docker Services                     │
├─────────────────────────────────────────────────────────┤
│ Frontend (Static Files) → Nginx                        │
│ API (FastAPI) → Port 8000                             │
│ PostgreSQL → Port 5432                                │
│ Redis → Port 6379                                     │
│ Celery Workers (5 specialized queues)                 │
│ Monitoring Stack (Prometheus, Grafana, Loki, Jaeger)  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Step-by-Step Implementation

### **Phase 1: VM and Domain Setup**

#### **1.1 VM Provisioning**

**Recommended Providers:**

- **DigitalOcean**: $40/month (4 vCPU, 8GB RAM, 160GB SSD)
- **AWS EC2**: t3.large instance (~$60/month)
- **Google Cloud**: e2-standard-4 (~$50/month)
- **Linode**: $40/month (4 vCPU, 8GB RAM, 160GB SSD)

**VM Specifications:**

```bash
# Minimum Requirements
CPU: 4 vCPUs
RAM: 8GB
Storage: 100GB SSD
OS: Ubuntu 22.04 LTS
Network: Public IP + Firewall
```

**Initial VM Setup:**

```bash
# Connect to VM
ssh root@YOUR_VM_IP

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y curl wget git ufw fail2ban htop nano

# Configure firewall
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable

# Create non-root user
adduser deploy
usermod -aG sudo deploy
```

#### **1.2 Domain Configuration**

**DNS Records Setup:**

```bash
# Required DNS Records:
Type    Name             Value           TTL
A       yourdomain.com   YOUR_VM_IP     300
A       www              YOUR_VM_IP     300
CNAME   api              yourdomain.com 300
CNAME   app              yourdomain.com 300

# For OAuth redirects:
# Google: https://yourdomain.com/api/oauth/google/callback
# Microsoft: https://yourdomain.com/api/oauth/microsoft/callback
```

### **Phase 2: Docker and Dependencies**

#### **2.1 Docker Installation**

```bash
# Switch to deploy user
su - deploy

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply group changes
exit
ssh deploy@YOUR_VM_IP
```

#### **2.2 Application Code Deployment**

```bash
# Clone repository
git clone https://github.com/yourusername/personal_assistant.git
cd personal_assistant

# Create logs directory
mkdir -p logs

# Set up environment files
cp docker/env.prod.example docker/.env.prod
```

### **Phase 3: SSL Certificate Setup**

#### **3.1 Nginx Installation (for Certbot)**

```bash
# Install Nginx temporarily for certificate generation
sudo apt install -y nginx certbot python3-certbot-nginx

# Stop nginx (we'll use Docker nginx)
sudo systemctl stop nginx
sudo systemctl disable nginx
```

#### **3.2 Let's Encrypt Certificate**

```bash
# Generate certificate using standalone mode
sudo certbot certonly --standalone --agree-tos --email your-email@domain.com -d yourdomain.com -d www.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

#### **3.3 Certificate Integration**

```bash
# Copy certificates to nginx SSL directory
sudo mkdir -p /home/deploy/personal_assistant/docker/nginx/ssl/prod
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /home/deploy/personal_assistant/docker/nginx/ssl/prod/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /home/deploy/personal_assistant/docker/nginx/ssl/prod/key.pem
sudo chown -R deploy:deploy /home/deploy/personal_assistant/docker/nginx/ssl/

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook "cd /home/deploy/personal_assistant && docker-compose -f docker/docker-compose.prod.yml restart nginx"
```

### **Phase 4: Environment Configuration**

#### **4.1 Production Environment Variables**

```bash
# Edit docker/.env.prod
nano docker/.env.prod
```

**Complete .env.prod file:**

```bash
# Database Configuration
PROD_DB_USER=prod_user
PROD_DB_PASSWORD=your_very_secure_db_password_here_min_32_chars

# Redis Configuration
PROD_REDIS_PASSWORD=your_very_secure_redis_password_here_min_32_chars

# Application Security
JWT_SECRET_KEY=your_jwt_secret_key_minimum_256_bits_base64_encoded
ENCRYPTION_KEY=your_32_character_encryption_key_here

# API Keys
GOOGLE_API_KEY=your_google_gemini_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret_here
GOOGLE_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/google/callback

MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_application_id_guid_here
MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_client_secret_here
MICROSOFT_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/microsoft/callback

# Notion (optional)
NOTION_OAUTH_CLIENT_ID=your_notion_oauth_client_id_here
NOTION_OAUTH_CLIENT_SECRET=your_notion_oauth_client_secret_here
NOTION_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/notion/callback

# Monitoring
PROD_GRAFANA_PASSWORD=your_secure_grafana_password_here

# Domain Configuration
DOMAIN_NAME=yourdomain.com
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://yourdomain.com/api
```

#### **4.2 Application Configuration Updates**

```bash
# Update src/personal_assistant/config/settings.py if needed
# Ensure OAuth redirect URIs use production domain
nano src/personal_assistant/config/settings.py
```

### **Phase 5: Frontend Build**

#### **5.1 Node.js Installation**

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be v20.x
npm --version   # Should be 10.x
```

#### **5.2 Frontend Build Process**

```bash
# Navigate to frontend directory
cd src/apps/frontend

# Install dependencies
npm ci --production=false

# Build for production
npm run build

# Copy built files to nginx static directory
mkdir -p ../../docker/nginx/static
cp -r dist/* ../../docker/nginx/static/

# Return to project root
cd ../../../
```

#### **5.3 Nginx Static File Configuration**

```bash
# Update nginx configuration to serve static files
# File: docker/nginx/conf.d/locations/frontend.conf
cat > docker/nginx/conf.d/locations/frontend.conf << 'EOF'
# Frontend static files
location / {
    root /usr/share/nginx/html;
    index index.html;
    try_files $uri $uri/ /index.html;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers for HTML
    location ~* \.html$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
}
EOF
```

### **Phase 6: Database Setup**

#### **6.1 Database Initialization**

```bash
# Start only PostgreSQL first
docker-compose -f docker/docker-compose.prod.yml up -d postgres

# Wait for PostgreSQL to be ready
sleep 30

# Check PostgreSQL health
docker-compose -f docker/docker-compose.prod.yml logs postgres
```

#### **6.2 Database Migration**

```bash
# Start the API service to run migrations
docker-compose -f docker/docker-compose.prod.yml up -d api

# Wait for API to be ready
sleep 30

# Run database migrations
docker-compose -f docker/docker-compose.prod.yml exec api python -m alembic upgrade head

# Create admin user
docker-compose -f docker/docker-compose.prod.yml exec api python scripts/create_admin_user.py
```

### **Phase 7: OAuth Provider Setup**

#### **7.1 Google OAuth Configuration**

**Google Cloud Console Setup:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing project
3. Enable APIs:

   - Google Calendar API
   - Gmail API
   - Google Drive API
   - YouTube Data API v3

4. Create OAuth 2.0 Credentials:

   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Name: "Personal Assistant TDAH Production"
   - Authorized JavaScript origins:
     - `https://yourdomain.com`
   - Authorized redirect URIs:
     - `https://yourdomain.com/api/oauth/google/callback`
     - `https://yourdomain.com/oauth/google/callback`

5. Configure OAuth consent screen:
   - User Type: External
   - App name: "Personal Assistant TDAH"
   - User support email: your-email@domain.com
   - Developer contact: your-email@domain.com
   - Scopes: Add the scopes your app needs

#### **7.2 Microsoft OAuth Configuration**

**Azure App Registration:**

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration":

   - Name: "Personal Assistant TDAH Production"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI:
     - Type: Web
     - URI: `https://yourdomain.com/api/oauth/microsoft/callback`

4. Configure API Permissions:

   - Microsoft Graph:
     - `Calendars.ReadWrite`
     - `Mail.ReadWrite`
     - `Files.ReadWrite.All`
     - `User.Read`
     - `offline_access`

5. Generate Client Secret:
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Copy the secret value (you won't see it again)

### **Phase 8: Full Application Deployment**

#### **8.1 Complete Stack Deployment**

```bash
# Deploy all services
docker-compose -f docker/docker-compose.prod.yml up -d

# Check all services are running
docker-compose -f docker/docker-compose.prod.yml ps

# Check logs for any errors
docker-compose -f docker/docker-compose.prod.yml logs -f --tail=50
```

#### **8.2 Service Verification**

```bash
# Test individual services
curl -f http://localhost:8000/health/overall  # API health
curl -f http://localhost:9090/               # Prometheus
curl -f http://localhost:3000/               # Grafana

# Test external access
curl -f https://yourdomain.com/health        # Nginx health
curl -f https://yourdomain.com/api/health/overall  # API through proxy
```

### **Phase 9: Monitoring and Logging**

#### **9.1 Grafana Setup**

```bash
# Access Grafana at https://yourdomain.com:3000
# Login: admin / [PROD_GRAFANA_PASSWORD from .env.prod]

# Import existing dashboards from docker/monitoring/grafana/dashboards/
# Dashboards should auto-load from provisioning
```

#### **9.2 Log Aggregation**

```bash
# Logs are automatically collected by Loki
# Access via Grafana → Explore → Loki data source

# Manual log viewing
docker-compose -f docker/docker-compose.prod.yml logs -f api
docker-compose -f docker/docker-compose.prod.yml logs -f nginx
```

### **Phase 10: Backup and Recovery**

#### **10.1 Database Backup Setup**

```bash
# Create backup script
cat > /home/deploy/backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="personal_assistant_prod"

mkdir -p $BACKUP_DIR

# Create database backup
docker exec personal_assistant_postgres_prod pg_dump -U prod_user $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 30 backups
ls -t $BACKUP_DIR/db_backup_*.sql.gz | tail -n +31 | xargs -r rm

echo "Database backup completed: db_backup_$DATE.sql.gz"
EOF

chmod +x /home/deploy/backup_database.sh
```

#### **10.2 Automated Backup Schedule**

```bash
# Setup cron job for backups
crontab -e

# Add these lines:
# Database backup every 6 hours
0 */6 * * * /home/deploy/backup_database.sh >> /home/deploy/logs/backup.log 2>&1

# SSL certificate renewal check daily
0 2 * * * /usr/bin/certbot renew --quiet --deploy-hook "cd /home/deploy/personal_assistant && docker-compose -f docker/docker-compose.prod.yml restart nginx"
```

## 🧪 Testing and Verification

### **Application Testing Checklist**

#### **Infrastructure Tests**

```bash
# Test DNS resolution
nslookup yourdomain.com
nslookup www.yourdomain.com

# Test SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Test firewall
nmap -p 22,80,443 yourdomain.com
```

#### **Application Tests**

```bash
# Test frontend
curl -f https://yourdomain.com/

# Test API endpoints
curl -f https://yourdomain.com/api/health/overall
curl -f https://yourdomain.com/api/auth/health

# Test OAuth endpoints (should return proper error/redirect)
curl -I https://yourdomain.com/api/oauth/google/authorize
curl -I https://yourdomain.com/api/oauth/microsoft/authorize
```

#### **OAuth Integration Tests**

1. **Google OAuth Test**:

   - Navigate to: `https://yourdomain.com/oauth/google/authorize`
   - Should redirect to Google login
   - After login, should redirect back to your callback URL

2. **Microsoft OAuth Test**:
   - Navigate to: `https://yourdomain.com/oauth/microsoft/authorize`
   - Should redirect to Microsoft login
   - After login, should redirect back to your callback URL

### **Performance Testing**

```bash
# Test page load times
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/

# Where curl-format.txt contains:
#     time_namelookup:  %{time_namelookup}s\n
#        time_connect:  %{time_connect}s\n
#     time_appconnect:  %{time_appconnect}s\n
#    time_pretransfer:  %{time_pretransfer}s\n
#       time_redirect:  %{time_redirect}s\n
#  time_starttransfer:  %{time_starttransfer}s\n
#                     ----------\n
#          time_total:  %{time_total}s\n
```

## 🔒 Security Hardening

### **System Security**

```bash
# Install and configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure SSH security
sudo nano /etc/ssh/sshd_config
# Add/modify:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

sudo systemctl restart ssh
```

### **Application Security**

```bash
# Verify non-root containers
docker-compose -f docker/docker-compose.prod.yml exec api whoami
# Should return: appuser

# Check security headers
curl -I https://yourdomain.com/
# Should include security headers from nginx configuration
```

## 🚨 Troubleshooting Guide

### **Common Issues**

#### **SSL Certificate Issues**

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew --force-renewal

# Check nginx SSL configuration
docker-compose -f docker/docker-compose.prod.yml exec nginx nginx -t
```

#### **OAuth Callback Issues**

```bash
# Check OAuth provider configurations match exactly:
# Google: https://yourdomain.com/api/oauth/google/callback
# Microsoft: https://yourdomain.com/api/oauth/microsoft/callback

# Check environment variables are loaded
docker-compose -f docker/docker-compose.prod.yml exec api env | grep OAUTH
```

#### **Database Connection Issues**

```bash
# Check PostgreSQL logs
docker-compose -f docker/docker-compose.prod.yml logs postgres

# Test database connection
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U prod_user -d personal_assistant_prod -c "SELECT 1;"
```

#### **Frontend Not Loading**

```bash
# Check nginx logs
docker-compose -f docker/docker-compose.prod.yml logs nginx

# Verify static files are present
docker-compose -f docker/docker-compose.prod.yml exec nginx ls -la /usr/share/nginx/html/

# Check nginx configuration
docker-compose -f docker/docker-compose.prod.yml exec nginx nginx -t
```

## 📊 Monitoring and Maintenance

### **Health Monitoring**

```bash
# Check all container health
docker-compose -f docker/docker-compose.prod.yml ps

# Monitor resource usage
docker stats

# Check disk usage
df -h
du -sh /home/deploy/personal_assistant/
```

### **Log Monitoring**

```bash
# Application logs
docker-compose -f docker/docker-compose.prod.yml logs -f api

# Nginx access logs
docker-compose -f docker/docker-compose.prod.yml logs -f nginx

# System logs
sudo journalctl -f
```

### **Performance Monitoring**

- **Grafana Dashboards**: https://yourdomain.com:3000
- **Prometheus Metrics**: https://yourdomain.com:9090
- **Application Traces**: https://yourdomain.com:16686

## 🎯 Post-Deployment Checklist

### **Immediate (Day 1)**

- [ ] Application accessible via HTTPS
- [ ] All Docker services healthy
- [ ] SSL certificate valid (A grade)
- [ ] Database migrations completed
- [ ] Admin user created
- [ ] Basic functionality tested

### **Short Term (Week 1)**

- [ ] OAuth flows tested and working
- [ ] User registration tested
- [ ] SMS functionality verified
- [ ] Monitoring dashboards configured
- [ ] Backup system verified
- [ ] Performance benchmarks established

### **Long Term (Month 1)**

- [ ] Security audit completed
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Documentation updated
- [ ] Disaster recovery tested

---

This technical implementation guide provides a comprehensive step-by-step approach to deploying the Personal Assistant TDAH application in a production environment with full OAuth integration capabilities.
