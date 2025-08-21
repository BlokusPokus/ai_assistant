# Task 037: General-Purpose Background Task System Implementation

## **📋 Task Overview**

**Task ID**: 037  
**Task Name**: General-Purpose Background Task System Implementation  
**Phase**: 2.3 - API & Backend Services  
**Module**: 2.3.2 - Background Task System  
**Status**: 🚀 **READY TO START**  
**Target Start Date**: January 2025  
**Effort Estimate**: 5 days  
**Dependencies**: Task 036 (User Management API) ✅ **COMPLETED**

## **🎯 Task Objectives**

### **Component 1: General-Purpose Background Task System (Task 2.3.2.1)**

Transform the current AI-specific scheduler into a comprehensive background task system that provides:

- **Separation of Concerns**: Decouple AI tasks from general background tasks
- **Modular Architecture**: Separate modules for different task types
- **Scalable Worker System**: Different worker types for different workloads
- **Centralized Task Management**: Unified Celery application with task routing
- **Enhanced Monitoring**: Task-specific metrics and monitoring

### **Component 2: Task Type Implementation (Task 2.3.2.2)**

Implement various background task types beyond AI scheduling:

- **Email Processing Tasks**: Email queue processing, categorization, notifications
- **File Management Tasks**: Cleanup, backup, synchronization
- **Data Processing Tasks**: Report generation, data aggregation
- **API Synchronization Tasks**: External API sync, conflict resolution
- **System Maintenance Tasks**: Log cleanup, performance optimization

## **🔍 Current State Analysis**

### **Existing Implementation (What We Have)**

```
src/personal_assistant/tools/ai_scheduler/
├── celery_config.py          # AI-specific Celery config
├── ai_task_scheduler.py      # AI task processing logic
├── task_executor.py          # AI task execution
├── task_scheduler.py         # AI scheduler management
└── README.md                 # AI scheduler documentation
```

**Current Capabilities**:

- ✅ Celery + Redis integration working
- ✅ AI task scheduling functional (every 10 minutes)
- ✅ AI task execution with full tool access
- ✅ Docker containerization ready
- ✅ Error handling and monitoring

**Current Limitations**:

- ❌ **Scope Limited**: Only AI-specific tasks
- ❌ **Tightly Coupled**: All logic mixed in one module
- ❌ **Hard to Extend**: Adding new task types requires modifying AI scheduler
- ❌ **Resource Management**: Single worker type for all tasks

### **Target Implementation (What We Want)**

```
src/personal_assistant/workers/
├── celery_app.py             # Central Celery application
├── tasks/
│   ├── ai_tasks.py           # AI task processing (moved from tools/)
│   ├── email_tasks.py        # Email processing tasks
│   ├── file_tasks.py         # File management tasks
│   ├── sync_tasks.py         # API synchronization tasks
│   ├── maintenance_tasks.py  # System maintenance tasks
│   └── __init__.py           # Task registry
├── schedulers/
│   ├── ai_scheduler.py       # AI task scheduling logic
│   ├── email_scheduler.py    # Email task scheduling
│   ├── maintenance_scheduler.py # System maintenance timing
│   └── __init__.py           # Scheduler registry
├── utils/
│   ├── task_monitoring.py    # Task monitoring utilities
│   ├── error_handling.py     # Centralized error handling
│   └── metrics.py            # Task-specific metrics
└── __init__.py               # Worker system initialization
```

## **📊 Implementation Plan**

### **Phase 1: Reorganize Current Code (Day 1)**

1. **Create New Directory Structure**

   ```bash
   mkdir -p src/personal_assistant/workers/{tasks,schedulers,utils}
   ```

2. **Move and Refactor AI Scheduler**

   - Move `tools/ai_scheduler/` → `workers/tasks/ai_tasks.py`
   - Extract scheduling logic to `workers/schedulers/ai_scheduler.py`
   - Update imports and references

3. **Create Central Celery Application**
   - Rename `celery_config.py` → `celery_app.py`
   - Move to `workers/celery_app.py`
   - Update task routing for new structure

### **Phase 2: Implement New Task Types (Days 2-3)**

1. **Email Processing Tasks**

   ```python
   # workers/tasks/email_tasks.py
   @celery_app.task
   def process_email_queue():
       """Process email queue every 5 minutes"""
       pass

   @celery_app.task
   def send_daily_email_summary():
       """Send daily email digest at 8 AM"""
       pass
   ```

2. **File Management Tasks**

   ```python
   # workers/tasks/file_tasks.py
   @celery_app.task
   def cleanup_temp_files():
       """Clean temporary files daily"""
       pass

   @celery_app.task
   def backup_user_data():
       """Backup user data weekly"""
       pass
   ```

3. **API Synchronization Tasks**

   ```python
   # workers/tasks/sync_tasks.py
   @celery_app.task
   def sync_calendar_events():
       """Sync calendar with external APIs every hour"""
       pass

   @celery_app.task
   def sync_notion_pages():
       """Sync Notion pages every 2 hours"""
       pass
   ```

4. **System Maintenance Tasks**

   ```python
   # workers/tasks/maintenance_tasks.py
   @celery_app.task
   def cleanup_old_logs():
       """Clean old log files daily"""
       pass

   @celery_app.task
   def optimize_database():
       """Run database optimization weekly"""
       pass
   ```

### **Phase 3: Enhanced Scheduling and Monitoring (Day 4)**

1. **Separate Schedulers**

   - Move AI scheduling logic to dedicated module
   - Create separate schedulers for different task types
   - Implement task-specific timing and frequency

2. **Enhanced Monitoring**

   - Task-specific metrics collection
   - Performance monitoring per task type
   - Error tracking and alerting

3. **Resource Management**
   - Different worker types for different workloads
   - Queue-based task routing
   - Priority-based task execution

### **Phase 4: Testing and Integration (Day 5)**

1. **Unit Testing**

   - Test each task type independently
   - Mock external dependencies
   - Validate task execution flow

2. **Integration Testing**

   - Test task scheduling and execution
   - Validate worker coordination
   - Test error handling and recovery

3. **Docker Integration**
   - Update Docker Compose files
   - Test worker scaling
   - Validate monitoring integration

## **✅ Acceptance Criteria**

### **Functional Requirements**

- ✅ **Task Separation**: AI tasks, email tasks, file tasks, sync tasks, maintenance tasks
- ✅ **Modular Architecture**: Each task type in its own module
- ✅ **Centralized Management**: Single Celery application with task routing
- ✅ **Enhanced Scheduling**: Separate schedulers for different task types
- ✅ **Resource Optimization**: Different worker types for different workloads

### **Technical Requirements**

- ✅ **Code Organization**: Clean separation of concerns
- ✅ **Error Handling**: Centralized error handling for all task types
- ✅ **Monitoring**: Task-specific metrics and monitoring
- ✅ **Testing**: Comprehensive test coverage for all task types
- ✅ **Documentation**: Clear documentation for each task type

### **Performance Requirements**

- ✅ **Scalability**: Support for multiple worker types
- ✅ **Resource Efficiency**: Optimized resource usage per task type
- ✅ **Monitoring**: Real-time task performance metrics
- ✅ **Error Recovery**: Graceful error handling and retry mechanisms

## **🔧 Technical Implementation Details**

### **Celery Configuration Updates**

```python
# workers/celery_app.py
app = Celery(
    'personal_assistant_workers',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Task routing for different task types
app.conf.task_routes = {
    'personal_assistant.workers.tasks.ai_tasks.*': {'queue': 'ai_tasks'},
    'personal_assistant.workers.tasks.email_tasks.*': {'queue': 'email_tasks'},
    'personal_assistant.workers.tasks.file_tasks.*': {'queue': 'file_tasks'},
    'personal_assistant.workers.tasks.sync_tasks.*': {'queue': 'sync_tasks'},
    'personal_assistant.workers.tasks.maintenance_tasks.*': {'queue': 'maintenance_tasks'},
}

# Beat schedule for different task types
app.conf.beat_schedule = {
    # AI tasks (existing)
    'process-due-ai-tasks': {
        'task': 'personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks',
        'schedule': crontab(minute='*/10'),
    },

    # Email tasks (new)
    'process-email-queue': {
        'task': 'personal_assistant.workers.tasks.email_tasks.process_email_queue',
        'schedule': crontab(minute='*/5'),
    },

    # File tasks (new)
    'cleanup-temp-files': {
        'task': 'personal_assistant.workers.tasks.file_tasks.cleanup_temp_files',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },

    # Sync tasks (new)
    'sync-calendar-events': {
        'task': 'personal_assistant.workers.tasks.sync_tasks.sync_calendar_events',
        'schedule': crontab(minute=0),  # Every hour
    },

    # Maintenance tasks (new)
    'cleanup-old-logs': {
        'task': 'personal_assistant.workers.tasks.maintenance_tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}
```

### **Docker Configuration Updates**

```yaml
# docker/docker-compose.prod.yml
services:
  # AI Task Worker
  ai_worker:
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=ai_tasks",
        "--concurrency=1",
      ]

  # Email Task Worker
  email_worker:
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=email_tasks",
        "--concurrency=4",
      ]

  # File Task Worker
  file_worker:
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=file_tasks",
        "--concurrency=2",
      ]

  # Sync Task Worker
  sync_worker:
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=sync_tasks",
        "--concurrency=2",
      ]

  # Maintenance Task Worker
  maintenance_worker:
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=maintenance_tasks",
        "--concurrency=1",
      ]
```

## **📈 Expected Benefits**

### **Architectural Improvements**

- **Separation of Concerns**: Each task type has its own module
- **Modularity**: Easy to add new task types without touching existing code
- **Maintainability**: Smaller, focused modules are easier to maintain
- **Testability**: Each task type can be tested independently

### **Operational Improvements**

- **Resource Optimization**: Different worker types for different workloads
- **Scalability**: Scale workers independently based on demand
- **Monitoring**: Task-specific metrics and performance tracking
- **Error Isolation**: Errors in one task type don't affect others

### **Development Improvements**

- **Code Reusability**: Common utilities shared across task types
- **Consistent Patterns**: Standardized approach for all background tasks
- **Easy Extension**: Simple template for adding new task types
- **Better Debugging**: Clear separation makes issues easier to identify

## **🚨 Risk Mitigation**

### **Migration Risks**

- **Breaking Changes**: Ensure backward compatibility during migration
- **Data Loss**: Backup current AI task data before migration
- **Service Disruption**: Plan migration during low-usage periods

### **Technical Risks**

- **Performance Impact**: Monitor performance during transition
- **Resource Usage**: Validate resource allocation for new worker types
- **Error Handling**: Ensure robust error handling in new system

## **📋 Task Checklist**

### **Phase 1: Reorganization**

- [ ] Create new directory structure
- [ ] Move AI scheduler code to new location
- [ ] Update imports and references
- [ ] Create central Celery application

### **Phase 2: New Task Types**

- [ ] Implement email processing tasks
- [ ] Implement file management tasks
- [ ] Implement API synchronization tasks
- [ ] Implement system maintenance tasks

### **Phase 3: Enhanced Features**

- [ ] Separate schedulers for different task types
- [ ] Implement task-specific monitoring
- [ ] Add resource management features
- [ ] Update task routing configuration

### **Phase 4: Testing & Integration**

- [ ] Write unit tests for all task types
- [ ] Perform integration testing
- [ ] Update Docker configurations
- [ ] Validate monitoring integration

## **🔗 Related Documentation**

- **Current Implementation**: `src/personal_assistant/tools/ai_scheduler/`
- **Roadmap Reference**: Phase 2.3.2 - Background Task System
- **Dependencies**: Task 036 (User Management API) ✅ **COMPLETED**
- **Next Phase**: Phase 2.4 - User Interface Development

## **📝 Notes**

This task represents a significant architectural improvement that will:

1. **Preserve all existing functionality** (AI task scheduling)
2. **Add new capabilities** (general background tasks)
3. **Improve system architecture** (separation of concerns)
4. **Enable future enhancements** (easy addition of new task types)

The migration from the current AI-specific scheduler to a general-purpose background task system will provide a solid foundation for handling all types of background processing needs while maintaining the sophisticated AI task capabilities already implemented.
