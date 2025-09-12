# Database Analysis: Current State vs Required State

## 🔍 **Current Database State**

### **Existing Task-Related Tables:**

#### **1. `tasks` table (Basic)**

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    task_name VARCHAR,
    status VARCHAR DEFAULT 'pending',
    scheduled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### **2. `ai_tasks` table (AI-Powered)**

```sql
CREATE TABLE ai_tasks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,  -- 'reminder', 'automated_task', 'periodic_task'
    schedule_type VARCHAR(20) NOT NULL,  -- 'once', 'daily', 'weekly', 'monthly', 'custom'
    schedule_config JSON,
    next_run_at TIMESTAMP,
    last_run_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'paused', 'completed', 'failed'
    ai_context TEXT,
    notification_channels TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **3. `reminders` table (Simple)**

```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message VARCHAR NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP,
    sent BOOLEAN DEFAULT FALSE
);
```

## ❌ **What's Missing: No `todos` Table**

**There is NO `todos` table in the current database!**

This means we need to create the entire todo system from scratch, not enhance an existing one.

## 🎯 **Required `todos` Table Schema**

Based on the requirements, we need to create:

```sql
CREATE TABLE todos (
    -- Primary key
    id INTEGER PRIMARY KEY,

    -- User relationship
    user_id INTEGER REFERENCES users(id) NOT NULL,

    -- Basic todo fields
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    done_date TIMESTAMP,
    priority VARCHAR(20) DEFAULT 'medium',  -- 'high', 'medium', 'low'
    category VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'cancelled'

    -- Missed counter fields (NEW)
    missed_count INTEGER DEFAULT 0 NOT NULL,
    last_missed_at TIMESTAMP,

    -- Segmentation fields (NEW)
    is_segmented BOOLEAN DEFAULT FALSE NOT NULL,
    parent_task_id INTEGER REFERENCES todos(id),
    segmentation_triggered_at TIMESTAMP,

    -- Analytics fields (NEW)
    completion_patterns JSONB,
    user_insights JSONB,
    segmentation_suggestions JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_due_date ON todos(due_date);
CREATE INDEX idx_todos_missed_count ON todos(missed_count);
CREATE INDEX idx_todos_is_segmented ON todos(is_segmented);
CREATE INDEX idx_todos_parent_task_id ON todos(parent_task_id);
CREATE INDEX idx_todos_user_missed ON todos(user_id, missed_count);
```

## 🔄 **Migration Strategy**

### **Option 1: Create New `todos` Table (Recommended)**

- Create a completely new `todos` table
- Keep existing `tasks` and `ai_tasks` tables for backward compatibility
- Migrate any relevant data from existing tables if needed

### **Option 2: Enhance Existing `tasks` Table**

- Add new fields to the existing `tasks` table
- Risk: Could break existing functionality
- More complex migration

### **Option 3: Enhance `ai_tasks` Table**

- Add todo-specific fields to `ai_tasks`
- Risk: Mixing concerns (AI tasks vs user todos)
- Could work but not ideal

## 📋 **Recommended Approach: Option 1**

**Create a new `todos` table** because:

1. **Clear Separation of Concerns**: Todos are user-driven tasks, different from AI tasks
2. **No Breaking Changes**: Existing `tasks` and `ai_tasks` remain unchanged
3. **Clean Implementation**: Can implement all required features without constraints
4. **Future Flexibility**: Can evolve independently from other task systems

## 🚀 **Implementation Steps**

### **1. Create Database Migration**

```python
# migrations/create_todos_table.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create todos table
    op.create_table('todos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('done_date', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(20), nullable=True, server_default='medium'),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, server_default='pending'),
        sa.Column('missed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_missed_at', sa.DateTime(), nullable=True),
        sa.Column('is_segmented', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('parent_task_id', sa.Integer(), nullable=True),
        sa.Column('segmentation_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('completion_patterns', postgresql.JSONB(), nullable=True),
        sa.Column('user_insights', postgresql.JSONB(), nullable=True),
        sa.Column('segmentation_suggestions', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_task_id'], ['todos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_todos_user_id', 'todos', ['user_id'])
    op.create_index('idx_todos_status', 'todos', ['status'])
    op.create_index('idx_todos_due_date', 'todos', ['due_date'])
    op.create_index('idx_todos_missed_count', 'todos', ['missed_count'])
    op.create_index('idx_todos_is_segmented', 'todos', ['is_segmented'])
    op.create_index('idx_todos_parent_task_id', 'todos', ['parent_task_id'])
    op.create_index('idx_todos_user_missed', 'todos', ['user_id', 'missed_count'])

def downgrade():
    op.drop_table('todos')
```

### **2. Create SQLAlchemy Model**

```python
# src/personal_assistant/database/models/todos.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Todo(Base):
    __tablename__ = "todos"

    # Primary key
    id = Column(Integer, primary_key=True)

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Basic todo fields
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    done_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default='medium')  # 'high', 'medium', 'low'
    category = Column(String(50), nullable=True)
    status = Column(String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'cancelled'

    # Missed counter fields
    missed_count = Column(Integer, default=0, nullable=False)
    last_missed_at = Column(DateTime, nullable=True)

    # Segmentation fields
    is_segmented = Column(Boolean, default=False, nullable=False)
    parent_task_id = Column(Integer, ForeignKey("todos.id"), nullable=True)
    segmentation_triggered_at = Column(DateTime, nullable=True)

    # Analytics fields
    completion_patterns = Column(JSONB, nullable=True)
    user_insights = Column(JSONB, nullable=True)
    segmentation_suggestions = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="todos")
    parent_task = relationship("Todo", remote_side=[id], backref="subtasks")

    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}', status='{self.status}')>"
```

### **3. Update User Model**

```python
# Add to src/personal_assistant/database/models/users.py
# Add this relationship to the User class:
todos = relationship("Todo", back_populates="user", cascade="all, delete-orphan")
```

## ✅ **Next Steps**

1. **Create the migration script** for the `todos` table
2. **Create the SQLAlchemy model** for `Todo`
3. **Update the User model** to include the relationship
4. **Run the migration** to create the table
5. **Implement the todo tool** with all the enhanced features

This approach gives us a clean, dedicated todo system that can be enhanced with all the missed counter and segmentation features without affecting existing functionality.
