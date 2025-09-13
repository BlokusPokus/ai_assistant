"""
Evaluation engine for calendar events using AI-first approach.

This module provides simple evaluation logic that checks if events have been handled
and leverages AgentCore intelligence to determine actionable events.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .evaluator import AIEventEvaluator
from .context_builder import EventContextBuilder
# TODO: Implement db_queries functions or import from appropriate location
# from .db_queries import get_event_by_id, get_upcoming_events

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of event evaluation."""
    event_id: int
    should_process: bool
    reason: str
    ai_suggested_actions: Optional[List[str]] = None
    confidence: float = 0.0


class EventEvaluationEngine:
    """
    Evaluation engine for calendar events using AI-first approach.

    This engine combines simple database checks with AI-powered evaluation
    to determine which events need attention and what actions to take.
    """

    def __init__(self, agent_core=None):
        """
        Initialize the evaluation engine.

        Args:
            agent_core: AgentCore instance for AI evaluation
        """
        self.agent_core = agent_core
        self.context_builder = EventContextBuilder()
        self.ai_evaluator = AIEventEvaluator(
            agent_core) if agent_core else None
        self.logger = logger

    async def evaluate_upcoming_events(self, hours_ahead: int = 2) -> List[EvaluationResult]:
        """
        Evaluate all upcoming events to determine which need processing.

        Args:
            hours_ahead: Number of hours to look ahead

        Returns:
            List of evaluation results
        """
        try:
            # TODO: Implement get_upcoming_events function
            # Get upcoming events from database
            # events = await get_upcoming_events(hours_ahead=hours_ahead)
            events = []  # Placeholder until db_queries is implemented

            self.logger.info(f"Evaluating {len(events)} upcoming events")

            evaluation_results = []
            for event in events:
                try:
                    result = await self._evaluate_single_event(event)
                    evaluation_results.append(result)
                except Exception as e:
                    self.logger.error(
                        f"Error evaluating event {event.id}: {e}")
                    # Create failed result
                    evaluation_results.append(EvaluationResult(
                        event_id=event.id,
                        should_process=False,
                        reason=f"Evaluation error: {str(e)}"
                    ))

            # Count results
            should_process = [
                r for r in evaluation_results if r.should_process]
            self.logger.info(
                f"Evaluation complete: {len(should_process)} events need processing")

            return evaluation_results

        except Exception as e:
            self.logger.error(f"Error in evaluate_upcoming_events: {e}")
            return []

    async def _evaluate_single_event(self, event) -> EvaluationResult:
        """
        Evaluate a single event using simple checks and AI analysis.

        Args:
            event: Event object to evaluate

        Returns:
            EvaluationResult with decision and reasoning
        """
        # Step 1: Simple database checks
        simple_check = await self._simple_event_check(event)
        if not simple_check['should_process']:
            return EvaluationResult(
                event_id=event.id,
                should_process=False,
                reason=simple_check['reason']
            )

        # Step 2: AI-powered evaluation (if AgentCore available)
        if self.ai_evaluator:
            try:
                ai_result = await self.ai_evaluator.evaluate_event(event)
                return EvaluationResult(
                    event_id=event.id,
                    should_process=ai_result['should_process'],
                    reason=ai_result['reason'],
                    ai_suggested_actions=ai_result.get('suggested_actions'),
                    confidence=ai_result.get('confidence', 0.0)
                )
            except Exception as e:
                self.logger.error(
                    f"AI evaluation failed for event {event.id}: {e}")
                # Fall back to simple check
                return EvaluationResult(
                    event_id=event.id,
                    should_process=simple_check['should_process'],
                    reason=f"AI evaluation failed, using simple check: {simple_check['reason']}"
                )
        else:
            # No AI evaluator available, use simple check
            return EvaluationResult(
                event_id=event.id,
                should_process=simple_check['should_process'],
                reason=simple_check['reason']
            )

    async def _simple_event_check(self, event) -> Dict[str, Any]:
        """
        Perform simple database checks to determine if event should be processed.

        Args:
            event: Event object to check

        Returns:
            Dict with should_process boolean and reason string
        """
        now = datetime.utcnow()

        # Check 1: Has event been handled recently?
        if event.handled_at:
            time_since_handled = now - event.handled_at
            if time_since_handled < timedelta(hours=24):
                return {
                    'should_process': False,
                    'reason': f"Event handled recently ({time_since_handled.total_seconds() / 3600:.1f} hours ago)"
                }

        # Check 2: Is event in the right time window?
        if event.start_time > now + timedelta(hours=2):
            return {
                'should_process': False,
                'reason': f"Event too far in future (starts in {(event.start_time - now).total_seconds() / 3600:.1f} hours)"
            }

        # Check 3: Is event already in progress or past?
        if event.start_time < now:
            return {
                'should_process': False,
                'reason': "Event has already started or is in the past"
            }

        # Check 4: Is event status appropriate?
        if event.processing_status not in ['pending', 'failed']:
            return {
                'should_process': False,
                'reason': f"Event status is '{event.processing_status}', not ready for processing"
            }

        # All checks passed
        return {
            'should_process': True,
            'reason': "Event passes all simple checks"
        }

    async def evaluate_event_by_id(self, event_id: int) -> Optional[EvaluationResult]:
        """
        Evaluate a specific event by ID.

        Args:
            event_id: ID of the event to evaluate

        Returns:
            EvaluationResult or None if event not found
        """
        try:
            # TODO: Implement get_event_by_id function
            # event = await get_event_by_id(event_id)
            event = None  # Placeholder until db_queries is implemented
            if not event:
                self.logger.warning(f"Event {event_id} not found")
                return None

            return await self._evaluate_single_event(event)

        except Exception as e:
            self.logger.error(f"Error evaluating event {event_id}: {e}")
            return None

    def get_evaluation_summary(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Generate a summary of evaluation results.

        Args:
            results: List of evaluation results

        Returns:
            Summary dictionary
        """
        total_events = len(results)
        should_process = [r for r in results if r.should_process]
        failed_evaluations = [
            r for r in results if "error" in r.reason.lower()]

        return {
            'total_events': total_events,
            'should_process': len(should_process),
            'should_not_process': total_events - len(should_process),
            'failed_evaluations': len(failed_evaluations),
            'ai_evaluated': len([r for r in results if r.ai_suggested_actions is not None]),
            'simple_check_only': len([r for r in results if r.ai_suggested_actions is None])
        }


def create_evaluation_engine(agent_core=None) -> EventEvaluationEngine:
    """
    Factory function to create an evaluation engine.

    Args:
        agent_core: Optional AgentCore instance

    Returns:
        EventEvaluationEngine instance
    """
    return EventEvaluationEngine(agent_core)
