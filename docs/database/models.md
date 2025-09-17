# Database Models Documentation

This document provides comprehensive documentation for all SQLAlchemy database models in the Personal Assistant TDAH system, including their relationships, methods, and usage patterns.

## Table of Contents

- [Model Overview](#model-overview)
- [Base Model](#base-model)
- [Authentication Models](#authentication-models)
- [RBAC Models](#rbac-models)
- [Communication Models](#communication-models)
- [Memory Models](#memory-models)
- [Task Models](#task-models)
- [Integration Models](#integration-models)
- [Analytics Models](#analytics-models)
- [Model Relationships](#model-relationships)
- [Usage Patterns](#usage-patterns)

## Model Overview

The Personal Assistant TDAH system uses SQLAlchemy ORM with PostgreSQL as the backend database. All models inherit from a common `Base` class and follow consistent patterns for:

- **Primary Keys**: Auto-incrementing integer IDs
- **Timestamps**: `created_at` and `updated_at` fields
- **Relationships**: Proper foreign key relationships with cascade options
- **Validation**: Field-level validation and constraints
- **Serialization**: Methods for converting to/from dictionaries

### Model Categories

1. **Authentication Models**: User accounts, sessions, MFA, security events
2. **RBAC Models**: Roles, permissions, user-role assignments
3. **Communication Models**: Conversations, messages, chat functionality
4. **Memory Models**: Long-term memory, context, relationships
5. **Task Models**: Todos, tasks, AI-generated actions
6. **Integration Models**: OAuth, external service connections
7. **Analytics Models**: Usage tracking, performance metrics

## Base Model

### Base Class

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields and methods."""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
```

**Key Features:**

- Abstract base class for all models
- Common timestamp fields
- Dictionary serialization method
- Consistent string representation

## Authentication Models

### User Model

```python
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # RBAC fields
    default_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role_assigned_at = Column(DateTime, nullable=True)
    role_assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    conversations = relationship("ConversationState", back_populates="user", cascade="all, delete-orphan")
    auth_tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")
    mfa_configuration = relationship("MFAConfiguration", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", foreign_keys="UserRole.user_id", back_populates="user", cascade="all, delete-orphan")
    access_audit_logs = relationship("AccessAuditLog", foreign_keys="AccessAuditLog.user_id", back_populates="user", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="user", cascade="all, delete-orphan")
```

**Key Features:**

- Unique email and phone number constraints
- Account lockout mechanism
- Password reset token management
- Comprehensive relationship mapping
- RBAC integration

**Methods:**

- `is_locked()`: Check if account is currently locked
- `increment_failed_login()`: Increment failed login attempts
- `reset_failed_login()`: Reset failed login counter
- `lock_account(duration)`: Lock account for specified duration

### AuthToken Model

```python
class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    token_type = Column(String, default="refresh")
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="auth_tokens")
```

**Key Features:**

- Token revocation support
- Usage tracking
- Type-based token categorization
- Automatic expiration

**Methods:**

- `is_expired()`: Check if token has expired
- `revoke()`: Mark token as revoked
- `update_usage()`: Update last used timestamp

### MFAConfiguration Model

```python
from sqlalchemy import JSON

class MFAConfiguration(Base):
    __tablename__ = "mfa_configurations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # TOTP Configuration
    totp_secret = Column(String(255), nullable=True)
    totp_enabled = Column(Boolean, default=False)

    # SMS Configuration
    sms_enabled = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)

    # Backup Codes
    backup_codes = Column(JSON, nullable=True)

    # Trusted Devices
    trusted_devices = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="mfa_configuration")
```

**Key Features:**

- One-to-one relationship with users
- JSON storage for backup codes and trusted devices
- Support for both TOTP and SMS MFA
- Encrypted secret storage

**Methods:**

- `enable_totp(secret)`: Enable TOTP with secret
- `disable_totp()`: Disable TOTP
- `enable_sms(phone_number)`: Enable SMS MFA
- `disable_sms()`: Disable SMS MFA
- `generate_backup_codes()`: Generate new backup codes
- `is_device_trusted(device_hash)`: Check if device is trusted

### UserSession Model

```python
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)

    # Device Information
    device_info = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Session Management
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
```

**Key Features:**

- Device fingerprinting
- IP and user agent tracking
- Session expiration management
- Active session monitoring

**Methods:**

- `is_expired()`: Check if session has expired
- `extend(duration)`: Extend session expiration
- `invalidate()`: Mark session as inactive
- `update_access()`: Update last accessed timestamp

### SecurityEvent Model

```python
class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Event Details
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=True)
    severity = Column(String(20), default="info")

    # Request Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="security_events")
```

**Key Features:**

- System-wide event logging
- Severity levels (info, warning, error, critical)
- JSON metadata for event context
- IP and user agent tracking

**Methods:**

- `log_event(event_type, data, severity)`: Static method to log events
- `get_events_by_user(user_id, limit)`: Get events for specific user
- `get_events_by_severity(severity, limit)`: Get events by severity level

## RBAC Models

### Role Model

```python
from sqlalchemy import Text

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("Permission", secondary="role_permissions")
    parent_role = relationship("Role", remote_side=[id])
    child_roles = relationship("Role", overlaps="parent_role")
```

**Key Features:**

- Self-referencing hierarchy
- Unique role names
- Descriptive text for role purpose
- Many-to-many relationship with permissions

**Methods:**

- `get_all_permissions()`: Get all permissions including inherited
- `add_permission(permission)`: Add permission to role
- `remove_permission(permission)`: Remove permission from role
- `get_child_roles()`: Get all child roles
- `get_parent_roles()`: Get all parent roles

### Permission Model

```python
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    resource_type = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary="role_permissions", overlaps="permissions")
```

**Key Features:**

- Resource-action based permissions
- Descriptive permission names
- Flexible resource type system
- Many-to-many relationship with roles

**Methods:**

- `get_roles()`: Get all roles with this permission
- `check_user_access(user_id)`: Check if user has this permission
- `create_permission(name, resource_type, action)`: Static method to create permissions

### UserRole Model

```python
class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    is_primary = Column(Boolean, default=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role")
```

**Key Features:**

- Primary role designation
- Grantor tracking for audit
- Role expiration support
- Cascade deletion on user/role deletion

**Methods:**

- `is_expired()`: Check if role assignment has expired
- `extend_expiration(duration)`: Extend role expiration
- `revoke()`: Revoke role assignment

## Communication Models

### ConversationState Model

```python
class ConversationState(Base):
    __tablename__ = "conversation_states"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_input = Column(Text)
    focus_areas = Column(JSON)
    step_count = Column(Integer, default=0)
    last_tool_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation_state", cascade="all, delete-orphan")
```

**Key Features:**

- Unique conversation identifiers
- JSON storage for flexible metadata
- Step counting for conversation flow
- Tool result tracking

**Methods:**

- `add_message(role, content, message_type)`: Add message to conversation
- `get_messages(limit)`: Get conversation messages
- `increment_step()`: Increment step count
- `update_tool_result(result)`: Update last tool result

### ConversationMessage Model

```python
from sqlalchemy import Index
from sqlalchemy.sql import func

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), ForeignKey("conversation_states.conversation_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)
    content = Column(Text)
    message_type = Column(String(50), index=True)
    tool_name = Column(String(100), index=True)
    tool_success = Column(String(10), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    additional_data = Column(JSON)

    # Relationship to conversation state
    conversation_state = relationship("ConversationState", back_populates="messages")

    # Indexes for performance
    __table_args__ = (
        Index("idx_message_conversation_role", "conversation_id", "role"),
        Index("idx_message_timestamp", "conversation_id", "timestamp"),
        Index("idx_message_type", "message_type"),
        Index("idx_message_tool", "tool_name", "tool_success"),
    )
```

**Key Features:**

- Role-based message categorization
- Tool execution tracking
- Timezone-aware timestamps
- JSON metadata for extensibility
- Performance-optimized indexes

**Methods:**

- `to_dict()`: Convert to dictionary for serialization
- `from_conversation_item(conversation_id, item, message_type)`: Create from conversation item
- `is_tool_message()`: Check if message is tool-related
- `get_tool_result()`: Get tool execution result

## Memory Models

### LTMMemory Model

```python
from sqlalchemy import DECIMAL

class LTMMemory(Base):
    __tablename__ = "ltm_memory"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    importance_score = Column(DECIMAL(3,2), default=0.5)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Key Features:**

- User-specific memory isolation
- Importance scoring for memory prioritization
- Access tracking for memory optimization
- Flexible memory type categorization

**Methods:**

- `increment_access()`: Increment access count
- `update_importance(score)`: Update importance score
- `get_related_memories()`: Get related memories
- `add_tag(tag_name, tag_value)`: Add tag to memory

### LTMMemoryTag Model

```python
class LTMMemoryTag(Base):
    __tablename__ = "ltm_memory_tags"

    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey("ltm_memory.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    tag_value = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('memory_id', 'tag_name', name='uq_memory_tag'),
    )
```

**Key Features:**

- Key-value tag system
- Unique constraint on memory-tag pairs
- Flexible tag value storage

**Methods:**

- `get_memories_by_tag(tag_name, tag_value)`: Static method to get memories by tag
- `remove_tag()`: Remove tag from memory

### LTMMemoryRelationship Model

```python
class LTMMemoryRelationship(Base):
    __tablename__ = "ltm_memory_relationships"

    id = Column(Integer, primary_key=True)
    source_memory_id = Column(Integer, ForeignKey("ltm_memory.id", ondelete="CASCADE"), nullable=False)
    target_memory_id = Column(Integer, ForeignKey("ltm_memory.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    strength = Column(DECIMAL(3,2), default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('source_memory_id', 'target_memory_id', 'relationship_type', name='uq_memory_relationship'),
    )
```

**Key Features:**

- Bidirectional memory relationships
- Relationship strength scoring
- Type-based relationship categorization

**Methods:**

- `get_related_memories(memory_id, relationship_type)`: Get related memories
- `add_relationship(target_memory, relationship_type, strength)`: Add relationship
- `remove_relationship(target_memory, relationship_type)`: Remove relationship

## Task Models

### Todo Model

```python
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="pending")
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="todos")
```

**Key Features:**

- User-specific task isolation
- Priority and status tracking
- Due date management
- Completion timestamp

**Methods:**

- `mark_completed()`: Mark todo as completed
- `mark_pending()`: Mark todo as pending
- `update_priority(priority)`: Update todo priority
- `is_overdue()`: Check if todo is overdue

### Task Model

```python
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(String(255), ForeignKey("conversation_states.conversation_id"))
    task_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="pending")
    priority = Column(Integer, default=5)
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Key Features:**

- AI-generated task tracking
- Conversation linkage
- Priority scoring (1-10)
- Task type categorization

**Methods:**

- `mark_completed()`: Mark task as completed
- `update_priority(priority)`: Update task priority
- `get_conversation_context()`: Get related conversation context

## Integration Models

### OAuthIntegration Model

```python
class OAuthIntegration(Base):
    __tablename__ = "oauth_integrations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    scopes = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_user_provider'),
    )
```

**Key Features:**

- Provider-specific integration
- Token management with expiration
- Scope-based permission tracking
- One integration per provider per user

**Methods:**

- `is_expired()`: Check if access token has expired
- `refresh_access_token()`: Refresh access token
- `revoke()`: Revoke integration
- `get_scope_permissions()`: Get permissions from scopes

## Analytics Models

### SMSUsageLog Model

```python
from sqlalchemy import DECIMAL

class SMSUsageLog(Base):
    __tablename__ = "sms_usage_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message_content = Column(Text, nullable=False)
    direction = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False)
    twilio_sid = Column(String(255))
    cost_usd = Column(DECIMAL(10,4))
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Key Features:**

- Cost tracking for billing
- Twilio integration tracking
- Direction-based message categorization
- Status monitoring

**Methods:**

- `calculate_cost()`: Calculate message cost
- `get_user_usage(user_id, period)`: Get usage for user
- `get_cost_breakdown(period)`: Get cost breakdown

### AnalyticsEvent Model

```python
class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON)
    session_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Key Features:**

- Flexible event tracking
- JSON metadata storage
- Session correlation
- User behavior analytics

**Methods:**

- `log_event(event_type, data, user_id)`: Static method to log events
- `get_events_by_type(event_type, limit)`: Get events by type
- `get_user_events(user_id, limit)`: Get events for user

## Model Relationships

### Relationship Patterns

**One-to-Many Relationships:**

- User → AuthTokens
- User → UserSessions
- User → SecurityEvents
- User → Conversations
- User → LTMMemory
- User → Todos
- User → Tasks
- Conversation → Messages

**One-to-One Relationships:**

- User → MFAConfiguration
- User → UserSettings

**Many-to-Many Relationships:**

- Role ↔ Permission (via RolePermission)
- User ↔ Role (via UserRole)

**Self-Referencing Relationships:**

- Role → Role (parent-child hierarchy)
- LTMMemory → LTMMemory (relationships)

### Cascade Options

**Cascade Delete:**

- User deletion cascades to all user-related data
- Role deletion cascades to role assignments
- Permission deletion cascades to role permissions
- Conversation deletion cascades to messages

**Cascade Options Used:**

- `all, delete-orphan`: Complete cascade with orphan cleanup
- `CASCADE`: Database-level cascade deletion
- `SET NULL`: Set foreign key to NULL on deletion

## Usage Patterns

### Common Query Patterns

**User Authentication:**

```python
# Find user by email
user = session.query(User).filter(User.email == email).first()

# Check if user is locked
if user.is_locked():
    raise AccountLockedError()

# Verify password
if not verify_password(password, user.hashed_password):
    user.increment_failed_login()
    raise InvalidCredentialsError()
```

**RBAC Permission Checking:**

```python
# Get user permissions
user_roles = session.query(UserRole).filter(
    UserRole.user_id == user_id,
    UserRole.is_primary == True
).all()

permissions = []
for user_role in user_roles:
    role_permissions = session.query(Permission).join(
        RolePermission
    ).filter(RolePermission.role_id == user_role.role_id).all()
    permissions.extend(role_permissions)
```

**Conversation Management:**

```python
# Create new conversation
conversation = ConversationState(
    conversation_id=generate_conversation_id(),
    user_id=user_id,
    user_input=user_input
)
session.add(conversation)

# Add message to conversation
message = ConversationMessage(
    conversation_id=conversation.conversation_id,
    role="user",
    content=user_input,
    message_type="user_input"
)
session.add(message)
```

**Memory Management:**

```python
# Create memory
memory = LTMMemory(
    user_id=user_id,
    memory_type="conversation",
    content=conversation_summary,
    importance_score=0.8
)
session.add(memory)

# Add tags
tag = LTMMemoryTag(
    memory_id=memory.id,
    tag_name="topic",
    tag_value="productivity"
)
session.add(tag)
```

### Performance Optimization

**Eager Loading:**

```python
# Load user with all relationships
user = session.query(User).options(
    joinedload(User.conversations),
    joinedload(User.auth_tokens),
    joinedload(User.mfa_configuration)
).filter(User.id == user_id).first()
```

**Batch Operations:**

```python
# Bulk insert messages
messages = [
    ConversationMessage(conversation_id=conv_id, role="user", content=msg)
    for msg in message_list
]
session.bulk_save_objects(messages)
```

**Query Optimization:**

```python
# Use indexes for performance
messages = session.query(ConversationMessage).filter(
    ConversationMessage.conversation_id == conv_id
).order_by(ConversationMessage.timestamp).limit(50).all()
```

This comprehensive model documentation provides developers with all the information needed to work effectively with the Personal Assistant TDAH database models, including their relationships, methods, and usage patterns.
