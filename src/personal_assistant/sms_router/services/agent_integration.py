"""
Agent integration service for SMS Router.
"""

import logging
from typing import Any, Dict, Optional

from ...config.settings import settings
from ...core import AgentCore
from ...llm.gemini import GeminiLLM
from ...tools import create_tool_registry

logger = logging.getLogger(__name__)


class AgentIntegrationService:
    """Service for integrating with existing Agent Core."""

    def __init__(self):
        """Initialize Agent Integration Service."""
        try:
            # Reuse existing Agent Core setup
            self.tool_registry = create_tool_registry()
            self.llm = GeminiLLM(
                api_key=settings.GOOGLE_API_KEY, model=settings.GEMINI_MODEL
            )
            self.agent_core = AgentCore(tools=self.tool_registry, llm=self.llm)

            logger.info("Agent Integration Service initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Agent Integration Service: {e}")
            self.agent_core = None
            self.tool_registry = None
            self.llm = None

    async def process_with_agent(self, message: str, user_info: Dict[str, Any]) -> str:
        """
        Process message with Agent Core using user context.

        Args:
            message: SMS message content
            user_info: User information including ID

        Returns:
            Agent response string
        """
        try:
            if not self.agent_core:
                logger.error("Agent Core not available")
                return "I'm sorry, the AI assistant is currently unavailable. Please try again later."

            user_id = user_info["id"]
            logger.info(f"Processing message for user {user_id}: {message[:50]}...")

            # Call existing Agent Core with user context
            result = await self.agent_core.run(message, user_id)

            if not result:
                logger.warning(f"No response generated for user {user_id}")
                return "I'm sorry, I couldn't generate a response. Please try rephrasing your question."

            logger.info(f"Agent response for user {user_id}: {result[:50]}...")
            return result  # type: ignore

        except Exception as e:
            logger.error(f"Error processing message with Agent Core: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."

    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the status of the Agent Core system.

        Returns:
            Dictionary with agent status information
        """
        try:
            status: dict[str, Any] = {
                "available": self.agent_core is not None,
                "tools_available": self.tool_registry is not None,
                "llm_available": self.llm is not None,
                "status": "healthy" if self.agent_core else "unavailable",
            }

            if self.agent_core:
                # Get tool information
                if self.tool_registry:
                    status["tool_count"] = (
                        len(self.tool_registry.tools)
                        if hasattr(self.tool_registry, "tools")
                        else 0
                    )

                # Get LLM information
                if self.llm:
                    status["llm_model"] = getattr(self.llm, "model", "unknown")

            return status

        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {"available": False, "status": "error", "error": str(e)}

    async def validate_agent_response(self, response: str) -> Dict[str, Any]:
        """
        Validate agent response for SMS delivery.

        Args:
            response: Raw agent response

        Returns:
            Validation result dictionary
        """
        try:
            validation: dict[str, Any] = {
                "valid": True,
                "length": len(response),
                "issues": [],
            }

            # Check response length
            if len(response) > 1600:  # Max 10 SMS segments
                validation["valid"] = False
                validation["issues"].append("Response too long for SMS delivery")

            # Check for empty response
            if not response or not response.strip():
                validation["valid"] = False
                validation["issues"].append("Empty response")

            # Check for inappropriate content
            inappropriate_words = ["spam", "error", "unavailable", "sorry"]
            if any(word in response.lower() for word in inappropriate_words):
                validation["issues"].append("Response contains error indicators")

            return validation

        except Exception as e:
            logger.error(f"Error validating agent response: {e}")
            return {"valid": False, "error": str(e)}

    async def get_user_context(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user context for agent processing.

        Args:
            user_id: User ID

        Returns:
            User context dictionary or None
        """
        try:
            # This could be enhanced to include user preferences, history, etc.
            context = {
                "user_id": user_id,
                "channel": "sms",
                "timestamp": None,  # Could be enhanced with actual timestamp
                "session_id": f"sms_{user_id}_{hash(str(user_id))}",
            }

            return context

        except Exception as e:
            logger.error(f"Error getting user context for {user_id}: {e}")
            return None

    async def handle_agent_error(
        self, error: Exception, user_info: Dict[str, Any]
    ) -> str:
        """
        Handle errors from Agent Core gracefully.

        Args:
            error: The error that occurred
            user_info: User information

        Returns:
            User-friendly error message
        """
        try:
            error_type = type(error).__name__
            logger.error(
                f"Agent error for user {user_info['id']}: {error_type}: {error}"
            )

            # Provide user-friendly error messages
            if "rate limit" in str(error).lower():
                return "I'm receiving too many requests right now. Please wait a moment and try again."
            elif "authentication" in str(error).lower():
                return "There was an authentication issue. Please try again later."
            elif "timeout" in str(error).lower():
                return "The request took too long to process. Please try again."
            else:
                return "I encountered an unexpected error. Please try again or contact support if the problem persists."

        except Exception as e:
            logger.error(f"Error handling agent error: {e}")
            return "I'm sorry, something went wrong. Please try again later."
