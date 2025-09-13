va# Task 070: Celery Worker Queue Routing Fix

## Problem Statement

The Celery worker system has a critical issue where scheduled tasks are not being automatically processed, even though manual triggering works perfectly. This indicates a queue routing mismatch between Celery Beat (scheduler) and the worker.

### Current Behavior

- ✅ **Celery Beat**: Successfully schedules `process-due-ai-tasks` every minute
- ✅ **Manual Execution**: `process_due_ai_tasks.delay()` works and processes 13 tasks successfully
- ❌ **Automatic Processing**: Worker shows "empty" queue and doesn't pick up scheduled tasks
- ✅ **Redis Connection**: Redis responds to ping and persistence is working

### Root Cause Analysis

The issue is likely a **queue routing mismatch**:

- Celery Beat sends tasks to one queue/routing key
- Worker listens to a different queue/routing key
- This creates a disconnect where scheduled tasks never reach the worker

## Task Objectives

1. **Identify the exact queue routing mismatch**
2. **Fix the routing configuration**
3. **Verify automatic task processing works**
4. **Create comprehensive testing to prevent regression**

## Success Criteria

- [x] Celery Beat scheduled tasks are automatically picked up by workers (FIXED)
- [x] No manual intervention required for task processing (FIXED)
- [x] All scheduled tasks execute successfully (FIXED)
- [x] Queue routing is consistent across all components (FIXED)
- [x] Comprehensive tests prevent future routing issues (COMPLETED)
- [x] **Redis queue naming conflict with special characters resolved** (COMPLETED)

## Technical Context

### Current Configuration Analysis

**Celery App Configuration** (`src/personal_assistant/workers/celery_app.py`):

```python
task_routes={
    "personal_assistant.workers.tasks.ai_tasks.*": {
        "queue": "ai_tasks",
        "priority": 10,
    },
    # ... other routes
}

beat_schedule={
    "process-due-ai-tasks": {
        "task": "personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks",
        "schedule": crontab(minute="*/1"),
        "options": {"priority": 10},
    },
    # ... other schedules
}
```

**Redis Configuration**:

- Development: `redis://:redis_password@localhost:6379/0`
- Docker: `redis://:redis_password@redis:6379/0`

**Worker Command**:

```bash
celery -A personal_assistant.workers.celery_app worker --loglevel=info
```

**Beat Command**:

```bash
celery -A personal_assistant.workers.celery_app beat --loglevel=info
```

### Suspected Issues

1. **Default Queue Mismatch**: Worker might be listening to `celery` queue instead of `ai_tasks`
2. **Queue Declaration**: Worker might not be declaring the `ai_tasks` queue
3. **Routing Key Mismatch**: Beat might be using different routing keys
4. **Redis Database Mismatch**: Different Redis databases being used

## Implementation Plan

### Phase 1: Diagnosis (Priority: Critical)

1. **Queue Inspection**: Check what queues exist in Redis
2. **Worker Queue List**: Verify which queues the worker is listening to
3. **Beat Queue Output**: Confirm where Beat is sending tasks
4. **Routing Verification**: Validate task routing configuration

### Phase 2: Fix Implementation (Priority: Critical)

1. **Fix Queue Configuration**: Ensure worker listens to correct queues
2. **Update Worker Command**: Add explicit queue declarations
3. **Verify Routing**: Confirm Beat and Worker use same routing
4. **Test Configuration**: Validate fix with test tasks

### Phase 3: Validation & Testing (Priority: High)

1. **End-to-End Testing**: Verify automatic task processing
2. **Load Testing**: Ensure system handles multiple scheduled tasks
3. **Regression Testing**: Prevent future routing issues
4. **Documentation**: Update configuration documentation

## Files to Modify

### Core Files

- `src/personal_assistant/workers/celery_app.py` - Main Celery configuration
- `docker/docker-compose.dev.yml` - Worker command configuration
- `tests/start_workers.sh` - Worker startup script

### New Files

- `tests/unit/test_workers/test_queue_routing.py` - Queue routing tests
- `scripts/diagnose_celery_queues.py` - Queue diagnosis script
- `docs/architecture/tasks/070_celery_worker_queue_routing_fix/DIAGNOSIS_REPORT.md` - Diagnosis findings

## Risk Assessment

### High Risk

- **Service Disruption**: Fixing queue routing might temporarily disrupt task processing
- **Data Loss**: Incorrect routing changes could cause task loss

### Medium Risk

- **Configuration Drift**: Changes might not be consistent across environments
- **Testing Complexity**: Queue routing is difficult to test comprehensively

### Mitigation Strategies

- **Staged Rollout**: Test in development before production
- **Backup Configuration**: Keep original configuration as backup
- **Comprehensive Testing**: Test all task types and schedules
- **Monitoring**: Add queue monitoring to detect issues early

## Dependencies

- Redis server running and accessible
- Celery Beat scheduler running
- Celery Worker running
- Database connectivity for task execution

## Timeline

- **Phase 1 (Diagnosis)**: 2-4 hours
- **Phase 2 (Fix Implementation)**: 2-3 hours
- **Phase 3 (Validation & Testing)**: 3-4 hours
- **Total Estimated Time**: 7-11 hours

## Investigation Findings

### ✅ Original Issue RESOLVED

The initial queue routing mismatch was successfully fixed:

- **Problem**: Worker was listening to `celery` queue, Beat was sending to `ai_tasks` queue
- **Solution**: Updated worker command to listen to all relevant queues (`ai_tasks`, `email_tasks`, etc.)
- **Result**: Tasks now flow correctly from Beat → Redis → Worker

### ⚠️ NEW ISSUE DISCOVERED: Redis Queue Naming Conflict

During investigation, a critical Redis queue naming issue was discovered:

**Problem**: Redis queues have special characters in their names:

- Expected: `ai_tasks`, `email_tasks`, `sync_tasks`
- Actual: `ai_tasks\x06\x169`, `email_tasks\x06\x163`, `sync_tasks\x06\x166`

**Impact**:

- Thousands of tasks accumulated in suffixed queues (1,259+ items in `ai_tasks\x06\x169`)
- Tasks are being sent to queues with special characters instead of expected names
- This suggests multiple Celery instances or queue naming conflicts

**Evidence**:

```
Redis CLI shows: ai_tasks\x06\x169 (1,259 items)
Python script shows: ai_tasks9 (1,259 items)
```

## ✅ FINAL SOLUTION IMPLEMENTED

### Issues Resolved

1. **Original Queue Routing Mismatch**: ✅ FIXED

   - Worker now listens to all required queues (`ai_tasks`, `email_tasks`, etc.)
   - Beat scheduler sends tasks to correct queues
   - Automatic task processing works without manual intervention

2. **Redis Queue Naming Conflicts**: ✅ FIXED
   - Identified and cleared problematic suffixed queues (`ai_tasks\x06\x169`, etc.)
   - Implemented proper process management to prevent multiple instances
   - Created comprehensive monitoring and cleanup procedures

### Comprehensive Testing Implemented

- **Unit Tests**: `tests/unit/test_workers/test_queue_routing.py`

  - Tests queue routing configuration
  - Tests queue declarations and consistency
  - Tests priority ordering and Redis connection
  - Tests for queue naming conflicts and special characters

- **Integration Tests**: `tests/integration/test_celery_integration.py`
  - Tests complete Beat → Redis → Worker flow
  - Tests queue isolation and routing correctness
  - Tests prevention of original issue regression

### Documentation Created

- **Troubleshooting Guide**: `docs/troubleshooting/celery_queue_issues.md`

  - Common issues and solutions
  - Diagnosis commands and procedures
  - Prevention strategies and monitoring
  - Emergency procedures and health checks

- **Diagnostic Script**: `scripts/diagnose_celery_queues.py`
  - Inspects Redis queues and Celery configuration
  - Identifies problematic queue names
  - Provides cleanup capabilities

### Prevention Measures

1. **Process Management**: Ensure only one Beat and Worker instance running
2. **Queue Monitoring**: Regular health checks and alerting
3. **Comprehensive Testing**: Automated tests prevent regression
4. **Clear Documentation**: Troubleshooting guide for future issues

## 🎯 TASK COMPLETED SUCCESSFULLY

All objectives have been achieved:

- ✅ Original queue routing issue resolved
- ✅ Redis queue naming conflicts resolved
- ✅ Comprehensive testing implemented
- ✅ Documentation and troubleshooting guide created
- ✅ Prevention measures in place

## Related Tasks

- Task 062: Celery Redis System Validation (previous analysis)
- Task 037: Background Task System (original implementation)
- Task 059: CI/CD Pipeline Automation (deployment considerations)
