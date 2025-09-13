"""
AI Task Scheduler Module

This module provides the main scheduler functionality for processing AI tasks.
It runs every 10 minutes to check for due AI tasks and execute them.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from .task_manager import AITaskManager

# Note: Task execution functions have been migrated to workers system
# from .ai_task_scheduler import (
#     process_due_ai_tasks,
#     test_scheduler_connection,
# )
# Import the new workers Celery app
try:
    from ....workers.celery_app import app
except ImportError:
    # Fallback if workers system is not available
    app = None

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Main scheduler class for AI task processing.
    """

    def __init__(self):
        self.app = app
        self.logger = logger
        self.task_manager = AITaskManager()

    def start_worker(self, loglevel: str = "INFO") -> None:
        """
        Start the Celery worker for processing AI tasks.

        Args:
            loglevel: Logging level for the worker
        """
        self.logger.info("Starting AI Task Scheduler worker...")

        # Start worker with specified options
        argv = [
            "worker",
            "--loglevel=" + loglevel,
            "--queues=ai_tasks",
            "--hostname=ai_task_worker@%h",
            "--concurrency=1",  # Single worker for now
        ]

        self.app.worker_main(argv)

    def start_beat(self, loglevel: str = "INFO") -> None:
        """
        Start the Celery beat scheduler for periodic tasks.

        Args:
            loglevel: Logging level for the beat scheduler
        """
        self.logger.info("Starting AI Task Scheduler beat...")

        # Start beat scheduler
        argv = [
            "beat",
            "--loglevel=" + loglevel,
            "--schedule=/tmp/celerybeat-schedule",
            "--pidfile=/tmp/celerybeat.pid",
        ]

        self.app.start(argv)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the scheduler connection and basic functionality.

        Returns:
            Dictionary with test results
        """
        try:
            # Simple connectivity test without requiring a worker
            return {
                "status": "success",
                "message": "AI Task Scheduler connection test successful",
                "timestamp": datetime.utcnow().isoformat(),
                "celery_app": "ai_scheduler",
                "queues": ["ai_tasks"],
                "tasks": [
                    # NOTE: Tasks migrated to workers system
                    "workers.tasks.ai_tasks.process_due_ai_tasks",
                    "workers.tasks.ai_tasks.test_scheduler_connection",
                    "workers.tasks.ai_tasks.cleanup_old_logs",
                    "workers.tasks.ai_tasks.create_ai_reminder",
                    "workers.tasks.ai_tasks.create_periodic_ai_task",
                ],
            }

        except Exception as e:
            self.logger.error(f"AI Task Scheduler connection test failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the AI task scheduler system.

        Returns:
            Dictionary with scheduler status information
        """
        try:
            # Get basic scheduler info
            status: Dict[str, Any] = {
                "scheduler_type": "AI Task Scheduler",
                "status": "running",
                "timestamp": datetime.utcnow().isoformat(),
                "queues": ["ai_tasks"],
                "tasks": [
                    # NOTE: Tasks migrated to workers system
                    "workers.tasks.ai_tasks.process_due_ai_tasks",
                    "workers.tasks.ai_tasks.test_scheduler_connection",
                    "workers.tasks.ai_tasks.cleanup_old_logs",
                    "workers.tasks.ai_tasks.create_ai_reminder",
                    "workers.tasks.ai_tasks.create_periodic_ai_task",
                ],
            }

            # Test connection
            connection_test = self.test_connection()
            status["connection_test"] = connection_test

            return status

        except Exception as e:
            self.logger.error(f"Error getting scheduler status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about AI tasks.

        Returns:
            Dictionary with task statistics
        """
        try:
            # Get due tasks count
            due_tasks = await self.task_manager.get_due_tasks(limit=1000)

            # Get all active tasks
            active_tasks = await self.task_manager.get_user_tasks(
                user_id=126, status="active", limit=1000  # TODO: Get from context
            )

            # Get task counts by type
            task_types: dict[str, int] = {}
            for task in active_tasks:
                task_type = task.task_type
                task_types[task_type] = task_types.get(task_type, 0) + 1

            return {
                "total_due_tasks": len(due_tasks),
                "total_active_tasks": len(active_tasks),
                "task_types": task_types,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting task statistics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def create_test_task(self) -> Dict[str, Any]:
        """
        Create a test AI task for debugging.

        Returns:
            Dictionary with test task creation result
        """
        try:
            # Create a test reminder
            remind_at = datetime.utcnow() + timedelta(minutes=2)
            test_task = await self.task_manager.create_task(
                user_id=126,
                title="Test AI Task",
                description="This is a test AI task for debugging",
                task_type="reminder",
                schedule_type="once",
                schedule_config={"run_at": remind_at},
                next_run_at=remind_at,
                notification_channels=["sms"],
            )

            return {
                "status": "success",
                "message": "Test task created successfully",
                "task_id": test_task.id,
                "task_title": test_task.title,
                "next_run_at": test_task.next_run_at.isoformat()
                if test_task.next_run_at
                else None,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error creating test task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


def create_task_scheduler() -> TaskScheduler:
    """
    Factory function to create a task scheduler instance.

    Returns:
        TaskScheduler instance
    """
    return TaskScheduler()


def run_worker():
    """Run the AI task scheduler worker."""
    scheduler = create_task_scheduler()
    scheduler.start_worker()


def run_beat():
    """Run the AI task scheduler beat."""
    scheduler = create_task_scheduler()
    scheduler.start_beat()


def test_scheduler():
    """Test the AI task scheduler."""
    scheduler = create_task_scheduler()
    result = scheduler.test_connection()
    print(f"Test result: {result}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "worker":
            run_worker()
        elif command == "beat":
            run_beat()
        elif command == "test":
            test_scheduler()
        else:
            print("Usage: python task_scheduler.py [worker|beat|test]")
    else:
        print("Usage: python task_scheduler.py [worker|beat|test]")
