-- Migration: 005_add_country_code_to_sms_usage_logs
-- Description: Add country_code field to SMS Usage Logs table for pricing calculations
-- Dependencies: 004_create_sms_router_tables
-- Rollback: Available

-- Add country_code column to sms_usage_logs table
ALTER TABLE sms_usage_logs 
ADD COLUMN IF NOT EXISTS country_code VARCHAR(10) DEFAULT 'US';

-- Add comment to explain the field
COMMENT ON COLUMN sms_usage_logs.country_code IS 'Country code for SMS pricing calculations (default: US)';

-- Update existing records to have US as default country code
UPDATE sms_usage_logs 
SET country_code = 'US' 
WHERE country_code IS NULL;

-- Create index for country code lookups (useful for cost calculations)
CREATE INDEX IF NOT EXISTS idx_sms_usage_logs_country_code ON sms_usage_logs(country_code);

-- Verify the change
SELECT column_name, data_type, column_default, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'sms_usage_logs' AND column_name = 'country_code';
