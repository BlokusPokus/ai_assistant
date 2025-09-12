# Implementation Plan: Celery Worker Queue Routing Fix

## Overview

This document outlines the step-by-step implementation plan to fix the Celery worker queue routing issue where scheduled tasks are not being automatically processed.

## Phase 1: Diagnosis and Analysis (2-4 hours)

### Step 1.1: Queue Inspection Script

**Objective**: Create a diagnostic script to inspect Redis queues and worker configuration

**Files to Create**:

- `scripts/diagnose_celery_queues.py`

**Implementation**:

```python
#!/usr/bin/env python3
"""
Celery Queue Diagnosis Script

This script inspects Redis queues and Celery configuration to identify
queue routing mismatches between Beat scheduler and Worker.
"""

import redis
import os
from dotenv import load_dotenv
from personal_assistant.workers.celery_app import app

def inspect_redis_queues():
    """Inspect Redis queues and their contents."""
    load_dotenv('config/development.env')

    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)

    print("🔍 REDIS QUEUE INSPECTION")
    print("=" * 50)

    # Get all keys
    keys = r.keys('*')
    print(f"Total keys in Redis: {len(keys)}")

    # Inspect specific queues
    queues = ['ai_tasks', 'celery', 'email_tasks', 'file_tasks', 'sync_tasks', 'maintenance_tasks']
    for queue in queues:
        length = r.llen(queue)
        print(f"Queue '{queue}': {length} tasks")

        if length > 0:
            # Show first few tasks
            tasks = r.lrange(queue, 0, 2)
            for i, task in enumerate(tasks):
                print(f"  Task {i+1}: {task[:100]}...")

def inspect_celery_config():
    """Inspect Celery configuration."""
    print("\n🔧 CELERY CONFIGURATION")
    print("=" * 50)

    print(f"Broker URL: {app.conf.broker_url}")
    print(f"Result Backend: {app.conf.result_backend}")
    print(f"Default Queue: {app.conf.task_default_queue}")

    print("\nTask Routes:")
    for pattern, config in app.conf.task_routes.items():
        print(f"  {pattern}: {config}")

    print("\nBeat Schedule:")
    for name, config in app.conf.beat_schedule.items():
        print(f"  {name}: {config['task']} -> {config.get('options', {})}")

def inspect_worker_queues():
    """Inspect what queues the worker is listening to."""
    print("\n👂 WORKER QUEUE LISTENING")
    print("=" * 50)

    try:
        # This requires a running worker
        inspect = app.control.inspect()
        active_queues = inspect.active_queues()

        if active_queues:
            for worker, queues in active_queues.items():
                print(f"Worker {worker}:")
                for queue in queues:
                    print(f"  - {queue['name']}")
        else:
            print("No active workers found")
    except Exception as e:
        print(f"Error inspecting worker queues: {e}")

if __name__ == "__main__":
    inspect_redis_queues()
    inspect_celery_config()
    inspect_worker_queues()
```

### Step 1.2: Current State Analysis

**Objective**: Document the current state of the system

**Tasks**:

1. Run the diagnosis script
2. Check Docker container logs
3. Verify Redis connectivity
4. Test manual task execution

**Commands**:

```bash
# Run diagnosis script
python scripts/diagnose_celery_queues.py

# Check worker logs
docker logs personal_assistant_worker -f

# Check scheduler logs
docker logs personal_assistant_scheduler -f

# Test Redis connectivity
redis-cli -a redis_password ping

# Test manual task execution
python -c "
from personal_assistant.workers.celery_app import app
result = app.send_task('personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks')
print(f'Task sent: {result.id}')
"
```

### Step 1.3: Identify Root Cause

**Objective**: Pinpoint the exact queue routing mismatch

**Analysis Points**:

1. **Queue Names**: Are Beat and Worker using the same queue names?
2. **Queue Declaration**: Is the worker declaring the `ai_tasks` queue?
3. **Redis Database**: Are both using the same Redis database?
4. **Routing Keys**: Are routing keys consistent?

**Expected Findings**:

- Beat sends to `ai_tasks` queue
- Worker listens to `celery` queue (default)
- No queue declaration in worker command

## Phase 2: Fix Implementation (2-3 hours)

### Step 2.1: Fix Worker Queue Configuration

**Objective**: Update worker to listen to the correct queues

**File to Modify**: `docker/docker-compose.dev.yml`

**Current Configuration**:

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
```

**Updated Configuration**:

```yaml
worker:
  command:
    [
      "celery",
      "-A",
      "personal_assistant.workers.celery_app",
      "worker",
      "--loglevel=info",
      "--queues=ai_tasks,email_tasks,file_tasks,sync_tasks,maintenance_tasks",
    ]
```

### Step 2.2: Enhance Celery Configuration

**Objective**: Add explicit queue declarations and default queue configuration

**File to Modify**: `src/personal_assistant/workers/celery_app.py`

**Additions**:

```python
# Add after line 91 (after task_routes)
# Explicit queue declarations
from kombu import Queue

app.conf.task_queues = (
    Queue('ai_tasks', routing_key='ai_tasks'),
    Queue('email_tasks', routing_key='email_tasks'),
    Queue('file_tasks', routing_key='file_tasks'),
    Queue('sync_tasks', routing_key='sync_tasks'),
    Queue('maintenance_tasks', routing_key='maintenance_tasks'),
)

# Default queue configuration
app.conf.task_default_queue = 'ai_tasks'
app.conf.task_default_exchange = 'ai_tasks'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'ai_tasks'
```

### Step 2.3: Update Worker Startup Script

**Objective**: Ensure consistent queue configuration in startup script

**File to Modify**: `tests/start_workers.sh`

**Current Configuration**:

```bash
celery -A personal_assistant.workers.celery_app worker --loglevel=info
```

**Updated Configuration**:

```bash
celery -A personal_assistant.workers.celery_app worker \
  --loglevel=info \
  --queues=ai_tasks,email_tasks,file_tasks,sync_tasks,maintenance_tasks
```

### Step 2.4: Add Queue Monitoring

**Objective**: Add logging to track queue activity

**File to Modify**: `src/personal_assistant/workers/celery_app.py`

**Additions**:

```python
# Add after line 196 (after beat schedule logging)
# Log queue configuration
logger.info("🚀 CELERY QUEUE CONFIGURATION:")
logger.info(f"📋 Default Queue: {app.conf.task_default_queue}")
logger.info(f"📋 Active Queues: {[q.name for q in app.conf.task_queues]}")
logger.info(f"📋 Task Routes: {app.conf.task_routes}")
print("🚀 CELERY QUEUE CONFIGURATION:")
print(f"📋 Default Queue: {app.conf.task_default_queue}")
print(f"📋 Active Queues: {[q.name for q in app.conf.task_queues]}")
print(f"📋 Task Routes: {app.conf.task_routes}")
```

## Phase 3: Validation and Testing (3-4 hours)

### Step 3.1: Unit Tests

**Objective**: Create comprehensive tests for queue routing

**File to Create**: `tests/unit/test_workers/test_queue_routing.py`

**Test Cases**:

```python
import pytest
from unittest.mock import patch, MagicMock
from personal_assistant.workers.celery_app import app

class TestQueueRouting:
    """Test queue routing configuration."""

    def test_task_routes_configuration(self):
        """Test that task routes are configured correctly."""
        routes = app.conf.task_routes

        assert 'personal_assistant.workers.tasks.ai_tasks.*' in routes
        assert routes['personal_assistant.workers.tasks.ai_tasks.*']['queue'] == 'ai_tasks'
        assert routes['personal_assistant.workers.tasks.ai_tasks.*']['priority'] == 10

    def test_queue_declarations(self):
        """Test that queues are properly declared."""
        queues = app.conf.task_queues
        queue_names = [q.name for q in queues]

        expected_queues = ['ai_tasks', 'email_tasks', 'file_tasks', 'sync_tasks', 'maintenance_tasks']
        for queue in expected_queues:
            assert queue in queue_names

    def test_default_queue_configuration(self):
        """Test default queue configuration."""
        assert app.conf.task_default_queue == 'ai_tasks'
        assert app.conf.task_default_exchange == 'ai_tasks'
        assert app.conf.task_default_exchange_type == 'direct'
        assert app.conf.task_default_routing_key == 'ai_tasks'

    def test_beat_schedule_configuration(self):
        """Test beat schedule configuration."""
        schedule = app.conf.beat_schedule

        assert 'process-due-ai-tasks' in schedule
        assert schedule['process-due-ai-tasks']['task'] == 'personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks'
        assert schedule['process-due-ai-tasks']['options']['priority'] == 10
```

### Step 3.2: Integration Tests

**Objective**: Test the complete Beat → Redis → Worker flow

**File to Create**: `tests/integration/test_celery_integration.py`

**Test Cases**:

```python
import pytest
import time
from personal_assistant.workers.celery_app import app
from personal_assistant.workers.tasks.ai_tasks import process_due_ai_tasks

class TestCeleryIntegration:
    """Test Celery integration and queue routing."""

    def test_task_routing_to_correct_queue(self):
        """Test that tasks are routed to the correct queue."""
        # Send a test task
        result = app.send_task('personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks')

        # Check that task is in the correct queue
        # This requires Redis inspection
        import redis
        r = redis.from_url(app.conf.broker_url)

        # Check ai_tasks queue
        ai_tasks_length = r.llen('ai_tasks')
        celery_length = r.llen('celery')

        # Task should be in ai_tasks queue, not celery queue
        assert ai_tasks_length > 0 or celery_length == 0

    def test_worker_queue_listening(self):
        """Test that worker is listening to correct queues."""
        inspect = app.control.inspect()
        active_queues = inspect.active_queues()

        if active_queues:
            for worker, queues in active_queues.items():
                queue_names = [q['name'] for q in queues]
                assert 'ai_tasks' in queue_names
```

### Step 3.3: End-to-End Testing

**Objective**: Verify automatic task processing works

**Test Procedure**:

1. **Start Services**: Start Redis, Worker, and Beat
2. **Monitor Logs**: Watch for task scheduling and execution
3. **Verify Processing**: Confirm tasks are automatically processed
4. **Check Results**: Validate task results and notifications

**Commands**:

```bash
# Start services
docker-compose -f docker/docker-compose.dev.yml up -d redis worker scheduler

# Monitor logs
docker logs personal_assistant_scheduler -f &
docker logs personal_assistant_worker -f &

# Wait for scheduled execution (up to 2 minutes)
sleep 120

# Check for successful task execution
docker logs personal_assistant_worker | grep "process_due_ai_tasks"
```

### Step 3.4: Load Testing

**Objective**: Ensure system handles multiple scheduled tasks

**Test Procedure**:

1. **Create Multiple Tasks**: Schedule several AI tasks
2. **Monitor Processing**: Watch for concurrent execution
3. **Verify Results**: Check all tasks are processed correctly
4. **Performance Check**: Ensure no bottlenecks

## Phase 4: Documentation and Cleanup (1-2 hours)

### Step 4.1: Update Documentation

**Files to Update**:

- `README.md` - Add Celery configuration section
- `docs/DEV_SETUP.md` - Update development setup instructions
- `docker/README.md` - Document Docker configuration

### Step 4.2: Create Troubleshooting Guide

**File to Create**: `docs/troubleshooting/celery_queue_issues.md`

**Content**:

- Common queue routing issues
- Diagnosis commands
- Fix procedures
- Prevention strategies

### Step 4.3: Cleanup

**Tasks**:

1. Remove temporary diagnostic files
2. Clean up test data
3. Update configuration examples
4. Verify all changes are committed

## Rollback Plan

If the fix causes issues:

1. **Immediate Rollback**:

   ```bash
   # Revert Docker configuration
   git checkout HEAD~1 docker/docker-compose.dev.yml

   # Revert Celery configuration
   git checkout HEAD~1 src/personal_assistant/workers/celery_app.py

   # Restart services
   docker-compose -f docker/docker-compose.dev.yml restart worker scheduler
   ```

2. **Investigation**:

   - Check logs for errors
   - Verify Redis connectivity
   - Test manual task execution
   - Identify what went wrong

3. **Alternative Approach**:
   - Try different queue configuration
   - Use default queue with different routing
   - Implement queue monitoring

## Success Metrics

- [ ] **Automatic Processing**: Scheduled tasks execute without manual intervention
- [ ] **Queue Consistency**: Beat and Worker use same queue configuration
- [ ] **Test Coverage**: Comprehensive tests prevent regression
- [ ] **Documentation**: Clear troubleshooting and configuration guides
- [ ] **Performance**: No degradation in task processing speed
- [ ] **Reliability**: System handles failures gracefully

## Timeline Summary

| Phase     | Duration       | Key Deliverables                            |
| --------- | -------------- | ------------------------------------------- |
| Phase 1   | 2-4 hours      | Diagnosis script, root cause identification |
| Phase 2   | 2-3 hours      | Fixed configuration, updated commands       |
| Phase 3   | 3-4 hours      | Comprehensive tests, validation             |
| Phase 4   | 1-2 hours      | Documentation, cleanup                      |
| **Total** | **8-13 hours** | **Complete fix with testing**               |

## Risk Mitigation

- **Staged Rollout**: Test in development before production
- **Backup Configuration**: Keep original configuration as backup
- **Comprehensive Testing**: Test all task types and schedules
- **Monitoring**: Add queue monitoring to detect issues early
- **Rollback Plan**: Clear procedure to revert changes if needed
