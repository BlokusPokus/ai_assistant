-- Fix Local Database Schema Migration
-- DESCRIPTION: Adds missing columns and updates column types to match production
-- VERSION: 007
-- DEPENDS: 000_complete_schema_migration.sql
-- ROLLBACK: See rollback section at the end

-- Fix users table
-- Add missing columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Update column types to match production
ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(255);
ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(255);

-- Fix auth_tokens table
-- Update column types to match production
ALTER TABLE auth_tokens ALTER COLUMN token TYPE VARCHAR(255);
ALTER TABLE auth_tokens ALTER COLUMN token_type TYPE VARCHAR(50);

-- Fix roles table
-- Update column types to match production
ALTER TABLE roles ALTER COLUMN name TYPE VARCHAR(100);
ALTER TABLE roles ALTER COLUMN description TYPE TEXT;

-- Add any other missing columns or type updates as needed
-- (This can be expanded based on further analysis)

-- ROLLBACK:
-- ALTER TABLE users DROP COLUMN IF EXISTS first_name;
-- ALTER TABLE users DROP COLUMN IF EXISTS last_name;
-- ALTER TABLE users DROP COLUMN IF EXISTS is_admin;
-- ALTER TABLE users ALTER COLUMN email TYPE VARCHAR;
-- ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR;
-- ALTER TABLE auth_tokens ALTER COLUMN token TYPE VARCHAR;
-- ALTER TABLE auth_tokens ALTER COLUMN token_type TYPE VARCHAR;
-- ALTER TABLE roles ALTER COLUMN name TYPE VARCHAR;
-- ALTER TABLE roles ALTER COLUMN description TYPE VARCHAR;
