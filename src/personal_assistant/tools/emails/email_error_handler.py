"""
Email-specific error handling utilities.

This module provides optimized error handling for email operations,
leveraging the centralized error_handling.py utilities while adding
email-specific context and reducing repetitive code.
"""


from ..error_handling import (
    classify_error,
    create_error_context,
    format_tool_error_response,
)


class EmailErrorHandler:
    """
    Email-specific error handler that eliminates repetitive code
    and provides email-specific error context.
    """

    # Email-specific user intents mapped to method names
    USER_INTENTS = {
        "read_recent_emails": "Read recent emails from inbox",
        "send_email": "Send an email to recipients",
        "delete_email": "Delete an email by ID",
        "get_email_content": "Get full content of a specific email",
    }

    # Email-specific error patterns for enhanced classification
    EMAIL_ERROR_PATTERNS = {
        "validation_error": [
            "email",
            "address",
            "recipient",
            "subject",
            "body",
            "message_id",
            "invalid",
            "required",
            "empty",
            "malformed",
            "format",
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
            "mail.send",
            "mail.read",
        ],
        "resource_error": [
            "email",
            "message",
            "inbox",
            "not found",
            "404",
            "resource",
            "quota",
            "limit",
            "exceeded",
            "mailbox",
        ],
        "connection_error": [
            "connection",
            "network",
            "timeout",
            "unreachable",
            "refused",
            "http",
            "smtp",
            "mail server",
        ],
    }

    @classmethod
    def create_email_error_context(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        Create error context specifically for email operations.

        Args:
            error: The exception that occurred
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method

        Returns:
            Dictionary with email-specific error context
        """
        # Get user intent from method name
        user_intent = cls.USER_INTENTS.get(method_name, "Perform email operation")

        # Create error context using centralized utilities
        return create_error_context(
            error=error,
            tool_name=f"email.{method_name}",
            args=args,
            user_intent=user_intent,
        )

    @classmethod
    def classify_email_error(cls, error: Exception, method_name: str) -> str:
        """
        Enhanced error classification for email-specific errors.

        Args:
            error: The exception to classify
            method_name: Name of the email method that failed

        Returns:
            String representing the error type
        """
        error_msg = str(error).lower()

        # Check email-specific error patterns first
        for error_type, patterns in cls.EMAIL_ERROR_PATTERNS.items():
            if any(pattern in error_msg for pattern in patterns):
                return error_type

        # Fall back to general classification from centralized module
        return classify_error(error)

    @classmethod
    def get_email_recovery_hints(
        cls, error_type: str, method_name: str, args: dict
    ) -> list:
        """
        Get email-specific recovery hints based on error type and method.

        Args:
            error_type: Type of error that occurred
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method

        Returns:
            List of email-specific recovery hints
        """
        # Email-specific recovery strategies
        email_strategies = {
            "validation_error": {
                "read_recent_emails": [
                    "Check count is between 1-100",
                    "Verify batch_size is between 1-50",
                    "Ensure parameters are positive integers",
                ],
                "send_email": [
                    "Verify email addresses are valid format",
                    "Check subject is not empty",
                    "Ensure body content is provided",
                    "Verify recipients are comma-separated",
                ],
                "delete_email": [
                    "Verify message ID is not empty",
                    "Check message ID format",
                    "Ensure message ID is a valid string",
                ],
                "get_email_content": [
                    "Verify message ID is not empty",
                    "Check message ID format",
                    "Ensure message ID is a valid string",
                ],
            },
            "permission_error": {
                "read_recent_emails": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.Read scope is granted",
                    "Ensure access token is valid",
                    "Check application registration scopes",
                ],
                "send_email": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.Send scope is granted",
                    "Ensure access token is valid",
                    "Check application registration scopes",
                ],
                "delete_email": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.ReadWrite scope is granted",
                    "Ensure access token is valid",
                ],
                "get_email_content": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.Read scope is granted",
                    "Ensure access token is valid",
                ],
            },
            "resource_error": {
                "read_recent_emails": [
                    "Check if mailbox is accessible",
                    "Verify user has email permissions",
                    "Try with smaller count values",
                    "Check for mailbox quota limits",
                ],
                "send_email": [
                    "Check if mailbox is accessible",
                    "Verify user has send permissions",
                    "Check for sending quota limits",
                    "Verify recipient addresses exist",
                ],
                "delete_email": [
                    "Verify message ID exists",
                    "Check if message is accessible",
                    "Try listing emails first to get valid IDs",
                    "Ensure message is not already deleted",
                ],
                "get_email_content": [
                    "Verify message ID exists",
                    "Check if message is accessible",
                    "Try listing emails first to get valid IDs",
                    "Ensure message is not deleted",
                ],
            },
            "connection_error": {
                "read_recent_emails": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "send_email": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                    "Check SMTP server availability",
                ],
                "delete_email": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                ],
                "get_email_content": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                ],
            },
        }

        # Get method-specific hints
        method_hints = email_strategies.get(error_type, {}).get(method_name, [])

        # Add general hints for the error type
        general_hints = [
            "Check system configuration",
            "Verify environment variables are set",
            "Contact administrator if the problem persists",
        ]

        return method_hints + general_hints

    @classmethod
    def handle_email_error(cls, error: Exception, method_name: str, args: dict) -> dict:
        """
        One-line error handling for email methods.

        Args:
            error: The exception that occurred
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method

        Returns:
            Formatted error response with LLM guidance
        """
        # Create email-specific error context
        error_context = cls.create_email_error_context(error, method_name, args)

        # Override recovery hints with email-specific ones
        error_context["recovery_hints"] = cls.get_email_recovery_hints(
            error_context["error_type"], method_name, args
        )

        # Return formatted error response
        return format_tool_error_response(error_context)

    @classmethod
    def handle_email_error_str(
        cls, error: Exception, method_name: str, args: dict
    ) -> str:
        """
        One-line error handling for email methods that return strings.

        Args:
            error: The exception that occurred
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method

        Returns:
            Formatted error response as string
        """
        # Create email-specific error context
        error_context = cls.create_email_error_context(error, method_name, args)

        # Override recovery hints with email-specific ones
        error_context["recovery_hints"] = cls.get_email_recovery_hints(
            error_context["error_type"], method_name, args
        )

        # Format as string for methods that return strings
        error_type = error_context["error_type"]
        error_message = error_context["error_message"]
        recovery_hints = error_context["recovery_hints"]

        response = f"❌ {error_type}: {error_message}\n"
        if recovery_hints:
            response += f"💡 Suggestions: {', '.join(recovery_hints[:3])}\n"
        response += "⏱️ Response Time: <3 seconds (target)"

        return response
