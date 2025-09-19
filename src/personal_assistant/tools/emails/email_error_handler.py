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
        "get_emails": "Read recent emails from inbox",
        "send_email": "Send an email to recipients",
        "delete_email": "Delete an email by ID",
        "get_email_content": "Get full content of a specific email",
        "get_sent_emails": "Get sent emails from sent folder",
        "search_emails": "Search emails by query",
        "move_email": "Move email to different folder",
        "find_all_email_folders": "List all email folders",
        "create_email_folder": "Create a new email folder",
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
            "folder",
            "query",
            "destination",
            "display_name",
            "parent_folder",
            "characters",
            "exceed",
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
            "mail.readwrite",
            "mailboxsettings.read",
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
            "folder",
            "already exists",
            "409",
            "conflict",
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
            "unreachable",
            "dns",
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
                "get_emails": [
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
                "get_sent_emails": [
                    "Check count is between 1-100",
                    "Verify batch_size is between 1-50",
                    "Ensure parameters are positive integers",
                ],
                "search_emails": [
                    "Verify search query is not empty",
                    "Check query length is reasonable",
                    "Ensure special characters are properly escaped",
                ],
                "move_email": [
                    "Verify email ID is not empty",
                    "Check destination folder name is valid",
                    "Ensure folder name is not empty",
                ],
                "find_all_email_folders": [
                    "Check if user has folder access permissions",
                    "Verify Microsoft Graph API access",
                ],
                "create_email_folder": [
                    "Verify folder name is not empty",
                    "Check folder name length (max 255 characters)",
                    "Ensure folder name doesn't contain invalid characters",
                    "Check if parent folder ID is valid",
                ],
            },
            "permission_error": {
                "get_emails": [
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
                "get_sent_emails": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.Read scope is granted",
                    "Ensure access token is valid",
                    "Check application registration scopes",
                ],
                "search_emails": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.Read scope is granted",
                    "Ensure access token is valid",
                    "Check application registration scopes",
                ],
                "move_email": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.ReadWrite scope is granted",
                    "Ensure access token is valid",
                ],
                "find_all_email_folders": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.Read scope is granted",
                    "Ensure access token is valid",
                ],
                "create_email_folder": [
                    "Check Microsoft Graph API permissions",
                    "Verify Mail.ReadWrite scope is granted",
                    "Ensure access token is valid",
                ],
            },
            "resource_error": {
                "get_emails": [
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
                "get_sent_emails": [
                    "Check if sent folder is accessible",
                    "Verify user has email permissions",
                    "Try with smaller count values",
                    "Check for mailbox quota limits",
                ],
                "search_emails": [
                    "Check if mailbox is accessible",
                    "Verify user has email permissions",
                    "Try with different search terms",
                    "Check for mailbox quota limits",
                ],
                "move_email": [
                    "Verify email ID exists",
                    "Check if destination folder exists",
                    "Try listing folders first to get valid folder names",
                    "Ensure email is not already moved",
                ],
                "find_all_email_folders": [
                    "Check if mailbox is accessible",
                    "Verify user has folder access permissions",
                    "Try refreshing the folder list",
                    "Check for mailbox quota limits",
                ],
                "create_email_folder": [
                    "Check if folder name already exists",
                    "Verify parent folder exists",
                    "Try with a different folder name",
                    "Check for folder creation limits",
                ],
            },
            "connection_error": {
                "get_emails": [
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
                "get_sent_emails": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "search_emails": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "move_email": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                ],
                "find_all_email_folders": [
                    "Check network connectivity",
                    "Verify Microsoft Graph API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "create_email_folder": [
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

    @classmethod
    def handle_user_id_required_error(cls) -> dict:
        """
        Handle the common "User ID is required" error pattern.
        
        Returns:
            Dictionary with formatted error response
        """
        return {
            "success": False,
            "error": "User ID is required for OAuth authentication",
            "error_type": "validation_error",
            "recovery_hints": [
                "Ensure user is properly authenticated",
                "Check if user session is valid",
                "Verify OAuth token is present",
            ],
            "message": "Authentication required to access email services"
        }

    @classmethod
    def handle_user_id_required_error_str(cls) -> str:
        """
        Handle the common "User ID is required" error pattern as string.
        
        Returns:
            String with formatted error response
        """
        return "❌ validation_error: User ID is required for OAuth authentication\n💡 Suggestions: Ensure user is properly authenticated, Check if user session is valid, Verify OAuth token is present\n⏱️ Response Time: <3 seconds (target)"

    @classmethod
    def handle_http_error(cls, response, method_name: str, args: dict) -> str:
        """
        Handle HTTP response errors with appropriate error classification.
        
        Args:
            response: HTTP response object
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method
            
        Returns:
            Formatted error response as string
        """
        if response.status_code == 400:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_message = error_data.get("error", {}).get("message", "Bad request")
            return cls.handle_email_error_str(
                Exception(f"Bad request: {error_message}"),
                method_name,
                args
            )
        elif response.status_code == 401:
            return cls.handle_email_error_str(
                Exception("Unauthorized: Invalid or expired access token"),
                method_name,
                args
            )
        elif response.status_code == 403:
            return cls.handle_email_error_str(
                Exception("Forbidden: Insufficient permissions"),
                method_name,
                args
            )
        elif response.status_code == 404:
            return cls.handle_email_error_str(
                Exception("Not found: Resource does not exist"),
                method_name,
                args
            )
        elif response.status_code == 409:
            return cls.handle_email_error_str(
                Exception("Conflict: Resource already exists or conflict occurred"),
                method_name,
                args
            )
        elif response.status_code == 429:
            return cls.handle_email_error_str(
                Exception("Rate limited: Too many requests"),
                method_name,
                args
            )
        elif response.status_code >= 500:
            return cls.handle_email_error_str(
                Exception(f"Server error: {response.status_code}"),
                method_name,
                args
            )
        else:
            return cls.handle_email_error_str(
                Exception(f"HTTP {response.status_code}: {response.text}"),
                method_name,
                args
            )

    @classmethod
    def handle_validation_error(cls, error_message: str, method_name: str, args: dict) -> str:
        """
        Handle validation errors with consistent formatting.
        
        Args:
            error_message: The validation error message
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method
            
        Returns:
            Formatted error response as string
        """
        return cls.handle_email_error_str(
            ValueError(error_message),
            method_name,
            args
        )

    @classmethod
    def handle_folder_conflict_error(cls, folder_name: str, method_name: str, args: dict) -> str:
        """
        Handle folder conflict errors (409 status).
        
        Args:
            folder_name: Name of the conflicting folder
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method
            
        Returns:
            Formatted error response as string
        """
        return cls.handle_email_error_str(
            Exception(f"A folder with the name '{folder_name}' already exists"),
            method_name,
            args
        )

    @classmethod
    def handle_folder_not_found_error(cls, folder_name: str, method_name: str, args: dict) -> str:
        """
        Handle folder not found errors.
        
        Args:
            folder_name: Name of the missing folder
            method_name: Name of the email method that failed
            args: Arguments that were passed to the method
            
        Returns:
            Formatted error response as string
        """
        return cls.handle_email_error_str(
            ValueError(f"Folder '{folder_name}' not found"),
            method_name,
            args
        )
