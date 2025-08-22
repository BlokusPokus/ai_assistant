"""
Simplified Reminder Tool that directly uses the enhanced AITaskManager.
This eliminates the redundant validation and formatting layer.
"""
import logging
from typing import Optional

from ..base import Tool
from personal_assistant.tools.ai_scheduler.ai_task_manager import AITaskManager

logger = logging.getLogger(__name__)


class ReminderTool:
    """
    Simplified reminder tool that directly uses the enhanced AITaskManager.
    All validation and formatting is now handled by AITaskManager.
    """

    def __init__(self):
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
                    "description": "User ID (default: 126)"
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
                    "description": "User ID (default: 126)"
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
                    "description": "User ID (default: 126)"
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
        """Set a new reminder using the enhanced AITaskManager"""
        task_manager = self._get_task_manager()
        result = await task_manager.create_reminder_with_validation(text, time, channel, user_id)
        return result['message']

    async def list_reminders(self, status: Optional[str] = "active", user_id: int = 126) -> str:
        """List user reminders using the enhanced AITaskManager"""
        task_manager = self._get_task_manager()
        result = await task_manager.list_user_reminders(status, user_id)
        return result['message']

    async def delete_reminder(self, reminder_id: int, user_id: int = 126) -> str:
        """Delete a user reminder using the enhanced AITaskManager"""
        task_manager = self._get_task_manager()
        result = await task_manager.delete_user_reminder(reminder_id, user_id)
        return result['message']
