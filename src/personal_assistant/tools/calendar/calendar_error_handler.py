"""
Calendar-specific error handling utilities.

This module provides optimized error handling for calendar operations,
leveraging the centralized error_handling.py utilities while adding
calendar-specific context and reducing repetitive code.
"""

from typing import Any, Dict

from ..error_handling import (
    classify_error,
    create_error_context,
    format_tool_error_response,
)


class CalendarErrorHandler:
    """
    Calendar-specific error handler that eliminates repetitive code
    and provides calendar-specific error context.
    """

    # Calendar-specific user intents mapped to method names
    USER_INTENTS = {
        "create_calendar_event": "Create a new calendar event",
        "get_calendar_events": "Retrieve calendar events",
        "update_calendar_event": "Update an existing calendar event",
        "delete_calendar_event": "Delete a calendar event",
        "get_calendar_event": "Get details of a specific calendar event",
    }

    # Calendar-specific error patterns for enhanced classification
    CALENDAR_ERROR_PATTERNS = {
        "validation_error": [
            "date",
            "time",
            "subject",
            "start_time",
            "end_time",
            "duration",
            "invalid",
            "required",
            "empty",
            "malformed",
            "format",
            "timezone",
        ],
        "permission_error": [
            "microsoft graph",
            "api",
            "token",
            "access",
            "permission",
            "unauthorized",
            "forbidden",
            "authentication",
            "scope",
            "calendar.read",
            "calendar.write",
        ],
        "resource_error": [
            "event",
            "calendar",
            "not found",
            "404",
            "resource",
            "quota",
            "limit",
            "exceeded",
            "mailbox",
            "calendar id",
        ],
        "connection_error": [
            "connection",
            "network",
            "timeout",
            "unreachable",
            "refused",
            "http",
            "microsoft graph",
            "api server",
        ],
        "configuration_error": [
            "environment",
            "variable",
            "missing",
            "invalid",
            "config",
            "application id",
            "client secret",
            "tenant id",
        ],
    }

    @classmethod
    def create_calendar_error_context(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        Create error context specifically for calendar operations.

        Args:
            error: The exception that occurred
            method_name: Name of the calendar method that failed
            args: Arguments that were passed to the method

        Returns:
            Dictionary with calendar-specific error context
        """
        # Get user intent from method name
        user_intent = cls.USER_INTENTS.get(method_name, "Perform calendar operation")

        # Create error context using centralized utilities
        return create_error_context(
            error=error,
            tool_name=f"calendar.{method_name}",
            args=args,
            user_intent=user_intent,
        )

    @classmethod
    def classify_calendar_error(cls, error: Exception, method_name: str) -> str:
        """
        Enhanced error classification for calendar-specific errors.

        Args:
            error: The exception to classify
            method_name: Name of the calendar method that failed

        Returns:
            String representing the error type
        """
        error_msg = str(error).lower()

        # Check calendar-specific error patterns first
        for error_type, patterns in cls.CALENDAR_ERROR_PATTERNS.items():
            if any(pattern in error_msg for pattern in patterns):
                return error_type

        # Fall back to general classification from centralized module
        return classify_error(error)

    @classmethod
    def get_calendar_recovery_hints(
        cls, error_type: str, method_name: str, args: dict
    ) -> list:
        """
        Get calendar-specific recovery hints based on error type and method.

        Args:
            error_type: Type of error that occurred
            method_name: Name of the calendar method that failed
            args: Arguments that were passed to the method

        Returns:
            List of calendar-specific recovery hints
        """
        # Calendar-specific recovery strategies
        calendar_strategies = {
            "validation_error": {
                "create_calendar_event": [
                    "Check that subject is not empty",
                    "Verify start_time is in YYYY-MM-DD HH:MM format",
                    "Ensure duration is a positive integer",
                    "Check that location is a valid string (optional)",
                ],
                "get_calendar_events": [
                    "Check that start_date is in YYYY-MM-DD format",
                    "Verify end_date is after start_date",
                    "Ensure max_results is between 1-100",
                ],
                "update_calendar_event": [
                    "Verify event_id is not empty",
                    "Check that at least one field to update is provided",
                    "Ensure date/time formats are correct",
                ],
                "delete_calendar_event": [
                    "Verify event_id is not empty",
                    "Check that event_id is a valid string",
                ],
                "get_calendar_event": [
                    "Verify event_id is not empty",
                    "Check that event_id is a valid string",
                ],
            },
            "permission_error": {
                "create_calendar_event": [
                    "Check Microsoft Graph API permissions",
                    "Verify Calendar.ReadWrite scope is granted",
                    "Ensure access token is valid",
                    "Check application registration scopes",
                ],
                "get_calendar_events": [
                    "Check Microsoft Graph API permissions",
                    "Verify Calendar.Read scope is granted",
                    "Ensure access token is valid",
                    "Check application registration scopes",
                ],
                "update_calendar_event": [
                    "Check Microsoft Graph API permissions",
                    "Verify Calendar.ReadWrite scope is granted",
                    "Ensure access token is valid",
                ],
                "delete_calendar_event": [
                    "Check Microsoft Graph API permissions",
                    "Verify Calendar.ReadWrite scope is granted",
                    "Ensure access token is valid",
                ],
                "get_calendar_event": [
                    "Check Microsoft Graph API permissions",
                    "Verify Calendar.Read scope is granted",
                    "Ensure access token is valid",
                ],
            },
            "resource_error": {
                "create_calendar_event": [
                    "Check if calendar is accessible",
                    "Verify user has calendar permissions",
                    "Check for calendar quota limits",
                    "Ensure calendar exists and is writable",
                ],
                "get_calendar_events": [
                    "Check if calendar is accessible",
                    "Verify user has calendar permissions",
                    "Try with smaller date ranges",
                    "Check for calendar quota limits",
                ],
                "update_calendar_event": [
                    "Verify event exists and is accessible",
                    "Check if event is not already deleted",
                    "Ensure event belongs to the user",
                    "Try listing events first to get valid IDs",
                ],
                "delete_calendar_event": [
                    "Verify event exists and is accessible",
                    "Check if event is not already deleted",
                    "Ensure event belongs to the user",
                    "Try listing events first to get valid IDs",
                ],
                "get_calendar_event": [
                    "Verify event exists and is accessible",
                    "Check if event is not already deleted",
                    "Ensure event belongs to the user",
                    "Try listing events first to get valid IDs",
                ],
            },
            "connection_error": {
                "create_calendar_event": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "get_calendar_events": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "update_calendar_event": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                ],
                "delete_calendar_event": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                ],
                "get_calendar_event": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                ],
            },
            "configuration_error": {
                "create_calendar_event": [
                    "Check MICROSOFT_APPLICATION_ID environment variable",
                    "Verify MICROSOFT_CLIENT_SECRET is set",
                    "Ensure MICROSOFT_TENANT_ID is configured",
                    "Check application registration in Azure portal",
                ],
                "get_calendar_events": [
                    "Check MICROSOFT_APPLICATION_ID environment variable",
                    "Verify MICROSOFT_CLIENT_SECRET is set",
                    "Ensure MICROSOFT_TENANT_ID is configured",
                    "Check application registration in Azure portal",
                ],
                "update_calendar_event": [
                    "Check MICROSOFT_APPLICATION_ID environment variable",
                    "Verify MICROSOFT_CLIENT_SECRET is set",
                    "Ensure MICROSOFT_TENANT_ID is configured",
                ],
                "delete_calendar_event": [
                    "Check MICROSOFT_APPLICATION_ID environment variable",
                    "Verify MICROSOFT_CLIENT_SECRET is set",
                    "Ensure MICROSOFT_TENANT_ID is configured",
                ],
                "get_calendar_event": [
                    "Check MICROSOFT_APPLICATION_ID environment variable",
                    "Verify MICROSOFT_CLIENT_SECRET is set",
                    "Ensure MICROSOFT_TENANT_ID is configured",
                ],
            },
        }

        # Get method-specific hints
        method_hints = calendar_strategies.get(error_type, {}).get(method_name, [])

        # Add general hints for the error type
        general_hints = [
            "Check system configuration",
            "Verify environment variables are set",
            "Contact administrator if the problem persists",
        ]

        return method_hints + general_hints

    @classmethod
    def handle_calendar_error(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        One-line error handling for calendar methods.

        Args:
            error: The exception that occurred
            method_name: Name of the calendar method that failed
            args: Arguments that were passed to the method

        Returns:
            Formatted error response with LLM guidance
        """
        # Create calendar-specific error context
        error_context = cls.create_calendar_error_context(error, method_name, args)

        # Override recovery hints with calendar-specific ones
        error_context["recovery_hints"] = cls.get_calendar_recovery_hints(
            error_context["error_type"], method_name, args
        )

        # Return formatted error response
        return format_tool_error_response(error_context)
