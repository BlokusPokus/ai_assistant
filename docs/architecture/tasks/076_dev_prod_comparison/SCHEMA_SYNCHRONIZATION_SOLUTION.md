# 🚨 Schema Synchronization Solution

## **Critical Issue Identified**

Your local and production databases have **significant schema differences** that need immediate attention:

### **Users Table Differences:**

| Column          | Local Database      | Production Database      | Status                  |
| --------------- | ------------------- | ------------------------ | ----------------------- |
| `email`         | `character varying` | `character varying(255)` | ⚠️ **Different**        |
| `password_hash` | `character varying` | `character varying(255)` | ⚠️ **Different**        |
| `first_name`    | ❌ **Missing**      | `character varying(100)` | ❌ **Missing in local** |
| `last_name`     | ❌ **Missing**      | `character varying(100)` | ❌ **Missing in local** |
| `is_admin`      | ❌ **Missing**      | `boolean`                | ❌ **Missing in local** |

### **Auth Tokens Table Differences:**

| Column       | Local Database      | Production Database      | Status           |
| ------------ | ------------------- | ------------------------ | ---------------- |
| `token`      | `character varying` | `character varying(255)` | ⚠️ **Different** |
| `token_type` | `character varying` | `character varying(50)`  | ⚠️ **Different** |

### **Roles Table Differences:**

| Column        | Local Database      | Production Database      | Status           |
| ------------- | ------------------- | ------------------------ | ---------------- |
| `name`        | `character varying` | `character varying(100)` | ⚠️ **Different** |
| `description` | `character varying` | `text`                   | ⚠️ **Different** |

## **Root Cause Analysis**

1. **Schema Drift**: Your local database was created with an older schema
2. **Missing Migrations**: The complete schema migration (`000_complete_schema_migration.sql`) exists but wasn't applied to your local database
3. **Development vs Production**: Your local Postgres.app database is separate from the Docker PostgreSQL container

## **Solution Options**

### **Option 1: Fix Local Database (Recommended)**

- Apply the existing migration to your local database
- Add missing columns and update column types
- **Risk**: Low (additive changes only)
- **Effort**: Minimal

### **Option 2: Recreate Local Database**

- Drop and recreate your local database with the complete schema
- **Risk**: High (data loss)
- **Effort**: High (data migration required)

### **Option 3: Use Docker Database**

- Switch to using the Docker PostgreSQL container
- **Risk**: Medium (workflow change)
- **Effort**: Medium (configuration changes)

## **Recommended Solution: Option 1**

### **Step 1: Apply Schema Fixes**

```bash
# Run the schema fix script
./scripts/fix_local_schema.sh
```

### **Step 2: Verify Changes**

```bash
# Check users table
psql -U ianleblanc -d postgres -c "\d users"

# Check auth_tokens table
psql -U ianleblanc -d postgres -c "\d auth_tokens"

# Check roles table
psql -U ianleblanc -d postgres -c "\d roles"
```

### **Step 3: Test Application**

- Start your local development server
- Test user registration/login
- Test OAuth functionality
- Verify all features work correctly

## **Migration Details**

The migration file `007_fix_local_schema.sql` includes:

1. **Add Missing Columns**:

   - `first_name VARCHAR(100)`
   - `last_name VARCHAR(100)`
   - `is_admin BOOLEAN DEFAULT FALSE`

2. **Update Column Types**:

   - `email` → `VARCHAR(255)`
   - `password_hash` → `VARCHAR(255)`
   - `token` → `VARCHAR(255)`
   - `token_type` → `VARCHAR(50)`
   - `name` → `VARCHAR(100)`
   - `description` → `TEXT`

3. **Safe Operations**:
   - Uses `IF NOT EXISTS` for column additions
   - Uses `ALTER COLUMN TYPE` for type changes
   - Includes rollback instructions

## **Prevention Strategy**

### **1. Database Schema Management**

- Always run migrations in development before production
- Use version control for database schemas
- Implement schema validation in CI/CD

### **2. Development Workflow**

- Use the same database setup across all environments
- Document database setup procedures
- Regular schema synchronization checks

### **3. Monitoring**

- Add schema validation to your deployment pipeline
- Monitor for schema drift in production
- Regular database health checks

## **Next Steps**

1. **Immediate**: Run the schema fix script
2. **Short-term**: Test all functionality
3. **Medium-term**: Implement schema validation
4. **Long-term**: Establish database governance practices

## **Files Created**

- `src/personal_assistant/database/migrations/007_fix_local_schema.sql` - Migration file
- `scripts/fix_local_schema.sh` - Execution script
- `docs/architecture/tasks/076_dev_prod_comparison/SCHEMA_SYNCHRONIZATION_SOLUTION.md` - This document

## **Support**

If you encounter any issues:

1. Check the migration logs
2. Verify database connectivity
3. Review the rollback instructions
4. Contact the development team

---

**⚠️ Important**: Always backup your database before running migrations in production!
