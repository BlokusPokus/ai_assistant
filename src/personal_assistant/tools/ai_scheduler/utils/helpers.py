"""
Helper functions for AI scheduler operations.

This module provides convenience functions for common AI scheduler operations
like setting reminders, listing reminders, and deleting reminders.
"""

from ..core.task_manager import AITaskManager


async def set_reminder(
    text: str, time: str, channel: str = "sms", user_id: int = 126
) -> str:
    """Set a new reminder with validation and formatting."""
    task_manager = AITaskManager()
    result = await task_manager.create_reminder_with_validation(
        text, time, channel, user_id
    )
    return result["message"]  # type: ignore


async def list_reminders(status: str = "active", user_id: int = 126) -> str:
    """List user reminders with formatting."""
    task_manager = AITaskManager()
    
    # Get user tasks filtered by status and task_type
    tasks = await task_manager.get_user_tasks(
        user_id=user_id, 
        status=status, 
        task_type="reminder", 
        limit=50
    )
    
    if not tasks:
        return f"No {status} reminders found."
    
    # Format the response
    result = task_manager._format_reminder_list_header(status or "all", len(tasks))
    for task in tasks:
        result += task_manager._format_reminder_item(task)
    
    return result


async def delete_reminder(reminder_id: int, user_id: int = 126) -> str:
    """Delete a user reminder with validation."""
    task_manager = AITaskManager()
    
    # First check if the reminder exists and belongs to the user
    user_tasks = await task_manager.get_user_tasks(
        user_id=user_id, 
        task_type="reminder", 
        limit=100
    )
    
    # Check if reminder exists
    reminder_exists = any(task.id == reminder_id for task in user_tasks)
    if not reminder_exists:
        return f"❌ Reminder {reminder_id} not found or you don't have permission to delete it"
    
    # Delete the task
    success = await task_manager.delete_task(reminder_id, user_id)
    
    if success:
        return f"✅ Reminder {reminder_id} deleted successfully"
    else:
        return f"❌ Failed to delete reminder {reminder_id}"
