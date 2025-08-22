# """
# AI Task Scheduler for handling AI-driven tasks and reminders.

# This module provides Celery tasks for scheduling and executing AI tasks,
# including reminders and automated tasks.
# """

# import asyncio
# import logging
# import os
# from datetime import datetime, timedelta
# from typing import Any, Dict, List

# from .ai_task_manager import AITaskManager
# from .celery_config import app
# from .notification_service import (
#     NotificationService,
# )
# from .task_executor import TaskExecutor

# logger = logging.getLogger(__name__)


# @app.task(bind=True, max_retries=3, default_retry_delay=60)
# def process_due_ai_tasks(self) -> Dict[str, Any]:
#     """
#     Main task that runs every 10 minutes to check for due AI tasks.

#     This task:
#     1. Queries the database for due AI tasks
#     2. Executes each task using the AI assistant
#     3. Sends notifications based on task results
#     4. Updates task status and schedules next run if recurring
#     """
#     task_id = self.request.id
#     logger.info(f"Starting process_due_ai_tasks task {task_id}")

#     try:
#         # Use asyncio.run() with proper event loop handling
#         import asyncio

#         import nest_asyncio

#         # Apply nest_asyncio to allow nested event loops
#         nest_asyncio.apply()

#         # Get or create event loop
#         try:
#             loop = asyncio.get_event_loop()
#         except RuntimeError:
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)

#         # Run the async function
#         result = loop.run_until_complete(_process_due_ai_tasks_async(task_id))
#         return result

#     except Exception as e:
#         logger.error(f"Task {task_id} failed with exception: {e}")
#         # Retry the task
#         raise self.retry(countdown=60, max_retries=3)


# async def _process_due_ai_tasks_async(task_id: str) -> Dict[str, Any]:
#     """
#     Async implementation of the AI task processing logic.
#     """
#     task_manager = AITaskManager()
#     notification_service = NotificationService()
#     task_executor = TaskExecutor()

#     try:
#         # Get due tasks
#         due_tasks = await task_manager.get_due_tasks(limit=50)
#         logger.info(f"Found {len(due_tasks)} due AI tasks")

#         if not due_tasks:
#             return {
#                 'task_id': task_id,
#                 'status': 'success',
#                 'tasks_processed': 0,
#                 'tasks_failed': 0,
#                 'message': 'No due tasks found'
#             }

#         processed_tasks = 0
#         failed_tasks = 0
#         results = []

#         for task in due_tasks:
#             try:
#                 logger.info(
#                     f"Processing AI task: {task.title} (ID: {task.id})")

#                 # Mark task as processing
#                 await task_manager.update_task_status(
#                     task_id=task.id,
#                     status='processing',
#                     last_run_at=datetime.utcnow()
#                 )

#                 # Execute the task
#                 execution_result = await task_executor.execute_task(task)

#                 # Update task status based on result
#                 if execution_result.get('success', False):
#                     # Calculate next run time for recurring tasks
#                     next_run_at = None
#                     if task.schedule_type != 'once':
#                         next_run_at = await task_manager.calculate_next_run(
#                             task.schedule_type,
#                             task.schedule_config
#                         )

#                     await task_manager.update_task_status(
#                         task_id=task.id,
#                         status='active' if next_run_at else 'completed',
#                         next_run_at=next_run_at
#                     )

#                     # Send notification if configured
#                     if task.should_notify():
#                         # TODO: Get user phone number from user settings
#                         user_phone = os.getenv('TWILIO_TO_NUMBER')  # Temporary
#                         if user_phone:
#                             await notification_service.send_task_completion_notification(
#                                 task=task,
#                                 result=execution_result,
#                                 user_phone=user_phone
#                             )

#                     processed_tasks += 1
#                     logger.info(f"Successfully processed task: {task.title}")

#                 else:
#                     # Mark task as failed
#                     await task_manager.update_task_status(
#                         task_id=task.id,
#                         status='failed'
#                     )
#                     failed_tasks += 1
#                     logger.error(f"Failed to process task: {task.title}")

#                 results.append({
#                     'task_id': task.id,
#                     'title': task.title,
#                     'result': execution_result
#                 })

#             except Exception as e:
#                 logger.error(f"Error processing task {task.id}: {e}")
#                 await task_manager.update_task_status(
#                     task_id=task.id,
#                     status='failed'
#                 )
#                 failed_tasks += 1

#         return {
#             'task_id': task_id,
#             'status': 'success',
#             'tasks_processed': processed_tasks,
#             'tasks_failed': failed_tasks,
#             'total_tasks': len(due_tasks),
#             'results': results
#         }

#     except Exception as e:
#         logger.error(f"Error in AI task processing: {e}")
#         return {
#             'task_id': task_id,
#             'status': 'failed',
#             'error': str(e),
#             'tasks_processed': 0,
#             'tasks_failed': 0
#         }


# @app.task
# def test_scheduler_connection() -> Dict[str, Any]:
#     """
#     Test task to verify the scheduler is working.
#     """
#     logger.info("Testing scheduler connection")
#     return {
#         'status': 'success',
#         'message': 'Scheduler is working',
#         'timestamp': datetime.utcnow().isoformat()
#     }


# @app.task
# def cleanup_old_logs() -> Dict[str, Any]:
#     """
#     Clean up old task logs and completed tasks.
#     """
#     try:
#         result = asyncio.run(_cleanup_old_logs_async())
#         return result
#     except Exception as e:
#         logger.error(f"Error in cleanup task: {e}")
#         return {
#             'status': 'failed',
#             'error': str(e)
#         }


# async def _cleanup_old_logs_async() -> Dict[str, Any]:
#     """
#     Async implementation of log cleanup.
#     """
#     task_manager = AITaskManager()

#     try:
#         # Get completed tasks older than 30 days
#         cutoff_date = datetime.utcnow() - timedelta(days=30)

#         # TODO: Implement cleanup logic for old completed tasks
#         # For now, just return success

#         logger.info("Cleanup task completed")
#         return {
#             'status': 'success',
#             'message': 'Cleanup completed',
#             'timestamp': datetime.utcnow().isoformat()
#         }

#     except Exception as e:
#         logger.error(f"Error in cleanup: {e}")
#         return {
#             'status': 'failed',
#             'error': str(e)
#         }


# @app.task
# def create_ai_reminder(
#     user_id: int,
#     title: str,
#     remind_at: str,
#     description: str = None,
#     notification_channels: List[str] = None
# ) -> Dict[str, Any]:
#     """
#     Create a new AI reminder task.

#     Args:
#         user_id: User ID
#         title: Reminder title
#         remind_at: When to send the reminder (ISO format)
#         description: Reminder description
#         notification_channels: List of notification channels

#     Returns:
#         Dictionary with creation result
#     """
#     try:
#         result = asyncio.run(_create_ai_reminder_async(
#             user_id, title, remind_at, description, notification_channels
#         ))
#         return result
#     except Exception as e:
#         logger.error(f"Error creating AI reminder: {e}")
#         return {
#             'status': 'failed',
#             'error': str(e)
#         }


# async def _create_ai_reminder_async(
#     user_id: int,
#     title: str,
#     remind_at: str,
#     description: str = None,
#     notification_channels: List[str] = None
# ) -> Dict[str, Any]:
#     """
#     Async implementation of AI reminder creation.
#     """
#     task_manager = AITaskManager()

#     try:
#         # Parse remind_at datetime
#         remind_datetime = datetime.fromisoformat(remind_at)

#         # Create the reminder task
#         task = await task_manager.create_reminder(
#             user_id=user_id,
#             title=title,
#             remind_at=remind_datetime,
#             description=description,
#             notification_channels=notification_channels or ['sms']
#         )

#         logger.info(f"Created AI reminder: {task.title} (ID: {task.id})")

#         return {
#             'status': 'success',
#             'task_id': task.id,
#             'title': task.title,
#             'remind_at': task.next_run_at.isoformat() if task.next_run_at else None
#         }

#     except Exception as e:
#         logger.error(f"Error creating AI reminder: {e}")
#         return {
#             'status': 'failed',
#             'error': str(e)
#         }


# @app.task
# def create_periodic_ai_task(
#     user_id: int,
#     title: str,
#     schedule_type: str,
#     schedule_config: Dict[str, Any],
#     description: str = None,
#     ai_context: str = None,
#     notification_channels: List[str] = None
# ) -> Dict[str, Any]:
#     """
#     Create a new periodic AI task.

#     Args:
#         user_id: User ID
#         title: Task title
#         schedule_type: Schedule type ('daily', 'weekly', 'monthly', 'custom')
#         schedule_config: Schedule configuration
#         description: Task description
#         ai_context: AI context for task execution
#         notification_channels: List of notification channels

#     Returns:
#         Dictionary with creation result
#     """
#     try:
#         result = asyncio.run(_create_periodic_ai_task_async(
#             user_id, title, schedule_type, schedule_config,
#             description, ai_context, notification_channels
#         ))
#         return result
#     except Exception as e:
#         logger.error(f"Error creating periodic AI task: {e}")
#         return {
#             'status': 'failed',
#             'error': str(e)
#         }


# async def _create_periodic_ai_task_async(
#     user_id: int,
#     title: str,
#     schedule_type: str,
#     schedule_config: Dict[str, Any],
#     description: str = None,
#     ai_context: str = None,
#     notification_channels: List[str] = None
# ) -> Dict[str, Any]:
#     """
#     Async implementation of periodic AI task creation.
#     """
#     task_manager = AITaskManager()

#     try:
#         # Create the periodic task
#         task = await task_manager.create_periodic_task(
#             user_id=user_id,
#             title=title,
#             schedule_type=schedule_type,
#             schedule_config=schedule_config,
#             description=description,
#             ai_context=ai_context,
#             notification_channels=notification_channels or ['sms']
#         )

#         logger.info(f"Created periodic AI task: {task.title} (ID: {task.id})")

#         return {
#             'status': 'success',
#             'task_id': task.id,
#             'title': task.title,
#             'schedule_type': task.schedule_type,
#             'next_run_at': task.next_run_at.isoformat() if task.next_run_at else None
#         }

#     except Exception as e:
#         logger.error(f"Error creating periodic AI task: {e}")
#         return {
#             'status': 'failed',
#             'error': str(e)
#         }
