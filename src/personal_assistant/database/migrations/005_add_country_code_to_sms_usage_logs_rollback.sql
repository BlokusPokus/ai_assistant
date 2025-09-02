-- Rollback Migration: 005_add_country_code_to_sms_usage_logs
-- Description: Remove country_code field from SMS Usage Logs table
-- Dependencies: 005_add_country_code_to_sms_usage_logs

-- Drop the index first
DROP INDEX IF EXISTS idx_sms_usage_logs_country_code;

-- Remove the country_code column
ALTER TABLE sms_usage_logs 
DROP COLUMN IF EXISTS country_code;

-- Verify the change
SELECT column_name, data_type, column_default, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'sms_usage_logs' AND column_name = 'country_code';
