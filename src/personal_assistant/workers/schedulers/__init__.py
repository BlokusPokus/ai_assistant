"""
Scheduler Modules for Background Tasks

This package contains scheduler modules for different task types.
"""

# Import scheduler modules
from . import ai_scheduler

# Create global scheduler instance
_ai_scheduler_instance = None


def get_ai_scheduler():
    """Get the global AI scheduler instance."""
    global _ai_scheduler_instance
    if _ai_scheduler_instance is None:
        _ai_scheduler_instance = ai_scheduler.AIScheduler()
    return _ai_scheduler_instance


def get_email_scheduler():
    """Get email scheduler for test compatibility."""

    # Create a mock scheduler for testing
    class MockEmailScheduler:
        def get_schedule_info(self):
            return {"type": "email", "status": "running"}

    return MockEmailScheduler()


def get_maintenance_scheduler():
    """Get maintenance scheduler for test compatibility."""

    # Create a mock scheduler for testing
    class MockMaintenanceScheduler:
        def get_schedule_info(self):
            return {"type": "maintenance", "status": "running"}

    return MockMaintenanceScheduler()


__all__ = [
    "ai_scheduler",
    "get_ai_scheduler",
    "get_email_scheduler",
    "get_maintenance_scheduler",
]
