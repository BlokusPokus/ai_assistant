"""Enhanced logging utilities for the agent core system."""

import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
from datetime import datetime


@contextmanager
def agent_context_logger(logger: logging.Logger, user_id: int, operation: str):
    """
    Context manager for enhanced logging with user context.

    Args:
        logger: The logger instance to use
        user_id: The user ID for context
        operation: The operation being performed

    Yields:
        None

    Raises:
        Exception: Re-raises any exception that occurs during execution
    """
    start_time = time.time()
    logger.info(f"Starting {operation} for user {user_id}")

    try:
        yield
    except Exception as e:
        logger.error(
            f"Error during {operation} for user {user_id}: {str(e)}",
            extra={
                "user_id": user_id,
                "operation": operation,
                "error": str(e),
                "duration": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat()
            },
            exc_info=True
        )
        raise
    else:
        duration = time.time() - start_time
        logger.info(
            f"Completed {operation} for user {user_id}",
            extra={
                "user_id": user_id,
                "operation": operation,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


def log_agent_operation(logger: logging.Logger, user_id: int, operation: str,
                        details: Optional[Dict[str, Any]] = None, level: str = "info"):
    """
    Log agent operations with consistent formatting and context.

    Args:
        logger: The logger instance to use
        user_id: The user ID for context
        operation: The operation being performed
        details: Optional additional details to log
        level: Log level (info, warning, error, debug)
    """
    log_data = {
        "user_id": user_id,
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat()
    }

    if details:
        log_data.update(details)

    if level == "info":
        logger.info(
            f"Agent operation: {operation} for user {user_id}", extra=log_data)
    elif level == "warning":
        logger.warning(
            f"Agent operation: {operation} for user {user_id}", extra=log_data)
    elif level == "error":
        logger.error(
            f"Agent operation: {operation} for user {user_id}", extra=log_data)
    elif level == "debug":
        logger.debug(
            f"Agent operation: {operation} for user {user_id}", extra=log_data)


def log_error_with_context(logger: logging.Logger, error: Exception, user_id: int,
                           operation: str, additional_context: Optional[Dict[str, Any]] = None):
    """
    Log errors with comprehensive context information.

    Args:
        logger: The logger instance to use
        error: The exception that occurred
        user_id: The user ID for context
        operation: The operation being performed
        additional_context: Optional additional context information
    """
    error_data = {
        "user_id": user_id,
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }

    if additional_context:
        error_data.update(additional_context)

    logger.error(
        f"Error in {operation} for user {user_id}: {str(error)}",
        extra=error_data,
        exc_info=True
    )


def log_performance_metrics(logger: logging.Logger, user_id: int, operation: str,
                            duration: float, success: bool, metadata: Optional[Dict[str, Any]] = None):
    """
    Log performance metrics for agent operations.

    Args:
        logger: The logger instance to use
        user_id: The user ID for context
        operation: The operation being performed
        duration: Duration of the operation in seconds
        success: Whether the operation was successful
        metadata: Optional additional metadata
    """
    metrics_data = {
        "user_id": user_id,
        "operation": operation,
        "duration": duration,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }

    if metadata:
        metrics_data.update(metadata)

    if success:
        logger.info(f"Performance: {operation} completed in {duration:.3f}s for user {user_id}",
                    extra=metrics_data)
    else:
        logger.warning(f"Performance: {operation} failed after {duration:.3f}s for user {user_id}",
                       extra=metrics_data)
