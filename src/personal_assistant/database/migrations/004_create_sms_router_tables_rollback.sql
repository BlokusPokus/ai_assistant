-- Rollback Migration: 004_create_sms_router_tables
-- Description: Drop SMS Router Service database tables
-- This will remove all SMS Router related tables and data

-- Drop indexes first
DROP INDEX IF EXISTS idx_user_phone_mappings_primary;
DROP INDEX IF EXISTS idx_user_phone_mappings_phone_number;
DROP INDEX IF EXISTS idx_user_phone_mappings_user_id;

DROP INDEX IF EXISTS idx_sms_usage_logs_created_at;
DROP INDEX IF EXISTS idx_sms_usage_logs_phone_number;
DROP INDEX IF EXISTS idx_sms_usage_logs_user_id;

DROP INDEX IF EXISTS idx_sms_router_configs_key;

-- Drop tables (in reverse order due to foreign key constraints)
DROP TABLE IF EXISTS user_phone_mappings;
DROP TABLE IF EXISTS sms_usage_logs;
DROP TABLE IF EXISTS sms_router_configs;

-- Note: The relationships in the User model will be automatically handled
-- when the tables are dropped, so no additional cleanup is needed
