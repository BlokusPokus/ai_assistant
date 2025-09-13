"""
Background Task Modules

This package contains all background task implementations for the Personal Assistant.
"""

# Import all task modules
from . import ai_tasks

# Create task registry for test compatibility
TASK_REGISTRY = {
    "ai_tasks": ai_tasks,
}

__all__ = [
    "ai_tasks",
    "TASK_REGISTRY",
]
