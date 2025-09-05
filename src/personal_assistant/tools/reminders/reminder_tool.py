"""
Reminder Tool for AI-driven task management.

This tool provides functionality for creating, managing, and scheduling
AI tasks and reminders that can be executed by the AI assistant.
"""

import logging

from ..ai_scheduler.ai_task_manager import AITaskManager
from ..base import Tool

logger = logging.getLogger(__name__)


class ReminderTool:
    """Container for reminder management tools."""

    def __init__(self):
        self.task_manager = AITaskManager()

        # Create individual tools
        self.create_reminder_tool = Tool(
            name="create_reminder",
            func=self.create_reminder,
            description="Create a new AI-driven reminder or task",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Reminder text or task description",
                    },
                    "time": {
                        "type": "string",
                        "description": "When to execute the reminder in ISO format (YYYY-MM-DDTHH:MM:SS) or relative time (e.g., 'in 1 hour', 'tomorrow at 9am')",
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["sms", "email", "push"],
                        "description": "Notification channel for the reminder (default: sms)",
                    },
                    "task_type": {
                        "type": "string",
                        "enum": ["reminder", "automated_task", "periodic_task"],
                        "description": "Type of task to create (default: reminder)",
                    },
                    "schedule_type": {
                        "type": "string",
                        "enum": ["once", "daily", "weekly", "monthly", "custom"],
                        "description": "How often the task should repeat (default: once)",
                    },
                },
                "required": ["text", "time"],
            },
        )

        self.list_reminders_tool = Tool(
            name="list_reminders",
            func=self.list_reminders,
            description="List user reminders and tasks",
            parameters={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "completed", "cancelled", "all"],
                        "description": "Status filter for listing reminders (default: active)",
                    }
                },
            },
        )

        self.delete_reminder_tool = Tool(
            name="delete_reminder",
            func=self.delete_reminder,
            description="Delete a reminder or task",
            parameters={
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "integer",
                        "description": "ID of the reminder to delete",
                    }
                },
                "required": ["reminder_id"],
            },
        )

        self.update_reminder_tool = Tool(
            name="update_reminder",
            func=self.update_reminder,
            description="Update an existing reminder or task",
            parameters={
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "integer",
                        "description": "ID of the reminder to update",
                    },
                    "text": {"type": "string", "description": "New reminder text"},
                    "time": {"type": "string", "description": "New execution time"},
                    "channel": {
                        "type": "string",
                        "enum": ["sms", "email", "push"],
                        "description": "New notification channel",
                    },
                    "task_type": {
                        "type": "string",
                        "enum": ["reminder", "automated_task", "periodic_task"],
                        "description": "New task type",
                    },
                    "schedule_type": {
                        "type": "string",
                        "enum": ["once", "daily", "weekly", "monthly", "custom"],
                        "description": "New schedule type",
                    },
                },
                "required": ["reminder_id"],
            },
        )

    async def create_reminder(self, **kwargs) -> str:
        """Create a new reminder."""
        text = kwargs.get("text")
        time = kwargs.get("time")
        channel = kwargs.get("channel", "sms")
        kwargs.get("task_type", "reminder")
        kwargs.get("schedule_type", "once")
        user_id = kwargs.get("user_id", 126)

        if not text:
            return "Error: 'text' parameter is required for creating reminders"
        if not time:
            return "Error: 'time' parameter is required for creating reminders"

        try:
            result = await self.task_manager.create_reminder_with_validation(
                text=text, time=time, channel=channel, user_id=user_id
            )
            return result.get("message", "Reminder created successfully")  # type: ignore
        except Exception as e:
            return f"Error creating reminder: {str(e)}"

    async def list_reminders(self, **kwargs) -> str:
        """List user reminders."""
        status = kwargs.get("status", "active")
        user_id = kwargs.get("user_id", 126)

        try:
            result = await self.task_manager.list_user_reminders(status, user_id)
            return result.get("message", "No reminders found")  # type: ignore
        except Exception as e:
            return f"Error listing reminders: {str(e)}"

    async def delete_reminder(self, **kwargs) -> str:
        """Delete a reminder."""
        reminder_id = kwargs.get("reminder_id")
        user_id = kwargs.get("user_id", 126)

        if not reminder_id:
            return "Error: 'reminder_id' parameter is required for deleting reminders"

        try:
            result = await self.task_manager.delete_user_reminder(reminder_id, user_id)
            return result.get("message", "Reminder deleted successfully")  # type: ignore
        except Exception as e:
            return f"Error deleting reminder: {str(e)}"

    async def update_reminder(self, **kwargs) -> str:
        """Update a reminder."""
        reminder_id = kwargs.get("reminder_id")
        user_id = kwargs.get("user_id", 126)

        if not reminder_id:
            return "Error: 'reminder_id' parameter is required for updating reminders"

        # Extract update fields
        update_data = {}
        if "text" in kwargs:
            update_data["title"] = kwargs["text"]
        if "time" in kwargs:
            update_data["next_run_at"] = kwargs["time"]
        if "channel" in kwargs:
            update_data["notification_channels"] = [kwargs["channel"]]
        if "task_type" in kwargs:
            update_data["task_type"] = kwargs["task_type"]
        if "schedule_type" in kwargs:
            update_data["schedule_type"] = kwargs["schedule_type"]

        if not update_data:
            return "Error: No update fields provided. Available fields: text, time, channel, task_type, schedule_type"

        try:
            result = await self.task_manager.update_task(
                reminder_id, user_id, update_data
            )
            return result.get("message", "Reminder updated successfully")  # type: ignore
        except Exception as e:
            return f"Error updating reminder: {str(e)}"

    def __iter__(self):
        """Iterate over available reminder tools."""
        yield self.create_reminder_tool
        yield self.list_reminders_tool
        yield self.delete_reminder_tool
        yield self.update_reminder_tool
