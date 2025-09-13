-- Migration: 006_interactive_sms_onboarding
-- Description: Add SMS onboarding session tracking for interactive onboarding flow
-- Created: 2024-01-XX
-- Author: AI Assistant

-- Create SMS onboarding sessions table
CREATE TABLE sms_onboarding_sessions (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    current_step VARCHAR(50) NOT NULL,
    collected_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
);

-- Create indexes for performance
CREATE INDEX idx_sms_onboarding_phone ON sms_onboarding_sessions(phone_number);
CREATE INDEX idx_sms_onboarding_expires ON sms_onboarding_sessions(expires_at);
CREATE INDEX idx_sms_onboarding_step ON sms_onboarding_sessions(current_step);

-- Create cleanup function for expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_onboarding_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sms_onboarding_sessions
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Add comment to table
COMMENT ON TABLE sms_onboarding_sessions IS 'Temporary storage for interactive SMS onboarding conversation state';
COMMENT ON COLUMN sms_onboarding_sessions.phone_number IS 'User phone number for session identification';
COMMENT ON COLUMN sms_onboarding_sessions.current_step IS 'Current step in onboarding flow (welcome, feature_overview, etc.)';
COMMENT ON COLUMN sms_onboarding_sessions.collected_data IS 'JSON data collected during onboarding (signup links, etc.)';
COMMENT ON COLUMN sms_onboarding_sessions.expires_at IS 'Session expiration timestamp (default 1 hour)';
