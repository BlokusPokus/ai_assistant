# 🔐 Database Schema Inspector

🔍 Inspecting database schema...
📋 Found 31 tables in database
============================================================

## 📊 Table: access_audit_logs

• id: integer NOT NULL DEFAULT nextval('access_audit_logs_id_seq'::regclass)
• user_id: integer NULL
• resource_type: character varying(50) NOT NULL
• resource_id: integer NULL
• action: character varying(50) NOT NULL
• permission_granted: boolean NOT NULL
• roles_checked: ARRAY NULL
• ip_address: inet NULL
• user_agent: text NULL
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
❌ Error inspecting database: (sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.AmbiguousColumnError'>: column reference "constraint_name" is ambiguous
[SQL:
SELECT
constraint_name,
constraint_type,
check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public' AND tc.table_name = $1
ORDER BY tc.constraint_type, tc.constraint_name
]
[parameters: ('access_audit_logs',)]
(Background on this error at: https://sqlalche.me/e/20/f405)
💥 Failed to inspect database schema
(venv_personal_assistant) (base) ianleblanc@MacBook-Air-de-Ian personal_assistant % source venv_personal_assistant/bin/activate && python scripts/inspect_database_schema.py source venv_personal_assistant/bin/activate && python scripts/inspect_database_schema.py
🔧 Logging level overridden by PA_LOG_LEVEL: WARNING
2025-08-25 07:43:48 - personal_assistant.tools.internet.internet_tool - INFO - Using ddgs library
2025-08-25 07:43:49 - personal_assistant.tools.youtube.youtube_tool - INFO - YouTube Transcript API library imported successfully
🔐 Database Schema Inspector
============================================================
🔍 Inspecting database schema...
📋 Found 31 tables in database
============================================================

## 📊 Table: access_audit_logs

• id: integer NOT NULL DEFAULT nextval('access_audit_logs_id_seq'::regclass)
• user_id: integer NULL
• resource_type: character varying(50) NOT NULL
• resource_id: integer NULL
• action: character varying(50) NOT NULL
• permission_granted: boolean NOT NULL
• roles_checked: ARRAY NULL
• ip_address: inet NULL
• user_agent: text NULL
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_25922_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25922_3_not_null - resource_type IS NOT NULL
🔒 CHECK: 2200_25922_5_not_null - action IS NOT NULL
🔒 CHECK: 2200_25922_6_not_null - permission_granted IS NOT NULL
🔗 FOREIGN KEY: access_audit_logs_user_id_fkey
🔑 PRIMARY KEY: access_audit_logs_pkey
📍 INDEX: access_audit_logs_pkey
📍 INDEX: idx_access_audit_logs_action
📍 INDEX: idx_access_audit_logs_created_at
📍 INDEX: idx_access_audit_logs_resource_type
📍 INDEX: idx_access_audit_logs_user_id
📊 Total: 10 columns, 6 constraints, 5 indexes

## 📊 Table: agent_logs

• id: integer NOT NULL DEFAULT nextval('agent_logs_id_seq'::regclass)
• user_id: integer NULL
• user_input: text NULL
• agent_response: text NULL
• tool_called: text NULL
• tool_output: text NULL
• memory_used: jsonb NULL
• timestamp: timestamp with time zone NULL DEFAULT now()
🔒 CHECK: 2200_16727_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: agent_logs_user_id_fkey
🔑 PRIMARY KEY: agent_logs_pkey
📍 INDEX: agent_logs_pkey
📊 Total: 8 columns, 3 constraints, 1 indexes

## 📊 Table: ai_tasks

• id: integer NOT NULL DEFAULT nextval('ai_tasks_id_seq'::regclass)
• user_id: integer NOT NULL
• title: character varying(255) NOT NULL
• description: text NULL
• task_type: character varying(50) NOT NULL
• schedule_type: character varying(20) NOT NULL
• schedule_config: jsonb NULL
• next_run_at: timestamp without time zone NULL
• last_run_at: timestamp without time zone NULL
• status: character varying(20) NULL DEFAULT 'active'::character varying
• ai_context: text NULL
• notification_channels: ARRAY NULL DEFAULT '{}'::text[]
• created_at: timestamp without time zone NULL DEFAULT now()
• updated_at: timestamp without time zone NULL DEFAULT now()
🔒 CHECK: 2200_24776_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_24776_2_not_null - user_id IS NOT NULL
🔒 CHECK: 2200_24776_3_not_null - title IS NOT NULL
🔒 CHECK: 2200_24776_5_not_null - task_type IS NOT NULL
🔒 CHECK: 2200_24776_6_not_null - schedule_type IS NOT NULL
🔒 CHECK: ai_tasks_schedule_type_check - (((schedule_type)::text = ANY ((ARRAY['once'::character varying, 'daily'::character varying, 'weekly'::character varying, 'monthly'::character varying, 'custom'::character varying])::text[])))
🔒 CHECK: ai_tasks_status_check - (((status)::text = ANY ((ARRAY['active'::character varying, 'paused'::character varying, 'completed'::character varying, 'failed'::character varying, 'processing'::character varying])::text[])))
🔒 CHECK: ai_tasks_task_type_check - (((task_type)::text = ANY ((ARRAY['reminder'::character varying, 'automated_task'::character varying, 'periodic_task'::character varying])::text[])))
🔗 FOREIGN KEY: ai_tasks_user_id_fkey
🔑 PRIMARY KEY: ai_tasks_pkey
📍 INDEX: ai_tasks_pkey
📍 INDEX: idx_ai_tasks_due_tasks
📍 INDEX: idx_ai_tasks_next_run_at
📍 INDEX: idx_ai_tasks_schedule_type
📍 INDEX: idx_ai_tasks_status
📍 INDEX: idx_ai_tasks_task_type
📍 INDEX: idx_ai_tasks_user_id
📊 Total: 14 columns, 10 constraints, 7 indexes

## 📊 Table: auth_tokens

• id: integer NOT NULL DEFAULT nextval('auth_tokens_id_seq'::regclass)
• user_id: integer NOT NULL
• token: text NOT NULL
• token_type: character varying(50) NULL DEFAULT 'refresh'::character varying
• expires_at: timestamp without time zone NOT NULL
• is_revoked: boolean NULL DEFAULT false
• created_at: timestamp without time zone NULL DEFAULT now()
• last_used_at: timestamp without time zone NULL
🔒 CHECK: 2200_25754_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25754_2_not_null - user_id IS NOT NULL
🔒 CHECK: 2200_25754_3_not_null - token IS NOT NULL
🔒 CHECK: 2200_25754_5_not_null - expires_at IS NOT NULL
🔗 FOREIGN KEY: auth_tokens_user_id_fkey
🔑 PRIMARY KEY: auth_tokens_pkey
✨ UNIQUE: auth_tokens_token_key
✨ UNIQUE: uq_auth_tokens_token
📍 INDEX: auth_tokens_pkey
📍 INDEX: auth_tokens_token_key
📍 INDEX: idx_auth_tokens_expires_at
📍 INDEX: idx_auth_tokens_token
📍 INDEX: idx_auth_tokens_user_id
📍 INDEX: uq_auth_tokens_token
📊 Total: 8 columns, 8 constraints, 6 indexes

## 📊 Table: event_creation_logs

• id: integer NOT NULL DEFAULT nextval('event_creation_logs_id_seq'::regclass)
• user_id: integer NULL
• user_input: text NULL
• parsed_details: jsonb NULL
• created_events: integer NULL DEFAULT 0
• errors: text NULL
• created_at: timestamp without time zone NULL DEFAULT now()
🔒 CHECK: 2200_24730_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: event_creation_logs_user_id_fkey
🔑 PRIMARY KEY: event_creation_logs_pkey
📍 INDEX: event_creation_logs_pkey
📍 INDEX: idx_event_creation_logs_created_at
📍 INDEX: idx_event_creation_logs_user_id
📊 Total: 7 columns, 3 constraints, 3 indexes

## 📊 Table: ltm_contexts

• id: integer NOT NULL DEFAULT nextval('ltm_contexts_id_seq'::regclass)
• memory_id: integer NOT NULL
• context_type: character varying(50) NOT NULL
• context_key: character varying(100) NOT NULL
• context_value: text NULL
• confidence: double precision NULL DEFAULT 1.0
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_25634_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25634_2_not_null - memory_id IS NOT NULL
🔒 CHECK: 2200_25634_3_not_null - context_type IS NOT NULL
🔒 CHECK: 2200_25634_4_not_null - context_key IS NOT NULL
🔗 FOREIGN KEY: ltm_contexts_memory_id_fkey
🔑 PRIMARY KEY: ltm_contexts_pkey
📍 INDEX: idx_ltm_contexts_memory_id
📍 INDEX: idx_ltm_contexts_type_key
📍 INDEX: ltm_contexts_pkey
📊 Total: 7 columns, 6 constraints, 3 indexes

## 📊 Table: ltm_memories

• id: integer NOT NULL DEFAULT nextval('ltm_memories_id_seq'::regclass)
• user_id: integer NOT NULL
• content: text NOT NULL
• tags: jsonb NOT NULL DEFAULT '[]'::jsonb
• importance_score: integer NULL DEFAULT 1
• context: text NULL
• created_at: timestamp without time zone NULL DEFAULT now()
• last_accessed: timestamp without time zone NULL DEFAULT now()
• memory_type: character varying(50) NULL
• category: character varying(100) NULL
• confidence_score: double precision NULL DEFAULT 1.0
• dynamic_importance: double precision NULL DEFAULT 1.0
• context_data: jsonb NULL
• source_type: character varying(50) NULL
• source_id: character varying(100) NULL
• created_by: character varying(50) NULL DEFAULT 'system'::character varying
• last_modified: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• access_count: integer NULL DEFAULT 0
• last_access_context: text NULL
• related_memory_ids: jsonb NULL
• parent_memory_id: integer NULL
• memory_metadata: jsonb NULL
• is_archived: boolean NULL DEFAULT false
• archive_reason: text NULL
🔒 CHECK: 2200_24962_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_24962_2_not_null - user_id IS NOT NULL
🔒 CHECK: 2200_24962_3_not_null - content IS NOT NULL
🔒 CHECK: 2200_24962_4_not_null - tags IS NOT NULL
🔒 CHECK: check_tags_is_array - ((jsonb_typeof(tags) = 'array'::text))
🔒 CHECK: check_tags_not_empty - ((jsonb_array_length(tags) > 0))
🔒 CHECK: ltm_memories_importance_score_check - (((importance_score >= 1) AND (importance_score <= 10)))
🔗 FOREIGN KEY: ltm_memories_parent_memory_id_fkey
🔗 FOREIGN KEY: ltm_memories_user_id_fkey
🔑 PRIMARY KEY: ltm_memories_pkey
📍 INDEX: idx_ltm_memories_category
📍 INDEX: idx_ltm_memories_content
📍 INDEX: idx_ltm_memories_created_at
📍 INDEX: idx_ltm_memories_dynamic_importance
📍 INDEX: idx_ltm_memories_importance
📍 INDEX: idx_ltm_memories_importance_score
📍 INDEX: idx_ltm_memories_last_accessed
📍 INDEX: idx_ltm_memories_memory_type
📍 INDEX: idx_ltm_memories_source_type
📍 INDEX: idx_ltm_memories_tags
📍 INDEX: idx_ltm_memories_tags_array
📍 INDEX: idx_ltm_memories_tags_gin
📍 INDEX: idx_ltm_memories_user_id
📍 INDEX: ltm_memories_pkey
📊 Total: 24 columns, 10 constraints, 14 indexes

## 📊 Table: ltm_memory_access

• id: integer NOT NULL DEFAULT nextval('ltm_memory_access_id_seq'::regclass)
• memory_id: integer NOT NULL
• access_timestamp: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• access_context: text NULL
• access_method: character varying(50) NULL
• user_query: text NULL
• was_relevant: boolean NULL
• relevance_score: double precision NULL
🔒 CHECK: 2200_25674_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25674_2_not_null - memory_id IS NOT NULL
🔗 FOREIGN KEY: ltm_memory_access_memory_id_fkey
🔑 PRIMARY KEY: ltm_memory_access_pkey
📍 INDEX: idx_ltm_access_memory_id
📍 INDEX: idx_ltm_access_timestamp
📍 INDEX: ltm_memory_access_pkey
📊 Total: 8 columns, 4 constraints, 3 indexes

## 📊 Table: ltm_memory_relationships

• id: integer NOT NULL DEFAULT nextval('ltm_memory_relationships_id_seq'::regclass)
• source_memory_id: integer NOT NULL
• target_memory_id: integer NOT NULL
• relationship_type: character varying(50) NOT NULL
• strength: double precision NULL DEFAULT 1.0
• description: text NULL
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• last_accessed: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_25650_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25650_2_not_null - source_memory_id IS NOT NULL
🔒 CHECK: 2200_25650_3_not_null - target_memory_id IS NOT NULL
🔒 CHECK: 2200_25650_4_not_null - relationship_type IS NOT NULL
🔗 FOREIGN KEY: ltm_memory_relationships_source_memory_id_fkey
🔗 FOREIGN KEY: ltm_memory_relationships_target_memory_id_fkey
🔑 PRIMARY KEY: ltm_memory_relationships_pkey
✨ UNIQUE: ltm_memory_relationships_source_memory_id_target_memory_id**key
📍 INDEX: idx_ltm_relationships_source
📍 INDEX: idx_ltm_relationships_target
📍 INDEX: ltm_memory_relationships_pkey
📍 INDEX: ltm_memory_relationships_source_memory_id_target_memory_id**key
📊 Total: 8 columns, 8 constraints, 4 indexes

## 📊 Table: ltm_memory_tags

• id: integer NOT NULL DEFAULT nextval('ltm_memory_tags_id_seq'::regclass)
• memory_id: integer NOT NULL
• tag_name: character varying(100) NOT NULL
• tag_category: character varying(50) NULL
• tag_importance: double precision NULL DEFAULT 1.0
• tag_confidence: double precision NULL DEFAULT 1.0
• usage_count: integer NULL DEFAULT 1
• first_used: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• last_used: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_25689_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25689_2_not_null - memory_id IS NOT NULL
🔒 CHECK: 2200_25689_3_not_null - tag_name IS NOT NULL
🔗 FOREIGN KEY: ltm_memory_tags_memory_id_fkey
🔑 PRIMARY KEY: ltm_memory_tags_pkey
✨ UNIQUE: ltm_memory_tags_memory_id_tag_name_key
📍 INDEX: idx_ltm_tags_category
📍 INDEX: idx_ltm_tags_memory_id
📍 INDEX: idx_ltm_tags_name
📍 INDEX: ltm_memory_tags_memory_id_tag_name_key
📍 INDEX: ltm_memory_tags_pkey
📊 Total: 9 columns, 6 constraints, 5 indexes

## 📊 Table: memory_chunks

• id: integer NOT NULL DEFAULT nextval('memory_chunks_id_seq'::regclass)
• user_id: integer NULL
• content: text NULL
• embedding: jsonb NULL
• created_at: timestamp with time zone NULL DEFAULT now()
🔒 CHECK: 2200_16963_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: memory_chunks_user_id_fkey
🔑 PRIMARY KEY: memory_chunks_pkey
📍 INDEX: idx_memory_chunks_created_at
📍 INDEX: idx_memory_chunks_id
📍 INDEX: idx_memory_chunks_user_created
📍 INDEX: idx_memory_chunks_user_id
📍 INDEX: memory_chunks_pkey
📊 Total: 5 columns, 3 constraints, 5 indexes

## 📊 Table: memory_metadata

• id: integer NOT NULL DEFAULT nextval('memory_metadata_id_seq'::regclass)
• chunk_id: integer NULL
• key: text NULL
• value: text NULL
🔒 CHECK: 2200_16979_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: memory_metadata_chunk_id_fkey
🔑 PRIMARY KEY: memory_metadata_pkey
📍 INDEX: idx_memory_metadata_chunk_id
📍 INDEX: idx_memory_metadata_key_value
📍 INDEX: idx_memory_metadata_key_value_chunk_id
📍 INDEX: memory_metadata_pkey
📊 Total: 4 columns, 3 constraints, 4 indexes

## 📊 Table: mfa_configurations

• id: integer NOT NULL DEFAULT nextval('mfa_configurations_id_seq'::regclass)
• user_id: integer NOT NULL
• totp_secret: character varying(255) NULL
• totp_enabled: boolean NULL DEFAULT false
• sms_enabled: boolean NULL DEFAULT false
• phone_number: character varying(20) NULL
• backup_codes: jsonb NULL
• trusted_devices: jsonb NULL
• created_at: timestamp without time zone NULL DEFAULT now()
• updated_at: timestamp without time zone NULL DEFAULT now()
🔒 CHECK: 2200_25781_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25781_2_not_null - user_id IS NOT NULL
🔗 FOREIGN KEY: mfa_configurations_user_id_fkey
🔑 PRIMARY KEY: mfa_configurations_pkey
✨ UNIQUE: mfa_configurations_user_id_key
📍 INDEX: idx_mfa_configurations_user_id
📍 INDEX: mfa_configurations_pkey
📍 INDEX: mfa_configurations_user_id_key
📊 Total: 10 columns, 5 constraints, 3 indexes

## 📊 Table: migration_history

• id: integer NOT NULL DEFAULT nextval('migration_history_id_seq'::regclass)
• migration_name: character varying(255) NOT NULL
• version: character varying(50) NOT NULL
• checksum: character varying(64) NOT NULL
• applied_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• applied_by: character varying(100) NULL DEFAULT 'system'::character varying
• rollback_sql: text NULL
• rollback_checksum: character varying(64) NULL
• status: character varying(20) NULL DEFAULT 'applied'::character varying
• execution_time_ms: integer NULL
• error_message: text NULL
🔒 CHECK: 2200_25975_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25975_2_not_null - migration_name IS NOT NULL
🔒 CHECK: 2200_25975_3_not_null - version IS NOT NULL
🔒 CHECK: 2200_25975_4_not_null - checksum IS NOT NULL
🔑 PRIMARY KEY: migration_history_pkey
✨ UNIQUE: migration_history_migration_name_version_key
📍 INDEX: migration_history_migration_name_version_key
📍 INDEX: migration_history_pkey
📊 Total: 11 columns, 6 constraints, 2 indexes

## 📊 Table: oauth_audit_log

• id: integer NOT NULL DEFAULT nextval('oauth_audit_log_id_seq'::regclass)
• integration_id: integer NULL
• user_id: integer NOT NULL
• action: character varying(50) NOT NULL
• provider: character varying(50) NOT NULL
• scopes: ARRAY NULL
• ip_address: inet NULL
• user_agent: text NULL
• success: boolean NOT NULL
• error_message: text NULL
• duration_ms: integer NULL
• action_metadata: jsonb NULL
• created_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
• status: character varying(20) NOT NULL DEFAULT 'pending'::character varying
• details: jsonb NULL
🔒 CHECK: 2200_26567_13_not_null - created_at IS NOT NULL
🔒 CHECK: 2200_26567_14_not_null - status IS NOT NULL
🔒 CHECK: 2200_26567_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_26567_3_not_null - user_id IS NOT NULL
🔒 CHECK: 2200_26567_4_not_null - action IS NOT NULL
🔒 CHECK: 2200_26567_5_not_null - provider IS NOT NULL
🔒 CHECK: 2200_26567_9_not_null - success IS NOT NULL
🔒 CHECK: oauth_audit_log_action_check - (((action)::text = ANY ((ARRAY['connect'::character varying, 'disconnect'::character varying, 'refresh'::character varying, 'revoke'::character varying, 'api_call'::character varying, 'error'::character varying])::text[])))
🔒 CHECK: oauth_audit_log_provider_check - (((provider)::text = ANY ((ARRAY['google'::character varying, 'microsoft'::character varying, 'notion'::character varying, 'youtube'::character varying])::text[])))
🔗 FOREIGN KEY: oauth_audit_log_integration_id_fkey
🔗 FOREIGN KEY: oauth_audit_log_user_id_fkey
🔑 PRIMARY KEY: oauth_audit_log_pkey
📍 INDEX: idx_oauth_audit_log_action
📍 INDEX: idx_oauth_audit_log_created_at
📍 INDEX: idx_oauth_audit_log_integration_id
📍 INDEX: idx_oauth_audit_log_provider
📍 INDEX: idx_oauth_audit_log_success
📍 INDEX: idx_oauth_audit_log_user_id
📍 INDEX: oauth_audit_log_pkey
📊 Total: 15 columns, 12 constraints, 7 indexes

## 📊 Table: oauth_consents

• id: integer NOT NULL DEFAULT nextval('oauth_consents_id_seq'::regclass)
• integration_id: integer NOT NULL
• scopes: ARRAY NOT NULL
• granted_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
• expires_at: timestamp without time zone NULL
• ip_address: inet NULL
• user_agent: text NULL
• consent_version: character varying(20) NOT NULL DEFAULT '1.0'::character varying
• is_revoked: boolean NOT NULL DEFAULT false
• revoked_at: timestamp without time zone NULL
• revoked_reason: character varying(100) NULL
🔒 CHECK: 2200_26550_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_26550_2_not_null - integration_id IS NOT NULL
🔒 CHECK: 2200_26550_3_not_null - scopes IS NOT NULL
🔒 CHECK: 2200_26550_4_not_null - granted_at IS NOT NULL
🔒 CHECK: 2200_26550_8_not_null - consent_version IS NOT NULL
🔒 CHECK: 2200_26550_9_not_null - is_revoked IS NOT NULL
🔗 FOREIGN KEY: oauth_consents_integration_id_fkey
🔑 PRIMARY KEY: oauth_consents_pkey
📍 INDEX: idx_oauth_consents_granted_at
📍 INDEX: idx_oauth_consents_integration_id
📍 INDEX: idx_oauth_consents_is_revoked
📍 INDEX: oauth_consents_pkey
📊 Total: 11 columns, 8 constraints, 4 indexes

## 📊 Table: oauth_integrations

• id: integer NOT NULL DEFAULT nextval('oauth_integrations_id_seq'::regclass)
• user_id: integer NOT NULL
• provider: character varying(50) NOT NULL
• provider_user_id: character varying(255) NULL
• status: character varying(20) NOT NULL DEFAULT 'pending'::character varying
• scopes: ARRAY NOT NULL DEFAULT '{}'::text[]
• provider_metadata: jsonb NULL
• created_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
• updated_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
• last_sync_at: timestamp without time zone NULL
• error_message: text NULL
• error_count: integer NULL DEFAULT 0
🔒 CHECK: 2200_26494_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_26494_2_not_null - user_id IS NOT NULL
🔒 CHECK: 2200_26494_3_not_null - provider IS NOT NULL
🔒 CHECK: 2200_26494_5_not_null - status IS NOT NULL
🔒 CHECK: 2200_26494_6_not_null - scopes IS NOT NULL
🔒 CHECK: 2200_26494_8_not_null - created_at IS NOT NULL
🔒 CHECK: 2200_26494_9_not_null - updated_at IS NOT NULL
🔒 CHECK: oauth_integrations_provider_check - (((provider)::text = ANY ((ARRAY['google'::character varying, 'microsoft'::character varying, 'notion'::character varying, 'youtube'::character varying])::text[])))
🔒 CHECK: oauth_integrations_status_check - (((status)::text = ANY ((ARRAY['pending'::character varying, 'active'::character varying, 'revoked'::character varying, 'error'::character varying])::text[])))
🔗 FOREIGN KEY: oauth_integrations_user_id_fkey
🔑 PRIMARY KEY: oauth_integrations_pkey
✨ UNIQUE: oauth_integrations_user_id_provider_key
📍 INDEX: idx_oauth_integrations_created_at
📍 INDEX: idx_oauth_integrations_provider
📍 INDEX: idx_oauth_integrations_status
📍 INDEX: idx_oauth_integrations_user_id
📍 INDEX: oauth_integrations_pkey
📍 INDEX: oauth_integrations_user_id_provider_key
📊 Total: 12 columns, 12 constraints, 6 indexes

## 📊 Table: oauth_scopes

• id: integer NOT NULL DEFAULT nextval('oauth_scopes_id_seq'::regclass)
• provider: character varying(50) NOT NULL
• scope_name: character varying(100) NOT NULL
• display_name: character varying(200) NOT NULL
• description: text NULL
• category: character varying(50) NULL
• is_required: boolean NOT NULL DEFAULT false
• is_dangerous: boolean NOT NULL DEFAULT false
• created_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_26535_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_26535_2_not_null - provider IS NOT NULL
🔒 CHECK: 2200_26535_3_not_null - scope_name IS NOT NULL
🔒 CHECK: 2200_26535_4_not_null - display_name IS NOT NULL
🔒 CHECK: 2200_26535_7_not_null - is_required IS NOT NULL
🔒 CHECK: 2200_26535_8_not_null - is_dangerous IS NOT NULL
🔒 CHECK: 2200_26535_9_not_null - created_at IS NOT NULL
🔒 CHECK: oauth_scopes_provider_check - (((provider)::text = ANY ((ARRAY['google'::character varying, 'microsoft'::character varying, 'notion'::character varying, 'youtube'::character varying])::text[])))
🔑 PRIMARY KEY: oauth_scopes_pkey
✨ UNIQUE: oauth_scopes_provider_scope_name_key
📍 INDEX: idx_oauth_scopes_category
📍 INDEX: idx_oauth_scopes_provider
📍 INDEX: oauth_scopes_pkey
📍 INDEX: oauth_scopes_provider_scope_name_key
📊 Total: 9 columns, 10 constraints, 4 indexes

## 📊 Table: oauth_state

• id: integer NOT NULL DEFAULT nextval('oauth_state_id_seq'::regclass)
• state_token: character varying(128) NOT NULL
• user_id: integer NOT NULL
• provider: character varying(50) NOT NULL
• scopes: ARRAY NOT NULL
• redirect_uri: character varying(500) NULL
• code_verifier: character varying(128) NULL
• code_challenge: character varying(128) NULL
• state_metadata: jsonb NULL
• created_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
• expires_at: timestamp without time zone NOT NULL
• is_used: boolean NOT NULL DEFAULT false
• used_at: timestamp without time zone NULL
🔒 CHECK: 2200_26589_10_not_null - created_at IS NOT NULL
🔒 CHECK: 2200_26589_11_not_null - expires_at IS NOT NULL
🔒 CHECK: 2200_26589_12_not_null - is_used IS NOT NULL
🔒 CHECK: 2200_26589_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_26589_2_not_null - state_token IS NOT NULL
🔒 CHECK: 2200_26589_3_not_null - user_id IS NOT NULL
🔒 CHECK: 2200_26589_4_not_null - provider IS NOT NULL
🔒 CHECK: 2200_26589_5_not_null - scopes IS NOT NULL
🔒 CHECK: oauth_state_provider_check - (((provider)::text = ANY ((ARRAY['google'::character varying, 'microsoft'::character varying, 'notion'::character varying, 'youtube'::character varying])::text[])))
🔗 FOREIGN KEY: oauth_state_user_id_fkey
🔑 PRIMARY KEY: oauth_state_pkey
✨ UNIQUE: oauth_state_state_token_key
📍 INDEX: idx_oauth_state_created_at
📍 INDEX: idx_oauth_state_expires_at
📍 INDEX: idx_oauth_state_is_used
📍 INDEX: idx_oauth_state_provider
📍 INDEX: idx_oauth_state_token
📍 INDEX: idx_oauth_state_user_id
📍 INDEX: oauth_state_pkey
📍 INDEX: oauth_state_state_token_key
📊 Total: 13 columns, 12 constraints, 8 indexes

## 📊 Table: oauth_tokens

• id: integer NOT NULL DEFAULT nextval('oauth_tokens_id_seq'::regclass)
• integration_id: integer NOT NULL
• access_token: text NOT NULL
• refresh_token: text NULL
• token_type: character varying(20) NOT NULL DEFAULT 'Bearer'::character varying
• expires_at: timestamp without time zone NOT NULL
• scope: text NULL
• created_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
• updated_at: timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
• last_used_at: timestamp without time zone NULL
• usage_count: integer NULL DEFAULT 0
🔒 CHECK: 2200_26517_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_26517_2_not_null - integration_id IS NOT NULL
🔒 CHECK: 2200_26517_3_not_null - access_token IS NOT NULL
🔒 CHECK: 2200_26517_5_not_null - token_type IS NOT NULL
🔒 CHECK: 2200_26517_6_not_null - expires_at IS NOT NULL
🔒 CHECK: 2200_26517_8_not_null - created_at IS NOT NULL
🔒 CHECK: 2200_26517_9_not_null - updated_at IS NOT NULL
🔗 FOREIGN KEY: oauth_tokens_integration_id_fkey
🔑 PRIMARY KEY: oauth_tokens_pkey
📍 INDEX: idx_oauth_tokens_created_at
📍 INDEX: idx_oauth_tokens_expires_at
📍 INDEX: idx_oauth_tokens_integration_id
📍 INDEX: oauth_tokens_pkey
📊 Total: 11 columns, 9 constraints, 4 indexes

## 📊 Table: permissions

• id: integer NOT NULL DEFAULT nextval('permissions_id_seq'::regclass)
• name: character varying(100) NOT NULL
• resource_type: character varying(50) NOT NULL
• action: character varying(50) NOT NULL
• description: text NULL
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_25864_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25864_2_not_null - name IS NOT NULL
🔒 CHECK: 2200_25864_3_not_null - resource_type IS NOT NULL
🔒 CHECK: 2200_25864_4_not_null - action IS NOT NULL
🔑 PRIMARY KEY: permissions_pkey
✨ UNIQUE: permissions_name_key
📍 INDEX: idx_permissions_name
📍 INDEX: idx_permissions_resource_action
📍 INDEX: permissions_name_key
📍 INDEX: permissions_pkey
📊 Total: 6 columns, 6 constraints, 4 indexes

## 📊 Table: reminders_view

• id: integer NULL
• user_id: integer NULL
• message: character varying(255) NULL
• remind_at: timestamp without time zone NULL
• created_at: timestamp without time zone NULL
• sent: boolean NULL
• category: text NULL
• priority: text NULL
• status: character varying(20) NULL
• notification_channels: ARRAY NULL
• ai_context: text NULL
• action_required: boolean NULL
• ai_task_description: text NULL
• last_processed: timestamp without time zone NULL
• processing_status: text NULL
• result_summary: text NULL
• error_message: text NULL
📊 Total: 17 columns, 0 constraints, 0 indexes

## 📊 Table: role_permissions

• id: integer NOT NULL DEFAULT nextval('role_permissions_id_seq'::regclass)
• role_id: integer NULL
• permission_id: integer NULL
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_25876_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: role_permissions_permission_id_fkey
🔗 FOREIGN KEY: role_permissions_role_id_fkey
🔑 PRIMARY KEY: role_permissions_pkey
✨ UNIQUE: role_permissions_role_id_permission_id_key
📍 INDEX: idx_role_permissions_permission_id
📍 INDEX: idx_role_permissions_role_id
📍 INDEX: role_permissions_pkey
📍 INDEX: role_permissions_role_id_permission_id_key
📊 Total: 4 columns, 5 constraints, 4 indexes

## 📊 Table: roles

• id: integer NOT NULL DEFAULT nextval('roles_id_seq'::regclass)
• name: character varying(50) NOT NULL
• description: text NULL
• parent_role_id: integer NULL
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• updated_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_25846_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25846_2_not_null - name IS NOT NULL
🔗 FOREIGN KEY: roles_parent_role_id_fkey
🔑 PRIMARY KEY: roles_pkey
✨ UNIQUE: roles_name_key
📍 INDEX: idx_roles_name
📍 INDEX: idx_roles_parent_role_id
📍 INDEX: roles_name_key
📍 INDEX: roles_pkey
📊 Total: 6 columns, 5 constraints, 4 indexes

## 📊 Table: security_events

• id: integer NOT NULL DEFAULT nextval('security_events_id_seq'::regclass)
• user_id: integer NULL
• event_type: character varying(100) NOT NULL
• event_data: jsonb NULL
• ip_address: inet NULL
• user_agent: text NULL
• severity: character varying(20) NULL DEFAULT 'info'::character varying
• created_at: timestamp without time zone NULL DEFAULT now()
🔒 CHECK: 2200_25826_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25826_3_not_null - event_type IS NOT NULL
🔗 FOREIGN KEY: security_events_user_id_fkey
🔑 PRIMARY KEY: security_events_pkey
📍 INDEX: idx_security_events_created_at
📍 INDEX: idx_security_events_event_type
📍 INDEX: idx_security_events_severity
📍 INDEX: idx_security_events_user_id
📍 INDEX: security_events_pkey
📊 Total: 8 columns, 4 constraints, 5 indexes

## 📊 Table: task_results

• id: integer NOT NULL DEFAULT nextval('task_results_id_seq'::regclass)
• task_id: integer NULL
• result: jsonb NULL
• completed_at: timestamp without time zone NULL
🔒 CHECK: 2200_16949_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: task_results_task_id_fkey
🔑 PRIMARY KEY: task_results_pkey
📍 INDEX: task_results_pkey
📊 Total: 4 columns, 3 constraints, 1 indexes

## 📊 Table: tasks

• id: integer NOT NULL DEFAULT nextval('tasks_id_seq'::regclass)
• user_id: integer NULL
• task_name: text NULL
• status: text NULL DEFAULT 'pending'::text
• scheduled_at: timestamp without time zone NULL
• created_at: timestamp without time zone NULL DEFAULT now()
🔒 CHECK: 2200_16933_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: tasks_user_id_fkey
🔑 PRIMARY KEY: tasks_pkey
📍 INDEX: tasks_pkey
📊 Total: 6 columns, 3 constraints, 1 indexes

## 📊 Table: user_roles

• id: integer NOT NULL DEFAULT nextval('user_roles_id_seq'::regclass)
• user_id: integer NULL
• role_id: integer NULL
• is_primary: boolean NULL DEFAULT false
• granted_by: integer NULL
• granted_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• expires_at: timestamp without time zone NULL
🔒 CHECK: 2200_25896_1_not_null - id IS NOT NULL
🔗 FOREIGN KEY: user_roles_granted_by_fkey
🔗 FOREIGN KEY: user_roles_role_id_fkey
🔗 FOREIGN KEY: user_roles_user_id_fkey
🔑 PRIMARY KEY: user_roles_pkey
✨ UNIQUE: user_roles_user_id_role_id_key
📍 INDEX: idx_user_roles_is_primary
📍 INDEX: idx_user_roles_role_id
📍 INDEX: idx_user_roles_user_id
📍 INDEX: user_roles_pkey
📍 INDEX: user_roles_user_id_role_id_key
📊 Total: 7 columns, 6 constraints, 5 indexes

## 📊 Table: user_sessions

• id: integer NOT NULL DEFAULT nextval('user_sessions_id_seq'::regclass)
• user_id: integer NOT NULL
• session_id: character varying(255) NOT NULL
• device_info: jsonb NULL
• ip_address: inet NULL
• user_agent: text NULL
• created_at: timestamp without time zone NULL DEFAULT now()
• last_accessed: timestamp without time zone NULL DEFAULT now()
• expires_at: timestamp without time zone NOT NULL
• is_active: boolean NULL DEFAULT true
🔒 CHECK: 2200_25804_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_25804_2_not_null - user_id IS NOT NULL
🔒 CHECK: 2200_25804_3_not_null - session_id IS NOT NULL
🔒 CHECK: 2200_25804_9_not_null - expires_at IS NOT NULL
🔗 FOREIGN KEY: user_sessions_user_id_fkey
🔑 PRIMARY KEY: user_sessions_pkey
✨ UNIQUE: user_sessions_session_id_key
📍 INDEX: idx_user_sessions_expires_at
📍 INDEX: idx_user_sessions_session_id
📍 INDEX: idx_user_sessions_user_id
📍 INDEX: user_sessions_pkey
📍 INDEX: user_sessions_session_id_key
📊 Total: 10 columns, 7 constraints, 5 indexes

## 📊 Table: user_settings

• id: integer NOT NULL DEFAULT nextval('user_settings_id_seq'::regclass)
• user_id: integer NULL
• key: text NOT NULL
• value: text NULL
• setting_type: character varying(50) NOT NULL DEFAULT 'string'::character varying
• is_public: boolean NULL DEFAULT false
• validation_rules: jsonb NULL
• category: character varying(100) NULL
• description: text NULL
• created_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
• updated_at: timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
🔒 CHECK: 2200_16698_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_16698_3_not_null - key IS NOT NULL
🔒 CHECK: 2200_16698_5_not_null - setting_type IS NOT NULL
🔗 FOREIGN KEY: user_settings_user_id_fkey
🔑 PRIMARY KEY: user_settings_pkey
📍 INDEX: idx_user_settings_created_at
📍 INDEX: idx_user_settings_key_category
📍 INDEX: idx_user_settings_user_category
📍 INDEX: user_settings_pkey
📊 Total: 11 columns, 5 constraints, 4 indexes

## 📊 Table: users

• id: integer NOT NULL DEFAULT nextval('users_id_seq'::regclass)
• email: text NOT NULL
• full_name: text NULL
• created_at: timestamp without time zone NULL DEFAULT now()
• hashed_password: text NULL
• is_active: boolean NULL
• is_verified: boolean NULL
• verification_token: text NULL
• password_reset_token: text NULL
• password_reset_expires: timestamp without time zone NULL
• last_login: timestamp without time zone NULL
• failed_login_attempts: integer NULL
• locked_until: timestamp without time zone NULL
• updated_at: timestamp without time zone NULL
• default_role_id: integer NULL
• role_assigned_at: timestamp without time zone NULL
• role_assigned_by: integer NULL
• phone_number: character varying(20) NULL
🔒 CHECK: 2200_16686_1_not_null - id IS NOT NULL
🔒 CHECK: 2200_16686_2_not_null - email IS NOT NULL
🔗 FOREIGN KEY: users_default_role_id_fkey
🔗 FOREIGN KEY: users_role_assigned_by_fkey
🔑 PRIMARY KEY: users_pkey
✨ UNIQUE: users_email_key
✨ UNIQUE: users_phone_number_key
📍 INDEX: idx_users_email
📍 INDEX: idx_users_is_active
📍 INDEX: idx_users_phone_number
📍 INDEX: users_email_key
📍 INDEX: users_phone_number_key
📍 INDEX: users_pkey
📊 Total: 18 columns, 7 constraints, 6 indexes

# 🔍 Checking for OAuth schema issues...

✅ oauth_state: Table exists
✅ Has 'scopes' column: ARRAY
❌ oauth_integration: Table missing
❌ oauth_token: Table missing
❌ oauth_scope: Table missing
❌ oauth_consent: Table missing
✅ oauth_audit_log: Table exists
✅ Has 'success' column: boolean (NOT NULL)
🔒 Action check constraint: action IS NOT NULL

🚨 Found 5 issues:
❌ oauth_integration: Table does not exist
❌ oauth_token: Table does not exist
❌ oauth_scope: Table does not exist
❌ oauth_consent: Table does not exist
⚠️ oauth_audit_log: Has action check constraint that may restrict values

🎉 Schema inspection completed!
📊 Total tables inspected: 31
