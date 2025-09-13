# DigitalOcean Docker Deployment Guide

## 🎯 Overview

This guide provides step-by-step instructions for deploying the Personal Assistant TDAH application on DigitalOcean using Docker containers. DigitalOcean offers excellent Docker support with their Droplets and managed services.

## 🚀 DigitalOcean Deployment Options

### **Option 1: Docker Droplet (Recommended)**

- Pre-configured Ubuntu droplet with Docker installed
- Most cost-effective for single-server deployment
- Full control over the environment
- **Cost**: $48/month for 4 vCPUs, 8GB RAM, 160GB SSD

### **Option 2: DigitalOcean App Platform**

- Managed container platform (PaaS)
- Automatic scaling and load balancing
- Higher cost but less maintenance
- **Cost**: ~$84/month for equivalent resources

### **Option 3: Kubernetes (DO Kubernetes)**

- For future scaling and multiple environments
- Overkill for initial deployment
- **Cost**: ~$120/month minimum

**Recommendation**: Start with **Option 1 (Docker Droplet)** for initial deployment.

## 🏗️ Step-by-Step DigitalOcean Deployment

### **Phase 1: DigitalOcean Account Setup**

#### **1.1 Create DigitalOcean Account**

1. **Sign Up**: Go to [DigitalOcean](https://www.digitalocean.com/)
2. **Verification**: Complete email and phone verification
3. **Payment Method**: Add credit card or PayPal
4. **Initial Credit**: Use referral code for $200 credit (if available)

#### **1.2 Generate SSH Key**

```bash
# On your local machine, generate SSH key pair
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/do_personal_assistant

# Display public key to copy
cat ~/.ssh/do_personal_assistant.pub
```

#### **1.3 Add SSH Key to DigitalOcean**

1. **Navigate**: DigitalOcean Control Panel → Settings → Security
2. **Add SSH Key**: Click "Add SSH Key"
3. **Paste Key**: Paste the public key content
4. **Name**: "Personal Assistant Production Key"

### **Phase 2: Create Docker Droplet**

#### **2.1 Droplet Creation**

1. **Navigate**: DigitalOcean Control Panel → Create → Droplets

2. **Choose Image**:

   ```
   Distribution: Ubuntu 22.04 (LTS) x64
   OR
   Marketplace: Docker on Ubuntu 22.04
   ```

3. **Choose Plan**:

   ```
   Basic Plan
   Regular Intel with SSD
   $48/month: 4 vCPUs, 8 GB RAM, 160 GB SSD, 5 TB transfer
   ```

4. **Choose Datacenter**:

   ```
   Recommended regions:
   - New York 1, 2, or 3 (US East)
   - San Francisco 2 or 3 (US West)
   - Amsterdam 3 (Europe)
   - Singapore 1 (Asia)

   Choose closest to your target users
   ```

5. **Additional Options**:

   ```
   ✓ Monitoring (free)
   ✓ IPv6 (free)
   ✓ User data (we'll configure this)
   ✓ Backups (+$9.60/month - recommended for production)
   ```

6. **Authentication**:

   ```
   SSH Keys: Select your "Personal Assistant Production Key"
   ```

7. **Finalize**:
   ```
   Hostname: personal-assistant-prod
   Tags: production, personal-assistant, docker
   Project: Default (or create "Personal Assistant")
   ```

#### **2.2 User Data Script (Optional)**

Add this user data script for automatic initial setup:

```bash
#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install essential packages
apt-get install -y curl wget git ufw fail2ban htop nano unzip

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Install Docker (if not using Docker marketplace image)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create deploy user
adduser --disabled-password --gecos "" deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Setup deploy user SSH
mkdir -p /home/deploy/.ssh
cp /root/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Create application directory
mkdir -p /home/deploy/personal_assistant
chown deploy:deploy /home/deploy/personal_assistant

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

echo "Droplet setup completed!" > /home/deploy/setup_complete.txt
```

### **Phase 3: Initial Server Configuration**

#### **3.1 Connect to Droplet**

```bash
# Connect using your SSH key
ssh -i ~/.ssh/do_personal_assistant root@YOUR_DROPLET_IP

# Or if deploy user was created via user data
ssh -i ~/.ssh/do_personal_assistant deploy@YOUR_DROPLET_IP
```

#### **3.2 Verify Installation**

```bash
# Check Docker installation
docker --version
docker-compose --version

# Check system resources
htop
df -h
free -h

# Check firewall status
sudo ufw status
```

#### **3.3 Security Hardening**

```bash
# Configure fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Secure SSH configuration
sudo nano /etc/ssh/sshd_config

# Add/modify these lines:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart ssh
```

### **Phase 4: Domain Configuration with DigitalOcean DNS**

#### **4.1 Add Domain to DigitalOcean**

1. **Navigate**: DigitalOcean Control Panel → Networking → Domains
2. **Add Domain**: Enter your domain name (e.g., `yourdomain.com`)
3. **Verify Ownership**: Follow verification steps

#### **4.2 Configure DNS Records**

```bash
# Required DNS Records:
Type    Name             Value                    TTL
A       @                YOUR_DROPLET_IP         300
A       www              YOUR_DROPLET_IP         300
CNAME   api              yourdomain.com          300
CNAME   app              yourdomain.com          300

# Optional records:
MX      @                mail.yourdomain.com     300
TXT     @                "v=spf1 -all"           300
```

#### **4.3 Update Domain Nameservers**

Point your domain's nameservers to DigitalOcean:

```
ns1.digitalocean.com
ns2.digitalocean.com
ns3.digitalocean.com
```

### **Phase 5: Application Deployment**

#### **5.1 Clone Repository**

```bash
# Switch to deploy user if not already
su - deploy

# Clone your repository
git clone https://github.com/yourusername/personal_assistant.git
cd personal_assistant

# Verify all files are present
ls -la
```

#### **5.2 Environment Configuration**

```bash
# Create production environment file
cp docker/env.prod.example docker/.env.prod

# Edit with your specific values
nano docker/.env.prod
```

**DigitalOcean-Specific Environment Variables**:

```bash
# Database Configuration
PROD_DB_USER=prod_user
PROD_DB_PASSWORD=your_very_secure_db_password_here

# Redis Configuration
PROD_REDIS_PASSWORD=your_very_secure_redis_password_here

# Domain Configuration
DOMAIN_NAME=yourdomain.com
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://yourdomain.com/api

# DigitalOcean Specific
DO_DROPLET_IP=YOUR_DROPLET_IP
DO_REGION=nyc1  # or your chosen region
```

#### **5.3 SSL Certificate Setup**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Stop any running nginx (if any)
sudo systemctl stop nginx 2>/dev/null || true

# Generate SSL certificate using standalone mode
sudo certbot certonly --standalone --agree-tos --email your-email@yourdomain.com -d yourdomain.com -d www.yourdomain.com

# Copy certificates to application directory
sudo mkdir -p /home/deploy/personal_assistant/docker/nginx/ssl/prod
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /home/deploy/personal_assistant/docker/nginx/ssl/prod/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /home/deploy/personal_assistant/docker/nginx/ssl/prod/key.pem
sudo chown -R deploy:deploy /home/deploy/personal_assistant/docker/nginx/ssl/
```

#### **5.4 Frontend Build**

```bash
# Navigate to frontend directory
cd src/apps/frontend

# Install dependencies
npm ci

# Build for production
npm run build

# Copy built files to nginx directory
mkdir -p ../../docker/nginx/static
cp -r dist/* ../../docker/nginx/static/

# Return to project root
cd ../../../
```

### **Phase 6: Docker Container Deployment**

#### **6.1 Build and Deploy**

```bash
# Pull latest images and build
docker-compose -f docker/docker-compose.prod.yml pull
docker-compose -f docker/docker-compose.prod.yml build --no-cache

# Start the database first
docker-compose -f docker/docker-compose.prod.yml up -d postgres redis

# Wait for services to be ready
sleep 30

# Run database migrations
docker-compose -f docker/docker-compose.prod.yml up -d api
sleep 30
docker-compose -f docker/docker-compose.prod.yml exec api python -m alembic upgrade head

# Create admin user
docker-compose -f docker/docker-compose.prod.yml exec api python scripts/create_admin_user.py

# Start all services
docker-compose -f docker/docker-compose.prod.yml up -d
```

#### **6.2 Verify Deployment**

```bash
# Check all containers are running
docker-compose -f docker/docker-compose.prod.yml ps

# Check logs for any errors
docker-compose -f docker/docker-compose.prod.yml logs -f --tail=50

# Test local connectivity
curl -f http://localhost:8000/health/overall
curl -f http://localhost/health  # nginx
```

### **Phase 7: DigitalOcean Monitoring Integration**

#### **7.1 Enable DigitalOcean Monitoring**

```bash
# Install DO monitoring agent
curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash

# Configure monitoring
sudo systemctl enable do-agent
sudo systemctl start do-agent
```

#### **7.2 Configure Alerts**

1. **Navigate**: DigitalOcean Control Panel → Monitoring
2. **Create Alert Policy**:

   ```
   Name: Personal Assistant High CPU
   Condition: CPU > 80% for 5 minutes
   Notification: Email to your-email@domain.com
   ```

3. **Additional Alerts**:
   ```
   - Memory usage > 90% for 5 minutes
   - Disk usage > 85%
   - Load average > 4.0 for 10 minutes
   ```

### **Phase 8: Backup Configuration**

#### **8.1 DigitalOcean Droplet Backups**

```bash
# Enable automatic backups (if not done during creation)
# This is done through the DigitalOcean control panel
# Cost: 20% of droplet cost (~$9.60/month)
```

#### **8.2 Database Backups to DigitalOcean Spaces**

```bash
# Install s3cmd for DigitalOcean Spaces
sudo apt install s3cmd -y

# Configure s3cmd for DO Spaces
s3cmd --configure
# Endpoint: nyc3.digitaloceanspaces.com (or your region)
# Access Key: Your Spaces access key
# Secret Key: Your Spaces secret key
```

**Backup Script for DigitalOcean Spaces**:

```bash
#!/bin/bash
# /home/deploy/backup_to_spaces.sh

BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="personal_assistant_prod"
SPACES_BUCKET="your-backup-bucket"

mkdir -p $BACKUP_DIR

# Create database backup
docker exec personal_assistant_postgres_prod pg_dump -U prod_user $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Upload to DigitalOcean Spaces
s3cmd put $BACKUP_DIR/db_backup_$DATE.sql.gz s3://$SPACES_BUCKET/database-backups/

# Clean up local files older than 7 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed and uploaded to Spaces: db_backup_$DATE.sql.gz"
```

#### **8.3 Automated Backup Schedule**

```bash
# Make backup script executable
chmod +x /home/deploy/backup_to_spaces.sh

# Add to crontab
crontab -e

# Add these lines:
# Database backup every 6 hours
0 */6 * * * /home/deploy/backup_to_spaces.sh >> /home/deploy/logs/backup.log 2>&1

# SSL certificate renewal
0 2 * * * /usr/bin/certbot renew --quiet --deploy-hook "cd /home/deploy/personal_assistant && docker-compose -f docker/docker-compose.prod.yml restart nginx"
```

### **Phase 9: Performance Optimization**

#### **9.1 DigitalOcean Droplet Optimization**

```bash
# Configure swap (recommended for 8GB RAM)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimize kernel parameters
sudo nano /etc/sysctl.conf

# Add these lines:
# vm.swappiness=10
# vm.vfs_cache_pressure=50
# net.core.rmem_max=134217728
# net.core.wmem_max=134217728

# Apply changes
sudo sysctl -p
```

#### **9.2 Docker Performance Tuning**

```bash
# Configure Docker daemon for production
sudo nano /etc/docker/daemon.json

# Add configuration:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "userland-proxy": false,
  "experimental": false
}

# Restart Docker
sudo systemctl restart docker
```

### **Phase 10: DigitalOcean-Specific Monitoring**

#### **10.1 Grafana Dashboard for DigitalOcean**

Add DigitalOcean-specific metrics to your Grafana dashboards:

```yaml
# Add to docker/monitoring/grafana/dashboards/digitalocean-metrics.json
{
  "dashboard":
    {
      "title": "DigitalOcean Droplet Metrics",
      "panels":
        [
          {
            "title": "CPU Usage",
            "type": "graph",
            "targets":
              [
                {
                  "expr": '100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
                },
              ],
          },
          {
            "title": "Memory Usage",
            "type": "graph",
            "targets":
              [
                {
                  "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
                },
              ],
          },
          {
            "title": "Disk Usage",
            "type": "graph",
            "targets":
              [
                {
                  "expr": '(node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_avail_bytes{fstype!="tmpfs"}) / node_filesystem_size_bytes{fstype!="tmpfs"} * 100',
                },
              ],
          },
        ],
    },
}
```

## 🔧 DigitalOcean-Specific Troubleshooting

### **Common DigitalOcean Issues**

#### **Issue: Droplet Not Accessible**

```bash
# Check droplet status in DO control panel
# Verify firewall rules
sudo ufw status

# Check SSH service
sudo systemctl status ssh

# Check network configuration
ip addr show
```

#### **Issue: DNS Not Resolving**

```bash
# Verify DNS settings in DO control panel
# Check nameserver configuration
nslookup yourdomain.com

# Test DNS propagation
dig yourdomain.com @8.8.8.8
```

#### **Issue: SSL Certificate Problems**

```bash
# Check certificate status
sudo certbot certificates

# Test certificate manually
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check nginx configuration
docker-compose -f docker/docker-compose.prod.yml exec nginx nginx -t
```

#### **Issue: Performance Problems**

```bash
# Check droplet resources
htop
df -h
free -h

# Monitor Docker containers
docker stats

# Check DigitalOcean monitoring graphs
# Navigate to: DO Control Panel → Droplets → Your Droplet → Graphs
```

### **DigitalOcean Support Resources**

#### **Getting Help**

- **Documentation**: [DigitalOcean Docs](https://docs.digitalocean.com/)
- **Community**: [DigitalOcean Community](https://www.digitalocean.com/community/)
- **Support Tickets**: Available for all paid accounts
- **Live Chat**: Available during business hours

#### **Useful DigitalOcean Commands**

```bash
# Check droplet metadata
curl -s http://169.254.169.254/metadata/v1/droplet/id

# Get droplet region
curl -s http://169.254.169.254/metadata/v1/region

# Check floating IP (if assigned)
curl -s http://169.254.169.254/metadata/v1/floating_ip/ipv4/active
```

## 📊 Cost Optimization

### **Monthly Cost Breakdown**

```
Droplet (4 vCPU, 8GB RAM): $48.00
Backups (20% of droplet):   $9.60
Monitoring (free):          $0.00
Spaces (if used):           $5.00 (250GB)
Bandwidth (5TB included):   $0.00
Total:                      ~$62.60/month
```

### **Cost Saving Tips**

1. **Resize Droplet**: Start with smaller size, scale up as needed
2. **Snapshot vs Backups**: Use snapshots for one-time backups ($0.05/GB/month)
3. **Reserved Instances**: Save up to 15% with 1-year commitment
4. **Monitoring**: Use built-in monitoring instead of external services

## 🚀 Scaling Options

### **Vertical Scaling (Resize Droplet)**

```bash
# Available upgrade paths:
# Current: $48/month (4 vCPU, 8GB RAM)
# Next:    $96/month (8 vCPU, 16GB RAM)
# Max:     $640/month (32 vCPU, 192GB RAM)
```

### **Horizontal Scaling Options**

1. **Load Balancer**: $12/month + additional droplets
2. **Database Cluster**: Managed PostgreSQL starting at $60/month
3. **Redis Cluster**: Managed Redis starting at $25/month

## ✅ DigitalOcean Deployment Checklist

### **Pre-Deployment**

- [ ] DigitalOcean account created and verified
- [ ] SSH key generated and added to account
- [ ] Domain name ready for configuration
- [ ] Payment method added to account

### **Droplet Setup**

- [ ] Docker droplet created with correct specifications
- [ ] SSH access configured and tested
- [ ] Firewall rules configured (22, 80, 443)
- [ ] Monitoring enabled
- [ ] Backups enabled (recommended)

### **Application Deployment**

- [ ] Repository cloned to droplet
- [ ] Environment variables configured
- [ ] SSL certificates generated and configured
- [ ] Frontend built and deployed
- [ ] All Docker containers running and healthy

### **Post-Deployment**

- [ ] Domain DNS configured and propagating
- [ ] SSL certificate valid (A grade)
- [ ] Application accessible via HTTPS
- [ ] OAuth integration tested
- [ ] Monitoring dashboards accessible
- [ ] Backup system operational

---

This DigitalOcean-specific deployment guide provides all the necessary steps to successfully deploy your Personal Assistant TDAH application on DigitalOcean's infrastructure with Docker containers.
