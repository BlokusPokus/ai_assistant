"""
Background Task Modules

This package contains all background task implementations for the Personal Assistant.
"""

# Import all task modules
from . import ai_tasks, email_tasks, file_tasks, maintenance_tasks, sync_tasks

# Create task registry for test compatibility
TASK_REGISTRY = {
    "ai_tasks": ai_tasks,
    "email_tasks": email_tasks,
    "file_tasks": file_tasks,
    "maintenance_tasks": maintenance_tasks,
    "sync_tasks": sync_tasks,
}

__all__ = [
    "ai_tasks",
    "email_tasks",
    "file_tasks",
    "sync_tasks",
    "maintenance_tasks",
    "TASK_REGISTRY",
]
