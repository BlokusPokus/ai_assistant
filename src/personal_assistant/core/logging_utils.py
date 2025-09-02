"""Enhanced logging utilities for the agent core system."""

import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
from datetime import datetime

# Import structured logging utilities
try:
    from ..logging import get_correlation_id, log_with_context
    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False


@contextmanager
def agent_context_logger(logger: logging.Logger, user_id: int, operation: str, **kwargs):
    """
    Context manager for enhanced logging with user context and correlation IDs.

    Args:
        logger: The logger instance to use
        user_id: The user ID for context
        operation: The operation being performed
        **kwargs: Additional metadata to include in logs

    Yields:
        None

    Raises:
        Exception: Re-raises any exception that occurs during execution
    """
    start_time = time.time()

    # Enhanced logging with correlation ID and structured metadata
    if STRUCTURED_LOGGING_AVAILABLE:
        log_with_context(
            logger, "info", f"Starting {operation} for user {user_id}",
            user_id=user_id, operation=operation, metadata=kwargs
        )
    else:
        logger.info(f"Starting {operation} for user {user_id}")

    try:
        yield
    except Exception as e:
        duration = time.time() - start_time
        error_metadata = {
            "error": str(e),
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }

        if STRUCTURED_LOGGING_AVAILABLE:
            log_with_context(
                logger, "error", f"Error during {operation} for user {user_id}: {str(e)}",
                user_id=user_id, operation=operation, metadata=error_metadata
            )
        else:
            logger.error(
                f"Error during {operation} for user {user_id}: {str(e)}",
                extra=error_metadata,
                exc_info=True
            )
        raise
    else:
        duration = time.time() - start_time
        success_metadata = {
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }

        if STRUCTURED_LOGGING_AVAILABLE:
            log_with_context(
                logger, "info", f"Completed {operation} for user {user_id}",
                user_id=user_id, operation=operation, metadata=success_metadata
            )
        else:
            logger.info(
                f"Completed {operation} for user {user_id}",
                extra=success_metadata
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
    message = f"Agent operation: {operation} for user {user_id}"

    if STRUCTURED_LOGGING_AVAILABLE:
        log_with_context(
            logger, level, message,
            user_id=user_id, operation=operation, metadata=details or {}
        )
    else:
        log_data = {
            "user_id": user_id,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat()
        }

        if details:
            log_data.update(details)

        if level == "info":
            logger.info(message, extra=log_data)
        elif level == "warning":
            logger.warning(message, extra=log_data)
        elif level == "error":
            logger.error(message, extra=log_data)
        elif level == "debug":
            logger.debug(message, extra=log_data)


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
    level = "info" if success else "warning"
    message = f"Performance: {operation} {'completed' if success else 'failed'} in {duration:.3f}s for user {user_id}"

    performance_metadata = {
        "duration": duration,
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
        **(metadata or {})
    }

    if STRUCTURED_LOGGING_AVAILABLE:
        log_with_context(
            logger, level, message,
            user_id=user_id, operation=operation, metadata=performance_metadata
        )
    else:
        metrics_data = {
            "user_id": user_id,
            "operation": operation,
            **performance_metadata
        }

        if success:
            logger.info(message, extra=metrics_data)
        else:
            logger.warning(message, extra=metrics_data)
