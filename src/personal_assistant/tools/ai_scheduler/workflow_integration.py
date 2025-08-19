"""
Complete workflow integration for the AI-first calendar scheduler system.

This module integrates all components from Tasks 001-004 into a seamless
end-to-end workflow with comprehensive monitoring and error handling.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from .action_executor import create_action_executor
from .action_parser import create_action_parser
from .context_builder import create_context_builder
from .db_queries import get_event_by_id, mark_event_completed, mark_event_failed
from .evaluation_engine import create_evaluation_engine

logger = logging.getLogger(__name__)


class WorkflowIntegration:
    """
    Complete workflow integration for event processing.

    This class integrates all components:
    1. Event retrieval and context building
    2. AI evaluation and decision-making
    3. Action parsing and execution
    4. Result tracking and logging
    """

    def __init__(self):
        self.logger = logger
        self.evaluation_engine = create_evaluation_engine()
        self.context_builder = create_context_builder()
        self.action_parser = create_action_parser()
        self.action_executor = create_action_executor()

    async def complete_event_workflow(self, event_id: int) -> Dict[str, Any]:
        """
        Complete end-to-end event processing workflow.

        This integrates all components:
        1. Event retrieval and context building
        2. AI evaluation and decision-making
        3. Action parsing and execution
        4. Result tracking and logging

        Args:
            event_id: ID of the event to process

        Returns:
            Dictionary with workflow results
        """
        start_time = time.time()

        try:
            self.logger.info(
                f"Starting complete workflow for event {event_id}")

            # Step 1: Get event and build context
            event = await get_event_by_id(event_id)
            if not event:
                raise ValueError(f"Event {event_id} not found")

            event_context = self.context_builder.build_event_context(event)
            self.logger.info(
                f"Built context for event {event_id}: {event.title}")

            # Step 2: AI evaluation
            evaluation_result = await self.evaluation_engine.evaluate_single_event(event)
            self.logger.info(
                f"Evaluation result for event {event_id}: {evaluation_result.should_process} - {evaluation_result.reason}")

            # Step 3: Action execution (if needed)
            actions_executed = 0
            execution_summary = {}

            if evaluation_result.should_process:
                actions = self.action_parser.parse_ai_actions(
                    evaluation_result)
                self.logger.info(
                    f"Parsed {len(actions)} actions for event {event_id}")

                if actions:
                    execution_results = await self.action_executor.execute_actions(actions, event_context)
                    actions_executed = len(execution_results)
                    execution_summary = self.action_executor.get_execution_summary(
                        execution_results)

                    self.logger.info(
                        f"Executed {actions_executed} actions for event {event_id}")
                else:
                    self.logger.info(
                        f"No actions to execute for event {event_id}")

            # Step 4: Update event status
            await mark_event_completed(event_id, evaluation_result.reason)

            # Calculate execution time
            execution_time = time.time() - start_time

            self.logger.info(
                f"Workflow completed for event {event_id} in {execution_time:.2f}s")

            return {
                'success': True,
                'event_id': event_id,
                'event_title': event.title,
                'evaluation': {
                    'should_process': evaluation_result.should_process,
                    'reason': evaluation_result.reason,
                    'suggested_actions': evaluation_result.ai_suggested_actions
                },
                'actions_executed': actions_executed,
                'execution_summary': execution_summary,
                'execution_time': execution_time
            }

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Workflow failed for event {event_id} after {execution_time:.2f}s: {e}")

            # Mark event as failed
            await mark_event_failed(event_id, str(e))

            return {
                'success': False,
                'event_id': event_id,
                'error': str(e),
                'execution_time': execution_time
            }

    async def process_multiple_events(self, event_ids: list[int]) -> Dict[str, Any]:
        """
        Process multiple events in parallel.

        Args:
            event_ids: List of event IDs to process

        Returns:
            Dictionary with batch processing results
        """
        start_time = time.time()

        self.logger.info(
            f"Starting batch processing for {len(event_ids)} events")

        # Process events concurrently
        tasks = [self.complete_event_workflow(
            event_id) for event_id in event_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful = [r for r in results if isinstance(
            r, dict) and r.get('success')]
        failed = [r for r in results if isinstance(
            r, dict) and not r.get('success')]
        exceptions = [r for r in results if isinstance(r, Exception)]

        total_execution_time = time.time() - start_time

        self.logger.info(
            f"Batch processing completed: {len(successful)} successful, {len(failed)} failed, {len(exceptions)} exceptions")

        return {
            'success': True,
            'total_events': len(event_ids),
            'successful': len(successful),
            'failed': len(failed),
            'exceptions': len(exceptions),
            'total_execution_time': total_execution_time,
            'average_execution_time': total_execution_time / len(event_ids) if event_ids else 0,
            'results': results
        }

    async def get_workflow_status(self, event_id: int) -> Dict[str, Any]:
        """
        Get the current status of a workflow for an event.

        Args:
            event_id: ID of the event

        Returns:
            Dictionary with workflow status
        """
        try:
            event = await get_event_by_id(event_id)
            if not event:
                return {
                    'event_id': event_id,
                    'status': 'not_found',
                    'message': 'Event not found'
                }

            # Check processing status
            if event.processing_status == 'completed':
                return {
                    'event_id': event_id,
                    'status': 'completed',
                    'title': event.title,
                    'handled_at': event.handled_at,
                    'agent_response': event.agent_response
                }
            elif event.processing_status == 'failed':
                return {
                    'event_id': event_id,
                    'status': 'failed',
                    'title': event.title,
                    'last_checked': event.last_checked
                }
            elif event.processing_status == 'processing':
                return {
                    'event_id': event_id,
                    'status': 'processing',
                    'title': event.title,
                    'last_checked': event.last_checked
                }
            else:
                return {
                    'event_id': event_id,
                    'status': 'pending',
                    'title': event.title
                }

        except Exception as e:
            return {
                'event_id': event_id,
                'status': 'error',
                'error': str(e)
            }


def create_workflow_integration() -> WorkflowIntegration:
    """
    Factory function to create a workflow integration instance.

    Returns:
        WorkflowIntegration instance
    """
    return WorkflowIntegration()
