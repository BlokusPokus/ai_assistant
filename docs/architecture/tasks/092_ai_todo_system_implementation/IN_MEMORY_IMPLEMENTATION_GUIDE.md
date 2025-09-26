# AI Todo System - In-Memory Implementation Guide

## Overview

This guide provides detailed implementation instructions for creating an AI todo management system that mirrors the sophisticated todo tracking capabilities used in AI coding assistants. The system will use in-memory storage (no database) and differentiate itself from user todos while providing intelligent task management for the personal assistant.

## Architecture Design

### In-Memory Service Architecture

#### AI Todo Data Structure

```python
from typing import List, Dict, Optional, Literal
from datetime import datetime
import uuid

class AITodo:
    def __init__(self, content: str, ai_session_id: str, **kwargs):
        self.id: str = str(uuid.uuid4())
        self.content: str = content
        self.status: Literal["pending", "in_progress", "completed", "cancelled"] = "pending"
        self.dependencies: List[str] = kwargs.get('dependencies', [])
        self.auto_generated: bool = True
        self.complexity_score: int = kwargs.get('complexity_score', 0)
        self.parallel_executable: bool = kwargs.get('parallel_executable', False)
        self.parent_request_id: Optional[str] = kwargs.get('parent_request_id')
        self.ai_session_id: str = ai_session_id
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.completed_at: Optional[datetime] = None

class AITodoService:
    def __init__(self):
        self.todos: Dict[str, AITodo] = {}
        self.session_todos: Dict[str, List[str]] = {}
        self.websocket_manager = WebSocketManager()

    async def create_todo(self, todo_data: dict) -> AITodo:
        """Create a new AI todo"""
        todo = AITodo(
            content=todo_data['content'],
            ai_session_id=todo_data['ai_session_id'],
            dependencies=todo_data.get('dependencies', []),
            complexity_score=todo_data.get('complexity_score', 0),
            parallel_executable=todo_data.get('parallel_executable', False),
            parent_request_id=todo_data.get('parent_request_id')
        )

        self.todos[todo.id] = todo
        if todo.ai_session_id not in self.session_todos:
            self.session_todos[todo.ai_session_id] = []
        self.session_todos[todo.ai_session_id].append(todo.id)

        await self.websocket_manager.broadcast_to_session(
            todo.ai_session_id,
            {"type": "todo_created", "todo": todo.__dict__}
        )

        return todo

    async def update_status(self, todo_id: str, status: str) -> AITodo:
        """Update todo status and notify clients"""
        if todo_id not in self.todos:
            raise ValueError(f"Todo {todo_id} not found")

        todo = self.todos[todo_id]
        todo.status = status
        todo.updated_at = datetime.now()

        if status == "completed":
            todo.completed_at = datetime.now()

        await self.websocket_manager.broadcast_to_session(
            todo.ai_session_id,
            {"type": "todo_updated", "todo": todo.__dict__}
        )

        return todo

    def get_todos_by_session(self, session_id: str) -> List[AITodo]:
        """Get all todos for a session"""
        if session_id not in self.session_todos:
            return []

        return [self.todos[todo_id] for todo_id in self.session_todos[session_id]]

    async def resolve_dependencies(self, todo_id: str) -> List[str]:
        """Resolve all dependencies for a given todo"""
        todo = self.todos.get(todo_id)
        if not todo:
            return []

        resolved = []
        for dep_id in todo.dependencies:
            dep_todo = self.todos.get(dep_id)
            if dep_todo and dep_todo.status == "completed":
                resolved.append(dep_id)
            else:
                # Recursively resolve dependencies
                resolved.extend(await self.resolve_dependencies(dep_id))

        return resolved

    async def can_execute_parallel(self, todo_ids: List[str]) -> bool:
        """Check if todos can execute in parallel"""
        for todo_id in todo_ids:
            todo = self.todos.get(todo_id)
            if not todo or not todo.parallel_executable:
                return False
            # Check if all dependencies are completed
            deps = await self.resolve_dependencies(todo_id)
            if len(deps) != len(todo.dependencies):
                return False

        return True

    def clear_session(self, session_id: str):
        """Clear all todos for a session"""
        if session_id in self.session_todos:
            for todo_id in self.session_todos[session_id]:
                if todo_id in self.todos:
                    del self.todos[todo_id]
            del self.session_todos[session_id]
```

#### Key Differences from User Todos

- **Session-Based**: Todos exist only for the duration of the AI session
- **Auto Generated**: Created by AI when processing complex requests
- **Dependency Management**: Tasks have prerequisite relationships
- **Parallel Execution**: Independent tasks can run simultaneously
- **Real-time Updates**: Status changes happen immediately
- **No Persistence**: Todos are not saved to database

### Backend Service Design

#### AI Todo Service Implementation

```python
# AI Todo Management Service
class AITodoService:
    def __init__(self):
        self.todos: Dict[str, AITodo] = {}
        self.session_todos: Dict[str, List[str]] = {}
        self.websocket_manager = WebSocketManager()

    async def create_todo(self, todo_data: dict) -> AITodo:
        """Create a new AI todo"""
        todo = AITodo(
            content=todo_data['content'],
            ai_session_id=todo_data['ai_session_id'],
            dependencies=todo_data.get('dependencies', []),
            complexity_score=todo_data.get('complexity_score', 0),
            parallel_executable=todo_data.get('parallel_executable', False),
            parent_request_id=todo_data.get('parent_request_id')
        )

        self.todos[todo.id] = todo
        if todo.ai_session_id not in self.session_todos:
            self.session_todos[todo.ai_session_id] = []
        self.session_todos[todo.ai_session_id].append(todo.id)

        await self.websocket_manager.broadcast_to_session(
            todo.ai_session_id,
            {"type": "todo_created", "todo": todo.__dict__}
        )

        return todo

    async def update_status(self, todo_id: str, status: str) -> AITodo:
        """Update todo status and notify clients"""
        if todo_id not in self.todos:
            raise ValueError(f"Todo {todo_id} not found")

        todo = self.todos[todo_id]
        todo.status = status
        todo.updated_at = datetime.now()

        if status == "completed":
            todo.completed_at = datetime.now()

        await self.websocket_manager.broadcast_to_session(
            todo.ai_session_id,
            {"type": "todo_updated", "todo": todo.__dict__}
        )

        return todo

    def get_todos_by_session(self, session_id: str) -> List[AITodo]:
        """Get all todos for a session"""
        if session_id not in self.session_todos:
            return []

        return [self.todos[todo_id] for todo_id in self.session_todos[session_id]]
```

### Frontend Component Architecture

#### AI Todo Dashboard

```typescript
// AITodoDashboard.tsx
interface AITodoDashboardProps {
  sessionId: string;
  showDependencies?: boolean;
  showParallelExecution?: boolean;
}

const AITodoDashboard: React.FC<AITodoDashboardProps> = ({
  sessionId,
  showDependencies = true,
  showParallelExecution = true,
}) => {
  const [todos, setTodos] = useState<AITodo[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`/ws/ai-todos/${sessionId}`);

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "todo_created" || data.type === "todo_updated") {
        setTodos((prev) => {
          const existing = prev.find((t) => t.id === data.todo.id);
          if (existing) {
            return prev.map((t) => (t.id === data.todo.id ? data.todo : t));
          } else {
            return [...prev, data.todo];
          }
        });
      }
    };

    return () => ws.close();
  }, [sessionId]);

  return (
    <div className="ai-todo-dashboard">
      <div className="dashboard-header">
        <h2>AI Task Progress</h2>
        <div
          className={`connection-status ${
            isConnected ? "connected" : "disconnected"
          }`}
        >
          {isConnected ? "Connected" : "Disconnected"}
        </div>
      </div>

      <AITodoList
        todos={todos}
        showDependencies={showDependencies}
        showParallelExecution={showParallelExecution}
      />
    </div>
  );
};
```

#### AI Todo List Component

```typescript
// AITodoList.tsx
interface AITodoListProps {
  todos: AITodo[];
  showDependencies?: boolean;
  showParallelExecution?: boolean;
}

const AITodoList: React.FC<AITodoListProps> = ({
  todos,
  showDependencies = true,
  showParallelExecution = true,
}) => {
  const pendingTodos = todos.filter((t) => t.status === "pending");
  const inProgressTodos = todos.filter((t) => t.status === "in_progress");
  const completedTodos = todos.filter((t) => t.status === "completed");

  return (
    <div className="ai-todo-list">
      <div className="todo-section">
        <h3>In Progress ({inProgressTodos.length})</h3>
        {inProgressTodos.map((todo) => (
          <AITodoItem
            key={todo.id}
            todo={todo}
            showDependencies={showDependencies}
            showParallelExecution={showParallelExecution}
          />
        ))}
      </div>

      <div className="todo-section">
        <h3>Pending ({pendingTodos.length})</h3>
        {pendingTodos.map((todo) => (
          <AITodoItem
            key={todo.id}
            todo={todo}
            showDependencies={showDependencies}
            showParallelExecution={showParallelExecution}
          />
        ))}
      </div>

      <div className="todo-section">
        <h3>Completed ({completedTodos.length})</h3>
        {completedTodos.map((todo) => (
          <AITodoItem
            key={todo.id}
            todo={todo}
            showDependencies={showDependencies}
            showParallelExecution={showParallelExecution}
          />
        ))}
      </div>
    </div>
  );
};
```

#### AI Todo Item Component

```typescript
// AITodoItem.tsx
interface AITodoItemProps {
  todo: AITodo;
  showDependencies?: boolean;
  showParallelExecution?: boolean;
}

const AITodoItem: React.FC<AITodoItemProps> = ({
  todo,
  showDependencies = true,
  showParallelExecution = true,
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return "⏳";
      case "in_progress":
        return "🔄";
      case "completed":
        return "✅";
      case "cancelled":
        return "❌";
      default:
        return "❓";
    }
  };

  return (
    <div
      className={`ai-todo-item ${todo.status} ${
        todo.parallel_executable ? "parallel" : ""
      }`}
    >
      <div className="todo-header">
        <span className="status-icon">{getStatusIcon(todo.status)}</span>
        <span className="todo-content">{todo.content}</span>
        {showParallelExecution && todo.parallel_executable && (
          <span className="parallel-badge">Parallel</span>
        )}
      </div>

      {showDependencies && todo.dependencies.length > 0 && (
        <div className="dependencies">
          <span className="dependency-label">Depends on:</span>
          <span className="dependency-count">
            {todo.dependencies.length} tasks
          </span>
        </div>
      )}

      <div className="todo-meta">
        <span className="complexity-score">
          Complexity: {todo.complexity_score}
        </span>
        <span className="created-at">
          {new Date(todo.created_at).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};
```

## Implementation Steps

### Phase 1: Service Setup

1. Create AI todo service class
2. Implement in-memory storage
3. Add WebSocket integration
4. Test service operations

### Phase 2: Backend Development

1. Implement AI todo data models
2. Create service methods for CRUD operations
3. Add dependency resolution logic
4. Implement parallel execution support
5. Add real-time status update via WebSocket

### Phase 3: Frontend Development

1. Create AI todo dashboard component
2. Implement dependency visualization
3. Add real-time status updates
4. Create AI-specific styling
5. Integrate with existing todo interface

### Phase 4: Integration

1. Connect AI todo system with personal assistant workflow
2. Implement automatic todo creation for complex requests
3. Add AI session management
4. Test end-to-end functionality

## Key Features Implementation

### Dependency Management

```python
async def resolve_dependencies(todo_id: str) -> List[str]:
    """Resolve all dependencies for a given todo"""
    todo = self.todos.get(todo_id)
    if not todo:
        return []

    resolved = []
    for dep_id in todo.dependencies:
        dep_todo = self.todos.get(dep_id)
        if dep_todo and dep_todo.status == "completed":
            resolved.append(dep_id)
        else:
            # Recursively resolve dependencies
            resolved.extend(await self.resolve_dependencies(dep_id))

    return resolved

async def can_execute_parallel(self, todo_ids: List[str]) -> bool:
    """Check if todos can execute in parallel"""
    for todo_id in todo_ids:
        todo = self.todos.get(todo_id)
        if not todo or not todo.parallel_executable:
            return False
        # Check if all dependencies are completed
        deps = await self.resolve_dependencies(todo_id)
        if len(deps) != len(todo.dependencies):
            return False

    return True
```

### Real-time Status Updates

```typescript
// WebSocket integration for real-time updates
const useAITodoUpdates = (sessionId: string) => {
  const [todos, setTodos] = useState<AITodo[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`/ws/ai-todos/${sessionId}`);

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "todo_created" || data.type === "todo_updated") {
        setTodos((prev) => {
          const existing = prev.find((t) => t.id === data.todo.id);
          if (existing) {
            return prev.map((t) => (t.id === data.todo.id ? data.todo : t));
          } else {
            return [...prev, data.todo];
          }
        });
      }
    };

    return () => ws.close();
  }, [sessionId]);

  return { todos, isConnected };
};
```

### Visual Distinction

```css
/* AI Todo Specific Styling */
.ai-todo-item {
  border-left: 4px solid #3b82f6; /* Blue accent for AI todos */
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  margin: 8px 0;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ai-todo-item.parallel-executable {
  border-left-color: #10b981; /* Green for parallel execution */
}

.ai-todo-item.has-dependencies {
  border-left-color: #f59e0b; /* Orange for dependencies */
}

.ai-todo-item.in_progress {
  border-left-color: #3b82f6; /* Blue for in progress */
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.ai-todo-item.completed {
  border-left-color: #10b981; /* Green for completed */
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.ai-todo-complexity {
  display: inline-block;
  padding: 2px 6px;
  background: #3b82f6;
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.ai-todo-dependency-graph {
  margin-top: 8px;
  padding: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.parallel-badge {
  background: #10b981;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.connection-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.connection-status.connected {
  background: #10b981;
  color: white;
}

.connection-status.disconnected {
  background: #ef4444;
  color: white;
}
```

## Testing Strategy

### Unit Tests

- AI todo CRUD operations
- Dependency resolution logic
- Parallel execution validation
- Status update handling

### Integration Tests

- Service functionality
- WebSocket real-time updates
- Frontend component behavior

### End-to-End Tests

- Complete AI todo workflow
- User interaction scenarios
- Performance under load
- Cross-browser compatibility

## Deployment Considerations

### Service Deployment

- Deploy AI todo service
- Configure WebSocket connections
- Set up session management
- Test service reliability

### Frontend Deployment

- Bundle AI todo components
- Optimize for performance
- Test cross-browser compatibility
- Monitor user experience metrics

## Monitoring and Maintenance

### Performance Monitoring

- Service response times
- Memory usage patterns
- Frontend rendering performance
- WebSocket connection stability

### Error Handling

- Graceful degradation
- User-friendly error messages
- Comprehensive logging
- Automated error reporting

### Maintenance Tasks

- Regular service optimization
- Memory usage monitoring
- Component updates
- Documentation updates

## Success Metrics

### Technical Metrics

- Service response times < 200ms
- Memory usage efficiency
- Real-time update latency < 100ms
- Component rendering performance

### User Experience Metrics

- Task completion rate
- User satisfaction scores
- Feature adoption rates
- Error rates and resolution times

### Business Metrics

- AI todo creation frequency
- Dependency resolution accuracy
- Parallel execution efficiency
- System reliability and uptime
