"""
AI Task Processing Module

This module handles AI-specific background tasks including:
- Processing due AI tasks
- Executing AI-driven workflows
- Managing AI task lifecycle
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Import the existing AI scheduler components
from ...tools.ai_scheduler.core.task_manager import AITaskManager
from ..celery_app import app

from ...tools.ai_scheduler.notifications.service import NotificationService
from ...tools.ai_scheduler.core.executor import TaskExecutor

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_due_ai_tasks(self) -> Dict[str, Any]:
    """
    Main task that runs every 1 minute to check for due AI tasks.

    This task:
    1. Queries the database for due AI tasks
    2. Executes each task using the AI assistant
    3. Sends notifications based on task results
    4. Updates task status and schedules next run if recurring
    """
    task_id = self.request.id
    current_time = datetime.utcnow()
    
    # Enhanced logging for Celery beat tracking
    logger.info(f"🚀 CELERY BEAT TRIGGERED: process_due_ai_tasks started at {current_time}")
    logger.info(f"📋 Task ID: {task_id}")
    logger.info(f"⏰ Current UTC time: {current_time}")
    print(f"🚀 CELERY BEAT TRIGGERED: process_due_ai_tasks started at {current_time}")
    print(f"📋 Task ID: {task_id}")
    print(f"⏰ Current UTC time: {current_time}")

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
        print("🔍 BREAKPOINT 2: About to call _process_due_ai_tasks_async")
        result = loop.run_until_complete(_process_due_ai_tasks_async(task_id))
        print(f"🔍 BREAKPOINT 3: _process_due_ai_tasks_async completed, result: {result}")
        return result

    except Exception as e:
        logger.error(f"Task {task_id} failed with exception: {e}")
        # Retry the task
        raise self.retry(countdown=60, max_retries=3)


async def _process_due_ai_tasks_async(task_id: str) -> Dict[str, Any]:
    """
    Async implementation of the AI task processing logic.
    """
    current_time = datetime.utcnow()
    logger.info(f"🔄 ASYNC PROCESSING: Starting _process_due_ai_tasks_async at {current_time}")
    print(f"🔄 ASYNC PROCESSING: Starting _process_due_ai_tasks_async at {current_time}")
    
    task_manager = AITaskManager()
    notification_service = NotificationService()
    task_executor = TaskExecutor()

    try:
        # Get due tasks
        logger.info(f"🔍 DATABASE QUERY: Checking for due tasks...")
        print(f"🔍 DATABASE QUERY: Checking for due tasks...")
        
        due_tasks = await task_manager.get_due_tasks(limit=50)
        logger.info(f"📊 DUE TASKS FOUND: {len(due_tasks)} due AI tasks")
        print(f"📊 DUE TASKS FOUND: {len(due_tasks)} due AI tasks")
        
        # Log details of each due task
        for i, task in enumerate(due_tasks):
            logger.info(f"📋 Task {i+1}: ID={task.id}, Title='{task.title}', Due={task.next_run_at}")
            print(f"📋 Task {i+1}: ID={task.id}, Title='{task.title}', Due={task.next_run_at}")

        if not due_tasks:
            return {
                "task_id": task_id,
                "status": "success",
                "tasks_processed": 0,
                "tasks_failed": 0,
                "message": "No due tasks found",
                "timestamp": datetime.utcnow().isoformat(),
            }

        processed_tasks = 0
        failed_tasks = 0
        results = []

        for task in due_tasks:
            try:
                logger.info(f"🔍 BREAKPOINT 6: Processing AI task: {task.title} (ID: {task.id})")
                print(f"🔍 BREAKPOINT 6: Processing AI task: {task.title} (ID: {task.id})")

                # Mark task as processing
                await task_manager.update_task_status(
                    task_id=int(task.id),
                    status="processing",
                    last_run_at=datetime.utcnow(),
                )

                # Execute the task
                print("🔍 BREAKPOINT 7: About to call TaskExecutor.execute_task")
                execution_result = await task_executor.execute_task(task)
                print(f"🔍 BREAKPOINT 8: TaskExecutor.execute_task completed, result: {execution_result}")

                # Mark task as completed
                await task_manager.update_task_status(
                    task_id=int(task.id),
                    status="completed",
                    last_run_at=datetime.utcnow(),
                )

                # Send notification if configured
                if task.should_notify():
                    print(f"🔍 BREAKPOINT 9: About to send SMS notification")
                    await notification_service.send_task_completion_notification(
                        task, execution_result
                    )
                    print(f"🔍 BREAKPOINT 10: SMS notification sent")
                else:
                    print(f"🔍 BREAKPOINT 9: Task should_notify() returned False, skipping SMS")

                processed_tasks += 1
                results.append(
                    {
                        "success": True,
                        "message": "Task executed successfully",
                        "task_id": task.id,
                        "task_title": task.title,
                        "task_type": task.task_type,
                        "execution_time": datetime.utcnow().isoformat(),
                        "ai_response": execution_result.get(
                            "ai_response", "No response"
                        ),
                    }
                )

                logger.info(f"Successfully processed AI task: {task.title}")

            except Exception as e:
                logger.error(f"Failed to process AI task {task.id}: {e}")
                failed_tasks += 1

                # Mark task as failed
                await task_manager.update_task_status(
                    task_id=int(task.id),
                    status="failed",
                    last_run_at=datetime.utcnow(),
                )

                results.append(
                    {
                        "success": False,
                        "message": f"Task execution failed: {str(e)}",
                        "task_id": task.id,
                        "task_title": task.title,
                        "task_type": task.task_type,
                        "execution_time": datetime.utcnow().isoformat(),
                        "error": str(e),
                    }
                )

        return {
            "task_id": task_id,
            "status": "success",
            "tasks_processed": processed_tasks,
            "tasks_failed": failed_tasks,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in AI task processing: {e}")
        return {
            "task_id": task_id,
            "status": "error",
            "message": f"AI task processing failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def create_ai_reminder(
    self,
    user_id: int,
    title: str,
    remind_at: str,
    description: Optional[str] = None,
    notification_channels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new AI reminder task.

    Args:
        user_id: User ID
        title: Reminder title
        remind_at: When to send the reminder (ISO format)
        description: Reminder description
        notification_channels: List of notification channels

    Returns:
        Dictionary with creation result
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
        result = loop.run_until_complete(
            _create_ai_reminder_async(
                user_id, title, remind_at, description, notification_channels
            )
        )
        result["task_id"] = task_id
        return result

    except Exception as e:
        logger.error(f"Error creating AI reminder: {e}")
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _create_ai_reminder_async(
    user_id: int,
    title: str,
    remind_at: str,
    description: Optional[str] = None,
    notification_channels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Async implementation of AI reminder creation."""
    task_manager = AITaskManager()

    try:
        # Parse remind_at datetime
        remind_datetime = datetime.fromisoformat(remind_at)

        # Create the reminder task
        task = await task_manager.create_reminder(
            user_id=user_id,
            title=title,
            remind_at=remind_datetime,
            description=description,
            notification_channels=notification_channels or ["sms"],
        )

        logger.info(f"Created AI reminder: {task.title} (ID: {task.id})")

        return {
            "status": "success",
            "task_id": task.id,
            "title": task.title,
            "remind_at": task.next_run_at.isoformat() if task.next_run_at else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error creating AI reminder: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def create_periodic_ai_task(
    self,
    user_id: int,
    title: str,
    schedule_type: str,
    schedule_config: Dict[str, Any],
    description: Optional[str] = None,
    ai_context: Optional[str] = None,
    notification_channels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new periodic AI task.

    Args:
        user_id: User ID
        title: Task title
        schedule_type: Type of schedule (daily, weekly, monthly, custom)
        schedule_config: Schedule configuration dictionary
        description: Task description
        ai_context: AI context for task execution
        notification_channels: List of notification channels

    Returns:
        Dictionary with creation result
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
        result = loop.run_until_complete(
            _create_periodic_ai_task_async(
                user_id,
                title,
                schedule_type,
                schedule_config,
                description,
                ai_context,
                notification_channels,
            )
        )
        result["task_id"] = task_id
        return result

    except Exception as e:
        logger.error(f"Error creating periodic AI task: {e}")
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _create_periodic_ai_task_async(
    user_id: int,
    title: str,
    schedule_type: str,
    schedule_config: Dict[str, Any],
    description: Optional[str] = None,
    ai_context: Optional[str] = None,
    notification_channels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Async implementation of periodic AI task creation."""
    task_manager = AITaskManager()

    try:
        # Create the periodic task
        task = await task_manager.create_periodic_task(
            user_id=user_id,
            title=title,
            schedule_type=schedule_type,
            schedule_config=schedule_config,
            description=description,
            ai_context=ai_context,
            notification_channels=notification_channels or ["sms"],
        )

        logger.info(f"Created periodic AI task: {task.title} (ID: {task.id})")

        return {
            "status": "success",
            "task_id": task.id,
            "title": task.title,
            "schedule_type": schedule_type,
            "next_run_at": task.next_run_at.isoformat() if task.next_run_at else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error creating periodic AI task: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def test_scheduler_connection(self) -> Dict[str, Any]:
    """
    Test task to verify scheduler connectivity and basic functionality.

    Returns:
        Dict containing test results
    """
    task_id = self.request.id
    current_time = datetime.utcnow()
    
    logger.info(f"🧪 CELERY BEAT TEST: test_scheduler_connection triggered at {current_time}")
    logger.info(f"📋 Test Task ID: {task_id}")
    print(f"🧪 CELERY BEAT TEST: test_scheduler_connection triggered at {current_time}")
    print(f"📋 Test Task ID: {task_id}")

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
            "task_id": task_id,
            "status": "error",
            "message": f"Scheduler connection test failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _test_scheduler_connection_async() -> Dict[str, Any]:
    """Async implementation of connection testing."""
    # Test database connection by trying to get due tasks
    task_manager = AITaskManager()
    
    try:
        # Test database connectivity by querying for due tasks
        due_tasks = await task_manager.get_due_tasks(limit=1)
        test_result = {
            "status": "success",
            "message": "Database connection test successful",
            "due_tasks_count": len(due_tasks),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        test_result = {
            "status": "error",
            "message": f"Database connection test failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
        }

    return {
        "task_id": None,  # Will be set by caller
        "status": "success",
        "test_result": test_result,
        "message": "Scheduler connection test successful",
        "timestamp": datetime.utcnow().isoformat(),
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
    cleaned_count = await task_manager.cleanup_old_logs(cleanup_date)  # type: ignore

    return {
        "task_id": None,  # Will be set by caller
        "status": "success",
        "cleaned_logs": cleaned_count,
        "message": f"Cleaned up {cleaned_count} old logs",
        "timestamp": datetime.utcnow().isoformat(),
    }
