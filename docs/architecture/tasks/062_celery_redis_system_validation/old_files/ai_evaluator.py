# """
# AI evaluator for calendar events using AgentCore intelligence.

# This module provides AI-powered evaluation of calendar events by leveraging
# AgentCore's natural language understanding and decision-making capabilities.
# """

# import json
# import logging
# from datetime import datetime
# from typing import Any, Dict, List, Optional

# from .context_builder import EventContext, EventContextBuilder

# logger = logging.getLogger(__name__)


# class AIEventEvaluator:
#     """
#     AI-powered event evaluator using AgentCore.

#     This class leverages AgentCore's intelligence to make decisions about
#     calendar events, including recurrence pattern understanding and
#     appropriate action suggestions.
#     """

#     def __init__(self, agent_core):
#         """
#         Initialize the AI evaluator.

#         Args:
#             agent_core: AgentCore instance for AI evaluation
#         """
#         self.agent_core = agent_core
#         self.context_builder = EventContextBuilder()
#         self.logger = logger

#     async def evaluate_event(self, event) -> Dict[str, Any]:
#         """
#         Evaluate an event using AI intelligence.

#         Args:
#             event: Event object to evaluate

#         Returns:
#             Dictionary with AI evaluation results
#         """
#         try:
#             # Build rich context
#             event_context = self.context_builder.build_event_context(event)
#             ai_context = self.context_builder.create_ai_context(event_context)

#             # Create evaluation prompt
#             evaluation_prompt = self._create_evaluation_prompt(ai_context)

#             # Get AI evaluation
#             ai_response = await self._get_ai_evaluation(evaluation_prompt, event_context)

#             # Parse AI response
#             result = self._parse_ai_response(ai_response, event_context)

#             self.logger.info(
#                 f"AI evaluation for event {event.id}: {result['should_process']}")
#             return result

#         except Exception as e:
#             self.logger.error(
#                 f"AI evaluation failed for event {event.id}: {e}")
#             return {
#                 'should_process': False,
#                 'reason': f"AI evaluation error: {str(e)}",
#                 'confidence': 0.0
#             }

#     def _create_evaluation_prompt(self, ai_context: Dict[str, Any]) -> str:
#         """
#         Create evaluation prompt for AgentCore.

#         Args:
#             ai_context: Rich context for the event

#         Returns:
#             Formatted prompt string
#         """
#         event = ai_context['event']
#         timing = ai_context['timing']
#         recurrence = ai_context['recurrence']
#         processing = ai_context['processing']

#         prompt = f"""
# You are an intelligent calendar assistant evaluating whether an upcoming event needs attention.

# EVENT DETAILS:
# - Title: {event['title']}
# - Type: {event['type']}
# - Priority: {event['priority']}
# - Location: {event['location'] or 'Not specified'}
# - Start Time: {event['start_time']}
# - End Time: {event['end_time'] or 'Not specified'}
# - Description: {event['description'] or 'No description'}

# TIMING:
# - Time until start: {timing['time_until_start_hours']:.1f} hours
# - Is urgent: {timing['is_urgent']}
# - Is soon: {timing['is_soon']}

# RECURRENCE:
# - Recurrence hint: {recurrence['hint'] or 'None'}
# - Is recurring: {recurrence['is_recurring']}
# - Pattern: {recurrence['pattern']}

# PROCESSING HISTORY:
# - Status: {processing['status']}
# - Last processed: {processing['last_processed'] or 'Never'}
# - Days since last processed: {processing['days_since_last_processed'] or 'N/A'}

# EVALUATION TASK:
# Determine if this event needs attention and what actions should be taken.

# Consider:
# 1. Is this a recurring event that needs to be processed for this occurrence?
# 2. Is the event urgent or important enough to require immediate attention?
# 3. Has this event been handled recently and doesn't need re-processing?
# 4. What specific actions would be helpful for this event type?

# RESPONSE FORMAT:
# Respond with a JSON object containing:
# {{
#     "should_process": true/false,
#     "reason": "explanation of decision",
#     "confidence": 0.0-1.0,
#     "suggested_actions": ["action1", "action2", ...],
#     "event_type_analysis": "analysis of event type and requirements"
# }}

# Focus on intelligent decision-making based on the event context and timing.
# """
#         return prompt

#     async def _get_ai_evaluation(self, prompt: str, event_context: EventContext) -> str:
#         """
#         Get AI evaluation from AgentCore.

#         Args:
#             prompt: Evaluation prompt
#             event_context: Event context for user_id

#         Returns:
#             AI response string
#         """
#         try:
#             # Use AgentCore to evaluate the event
#             # We'll use a special user_id format to indicate this is an AI evaluation
#             user_id = f"ai_evaluator_{event_context.user_id}"

#             response = await self.agent_core.run(prompt, user_id)
#             return response

#         except Exception as e:
#             self.logger.error(f"Error getting AI evaluation: {e}")
#             raise

#     def _parse_ai_response(self, ai_response: str, event_context: EventContext) -> Dict[str, Any]:
#         """
#         Parse AI response into structured result.

#         Args:
#             ai_response: Raw AI response
#             event_context: Event context

#         Returns:
#             Parsed result dictionary
#         """
#         try:
#             # Try to extract JSON from response
#             json_start = ai_response.find('{')
#             json_end = ai_response.rfind('}') + 1

#             if json_start >= 0 and json_end > json_start:
#                 json_str = ai_response[json_start:json_end]
#                 parsed = json.loads(json_str)

#                 # Validate required fields
#                 required_fields = ['should_process', 'reason']
#                 for field in required_fields:
#                     if field not in parsed:
#                         raise ValueError(f"Missing required field: {field}")

#                 # Set defaults for optional fields
#                 parsed.setdefault('confidence', 0.5)
#                 parsed.setdefault('suggested_actions', [])
#                 parsed.setdefault('event_type_analysis', '')

#                 return parsed
#             else:
#                 # Fallback parsing for non-JSON responses
#                 return self._fallback_parse_response(ai_response)

#         except (json.JSONDecodeError, ValueError) as e:
#             self.logger.warning(f"Failed to parse AI response as JSON: {e}")
#             return self._fallback_parse_response(ai_response)

#     def _fallback_parse_response(self, ai_response: str) -> Dict[str, Any]:
#         """
#         Fallback parsing for non-JSON AI responses.

#         Args:
#             ai_response: Raw AI response

#         Returns:
#             Parsed result dictionary
#         """
#         response_lower = ai_response.lower()

#         # Simple keyword-based parsing
#         should_process = any(word in response_lower for word in [
#                              'yes', 'true', 'should', 'need', 'process'])
#         confidence = 0.7 if should_process else 0.3

#         # Extract reason from response
#         reason = "AI evaluation completed"
#         if "because" in response_lower:
#             because_index = response_lower.find("because")
#             reason = ai_response[because_index:].strip()
#         elif "reason" in response_lower:
#             reason_index = response_lower.find("reason")
#             reason = ai_response[reason_index:].strip()

#         return {
#             'should_process': should_process,
#             'reason': reason,
#             'confidence': confidence,
#             'suggested_actions': [],
#             'event_type_analysis': ''
#         }

#     async def analyze_recurrence_pattern(self, event_title: str, last_processed: Optional[datetime] = None) -> Dict[str, Any]:
#         """
#         Analyze recurrence pattern using AI.

#         Args:
#             event_title: Event title with recurrence hint
#             last_processed: When this event was last processed

#         Returns:
#             Analysis result
#         """
#         try:
#             # Build context for recurrence analysis
#             context = {
#                 "event_title": event_title,
#                 "last_processed": last_processed.isoformat() if last_processed else None,
#                 "current_time": datetime.utcnow().isoformat()
#             }

#             prompt = f"""
# Analyze this recurring event pattern:

# Event Title: {event_title}
# Last Processed: {last_processed.isoformat() if last_processed else 'Never'}
# Current Time: {datetime.utcnow().isoformat()}

# Determine:
# 1. What is the recurrence pattern?
# 2. Should this event be processed for the current time?
# 3. Is this the right time to handle this recurring event?

# Respond with JSON:
# {{
#     "pattern": "description of recurrence pattern",
#     "should_process_now": true/false,
#     "reason": "explanation",
#     "next_occurrence": "when this should be processed next"
# }}
# """

#             user_id = "ai_recurrence_analyzer"
#             response = await self.agent_core.run(prompt, user_id)

#             # Parse response
#             json_start = response.find('{')
#             json_end = response.rfind('}') + 1

#             if json_start >= 0 and json_end > json_start:
#                 json_str = response[json_start:json_end]
#                 return json.loads(json_str)
#             else:
#                 return {
#                     "pattern": "unknown",
#                     "should_process_now": False,
#                     "reason": "Could not parse AI response",
#                     "next_occurrence": "unknown"
#                 }

#         except Exception as e:
#             self.logger.error(f"Error analyzing recurrence pattern: {e}")
#             return {
#                 "pattern": "error",
#                 "should_process_now": False,
#                 "reason": f"Analysis error: {str(e)}",
#                 "next_occurrence": "unknown"
#             }

#     async def suggest_actions_for_event(self, event_context: EventContext) -> List[str]:
#         """
#         Get AI-suggested actions for an event.

#         Args:
#             event_context: Rich event context

#         Returns:
#             List of suggested actions
#         """
#         try:
#             ai_context = self.context_builder.create_ai_context(event_context)

#             prompt = f"""
# Based on this event, suggest specific actions that would be helpful:

# Event: {ai_context['event']['title']}
# Type: {ai_context['event']['type']}
# Priority: {ai_context['event']['priority']}
# Time until start: {ai_context['timing']['time_until_start_hours']:.1f} hours
# Is urgent: {ai_context['timing']['is_urgent']}

# Suggest 3-5 specific, actionable items that would help with this event.
# Focus on practical, useful actions.

# Respond with JSON:
# {{
#     "suggested_actions": ["action1", "action2", "action3"]
# }}
# """

#             user_id = f"ai_action_suggester_{event_context.user_id}"
#             response = await self.agent_core.run(prompt, user_id)

#             # Parse response
#             json_start = response.find('{')
#             json_end = response.rfind('}') + 1

#             if json_start >= 0 and json_end > json_start:
#                 json_str = response[json_start:json_end]
#                 parsed = json.loads(json_str)
#                 return parsed.get('suggested_actions', [])
#             else:
#                 return []

#         except Exception as e:
#             self.logger.error(f"Error suggesting actions: {e}")
#             return []


# def create_ai_evaluator(agent_core) -> AIEventEvaluator:
#     """
#     Factory function to create an AI evaluator.

#     Args:
#         agent_core: AgentCore instance

#     Returns:
#         AIEventEvaluator instance
#     """
#     return AIEventEvaluator(agent_core)
