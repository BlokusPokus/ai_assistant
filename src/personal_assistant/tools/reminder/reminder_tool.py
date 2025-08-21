"""
Reminder Tool for setting and managing reminders using the AI task system.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any

from ..base import Tool
from personal_assistant.tools.ai_scheduler.ai_task_manager import AITaskManager
from .reminder_internal import (
    validate_reminder_text,
    validate_reminder_time,
    validate_user_id,
    validate_notification_channel,
    validate_reminder_status,
    validate_reminder_id,
    parse_reminder_time,
    format_reminder_response,
    format_reminder_list_header,
    format_reminder_item,
    format_no_reminders_found,
    format_reminder_deleted_success,
    format_reminder_deleted_failure,
    format_reminder_not_found,
    check_reminder_exists,
    build_notification_channels
)

logger = logging.getLogger(__name__)


class ReminderTool:
    """
    Comprehensive reminder tool that provides:
    - Setting new reminders with various notification channels
    - Listing and managing existing reminders
    - Deleting reminders by ID
    - Status-based reminder filtering
    """

    def __init__(self):
        # Initialize any shared resources, tokens, clients, etc.
        self._task_manager = None

        # Create individual tools
        self.set_reminder_tool = Tool(
            name="set_reminder",
            func=self.set_reminder,
            description="Set a new reminder for a specific time",
            parameters={
                "text": {
                    "type": "string",
                    "description": "Reminder text (required)"
                },
                "time": {
                    "type": "string",
                    "description": "Time in ISO format (YYYY-MM-DDTHH:MM:SS) (required)"
                },
                "channel": {
                    "type": "string",
                    "description": "Notification channel: sms, email, in_app (default: sms)"
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID (default: 4)"
                }
            }
        )

        self.list_reminders_tool = Tool(
            name="list_reminders",
            func=self.list_reminders,
            description="List active reminders for the user",
            parameters={
                "status": {
                    "type": "string",
                    "description": "Status filter: active, completed, failed, paused (default: active)"
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID (default: 4)"
                }
            }
        )

        self.delete_reminder_tool = Tool(
            name="delete_reminder",
            func=self.delete_reminder,
            description="Delete a reminder by ID",
            parameters={
                "reminder_id": {
                    "type": "integer",
                    "description": "Reminder ID to delete (required)"
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID (default: 4)"
                }
            }
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([
            self.set_reminder_tool,
            self.list_reminders_tool,
            self.delete_reminder_tool
        ])

    def _get_task_manager(self):
        """Get or create AI task manager instance"""
        if self._task_manager is None:
            self._task_manager = AITaskManager()
        return self._task_manager

    async def set_reminder(self, text: str, time: str, channel: Optional[str] = "sms", user_id: int = 126) -> str:
        """Set a new reminder using the AI task system"""
        try:
            # Validate input parameters using internal functions
            is_valid, error_msg = validate_reminder_text(text)
            if not is_valid:
                return error_msg

            is_valid, error_msg = validate_reminder_time(time)
            if not is_valid:
                return error_msg

            is_valid, user_id, error_msg = validate_user_id(user_id)
            if not is_valid:
                return error_msg

            is_valid, channel, error_msg = validate_notification_channel(
                channel)
            if not is_valid:
                return error_msg

            # Parse time using internal function
            is_valid, remind_at, error_msg = parse_reminder_time(time)
            if not is_valid:
                return error_msg

            task_manager = self._get_task_manager()

            # Create the reminder task
            task = await task_manager.create_reminder(
                user_id=user_id,
                title=text,
                remind_at=remind_at,
                description=text,
                notification_channels=build_notification_channels(channel)
            )

            return format_reminder_response(text, remind_at, task.id)

        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return f"❌ Error setting reminder: {str(e)}"

    async def list_reminders(self, status: Optional[str] = "active", user_id: int = 126) -> str:
        """List active reminders using the AI task system"""
        try:
            # Validate input parameters using internal functions
            is_valid, status, error_msg = validate_reminder_status(status)
            if not is_valid:
                return error_msg

            is_valid, user_id, error_msg = validate_user_id(user_id)
            if not is_valid:
                return error_msg

            task_manager = self._get_task_manager()

            # Get user's reminder tasks
            tasks = await task_manager.get_user_tasks(
                user_id=user_id,
                status=status,
                task_type='reminder',
                limit=50
            )

            if not tasks:
                return format_no_reminders_found(status)

            # Format the response using internal functions
            result = format_reminder_list_header(status, len(tasks))

            for task in tasks:
                result += format_reminder_item(task)

            return result

        except Exception as e:
            logger.error(f"Error listing reminders: {e}")
            return f"❌ Error listing reminders: {str(e)}"

    async def delete_reminder(self, reminder_id: int, user_id: int = 126) -> str:
        """Delete a reminder by ID"""
        try:
            # Validate input parameters using internal functions
            is_valid, reminder_id, error_msg = validate_reminder_id(
                reminder_id)
            if not is_valid:
                return error_msg

            is_valid, user_id, error_msg = validate_user_id(user_id)
            if not is_valid:
                return error_msg

            task_manager = self._get_task_manager()

            # First check if the reminder exists and belongs to the user
            user_tasks = await task_manager.get_user_tasks(
                user_id=user_id,
                task_type='reminder',
                limit=100
            )

            if not check_reminder_exists(reminder_id, user_tasks):
                return format_reminder_not_found(reminder_id)

            # Delete the task - use positional arguments as expected by the method
            success = await task_manager.delete_task(reminder_id, user_id)

            if success:
                return format_reminder_deleted_success(reminder_id)
            else:
                return format_reminder_deleted_failure(reminder_id)

        except Exception as e:
            logger.error(f"Error deleting reminder: {e}")
            return f"❌ Error deleting reminder: {str(e)}"
