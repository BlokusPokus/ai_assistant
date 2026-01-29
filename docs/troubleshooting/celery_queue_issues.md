# Celery Queue Issues Troubleshooting Guide

## Overview

This guide helps diagnose and fix common Celery queue routing issues, particularly the queue naming conflicts that were discovered and resolved in Task 070.

## Common Issues

### 1. Queue Routing Mismatch

**Symptoms:**

- Scheduled tasks are not being processed automatically
- Manual task execution works fine
- Worker shows "empty" queue when inspected
- Beat scheduler is running and sending tasks

**Root Cause:**
Celery Beat sends tasks to one queue (e.g., `ai_tasks`) but Worker listens to a different queue (e.g., `celery`).

**Solution:**
Ensure worker command includes explicit queue declarations. Use the canonical app entrypoint `personal_assistant.celery` and the current queues:

```bash
celery -A personal_assistant.celery worker \
  --queues=ai_tasks,sms_tasks,grocery_tasks \
  --loglevel=info
```

### 2. Queue Naming Conflicts with Special Characters

**Symptoms:**

- Redis shows queue names like `ai_tasks\x06\x169`, `email_tasks\x06\x163`
- Thousands of tasks accumulated in suffixed queues
- Tasks never get processed from these queues

**Root Cause:**
Multiple Celery instances running simultaneously or queue naming conflicts causing Redis to append special characters to queue names.

**Solution:**

1. Stop all Celery instances:

   ```bash
   docker stop personal_assistant_worker personal_assistant_scheduler
   ```

2. Clear problematic queues (legacy example; adjust queue names to match your env):

   ```bash
   redis-cli -h localhost -p 6379 -a redis_password del "ai_tasks\x06\x169" "sms_tasks\x06\x163" "grocery_tasks\x06\x166"
   ```

3. Restart services with proper configuration (uses `-A personal_assistant.celery`):
   ```bash
   docker-compose -f docker/docker-compose.dev.yml up -d worker scheduler
   ```

## Diagnosis Commands

### Check Redis Queue Status

```bash
# List all Redis keys
redis-cli -h localhost -p 6379 -a redis_password keys "*"

# Check specific queue lengths
redis-cli -h localhost -p 6379 -a redis_password llen "ai_tasks"
redis-cli -h localhost -p 6379 -a redis_password llen "celery"

# Check for problematic suffixed queues
redis-cli -h localhost -p 6379 -a redis_password keys "*tasks*"
```

### Check Celery Configuration

```bash
# Run diagnostic script
python scripts/diagnose_celery_queues.py

# Check running processes
ps aux | grep celery

# Check Docker containers
docker ps | grep personal_assistant
```

### Check Worker Queue Listening

```bash
# Inspect active worker queues (use canonical app personal_assistant.celery)
python -c "
from personal_assistant.celery import app
inspect = app.control.inspect()
active_queues = inspect.active_queues()
print(active_queues)
"
```

## Prevention Strategies

### 1. Proper Configuration

Ensure all components use consistent queue configuration. The canonical app and config live in `personal_assistant.celery` and `personal_assistant.celery.config`; the current queues are `ai_tasks`, `sms_tasks`, and `grocery_tasks`.

**Celery configuration** (`src/personal_assistant/celery/config.py`):

```python
task_queues=(
    Queue('ai_tasks', routing_key='ai_tasks'),
    Queue('sms_tasks', routing_key='sms_tasks'),
    Queue('grocery_tasks', routing_key='grocery_tasks'),
),
task_default_queue='ai_tasks',
```

**Docker worker / beat** – use app entrypoint `personal_assistant.celery` (`docker/docker-compose.dev.yml`):

```yaml
# Worker
command:
  [
    "celery",
    "-A",
    "personal_assistant.celery",
    "worker",
    "--loglevel=info",
    "--queues=ai_tasks,sms_tasks,grocery_tasks",
  ]

# Beat scheduler
command:
  [
    "celery",
    "-A",
    "personal_assistant.celery",
    "beat",
    "--loglevel=info",
  ]
```

**Legacy queue names** (no longer in use): `email_tasks`, `file_tasks`, `sync_tasks`, `maintenance_tasks`. Historical docs may still reference them.

### 2. Process Management

- Ensure only one Beat scheduler instance is running
- Ensure only one Worker instance per queue is running
- Use Docker Compose for consistent service management
- Monitor for multiple Celery processes

### 3. Monitoring

- Set up queue monitoring to detect backlog
- Monitor Redis queue lengths
- Alert on queue naming conflicts
- Regular health checks

### 4. Testing

Run comprehensive tests to prevent regression:

```bash
# Unit tests
python -m pytest tests/unit/test_workers/test_queue_routing.py -v

# Integration tests
python -m pytest tests/integration/test_celery_integration.py -v
```

## Emergency Procedures

### Clear All Queues

If queues are completely corrupted or have special characters:

```bash
# Stop all services
docker stop personal_assistant_worker personal_assistant_scheduler

# Clear all task queues (including problematic suffixed queues)
redis-cli -h localhost -p 6379 -a redis_password flushdb

# Verify Redis is clean
redis-cli -h localhost -p 6379 -a redis_password keys "*"

# Restart services
docker-compose -f docker/docker-compose.dev.yml up -d worker scheduler
```

**Note**: The `flushdb` command clears the entire Redis database. This is the most effective way to remove problematic queues with special characters like `ai_tasks\x06\x169`.

### Reset Celery Beat Schedule

If Beat scheduler is corrupted:

```bash
# Stop scheduler
docker stop personal_assistant_scheduler

# Remove beat schedule database
rm celerybeat-schedule.db

# Restart scheduler
docker-compose -f docker/docker-compose.dev.yml up -d scheduler
```

## Monitoring Commands

### Queue Health Check

```bash
#!/bin/bash
# queue_health_check.sh

REDIS_URL="redis://:redis_password@localhost:6379"

echo "🔍 Celery Queue Health Check"
echo "=============================="

# Check Redis connection
redis-cli -h localhost -p 6379 -a redis_password ping

# Check queue lengths (current queues: ai_tasks, sms_tasks, grocery_tasks)
echo "📊 Queue Status:"
for queue in ai_tasks sms_tasks grocery_tasks; do
    length=$(redis-cli -h localhost -p 6379 -a redis_password llen "$queue")
    echo "  $queue: $length tasks"
done

# Check for problematic queues
echo "⚠️  Problematic Queues:"
problematic=$(redis-cli -h localhost -p 6379 -a redis_password keys "*tasks*" | grep -v -E "(ai_tasks|sms_tasks|grocery_tasks)$")
if [ -n "$problematic" ]; then
    echo "$problematic"
else
    echo "  None found"
fi
```

### Worker Status Check

```bash
#!/bin/bash
# worker_status_check.sh

echo "👂 Worker Status Check"
echo "======================"

# Check Docker containers
echo "🐳 Docker Containers:"
docker ps | grep personal_assistant

# Check Celery processes
echo "🔄 Celery Processes:"
ps aux | grep celery

# Check worker queue listening (canonical app: personal_assistant.celery)
echo "📡 Active Worker Queues:"
python -c "
from personal_assistant.celery import app
try:
    inspect = app.control.inspect()
    active_queues = inspect.active_queues()
    if active_queues:
        for worker, queues in active_queues.items():
            print(f'  {worker}:')
            for queue in queues:
                print(f'    - {queue[\"name\"]}')
    else:
        print('  No active workers found')
except Exception as e:
    print(f'  Error: {e}')
"
```

## Related Documentation

- [Task 070: Celery Worker Queue Routing Fix](../architecture/tasks/070_celery_worker_queue_routing_fix/README.md)
- [Celery Configuration](../architecture/tasks/070_celery_worker_queue_routing_fix/IMPLEMENTATION_PLAN.md)
- [Development Setup](../../DEV_SETUP.md)
- [Docker Configuration](../../docker/README.md)

## Support

If you encounter issues not covered in this guide:

1. Check the diagnostic script output: `python scripts/diagnose_celery_queues.py`
2. Review the task documentation: `docs/architecture/tasks/070_celery_worker_queue_routing_fix/`
3. Run the comprehensive tests: `python -m pytest tests/unit/test_workers/test_queue_routing.py`
4. Check Docker container logs: `docker logs personal_assistant_worker`
