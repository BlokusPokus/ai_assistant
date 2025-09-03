"""
Centralized error handling utilities for all tools.

This module provides simple, consistent error handling that tools can use
to provide better LLM guidance when errors occur.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def create_error_context(
    error: Exception, tool_name: str, args: dict, user_intent: str = None
) -> dict:
    """
    Create simple error context dictionary for LLM guidance.

    Args:
        error: The exception that occurred
        tool_name: Name of the tool that failed
        args: Arguments that were passed to the tool
        user_intent: What the user was trying to accomplish (optional)

    Returns:
        Dictionary with error context information
    """
    return {
        "error_type": classify_error(error),
        "tool_name": tool_name,
        "args": args,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
        "user_intent": user_intent,
        "recovery_hints": get_recovery_hints(error, tool_name),
        "suggested_actions": get_suggested_actions(error, tool_name),
    }


def classify_error(error: Exception) -> str:
    """
    Simple error classification without complex classes.

    Args:
        error: The exception to classify

    Returns:
        String representing the error type
    """
    error_msg = str(error).lower()

    # Validation errors
    if any(
        word in error_msg
        for word in ["validation", "invalid", "malformed", "format", "required"]
    ):
        return "validation_error"

    # Connection/network errors
    elif any(
        word in error_msg
        for word in [
            "connection",
            "network",
            "unreachable",
            "refused",
            "timeout",
            "timed out",
        ]
    ):
        return "connection_error"

    # Permission/authentication errors
    elif any(
        word in error_msg
        for word in [
            "permission",
            "unauthorized",
            "forbidden",
            "access denied",
            "authentication",
            "token",
        ]
    ):
        return "permission_error"

    # Resource errors
    elif any(
        word in error_msg
        for word in ["resource", "memory", "disk", "quota", "limit", "not found", "404"]
    ):
        return "resource_error"

    # Configuration errors
    elif any(
        word in error_msg
        for word in ["configuration", "config", "environment", "missing", "undefined"]
    ):
        return "configuration_error"

    # Default to general error
    else:
        return "general_error"


def get_recovery_hints(error_type: str, tool_name: str) -> List[str]:
    """
    Generate simple recovery hints based on error type and tool.

    Args:
        error_type: Type of error that occurred
        tool_name: Name of the tool that failed

    Returns:
        List of recovery hints
    """
    # General hints for each error type
    general_hints = {
        "validation_error": [
            "Check parameter format and requirements",
            "Verify input data validity",
            "Use help command to see parameter details",
        ],
        "connection_error": [
            "Check network connectivity",
            "Try again in a few moments",
            "Verify service availability",
        ],
        "permission_error": [
            "Check user permissions",
            "Verify authentication status",
            "Contact administrator if needed",
        ],
        "resource_error": [
            "Check if the requested resource exists",
            "Verify resource availability",
            "Try with different parameters",
        ],
        "configuration_error": [
            "Check system configuration",
            "Verify environment variables",
            "Contact system administrator",
        ],
        "general_error": [
            "Review the error and try again",
            "Check system status",
            "Ask for help if the problem persists",
        ],
    }

    # Tool-specific hints
    tool_specific_hints = {
        "calendar": {
            "validation_error": [
                "Ensure date format is YYYY-MM-DD HH:MM",
                "Check that duration is between 1-1440 minutes",
                "Verify event subject is not empty",
            ],
            "permission_error": [
                "Check Microsoft Graph API permissions",
                "Verify access token is valid",
                "Ensure calendar access is granted",
            ],
        },
        "emails": {
            "validation_error": [
                "Check email address format",
                "Verify subject and body are not empty",
                "Ensure recipient addresses are valid",
            ],
            "permission_error": [
                "Check email sending permissions",
                "Verify Microsoft Graph API access",
                "Ensure mailbox access is granted",
            ],
        },
        "notion_pages": {
            "validation_error": [
                "Check page title is not empty",
                "Verify content format is valid",
                "Ensure database ID is correct",
            ],
            "permission_error": [
                "Check Notion API access token",
                "Verify page/database permissions",
                "Ensure integration is properly configured",
            ],
        },
    }

    # Combine general and tool-specific hints
    hints = general_hints.get(error_type, general_hints["general_error"])

    if (
        tool_name in tool_specific_hints
        and error_type in tool_specific_hints[tool_name]
    ):
        hints.extend(tool_specific_hints[tool_name][error_type])

    return hints


def get_suggested_actions(error_type: str, tool_name: str) -> List[str]:
    """
    Generate suggested actions for the LLM to take.

    Args:
        error_type: Type of error that occurred
        tool_name: Name of the tool that failed

    Returns:
        List of suggested actions
    """
    actions = {
        "validation_error": [
            "Ask user to correct the parameters",
            "Suggest the correct format",
            "Provide examples of valid input",
        ],
        "connection_error": [
            "Suggest retrying the operation",
            "Ask user to check their connection",
            "Offer alternative approaches if available",
        ],
        "permission_error": [
            "Explain what permissions are needed",
            "Guide user to check their access",
            "Suggest contacting support if needed",
        ],
        "resource_error": [
            "Check if resource exists with different parameters",
            "Suggest alternative resources",
            "Ask user to verify the resource details",
        ],
        "configuration_error": [
            "Explain what configuration is needed",
            "Guide user to check system settings",
            "Suggest contacting administrator",
        ],
        "general_error": [
            "Ask user to try again",
            "Request more context about what they're trying to do",
            "Offer to help troubleshoot the issue",
        ],
    }

    return actions.get(error_type, actions["general_error"])


def generate_llm_instructions(error_context: dict) -> str:
    """
    Generate simple LLM guidance without complex classes.

    Args:
        error_context: Error context dictionary

    Returns:
        Formatted instructions for the LLM
    """
    tool_name = error_context["tool_name"]
    error_type = error_context["error_type"]
    error_message = error_context["error_message"]
    recovery_hints = error_context["recovery_hints"]
    suggested_actions = error_context["suggested_actions"]

    # Build the instruction message
    instruction = f"""
The tool '{tool_name}' failed with a {error_type.replace('_', ' ')} error.

Error Details:
- Error: {error_message}
- Tool: {tool_name}
- Timestamp: {error_context['timestamp']}

Recovery Hints:
{chr(10).join(f"- {hint}" for hint in recovery_hints)}

Suggested Actions:
{chr(10).join(f"- {action}" for action in suggested_actions)}

Next Steps:
1. Analyze the error type and context
2. Use the recovery hints to understand what went wrong
3. Take one of the suggested actions to resolve the issue
4. If the problem persists, ask the user for more information or suggest alternative approaches

Proceed with your response, taking into account this error context.
"""

    return instruction.strip()


def format_tool_error_response(error_context: dict) -> Dict[str, Any]:
    """
    Format a standardized error response for tools to return.

    Args:
        error_context: Error context dictionary

    Returns:
        Formatted error response
    """
    return {
        "error": True,
        "error_type": error_context["error_type"],
        "error_message": error_context["error_message"],
        "tool_name": error_context["tool_name"],
        "context": error_context,
        "llm_instructions": generate_llm_instructions(error_context),
        "recovery_hints": error_context["recovery_hints"],
        "suggested_actions": error_context["suggested_actions"],
        "timestamp": error_context["timestamp"],
    }


def enhance_prompt_with_error(prompt: str, error_context: dict) -> str:
    """
    Enhance an LLM prompt with error context for better guidance.

    Args:
        prompt: Original prompt
        error_context: Error context dictionary

    Returns:
        Enhanced prompt with error context
    """
    enhanced_prompt = f"""
{prompt}

IMPORTANT: The previous tool execution failed with the following error:
- Tool: {error_context['tool_name']}
- Error Type: {error_context['error_type']}
- Error: {error_context['error_message']}

Recovery Hints:
{chr(10).join(f"- {hint}" for hint in error_context['recovery_hints'])}

Suggested Actions:
{chr(10).join(f"- {action}" for action in error_context['suggested_actions'])}

Please use this information to guide your next action. Consider:
1. Fixing the parameters if it was a validation error
2. Using an alternative approach if available
3. Asking the user for clarification if needed
4. Breaking down the request into simpler steps
5. Following the suggested actions above

Proceed with your response, taking into account this error context.
"""

    return enhanced_prompt.strip()
