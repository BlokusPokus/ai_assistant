# Task 055: Todo List Tool - Implementation Guide

## 🎯 **Quick Start**

This guide provides step-by-step instructions for implementing the todo list tool.

## 📁 **File Structure**

```
src/personal_assistant/tools/todos/
├── __init__.py
├── todo_tool.py              # Main tool implementation
├── todo_internal.py          # Business logic
└── todo_error_handler.py     # Error handling
```

## 🗄️ **Database Changes**

### **Enhanced Task Model**

```python
# Add to src/personal_assistant/database/models/tasks.py
class Task(Base):
    __tablename__ = 'tasks'

    # Existing fields
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_name = Column(String)
    status = Column(String, default='pending')
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

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

### **Migration Script**

```python
# Create migration file
def upgrade():
    op.add_column('tasks', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('tasks', sa.Column('priority', sa.String(20), nullable=True, default='medium'))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('completed_at', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('progress_percentage', sa.Integer(), nullable=True, default=0))
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('tasks', sa.Column('metadata', sa.JSON(), nullable=True))
```

## 🛠️ **Tool Implementation**

### **Basic Todo Tool Structure**

```python
# src/personal_assistant/tools/todos/todo_tool.py
from ..base import Tool
from .todo_internal import TodoInternal

class TodoTool:
    """Container for todo management tools."""

    def __init__(self):
        self.todo_internal = TodoInternal()

        # Create individual tools
        self.create_todo_tool = Tool(
            name="create_todo",
            func=self.create_todo,
            description="Create a new todo item",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Todo title"},
                    "description": {"type": "string", "description": "Todo description"},
                    "category": {"type": "string", "description": "Todo category"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                    "due_date": {"type": "string", "description": "Due date"}
                },
                "required": ["title"]
            }
        )

        # Add other tools...

    async def create_todo(self, **kwargs) -> str:
        """Create a new todo."""
        return await self.todo_internal.create_todo(**kwargs)

    def __iter__(self):
        """Iterate over available todo tools."""
        yield self.create_todo_tool
        # ... yield other tools
```

## 🔗 **Integration Steps**

### **1. Register Tools**

```python
# Update src/personal_assistant/tools/__init__.py
from .todos.todo_tool import TodoTool

def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    # Register todo tools
    todo_tool = TodoTool()
    for tool in todo_tool:
        tool.set_category("Todos")
        registry.register(tool)

    # ... existing tool registrations
```

### **2. API Endpoints**

```python
# Create src/apps/fastapi_app/routes/todos.py
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

@router.post("/")
async def create_todo(todo_data: TodoCreate, current_user = Depends(get_current_user)):
    """Create a new todo."""
    # Implementation here
    pass

@router.get("/")
async def list_todos(current_user = Depends(get_current_user)):
    """List user todos."""
    # Implementation here
    pass
```

## 🧪 **Testing**

### **Unit Tests**

```python
# tests/tools/test_todo_tool.py
import pytest
from src.personal_assistant.tools.todos.todo_tool import TodoTool

@pytest.mark.asyncio
async def test_create_todo():
    todo_tool = TodoTool()
    result = await todo_tool.create_todo(
        title="Test Todo",
        description="Test Description",
        category="work",
        priority="high"
    )
    assert "created successfully" in result.lower()
```

## 📊 **Success Metrics**

- [ ] All CRUD operations working
- [ ] 90%+ test coverage
- [ ] < 200ms response time
- [ ] Natural language SMS interface
- [ ] Web dashboard integration
- [ ] ADHD-friendly features implemented

## 🚨 **Common Issues**

1. **Database Migration**: Ensure backward compatibility
2. **Tool Registration**: Verify tools are properly registered
3. **Error Handling**: Implement comprehensive error handling
4. **Performance**: Optimize database queries
5. **User Experience**: Focus on ADHD-friendly design

---

**Next Steps**: Follow the task checklist for detailed implementation steps.
