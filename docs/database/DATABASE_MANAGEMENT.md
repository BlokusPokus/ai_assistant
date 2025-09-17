# Database Management Guide

This guide helps you prevent database loss and manage your PostgreSQL database effectively.

## 🛡️ **Prevention Strategies**

### **1. Automated Backups**

```bash
# Create a backup
python scripts/backup_database.py backup

# Restore from backup
python scripts/backup_database.py restore --file backups/personal_assistant_backup_20240913_120000.sql

# Setup automated daily backups
./scripts/setup_backup_cron.sh
```

### **2. Health Monitoring**

```bash
# Check database health
python scripts/check_database_health.py

# Startup health check (runs automatically)
python scripts/startup_health_check.py
```

### **3. Database Initialization**

```bash
# Initialize database (if tables are missing)
python scripts/init_database.py
```

## 🚨 **Emergency Recovery**

If your database is lost or corrupted:

1. **Check if PostgreSQL is running:**

   ```bash
   brew services list | grep postgresql
   # or
   pg_isready -h localhost -p 5432
   ```

2. **Restore from latest backup:**

   ```bash
   python scripts/backup_database.py restore --file backups/latest_backup.sql
   ```

3. **Or reinitialize database:**

   ```bash
   python scripts/init_database.py
   ```

4. **Verify everything is working:**
   ```bash
   python scripts/check_database_health.py
   python run_server.py
   ```

## 📊 **Database Information**

- **Database Type:** PostgreSQL
- **Default Port:** 5432
- **Default Database:** postgres
- **Default User:** ianleblanc
- **Connection String:** `postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres`

## 🔧 **Configuration**

Database settings are configured in:

- `config/development.env` (development)
- `config/production.env` (production)
- Environment variable: `REAL_DB_URL`

## 📁 **Backup Storage**

- **Location:** `backups/` directory
- **Format:** SQL dump files
- **Naming:** `personal_assistant_backup_YYYYMMDD_HHMMSS.sql`
- **Retention:** Configure in cron job

## 🐳 **Docker Usage**

If using Docker Compose:

```bash
# Start with persistent volumes
docker-compose -f docker/docker-compose.dev.yml up -d

# Backup Docker database
docker exec personal_assistant_postgres pg_dump -U ianleblanc personal_assistant > backup.sql

# Restore to Docker database
docker exec -i personal_assistant_postgres psql -U ianleblanc personal_assistant < backup.sql
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"relation does not exist"**

   - Run: `python scripts/init_database.py`

2. **"Connection refused"**

   - Check if PostgreSQL is running
   - Verify connection settings

3. **"Authentication failed"**

   - Check username/password in config
   - Verify database exists

4. **"Permission denied"**
   - Check file permissions: `chmod +x scripts/*.py`
   - Verify database user permissions

### **Logs:**

- Application logs: `logs/`
- Backup logs: `logs/backup.log`
- Health check logs: `logs/health_check.log`

## 📋 **Maintenance Schedule**

- **Daily:** Automated backups at 2:00 AM
- **Weekly:** Health checks on Mondays at 6:00 AM
- **Monthly:** Review backup retention policy
- **Before major changes:** Manual backup

## 🆘 **Emergency Contacts**

If you need help:

1. Check this guide first
2. Review logs in `logs/` directory
3. Run health check scripts
4. Check PostgreSQL service status
