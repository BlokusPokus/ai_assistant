"""
AI Scheduler Package

This package provides a comprehensive AI task management system with clear
separation of concerns across different functional areas.

Structure:
- core/: Core business logic (task management, scheduling, execution)
- evaluation/: AI evaluation components (event analysis, context building)
- notifications/: Notification system components
- utils/: Utility functions and convenience helpers
"""

# Core components
from .core import AITaskManager, TaskScheduler, create_task_scheduler, TaskExecutor

# Evaluation components  
from .evaluation import AIEventEvaluator, create_ai_evaluator, EventContext, EventContextBuilder, EventEvaluationEngine

# Notification components
from .notifications import NotificationService

# Utility functions
from .utils import set_reminder, list_reminders, delete_reminder

__version__ = "3.0.0"
__author__ = "Personal Assistant Team"

__all__ = [
    # Core components
    "AITaskManager",
    "TaskScheduler",
    "create_task_scheduler", 
    "TaskExecutor",
    
    # Evaluation components
    "AIEventEvaluator",
    "create_ai_evaluator",
    "EventContext",
    "EventContextBuilder",
    "EventEvaluationEngine",
    
    # Notification components
    "NotificationService",
    
    # Utility functions
    "set_reminder",
    "list_reminders",
    "delete_reminder",
]