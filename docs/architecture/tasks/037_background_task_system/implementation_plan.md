# Task 037: Implementation Plan - Background Task System

## **📋 Implementation Overview**

This document provides a detailed, step-by-step implementation plan for transforming the current AI-specific scheduler into a comprehensive, general-purpose background task system.

**Target Timeline**: 5 days  
**Current Status**: AI scheduler working, needs reorganization and expansion  
**Goal**: Modular, scalable background task system with separation of concerns

## **🔍 Current Architecture Analysis**

### **Existing Code Structure**

```
src/personal_assistant/tools/ai_scheduler/
├── celery_config.py          # Celery configuration
├── ai_task_scheduler.py      # Main task processing logic
├── task_executor.py          # AI task execution
├── task_scheduler.py         # Scheduler management
├── ai_task_manager.py        # Database operations
├── notification_service.py   # Notification handling
├── task_evaluator.py        # Task evaluation logic
├── health_monitor.py        # Health monitoring
├── performance_monitor.py   # Performance tracking
└── README.md                 # Documentation
```

### **Current Limitations Identified**

1. **Tight Coupling**: All logic mixed in single modules
2. **Limited Scope**: Only AI-specific tasks
3. **Hard to Extend**: Adding new task types requires modifying existing code
4. **Resource Management**: Single worker type for all tasks
5. **Monitoring**: Limited task-specific metrics

## **🎯 Target Architecture**

### **New Directory Structure**

```
src/personal_assistant/workers/
├── celery_app.py             # Central Celery application
├── tasks/
│   ├── __init__.py           # Task registry
│   ├── ai_tasks.py           # AI task processing (moved from tools/)
│   ├── email_tasks.py        # Email processing tasks
│   ├── file_tasks.py         # File management tasks
│   ├── sync_tasks.py         # API synchronization tasks
│   ├── maintenance_tasks.py  # System maintenance tasks
│   └── base_tasks.py         # Base task classes and utilities
├── schedulers/
│   ├── __init__.py           # Scheduler registry
│   ├── ai_scheduler.py       # AI task scheduling logic
│   ├── email_scheduler.py    # Email task scheduling
│   ├── maintenance_scheduler.py # System maintenance timing
│   └── base_scheduler.py     # Base scheduler classes
├── utils/
│   ├── __init__.py           # Utility registry
│   ├── task_monitoring.py    # Task monitoring utilities
│   ├── error_handling.py     # Centralized error handling
│   ├── metrics.py            # Task-specific metrics
│   └── health_check.py       # Health check utilities
└── __init__.py               # Worker system initialization
```

## **📊 Implementation Phases**

### **Phase 1: Reorganize Current Code (Day 1)**

#### **Step 1.1: Create New Directory Structure**

```bash
# Create new directory structure
mkdir -p src/personal_assistant/workers/{tasks,schedulers,utils}

# Create __init__.py files
touch src/personal_assistant/workers/__init__.py
touch src/personal_assistant/workers/tasks/__init__.py
touch src/personal_assistant/workers/schedulers/__init__.py
touch src/personal_assistant/workers/utils/__init__.py
```

#### **Step 1.2: Move and Refactor AI Scheduler**

```python
# workers/tasks/ai_tasks.py
"""
AI Task Processing Module

This module handles AI-specific background tasks including:
- Processing due AI tasks
- Executing AI-driven workflows
- Managing AI task lifecycle
"""

from celery import shared_task
from datetime import datetime
from typing import Any, Dict

from ..celery_app import app
from ...database.models.ai_tasks import AITask
from ...core import AgentCore

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_due_ai_tasks(self) -> Dict[str, Any]:
    """Process due AI tasks every 10 minutes."""
    # Move existing logic from ai_task_scheduler.py
    pass

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def test_scheduler_connection(self) -> Dict[str, Any]:
    """Test scheduler connection every 30 minutes."""
    # Move existing logic from ai_task_scheduler.py
    pass

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_old_logs(self) -> Dict[str, Any]:
    """Clean up old logs daily at 2 AM."""
    # Move existing logic from ai_task_scheduler.py
    pass
```

#### **Step 1.3: Create Central Celery Application**

```python
# workers/celery_app.py
"""
Central Celery Application for Personal Assistant Background Tasks

This module provides a unified Celery application that handles all types
of background tasks with proper routing and configuration.
"""

import logging
import os
from celery import Celery
from celery.schedules import crontab

# Get Redis URL from environment or use default
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# Create Celery app
app = Celery(
    'personal_assistant_workers',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery configuration
app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task routing for different task types
    task_routes={
        'personal_assistant.workers.tasks.ai_tasks.*': {'queue': 'ai_tasks'},
        'personal_assistant.workers.tasks.email_tasks.*': {'queue': 'email_tasks'},
        'personal_assistant.workers.tasks.file_tasks.*': {'queue': 'file_tasks'},
        'personal_assistant.workers.tasks.sync_tasks.*': {'queue': 'sync_tasks'},
        'personal_assistant.workers.tasks.maintenance_tasks.*': {'queue': 'maintenance_tasks'},
    },

    # Beat schedule for different task types
    beat_schedule={
        # AI tasks (existing functionality)
        'process-due-ai-tasks': {
            'task': 'personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
        },
        'test-scheduler-connection': {
            'task': 'personal_assistant.workers.tasks.ai_tasks.test_scheduler_connection',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
        },
        'cleanup-old-logs': {
            'task': 'personal_assistant.workers.tasks.ai_tasks.cleanup_old_logs',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },

        # Email tasks (new functionality)
        'process-email-queue': {
            'task': 'personal_assistant.workers.tasks.email_tasks.process_email_queue',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'send-daily-email-summary': {
            'task': 'personal_assistant.workers.tasks.email_tasks.send_daily_email_summary',
            'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
        },

        # File tasks (new functionality)
        'cleanup-temp-files': {
            'task': 'personal_assistant.workers.tasks.file_tasks.cleanup_temp_files',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'backup-user-data': {
            'task': 'personal_assistant.workers.tasks.file_tasks.backup_user_data',
            'schedule': crontab(day_of_week=0, hour=1, minute=0),  # Weekly on Sunday at 1 AM
        },

        # Sync tasks (new functionality)
        'sync-calendar-events': {
            'task': 'personal_assistant.workers.tasks.sync_tasks.sync_calendar_events',
            'schedule': crontab(minute=0),  # Every hour
        },
        'sync-notion-pages': {
            'task': 'personal_assistant.workers.tasks.sync_tasks.sync_notion_pages',
            'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
        },

        # Maintenance tasks (new functionality)
        'optimize-database': {
            'task': 'personal_assistant.workers.tasks.maintenance_tasks.optimize_database',
            'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Weekly on Sunday at 3 AM
        },
        'cleanup-old-sessions': {
            'task': 'personal_assistant.workers.tasks.maintenance_tasks.cleanup_old_sessions',
            'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
        },
    },

    # Task execution settings
    task_always_eager=False,  # Set to True for testing without Redis
    task_eager_propagates=True,

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour

    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

# Optional: Configure logging
logging.basicConfig(level=logging.INFO)
```

### **Phase 2: Implement New Task Types (Days 2-3)**

#### **Step 2.1: Email Processing Tasks**

```python
# workers/tasks/email_tasks.py
"""
Email Processing Background Tasks

This module handles email-related background tasks including:
- Processing email queues
- Sending scheduled notifications
- Email categorization and organization
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..celery_app import app
from ...database.models.users import User
from ...tools.emails.email_tool import EmailTool

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, default_retry_delay=300)
def process_email_queue(self) -> Dict[str, Any]:
    """
    Process email queue every 5 minutes.

    This task:
    1. Checks for new emails in the queue
    2. Processes and categorizes emails
    3. Updates user notifications
    4. Logs processing results
    """
    task_id = self.request.id
    logger.info(f"Starting email queue processing task {task_id}")

    try:
        # Initialize email tool
        email_tool = EmailTool()

        # Process email queue logic
        # TODO: Implement email queue processing

        result = {
            'task_id': task_id,
            'status': 'success',
            'emails_processed': 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Email queue processing completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Email queue processing failed: {e}")
        raise self.retry(countdown=300, max_retries=3)

@app.task(bind=True, max_retries=3, default_retry_delay=600)
def send_daily_email_summary(self) -> Dict[str, Any]:
    """
    Send daily email summary at 8 AM.

    This task:
    1. Generates daily summary reports
    2. Sends personalized summaries to users
    3. Tracks delivery status
    """
    task_id = self.request.id
    logger.info(f"Starting daily email summary task {task_id}")

    try:
        # TODO: Implement daily email summary logic

        result = {
            'task_id': task_id,
            'status': 'success',
            'summaries_sent': 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Daily email summary completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Daily email summary failed: {e}")
        raise self.retry(countdown=600, max_retries=3)
```

#### **Step 2.2: File Management Tasks**

```python
# workers/tasks/file_tasks.py
"""
File Management Background Tasks

This module handles file-related background tasks including:
- Temporary file cleanup
- User data backup
- File synchronization
"""

import logging
import os
import shutil
from datetime import datetime, timedelta
from typing import Any, Dict, List
from pathlib import Path

from ..celery_app import app

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, default_retry_delay=600)
def cleanup_temp_files(self) -> Dict[str, Any]:
    """
    Clean up temporary files daily at 2 AM.

    This task:
    1. Identifies temporary files older than 24 hours
    2. Removes expired temporary files
    3. Logs cleanup results
    """
    task_id = self.request.id
    logger.info(f"Starting temp file cleanup task {task_id}")

    try:
        temp_dirs = [
            '/tmp/personal_assistant',
            'logs/temp',
            'uploads/temp'
        ]

        files_removed = 0
        total_size_cleaned = 0

        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                # TODO: Implement temp file cleanup logic
                pass

        result = {
            'task_id': task_id,
            'status': 'success',
            'files_removed': files_removed,
            'size_cleaned_bytes': total_size_cleaned,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Temp file cleanup completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Temp file cleanup failed: {e}")
        raise self.retry(countdown=600, max_retries=3)

@app.task(bind=True, max_retries=3, default_retry_delay=3600)
def backup_user_data(self) -> Dict[str, Any]:
    """
    Backup user data weekly on Sunday at 1 AM.

    This task:
    1. Creates compressed backups of user data
    2. Stores backups in secure location
    3. Manages backup retention
    """
    task_id = self.request.id
    logger.info(f"Starting user data backup task {task_id}")

    try:
        # TODO: Implement user data backup logic

        result = {
            'task_id': task_id,
            'status': 'success',
            'backup_size_bytes': 0,
            'backup_location': '',
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"User data backup completed: {result}")
        return result

    except Exception as e:
        logger.error(f"User data backup failed: {e}")
        raise self.retry(countdown=3600, max_retries=3)
```

#### **Step 2.3: API Synchronization Tasks**

```python
# workers/tasks/sync_tasks.py
"""
API Synchronization Background Tasks

This module handles external API synchronization tasks including:
- Calendar event synchronization
- Notion page synchronization
- Email service synchronization
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..celery_app import app
from ...tools.calendar.calendar_tool import CalendarTool
from ...tools.notion_pages.notion_pages_tool import NotionPagesTool

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, default_retry_delay=300)
def sync_calendar_events(self) -> Dict[str, Any]:
    """
    Sync calendar events every hour.

    This task:
    1. Fetches new events from external calendars
    2. Updates local calendar database
    3. Resolves conflicts and duplicates
    4. Sends notifications for new events
    """
    task_id = self.request.id
    logger.info(f"Starting calendar sync task {task_id}")

    try:
        # Initialize calendar tool
        calendar_tool = CalendarTool()

        # TODO: Implement calendar synchronization logic

        result = {
            'task_id': task_id,
            'status': 'success',
            'events_synced': 0,
            'conflicts_resolved': 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Calendar sync completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Calendar sync failed: {e}")
        raise self.retry(countdown=300, max_retries=3)

@app.task(bind=True, max_retries=3, default_retry_delay=600)
def sync_notion_pages(self) -> Dict[str, Any]:
    """
    Sync Notion pages every 2 hours.

    This task:
    1. Fetches updated pages from Notion
    2. Updates local Notion database
    3. Handles page conflicts and updates
    4. Maintains bidirectional sync
    """
    task_id = self.request.id
    logger.info(f"Starting Notion sync task {task_id}")

    try:
        # Initialize Notion tool
        notion_tool = NotionPagesTool()

        # TODO: Implement Notion synchronization logic

        result = {
            'task_id': task_id,
            'status': 'success',
            'pages_synced': 0,
            'conflicts_resolved': 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Notion sync completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Notion sync failed: {e}")
        raise self.retry(countdown=600, max_retries=3)
```

#### **Step 2.4: System Maintenance Tasks**

```python
# workers/tasks/maintenance_tasks.py
"""
System Maintenance Background Tasks

This module handles system maintenance tasks including:
- Database optimization
- Log cleanup
- Session management
- Performance monitoring
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..celery_app import app
from ...database.database import get_db
from ...database.models.user_sessions import UserSession

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, default_retry_delay=3600)
def optimize_database(self) -> Dict[str, Any]:
    """
    Run database optimization weekly on Sunday at 3 AM.

    This task:
    1. Analyzes database performance
    2. Updates table statistics
    3. Optimizes indexes
    4. Cleans up unused data
    """
    task_id = self.request.id
    logger.info(f"Starting database optimization task {task_id}")

    try:
        # TODO: Implement database optimization logic

        result = {
            'task_id': task_id,
            'status': 'success',
            'tables_optimized': 0,
            'indexes_updated': 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Database optimization completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        raise self.retry(countdown=3600, max_retries=3)

@app.task(bind=True, max_retries=3, default_retry_delay=600)
def cleanup_old_sessions(self) -> Dict[str, Any]:
    """
    Clean up old user sessions daily at 4 AM.

    This task:
    1. Identifies expired user sessions
    2. Removes old session data
    3. Updates session statistics
    """
    task_id = self.request.id
    logger.info(f"Starting session cleanup task {task_id}")

    try:
        # TODO: Implement session cleanup logic

        result = {
            'task_id': task_id,
            'status': 'success',
            'sessions_cleaned': 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Session cleanup completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        raise self.retry(countdown=600, max_retries=3)
```

### **Phase 3: Enhanced Scheduling and Monitoring (Day 4)**

#### **Step 3.1: Separate Schedulers**

```python
# workers/schedulers/ai_scheduler.py
"""
AI Task Scheduler

This module handles AI-specific task scheduling logic,
separated from the general task execution.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from ...database.models.ai_tasks import AITask
from ...database.database import get_db

class AIScheduler:
    """Handles AI task scheduling and management."""

    async def get_due_tasks(self, limit: int = 50) -> List[AITask]:
        """Get AI tasks that are due for execution."""
        # TODO: Implement AI task scheduling logic
        pass

    async def calculate_next_run(self, schedule_type: str, schedule_config: Dict) -> datetime:
        """Calculate next run time for recurring AI tasks."""
        # TODO: Implement next run calculation logic
        pass
```

#### **Step 3.2: Enhanced Monitoring**

```python
# workers/utils/metrics.py
"""
Task Metrics Collection

This module provides task-specific metrics collection
for monitoring and performance analysis.
"""

import time
from datetime import datetime
from typing import Any, Dict
from functools import wraps

def track_task_metrics(task_name: str):
    """Decorator to track task execution metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_datetime = datetime.utcnow()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # TODO: Record success metrics
                record_task_success(task_name, execution_time, start_datetime)

                return result

            except Exception as e:
                execution_time = time.time() - start_time

                # TODO: Record failure metrics
                record_task_failure(task_name, execution_time, start_datetime, str(e))

                raise

        return wrapper
    return decorator

def record_task_success(task_name: str, execution_time: float, start_time: datetime):
    """Record successful task execution metrics."""
    # TODO: Implement metrics recording
    pass

def record_task_failure(task_name: str, execution_time: float, start_time: datetime, error: str):
    """Record failed task execution metrics."""
    # TODO: Implement metrics recording
    pass
```

### **Phase 4: Testing and Integration (Day 5)**

#### **Step 4.1: Unit Testing**

```python
# tests/workers/test_tasks.py
"""
Unit tests for background task system.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from personal_assistant.workers.tasks.ai_tasks import process_due_ai_tasks
from personal_assistant.workers.tasks.email_tasks import process_email_queue
from personal_assistant.workers.tasks.file_tasks import cleanup_temp_files

class TestAITasks:
    """Test AI task processing."""

    @patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager')
    def test_process_due_ai_tasks_success(self, mock_manager):
        """Test successful AI task processing."""
        # TODO: Implement test
        pass

    @patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager')
    def test_process_due_ai_tasks_failure(self, mock_manager):
        """Test AI task processing failure handling."""
        # TODO: Implement test
        pass

class TestEmailTasks:
    """Test email task processing."""

    @patch('personal_assistant.workers.tasks.email_tasks.EmailTool')
    def test_process_email_queue_success(self, mock_tool):
        """Test successful email queue processing."""
        # TODO: Implement test
        pass

class TestFileTasks:
    """Test file management tasks."""

    @patch('os.path.exists')
    def test_cleanup_temp_files_success(self, mock_exists):
        """Test successful temp file cleanup."""
        # TODO: Implement test
        pass
```

#### **Step 4.2: Docker Integration Updates**

```yaml
# docker/docker-compose.prod.yml (updated)
services:
  # AI Task Worker
  ai_worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: personal_assistant_ai_worker_prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - CELERY_BROKER_URL=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=ai_tasks",
        "--loglevel=info",
        "--concurrency=1",
        "--max-tasks-per-child=1000",
      ]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
        reservations:
          memory: 256M
          cpus: "0.25"

  # Email Task Worker
  email_worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: personal_assistant_email_worker_prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - CELERY_BROKER_URL=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=email_tasks",
        "--loglevel=info",
        "--concurrency=4",
        "--max-tasks-per-child=1000",
      ]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"
        reservations:
          memory: 512M
          cpus: "0.5"

  # File Task Worker
  file_worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: personal_assistant_file_worker_prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - CELERY_BROKER_URL=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=file_tasks",
        "--loglevel=info",
        "--concurrency=2",
        "--max-tasks-per-child=1000",
      ]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"
        reservations:
          memory: 512M
          cpus: "0.5"

  # Sync Task Worker
  sync_worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: personal_assistant_sync_worker_prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - CELERY_BROKER_URL=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=sync_tasks",
        "--loglevel=info",
        "--concurrency=2",
        "--max-tasks-per-child=1000",
      ]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"
        reservations:
          memory: 512M
          cpus: "0.5"

  # Maintenance Task Worker
  maintenance_worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: personal_assistant_maintenance_worker_prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - CELERY_BROKER_URL=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "worker",
        "--queues=maintenance_tasks",
        "--loglevel=info",
        "--concurrency=1",
        "--max-tasks-per-child=1000",
      ]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
        reservations:
          memory: 256M
          cpus: "0.25"

  # Celery Beat Scheduler (updated)
  scheduler:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: personal_assistant_scheduler_prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - CELERY_BROKER_URL=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0
    command:
      [
        "celery",
        "-A",
        "personal_assistant.workers.celery_app",
        "beat",
        "--loglevel=info",
      ]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - personal_assistant_prod_network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
        reservations:
          memory: 256M
          cpus: "0.25"
```

## **🔧 Migration Scripts**

### **Migration Script 1: Directory Structure Creation**

```bash
#!/bin/bash
# migrate_to_workers.sh

echo "Creating new workers directory structure..."

# Create new directories
mkdir -p src/personal_assistant/workers/{tasks,schedulers,utils}

# Create __init__.py files
touch src/personal_assistant/workers/__init__.py
touch src/personal_assistant/workers/tasks/__init__.py
touch src/personal_assistant/workers/schedulers/__init__.py
touch src/personal_assistant/workers/utils/__init__.py

echo "Directory structure created successfully!"
```

### **Migration Script 2: Code Migration**

```bash
#!/bin/bash
# migrate_ai_scheduler.sh

echo "Migrating AI scheduler to new workers structure..."

# Move AI scheduler files
mv src/personal_assistant/tools/ai_scheduler/ai_task_scheduler.py src/personal_assistant/workers/tasks/ai_tasks.py
mv src/personal_assistant/tools/ai_scheduler/task_executor.py src/personal_assistant/workers/tasks/ai_task_executor.py
mv src/personal_assistant/tools/ai_scheduler/task_scheduler.py src/personal_assistant/workers/schedulers/ai_scheduler.py

# Move utility files
mv src/personal_assistant/tools/ai_scheduler/health_monitor.py src/personal_assistant/workers/utils/health_monitor.py
mv src/personal_assistant/tools/ai_scheduler/performance_monitor.py src/personal_assistant/workers/utils/performance_monitor.py

echo "AI scheduler migration completed!"
```

## **📋 Implementation Checklist**

### **Phase 1: Reorganization (Day 1)**

- [ ] Create new directory structure
- [ ] Move AI scheduler code to new location
- [ ] Update imports and references
- [ ] Create central Celery application
- [ ] Test basic functionality

### **Phase 2: New Task Types (Days 2-3)**

- [ ] Implement email processing tasks
- [ ] Implement file management tasks
- [ ] Implement API synchronization tasks
- [ ] Implement system maintenance tasks
- [ ] Test individual task types

### **Phase 3: Enhanced Features (Day 4)**

- [ ] Separate schedulers for different task types
- [ ] Implement task-specific monitoring
- [ ] Add resource management features
- [ ] Update task routing configuration
- [ ] Test enhanced features

### **Phase 4: Testing & Integration (Day 5)**

- [ ] Write unit tests for all task types
- [ ] Perform integration testing
- [ ] Update Docker configurations
- [ ] Validate monitoring integration
- [ ] Final testing and validation

## **🚨 Risk Mitigation Strategies**

### **Migration Risks**

1. **Breaking Changes**: Implement backward compatibility layer
2. **Data Loss**: Create comprehensive backups before migration
3. **Service Disruption**: Plan migration during low-usage periods

### **Technical Risks**

1. **Performance Impact**: Monitor performance during transition
2. **Resource Usage**: Validate resource allocation for new worker types
3. **Error Handling**: Ensure robust error handling in new system

## **📈 Success Metrics**

### **Functional Metrics**

- ✅ All existing AI tasks continue to work
- ✅ New task types execute successfully
- ✅ Task routing works correctly
- ✅ Monitoring provides accurate metrics

### **Performance Metrics**

- ✅ Task execution time remains stable
- ✅ Resource usage is optimized per worker type
- ✅ Error rates remain low
- ✅ System scalability improves

### **Operational Metrics**

- ✅ Deployment process is streamlined
- ✅ Monitoring provides actionable insights
- ✅ Error handling is robust
- ✅ System maintenance is automated

This implementation plan provides a comprehensive roadmap for transforming the current AI-specific scheduler into a robust, general-purpose background task system while maintaining all existing functionality and improving the overall architecture.
