# AI Todo System - Clarity and Stability in Python

## Overview

This document explains how we ensure clarity and stability in the AI todo management system, specifically focusing on Python implementation patterns, error handling, and best practices for maintaining system reliability.

## Clarity Mechanisms

### 1. Clear Task Breakdown with Type Hints

```python
from typing import List, Dict, Optional, Literal, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class TodoStatus(Enum):
    """Clear enumeration of possible todo states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class AITodo:
    """Clear data structure with explicit types"""
    id: str
    content: str
    status: TodoStatus
    dependencies: List[str]
    auto_generated: bool = True
    complexity_score: int = 0
    parallel_executable: bool = False
    parent_request_id: Optional[str] = None
    ai_session_id: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Ensure required fields are set"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if not self.ai_session_id:
            raise ValueError("ai_session_id is required")
```

### 2. Explicit Status Management

```python
class TodoStatusManager:
    """Centralized status management with clear transitions"""

    VALID_TRANSITIONS = {
        TodoStatus.PENDING: [TodoStatus.IN_PROGRESS, TodoStatus.CANCELLED],
        TodoStatus.IN_PROGRESS: [TodoStatus.COMPLETED, TodoStatus.CANCELLED],
        TodoStatus.COMPLETED: [],  # Terminal state
        TodoStatus.CANCELLED: []  # Terminal state
    }

    @classmethod
    def can_transition(cls, from_status: TodoStatus, to_status: TodoStatus) -> bool:
        """Check if status transition is valid"""
        return to_status in cls.VALID_TRANSITIONS.get(from_status, [])

    @classmethod
    def validate_transition(cls, todo: AITodo, new_status: TodoStatus) -> None:
        """Validate and raise exception if transition is invalid"""
        if not cls.can_transition(todo.status, new_status):
            raise ValueError(
                f"Invalid transition from {todo.status.value} to {new_status.value}"
            )
```

### 3. Clear Dependency Resolution

```python
class DependencyResolver:
    """Clear dependency resolution with comprehensive error handling"""

    def __init__(self, todo_service: 'AITodoService'):
        self.todo_service = todo_service
        self._resolution_cache: Dict[str, List[str]] = {}

    async def resolve_dependencies(self, todo_id: str) -> List[str]:
        """Resolve all dependencies for a given todo with caching"""
        if todo_id in self._resolution_cache:
            return self._resolution_cache[todo_id]

        todo = self.todo_service.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")

        resolved = []
        for dep_id in todo.dependencies:
            dep_todo = self.todo_service.get_todo(dep_id)
            if not dep_todo:
                raise ValueError(f"Dependency {dep_id} not found")

            if dep_todo.status == TodoStatus.COMPLETED:
                resolved.append(dep_id)
            else:
                # Recursively resolve dependencies
                sub_deps = await self.resolve_dependencies(dep_id)
                resolved.extend(sub_deps)

        self._resolution_cache[todo_id] = resolved
        return resolved

    async def check_circular_dependencies(self, todo_id: str, visited: set = None) -> bool:
        """Check for circular dependencies"""
        if visited is None:
            visited = set()

        if todo_id in visited:
            return True  # Circular dependency detected

        visited.add(todo_id)
        todo = self.todo_service.get_todo(todo_id)

        for dep_id in todo.dependencies:
            if await self.check_circular_dependencies(dep_id, visited.copy()):
                return True

        return False
```

## Stability Mechanisms

### 1. Atomic Operations with Context Managers

```python
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class AITodoService:
    """Service with atomic operations and proper error handling"""

    def __init__(self):
        self.todos: Dict[str, AITodo] = {}
        self.session_todos: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()
        self.dependency_resolver = DependencyResolver(self)

    @asynccontextmanager
    async def atomic_operation(self) -> AsyncGenerator[None, None]:
        """Context manager for atomic operations"""
        async with self._lock:
            try:
                yield
            except Exception as e:
                # Log error and re-raise
                logger.error(f"Atomic operation failed: {e}")
                raise

    async def create_todo(self, todo_data: dict) -> AITodo:
        """Create todo with atomic operation and validation"""
        async with self.atomic_operation():
            # Validate input data
            self._validate_todo_data(todo_data)

            # Create todo
            todo = AITodo(
                id=str(uuid.uuid4()),
                content=todo_data['content'],
                status=TodoStatus.PENDING,
                dependencies=todo_data.get('dependencies', []),
                complexity_score=todo_data.get('complexity_score', 0),
                parallel_executable=todo_data.get('parallel_executable', False),
                parent_request_id=todo_data.get('parent_request_id'),
                ai_session_id=todo_data['ai_session_id']
            )

            # Check for circular dependencies
            if await self.dependency_resolver.check_circular_dependencies(todo.id):
                raise ValueError(f"Circular dependency detected for todo {todo.id}")

            # Store todo
            self.todos[todo.id] = todo
            if todo.ai_session_id not in self.session_todos:
                self.session_todos[todo.ai_session_id] = []
            self.session_todos[todo.ai_session_id].append(todo.id)

            # Notify clients
            await self._notify_todo_created(todo)

            return todo

    def _validate_todo_data(self, todo_data: dict) -> None:
        """Validate todo data with clear error messages"""
        required_fields = ['content', 'ai_session_id']
        for field in required_fields:
            if field not in todo_data:
                raise ValueError(f"Missing required field: {field}")

        if not todo_data['content'].strip():
            raise ValueError("Todo content cannot be empty")

        if not todo_data['ai_session_id'].strip():
            raise ValueError("AI session ID cannot be empty")

        # Validate dependencies exist
        for dep_id in todo_data.get('dependencies', []):
            if dep_id not in self.todos:
                raise ValueError(f"Dependency {dep_id} not found")
```

### 2. Robust Error Handling

```python
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def handle_errors(func: Callable) -> Callable:
    """Decorator for consistent error handling"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise
        except KeyError as e:
            logger.error(f"Key error in {func.__name__}: {e}")
            raise ValueError(f"Missing required data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise

    return wrapper

class AITodoService:
    """Service with comprehensive error handling"""

    @handle_errors
    async def update_status(self, todo_id: str, status: str) -> AITodo:
        """Update todo status with error handling"""
        async with self.atomic_operation():
            todo = self.get_todo(todo_id)
            if not todo:
                raise ValueError(f"Todo {todo_id} not found")

            # Validate status transition
            new_status = TodoStatus(status)
            TodoStatusManager.validate_transition(todo, new_status)

            # Update status
            old_status = todo.status
            todo.status = new_status
            todo.updated_at = datetime.now()

            if new_status == TodoStatus.COMPLETED:
                todo.completed_at = datetime.now()

            # Notify clients
            await self._notify_todo_updated(todo, old_status)

            return todo

    def get_todo(self, todo_id: str) -> Optional[AITodo]:
        """Get todo with proper error handling"""
        return self.todos.get(todo_id)

    def get_todos_by_session(self, session_id: str) -> List[AITodo]:
        """Get todos by session with validation"""
        if not session_id:
            raise ValueError("Session ID cannot be empty")

        if session_id not in self.session_todos:
            return []

        todos = []
        for todo_id in self.session_todos[session_id]:
            todo = self.todos.get(todo_id)
            if todo:
                todos.append(todo)
            else:
                logger.warning(f"Todo {todo_id} not found in session {session_id}")

        return todos
```

### 3. Session Management and Cleanup

```python
class SessionManager:
    """Manage AI sessions with proper cleanup"""

    def __init__(self, todo_service: AITodoService):
        self.todo_service = todo_service
        self.active_sessions: Dict[str, datetime] = {}
        self.session_timeout = timedelta(hours=24)  # 24 hour timeout

    async def create_session(self, session_id: str) -> None:
        """Create new session with validation"""
        if not session_id:
            raise ValueError("Session ID cannot be empty")

        if session_id in self.active_sessions:
            logger.warning(f"Session {session_id} already exists")

        self.active_sessions[session_id] = datetime.now()
        logger.info(f"Created session {session_id}")

    async def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        now = datetime.now()
        expired_sessions = []

        for session_id, created_at in self.active_sessions.items():
            if now - created_at > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            await self.clear_session(session_id)
            logger.info(f"Cleaned up expired session {session_id}")

    async def clear_session(self, session_id: str) -> None:
        """Clear session with proper cleanup"""
        async with self.todo_service.atomic_operation():
            if session_id in self.todo_service.session_todos:
                # Clear all todos for this session
                for todo_id in self.todo_service.session_todos[session_id]:
                    if todo_id in self.todo_service.todos:
                        del self.todo_service.todos[todo_id]

                del self.todo_service.session_todos[session_id]

            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            logger.info(f"Cleared session {session_id}")
```

### 4. Memory Management and Monitoring

```python
import psutil
import gc
from typing import Dict, Any

class MemoryMonitor:
    """Monitor memory usage and prevent leaks"""

    def __init__(self):
        self.initial_memory = psutil.Process().memory_info().rss
        self.memory_threshold = 100 * 1024 * 1024  # 100MB threshold

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'initial_memory': self.initial_memory,
            'growth': memory_info.rss - self.initial_memory
        }

    def check_memory_threshold(self) -> bool:
        """Check if memory usage exceeds threshold"""
        current_memory = psutil.Process().memory_info().rss
        return current_memory > self.memory_threshold

    def force_garbage_collection(self) -> None:
        """Force garbage collection to free memory"""
        gc.collect()
        logger.info("Forced garbage collection")

class AITodoService:
    """Service with memory monitoring"""

    def __init__(self):
        self.todos: Dict[str, AITodo] = {}
        self.session_todos: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()
        self.memory_monitor = MemoryMonitor()
        self.dependency_resolver = DependencyResolver(self)

    async def periodic_cleanup(self) -> None:
        """Periodic cleanup to prevent memory leaks"""
        if self.memory_monitor.check_memory_threshold():
            logger.warning("Memory usage exceeds threshold, performing cleanup")

            # Clear old sessions
            await self._cleanup_old_sessions()

            # Force garbage collection
            self.memory_monitor.force_garbage_collection()

            # Log memory usage
            memory_stats = self.memory_monitor.get_memory_usage()
            logger.info(f"Memory usage after cleanup: {memory_stats}")

    async def _cleanup_old_sessions(self) -> None:
        """Clean up old sessions to free memory"""
        cutoff_time = datetime.now() - timedelta(hours=1)

        for session_id, todos in list(self.session_todos.items()):
            if todos:
                first_todo = self.todos.get(todos[0])
                if first_todo and first_todo.created_at < cutoff_time:
                    await self.clear_session(session_id)
```

### 5. Parallel Execution Safety

```python
class ParallelExecutor:
    """Safe parallel execution of independent tasks"""

    def __init__(self, todo_service: AITodoService):
        self.todo_service = todo_service
        self.max_concurrent = 5  # Maximum concurrent tasks

    async def can_execute_parallel(self, todo_ids: List[str]) -> bool:
        """Check if todos can execute in parallel safely"""
        for todo_id in todo_ids:
            todo = self.todo_service.get_todo(todo_id)
            if not todo or not todo.parallel_executable:
                return False

            # Check if all dependencies are completed
            resolved_deps = await self.todo_service.dependency_resolver.resolve_dependencies(todo_id)
            if len(resolved_deps) != len(todo.dependencies):
                return False

        return True

    async def execute_parallel(self, todo_ids: List[str]) -> List[AITodo]:
        """Execute todos in parallel with proper error handling"""
        if not await self.can_execute_parallel(todo_ids):
            raise ValueError("Todos cannot be executed in parallel")

        # Limit concurrent execution
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def execute_single(todo_id: str) -> AITodo:
            async with semaphore:
                return await self.todo_service.update_status(todo_id, TodoStatus.IN_PROGRESS.value)

        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[execute_single(todo_id) for todo_id in todo_ids],
            return_exceptions=True
        )

        # Handle any exceptions
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {todo_ids[i]} failed: {result}")
            else:
                successful_results.append(result)

        return successful_results
```

## Testing for Stability

### 1. Unit Tests with Proper Assertions

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

class TestAITodoService:
    """Comprehensive unit tests for stability"""

    @pytest.fixture
    async def todo_service(self):
        """Create todo service for testing"""
        service = AITodoService()
        await service.create_session("test_session")
        return service

    @pytest.mark.asyncio
    async def test_create_todo_validation(self, todo_service):
        """Test todo creation with validation"""
        # Test valid todo creation
        todo_data = {
            'content': 'Test todo',
            'ai_session_id': 'test_session',
            'dependencies': [],
            'complexity_score': 1
        }

        todo = await todo_service.create_todo(todo_data)
        assert todo.content == 'Test todo'
        assert todo.status == TodoStatus.PENDING
        assert todo.ai_session_id == 'test_session'

    @pytest.mark.asyncio
    async def test_invalid_todo_creation(self, todo_service):
        """Test invalid todo creation raises proper errors"""
        # Test missing required field
        with pytest.raises(ValueError, match="Missing required field"):
            await todo_service.create_todo({'content': 'Test'})

        # Test empty content
        with pytest.raises(ValueError, match="Todo content cannot be empty"):
            await todo_service.create_todo({
                'content': '',
                'ai_session_id': 'test_session'
            })

    @pytest.mark.asyncio
    async def test_status_transitions(self, todo_service):
        """Test valid and invalid status transitions"""
        todo_data = {
            'content': 'Test todo',
            'ai_session_id': 'test_session'
        }

        todo = await todo_service.create_todo(todo_data)

        # Valid transition: pending -> in_progress
        updated_todo = await todo_service.update_status(todo.id, TodoStatus.IN_PROGRESS.value)
        assert updated_todo.status == TodoStatus.IN_PROGRESS

        # Valid transition: in_progress -> completed
        completed_todo = await todo_service.update_status(todo.id, TodoStatus.COMPLETED.value)
        assert completed_todo.status == TodoStatus.COMPLETED
        assert completed_todo.completed_at is not None

        # Invalid transition: completed -> in_progress
        with pytest.raises(ValueError, match="Invalid transition"):
            await todo_service.update_status(todo.id, TodoStatus.IN_PROGRESS.value)

    @pytest.mark.asyncio
    async def test_dependency_resolution(self, todo_service):
        """Test dependency resolution with circular dependency detection"""
        # Create todos with dependencies
        todo1_data = {'content': 'Todo 1', 'ai_session_id': 'test_session'}
        todo1 = await todo_service.create_todo(todo1_data)

        todo2_data = {
            'content': 'Todo 2',
            'ai_session_id': 'test_session',
            'dependencies': [todo1.id]
        }
        todo2 = await todo_service.create_todo(todo2_data)

        # Test dependency resolution
        resolved_deps = await todo_service.dependency_resolver.resolve_dependencies(todo2.id)
        assert todo1.id in resolved_deps

        # Test circular dependency detection
        todo3_data = {
            'content': 'Todo 3',
            'ai_session_id': 'test_session',
            'dependencies': [todo2.id]
        }
        todo3 = await todo_service.create_todo(todo3_data)

        # Create circular dependency
        todo1.dependencies = [todo3.id]

        with pytest.raises(ValueError, match="Circular dependency detected"):
            await todo_service.dependency_resolver.check_circular_dependencies(todo1.id)

    @pytest.mark.asyncio
    async def test_session_cleanup(self, todo_service):
        """Test session cleanup and memory management"""
        # Create multiple todos
        for i in range(5):
            todo_data = {
                'content': f'Test todo {i}',
                'ai_session_id': 'test_session'
            }
            await todo_service.create_todo(todo_data)

        # Verify todos exist
        todos = todo_service.get_todos_by_session('test_session')
        assert len(todos) == 5

        # Clear session
        await todo_service.clear_session('test_session')

        # Verify todos are cleared
        todos = todo_service.get_todos_by_session('test_session')
        assert len(todos) == 0
```

### 2. Integration Tests

```python
class TestAITodoIntegration:
    """Integration tests for end-to-end functionality"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete todo workflow"""
        service = AITodoService()
        await service.create_session("integration_test")

        # Create todos with dependencies
        todo1 = await service.create_todo({
            'content': 'Setup environment',
            'ai_session_id': 'integration_test'
        })

        todo2 = await service.create_todo({
            'content': 'Install dependencies',
            'ai_session_id': 'integration_test',
            'dependencies': [todo1.id]
        })

        todo3 = await service.create_todo({
            'content': 'Run tests',
            'ai_session_id': 'integration_test',
            'dependencies': [todo2.id]
        })

        # Execute workflow
        await service.update_status(todo1.id, TodoStatus.IN_PROGRESS.value)
        await service.update_status(todo1.id, TodoStatus.COMPLETED.value)

        await service.update_status(todo2.id, TodoStatus.IN_PROGRESS.value)
        await service.update_status(todo2.id, TodoStatus.COMPLETED.value)

        await service.update_status(todo3.id, TodoStatus.IN_PROGRESS.value)
        await service.update_status(todo3.id, TodoStatus.COMPLETED.value)

        # Verify final state
        todos = service.get_todos_by_session('integration_test')
        assert all(todo.status == TodoStatus.COMPLETED for todo in todos)
```

## Best Practices Summary

### 1. **Type Safety**

- Use type hints for all functions and classes
- Use dataclasses for data structures
- Use enums for status values
- Validate input data with clear error messages

### 2. **Error Handling**

- Use decorators for consistent error handling
- Provide clear error messages
- Log errors appropriately
- Fail fast with validation

### 3. **Memory Management**

- Monitor memory usage
- Clean up expired sessions
- Use context managers for atomic operations
- Force garbage collection when needed

### 4. **Concurrency Safety**

- Use locks for atomic operations
- Limit concurrent execution
- Handle exceptions in parallel operations
- Use semaphores for resource management

### 5. **Testing**

- Write comprehensive unit tests
- Test error conditions
- Test edge cases
- Use integration tests for workflows

This approach ensures that the AI todo system is both clear in its operation and stable in its execution, providing a robust foundation for intelligent task management.
