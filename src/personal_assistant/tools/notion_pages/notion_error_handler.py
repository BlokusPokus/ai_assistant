"""
Notion-specific error handling utilities.

This module provides optimized error handling for Notion operations,
leveraging the centralized error_handling.py utilities while adding
notion-specific context and reducing repetitive code.
"""


from ..error_handling import (
    classify_error,
    create_error_context,
    format_tool_error_response,
)


class NotionErrorHandler:
    """
    Notion-specific error handler that eliminates repetitive code
    and provides notion-specific error context.
    """

    # Notion-specific user intents mapped to method names
    USER_INTENTS = {
        "create_note_page": "Create a new note page in Notion",
        "read_note_page": "Read content from a Notion note page",
        "update_note_page": "Update an existing Notion note page",
        "delete_note_page": "Delete a Notion note page",
        "search_notes": "Search across Notion note pages",
        "get_table_of_contents": "Get the table of contents from Notion",
        "create_link": "Create a link between Notion pages",
        "get_backlinks": "Get pages that link to a specific page",
    }

    # Notion-specific error patterns for enhanced classification
    NOTION_ERROR_PATTERNS = {
        "validation_error": [
            "title",
            "content",
            "page_id",
            "page_identifier",
            "query",
            "invalid",
            "required",
            "empty",
            "malformed",
            "format",
            "uuid",
            "not found",
            "missing",
        ],
        "permission_error": [
            "notion",
            "api",
            "key",
            "access",
            "permission",
            "unauthorized",
            "forbidden",
            "authentication",
            "scope",
            "integration",
        ],
        "resource_error": [
            "page",
            "block",
            "database",
            "not found",
            "404",
            "resource",
            "archived",
            "deleted",
            "unavailable",
            "parent",
            "child",
        ],
        "connection_error": [
            "connection",
            "network",
            "timeout",
            "unreachable",
            "refused",
            "http",
            "api",
            "server",
            "notion",
            "rate limit",
        ],
        "configuration_error": [
            "environment",
            "variable",
            "missing",
            "invalid",
            "config",
            "api key",
            "root page",
            "database id",
            "notion token",
        ],
    }

    @classmethod
    def create_notion_error_context(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        Create error context specifically for Notion operations.

        Args:
            error: The exception that occurred
            method_name: Name of the Notion method that failed
            args: Arguments that were passed to the method

        Returns:
            Dictionary with Notion-specific error context
        """
        # Get user intent from method name
        user_intent = cls.USER_INTENTS.get(method_name, "Perform Notion operation")

        # Create error context using centralized utilities
        return create_error_context(
            error=error,
            tool_name=f"notion.{method_name}",
            args=args,
            user_intent=user_intent,
        )

    @classmethod
    def classify_notion_error(cls, error: Exception, method_name: str) -> str:
        """
        Enhanced error classification for Notion-specific errors.

        Args:
            error: The exception to classify
            method_name: Name of the Notion method that failed

        Returns:
            String representing the error type
        """
        error_msg = str(error).lower()

        # Check Notion-specific error patterns first
        for error_type, patterns in cls.NOTION_ERROR_PATTERNS.items():
            if any(pattern in error_msg for pattern in patterns):
                return error_type

        # Fall back to general classification from centralized module
        return classify_error(error)

    @classmethod
    def get_notion_recovery_hints(
        cls, error_type: str, method_name: str, args: dict
    ) -> list:
        """
        Get Notion-specific recovery hints based on error type and method.

        Args:
            error_type: Type of error that occurred
            method_name: Name of the Notion method that failed
            args: Arguments that were passed to the method

        Returns:
            List of Notion-specific recovery hints
        """
        # Notion-specific recovery strategies
        notion_strategies = {
            "validation_error": {
                "create_note_page": [
                    "Check that title is not empty",
                    "Verify content is provided",
                    "Ensure tags are comma-separated if provided",
                    "Check that category is a valid string",
                ],
                "read_note_page": [
                    "Verify page_identifier is not empty",
                    "Check if page ID is in correct UUID format",
                    "Ensure page title exists and is exact match",
                    "Try searching for the page first",
                ],
                "update_note_page": [
                    "Verify page_id is not empty and valid",
                    "Check that at least one field to update is provided",
                    "Ensure page_id is in correct UUID format",
                    "Verify the page exists and is accessible",
                ],
                "delete_note_page": [
                    "Verify page_id is not empty",
                    "Check that page_id is in correct UUID format",
                    "Ensure the page exists and is not already deleted",
                    "Verify you have permission to delete the page",
                ],
                "search_notes": [
                    "Check that search query is not empty",
                    "Verify category name is exact match if provided",
                    "Ensure tags are comma-separated if provided",
                    "Try with different search terms",
                ],
                "get_table_of_contents": [
                    "Check if main page exists",
                    "Verify main page is accessible",
                    "Ensure main page has child pages",
                    "Check if table of contents needs to be updated",
                ],
                "create_link": [
                    "Verify source_page_id is valid UUID",
                    "Check that target_page_title is not empty",
                    "Ensure both pages exist and are accessible",
                    "Verify target page title is exact match",
                ],
                "get_backlinks": [
                    "Verify page_id is not empty and valid",
                    "Check that page_id is in correct UUID format",
                    "Ensure the page exists and is accessible",
                    "Check if any pages actually link to this page",
                ],
            },
            "permission_error": {
                "create_note_page": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to the workspace",
                    "Ensure integration has page creation permissions",
                    "Check if integration is properly configured",
                ],
                "read_note_page": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to the page",
                    "Ensure integration has read permissions",
                    "Check if page is shared with the integration",
                ],
                "update_note_page": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to the page",
                    "Ensure integration has update permissions",
                    "Check if page is shared with the integration",
                ],
                "delete_note_page": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to the page",
                    "Ensure integration has delete permissions",
                    "Check if page is shared with the integration",
                ],
                "search_notes": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to the workspace",
                    "Ensure integration has search permissions",
                    "Check if workspace is shared with the integration",
                ],
                "get_table_of_contents": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to the main page",
                    "Ensure integration has read permissions",
                    "Check if main page is shared with the integration",
                ],
                "create_link": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to both pages",
                    "Ensure integration has update permissions",
                    "Check if pages are shared with the integration",
                ],
                "get_backlinks": [
                    "Check Notion API key is valid and active",
                    "Verify integration has access to the page",
                    "Ensure integration has read permissions",
                    "Check if page is shared with the integration",
                ],
            },
            "resource_error": {
                "create_note_page": [
                    "Check if parent page exists and is accessible",
                    "Verify workspace has available space",
                    "Ensure main page is properly configured",
                    "Check if page creation is allowed in this location",
                ],
                "read_note_page": [
                    "Verify page exists and is not archived",
                    "Check if page has been moved or deleted",
                    "Ensure page is accessible from current location",
                    "Try searching for the page in different locations",
                ],
                "update_note_page": [
                    "Verify page exists and is not archived",
                    "Check if page has been moved or deleted",
                    "Ensure page is accessible from current location",
                    "Verify page is not locked or read-only",
                ],
                "delete_note_page": [
                    "Verify page exists and is not already deleted",
                    "Check if page has been moved to different location",
                    "Ensure page is accessible from current location",
                    "Verify page is not locked or protected",
                ],
                "search_notes": [
                    "Check if any pages exist in the workspace",
                    "Verify search scope includes the target pages",
                    "Ensure pages are not archived or deleted",
                    "Check if search index is up to date",
                ],
                "get_table_of_contents": [
                    "Check if main page exists and is accessible",
                    "Verify main page has child pages",
                    "Ensure child pages are not archived",
                    "Check if table of contents needs to be rebuilt",
                ],
                "create_link": [
                    "Verify both pages exist and are accessible",
                    "Check if pages have been moved or deleted",
                    "Ensure pages are in the same workspace",
                    "Verify pages are not archived",
                ],
                "get_backlinks": [
                    "Verify page exists and is not archived",
                    "Check if page has been moved or deleted",
                    "Ensure page is accessible from current location",
                    "Check if any pages actually link to this page",
                ],
            },
            "connection_error": {
                "create_note_page": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                    "Verify API rate limits are not exceeded",
                ],
                "read_note_page": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "update_note_page": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "delete_note_page": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "search_notes": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "get_table_of_contents": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "create_link": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "get_backlinks": [
                    "Check internet connectivity",
                    "Verify Notion API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
            },
            "configuration_error": {
                "create_note_page": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify NOTION_ROOT_PAGE_ID is configured",
                    "Ensure integration is properly set up in Notion",
                    "Check workspace permissions and sharing settings",
                ],
                "read_note_page": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify integration has access to the workspace",
                    "Ensure integration is properly configured",
                    "Check workspace permissions and sharing settings",
                ],
                "update_note_page": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify integration has access to the workspace",
                    "Ensure integration is properly configured",
                    "Check workspace permissions and sharing settings",
                ],
                "delete_note_page": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify integration has access to the workspace",
                    "Ensure integration is properly configured",
                    "Check workspace permissions and sharing settings",
                ],
                "search_notes": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify NOTION_ROOT_PAGE_ID is configured",
                    "Ensure integration is properly set up in Notion",
                    "Check workspace permissions and sharing settings",
                ],
                "get_table_of_contents": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify NOTION_ROOT_PAGE_ID is configured",
                    "Ensure integration is properly set up in Notion",
                    "Check workspace permissions and sharing settings",
                ],
                "create_link": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify integration has access to the workspace",
                    "Ensure integration is properly configured",
                    "Check workspace permissions and sharing settings",
                ],
                "get_backlinks": [
                    "Check NOTION_API_KEY environment variable",
                    "Verify integration has access to the workspace",
                    "Ensure integration is properly configured",
                    "Check workspace permissions and sharing settings",
                ],
            },
        }

        # Get method-specific hints
        method_hints = notion_strategies.get(error_type, {}).get(method_name, [])

        # Add general hints for the error type
        general_hints = [
            "Check system configuration",
            "Verify environment variables are set",
            "Check Notion workspace permissions",
            "Contact administrator if the problem persists",
        ]

        return method_hints + general_hints

    @classmethod
    def handle_notion_error(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        One-line error handling for Notion methods.

        Args:
            error: The exception that occurred
            method_name: Name of the Notion method that failed
            args: Arguments that were passed to the method

        Returns:
            Formatted error response with LLM guidance
        """
        # Create Notion-specific error context
        error_context = cls.create_notion_error_context(error, method_name, args)

        # Override recovery hints with Notion-specific ones
        error_context["recovery_hints"] = cls.get_notion_recovery_hints(
            error_context["error_type"], method_name, args
        )

        # Return formatted error response
        return format_tool_error_response(error_context)
