"""
Action parser for AI-suggested actions from Task 003.

This module parses AI-suggested actions from evaluation results and converts
them into structured, executable actions.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .evaluation_engine import EvaluationResult

logger = logging.getLogger(__name__)


@dataclass
class Action:
    """Structured action for execution."""
    type: str
    description: str
    priority: str = 'medium'
    timing: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionResult:
    """Result of action execution."""
    action: Action
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None


class ActionParser:
    """
    Parser for AI-suggested actions.

    This class takes AI-suggested actions from evaluation results and
    converts them into structured, executable actions.
    """

    def __init__(self):
        self.logger = logger

    def parse_ai_actions(self, evaluation_result: EvaluationResult) -> List[Action]:
        """
        Parse AI-suggested actions into executable format.

        Args:
            evaluation_result: Evaluation result with AI suggestions

        Returns:
            List of structured actions
        """
        actions = []

        if not evaluation_result.ai_suggested_actions:
            return actions

        for action_text in evaluation_result.ai_suggested_actions:
            try:
                action = self._parse_action_text(action_text)
                if action:
                    actions.append(action)
                    self.logger.info(
                        f"Parsed action: {action.type} - {action.description}")
            except Exception as e:
                self.logger.error(f"Error parsing action '{action_text}': {e}")

        return actions

    def _parse_action_text(self, action_text: str) -> Optional[Action]:
        """
        Parse action text and determine type and parameters.

        Args:
            action_text: Raw action text from AI

        Returns:
            Structured Action object or None if parsing fails
        """
        if not action_text or not action_text.strip():
            return None

        action_text_lower = action_text.lower().strip()

        # Extract timing information
        timing = self._extract_timing(action_text_lower)

        # Determine action type based on keywords
        action_type = self._determine_action_type(action_text_lower)

        # Determine priority based on urgency keywords
        priority = self._determine_priority(action_text_lower)

        # Extract parameters
        parameters = self._extract_parameters(action_text_lower)

        return Action(
            type=action_type,
            description=action_text.strip(),
            priority=priority,
            timing=timing,
            parameters=parameters
        )

    def _determine_action_type(self, action_text: str) -> str:
        """
        Determine action type based on keywords.

        Args:
            action_text: Lowercase action text

        Returns:
            Action type string
        """
        # SMS/Text notifications (primary method for all notifications)
        if any(word in action_text for word in ['sms', 'text', 'message', 'send reminder', 'notify', 'send notification']):
            return 'sms'

        # Email notifications (fallback, but prefer SMS)
        if any(word in action_text for word in ['email', 'send email']):
            return 'sms'  # Route email requests to SMS instead

        # Reminders/Tasks
        if any(word in action_text for word in ['reminder', 'task', 'todo', 'create reminder', 'create task']):
            return 'reminder'

        # Preparation tasks
        if any(word in action_text for word in ['prepare', 'preparation', 'check', 'review']):
            return 'preparation'

        # Document requests
        if any(word in action_text for word in ['document', 'file', 'attachment', 'bring']):
            return 'document'

        # Research tasks
        if any(word in action_text for word in ['research', 'look up', 'find', 'search']):
            return 'research'

        # Default to SMS for any general notification
        if any(word in action_text for word in ['send', 'notify', 'alert', 'remind']):
            return 'sms'

        # Default to general action
        return 'general'

    def _determine_priority(self, action_text: str) -> str:
        """
        Determine action priority based on urgency keywords.

        Args:
            action_text: Lowercase action text

        Returns:
            Priority level
        """
        # High priority keywords
        if any(word in action_text for word in ['urgent', 'immediate', 'now', 'asap', 'critical']):
            return 'high'

        # Medium priority keywords
        if any(word in action_text for word in ['soon', 'shortly', 'prepare', 'check']):
            return 'medium'

        # Default to medium priority
        return 'medium'

    def _extract_timing(self, action_text: str) -> Optional[str]:
        """
        Extract timing information from action text.

        Args:
            action_text: Lowercase action text

        Returns:
            Timing string or None
        """
        # Common timing patterns
        timing_patterns = [
            r'(\d+)\s*(minutes?|mins?)\s*before',
            r'(\d+)\s*(hours?|hrs?)\s*before',
            r'(\d+)\s*(days?)\s*before',
            r'(\d+)\s*(minutes?|mins?)\s*after',
            r'(\d+)\s*(hours?|hrs?)\s*after',
            r'immediately',
            r'now',
            r'asap',
            r'soon'
        ]

        for pattern in timing_patterns:
            match = re.search(pattern, action_text)
            if match:
                if pattern in ['immediately', 'now', 'asap', 'soon']:
                    return match.group(0)
                else:
                    return match.group(0)

        return None

    def _extract_parameters(self, action_text: str) -> Dict[str, Any]:
        """
        Extract additional parameters from action text.

        Args:
            action_text: Lowercase action text

        Returns:
            Dictionary of parameters
        """
        parameters = {}

        # Extract phone number patterns
        phone_match = re.search(
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', action_text)
        if phone_match:
            parameters['phone_number'] = phone_match.group(0)

        # Extract email patterns
        email_match = re.search(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', action_text)
        if email_match:
            parameters['email'] = email_match.group(0)

        # Extract duration
        duration_match = re.search(
            r'(\d+)\s*(minutes?|mins?|hours?|hrs?)', action_text)
        if duration_match:
            parameters['duration'] = {
                'value': int(duration_match.group(1)),
                'unit': duration_match.group(2)
            }

        # Extract location
        location_patterns = [
            r'at\s+([A-Za-z0-9\s]+)',
            r'in\s+([A-Za-z0-9\s]+)',
            r'location:\s*([A-Za-z0-9\s]+)'
        ]

        for pattern in location_patterns:
            location_match = re.search(pattern, action_text)
            if location_match:
                parameters['location'] = location_match.group(1).strip()
                break

        return parameters

    def validate_action(self, action: Action) -> bool:
        """
        Validate that an action has required parameters.

        Args:
            action: Action to validate

        Returns:
            True if valid, False otherwise
        """
        if not action.type or not action.description:
            return False

        # Validate action type
        valid_types = ['sms', 'email', 'reminder',
                       'preparation', 'document', 'research', 'general']
        if action.type not in valid_types:
            self.logger.warning(f"Invalid action type: {action.type}")
            return False

        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        if action.priority not in valid_priorities:
            self.logger.warning(f"Invalid priority: {action.priority}")
            return False

        return True

    def get_action_summary(self, actions: List[Action]) -> Dict[str, Any]:
        """
        Generate summary of parsed actions.

        Args:
            actions: List of parsed actions

        Returns:
            Summary dictionary
        """
        if not actions:
            return {
                'total_actions': 0,
                'action_types': {},
                'priorities': {},
                'timing': {}
            }

        action_types = {}
        priorities = {}
        timing = {}

        for action in actions:
            # Count action types
            action_types[action.type] = action_types.get(action.type, 0) + 1

            # Count priorities
            priorities[action.priority] = priorities.get(
                action.priority, 0) + 1

            # Count timing
            if action.timing:
                timing[action.timing] = timing.get(action.timing, 0) + 1

        return {
            'total_actions': len(actions),
            'action_types': action_types,
            'priorities': priorities,
            'timing': timing
        }


def create_action_parser() -> ActionParser:
    """
    Factory function to create an action parser.

    Returns:
        ActionParser instance
    """
    return ActionParser()
