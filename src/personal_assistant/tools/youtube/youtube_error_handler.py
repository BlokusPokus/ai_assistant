"""
YouTube-specific error handling utilities.

This module provides optimized error handling for YouTube operations,
leveraging the centralized error_handling.py utilities while adding
YouTube-specific context and reducing repetitive code.
"""

from typing import Any, Dict

from ..error_handling import (
    classify_error,
    create_error_context,
    format_tool_error_response,
)


class YouTubeErrorHandler:
    """
    YouTube-specific error handler that eliminates repetitive code
    and provides YouTube-specific error context.
    """

    # YouTube-specific user intents mapped to method names
    USER_INTENTS = {
        "get_video_info": "Get detailed information about a YouTube video",
        "get_video_transcript": "Extract and process YouTube video transcript",
        "search_videos": "Search for YouTube videos by query",
        "get_channel_info": "Get information about a YouTube channel",
        "get_playlist_info": "Get information about a YouTube playlist",
    }

    # YouTube-specific error patterns for enhanced classification
    YOUTUBE_ERROR_PATTERNS = {
        "validation_error": [
            "video_id",
            "channel_id",
            "playlist_id",
            "query",
            "max_results",
            "invalid",
            "required",
            "empty",
            "malformed",
            "format",
            "not found",
            "missing",
            "extract",
            "valid",
        ],
        "permission_error": [
            "youtube",
            "api",
            "key",
            "access",
            "permission",
            "unauthorized",
            "forbidden",
            "authentication",
            "scope",
            "quota",
            "exceeded",
            "403",
            "401",
            "developer",
            "api key",
        ],
        "resource_error": [
            "video",
            "channel",
            "playlist",
            "transcript",
            "not found",
            "404",
            "resource",
            "unavailable",
            "disabled",
            "captions",
            "no transcript",
            "private",
            "deleted",
            "removed",
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
            "youtube",
            "rate limit",
            "throttled",
        ],
        "configuration_error": [
            "environment",
            "variable",
            "missing",
            "invalid",
            "config",
            "youtube api key",
            "google api",
            "client library",
            "dependency",
        ],
        "quota_error": [
            "quota",
            "exceeded",
            "limit",
            "daily",
            "monthly",
            "cost",
            "billing",
            "usage",
            "allocation",
            "reset",
        ],
    }

    @classmethod
    def create_youtube_error_context(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        Create error context specifically for YouTube operations.

        Args:
            error: The exception that occurred
            method_name: Name of the YouTube method that failed
            args: Arguments that were passed to the method

        Returns:
            Dictionary with YouTube-specific error context
        """
        # Get user intent from method name
        user_intent = cls.USER_INTENTS.get(method_name, "Perform YouTube operation")

        # Create error context using centralized utilities
        return create_error_context(
            error=error,
            tool_name=f"youtube.{method_name}",
            args=args,
            user_intent=user_intent,
        )

    @classmethod
    def classify_youtube_error(cls, error: Exception, method_name: str) -> str:
        """
        Enhanced error classification for YouTube-specific errors.

        Args:
            error: The exception to classify
            method_name: Name of the YouTube method that failed

        Returns:
            String representing the error type
        """
        error_msg = str(error).lower()

        # Check YouTube-specific error patterns first
        for error_type, patterns in cls.YOUTUBE_ERROR_PATTERNS.items():
            if any(pattern in error_msg for pattern in patterns):
                return error_type

        # Fall back to general classification from centralized module
        return classify_error(error)

    @classmethod
    def get_youtube_recovery_hints(
        cls, error_type: str, method_name: str, args: dict
    ) -> list:
        """
        Get YouTube-specific recovery hints based on error type and method.

        Args:
            error_type: Type of error that occurred
            method_name: Name of the YouTube method that failed
            args: Arguments that were passed to the method

        Returns:
            List of YouTube-specific recovery hints
        """
        # YouTube-specific recovery strategies
        youtube_strategies = {
            "validation_error": {
                "get_video_info": [
                    "Check that video_id is not empty",
                    "Verify video_id is a valid YouTube video ID",
                    "Ensure video_id is in correct format (11 characters)",
                    "Try extracting video ID from full YouTube URL",
                ],
                "get_video_transcript": [
                    "Check that video_id is not empty",
                    "Verify video_id is a valid YouTube video ID",
                    "Ensure video_id is in correct format (11 characters)",
                    "Try extracting video ID from full YouTube URL",
                ],
                "search_videos": [
                    "Check that search query is not empty",
                    "Verify max_results is between 1-50",
                    "Ensure video_duration is one of: short, medium, long",
                    "Check upload_date format (e.g., 'today', 'this_week')",
                ],
                "get_channel_info": [
                    "Check that channel_id is not empty",
                    "Verify channel_id is a valid YouTube channel ID",
                    "Ensure channel_id starts with 'UC'",
                    "Try extracting channel ID from channel URL",
                ],
                "get_playlist_info": [
                    "Check that playlist_id is not empty",
                    "Verify playlist_id is a valid YouTube playlist ID",
                    "Ensure playlist_id starts with 'PL'",
                    "Try extracting playlist ID from playlist URL",
                ],
            },
            "permission_error": {
                "get_video_info": [
                    "Check YouTube API key is valid and active",
                    "Verify API key has YouTube Data API v3 access",
                    "Ensure API key is not restricted or disabled",
                    "Check if API key has required scopes",
                ],
                "get_video_transcript": [
                    "Check YouTube Transcript API access",
                    "Verify no authentication is required",
                    "Ensure API is not rate-limited",
                    "Check if service is available in your region",
                ],
                "search_videos": [
                    "Check YouTube API key is valid and active",
                    "Verify API key has YouTube Data API v3 access",
                    "Ensure API key is not restricted or disabled",
                    "Check if API key has required scopes",
                ],
                "get_channel_info": [
                    "Check YouTube API key is valid and active",
                    "Verify API key has YouTube Data API v3 access",
                    "Ensure API key is not restricted or disabled",
                    "Check if API key has required scopes",
                ],
                "get_playlist_info": [
                    "Check YouTube API key is valid and active",
                    "Verify API key has YouTube Data API v3 access",
                    "Ensure API key is not restricted or disabled",
                    "Check if API key has required scopes",
                ],
            },
            "resource_error": {
                "get_video_info": [
                    "Verify video exists and is publicly accessible",
                    "Check if video is private or deleted",
                    "Ensure video is not age-restricted",
                    "Try with a different video ID",
                ],
                "get_video_transcript": [
                    "Check if video has captions/transcripts enabled",
                    "Verify video is not private or deleted",
                    "Ensure video supports transcript generation",
                    "Try with a different video that has captions",
                ],
                "search_videos": [
                    "Try with different search terms",
                    "Check if search query is too specific",
                    "Verify search parameters are valid",
                    "Try reducing max_results value",
                ],
                "get_channel_info": [
                    "Verify channel exists and is publicly accessible",
                    "Check if channel is private or deleted",
                    "Ensure channel ID is correct",
                    "Try with a different channel ID",
                ],
                "get_playlist_info": [
                    "Verify playlist exists and is publicly accessible",
                    "Check if playlist is private or deleted",
                    "Ensure playlist ID is correct",
                    "Try with a different playlist ID",
                ],
            },
            "connection_error": {
                "get_video_info": [
                    "Check internet connectivity",
                    "Verify YouTube API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                    "Verify API rate limits are not exceeded",
                ],
                "get_video_transcript": [
                    "Check internet connectivity",
                    "Verify YouTube Transcript API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                ],
                "search_videos": [
                    "Check internet connectivity",
                    "Verify YouTube API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                    "Verify API rate limits are not exceeded",
                ],
                "get_channel_info": [
                    "Check internet connectivity",
                    "Verify YouTube API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                    "Verify API rate limits are not exceeded",
                ],
                "get_playlist_info": [
                    "Check internet connectivity",
                    "Verify YouTube API availability",
                    "Try again in a few moments",
                    "Check firewall/proxy settings",
                    "Verify API rate limits are not exceeded",
                ],
            },
            "configuration_error": {
                "get_video_info": [
                    "Check YOUTUBE_API_KEY environment variable",
                    "Verify google-api-python-client is installed",
                    "Ensure YouTube Data API v3 is enabled",
                    "Check Google Cloud Console configuration",
                ],
                "get_video_transcript": [
                    "Check youtube-transcript-api is installed",
                    "Verify library version compatibility",
                    "Ensure no conflicting dependencies",
                    "Try reinstalling the library",
                ],
                "search_videos": [
                    "Check YOUTUBE_API_KEY environment variable",
                    "Verify google-api-python-client is installed",
                    "Ensure YouTube Data API v3 is enabled",
                    "Check Google Cloud Console configuration",
                ],
                "get_channel_info": [
                    "Check YOUTUBE_API_KEY environment variable",
                    "Verify google-api-python-client is installed",
                    "Ensure YouTube Data API v3 is enabled",
                    "Check Google Cloud Console configuration",
                ],
                "get_playlist_info": [
                    "Check YOUTUBE_API_KEY environment variable",
                    "Verify google-api-python-client is installed",
                    "Ensure YouTube Data API v3 is enabled",
                    "Check Google Cloud Console configuration",
                ],
            },
            "quota_error": {
                "get_video_info": [
                    "Check current API quota usage",
                    "Wait for quota reset (usually daily)",
                    "Reduce API request frequency",
                    "Consider upgrading API quota allocation",
                    "Use cached results when possible",
                ],
                "get_video_transcript": [
                    "Check if YouTube Transcript API has rate limits",
                    "Wait a few moments before retrying",
                    "Reduce request frequency",
                    "Use cached transcripts when possible",
                ],
                "search_videos": [
                    "Check current API quota usage",
                    "Wait for quota reset (usually daily)",
                    "Reduce API request frequency",
                    "Consider upgrading API quota allocation",
                    "Use cached results when possible",
                ],
                "get_channel_info": [
                    "Check current API quota usage",
                    "Wait for quota reset (usually daily)",
                    "Reduce API request frequency",
                    "Consider upgrading API quota allocation",
                    "Use cached results when possible",
                ],
                "get_playlist_info": [
                    "Check current API quota usage",
                    "Wait for quota reset (usually daily)",
                    "Reduce API request frequency",
                    "Consider upgrading API quota allocation",
                    "Use cached results when possible",
                ],
            },
        }

        # Get method-specific hints
        method_hints = youtube_strategies.get(error_type, {}).get(method_name, [])

        # Add general hints for the error type
        general_hints = [
            "Check system configuration",
            "Verify environment variables are set",
            "Check YouTube API status and availability",
            "Contact administrator if the problem persists",
        ]

        return method_hints + general_hints

    @classmethod
    def handle_youtube_error(
        cls, error: Exception, method_name: str, args: dict
    ) -> dict:
        """
        One-line error handling for YouTube methods.

        Args:
            error: The exception that occurred
            method_name: Name of the YouTube method that failed
            args: Arguments that were passed to the method

        Returns:
            Formatted error response with LLM guidance
        """
        # Create YouTube-specific error context
        error_context = cls.create_youtube_error_context(error, method_name, args)

        # Override recovery hints with YouTube-specific ones
        error_context["recovery_hints"] = cls.get_youtube_recovery_hints(
            error_context["error_type"], method_name, args
        )

        # Return formatted error response
        return format_tool_error_response(error_context)
