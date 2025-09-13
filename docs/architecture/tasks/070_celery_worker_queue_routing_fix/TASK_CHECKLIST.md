# Task Checklist: Celery Worker Queue Routing Fix

## Pre-Implementation Checklist

### Environment Setup

- [ ] Redis server is running and accessible
- [ ] Docker containers are running (redis, worker, scheduler)
- [ ] Development environment is properly configured
- [ ] All required environment variables are set
- [ ] Database connectivity is working

### Current State Verification

- [ ] Manual task execution works: `process_due_ai_tasks.delay()`
- [ ] Celery Beat is scheduling tasks every minute
- [ ] Worker shows "empty" queue when inspected
- [ ] Redis responds to ping and persistence is working
- [ ] Logs show Beat sending tasks but Worker not picking them up

## Phase 1: Diagnosis and Analysis

### Queue Inspection

- [ ] Create `scripts/diagnose_celery_queues.py` script
- [ ] Run diagnosis script to inspect Redis queues
- [ ] Check what queues exist in Redis (`KEYS *`)
- [ ] Verify queue lengths (`LLEN ai_tasks`, `LLEN celery`)
- [ ] Document current queue state

### Celery Configuration Analysis

- [ ] Inspect Celery app configuration
- [ ] Verify task routes configuration
- [ ] Check beat schedule configuration
- [ ] Validate Redis URL consistency
- [ ] Document current configuration

### Worker Queue Verification

- [ ] Check what queues worker is listening to
- [ ] Verify worker queue declarations
- [ ] Test worker connectivity to Redis
- [ ] Document worker configuration

### Root Cause Identification

- [ ] Identify exact queue routing mismatch
- [ ] Determine if Beat and Worker use different queues
- [ ] Check for missing queue declarations
- [ ] Verify Redis database consistency
- [ ] Document root cause analysis

## Phase 2: Fix Implementation

### Worker Queue Configuration

- [ ] Update `docker/docker-compose.dev.yml` worker command
- [ ] Add explicit queue declarations to worker command
- [ ] Include all required queues: `ai_tasks,email_tasks,file_tasks,sync_tasks,maintenance_tasks`
- [ ] Test updated worker command

### Celery Configuration Enhancement

- [ ] Add explicit queue declarations to `celery_app.py`
- [ ] Configure default queue settings
- [ ] Add queue monitoring and logging
- [ ] Update task routes if needed
- [ ] Test configuration changes

### Worker Startup Script Update

- [ ] Update `tests/start_workers.sh` script
- [ ] Add queue declarations to startup command
- [ ] Ensure consistency with Docker configuration
- [ ] Test startup script

### Configuration Validation

- [ ] Verify all configuration changes are consistent
- [ ] Check environment variable usage
- [ ] Validate Redis URL consistency
- [ ] Test configuration loading

## Phase 3: Validation and Testing

### Unit Tests

- [ ] Create `tests/unit/test_workers/test_queue_routing.py`
- [ ] Test task routes configuration
- [ ] Test queue declarations
- [ ] Test default queue configuration
- [ ] Test beat schedule configuration
- [ ] Run unit tests and verify all pass

### Integration Tests

- [ ] Create `tests/integration/test_celery_integration.py`
- [ ] Test task routing to correct queue
- [ ] Test worker queue listening
- [ ] Test Beat → Redis → Worker flow
- [ ] Run integration tests and verify all pass

### End-to-End Testing

- [ ] Start all services (Redis, Worker, Beat)
- [ ] Monitor logs for task scheduling
- [ ] Verify automatic task processing
- [ ] Check task execution results
- [ ] Validate SMS notifications
- [ ] Confirm no manual intervention needed

### Load Testing

- [ ] Create multiple scheduled tasks
- [ ] Monitor concurrent execution
- [ ] Verify all tasks are processed
- [ ] Check for performance bottlenecks
- [ ] Validate system stability

## Phase 4: Documentation and Cleanup

### Documentation Updates

- [ ] Update `README.md` with Celery configuration section
- [ ] Update `docs/DEV_SETUP.md` with development setup instructions
- [ ] Update `docker/README.md` with Docker configuration details
- [ ] Create troubleshooting guide for queue issues

### Troubleshooting Guide

- [ ] Create `docs/troubleshooting/celery_queue_issues.md`
- [ ] Document common queue routing issues
- [ ] Provide diagnosis commands
- [ ] Include fix procedures
- [ ] Add prevention strategies

### Cleanup Tasks

- [ ] Remove temporary diagnostic files
- [ ] Clean up test data
- [ ] Update configuration examples
- [ ] Verify all changes are committed
- [ ] Update task documentation

## Post-Implementation Verification

### Functional Testing

- [ ] Scheduled tasks execute automatically every minute
- [ ] No manual intervention required for task processing
- [ ] All scheduled tasks execute successfully
- [ ] SMS notifications are sent correctly
- [ ] Task results are properly stored

### Performance Testing

- [ ] Task processing time is acceptable
- [ ] No memory leaks or resource issues
- [ ] System handles multiple concurrent tasks
- [ ] Redis queue performance is optimal
- [ ] Worker performance is stable

### Monitoring Setup

- [ ] Queue monitoring is working
- [ ] Logs show proper task flow
- [ ] Error handling is working
- [ ] Alerting is configured (if applicable)
- [ ] Metrics collection is working

## Rollback Preparation

### Backup Configuration

- [ ] Backup original `docker/docker-compose.dev.yml`
- [ ] Backup original `celery_app.py`
- [ ] Backup original `start_workers.sh`
- [ ] Document original configuration
- [ ] Create rollback script

### Rollback Testing

- [ ] Test rollback procedure
- [ ] Verify rollback restores original functionality
- [ ] Document rollback steps
- [ ] Ensure rollback is reversible

## Success Criteria Verification

### Primary Objectives

- [ ] **Automatic Processing**: Scheduled tasks execute without manual intervention
- [ ] **Queue Consistency**: Beat and Worker use same queue configuration
- [ ] **No Regression**: Manual task execution still works
- [ ] **Performance**: No degradation in task processing speed
- [ ] **Reliability**: System handles failures gracefully

### Secondary Objectives

- [ ] **Test Coverage**: Comprehensive tests prevent regression
- [ ] **Documentation**: Clear troubleshooting and configuration guides
- [ ] **Monitoring**: Queue monitoring detects issues early
- [ ] **Maintainability**: Configuration is easy to understand and modify

## Final Validation

### System Health Check

- [ ] All services are running normally
- [ ] No error logs in any service
- [ ] Redis is healthy and responsive
- [ ] Database connectivity is working
- [ ] All scheduled tasks are processing

### User Acceptance Testing

- [ ] AI tasks are processed automatically
- [ ] SMS notifications are sent correctly
- [ ] System responds to user requests normally
- [ ] No user-facing errors or issues
- [ ] Performance meets expectations

### Documentation Review

- [ ] All documentation is up to date
- [ ] Configuration examples are correct
- [ ] Troubleshooting guide is comprehensive
- [ ] Setup instructions are clear
- [ ] Code comments are helpful

## Sign-off Checklist

### Technical Review

- [ ] Code changes are reviewed and approved
- [ ] Configuration changes are validated
- [ ] Tests are comprehensive and passing
- [ ] Performance is acceptable
- [ ] Security considerations are addressed

### Documentation Review

- [ ] Documentation is complete and accurate
- [ ] Troubleshooting guide is helpful
- [ ] Configuration examples work
- [ ] Setup instructions are clear
- [ ] Code comments are appropriate

### Final Approval

- [ ] All checklist items are completed
- [ ] Success criteria are met
- [ ] No outstanding issues
- [ ] System is ready for production
- [ ] Task is considered complete

## Notes and Observations

### Issues Encountered

- [ ] Document any issues encountered during implementation
- [ ] Note any workarounds or special considerations
- [ ] Record any performance observations
- [ ] Document any configuration gotchas

### Lessons Learned

- [ ] Document key learnings from this task
- [ ] Note any best practices discovered
- [ ] Record any recommendations for future tasks
- [ ] Document any process improvements

### Future Improvements

- [ ] Note any potential future improvements
- [ ] Document any technical debt created
- [ ] Record any optimization opportunities
- [ ] Note any monitoring enhancements needed
