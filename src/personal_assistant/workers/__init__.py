"""
Personal Assistant Background Task System

This package provides a comprehensive background task system for the Personal Assistant,
including AI tasks, email processing, file management, API synchronization, and system maintenance.
"""

__version__ = "1.0.0"
__author__ = "Personal Assistant Team"

# Import main components
from .celery_app import app

# Import task modules
from .tasks import ai_tasks, email_tasks, file_tasks, sync_tasks, maintenance_tasks

# Import utility modules
from .utils import task_monitoring, error_handling, health_check

# Import scheduler modules
from .schedulers import ai_scheduler

__all__ = [
    'app',
    'ai_tasks',
    'email_tasks',
    'file_tasks',
    'sync_tasks',
    'maintenance_tasks',
    'task_monitoring',
    'error_handling',
    'health_check',
    'ai_scheduler'
]
