"""
Error pattern analysis for intelligent memory management.

This module provides analysis of error patterns in conversation history to:
- Identify common error types
- Learn from repeated failures
- Provide intelligent retry recommendations
- Prevent repeated error patterns
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ErrorPatternAnalyzer:
    """Analyzes error patterns in conversation history"""

    def __init__(self, max_retry_attempts: int = 3):
        """
        Initialize the error pattern analyzer.

        Args:
            max_retry_attempts: Maximum number of retry attempts allowed
        """
        self.max_retry_attempts = max_retry_attempts

        # Error type patterns that are known to be transient
        self.transient_error_patterns = [
            "timeout",
            "connection",
            "rate limit",
            "temporary",
            "retry",
            "async",
            "network",
        ]

        # Error type patterns that are configuration issues
        self.configuration_error_patterns = [
            "validation",
            "invalid",
            "missing",
            "undefined",
            "not found",
            "permission",
            "access denied",
        ]

    def analyze_error_patterns(
        self, conversation_history: List[dict]
    ) -> Dict[str, Any]:
        """
        Analyze patterns in tool call errors.

        Args:
            conversation_history: List of conversation history items

        Returns:
            Dictionary containing error pattern analysis
        """
        error_patterns = defaultdict(list)
        tool_error_counts: Dict[str, int] = defaultdict(int)
        error_type_counts: Dict[str, int] = defaultdict(int)

        for item in conversation_history:
            if item.get("role") == "tool":
                tool_name = item.get("name", "")
                content = str(item.get("content", ""))

                if "Error" in content:
                    # Extract error information
                    error_info = self._extract_error_info(content, tool_name)

                    # Categorize by tool
                    error_patterns[tool_name].append(error_info)
                    tool_error_counts[tool_name] += 1

                    # Categorize by error type
                    error_type = error_info.get("error_type", "unknown")
                    error_type_counts[error_type] += 1

        # Analyze patterns
        analysis = {
            "total_errors": sum(tool_error_counts.values()),
            "tools_with_errors": dict(tool_error_counts),
            "error_types": dict(error_type_counts),
            "error_patterns": dict(error_patterns),
            "recommendations": self._generate_recommendations(error_patterns),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"Error analysis complete: {analysis['total_errors']} errors found across {len(tool_error_counts)} tools"
        )

        return analysis

    def _extract_error_info(self, content: str, tool_name: str) -> Dict[str, Any]:
        """
        Extract detailed error information from error content.

        Args:
            content: Error content string
            tool_name: Name of the tool that generated the error

        Returns:
            Dictionary with extracted error information
        """
        error_type = self._categorize_error_type(content)
        severity = self._assess_error_severity(content, error_type)

        return {
            "tool_name": tool_name,
            "error_content": content,
            "error_type": error_type,
            "severity": severity,
            "is_transient": self._is_transient_error(content),
            "is_configuration": self._is_configuration_error(content),
            "timestamp": datetime.now().isoformat(),
            "content_length": len(content),
        }

    def _categorize_error_type(self, content: str) -> str:
        """
        Categorize error type based on content.

        Args:
            content: Error content string

        Returns:
            Categorized error type
        """
        content_lower = content.lower()

        # Check for specific error patterns
        if any(
            pattern in content_lower
            for pattern in ["validation", "invalid", "failed validation"]
        ):
            return "validation_error"
        elif any(
            pattern in content_lower
            for pattern in ["not found", "undefined", "missing"]
        ):
            return "not_found_error"
        elif any(
            pattern in content_lower
            for pattern in ["permission", "access denied", "unauthorized"]
        ):
            return "permission_error"
        elif any(
            pattern in content_lower for pattern in ["timeout", "connection", "network"]
        ):
            return "connection_error"
        elif any(
            pattern in content_lower for pattern in ["rate limit", "quota", "throttle"]
        ):
            return "rate_limit_error"
        elif any(
            pattern in content_lower for pattern in ["async", "await", "coroutine"]
        ):
            return "async_error"
        else:
            return "general_error"

    def _assess_error_severity(self, content: str, error_type: str) -> str:
        """
        Assess the severity of an error.

        Args:
            content: Error content string
            error_type: Categorized error type

        Returns:
            Severity level (low, medium, high, critical)
        """
        content_lower = content.lower()

        # Critical errors
        if any(pattern in content_lower for pattern in ["fatal", "critical", "system"]):
            return "critical"

        # High severity errors
        if error_type in ["permission_error", "validation_error"]:
            return "high"

        # Medium severity errors
        if error_type in ["not_found_error", "connection_error"]:
            return "medium"

        # Low severity errors
        if error_type in ["rate_limit_error", "async_error"]:
            return "low"

        return "medium"

    def _is_transient_error(self, content: str) -> bool:
        """
        Check if an error is transient (can be retried).

        Args:
            content: Error content string

        Returns:
            True if error is transient
        """
        content_lower = content.lower()
        return any(
            pattern in content_lower for pattern in self.transient_error_patterns
        )

    def _is_configuration_error(self, content: str) -> bool:
        """
        Check if an error is a configuration issue (won't be fixed by retrying).

        Args:
            content: Error content string

        Returns:
            True if error is configuration-related
        """
        content_lower = content.lower()
        return any(
            pattern in content_lower for pattern in self.configuration_error_patterns
        )

    def should_retry_tool(
        self, tool_name: str, error_content: str, retry_count: int
    ) -> bool:
        """
        Determine if a tool should be retried based on error patterns.

        Args:
            tool_name: Name of the tool
            error_content: Error content string
            retry_count: Current retry attempt number

        Returns:
            True if tool should be retried
        """
        # Don't retry if we've exceeded max attempts
        if retry_count >= self.max_retry_attempts:
            logger.debug(
                f"Tool {tool_name} exceeded max retry attempts ({retry_count})"
            )
            return False

        # Don't retry configuration errors
        if self._is_configuration_error(error_content):
            logger.debug(f"Tool {tool_name} has configuration error, won't retry")
            return False

        # Retry transient errors
        if self._is_transient_error(error_content):
            logger.debug(
                f"Tool {tool_name} has transient error, will retry (attempt {retry_count + 1})"
            )
            return True

        # For other errors, retry with exponential backoff
        if retry_count < 2:  # Allow up to 2 retries for general errors
            logger.debug(
                f"Tool {tool_name} has general error, will retry (attempt {retry_count + 1})"
            )
            return True

        logger.debug(
            f"Tool {tool_name} has general error, won't retry after {retry_count} attempts"
        )
        return False

    def get_retry_delay(self, retry_count: int, error_type: str) -> float:
        """
        Calculate retry delay based on retry count and error type.

        Args:
            retry_count: Current retry attempt number
            error_type: Type of error encountered

        Returns:
            Delay in seconds before next retry
        """
        base_delay: float = 1.0  # 1 second base delay

        if error_type == "rate_limit_error":
            # Longer delays for rate limit errors
            return base_delay * (2**retry_count) * 2  # type: ignore
        elif error_type == "connection_error":
            # Moderate delays for connection errors
            return base_delay * (2**retry_count)  # type: ignore
        else:
            # Standard exponential backoff
            return base_delay * (2**retry_count)  # type: ignore

    def _generate_recommendations(
        self, error_patterns: Dict[str, List[Dict]]
    ) -> List[str]:
        """
        Generate recommendations based on error patterns.

        Args:
            error_patterns: Dictionary of error patterns by tool

        Returns:
            List of recommendations
        """
        recommendations = []

        for tool_name, errors in error_patterns.items():
            if len(errors) > 3:
                # Tool has many errors
                error_types = [error.get("error_type") for error in errors]
                most_common_error = max(set(error_types), key=error_types.count)

                if most_common_error == "validation_error":
                    recommendations.append(
                        f"Tool '{tool_name}' has frequent validation errors. Check input parameters."
                    )
                elif most_common_error == "permission_error":
                    recommendations.append(
                        f"Tool '{tool_name}' has permission issues. Verify access credentials."
                    )
                elif most_common_error == "connection_error":
                    recommendations.append(
                        f"Tool '{tool_name}' has connection issues. Check network connectivity."
                    )
                else:
                    recommendations.append(
                        f"Tool '{tool_name}' has {len(errors)} errors. Investigate root cause."
                    )

        # General recommendations
        if not recommendations:
            recommendations.append("No significant error patterns detected.")

        return recommendations

    def get_error_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a human-readable error summary.

        Args:
            analysis: Error pattern analysis result

        Returns:
            Formatted error summary string
        """
        total_errors = analysis.get("total_errors", 0)
        tools_with_errors = analysis.get("tools_with_errors", {})
        error_types = analysis.get("error_types", {})

        if total_errors == 0:
            return "No errors detected in conversation history."

        summary_parts = [
            f"Found {total_errors} errors across {len(tools_with_errors)} tools:"
        ]

        # Tool-specific errors
        for tool_name, error_count in sorted(
            tools_with_errors.items(), key=lambda x: x[1], reverse=True
        ):
            summary_parts.append(f"  - {tool_name}: {error_count} errors")

        # Error type breakdown
        if error_types:
            summary_parts.append("\nError types:")
            for error_type, count in sorted(
                error_types.items(), key=lambda x: x[1], reverse=True
            ):
                summary_parts.append(f"  - {error_type}: {count} occurrences")

        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            summary_parts.append("\nRecommendations:")
            for rec in recommendations:
                summary_parts.append(f"  - {rec}")

        return "\n".join(summary_parts)
