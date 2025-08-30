"""
Error handler for the agent core system that centralizes error processing and user-friendly message generation.
"""

import time
from typing import Dict, Any, Optional
from .exceptions import (
    ConversationError,
    AgentExecutionError,
    ValidationError,
    AgentMemoryError,
    ToolExecutionError,
    LLMError,
    ContextError,
    AgentCoreError
)
from .logging_utils import (
    log_error_with_context,
    log_performance_metrics
)


class AgentErrorHandler:
    """Handles error processing and user-friendly message generation for the agent system."""

    def __init__(self, logger):
        self.logger = logger
        self._error_messages = self._initialize_error_messages()

    def _initialize_error_messages(self) -> Dict[str, str]:
        """Initialize the mapping of error types to user-friendly messages."""
        return {
            "validation_error": "I'm sorry, but I couldn't process your request due to invalid input. Please try again.",
            "conversation_error": "I'm having trouble managing our conversation. Let me start fresh.",
            "memory_error": "I'm having trouble accessing your conversation history. Let me start fresh.",
            "tool_execution_error": "I encountered an issue while using a tool. Please try again in a moment.",
            "llm_error": "I'm having trouble processing your request with my language model. Please try again in a moment.",
            "context_error": "I'm having trouble accessing relevant information. Please try again.",
            "agent_execution_error": "I'm having trouble executing your request. Please try again.",
            "unexpected_error": "I'm experiencing technical difficulties. Please try again later."
        }

    async def handle_error(
        self,
        error: Exception,
        user_id: int,
        start_time: float,
        **context: Any
    ) -> str:
        """
        Handle an error by logging it and returning a user-friendly message.

        Args:
            error: The exception that occurred
            user_id: ID of the user who encountered the error
            start_time: Timestamp when the operation started
            **context: Additional context for the error

        Returns:
            str: User-friendly error message
        """
        error_type = self._get_error_type(error)

        # Log the error with context
        log_error_with_context(
            self.logger,
            error,
            user_id,
            error_type,
            context
        )

        # Log performance metrics
        duration = time.time() - start_time
        log_performance_metrics(
            self.logger,
            user_id,
            "agent_run_complete",
            duration,
            False,
            {"error_type": error_type, **context}
        )

        # Return user-friendly message
        return self._get_user_friendly_message(error, error_type)

    def _get_error_type(self, error: Exception) -> str:
        """Determine the error type based on the exception class."""
        if isinstance(error, ValidationError):
            return "validation_error"
        elif isinstance(error, ConversationError):
            return "conversation_error"
        elif isinstance(error, AgentMemoryError):
            return "memory_error"
        elif isinstance(error, ToolExecutionError):
            return "tool_execution_error"
        elif isinstance(error, LLMError):
            return "llm_error"
        elif isinstance(error, ContextError):
            return "context_error"
        elif isinstance(error, AgentExecutionError):
            return "agent_execution_error"
        else:
            return "unexpected_error"

    def _get_user_friendly_message(self, error: Exception, error_type: str) -> str:
        """Generate a user-friendly error message."""
        base_message = self._error_messages.get(
            error_type, self._error_messages["unexpected_error"])

        # Add error details for debugging (in development)
        if hasattr(error, 'message'):
            error_detail = str(error.message)
        else:
            error_detail = str(error)

        # Include error details in parentheses for transparency
        return f"{base_message} (Error: {error_detail})"

    def get_error_context(self, error: Exception) -> Dict[str, Any]:
        """Extract relevant context from an error for logging purposes."""
        context = {}

        if isinstance(error, ValidationError):
            context.update({
                "field": getattr(error, 'field', None),
                "value": getattr(error, 'value', None)
            })
        elif isinstance(error, AgentMemoryError):
            context.update({
                "operation": getattr(error, 'operation', None)
            })
        elif isinstance(error, ToolExecutionError):
            context.update({
                "tool_name": getattr(error, 'tool_name', None)
            })
        elif isinstance(error, LLMError):
            context.update({
                "model": getattr(error, 'model', None),
                "operation": getattr(error, 'operation', None)
            })
        elif isinstance(error, ContextError):
            context.update({
                "context_type": getattr(error, 'context_type', None)
            })
        elif isinstance(error, AgentExecutionError):
            context.update({
                # tool_name is used for operation in this case
                "operation": getattr(error, 'tool_name', None)
            })

        return context
