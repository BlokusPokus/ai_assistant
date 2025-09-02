-- Migration: 004_create_sms_router_tables
-- Description: Create SMS Router Service database tables
-- Dependencies: 003_add_phone_number_to_users
-- Rollback: Available

-- Create SMS Router Configuration table
CREATE TABLE IF NOT EXISTS sms_router_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for config lookups
CREATE INDEX IF NOT EXISTS idx_sms_router_configs_key ON sms_router_configs(config_key);

-- Create SMS Usage Logs table
CREATE TABLE IF NOT EXISTS sms_usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    message_direction VARCHAR(10) NOT NULL CHECK (message_direction IN ('inbound', 'outbound')),
    message_length INTEGER NOT NULL,
    message_content TEXT,
    success BOOLEAN DEFAULT TRUE,
    processing_time_ms INTEGER,
    error_message TEXT,
    sms_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for usage logs
CREATE INDEX IF NOT EXISTS idx_sms_usage_logs_user_id ON sms_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_sms_usage_logs_phone_number ON sms_usage_logs(phone_number);
CREATE INDEX IF NOT EXISTS idx_sms_usage_logs_created_at ON sms_usage_logs(created_at);

-- Create User Phone Mappings table
CREATE TABLE IF NOT EXISTS user_phone_mappings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_method VARCHAR(50),
    verification_code VARCHAR(10),
    verification_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, phone_number)
);

-- Create indexes for phone mappings
CREATE INDEX IF NOT EXISTS idx_user_phone_mappings_user_id ON user_phone_mappings(user_id);
CREATE INDEX IF NOT EXISTS idx_user_phone_mappings_phone_number ON user_phone_mappings(phone_number);
CREATE INDEX IF NOT EXISTS idx_user_phone_mappings_primary ON user_phone_mappings(is_primary);

-- Insert default SMS Router configuration
INSERT INTO sms_router_configs (config_key, config_value, description) VALUES
('max_sms_length', '160', 'Maximum SMS message length'),
('max_concatenated_length', '1600', 'Maximum length for concatenated SMS'),
('spam_threshold', '0.7', 'Spam detection threshold (0.0-1.0)'),
('cache_ttl_seconds', '3600', 'Cache time-to-live in seconds'),
('rate_limit_per_minute', '10', 'Rate limit per phone number per minute'),
('enable_spam_detection', 'true', 'Enable spam detection'),
('enable_command_processing', 'true', 'Enable command processing'),
('default_response_timeout', '30', 'Default response timeout in seconds')
ON CONFLICT (config_key) DO NOTHING;

-- Add phone_mappings relationship to users table (if not exists)
-- This is handled by the User model relationship

-- Add sms_usage_logs relationship to users table (if not exists)
-- This is handled by the User model relationship
