"""
Task Monitoring Utilities

This module provides basic task monitoring capabilities for the background task system.
"""

import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def track_task_execution(task_name: str):
    """
    Decorator to track basic task execution metrics.

    This is a simplified version that will be enhanced in Task 037.2.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_datetime = datetime.utcnow()

            logger.info(f"Task {task_name} started at {start_datetime}")

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                logger.info(
                    f"Task {task_name} completed successfully in {execution_time:.2f}s"
                )
                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Task {task_name} failed after {execution_time:.2f}s: {e}"
                )
                raise

        return wrapper

    return decorator


class TaskMonitor:
    """
    Basic task monitoring class for tracking task execution.

    This is a simplified version that will be enhanced in Task 037.2.
    """

    def __init__(self):
        self.task_history = []
        self.failed_tasks = []

    def record_task_start(self, task_name: str, task_id: str):
        """Record the start of a task execution."""
        record = {
            "task_name": task_name,
            "task_id": task_id,
            "start_time": datetime.utcnow(),
            "status": "running",
        }
        self.task_history.append(record)
        logger.info(f"Task {task_name} ({task_id}) started")

    def record_task_success(self, task_name: str, task_id: str, execution_time: float):
        """Record the successful completion of a task."""
        for record in self.task_history:
            if record["task_id"] == task_id:
                record["status"] = "completed"
                record["execution_time"] = execution_time
                record["end_time"] = datetime.utcnow()
                break

        logger.info(f"Task {task_name} ({task_id}) completed in {execution_time:.2f}s")

    def record_task_failure(
        self, task_name: str, task_id: str, execution_time: float, error: str
    ):
        """Record the failure of a task."""
        for record in self.task_history:
            if record["task_id"] == task_id:
                record["status"] = "failed"
                record["execution_time"] = execution_time
                record["end_time"] = datetime.utcnow()
                record["error"] = error
                break

        failure_record = {
            "task_name": task_name,
            "task_id": task_id,
            "execution_time": execution_time,
            "error": error,
            "timestamp": datetime.utcnow(),
        }
        self.failed_tasks.append(failure_record)

        logger.error(
            f"Task {task_name} ({task_id}) failed after {execution_time:.2f}s: {error}"
        )

    def get_task_summary(self) -> Dict[str, Any]:
        """Get a summary of task execution history."""
        total_tasks = len(self.task_history)
        completed_tasks = len(
            [r for r in self.task_history if r.get("status") == "completed"]
        )
        failed_tasks = len(
            [r for r in self.task_history if r.get("status") == "failed"]
        )
        running_tasks = len(
            [r for r in self.task_history if r.get("status") == "running"]
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "success_rate": (completed_tasks / total_tasks * 100)
            if total_tasks > 0
            else 0,
        }

    def get_recent_failures(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent task failures within the specified time window."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_failures = [f for f in self.failed_tasks if f["timestamp"] > cutoff_time]
        return recent_failures


# Global task monitor instance
task_monitor = TaskMonitor()
