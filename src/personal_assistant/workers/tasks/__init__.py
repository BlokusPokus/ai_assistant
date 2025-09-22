"""
Background Task Modules

This package contains all background task implementations for the Personal Assistant.
"""

# Import all task modules
from . import ai_tasks
from . import sms_tasks
from . import grocery_tasks

# Create task registry for test compatibility
TASK_REGISTRY = {
    "ai_tasks": ai_tasks,
    "sms_tasks": sms_tasks,
    "grocery_tasks": grocery_tasks,
}

__all__ = [
    "ai_tasks",
    "sms_tasks", 
    "grocery_tasks",
    "TASK_REGISTRY",
]
