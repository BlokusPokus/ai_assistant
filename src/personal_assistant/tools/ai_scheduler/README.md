# AI Scheduler Package

A comprehensive AI task management system with clear separation of concerns across different functional areas.

## 📁 Package Structure

```
ai_scheduler/
├── core/                           # Core business logic
│   ├── __init__.py
│   ├── task_manager.py            # AITaskManager - Database operations
│   ├── scheduler.py               # TaskScheduler - Main orchestrator
│   └── executor.py                # TaskExecutor - Task execution logic
│
├── evaluation/                     # AI evaluation components
│   ├── __init__.py
│   ├── evaluator.py               # AIEventEvaluator - AI-powered evaluation
│   ├── context_builder.py         # EventContext, EventContextBuilder
│   └── task_evaluator.py          # TaskEvaluator - Task-specific evaluation
│
├── notifications/                  # Notification system
│   ├── __init__.py
│   └── service.py                 # NotificationService - SMS, email, in-app
│
├── utils/                         # Utility functions and helpers
│   ├── __init__.py
│   └── helpers.py                 # Convenience functions (set_reminder, etc.)
│
├── __init__.py                    # Main package exports
└── README.md                      # This documentation
```

## 🎯 Core Components

### **core/** - Core Business Logic

#### `task_manager.py` - AITaskManager
- **Purpose**: Central database operations for AI tasks
- **Key Functions**:
  - `create_task()` - Create new AI tasks
  - `get_due_tasks()` - Retrieve tasks ready for execution
  - `update_task()` - Update task properties
  - `delete_task()` - Remove tasks
  - `create_reminder_with_validation()` - Create reminders with validation

#### `scheduler.py` - TaskScheduler
- **Purpose**: Main orchestrator for the AI task system
- **Key Functions**:
  - `start_worker()` - Start Celery workers
  - `start_beat()` - Start periodic scheduling
  - `get_status()` - System health monitoring
  - `get_task_statistics()` - Performance metrics

#### `executor.py` - TaskExecutor
- **Purpose**: Execute AI tasks using the AI assistant
- **Key Functions**:
  - `execute_task()` - Run individual tasks
  - `handle_task_completion()` - Process task results

### **evaluation/** - AI Evaluation Components

#### `evaluator.py` - AIEventEvaluator
- **Purpose**: AI-powered evaluation of calendar events
- **Key Functions**:
  - `evaluate_event()` - Determine if events need attention
  - `analyze_recurrence_pattern()` - Understand recurring patterns
  - `suggest_actions_for_event()` - Generate action recommendations

#### `context_builder.py` - EventContext & EventContextBuilder
- **Purpose**: Build rich context for AI evaluation
- **Key Functions**:
  - `build_event_context()` - Create comprehensive event context
  - `create_ai_context()` - Format context for AI processing

#### `task_evaluator.py` - TaskEvaluator
- **Purpose**: Evaluate individual tasks for processing
- **Key Functions**:
  - `evaluate_task()` - Assess task readiness
  - `should_process_task()` - Decision logic for task processing

### **notifications/** - Notification System

#### `service.py` - NotificationService
- **Purpose**: Handle all notification types
- **Key Functions**:
  - `send_notification()` - Send SMS, email, or in-app notifications
  - `format_message()` - Format messages for different channels

### **utils/** - Utility Functions

#### `helpers.py` - Convenience Functions
- **Purpose**: Easy-to-use functions for common operations
- **Key Functions**:
  - `set_reminder()` - Quick reminder creation
  - `list_reminders()` - List user reminders
  - `delete_reminder()` - Remove reminders

## 🚀 Usage Examples

### Basic Task Management

```python
from personal_assistant.tools.ai_scheduler import AITaskManager

# Create a task manager
task_manager = AITaskManager()

# Create a new task
task = await task_manager.create_task(
    user_id=126,
    title="Meeting reminder",
    description="Don't forget the team meeting",
    task_type="reminder",
    schedule_type="once",
    schedule_config={"run_at": "2025-09-08 10:00:00"},
    next_run_at=datetime(2025, 9, 8, 10, 0),
    notification_channels=["sms"]
)
```

### Using the Scheduler

```python
from personal_assistant.tools.ai_scheduler import TaskScheduler

# Create and start the scheduler
scheduler = TaskScheduler()
scheduler.start_worker()  # Start background workers
scheduler.start_beat()    # Start periodic scheduling

# Check system status
status = scheduler.get_status()
print(f"Scheduler status: {status['status']}")
```

### Quick Reminder Operations

```python
from personal_assistant.tools.ai_scheduler import set_reminder, list_reminders

# Set a quick reminder
await set_reminder("Call mom", "in 1 hour", "sms", user_id=126)

# List active reminders
reminders = await list_reminders("active", user_id=126)
print(reminders)
```

### AI Event Evaluation

```python
from personal_assistant.tools.ai_scheduler import AIEventEvaluator

# Create evaluator with agent core
evaluator = AIEventEvaluator(agent_core)

# Evaluate an event
result = await evaluator.evaluate_event(event)
if result['should_process']:
    print(f"Event needs attention: {result['reason']}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Redis (for Celery)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Scheduler
SCHEDULER_CHECK_INTERVAL=10  # minutes
EVENT_TIME_WINDOW=2  # hours to look ahead
```

## 📊 System Architecture

```mermaid
graph TD
    A[TaskScheduler] --> B[AITaskManager]
    A --> C[Celery Workers]
    A --> D[Beat Scheduler]
    
    B --> E[Database]
    C --> F[TaskExecutor]
    F --> G[AI Assistant]
    
    H[AIEventEvaluator] --> I[EventContextBuilder]
    H --> J[AgentCore]
    
    K[NotificationService] --> L[SMS]
    K --> M[Email]
    K --> N[In-App]
```

## 🧪 Testing

### Run Tests

```bash
# Test the scheduler
python -m personal_assistant.tools.ai_scheduler.core.scheduler test

# Test task creation
python -c "
import asyncio
from personal_assistant.tools.ai_scheduler import AITaskManager
async def test():
    manager = AITaskManager()
    result = await manager.create_task(...)
    print(result)
asyncio.run(test())
"
```

## 🔄 Migration from Old Structure

The package has been reorganized for better clarity:

- **Old**: `ai_task_manager.py` → **New**: `core/task_manager.py`
- **Old**: `task_scheduler.py` → **New**: `core/scheduler.py`
- **Old**: `ai_evaluator.py` → **New**: `evaluation/evaluator.py`
- **Old**: `notification_service.py` → **New**: `notifications/service.py`

All imports have been updated to use the new structure.

## 📈 Benefits of New Structure

1. **Clear Separation of Concerns** - Each folder has a specific purpose
2. **Better Maintainability** - Easier to find and modify specific functionality
3. **Improved Scalability** - Easy to add new components in appropriate folders
4. **Cleaner Imports** - More intuitive import paths
5. **Better Documentation** - Clear structure makes it easier to understand
6. **Reduced Coupling** - Components are more loosely coupled

## 🚨 Breaking Changes

- Import paths have changed (see migration guide above)
- Some convenience functions moved to `utils/` folder
- Dead code removed (`ai_task_scheduler.py`)

## 🤝 Contributing

When adding new components:

1. **Core logic** → `core/` folder
2. **AI evaluation** → `evaluation/` folder  
3. **Notifications** → `notifications/` folder
4. **Utilities** → `utils/` folder

Update the appropriate `__init__.py` file to export new components.