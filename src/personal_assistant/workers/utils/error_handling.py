"""
Centralized Error Handling Utilities

This module provides centralized error handling for the background task system.
"""

import logging
import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class TaskErrorHandler:
    """
    Centralized error handler for background tasks.

    This is a simplified version that will be enhanced in Task 037.2.
    """

    def __init__(self):
        self.error_callbacks = {}
        self.error_history = []

    def register_error_callback(self, error_type: str, callback: Callable):
        """Register a callback function for specific error types."""
        self.error_callbacks[error_type] = callback
        logger.info(f"Registered error callback for {error_type}")

    def handle_task_error(
        self,
        task_name: str,
        task_id: str,
        error: Exception,
        context: Dict[str, Any] | None = None,
    ):
        """Handle a task error with centralized logic."""
        error_record = {
            "task_name": task_name,
            "task_id": task_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "timestamp": datetime.utcnow(),
        }

        self.error_history.append(error_record)

        # Log the error
        logger.error(f"Task {task_name} ({task_id}) failed: {error}")
        logger.error(f"Error context: {context}")
        logger.debug(f"Full traceback: {error_record['traceback']}")

        # Execute error callbacks if registered
        error_type = type(error).__name__
        if error_type in self.error_callbacks:
            try:
                self.error_callbacks[error_type](error_record)
            except Exception as callback_error:
                logger.error(f"Error callback failed: {callback_error}")

        return error_record

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get a summary of recent errors."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if e["timestamp"] > cutoff_time]

        error_types: dict[str, int] = {}
        for error in recent_errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": len(recent_errors),
            "error_types": error_types,
            "time_window_hours": hours,
        }

    def clear_old_errors(self, days: int = 7):
        """Clear errors older than specified days."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        self.error_history = [
            e for e in self.error_history if e["timestamp"] > cutoff_time
        ]
        logger.info(f"Cleared errors older than {days} days")


def handle_task_errors(task_name: str | None = None):
    """
    Decorator to handle task errors with centralized error handling.

    This is a simplified version that will be enhanced in Task 037.2.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract task name from function or decorator parameter
            actual_task_name = task_name or func.__name__

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get task_id from self if it's a bound method
                task_id = (
                    getattr(args[0], "request", {}).get("id", "unknown")
                    if args
                    else "unknown"
                )

                # Handle the error
                error_handler.handle_task_error(
                    task_name=actual_task_name,
                    task_id=task_id,
                    error=e,
                    context={"args": args, "kwargs": kwargs},
                )

                # Re-raise the exception for Celery to handle
                raise

        return wrapper

    return decorator


def retry_on_error(max_retries: int = 3, delay: int = 60):
    """
    Decorator to automatically retry tasks on error.

    This is a simplified version that will be enhanced in Task 037.2.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Task {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                        )
                        # In a real implementation, this would use Celery's retry mechanism
                        import time

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Task {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise last_exception

        return wrapper

    return decorator


# Global error handler instance
error_handler = TaskErrorHandler()
