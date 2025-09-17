# Database Schema Documentation

This document provides a comprehensive overview of the Personal Assistant TDAH database schema, including all tables, relationships, constraints, and indexes.

## Table of Contents

- [Schema Overview](#schema-overview)
- [Core Tables](#core-tables)
- [Authentication Tables](#authentication-tables)
- [RBAC Tables](#rbac-tables)
- [Communication Tables](#communication-tables)
- [Memory and Context Tables](#memory-and-context-tables)
- [Task Management Tables](#task-management-tables)
- [Integration Tables](#integration-tables)
- [Analytics Tables](#analytics-tables)
- [Relationships and Constraints](#relationships-and-constraints)
- [Indexes and Performance](#indexes-and-performance)
- [Data Types and Constraints](#data-types-and-constraints)

## Schema Overview

The Personal Assistant TDAH database is designed as a normalized PostgreSQL schema with the following key characteristics:

- **Multi-tenant architecture**: User data isolation with proper foreign key relationships
- **Security-first design**: Comprehensive audit logging and access control
- **Scalable structure**: Optimized indexes and partitioning strategies
- **Flexible data storage**: JSON fields for extensible metadata
- **ACID compliance**: Transactional integrity with proper constraints

### Database Statistics

- **Total Tables**: 35+ tables
- **Primary Entities**: Users, Conversations, Tasks, Integrations
- **Security Tables**: 8 tables for authentication and authorization
- **Analytics Tables**: 5 tables for usage tracking and reporting
- **Integration Tables**: 4 tables for external service connections

## Core Tables

### Users Table

The central user table storing all user account information.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- RBAC fields
    default_role_id INTEGER REFERENCES roles(id),
    role_assigned_at TIMESTAMP,
    role_assigned_by INTEGER REFERENCES users(id)
);
```

**Key Features:**

- Unique email constraint for account identification
- Phone number support for SMS authentication
- Account lockout mechanism for security
- Password reset token management
- RBAC integration with role assignment tracking

**Indexes:**

- Primary key on `id`
- Unique index on `email`
- Unique index on `phone_number`
- Index on `verification_token`
- Index on `password_reset_token`

## Authentication Tables

### Auth Tokens Table

Stores JWT tokens and refresh tokens for user sessions.

```sql
CREATE TABLE auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    token_type VARCHAR(50) DEFAULT 'refresh',
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP
);
```

**Key Features:**

- Token revocation support
- Usage tracking with `last_used_at`
- Automatic cleanup of expired tokens
- Cascade deletion when user is deleted

### MFA Configurations Table

Stores multi-factor authentication settings for users.

```sql
CREATE TABLE mfa_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- TOTP Configuration
    totp_secret VARCHAR(255),
    totp_enabled BOOLEAN DEFAULT FALSE,

    -- SMS Configuration
    sms_enabled BOOLEAN DEFAULT FALSE,
    phone_number VARCHAR(20),

    -- Backup Codes
    backup_codes JSON,

    -- Trusted Devices
    trusted_devices JSON,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- Encrypted TOTP secret storage
- JSON storage for backup codes and trusted devices
- Support for both TOTP and SMS MFA
- One-to-one relationship with users

### User Sessions Table

Tracks active user sessions for security and management.

```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,

    -- Device Information
    device_info JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,

    -- Session Management
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Key Features:**

- Device fingerprinting with JSON metadata
- IP address and user agent tracking
- Session expiration management
- Active session monitoring

### Security Events Table

Comprehensive audit logging for security events.

```sql
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSON,
    severity VARCHAR(20) DEFAULT 'info',
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- System-wide event logging
- Severity levels (info, warning, error, critical)
- JSON metadata for event context
- IP and user agent tracking

## RBAC Tables

### Roles Table

Hierarchical role system for access control.

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_role_id INTEGER REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- Self-referencing hierarchy
- Unique role names
- Descriptive text for role purpose

### Permissions Table

Granular permissions for resource access.

```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- Resource-action based permissions
- Descriptive permission names
- Flexible resource type system

### Role Permissions Table

Many-to-many relationship between roles and permissions.

```sql
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(role_id, permission_id)
);
```

**Key Features:**

- Cascade deletion for data integrity
- Unique constraint on role-permission pairs
- Audit trail with creation timestamps

### User Roles Table

User-role associations with audit trail.

```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

**Key Features:**

- Primary role designation
- Grantor tracking for audit
- Role expiration support
- Cascade deletion on user/role deletion

### Access Audit Logs Table

Comprehensive audit trail for all access decisions.

```sql
CREATE TABLE access_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    action VARCHAR(50) NOT NULL,
    permission_granted BOOLEAN NOT NULL,
    roles_checked TEXT[],
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- Array storage for roles checked
- INET type for IP addresses
- Detailed access decision logging
- Resource-specific audit trails

## Communication Tables

### Conversation States Table

High-level conversation management and metadata.

```sql
CREATE TABLE conversation_states (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_input TEXT,
    focus_areas JSON,
    step_count INTEGER DEFAULT 0,
    last_tool_result JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- Unique conversation identifiers
- JSON storage for flexible metadata
- Step counting for conversation flow
- Tool result tracking

### Conversation Messages Table

Individual message storage with comprehensive metadata.

```sql
CREATE TABLE conversation_messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL REFERENCES conversation_states(conversation_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT,
    message_type VARCHAR(50),
    tool_name VARCHAR(100),
    tool_success VARCHAR(10),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_data JSON
);
```

**Key Features:**

- Role-based message categorization
- Tool execution tracking
- Timezone-aware timestamps
- JSON metadata for extensibility

**Indexes:**

- Composite index on `(conversation_id, role)`
- Composite index on `(conversation_id, timestamp)`
- Index on `message_type`
- Index on `(tool_name, tool_success)`

## Memory and Context Tables

### LTM Memory Table

Long-term memory storage for AI agent context.

```sql
CREATE TABLE ltm_memory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    importance_score DECIMAL(3,2) DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- User-specific memory isolation
- Importance scoring for memory prioritization
- Access tracking for memory optimization
- Flexible memory type categorization

### LTM Memory Tags Table

Tagging system for memory organization.

```sql
CREATE TABLE ltm_memory_tags (
    id SERIAL PRIMARY KEY,
    memory_id INTEGER NOT NULL REFERENCES ltm_memory(id) ON DELETE CASCADE,
    tag_name VARCHAR(100) NOT NULL,
    tag_value VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(memory_id, tag_name)
);
```

**Key Features:**

- Key-value tag system
- Unique constraint on memory-tag pairs
- Flexible tag value storage

### LTM Memory Relationships Table

Relationship mapping between memories.

```sql
CREATE TABLE ltm_memory_relationships (
    id SERIAL PRIMARY KEY,
    source_memory_id INTEGER NOT NULL REFERENCES ltm_memory(id) ON DELETE CASCADE,
    target_memory_id INTEGER NOT NULL REFERENCES ltm_memory(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    strength DECIMAL(3,2) DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(source_memory_id, target_memory_id, relationship_type)
);
```

**Key Features:**

- Bidirectional memory relationships
- Relationship strength scoring
- Type-based relationship categorization

## Task Management Tables

### Todos Table

User task management and organization.

```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- User-specific task isolation
- Priority and status tracking
- Due date management
- Completion timestamp

### Tasks Table

AI-generated task management.

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id VARCHAR(255) REFERENCES conversation_states(conversation_id),
    task_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- AI-generated task tracking
- Conversation linkage
- Priority scoring (1-10)
- Task type categorization

## Integration Tables

### OAuth Integrations Table

External service integration management.

```sql
CREATE TABLE oauth_integrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    scopes JSON,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, provider)
);
```

**Key Features:**

- Provider-specific integration
- Token management with expiration
- Scope-based permission tracking
- One integration per provider per user

### Sync Logs Tables

Integration synchronization tracking.

```sql
CREATE TABLE calendar_sync_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    integration_id INTEGER REFERENCES oauth_integrations(id),
    sync_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    items_synced INTEGER DEFAULT 0,
    error_message TEXT,
    sync_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_completed_at TIMESTAMP
);
```

**Key Features:**

- Sync operation tracking
- Error logging and status monitoring
- Performance metrics (items synced)
- Timing information

## Analytics Tables

### SMS Usage Logs Table

SMS service usage tracking and billing.

```sql
CREATE TABLE sms_usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    direction VARCHAR(10) NOT NULL, -- 'inbound' or 'outbound'
    status VARCHAR(20) NOT NULL,
    twilio_sid VARCHAR(255),
    cost_usd DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- Cost tracking for billing
- Twilio integration tracking
- Direction-based message categorization
- Status monitoring

### Analytics Events Table

General analytics and usage tracking.

```sql
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSON,
    session_id VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**

- Flexible event tracking
- JSON metadata storage
- Session correlation
- User behavior analytics

## Relationships and Constraints

### Foreign Key Relationships

**User-Centric Relationships:**

- `users` → `auth_tokens` (1:many)
- `users` → `mfa_configurations` (1:1)
- `users` → `user_sessions` (1:many)
- `users` → `security_events` (1:many)
- `users` → `conversation_states` (1:many)
- `users` → `ltm_memory` (1:many)
- `users` → `todos` (1:many)
- `users` → `tasks` (1:many)
- `users` → `oauth_integrations` (1:many)

**RBAC Relationships:**

- `users` → `user_roles` (1:many)
- `roles` → `user_roles` (1:many)
- `roles` → `role_permissions` (1:many)
- `permissions` → `role_permissions` (1:many)
- `roles` → `roles` (self-referencing hierarchy)

**Conversation Relationships:**

- `conversation_states` → `conversation_messages` (1:many)
- `conversation_states` → `tasks` (1:many)

**Memory Relationships:**

- `ltm_memory` → `ltm_memory_tags` (1:many)
- `ltm_memory` → `ltm_memory_relationships` (self-referencing)

### Constraint Types

**Unique Constraints:**

- Email addresses (users table)
- Phone numbers (users table)
- Session IDs (user_sessions table)
- Auth tokens (auth_tokens table)
- Conversation IDs (conversation_states table)
- User-provider pairs (oauth_integrations table)

**Check Constraints:**

- Priority values (1-10 range)
- Importance scores (0.0-1.0 range)
- Status values (enum-like constraints)
- Boolean field defaults

**Cascade Deletions:**

- User deletion cascades to all user-related data
- Role deletion cascades to role assignments
- Permission deletion cascades to role permissions
- Conversation deletion cascades to messages

## Indexes and Performance

### Primary Indexes

**User Table:**

- Primary key on `id`
- Unique index on `email`
- Unique index on `phone_number`
- Index on `verification_token`
- Index on `password_reset_token`

**Conversation Tables:**

- Composite index on `(conversation_id, role)` in messages
- Composite index on `(conversation_id, timestamp)` in messages
- Index on `message_type` in messages
- Index on `(tool_name, tool_success)` in messages

**RBAC Tables:**

- Index on `user_id` in user_roles
- Index on `role_id` in user_roles
- Index on `(user_id, role_id)` in user_roles
- Index on `resource_type` in access_audit_logs

**Analytics Tables:**

- Index on `user_id` in all analytics tables
- Index on `created_at` for time-based queries
- Index on `event_type` in analytics_events
- Index on `status` in sms_usage_logs

### Performance Optimizations

**Partitioning Strategy:**

- Time-based partitioning for audit logs
- User-based partitioning for large tables
- Hash partitioning for session data

**Query Optimization:**

- Composite indexes for common query patterns
- Covering indexes for frequently accessed columns
- Partial indexes for filtered queries

**Maintenance:**

- Regular VACUUM and ANALYZE operations
- Index usage monitoring
- Query performance tracking

## Data Types and Constraints

### Standard Data Types

**Identifiers:**

- `SERIAL` for auto-incrementing primary keys
- `INTEGER` for foreign key references
- `VARCHAR(n)` for string fields with length limits

**Text Storage:**

- `TEXT` for unlimited text content
- `VARCHAR(n)` for limited text fields
- `JSON` for structured metadata

**Temporal Data:**

- `TIMESTAMP` for absolute time values
- `TIMESTAMP WITH TIME ZONE` for timezone-aware data
- `INTERVAL` for duration calculations

**Numeric Data:**

- `DECIMAL(p,s)` for precise decimal values
- `INTEGER` for whole numbers
- `BOOLEAN` for true/false values

### Custom Constraints

**Email Validation:**

```sql
ALTER TABLE users ADD CONSTRAINT email_format
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
```

**Phone Number Validation:**

```sql
ALTER TABLE users ADD CONSTRAINT phone_format
CHECK (phone_number ~* '^\+?[1-9]\d{1,14}$');
```

**Priority Range Validation:**

```sql
ALTER TABLE tasks ADD CONSTRAINT priority_range
CHECK (priority >= 1 AND priority <= 10);
```

**Status Enum Validation:**

```sql
ALTER TABLE todos ADD CONSTRAINT status_valid
CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled'));
```

This comprehensive database schema provides a solid foundation for the Personal Assistant TDAH system, ensuring data integrity, security, and scalability while supporting all the required functionality for user management, AI interactions, and external integrations.
