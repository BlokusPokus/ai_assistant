# Task 055: Todo List Tool - Onboarding

## 🎯 **Context & Background**

You are implementing a comprehensive todo list management tool for the Personal Assistant TDAH system. This tool will provide users with an intuitive way to create, manage, and track their personal tasks and todos, with features specifically designed for ADHD-friendly organization and productivity.

## 📋 **Current System State**

### **Existing Infrastructure**

The system already has:

- **Database Models**: `Task` and `AITask` models in `src/personal_assistant/database/models/`
- **Reminder System**: AI-driven reminder tool in `src/personal_assistant/tools/reminders/`
- **Tools Architecture**: Robust tool registry and execution system in `src/personal_assistant/tools/`
- **Agent Integration**: LLM-powered agent that can use tools
- **Multi-Interface Support**: SMS and web interfaces

### **Current Task Management**

- **Basic Task Model**: Simple task storage with user_id, task_name, status, scheduled_at
- **AI Task Model**: More complex model with task_type, schedule_type, AI context
- **Reminder Tool**: Focuses on AI-driven scheduled tasks and reminders
- **Background Task System**: Celery-based system for automated tasks

### **Gap Analysis**

- **User-Driven Tasks**: Current system focuses on AI-driven tasks, not user-driven todos
- **Todo-Specific Features**: Missing categories, priorities, progress tracking
- **ADHD-Friendly Design**: No visual organization or motivation features
- **Natural Language Interface**: Limited natural language task creation
- **Web Dashboard Integration**: No visual todo management interface

## 🏗️ **Architecture Overview**

### **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SMS Interface │    │   Web Interface │    │   Agent Core    │
│   (Primary)     │    │   (Dashboard)   │    │   (LLM)         │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Todo Tool System      │
                    │  ┌─────────────────────┐  │
                    │  │   TodoTool Class    │  │
                    │  │   - CRUD Operations │  │
                    │  │   - Natural Language│  │
                    │  │   - ADHD Features   │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Database Layer         │
                    │  ┌─────────────────────┐  │
                    │  │   Enhanced Task     │  │
                    │  │   Model             │  │
                    │  │   - Categories      │  │
                    │  │   - Priorities      │  │
                    │  │   - Progress        │  │
                    │  │   - Dependencies    │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

### **Tool Integration Pattern**

The todo tool will follow the existing tool pattern:

```python
class TodoTool:
    """Container for todo management tools."""

    def __init__(self):
        # Create individual tools
        self.create_todo_tool = Tool(...)
        self.list_todos_tool = Tool(...)
        self.update_todo_tool = Tool(...)
        self.delete_todo_tool = Tool(...)
        self.complete_todo_tool = Tool(...)

    def __iter__(self):
        """Iterate over available todo tools."""
        yield self.create_todo_tool
        yield self.list_todos_tool
        # ... etc
```

## 🔍 **Key Files to Study**

### **Existing Tool Examples**

1. **`src/personal_assistant/tools/reminders/reminder_tool.py`**

   - Study the tool structure and patterns
   - Understand how tools integrate with the agent
   - See how database operations are handled

2. **`src/personal_assistant/tools/base.py`**

   - Understand the Tool base class
   - Study the ToolRegistry system
   - Learn about tool execution patterns

3. **`src/personal_assistant/database/models/tasks.py`**
   - Current Task model structure
   - Database relationships and constraints
   - Migration patterns

### **Database Models**

1. **`src/personal_assistant/database/models/tasks.py`**

   - Basic Task model (needs enhancement)
   - User relationship and foreign keys
   - Current fields and constraints

2. **`src/personal_assistant/database/models/ai_tasks.py`**
   - More complex AITask model
   - Advanced scheduling and AI context
   - JSON fields and arrays

### **Agent Integration**

1. **`src/personal_assistant/core/agent.py`**

   - How tools are executed by the agent
   - Tool calling patterns and error handling
   - User context and authentication

2. **`src/personal_assistant/tools/__init__.py`**
   - How tools are registered in the system
   - Tool registry creation and management
   - Category assignment and organization

## 🎯 **Implementation Strategy**

### **Phase 1: Core Implementation (2 days)**

1. **Database Enhancement**

   - Add todo-specific fields to Task model
   - Create database migration
   - Test database operations

2. **Basic Todo Tool**

   - Implement TodoTool class with CRUD operations
   - Follow existing tool patterns
   - Add error handling and validation

3. **API Endpoints**
   - Create RESTful endpoints for todo management
   - Follow existing API patterns
   - Add proper authentication and validation

### **Phase 2: Advanced Features (2 days)**

1. **Categories and Priorities**

   - Implement category system
   - Add priority levels (high, medium, low)
   - Create visual indicators

2. **Progress Tracking**

   - Add progress percentage tracking
   - Implement completion status
   - Create progress insights

3. **Due Date Management**
   - Smart due date parsing
   - Reminder integration
   - Overdue task handling

### **Phase 3: ADHD-Friendly Features (1 day)**

1. **Visual Organization**

   - Color-coded categories
   - Priority indicators
   - Progress visualization

2. **Motivation Features**

   - Completion celebrations
   - Progress insights
   - Achievement tracking

3. **Task Breakdown**
   - Subtask support
   - Task dependencies
   - Smart suggestions

## 🚨 **Critical Considerations**

### **Database Schema Changes**

The existing Task model needs enhancement:

```python
# Current Task model
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_name = Column(String)
    status = Column(String, default='pending')
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Enhanced Task model (what we need to add)
class Task(Base):
    # ... existing fields ...

    # New todo-specific fields
    description = Column(Text)
    category = Column(String(50))
    priority = Column(String(20), default='medium')
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    progress_percentage = Column(Integer, default=0)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'))
    tags = Column(JSON)
    metadata = Column(JSON)
```

### **Migration Strategy**

- **Backward Compatibility**: Ensure existing tasks continue to work
- **Default Values**: Provide sensible defaults for new fields
- **Data Migration**: Handle existing task data appropriately
- **Rollback Plan**: Ability to revert changes if needed

### **Tool Integration**

- **Registry Integration**: Register todo tools with existing system
- **Agent Integration**: Enable agent to use todo tools intelligently
- **Error Handling**: Follow existing error handling patterns
- **Performance**: Ensure efficient database queries

## 🔧 **Technical Requirements**

### **Database Requirements**

- **PostgreSQL**: Use existing database setup
- **SQLAlchemy**: Follow existing ORM patterns
- **Migrations**: Use Alembic for schema changes
- **Indexing**: Add indexes for performance

### **API Requirements**

- **FastAPI**: Follow existing API patterns
- **Authentication**: Use existing JWT authentication
- **Validation**: Use Pydantic models for validation
- **Error Handling**: Follow existing error response patterns

### **Frontend Requirements**

- **React**: Integrate with existing dashboard
- **TypeScript**: Follow existing type patterns
- **Styling**: Use existing Tailwind CSS setup
- **State Management**: Use existing Zustand store

## 📊 **Success Criteria**

### **Functional Requirements**

- [ ] Create, read, update, delete todos
- [ ] Category and priority management
- [ ] Progress tracking and completion
- [ ] Due date management and reminders
- [ ] Natural language SMS interface
- [ ] Web dashboard integration

### **Technical Requirements**

- [ ] 90%+ test coverage
- [ ] < 200ms response time
- [ ] Proper error handling
- [ ] Database migration working
- [ ] API documentation complete

### **User Experience Requirements**

- [ ] Intuitive task creation
- [ ] Visual organization
- [ ] ADHD-friendly features
- [ ] Consistent SMS/web experience
- [ ] Performance optimization

## 🚀 **Getting Started**

### **Step 1: Study Existing Code**

1. Read `src/personal_assistant/tools/reminders/reminder_tool.py`
2. Study `src/personal_assistant/tools/base.py`
3. Review `src/personal_assistant/database/models/tasks.py`
4. Understand `src/personal_assistant/tools/__init__.py`

### **Step 2: Plan Database Changes**

1. Design enhanced Task model
2. Plan database migration
3. Consider backward compatibility
4. Plan rollback strategy

### **Step 3: Implement Core Tool**

1. Create `src/personal_assistant/tools/todos/` directory
2. Implement `todo_tool.py` following existing patterns
3. Add error handling and validation
4. Test basic CRUD operations

### **Step 4: Add Advanced Features**

1. Implement categories and priorities
2. Add progress tracking
3. Create due date management
4. Add ADHD-friendly features

### **Step 5: Integration & Testing**

1. Register tools with system
2. Test agent integration
3. Add comprehensive tests
4. Performance optimization

## ❓ **Questions to Answer**

Before starting implementation, consider:

1. **Database Design**: Should we enhance Task model or create new Todo model?
2. **Feature Priority**: Which ADHD-friendly features are most important?
3. **Interface Priority**: SMS first or web interface first?
4. **Agent Integration**: How should agent intelligently use todo tools?
5. **Performance**: What are the expected usage patterns?

## 📚 **Additional Resources**

### **ADHD-Friendly Design**

- **Visual Organization**: Clear categories, priorities, progress indicators
- **Motivation**: Completion celebrations, progress insights
- **Simplicity**: Easy task creation and management
- **Flexibility**: Support different organizational styles

### **Technical References**

- **Existing Tools**: Study reminder_tool.py and other implementations
- **Database Patterns**: Review existing model patterns
- **API Patterns**: Follow existing FastAPI patterns
- **Frontend Patterns**: Use existing React component patterns

---

**Remember**: This is a user-facing feature that will significantly impact the user experience. Focus on creating an intuitive, ADHD-friendly interface that makes task management simple and motivating.
