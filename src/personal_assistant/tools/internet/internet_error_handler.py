"""
Internet-specific error handling utilities.

This module provides optimized error handling for internet operations,
leveraging the centralized error_handling.py utilities while adding
internet-specific context and reducing repetitive code.
"""

from typing import Any, Dict

from ..error_handling import (
    classify_error,
    create_error_context,
    format_tool_error_response,
)


class InternetErrorHandler:
    """
    Internet-specific error handler that eliminates repetitive code
    and provides internet-specific error context.
    """

    # Internet-specific user intents mapped to method names
    USER_INTENTS = {
        "web_search": "Search the web for information",
        "get_news_articles": "Get current news articles",
        "get_wikipedia": "Search Wikipedia for information",
        "search_images": "Search for images on the web",
    }

    # Internet-specific error patterns for enhanced classification
    INTERNET_ERROR_PATTERNS = {
        "validation_error": [
            "query",
            "topic",
            "max_results",
            "safe_search",
            "language",
            "invalid",
            "required",
            "empty",
            "malformed",
            "format",
            "min_val",
            "max_val",
            "out of range",
        ],
        "rate_limit_error": [
            "rate limit",
            "too many requests",
            "throttled",
            "quota",
            "exceeded",
            "delay",
            "wait",
            "slow down",
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
            "duckduckgo",
            "wikipedia",
        ],
        "resource_error": [
            "not found",
            "404",
            "no results",
            "empty",
            "unavailable",
            "library",
            "import",
            "module",
            "dependency",
        ],
        "permission_error": [
            "access",
            "permission",
            "unauthorized",
            "forbidden",
            "api key",
            "authentication",
            "scope",
        ],
    }

    @classmethod
    def create_internet_error_context(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        Create error context specifically for internet operations.

        Args:
            error: The exception that occurred
            method_name: Name of the internet method that failed
            args: Arguments that were passed to the method

        Returns:
            Dictionary with internet-specific error context
        """
        # Get user intent from method name
        user_intent = cls.USER_INTENTS.get(method_name, "Perform internet operation")

        # Create error context using centralized utilities
        return create_error_context(
            error=error,
            tool_name=f"internet.{method_name}",
            args=args,
            user_intent=user_intent,
        )

    @classmethod
    def classify_internet_error(cls, error: Exception, method_name: str) -> str:
        """
        Enhanced error classification for internet-specific errors.

        Args:
            error: The exception to classify
            method_name: Name of the internet method that failed

        Returns:
            String representing the error type
        """
        error_msg = str(error).lower()

        # Check internet-specific error patterns first
        for error_type, patterns in cls.INTERNET_ERROR_PATTERNS.items():
            if any(pattern in error_msg for pattern in patterns):
                return error_type

        # Fall back to general classification from centralized module
        return classify_error(error)

    @classmethod
    def get_internet_recovery_hints(
        cls, error_type: str, method_name: str, args: dict
    ) -> list:
        """
        Get internet-specific recovery hints based on error type and method.

        Args:
            error_type: Type of error that occurred
            method_name: Name of the internet method that failed
            args: Arguments that were passed to the method

        Returns:
            List of internet-specific recovery hints
        """
        # Internet-specific recovery strategies
        internet_strategies = {
            "validation_error": {
                "web_search": [
                    "Check that search query is not empty",
                    "Verify max_results is between 1-20",
                    "Ensure safe_search is one of: strict, moderate, off",
                    "Try a different search query",
                ],
                "get_news_articles": [
                    "Check that max_articles is between 1-20",
                    "Try a different category or topic",
                    "Ensure parameters are valid strings",
                ],
                "get_wikipedia": [
                    "Check that topic is not empty",
                    "Verify language code is 2 characters (e.g., 'en')",
                    "Try a different topic or language",
                    "Ensure topic is a valid search term",
                ],
                "search_images": [
                    "Check that search query is not empty",
                    "Verify max_results is between 1-50",
                    "Ensure safe_search is one of: strict, moderate, off",
                    "Try a different image search query",
                ],
            },
            "rate_limit_error": {
                "web_search": [
                    "Wait a few seconds before trying again",
                    "Reduce the frequency of search requests",
                    "Try with fewer max_results",
                    "Check if other users are making many requests",
                ],
                "get_news_articles": [
                    "Wait a few seconds before trying again",
                    "Reduce the frequency of news requests",
                    "Try with fewer max_articles",
                    "Check if other users are making many requests",
                ],
                "get_wikipedia": [
                    "Wait a few seconds before trying again",
                    "Reduce the frequency of Wikipedia requests",
                    "Check if other users are making many requests",
                ],
                "search_images": [
                    "Wait a few seconds before trying again",
                    "Reduce the frequency of image search requests",
                    "Try with fewer max_results",
                    "Check if other users are making many requests",
                ],
            },
            "connection_error": {
                "web_search": [
                    "Check internet connectivity",
                    "Verify DuckDuckGo API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                    "Verify network configuration",
                ],
                "get_news_articles": [
                    "Check internet connectivity",
                    "Verify News API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "get_wikipedia": [
                    "Check internet connectivity",
                    "Verify Wikipedia API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "search_images": [
                    "Check internet connectivity",
                    "Verify DuckDuckGo API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
            },
            "resource_error": {
                "web_search": [
                    "Try a different search query",
                    "Check if the search terms are too specific",
                    "Verify DuckDuckGo library is properly installed",
                    "Try with different search parameters",
                ],
                "get_news_articles": [
                    "Try a different category or topic",
                    "Check if the news source is available",
                    "Verify News API integration is working",
                    "Try with different parameters",
                ],
                "get_wikipedia": [
                    "Try a different topic",
                    "Check if the topic exists on Wikipedia",
                    "Verify Wikipedia API integration is working",
                    "Try with different language codes",
                ],
                "search_images": [
                    "Try a different image search query",
                    "Check if the search terms are too specific",
                    "Verify DuckDuckGo library is properly installed",
                    "Try with different search parameters",
                ],
            },
            "permission_error": {
                "web_search": [
                    "Check if DuckDuckGo API access is available",
                    "Verify no authentication is required",
                    "Check if the service is free to use",
                    "Contact administrator if the problem persists",
                ],
                "get_news_articles": [
                    "Check if News API key is required",
                    "Verify API key is valid and active",
                    "Check if the service requires authentication",
                    "Contact administrator for API access",
                ],
                "get_wikipedia": [
                    "Check if Wikipedia API access is available",
                    "Verify no authentication is required",
                    "Check if the service is free to use",
                    "Contact administrator if the problem persists",
                ],
                "search_images": [
                    "Check if DuckDuckGo API access is available",
                    "Verify no authentication is required",
                    "Check if the service is free to use",
                    "Contact administrator if the problem persists",
                ],
            },
        }

        # Get method-specific hints
        method_hints = internet_strategies.get(error_type, {}).get(method_name, [])

        # Add general hints for the error type
        general_hints = [
            "Check system configuration",
            "Verify internet connectivity",
            "Try again in a few moments",
            "Contact administrator if the problem persists",
        ]

        return method_hints + general_hints

    @classmethod
    def handle_internet_error(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        One-line error handling for internet methods.

        Args:
            error: The exception that occurred
            method_name: Name of the internet method that failed
            args: Arguments that were passed to the method

        Returns:
            Formatted error response with LLM guidance
        """
        # Create internet-specific error context
        error_context = cls.create_internet_error_context(error, method_name, args)

        # Override recovery hints with internet-specific ones
        error_context["recovery_hints"] = cls.get_internet_recovery_hints(
            error_context["error_type"], method_name, args
        )

        # Return formatted error response
        return format_tool_error_response(error_context)
