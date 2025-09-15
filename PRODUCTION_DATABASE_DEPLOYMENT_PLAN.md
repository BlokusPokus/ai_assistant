# 🗄️ Production Database Deployment Plan

## 📊 **Current Situation Analysis**

### **Development Database:**

- **Tables**: 43 tables (complete schema)
- **Migration Tracking**: ❌ None (created directly from SQLAlchemy models)
- **Status**: Fully functional with all features

### **Production Database:**

- **Tables**: 0 tables (empty)
- **Migration Tracking**: ❌ None
- **Status**: ❌ Not functional (can't login/signup)

### **Migration Files:**

- **Existing**: 11 migration files (incomplete)
- **New**: 1 complete schema migration file
- **Total**: 12 migration files

## 🎯 **Deployment Strategy**

### **Option 1: Complete Schema Migration (Recommended)**

Use the new `000_complete_schema_migration.sql` to create the entire schema at once.

**Pros:**

- ✅ Creates exact same schema as development
- ✅ Single migration, no dependency issues
- ✅ Fast deployment
- ✅ Guaranteed consistency

**Cons:**

- ❌ Skips individual migration history
- ❌ No granular rollback per feature

### **Option 2: Sequential Migration**

Apply all 12 migration files in order.

**Pros:**

- ✅ Complete migration history
- ✅ Granular rollback capability
- ✅ Proper audit trail

**Cons:**

- ❌ Risk of dependency conflicts
- ❌ May not match development exactly
- ❌ Slower deployment

## 🚀 **Recommended Deployment Steps**

### **Step 1: Backup Current State**

```bash
# On production server
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_dump -U personal_assistant_prod personal_assistant_prod > backup_before_migration.sql
```

### **Step 2: Apply Complete Schema Migration**

```bash
# On production server
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
import asyncio
from src.personal_assistant.database.migrations.manager import migration_manager

async def apply_complete_schema():
    # Apply only the complete schema migration
    pending = await migration_manager.get_pending_migrations()
    complete_schema = [m for m in pending if m.migration_name == '000_complete_schema_migration']

    if complete_schema:
        result = await migration_manager.apply_migration(complete_schema[0], 'production_deployment')
        print(f'Migration result: {result}')
    else:
        print('Complete schema migration not found')

asyncio.run(apply_complete_schema())
"
```

### **Step 3: Verify Schema**

```bash
# Check tables were created
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod -c "\dt"

# Should show 43 tables
```

### **Step 4: Create Admin User**

```bash
# Create admin user
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
import asyncio
from src.personal_assistant.database.models.users import User
from src.personal_assistant.database.session import _get_session_factory

async def create_admin():
    session_factory = _get_session_factory()
    async with session_factory() as db:
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

### **Step 5: Test Application**

```bash
# Test API health
curl -X GET https://ianleblanc.ca/api/health

# Test login endpoint
curl -X POST https://ianleblanc.ca/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔄 **Alternative: Sequential Migration**

If you prefer the sequential approach:

```bash
# Apply all migrations in order
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
import asyncio
from src.personal_assistant.database.migrations.manager import migration_manager

async def apply_all_migrations():
    result = await migration_manager.apply_all_pending('production_deployment')
    print(f'Migration result: {result}')

asyncio.run(apply_all_migrations())
"
```

## ⚠️ **Important Notes**

1. **Backup First**: Always backup before migration
2. **Test Locally**: Test the migration on a copy of production data first
3. **Monitor Logs**: Watch for errors during migration
4. **Verify Data**: Ensure all tables and data are correct after migration

## 🎯 **Expected Result**

After successful deployment:

- ✅ 43 tables created in production
- ✅ Admin user can login
- ✅ All features functional
- ✅ Database matches development schema exactly

## 🔧 **Troubleshooting**

### **If Migration Fails:**

1. Check logs: `docker-compose -f docker/docker-compose.prod.yml logs api`
2. Restore backup: `docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod < backup_before_migration.sql`
3. Fix issues and retry

### **If Tables Don't Match:**

1. Compare table counts: `docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"`
2. Check specific tables: `docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod -c "\dt"`

## 📋 **Quick Commands Summary**

```bash
# Connect to production
ssh deploy@YOUR_DROPLET_IP
cd /home/deploy/ai_assistant

# Backup database
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_dump -U personal_assistant_prod personal_assistant_prod > backup_before_migration.sql

# Apply complete schema migration
docker-compose -f docker/docker-compose.prod.yml exec api python -c "
import asyncio
from src.personal_assistant.database.migrations.manager import migration_manager
async def apply_complete_schema():
    pending = await migration_manager.get_pending_migrations()
    complete_schema = [m for m in pending if m.migration_name == '000_complete_schema_migration']
    if complete_schema:
        result = await migration_manager.apply_migration(complete_schema[0], 'production_deployment')
        print(f'Migration result: {result}')
asyncio.run(apply_complete_schema())
"

# Verify tables
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U personal_assistant_prod -d personal_assistant_prod -c "\dt"

# Test API
curl -X GET https://ianleblanc.ca/api/health
```
