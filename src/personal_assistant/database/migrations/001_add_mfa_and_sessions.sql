-- Migration: Add MFA and Session Management Tables
-- Version: 001
-- Description: Creates tables for Multi-Factor Authentication and session management
-- Date: December 2024

-- Create MFA configuration table
CREATE TABLE IF NOT EXISTS mfa_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    totp_secret VARCHAR(255),
    totp_enabled BOOLEAN DEFAULT FALSE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    phone_number VARCHAR(20),
    backup_codes JSONB,
    trusted_devices JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_mfa_configurations_user_id ON mfa_configurations(user_id);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_mfa_configurations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_mfa_configurations_updated_at
    BEFORE UPDATE ON mfa_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_mfa_configurations_updated_at();

-- Create user sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Create security events table
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    severity VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for security monitoring
CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_event_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);

-- Add comments for documentation
COMMENT ON TABLE mfa_configurations IS 'Multi-Factor Authentication configuration for users';
COMMENT ON TABLE user_sessions IS 'User session tracking for security and management';
COMMENT ON TABLE security_events IS 'Security event logging for audit and monitoring';

COMMENT ON COLUMN mfa_configurations.totp_secret IS 'TOTP secret key (should be encrypted in production)';
COMMENT ON COLUMN mfa_configurations.backup_codes IS 'JSON array of backup codes for account recovery';
COMMENT ON COLUMN mfa_configurations.trusted_devices IS 'JSON array of trusted device information';

COMMENT ON COLUMN user_sessions.device_info IS 'JSON object containing browser, OS, and device information';
COMMENT ON COLUMN user_sessions.ip_address IS 'IP address of the session (IPv4 or IPv6)';
COMMENT ON COLUMN user_sessions.session_id IS 'Cryptographically secure session identifier';

COMMENT ON COLUMN security_events.event_type IS 'Type of security event (login, logout, mfa_setup, etc.)';
COMMENT ON COLUMN security_events.event_data IS 'Additional event context and metadata';
COMMENT ON COLUMN security_events.severity IS 'Event severity level (info, warning, error, critical)'; 