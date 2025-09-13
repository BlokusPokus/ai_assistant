"""
AI evaluator for calendar events using AgentCore intelligence.

This module provides AI-powered evaluation of calendar events by leveraging
AgentCore's natural language understanding and decision-making capabilities.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .context_builder import EventContext, EventContextBuilder
from ....prompts.ai_evaluator_prompts import AIEvaluatorPrompts

logger = logging.getLogger(__name__)


class AIEventEvaluator:
    """
    AI-powered event evaluator using AgentCore.

    This class leverages AgentCore's intelligence to make decisions about
    calendar events, including recurrence pattern understanding and
    appropriate action suggestions.
    """

    def __init__(self, agent_core):
        """
        Initialize the AI evaluator.

        Args:
            agent_core: AgentCore instance for AI evaluation
        """
        self.agent_core = agent_core
        self.context_builder = EventContextBuilder()
        self.logger = logger

    async def evaluate_event(self, event) -> Dict[str, Any]:
        """
        Evaluate an event using AI intelligence.

        Args:
            event: Event object to evaluate

        Returns:
            Dictionary with AI evaluation results
        """
        try:
            # Build rich context
            event_context = self.context_builder.build_event_context(event)
            ai_context = self.context_builder.create_ai_context(event_context)

            # Create evaluation prompt
            evaluation_prompt = self._create_evaluation_prompt(ai_context)

            # Get AI evaluation
            ai_response = await self._get_ai_evaluation(evaluation_prompt, event_context)

            # Parse AI response
            result = self._parse_ai_response(ai_response, event_context)

            self.logger.info(
                f"AI evaluation for event {event.id}: {result['should_process']}")
            return result

        except Exception as e:
            self.logger.error(
                f"AI evaluation failed for event {event.id}: {e}")
            return {
                'should_process': False,
                'reason': f"AI evaluation error: {str(e)}",
                'confidence': 0.0
            }

    def _create_evaluation_prompt(self, ai_context: Dict[str, Any]) -> str:
        """
        Create evaluation prompt for AgentCore.

        Args:
            ai_context: Rich context for the event

        Returns:
            Formatted prompt string
        """
        return AIEvaluatorPrompts.create_evaluation_prompt(ai_context)

    async def _get_ai_evaluation(self, prompt: str, event_context: EventContext) -> str:
        """
        Get AI evaluation from AgentCore.

        Args:
            prompt: Evaluation prompt
            event_context: Event context for user_id

        Returns:
            AI response string
        """
        try:
            # Use AgentCore to evaluate the event
            # We'll use a special user_id format to indicate this is an AI evaluation
            user_id = f"ai_evaluator_{event_context.user_id}"

            response = await self.agent_core.run(prompt, user_id)
            return response

        except Exception as e:
            self.logger.error(f"Error getting AI evaluation: {e}")
            raise

    def _parse_ai_response(self, ai_response: str, event_context: EventContext) -> Dict[str, Any]:
        """
        Parse AI response into structured result.

        Args:
            ai_response: Raw AI response
            event_context: Event context

        Returns:
            Parsed result dictionary
        """
        try:
            # Try to extract JSON from response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                parsed = json.loads(json_str)

                # Validate required fields
                required_fields = ['should_process', 'reason']
                for field in required_fields:
                    if field not in parsed:
                        raise ValueError(f"Missing required field: {field}")

                # Set defaults for optional fields
                parsed.setdefault('confidence', 0.5)
                parsed.setdefault('suggested_actions', [])
                parsed.setdefault('event_type_analysis', '')

                return parsed
            else:
                # Fallback parsing for non-JSON responses
                return self._fallback_parse_response(ai_response)

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse AI response as JSON: {e}")
            return self._fallback_parse_response(ai_response)

    def _fallback_parse_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Fallback parsing for non-JSON AI responses.

        Args:
            ai_response: Raw AI response

        Returns:
            Parsed result dictionary
        """
        response_lower = ai_response.lower()

        # Simple keyword-based parsing
        should_process = any(word in response_lower for word in [
                             'yes', 'true', 'should', 'need', 'process'])
        confidence = 0.7 if should_process else 0.3

        # Extract reason from response
        reason = "AI evaluation completed"
        if "because" in response_lower:
            because_index = response_lower.find("because")
            reason = ai_response[because_index:].strip()
        elif "reason" in response_lower:
            reason_index = response_lower.find("reason")
            reason = ai_response[reason_index:].strip()

        return {
            'should_process': should_process,
            'reason': reason,
            'confidence': confidence,
            'suggested_actions': [],
            'event_type_analysis': ''
        }

    async def analyze_recurrence_pattern(self, event_title: str, last_processed: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Analyze recurrence pattern using AI.

        Args:
            event_title: Event title with recurrence hint
            last_processed: When this event was last processed

        Returns:
            Analysis result
        """
        try:
            prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt(event_title, last_processed)

            user_id = "ai_recurrence_analyzer"
            response = await self.agent_core.run(prompt, user_id)

            # Parse response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "pattern": "unknown",
                    "should_process_now": False,
                    "reason": "Could not parse AI response",
                    "next_occurrence": "unknown"
                }

        except Exception as e:
            self.logger.error(f"Error analyzing recurrence pattern: {e}")
            return {
                "pattern": "error",
                "should_process_now": False,
                "reason": f"Analysis error: {str(e)}",
                "next_occurrence": "unknown"
            }

    async def suggest_actions_for_event(self, event_context: EventContext) -> List[str]:
        """
        Get AI-suggested actions for an event.

        Args:
            event_context: Rich event context

        Returns:
            List of suggested actions
        """
        try:
            ai_context = self.context_builder.create_ai_context(event_context)

            prompt = AIEvaluatorPrompts.create_action_suggestion_prompt(ai_context)

            user_id = f"ai_action_suggester_{event_context.user_id}"
            response = await self.agent_core.run(prompt, user_id)

            # Parse response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
                return parsed.get('suggested_actions', [])
            else:
                return []

        except Exception as e:
            self.logger.error(f"Error suggesting actions: {e}")
            return []


def create_ai_evaluator(agent_core) -> AIEventEvaluator:
    """
    Factory function to create an AI evaluator.

    Args:
        agent_core: AgentCore instance

    Returns:
        AIEventEvaluator instance
    """
    return AIEventEvaluator(agent_core)
