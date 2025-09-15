-- Complete Database Schema Migration
-- Generated from development database
-- DESCRIPTION: Creates all tables to match development schema
-- VERSION: 000
-- DEPENDS: 
-- ROLLBACK: DROP SCHEMA public CASCADE; CREATE SCHEMA public;

-- Create all tables to match development database exactly
-- This migration creates the complete schema in one go

-- Table: access_audit_logs
CREATE TABLE access_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    action VARCHAR(50) NOT NULL,
    permission_granted BOOLEAN NOT NULL,
    roles_checked TEXT[],
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: ai_tasks
CREATE TABLE ai_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,
    schedule_type VARCHAR(20) NOT NULL,
    schedule_config JSON,
    next_run_at TIMESTAMP WITHOUT TIME ZONE,
    last_run_at TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(20),
    ai_context TEXT,
    notification_channels TEXT[],
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: auth_tokens
CREATE TABLE auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR NOT NULL,
    token_type VARCHAR,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    is_revoked BOOLEAN,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    last_used_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: conversation_messages
CREATE TABLE conversation_messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT,
    message_type VARCHAR(50),
    tool_name VARCHAR(100),
    tool_success VARCHAR(10),
    additional_data JSON,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: conversation_states
CREATE TABLE conversation_states (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    user_input TEXT,
    focus_areas JSON,
    step_count INTEGER,
    last_tool_result JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: event_creation_logs
CREATE TABLE event_creation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    user_input TEXT,
    parsed_details JSON,
    created_events INTEGER,
    errors TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: event_processing_log
CREATE TABLE event_processing_log (
    id SERIAL PRIMARY KEY,
    event_id INTEGER,
    processing_status VARCHAR,
    agent_response TEXT,
    error_message TEXT,
    processed_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: events
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    user_id INTEGER,
    description VARCHAR,
    start_time TIMESTAMP WITHOUT TIME ZONE,
    end_time TIMESTAMP WITHOUT TIME ZONE,
    source VARCHAR,
    external_id VARCHAR,
    handled_at TIMESTAMP WITHOUT TIME ZONE,
    processing_status VARCHAR,
    agent_response TEXT,
    last_checked TIMESTAMP WITHOUT TIME ZONE,
    recurrence_pattern_id INTEGER,
    is_recurring BOOLEAN,
    parent_event_id INTEGER,
    recurrence_instance_number INTEGER
);

-- Table: expense_categories
CREATE TABLE expense_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

-- Table: expenses
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    amount NUMERIC,
    category_id INTEGER,
    description VARCHAR,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: grocery_analysis
CREATE TABLE grocery_analysis (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    analysis JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: grocery_deals
CREATE TABLE grocery_deals (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    price VARCHAR,
    image_url VARCHAR,
    source VARCHAR,
    flyer_date DATE,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: grocery_items
CREATE TABLE grocery_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    user_id INTEGER,
    quantity VARCHAR,
    added_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: ltm_contexts
CREATE TABLE ltm_contexts (
    id SERIAL PRIMARY KEY,
    memory_id INTEGER NOT NULL,
    context_key VARCHAR(100) NOT NULL,
    context_type VARCHAR(50) NOT NULL,
    context_value TEXT,
    confidence DOUBLE PRECISION,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: ltm_memories
CREATE TABLE ltm_memories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    tags JSON NOT NULL,
    memory_type VARCHAR(50),
    category VARCHAR(100),
    importance_score INTEGER,
    confidence_score DOUBLE PRECISION,
    dynamic_importance DOUBLE PRECISION,
    context TEXT,
    context_data JSON,
    source_type VARCHAR(50),
    source_id VARCHAR(100),
    created_by VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE,
    last_modified TIMESTAMP WITHOUT TIME ZONE,
    last_accessed TIMESTAMP WITHOUT TIME ZONE,
    access_count INTEGER,
    last_access_context TEXT,
    related_memory_ids JSON,
    parent_memory_id INTEGER,
    is_archived BOOLEAN,
    archive_reason TEXT,
    memory_metadata JSON
);

-- Table: ltm_memory_access
CREATE TABLE ltm_memory_access (
    id SERIAL PRIMARY KEY,
    memory_id INTEGER NOT NULL,
    access_type VARCHAR(50) NOT NULL,
    access_context TEXT,
    accessed_at TIMESTAMP WITHOUT TIME ZONE,
    user_id INTEGER,
    session_id VARCHAR(255)
);

-- Table: ltm_memory_relationships
CREATE TABLE ltm_memory_relationships (
    id SERIAL PRIMARY KEY,
    source_memory_id INTEGER NOT NULL,
    target_memory_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    strength DOUBLE PRECISION,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: ltm_memory_tags
CREATE TABLE ltm_memory_tags (
    id SERIAL PRIMARY KEY,
    memory_id INTEGER NOT NULL,
    tag_name VARCHAR(100) NOT NULL,
    tag_value VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: memory_context_items
CREATE TABLE memory_context_items (
    id SERIAL PRIMARY KEY,
    memory_id INTEGER NOT NULL,
    context_key VARCHAR(100) NOT NULL,
    context_value TEXT,
    context_type VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: mfa_configurations
CREATE TABLE mfa_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    mfa_type VARCHAR(50) NOT NULL,
    secret_key VARCHAR(255),
    backup_codes TEXT[],
    is_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: note_sync_log
CREATE TABLE note_sync_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    sync_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    sync_data JSON,
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: notes
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: oauth_audit_logs
CREATE TABLE oauth_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    provider VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: oauth_consents
CREATE TABLE oauth_consents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,
    consent_given BOOLEAN NOT NULL,
    scopes TEXT[],
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: oauth_integrations
CREATE TABLE oauth_integrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,
    integration_status VARCHAR(20) NOT NULL,
    last_sync_at TIMESTAMP WITHOUT TIME ZONE,
    sync_frequency INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: oauth_states
CREATE TABLE oauth_states (
    id SERIAL PRIMARY KEY,
    state_value VARCHAR(255) NOT NULL UNIQUE,
    user_id INTEGER,
    provider VARCHAR(50) NOT NULL,
    redirect_uri TEXT,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: oauth_tokens
CREATE TABLE oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type VARCHAR(50),
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    scopes TEXT[],
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: permissions
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    resource_type VARCHAR(50),
    action VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: recurrence_patterns
CREATE TABLE recurrence_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_config JSON NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: reminders
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reminder_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: role_permissions
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: security_events
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    event_type VARCHAR(50) NOT NULL,
    event_data JSON,
    ip_address INET,
    user_agent TEXT,
    severity VARCHAR(20),
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: sms_router_configs
CREATE TABLE sms_router_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    routing_rules JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: sms_usage_logs
CREATE TABLE sms_usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    phone_number VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    message_sid VARCHAR(100),
    twilio_status VARCHAR(50),
    final_status VARCHAR(50),
    error_code VARCHAR(20),
    error_message TEXT,
    cost_cents INTEGER,
    country_code VARCHAR(5),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITHOUT TIME ZONE,
    sms_metadata JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: task_results
CREATE TABLE task_results (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    result_data JSON,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL,
    priority INTEGER DEFAULT 0,
    due_date TIMESTAMP WITHOUT TIME ZONE,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: todos
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0,
    due_date TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: user_phone_mappings
CREATE TABLE user_phone_mappings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(10),
    verification_expires_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: user_roles
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    assigned_by INTEGER
);

-- Table: user_sessions
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    last_accessed TIMESTAMP WITHOUT TIME ZONE
);

-- Table: user_settings
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires_at TIMESTAMP WITHOUT TIME ZONE,
    last_login_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_access_audit_logs_user_id ON access_audit_logs(user_id);
CREATE INDEX idx_access_audit_logs_created_at ON access_audit_logs(created_at);
CREATE INDEX idx_ai_tasks_user_id ON ai_tasks(user_id);
CREATE INDEX idx_ai_tasks_status ON ai_tasks(status);
CREATE INDEX idx_ai_tasks_next_run_at ON ai_tasks(next_run_at);
CREATE INDEX idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX idx_auth_tokens_token ON auth_tokens(token);
CREATE INDEX idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_conversation_states_user_id ON conversation_states(user_id);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_ltm_memories_user_id ON ltm_memories(user_id);
CREATE INDEX idx_ltm_memories_memory_type ON ltm_memories(memory_type);
CREATE INDEX idx_ltm_memories_tags ON ltm_memories USING GIN(tags);
CREATE INDEX idx_oauth_tokens_user_id ON oauth_tokens(user_id);
CREATE INDEX idx_oauth_tokens_provider ON oauth_tokens(provider);
CREATE INDEX idx_sms_usage_logs_user_id ON sms_usage_logs(user_id);
CREATE INDEX idx_sms_usage_logs_phone_number ON sms_usage_logs(phone_number);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_completed ON todos(completed);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);