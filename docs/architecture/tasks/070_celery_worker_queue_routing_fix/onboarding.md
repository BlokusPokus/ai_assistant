# Onboarding: Celery Worker Queue Routing Fix

## Context

You are working on **Task 070: Celery Worker Queue Routing Fix**. The Personal Assistant system has a critical issue where Celery scheduled tasks are not being automatically processed by workers, even though manual task execution works perfectly.

## Problem Summary

- **Celery Beat** successfully schedules `process-due-ai-tasks` every minute
- **Manual execution** works: `process_due_ai_tasks.delay()` processes 13 tasks successfully
- **Automatic processing fails**: Worker shows "empty" queue and doesn't pick up scheduled tasks
- **Root cause**: Queue routing mismatch between Beat scheduler and Worker

## Key Files to Understand

### 1. Celery Configuration (`src/personal_assistant/workers/celery_app.py`)

```python
# Task routing configuration
task_routes={
    "personal_assistant.workers.tasks.ai_tasks.*": {
        "queue": "ai_tasks",
        "priority": 10,
    },
}

# Beat schedule configuration
beat_schedule={
    "process-due-ai-tasks": {
        "task": "personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks",
        "schedule": crontab(minute="*/1"),
        "options": {"priority": 10},
    },
}
```

### 2. Task Implementation (`src/personal_assistant/workers/tasks/ai_tasks.py`)

```python
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_due_ai_tasks(self) -> Dict[str, Any]:
    # Main task that processes due AI tasks
    # Works when called manually, fails when scheduled
```

### 3. Docker Configuration (`docker/docker-compose.dev.yml`)

```yaml
worker:
  command:
    [
      "celery",
      "-A",
      "personal_assistant.workers.celery_app",
      "worker",
      "--loglevel=info",
    ]

scheduler:
  command:
    [
      "celery",
      "-A",
      "personal_assistant.workers.celery_app",
      "beat",
      "--loglevel=info",
    ]
```

## Current System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Celery Beat   │───▶│     Redis      │───▶│ Celery Worker   │
│   (Scheduler)   │    │   (Queue)      │    │   (Executor)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │ Schedules tasks       │ Stores tasks          │ Processes tasks
        │ every minute          │ in queues             │ from queues
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ process-due-     │    │ Queue: ai_tasks │    │ Queue: ???      │
│ ai-tasks        │    │ Priority: 10    │    │ (Mismatch!)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Suspected Issues

### 1. Default Queue Mismatch

- **Beat sends to**: `ai_tasks` queue (configured in task_routes)
- **Worker listens to**: `celery` queue (default behavior)
- **Result**: Tasks never reach the worker

### 2. Queue Declaration Missing

- Worker might not be declaring the `ai_tasks` queue
- Celery needs explicit queue declaration for custom queues

### 3. Redis Database Mismatch

- Different Redis databases being used
- Beat uses database 0, Worker uses different database

## Investigation Strategy

### Step 1: Queue Inspection

```bash
# Connect to Redis and inspect queues
redis-cli -a redis_password
> KEYS *
> LLEN ai_tasks
> LLEN celery
```

### Step 2: Worker Queue Verification

```bash
# Check what queues worker is listening to
celery -A personal_assistant.workers.celery_app inspect active_queues
```

### Step 3: Beat Queue Output

```bash
# Monitor Beat scheduler output
docker logs personal_assistant_scheduler -f
```

### Step 4: Test Queue Routing

```python
# Test task routing manually
from personal_assistant.workers.celery_app import app
result = app.send_task('personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks')
print(f"Task sent to queue: {result.queue}")
```

## Expected Fixes

### Fix 1: Explicit Queue Declaration

```bash
# Update worker command to explicitly declare queues
celery -A personal_assistant.workers.celery_app worker \
  --loglevel=info \
  --queues=ai_tasks,email_tasks,file_tasks,sync_tasks,maintenance_tasks
```

### Fix 2: Default Queue Configuration

```python
# Add default queue configuration
app.conf.task_default_queue = 'ai_tasks'
app.conf.task_default_exchange = 'ai_tasks'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'ai_tasks'
```

### Fix 3: Queue Declaration in Code

```python
# Ensure queues are declared
from kombu import Queue

app.conf.task_queues = (
    Queue('ai_tasks', routing_key='ai_tasks'),
    Queue('email_tasks', routing_key='email_tasks'),
    Queue('file_tasks', routing_key='file_tasks'),
    Queue('sync_tasks', routing_key='sync_tasks'),
    Queue('maintenance_tasks', routing_key='maintenance_tasks'),
)
```

## Testing Strategy

### 1. Unit Tests

- Test queue routing configuration
- Test task registration
- Test queue declaration

### 2. Integration Tests

- Test Beat → Redis → Worker flow
- Test multiple task types
- Test priority handling

### 3. End-to-End Tests

- Verify automatic task processing
- Test scheduled task execution
- Validate SMS notifications

## Success Criteria

- [ ] Celery Beat scheduled tasks are automatically picked up by workers
- [ ] No manual intervention required for task processing
- [ ] All scheduled tasks execute successfully
- [ ] Queue routing is consistent across all components
- [ ] Comprehensive tests prevent future routing issues

## Common Pitfalls

1. **Queue Name Mismatch**: Ensure exact queue names match between Beat and Worker
2. **Redis Database Mismatch**: Verify same Redis database is used
3. **Queue Declaration**: Worker must explicitly declare custom queues
4. **Priority Handling**: Ensure priority configuration is consistent
5. **Environment Variables**: Check Redis URL consistency across components

## Next Steps

1. **Start with diagnosis**: Use the investigation strategy above
2. **Identify the exact mismatch**: Pinpoint where the disconnect occurs
3. **Implement the fix**: Apply the appropriate solution
4. **Test thoroughly**: Verify the fix works end-to-end
5. **Document changes**: Update configuration documentation

## Resources

- [Celery Task Routing Documentation](https://docs.celeryproject.org/en/stable/userguide/routing.html)
- [Celery Queue Configuration](https://docs.celeryproject.org/en/stable/userguide/configuration.html#task-routes)
- [Redis Queue Commands](https://redis.io/commands/)
- [Docker Compose Celery Setup](https://docs.docker.com/compose/)

Remember: The goal is to ensure that when Celery Beat schedules a task, the Celery Worker automatically picks it up and executes it without manual intervention.
