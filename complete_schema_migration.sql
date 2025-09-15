-- Complete Database Schema Migration
-- Generated from development database
-- DESCRIPTION: Creates all tables to match development schema

-- Table: access_audit_logs
CREATE TABLE access_audit_logs (id integer NOT NULL DEFAULT nextval('access_audit_logs_id_seq'::regclass), user_id integer NOT NULL, resource_type character varying(50) NOT NULL, resource_id integer, action character varying(50) NOT NULL, permission_granted boolean NOT NULL, roles_checked ARRAY, ip_address inet, user_agent text, created_at timestamp without time zone);

-- Table: ai_tasks
CREATE TABLE ai_tasks (ai_context text, notification_channels ARRAY, created_at timestamp without time zone, updated_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('ai_tasks_id_seq'::regclass), user_id integer NOT NULL, title character varying(255) NOT NULL, description text, task_type character varying(50) NOT NULL, schedule_type character varying(20) NOT NULL, schedule_config json, next_run_at timestamp without time zone, last_run_at timestamp without time zone, status character varying(20));

-- Table: auth_tokens
CREATE TABLE auth_tokens (last_used_at timestamp without time zone, user_id integer NOT NULL, token character varying NOT NULL, token_type character varying, expires_at timestamp without time zone NOT NULL, is_revoked boolean, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('auth_tokens_id_seq'::regclass));

-- Table: conversation_messages
CREATE TABLE conversation_messages (tool_name character varying(100), conversation_id character varying(255) NOT NULL, role character varying(50) NOT NULL, content text, message_type character varying(50), tool_success character varying(10), additional_data json, id integer NOT NULL DEFAULT nextval('conversation_messages_id_seq'::regclass), timestamp timestamp with time zone DEFAULT now());

-- Table: conversation_states
CREATE TABLE conversation_states (updated_at timestamp with time zone DEFAULT now(), conversation_id character varying(255) NOT NULL, user_id integer NOT NULL, user_input text, focus_areas json, step_count integer, last_tool_result json, id integer NOT NULL DEFAULT nextval('conversation_states_id_seq'::regclass), created_at timestamp with time zone DEFAULT now());

-- Table: event_creation_logs
CREATE TABLE event_creation_logs (parsed_details json, created_events integer, errors text, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('event_creation_logs_id_seq'::regclass), user_id integer, user_input text);

-- Table: event_processing_log
CREATE TABLE event_processing_log (agent_response text, error_message text, event_id integer, id integer NOT NULL DEFAULT nextval('event_processing_log_id_seq'::regclass), processed_at timestamp without time zone, processing_status character varying);

-- Table: events
CREATE TABLE events (recurrence_instance_number integer, id integer NOT NULL DEFAULT nextval('events_id_seq'::regclass), title character varying, user_id integer, description character varying, start_time timestamp without time zone, end_time timestamp without time zone, source character varying, external_id character varying, handled_at timestamp without time zone, processing_status character varying, agent_response text, last_checked timestamp without time zone, recurrence_pattern_id integer, is_recurring boolean, parent_event_id integer);

-- Table: expense_categories
CREATE TABLE expense_categories (id integer NOT NULL DEFAULT nextval('expense_categories_id_seq'::regclass), name character varying NOT NULL);

-- Table: expenses
CREATE TABLE expenses (id integer NOT NULL DEFAULT nextval('expenses_id_seq'::regclass), user_id integer, amount numeric, category_id integer, description character varying, created_at timestamp without time zone);

-- Table: grocery_analysis
CREATE TABLE grocery_analysis (user_id integer, analysis json, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('grocery_analysis_id_seq'::regclass));

-- Table: grocery_deals
CREATE TABLE grocery_deals (source character varying, title character varying, price character varying, image_url character varying, flyer_date date, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('grocery_deals_id_seq'::regclass));

-- Table: grocery_items
CREATE TABLE grocery_items (user_id integer, quantity character varying, added_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('grocery_items_id_seq'::regclass), name character varying);

-- Table: ltm_contexts
CREATE TABLE ltm_contexts (id integer NOT NULL DEFAULT nextval('ltm_contexts_id_seq'::regclass), confidence double precision, context_value text, context_key character varying(100) NOT NULL, context_type character varying(50) NOT NULL, memory_id integer NOT NULL, created_at timestamp without time zone);

-- Table: ltm_memories
CREATE TABLE ltm_memories (is_archived boolean, parent_memory_id integer, created_at timestamp without time zone, last_accessed timestamp without time zone, last_modified timestamp without time zone, access_count integer, last_access_context text, related_memory_ids json, content text NOT NULL, tags json NOT NULL, user_id integer NOT NULL, memory_type character varying(50), category character varying(100), importance_score integer, confidence_score double precision, dynamic_importance double precision, context text, context_data json, source_type character varying(50), source_id character varying(100), created_by character varying(50), id integer NOT NULL DEFAULT nextval('ltm_memories_id_seq'::regclass), archive_reason text, memory_metadata json);

-- Table: ltm_memory_access
CREATE TABLE ltm_memory_access (id integer NOT NULL DEFAULT nextval('ltm_memory_access_id_seq'::regclass), memory_id integer NOT NULL, access_timestamp timestamp without time zone, access_context text, access_method character varying(50), user_query text, was_relevant boolean, relevance_score double precision);

-- Table: ltm_memory_relationships
CREATE TABLE ltm_memory_relationships (source_memory_id integer NOT NULL, target_memory_id integer NOT NULL, strength double precision, relationship_type character varying(50) NOT NULL, description text, created_at timestamp without time zone, last_accessed timestamp without time zone, id integer NOT NULL DEFAULT nextval('ltm_memory_relationships_id_seq'::regclass));

-- Table: ltm_memory_tags
CREATE TABLE ltm_memory_tags (last_used timestamp without time zone, tag_name character varying(100) NOT NULL, memory_id integer NOT NULL, tag_confidence double precision, usage_count integer, first_used timestamp without time zone, tag_category character varying(50), id integer NOT NULL DEFAULT nextval('ltm_memory_tags_id_seq'::regclass), tag_importance double precision);

-- Table: memory_context_items
CREATE TABLE memory_context_items (preference_type character varying(100), additional_data json, id integer NOT NULL DEFAULT nextval('memory_context_items_id_seq'::regclass), source character varying(50) NOT NULL, timestamp timestamp with time zone DEFAULT now(), original_role character varying(50), context_type character varying(50), relevance_score double precision, conversation_id character varying(255) NOT NULL, content text, focus_area character varying(100));

-- Table: mfa_configurations
CREATE TABLE mfa_configurations (phone_number character varying(20), sms_enabled boolean, totp_secret character varying(255), totp_enabled boolean, user_id integer NOT NULL, id integer NOT NULL DEFAULT nextval('mfa_configurations_id_seq'::regclass), updated_at timestamp without time zone, created_at timestamp without time zone, trusted_devices json, backup_codes json);

-- Table: migration_history
CREATE TABLE migration_history (applied_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP, id integer NOT NULL DEFAULT nextval('migration_history_id_seq'::regclass), error_message text, migration_name character varying(255) NOT NULL, version character varying(50) NOT NULL, checksum character varying(64) NOT NULL, rollback_sql text, rollback_checksum character varying(64), execution_time_ms integer, status character varying(20) DEFAULT 'applied'::character varying, applied_by character varying(100) DEFAULT 'system'::character varying);

-- Table: note_sync_log
CREATE TABLE note_sync_log (sync_status character varying, synced_at timestamp without time zone, note_id integer, user_id integer, id integer NOT NULL DEFAULT nextval('note_sync_log_id_seq'::regclass));

-- Table: notes
CREATE TABLE notes (last_synced timestamp without time zone, id integer NOT NULL DEFAULT nextval('notes_id_seq'::regclass), created_at timestamp without time zone, content character varying, title character varying, user_id integer);

-- Table: oauth_audit_logs
CREATE TABLE oauth_audit_logs (integration_id integer, error_message text, success boolean NOT NULL DEFAULT false, scopes ARRAY, provider character varying(50) NOT NULL, user_id integer NOT NULL, created_at timestamp without time zone DEFAULT now(), id integer NOT NULL DEFAULT nextval('oauth_audit_logs_id_seq'::regclass), user_agent text, ip_address character varying(45), details jsonb, status character varying(20) NOT NULL, action character varying(50) NOT NULL, duration_ms integer, action_metadata jsonb);

-- Table: oauth_consents
CREATE TABLE oauth_consents (integration_id integer NOT NULL, scopes ARRAY NOT NULL, expires_at timestamp without time zone, ip_address character varying(45), user_agent text, revoked_at timestamp without time zone, revoked_reason text, id integer NOT NULL DEFAULT nextval('oauth_consents_id_seq'::regclass), granted_at timestamp without time zone DEFAULT now(), consent_version character varying(10) DEFAULT '1.0'::character varying, is_revoked boolean DEFAULT false);

-- Table: oauth_integrations
CREATE TABLE oauth_integrations (error_count integer DEFAULT 0, updated_at timestamp without time zone DEFAULT now(), provider character varying(50) NOT NULL, provider_user_id character varying(255), scopes ARRAY, provider_metadata jsonb, last_sync_at timestamp without time zone, error_message text, id integer NOT NULL DEFAULT nextval('oauth_integrations_id_seq'::regclass), status character varying(20) DEFAULT 'pending'::character varying, user_id integer NOT NULL, created_at timestamp without time zone DEFAULT now());

-- Table: oauth_states
CREATE TABLE oauth_states (created_at timestamp without time zone DEFAULT now(), state_token character varying(255) NOT NULL, user_id integer NOT NULL, provider character varying(50) NOT NULL, scopes ARRAY, redirect_uri text, expires_at timestamp without time zone NOT NULL, used_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('oauth_states_id_seq'::regclass), is_used boolean DEFAULT false);

-- Table: oauth_tokens
CREATE TABLE oauth_tokens (refresh_token text, expires_at timestamp without time zone NOT NULL, token_type character varying(20) DEFAULT 'Bearer'::character varying, scope text, last_used_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('oauth_tokens_id_seq'::regclass), usage_count integer DEFAULT 0, updated_at timestamp without time zone DEFAULT now(), created_at timestamp without time zone DEFAULT now(), integration_id integer NOT NULL, access_token text NOT NULL);

-- Table: permissions
CREATE TABLE permissions (resource_type character varying(50) NOT NULL, name character varying(100) NOT NULL, id integer NOT NULL DEFAULT nextval('permissions_id_seq'::regclass), created_at timestamp without time zone, description text, action character varying(50) NOT NULL);

-- Table: recurrence_patterns
CREATE TABLE recurrence_patterns (max_occurrences integer, frequency character varying NOT NULL, interval integer, weekdays ARRAY, end_date timestamp without time zone, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('recurrence_patterns_id_seq'::regclass));

-- Table: reminders
CREATE TABLE reminders (user_id integer, message character varying NOT NULL, sent boolean, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('reminders_id_seq'::regclass), remind_at timestamp without time zone NOT NULL);

-- Table: role_permissions
CREATE TABLE role_permissions (created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('role_permissions_id_seq'::regclass), role_id integer NOT NULL, permission_id integer NOT NULL);

-- Table: roles
CREATE TABLE roles (parent_role_id integer, created_at timestamp without time zone, updated_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('roles_id_seq'::regclass), name character varying(50) NOT NULL, description text);

-- Table: security_events
CREATE TABLE security_events (id integer NOT NULL DEFAULT nextval('security_events_id_seq'::regclass), user_id integer, event_type character varying(100) NOT NULL, event_data json, severity character varying(20), ip_address character varying(45), user_agent text, created_at timestamp without time zone);

-- Table: sms_router_configs
CREATE TABLE sms_router_configs (config_key character varying(100) NOT NULL, config_value text NOT NULL, description text, is_active boolean, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('sms_router_configs_id_seq'::regclass), updated_at timestamp without time zone);

-- Table: sms_usage_logs
CREATE TABLE sms_usage_logs (max_retries integer, id integer NOT NULL DEFAULT nextval('sms_usage_logs_id_seq'::regclass), final_status character varying(20), twilio_message_sid character varying(50), next_retry_at timestamp without time zone, retry_count integer, created_at timestamp without time zone, sms_metadata json, country_code character varying(10), error_message text, processing_time_ms integer, success boolean, message_content text, message_length integer NOT NULL, message_direction character varying(10) NOT NULL, phone_number character varying(20) NOT NULL, user_id integer NOT NULL);

-- Table: task_results
CREATE TABLE task_results (id integer NOT NULL DEFAULT nextval('task_results_id_seq'::regclass), task_id integer, result json, completed_at timestamp without time zone);

-- Table: tasks
CREATE TABLE tasks (scheduled_at timestamp without time zone, created_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('tasks_id_seq'::regclass), user_id integer, task_name character varying, status character varying);

-- Table: todos
CREATE TABLE todos (user_id integer NOT NULL, title character varying(255) NOT NULL, description text, due_date timestamp without time zone, done_date timestamp without time zone, priority character varying(20), category character varying(50), status character varying(20), last_missed_at timestamp without time zone, missed_count integer NOT NULL, segmentation_suggestions jsonb, created_at timestamp without time zone, updated_at timestamp without time zone, id integer NOT NULL DEFAULT nextval('todos_id_seq'::regclass), completion_patterns jsonb, segmentation_triggered_at timestamp without time zone, parent_task_id integer, is_segmented boolean NOT NULL, user_insights jsonb);

-- Table: user_phone_mappings
CREATE TABLE user_phone_mappings (id integer NOT NULL DEFAULT nextval('user_phone_mappings_id_seq'::regclass), user_id integer NOT NULL, phone_number character varying(20) NOT NULL, is_primary boolean, is_verified boolean, verification_method character varying(50), created_at timestamp without time zone, updated_at timestamp without time zone);

-- Table: user_roles
CREATE TABLE user_roles (granted_by integer, granted_at timestamp without time zone, expires_at timestamp without time zone, user_id integer NOT NULL, role_id integer NOT NULL, is_primary boolean, id integer NOT NULL DEFAULT nextval('user_roles_id_seq'::regclass));

-- Table: user_sessions
CREATE TABLE user_sessions (is_active boolean, expires_at timestamp without time zone NOT NULL, last_accessed timestamp without time zone, created_at timestamp without time zone, user_agent text, ip_address character varying(45), device_info json, session_id character varying(255) NOT NULL, user_id integer NOT NULL, id integer NOT NULL DEFAULT nextval('user_sessions_id_seq'::regclass));

-- Table: user_settings
CREATE TABLE user_settings (is_public boolean, user_id integer NOT NULL, id integer NOT NULL DEFAULT nextval('user_settings_id_seq'::regclass), updated_at timestamp without time zone, created_at timestamp without time zone, description text, category character varying(100), validation_rules json, setting_type character varying(50) NOT NULL, value text, key character varying(255) NOT NULL);

-- Table: users
CREATE TABLE users (phone_number character varying(20), password_reset_expires timestamp without time zone, last_login timestamp without time zone, failed_login_attempts integer, locked_until timestamp without time zone, created_at timestamp without time zone, updated_at timestamp without time zone, default_role_id integer, role_assigned_at timestamp without time zone, role_assigned_by integer, id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass), password_reset_token character varying, verification_token character varying, is_verified boolean, is_active boolean, hashed_password character varying NOT NULL, full_name character varying, email character varying NOT NULL);

