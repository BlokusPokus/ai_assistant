"""
AI Scheduler Package

This package provides core AI task management components.
The task execution functions have been migrated to the workers system.
"""

from .ai_task_manager import AITaskManager
# from .notification_service import NotificationService  # Commented out - file issues
# from .task_executor import TaskExecutor  # Commented out - file issues
# from .task_scheduler import TaskScheduler, create_task_scheduler  # Commented out - file issues

__version__ = '2.0.0'
__author__ = 'Personal Assistant Team'

__all__ = [
    # Core AI Task Management Components (still used by workers)
    'AITaskManager',
    # 'NotificationService',  # Commented out
    # 'TaskExecutor',  # Commented out
    # 'TaskScheduler',  # Commented out
    # 'create_task_scheduler',  # Commented out
]

# Convenience functions for common reminder operations


async def set_reminder(text: str, time: str, channel: str = "sms", user_id: int = 126) -> str:
    """Set a new reminder with validation and formatting."""
    task_manager = AITaskManager()
    result = await task_manager.create_reminder_with_validation(text, time, channel, user_id)
    return result['message']


async def list_reminders(status: str = "active", user_id: int = 126) -> str:
    """List user reminders with formatting."""
    task_manager = AITaskManager()
    result = await task_manager.list_user_reminders(status, user_id)
    return result['message']


async def delete_reminder(reminder_id: int, user_id: int = 126) -> str:
    """Delete a user reminder with validation."""
    task_manager = AITaskManager()
    result = await task_manager.delete_user_reminder(reminder_id, user_id)
    return result['message']
