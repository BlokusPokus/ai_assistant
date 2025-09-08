"""
Reminder Tool for AI-driven task management.

This tool provides functionality for creating, managing, and scheduling
AI tasks and reminders that can be executed by the AI assistant.
"""

import logging
from typing import Any, Dict, Optional

from ..ai_scheduler.core.task_manager import AITaskManager
from ..base import Tool
from .reminder_internal import ReminderInternal

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
        """Create a new reminder or periodic task."""
        text = kwargs.get("text")
        time = kwargs.get("time")
        channel = kwargs.get("channel", "sms")
        task_type = kwargs.get("task_type", "reminder")
        schedule_type = kwargs.get("schedule_type", "once")
        user_id = kwargs.get("user_id", 126)

        # Validate inputs
        is_valid, error_msg = ReminderInternal.validate_reminder_inputs(text, time)
        if not is_valid:
            return error_msg

        try:
            # For one-time reminders, use the existing validation function
            if schedule_type == "once" and task_type == "reminder":
                result = await self.task_manager.create_reminder_with_validation(
                    text=text, time=time, channel=channel, user_id=user_id
                )
                return result.get("message", "Reminder created successfully")  # type: ignore
            
            # For periodic tasks, create directly using create_task
            else:
                # Parse time for periodic tasks
                remind_at = ReminderInternal.parse_time_string(time)
                if remind_at is None:
                    return f"❌ Error: Invalid time format '{time}'. Please use ISO format (YYYY-MM-DDTHH:MM:SS) or relative time (e.g., 'in 1 hour', 'tomorrow at 9am')"
                
                # Create schedule config based on schedule_type
                schedule_config = ReminderInternal.create_schedule_config(schedule_type, remind_at)
                
                # Calculate next run time
                next_run_at = await self.task_manager.calculate_next_run(schedule_type, schedule_config)
                
                # Create the task
                task = await self.task_manager.create_task(
                    user_id=user_id,
                    title=text,
                    description=text,
                    task_type=task_type,
                    schedule_type=schedule_type,
                    schedule_config=schedule_config,
                    next_run_at=next_run_at,
                    notification_channels=[channel],
                )
                
                return ReminderInternal.format_task_creation_response(task_type, text, task.id, schedule_type)
                
        except Exception as e:
            return f"Error creating reminder: {str(e)}"

    async def list_reminders(self, **kwargs) -> str:
        """List user reminders."""
        status = kwargs.get("status", "active")
        user_id = kwargs.get("user_id", 126)

        try:
            # Validate status
            is_valid, error_msg = ReminderInternal.validate_status(status)
            if not is_valid:
                return error_msg

            # Get user's reminder tasks directly
            tasks = await self.task_manager.get_user_tasks(
                user_id=user_id, status=status, task_type="reminder", limit=50
            )

            if not tasks:
                return f"No {status} reminders found."

            # Format the response
            result = ReminderInternal.format_reminder_list_header(status or "all", len(tasks))
            for task in tasks:
                result += ReminderInternal.format_reminder_item(task)

            return result
        except Exception as e:
            return f"Error listing reminders: {str(e)}"

    async def delete_reminder(self, **kwargs) -> str:
        """Delete a reminder."""
        reminder_id = kwargs.get("reminder_id")
        user_id = kwargs.get("user_id", 126)

        # Validate reminder_id
        is_valid, parsed_id, error_msg = ReminderInternal.validate_reminder_id(reminder_id)
        if not is_valid:
            return error_msg

        try:
            # Check if the reminder exists and belongs to the user
            user_tasks = await self.task_manager.get_user_tasks(
                user_id=user_id, task_type="reminder", limit=100
            )

            if not ReminderInternal.check_reminder_ownership(parsed_id, user_tasks):
                return f"❌ Reminder {parsed_id} not found or you don't have permission to delete it"

            # Delete the task directly
            success = await self.task_manager.delete_task(parsed_id, user_id)
            return ReminderInternal.format_deletion_response(parsed_id, success)

        except Exception as e:
            return f"❌ Error deleting reminder: {str(e)}"

    async def update_reminder(self, **kwargs) -> str:
        """Update a reminder."""
        reminder_id = kwargs.get("reminder_id")
        user_id = kwargs.get("user_id", 126)

        # Validate reminder_id
        is_valid, parsed_id, error_msg = ReminderInternal.validate_reminder_id(reminder_id)
        if not is_valid:
            return error_msg

        # Extract update fields
        update_data = ReminderInternal.build_update_data(**kwargs)

        if not update_data:
            return "Error: No update fields provided. Available fields: text, time, channel, task_type, schedule_type"

        try:
            result = await self.task_manager.update_task(
                parsed_id, user_id, update_data
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
