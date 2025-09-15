-- Fix OAuth Database Schema Issues
-- This script adds missing columns to OAuth tables to match the application models

-- Fix oauth_states table
-- Add missing columns: state_token, scopes, is_used, used_at
ALTER TABLE oauth_states 
ADD COLUMN IF NOT EXISTS state_token VARCHAR(255),
ADD COLUMN IF NOT EXISTS scopes TEXT[],
ADD COLUMN IF NOT EXISTS is_used BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS used_at TIMESTAMP WITHOUT TIME ZONE;

-- Create unique index on state_token if it doesn't exist
CREATE UNIQUE INDEX IF NOT EXISTS oauth_states_state_token_key ON oauth_states(state_token);

-- Fix oauth_consents table  
-- Add missing columns: granted_at, ip_address, user_agent, consent_version, is_revoked, revoked_at, revoked_reason
ALTER TABLE oauth_consents
ADD COLUMN IF NOT EXISTS granted_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45),
ADD COLUMN IF NOT EXISTS user_agent TEXT,
ADD COLUMN IF NOT EXISTS consent_version VARCHAR(10) DEFAULT '1.0',
ADD COLUMN IF NOT EXISTS is_revoked BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMP WITHOUT TIME ZONE,
ADD COLUMN IF NOT EXISTS revoked_reason VARCHAR(100);

-- Fix oauth_audit_logs table
-- Add missing columns: action_metadata, details, status, duration_ms
ALTER TABLE oauth_audit_logs
ADD COLUMN IF NOT EXISTS action_metadata JSONB,
ADD COLUMN IF NOT EXISTS details JSONB,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS duration_ms INTEGER;

-- Fix oauth_tokens table
-- Add missing columns: token_type default, scope (if not exists), last_used_at, usage_count
ALTER TABLE oauth_tokens
ALTER COLUMN token_type SET DEFAULT 'Bearer';

-- Update existing records to have proper defaults
UPDATE oauth_states SET is_used = FALSE WHERE is_used IS NULL;
UPDATE oauth_consents SET granted_at = NOW() WHERE granted_at IS NULL;
UPDATE oauth_consents SET consent_version = '1.0' WHERE consent_version IS NULL;
UPDATE oauth_consents SET is_revoked = FALSE WHERE is_revoked IS NULL;
UPDATE oauth_audit_logs SET status = 'pending' WHERE status IS NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_oauth_states_expires_at ON oauth_states(expires_at);
CREATE INDEX IF NOT EXISTS idx_oauth_states_is_used ON oauth_states(is_used);
CREATE INDEX IF NOT EXISTS idx_oauth_states_provider ON oauth_states(provider);
CREATE INDEX IF NOT EXISTS idx_oauth_states_user_id ON oauth_states(user_id);

CREATE INDEX IF NOT EXISTS idx_oauth_consents_integration_id ON oauth_consents(integration_id);
CREATE INDEX IF NOT EXISTS idx_oauth_consents_is_revoked ON oauth_consents(is_revoked);

CREATE INDEX IF NOT EXISTS idx_oauth_audit_logs_user_id ON oauth_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_audit_logs_provider ON oauth_audit_logs(provider);
CREATE INDEX IF NOT EXISTS idx_oauth_audit_logs_action ON oauth_audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_oauth_audit_logs_created_at ON oauth_audit_logs(created_at);

-- Verify the changes
SELECT 'oauth_states columns:' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'oauth_states' 
ORDER BY ordinal_position;

SELECT 'oauth_consents columns:' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'oauth_consents' 
ORDER BY ordinal_position;

SELECT 'oauth_audit_logs columns:' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'oauth_audit_logs' 
ORDER BY ordinal_position;

