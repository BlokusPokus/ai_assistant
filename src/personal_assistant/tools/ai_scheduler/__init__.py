"""
AI Scheduler Package

This package provides automated AI task scheduling and execution using a database-first approach.
It includes a scheduler that runs every 10 minutes to check for due AI tasks and
execute them using the AI assistant with SMS notifications.
"""

from .ai_task_manager import AITaskManager
from .ai_task_scheduler import (
    cleanup_old_logs,
    create_ai_reminder,
    create_periodic_ai_task,
    process_due_ai_tasks,
    test_scheduler_connection,
)
from .notification_service import NotificationService
from .task_executor import TaskExecutor
from .task_scheduler import TaskScheduler, create_task_scheduler

__version__ = '2.0.0'
__author__ = 'Personal Assistant Team'

__all__ = [
    # AI Task Scheduler components
    'process_due_ai_tasks',
    'test_scheduler_connection',
    'cleanup_old_logs',
    'create_ai_reminder',
    'create_periodic_ai_task',

    # AI Task Management
    'AITaskManager',
    'NotificationService',
    'TaskExecutor',
    'TaskScheduler',
    'create_task_scheduler',
]
