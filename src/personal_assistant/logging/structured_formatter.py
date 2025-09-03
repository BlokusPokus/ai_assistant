"""
Structured JSON logging formatter for the personal assistant framework.

📁 logging/structured_formatter.py
Provides structured JSON logging with correlation IDs, user context,
and metadata for enhanced observability and debugging.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging with correlation IDs and metadata.

    Converts log records to structured JSON format with:
    - Timestamp in ISO format
    - Log level and logger name
    - Message content
    - Correlation ID for request tracing
    - User context and operation details
    - Service and module identification
    - Custom metadata
    """

    def __init__(self, include_extra_fields: bool = True):
        """
        Initialize the structured JSON formatter.

        Args:
            include_extra_fields: Whether to include extra fields from log records
        """
        super().__init__()
        self.include_extra_fields = include_extra_fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as structured JSON.

        Args:
            record: The log record to format

        Returns:
            JSON string representation of the log record
        """
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "personal_assistant",
            "module": self._extract_module_name(record.name),
        }

        # Add correlation ID if available
        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        # Add user context if available
        user_id = getattr(record, "user_id", None)
        if user_id is not None:
            log_entry["user_id"] = user_id

        # Add operation context if available
        operation = getattr(record, "operation", None)
        if operation:
            log_entry["operation"] = operation

        # Add thread and process information
        log_entry["thread"] = record.thread
        log_entry["process"] = record.process

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
                if record.exc_info
                else None,
            }

        # Add custom metadata if available
        metadata = getattr(record, "metadata", {})
        if metadata:
            log_entry["metadata"] = metadata

        # Add performance metrics if available
        duration = getattr(record, "duration", None)
        if duration is not None:
            log_entry["duration_ms"] = round(duration * 1000, 2)

        # Add extra fields if enabled
        if self.include_extra_fields:
            extra_fields = self._extract_extra_fields(record)
            if extra_fields:
                log_entry.update(extra_fields)

        # Add security level for audit logs
        security_level = getattr(record, "security_level", None)
        if security_level:
            log_entry["security_level"] = security_level

        return json.dumps(log_entry, ensure_ascii=False, separators=(",", ":"))

    def _extract_module_name(self, logger_name: str) -> str:
        """
        Extract module name from logger name.

        Args:
            logger_name: Full logger name (e.g., 'personal_assistant.core')

        Returns:
            Module name (e.g., 'core')
        """
        if "." in logger_name:
            return logger_name.split(".")[-1]
        return logger_name

    def _extract_extra_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        Extract extra fields from log record that aren't standard logging fields.

        Args:
            record: The log record

        Returns:
            Dictionary of extra fields
        """
        extra_fields = {}

        # Get all attributes of the record
        for key, value in record.__dict__.items():
            # Skip standard logging fields
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "correlation_id",
                "user_id",
                "operation",
                "metadata",
                "duration",
                "security_level",
            }:
                # Only include serializable values
                try:
                    json.dumps(value)
                    extra_fields[key] = value
                except (TypeError, ValueError):
                    # Convert non-serializable values to strings
                    extra_fields[key] = str(value)

        return extra_fields


class CorrelationContext:
    """
    Context manager for storing and retrieving correlation IDs across requests.
    """

    def __init__(self):
        self._context = {}

    def set_correlation_id(self, correlation_id: str) -> None:
        """
        Set the correlation ID for the current context.

        Args:
            correlation_id: Unique correlation ID
        """
        import threading

        thread_id = threading.get_ident()
        self._context[thread_id] = correlation_id

    def get_correlation_id(self) -> Optional[str]:
        """
        Get the correlation ID for the current context.

        Returns:
            Correlation ID if set, None otherwise
        """
        import threading

        thread_id = threading.get_ident()
        return self._context.get(thread_id)

    def clear_correlation_id(self) -> None:
        """
        Clear the correlation ID for the current context.
        """
        import threading

        thread_id = threading.get_ident()
        self._context.pop(thread_id, None)


# Global correlation context instance
correlation_context = CorrelationContext()


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID.

    Returns:
        Current correlation ID if set, None otherwise
    """
    return correlation_context.get_correlation_id()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current context.

    Args:
        correlation_id: Unique correlation ID
    """
    correlation_context.set_correlation_id(correlation_id)


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.

    Returns:
        New unique correlation ID
    """
    return str(uuid.uuid4())


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    user_id: Optional[int] = None,
    operation: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> None:
    """
    Log a message with automatic context injection.

    Args:
        logger: Logger instance
        level: Log level (info, warning, error, etc.)
        message: Log message
        user_id: User ID for context
        operation: Operation being performed
        metadata: Additional metadata
        **kwargs: Additional fields to include in log
    """
    extra = {
        "correlation_id": get_correlation_id(),
        "user_id": user_id,
        "operation": operation,
        "metadata": metadata or {},
    }

    # Add any additional kwargs
    extra.update(kwargs)

    # Get the logging method
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, extra=extra)
