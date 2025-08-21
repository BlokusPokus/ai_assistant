"""
AI Task Processing Module

This module handles AI-specific background tasks including:
- Processing due AI tasks
- Executing AI-driven workflows
- Managing AI task lifecycle
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..celery_app import app

# Import the existing AI scheduler components
from ...tools.ai_scheduler.ai_task_manager import AITaskManager
from ...tools.ai_scheduler.notification_service import NotificationService
from .ai_task_executor import TaskExecutor

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_due_ai_tasks(self) -> Dict[str, Any]:
    """
    Main task that runs every 10 minutes to check for due AI tasks.

    This task:
    1. Queries the database for due AI tasks
    2. Executes each task using the AI assistant
    3. Sends notifications based on task results
    4. Updates task status and schedules next run if recurring
    """
    task_id = self.request.id
    logger.info(f"Starting process_due_ai_tasks task {task_id}")

    try:
        # Use asyncio.run() with proper event loop handling
        import nest_asyncio

        # Apply nest_asyncio to allow nested event loops
        nest_asyncio.apply()

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function
        result = loop.run_until_complete(_process_due_ai_tasks_async(task_id))
        return result

    except Exception as e:
        logger.error(f"Task {task_id} failed with exception: {e}")
        # Retry the task
        raise self.retry(countdown=60, max_retries=3)


async def _process_due_ai_tasks_async(task_id: str) -> Dict[str, Any]:
    """
    Async implementation of the AI task processing logic.
    """
    task_manager = AITaskManager()
    notification_service = NotificationService()
    task_executor = TaskExecutor()

    try:
        # Get due tasks
        due_tasks = await task_manager.get_due_tasks(limit=50)
        logger.info(f"Found {len(due_tasks)} due AI tasks")

        if not due_tasks:
            return {
                'task_id': task_id,
                'status': 'success',
                'tasks_processed': 0,
                'tasks_failed': 0,
                'message': 'No due tasks found',
                'timestamp': datetime.utcnow().isoformat()
            }

        processed_tasks = 0
        failed_tasks = 0
        results = []

        for task in due_tasks:
            try:
                logger.info(
                    f"Processing AI task: {task.title} (ID: {task.id})")

                # Mark task as processing
                await task_manager.update_task_status(
                    task_id=task.id,
                    status='processing',
                    last_run_at=datetime.utcnow()
                )

                # Execute the task
                execution_result = await task_executor.execute_task(task)

                # Mark task as completed
                await task_manager.update_task_status(
                    task_id=task.id,
                    status='completed',
                    last_run_at=datetime.utcnow(),
                    result_data=execution_result
                )

                # Send notification if configured
                if task.notification_enabled:
                    await notification_service.send_task_completion_notification(
                        task, execution_result
                    )

                processed_tasks += 1
                results.append({
                    'success': True,
                    'message': 'Task executed successfully',
                    'task_id': task.id,
                    'task_title': task.title,
                    'task_type': task.task_type,
                    'execution_time': datetime.utcnow().isoformat(),
                    'ai_response': execution_result.get('ai_response', 'No response')
                })

                logger.info(
                    f"Successfully processed AI task: {task.title}")

            except Exception as e:
                logger.error(f"Failed to process AI task {task.id}: {e}")
                failed_tasks += 1

                # Mark task as failed
                await task_manager.update_task_status(
                    task_id=task.id,
                    status='failed',
                    last_run_at=datetime.utcnow(),
                    error_message=str(e)
                )

                results.append({
                    'success': False,
                    'message': f'Task execution failed: {str(e)}',
                    'task_id': task.id,
                    'task_title': task.title,
                    'task_type': task.task_type,
                    'execution_time': datetime.utcnow().isoformat(),
                    'error': str(e)
                })

        return {
            'task_id': task_id,
            'status': 'success',
            'tasks_processed': processed_tasks,
            'tasks_failed': failed_tasks,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in AI task processing: {e}")
        return {
            'task_id': task_id,
            'status': 'error',
            'message': f'AI task processing failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def create_ai_reminder(self, user_id: int, reminder_text: str,
                       reminder_time: datetime, reminder_type: str = 'reminder') -> Dict[str, Any]:
    """
    Create a new AI reminder task.

    Args:
        user_id: ID of the user creating the reminder
        reminder_text: Text content of the reminder
        reminder_time: When the reminder should trigger
        reminder_type: Type of reminder (reminder, task, etc.)

    Returns:
        Dict containing the result of reminder creation
    """
    task_id = self.request.id
    logger.info(f"Creating AI reminder task {task_id} for user {user_id}")

    try:
        # Use asyncio.run() with proper event loop handling
        import nest_asyncio
        nest_asyncio.apply()

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function
        result = loop.run_until_complete(_create_ai_reminder_async(
            user_id, reminder_text, reminder_time, reminder_type))
        return result

    except Exception as e:
        logger.error(f"Failed to create AI reminder: {e}")
        raise self.retry(countdown=60, max_retries=3)


async def _create_ai_reminder_async(user_id: int, reminder_text: str,
                                    reminder_time: datetime, reminder_type: str = 'reminder') -> Dict[str, Any]:
    """Async implementation of reminder creation."""
    task_manager = AITaskManager()

    # Create the reminder task
    reminder_task = await task_manager.create_ai_task(
        user_id=user_id,
        task_type=reminder_type,
        title=reminder_text,
        description=reminder_text,
        scheduled_time=reminder_time,
        notification_enabled=True
    )

    return {
        'task_id': None,  # Will be set by caller
        'status': 'success',
        'reminder_id': reminder_task.id,
        'message': 'AI reminder created successfully',
        'timestamp': datetime.utcnow().isoformat()
    }


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def create_periodic_ai_task(self, user_id: int, task_title: str,
                            task_description: str, schedule: str,
                            task_type: str = 'periodic') -> Dict[str, Any]:
    """
    Create a periodic AI task that repeats based on a schedule.

    Args:
        user_id: ID of the user creating the task
        task_title: Title of the periodic task
        task_description: Description of what the task does
        schedule: Cron-like schedule string
        task_type: Type of periodic task

    Returns:
        Dict containing the result of task creation
    """
    task_id = self.request.id
    logger.info(f"Creating periodic AI task {task_id} for user {user_id}")

    try:
        # Use asyncio.run() with proper event loop handling
        import nest_asyncio
        nest_asyncio.apply()

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function
        result = loop.run_until_complete(_create_periodic_ai_task_async(
            user_id, task_title, task_description, schedule, task_type))
        return result

    except Exception as e:
        logger.error(f"Failed to create periodic AI task: {e}")
        raise self.retry(countdown=60, max_retries=3)


async def _create_periodic_ai_task_async(user_id: int, task_title: str,
                                         task_description: str, schedule: str,
                                         task_type: str = 'periodic') -> Dict[str, Any]:
    """Async implementation of periodic task creation."""
    task_manager = AITaskManager()

    # Create the periodic task
    periodic_task = await task_manager.create_periodic_ai_task(
        user_id=user_id,
        task_type=task_type,
        title=task_title,
        description=task_description,
        schedule=schedule,
        notification_enabled=True
    )

    return {
        'task_id': None,  # Will be set by caller
        'status': 'success',
        'periodic_task_id': periodic_task.id,
        'message': 'Periodic AI task created successfully',
        'timestamp': datetime.utcnow().isoformat()
    }


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def test_scheduler_connection(self) -> Dict[str, Any]:
    """
    Test task to verify scheduler connectivity and basic functionality.

    Returns:
        Dict containing test results
    """
    task_id = self.request.id
    logger.info(f"Testing scheduler connection for task {task_id}")

    try:
        # Use asyncio.run() with proper event loop handling
        import nest_asyncio
        nest_asyncio.apply()

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function
        result = loop.run_until_complete(_test_scheduler_connection_async())
        return result

    except Exception as e:
        logger.error(f"Scheduler connection test failed: {e}")
        return {
            'task_id': task_id,
            'status': 'error',
            'message': f'Scheduler connection test failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }


async def _test_scheduler_connection_async() -> Dict[str, Any]:
    """Async implementation of connection testing."""
    # Test database connection
    task_manager = AITaskManager()
    test_result = await task_manager.test_connection()

    return {
        'task_id': None,  # Will be set by caller
        'status': 'success',
        'test_result': test_result,
        'message': 'Scheduler connection test successful',
        'timestamp': datetime.utcnow().isoformat()
    }


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_old_logs(self) -> Dict[str, Any]:
    """
    Clean up old AI task logs and results.

    Returns:
        Dict containing cleanup results
    """
    task_id = self.request.id
    logger.info(f"Starting log cleanup task {task_id}")

    try:
        # Use asyncio.run() with proper event loop handling
        import nest_asyncio
        nest_asyncio.apply()

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function
        result = loop.run_until_complete(_cleanup_old_logs_async())
        return result

    except Exception as e:
        logger.error(f"Log cleanup failed: {e}")
        raise self.retry(countdown=60, max_retries=3)


async def _cleanup_old_logs_async() -> Dict[str, Any]:
    """Async implementation of log cleanup."""
    task_manager = AITaskManager()

    # Clean up old logs (older than 30 days)
    cleanup_date = datetime.utcnow() - timedelta(days=30)
    cleaned_count = await task_manager.cleanup_old_logs(cleanup_date)

    return {
        'task_id': None,  # Will be set by caller
        'status': 'success',
        'cleaned_logs': cleaned_count,
        'message': f'Cleaned up {cleaned_count} old logs',
        'timestamp': datetime.utcnow().isoformat()
    }
