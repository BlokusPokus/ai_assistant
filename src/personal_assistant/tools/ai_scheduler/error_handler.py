"""
Error handling and recovery for the AI-first calendar scheduler system.

This module provides comprehensive error handling and recovery mechanisms
for workflow execution and system operations.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from .db_queries import mark_event_failed

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur."""
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_ERROR = "resource_error"
    GENERAL_ERROR = "general_error"


@dataclass
class ErrorInfo:
    """Information about an error."""
    event_id: int
    error_type: ErrorType
    error_message: str
    timestamp: datetime
    context: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3


class ErrorHandler:
    """
    Handle errors and implement recovery mechanisms.

    This class provides comprehensive error handling and recovery
    strategies for different types of errors.
    """

    def __init__(self):
        self.logger = logger
        self.error_history: List[ErrorInfo] = []
        self.retry_delays = {
            ErrorType.CONNECTION_ERROR: 60,  # 1 minute
            ErrorType.TIMEOUT_ERROR: 30,      # 30 seconds
            ErrorType.VALIDATION_ERROR: 0,    # No retry
            ErrorType.PERMISSION_ERROR: 0,    # No retry
            ErrorType.RESOURCE_ERROR: 120,    # 2 minutes
            ErrorType.GENERAL_ERROR: 60       # 1 minute
        }

    async def handle_workflow_error(self, event_id: int, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workflow errors with recovery.

        Args:
            event_id: ID of the event that caused the error
            error: The exception that occurred
            context: Additional context about the error

        Returns:
            Dictionary with error handling results
        """
        # Determine error type
        error_type = self._classify_error(error)

        # Create error info
        error_info = ErrorInfo(
            event_id=event_id,
            error_type=error_type,
            error_message=str(error),
            timestamp=datetime.utcnow(),
            context=context
        )

        # Log the error
        self.logger.error(
            f"Workflow error for event {event_id}: {error} (Type: {error_type.value})")

        # Store error info
        self.error_history.append(error_info)

        # Handle based on error type
        if error_type == ErrorType.CONNECTION_ERROR:
            return await self._handle_connection_error(event_id, error_info)
        elif error_type == ErrorType.TIMEOUT_ERROR:
            return await self._handle_timeout_error(event_id, error_info)
        elif error_type == ErrorType.VALIDATION_ERROR:
            return await self._handle_validation_error(event_id, error_info)
        elif error_type == ErrorType.PERMISSION_ERROR:
            return await self._handle_permission_error(event_id, error_info)
        elif error_type == ErrorType.RESOURCE_ERROR:
            return await self._handle_resource_error(event_id, error_info)
        else:
            return await self._handle_general_error(event_id, error_info)

    def _classify_error(self, error: Exception) -> ErrorType:
        """
        Classify the type of error based on the exception.

        Args:
            error: The exception to classify

        Returns:
            ErrorType classification
        """
        error_message = str(error).lower()

        # Connection errors
        if any(word in error_message for word in ['connection', 'network', 'unreachable', 'refused']):
            return ErrorType.CONNECTION_ERROR

        # Timeout errors
        if any(word in error_message for word in ['timeout', 'timed out', 'deadline']):
            return ErrorType.TIMEOUT_ERROR

        # Validation errors
        if any(word in error_message for word in ['validation', 'invalid', 'malformed', 'format']):
            return ErrorType.VALIDATION_ERROR

        # Permission errors
        if any(word in error_message for word in ['permission', 'unauthorized', 'forbidden', 'access denied']):
            return ErrorType.PERMISSION_ERROR

        # Resource errors
        if any(word in error_message for word in ['resource', 'memory', 'disk', 'quota', 'limit']):
            return ErrorType.RESOURCE_ERROR

        # Default to general error
        return ErrorType.GENERAL_ERROR

    async def _handle_connection_error(self, event_id: int, error_info: ErrorInfo) -> Dict[str, Any]:
        """
        Handle connection errors with retry.

        Args:
            event_id: ID of the event
            error_info: Error information

        Returns:
            Dictionary with handling results
        """
        # Check if we should retry
        if error_info.retry_count < error_info.max_retries:
            retry_delay = self.retry_delays[ErrorType.CONNECTION_ERROR]

            self.logger.info(
                f"Connection error for event {event_id}, will retry in {retry_delay}s (attempt {error_info.retry_count + 1}/{error_info.max_retries})")

            # Mark for retry (don't mark as failed yet)
            return {
                'handled': True,
                'action': 'retry',
                'retry_delay': retry_delay,
                'retry_count': error_info.retry_count + 1,
                'message': f'Connection error, will retry in {retry_delay}s'
            }
        else:
            # Max retries exceeded, mark as failed
            await mark_event_failed(event_id, f"Connection error after {error_info.max_retries} retries: {error_info.error_message}")

            self.logger.error(
                f"Event {event_id} failed after {error_info.max_retries} connection retries")

            return {
                'handled': True,
                'action': 'failed',
                'message': f'Connection error after {error_info.max_retries} retries'
            }

    async def _handle_timeout_error(self, event_id: int, error_info: ErrorInfo) -> Dict[str, Any]:
        """
        Handle timeout errors.

        Args:
            event_id: ID of the event
            error_info: Error information

        Returns:
            Dictionary with handling results
        """
        retry_delay = self.retry_delays[ErrorType.TIMEOUT_ERROR]

        if error_info.retry_count < error_info.max_retries:
            self.logger.warning(
                f"Timeout error for event {event_id}, will retry in {retry_delay}s")

            return {
                'handled': True,
                'action': 'retry',
                'retry_delay': retry_delay,
                'retry_count': error_info.retry_count + 1,
                'message': f'Timeout error, will retry in {retry_delay}s'
            }
        else:
            await mark_event_failed(event_id, f"Timeout error after {error_info.max_retries} retries: {error_info.error_message}")

            self.logger.error(
                f"Event {event_id} failed after {error_info.max_retries} timeout retries")

            return {
                'handled': True,
                'action': 'failed',
                'message': f'Timeout error after {error_info.max_retries} retries'
            }

    async def _handle_validation_error(self, event_id: int, error_info: ErrorInfo) -> Dict[str, Any]:
        """
        Handle validation errors (no retry).

        Args:
            event_id: ID of the event
            error_info: Error information

        Returns:
            Dictionary with handling results
        """
        await mark_event_failed(event_id, f"Validation error: {error_info.error_message}")

        self.logger.error(
            f"Validation error for event {event_id}: {error_info.error_message}")

        return {
            'handled': True,
            'action': 'failed',
            'message': 'Validation error - no retry'
        }

    async def _handle_permission_error(self, event_id: int, error_info: ErrorInfo) -> Dict[str, Any]:
        """
        Handle permission errors (no retry).

        Args:
            event_id: ID of the event
            error_info: Error information

        Returns:
            Dictionary with handling results
        """
        await mark_event_failed(event_id, f"Permission error: {error_info.error_message}")

        self.logger.error(
            f"Permission error for event {event_id}: {error_info.error_message}")

        return {
            'handled': True,
            'action': 'failed',
            'message': 'Permission error - no retry'
        }

    async def _handle_resource_error(self, event_id: int, error_info: ErrorInfo) -> Dict[str, Any]:
        """
        Handle resource errors with longer retry delay.

        Args:
            event_id: ID of the event
            error_info: Error information

        Returns:
            Dictionary with handling results
        """
        retry_delay = self.retry_delays[ErrorType.RESOURCE_ERROR]

        if error_info.retry_count < error_info.max_retries:
            self.logger.warning(
                f"Resource error for event {event_id}, will retry in {retry_delay}s")

            return {
                'handled': True,
                'action': 'retry',
                'retry_delay': retry_delay,
                'retry_count': error_info.retry_count + 1,
                'message': f'Resource error, will retry in {retry_delay}s'
            }
        else:
            await mark_event_failed(event_id, f"Resource error after {error_info.max_retries} retries: {error_info.error_message}")

            self.logger.error(
                f"Event {event_id} failed after {error_info.max_retries} resource retries")

            return {
                'handled': True,
                'action': 'failed',
                'message': f'Resource error after {error_info.max_retries} retries'
            }

    async def _handle_general_error(self, event_id: int, error_info: ErrorInfo) -> Dict[str, Any]:
        """
        Handle general errors with retry.

        Args:
            event_id: ID of the event
            error_info: Error information

        Returns:
            Dictionary with handling results
        """
        retry_delay = self.retry_delays[ErrorType.GENERAL_ERROR]

        if error_info.retry_count < error_info.max_retries:
            self.logger.warning(
                f"General error for event {event_id}, will retry in {retry_delay}s")

            return {
                'handled': True,
                'action': 'retry',
                'retry_delay': retry_delay,
                'retry_count': error_info.retry_count + 1,
                'message': f'General error, will retry in {retry_delay}s'
            }
        else:
            await mark_event_failed(event_id, f"General error after {error_info.max_retries} retries: {error_info.error_message}")

            self.logger.error(
                f"Event {event_id} failed after {error_info.max_retries} general retries")

            return {
                'handled': True,
                'action': 'failed',
                'message': f'General error after {error_info.max_retries} retries'
            }

    def get_error_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get summary of errors in the specified time window.

        Args:
            time_window: Time window to analyze (default: all errors)

        Returns:
            Dictionary with error summary
        """
        if not self.error_history:
            return {
                'total_errors': 0,
                'error_types': {},
                'retry_attempts': 0,
                'failed_events': 0
            }

        # Filter errors by time window
        if time_window:
            cutoff_time = datetime.utcnow() - time_window
            filtered_errors = [
                e for e in self.error_history if e.timestamp >= cutoff_time]
        else:
            filtered_errors = self.error_history

        if not filtered_errors:
            return {
                'total_errors': 0,
                'error_types': {},
                'retry_attempts': 0,
                'failed_events': 0
            }

        # Count error types
        error_types = {}
        for error in filtered_errors:
            error_type = error.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1

        # Count retry attempts
        retry_attempts = sum(error.retry_count for error in filtered_errors)

        # Count unique failed events
        failed_events = len(set(error.event_id for error in filtered_errors))

        return {
            'total_errors': len(filtered_errors),
            'error_types': error_types,
            'retry_attempts': retry_attempts,
            'failed_events': failed_events
        }

    def clear_old_errors(self, max_age: timedelta = timedelta(days=7)):
        """
        Clear old errors to prevent memory issues.

        Args:
            max_age: Maximum age of errors to keep
        """
        cutoff_time = datetime.utcnow() - max_age
        original_count = len(self.error_history)

        self.error_history = [
            e for e in self.error_history if e.timestamp >= cutoff_time]

        cleared_count = original_count - len(self.error_history)
        if cleared_count > 0:
            self.logger.info(f"Cleared {cleared_count} old error records")


def create_error_handler() -> ErrorHandler:
    """
    Factory function to create an error handler instance.

    Returns:
        ErrorHandler instance
    """
    return ErrorHandler()
