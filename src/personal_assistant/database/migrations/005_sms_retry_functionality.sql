-- Migration: 005_sms_retry_functionality
-- Description: Add SMS retry functionality fields to existing tables
-- Dependencies: 004_create_sms_router_tables
-- Rollback: Available

-- Add retry fields to SMS Usage Logs table
ALTER TABLE sms_usage_logs
ADD COLUMN retry_count INTEGER DEFAULT 0,
ADD COLUMN max_retries INTEGER DEFAULT 3,
ADD COLUMN next_retry_at TIMESTAMP,
ADD COLUMN twilio_message_sid VARCHAR(50),
ADD COLUMN final_status VARCHAR(20) DEFAULT 'unknown';

-- Add constraint for final_status
ALTER TABLE sms_usage_logs
ADD CONSTRAINT chk_final_status CHECK (final_status IN ('unknown', 'sent', 'delivered', 'failed', 'undelivered'));

-- Create index for retry processing (only for failed messages with retry scheduled)
CREATE INDEX idx_sms_usage_logs_retry ON sms_usage_logs(success, next_retry_at)
WHERE success = false AND next_retry_at IS NOT NULL;

-- Create index for twilio_message_sid lookups
CREATE INDEX idx_sms_usage_logs_twilio_sid ON sms_usage_logs(twilio_message_sid);

-- Add comment to document the new fields
COMMENT ON COLUMN sms_usage_logs.retry_count IS 'Number of retry attempts made for this SMS';
COMMENT ON COLUMN sms_usage_logs.max_retries IS 'Maximum number of retry attempts allowed';
COMMENT ON COLUMN sms_usage_logs.next_retry_at IS 'Timestamp when next retry should be attempted';
COMMENT ON COLUMN sms_usage_logs.twilio_message_sid IS 'Twilio message SID for tracking delivery status';
COMMENT ON COLUMN sms_usage_logs.final_status IS 'Final delivery status: unknown, sent, delivered, failed, undelivered';
