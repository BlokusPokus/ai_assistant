"""
Internal helper functions for reminder management.

This module contains the internal implementation details and helper functions
used by the ReminderTool class. It separates the core logic from the tool interface.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ReminderInternal:
    """Internal helper class for reminder operations."""

    @staticmethod
    def parse_time_string(time_str) -> Optional[datetime]:
        """Parse various time string formats into datetime object."""
        if not time_str:
            return None

        # Convert to string if it's not already
        if not isinstance(time_str, str):
            time_str = str(time_str)

        if not time_str.strip():
            return None

        time_str = time_str.strip().lower()
        now = datetime.now()

        try:
            # Try ISO format first
            if "t" in time_str or "-" in time_str:
                return datetime.fromisoformat(time_str)
        except ValueError:
            pass

        try:
            # Handle relative times
            if time_str.startswith("in "):
                # Parse "in X minutes/hours/days"
                parts = time_str[3:].split()
                if len(parts) >= 2:
                    amount = int(parts[0])
                    unit = parts[1]

                    if unit.startswith("minute"):
                        return now + timedelta(minutes=amount)
                    elif unit.startswith("hour"):
                        return now + timedelta(hours=amount)
                    elif unit.startswith("day"):
                        return now + timedelta(days=amount)
                    elif unit.startswith("week"):
                        return now + timedelta(weeks=amount)

            # Handle "tomorrow at X"
            if time_str.startswith("tomorrow"):
                tomorrow = now + timedelta(days=1)
                if " at " in time_str:
                    time_part = time_str.split(" at ")[1]
                    hour, minute = ReminderInternal._parse_time_part(time_part)
                    if hour is not None:
                        return tomorrow.replace(
                            hour=hour, minute=minute or 0, second=0, microsecond=0
                        )
                else:
                    return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)

            # Handle "today at X"
            if time_str.startswith("today"):
                if " at " in time_str:
                    time_part = time_str.split(" at ")[1]
                    hour, minute = ReminderInternal._parse_time_part(time_part)
                    if hour is not None:
                        result = now.replace(
                            hour=hour, minute=minute or 0, second=0, microsecond=0
                        )
                        # If time has passed today, schedule for tomorrow
                        if result <= now:
                            result += timedelta(days=1)
                        return result

            # Handle simple time formats like "7:00", "7:00 AM", "19:00"
            hour, minute = ReminderInternal._parse_time_part(time_str)
            if hour is not None:
                result = now.replace(
                    hour=hour, minute=minute or 0, second=0, microsecond=0
                )
                # If time has passed today, schedule for tomorrow
                if result <= now:
                    result += timedelta(days=1)
                return result

        except (ValueError, IndexError):
            pass

        return None

    @staticmethod
    def _parse_time_part(time_part: str) -> tuple[Optional[int], Optional[int]]:
        """Parse time part like '7:00 AM' or '19:00' into hour and minute."""
        try:
            time_part = time_part.strip()

            # Handle AM/PM format
            is_pm = "pm" in time_part
            is_am = "am" in time_part

            if is_pm or is_am:
                time_part = time_part.replace("am", "").replace("pm", "").strip()

            if ":" in time_part:
                hour_str, minute_str = time_part.split(":")
                hour = int(hour_str)
                minute = int(minute_str)

                # Convert to 24-hour format
                if is_pm and hour != 12:
                    hour += 12
                elif is_am and hour == 12:
                    hour = 0

                return hour, minute
            else:
                # Just hour
                hour = int(time_part)
                if is_pm and hour != 12:
                    hour += 12
                elif is_am and hour == 12:
                    hour = 0
                return hour, 0

        except (ValueError, IndexError):
            return None, None

    @staticmethod
    def create_schedule_config(schedule_type: str, remind_at: datetime) -> Dict[str, Any]:
        """Create schedule configuration based on schedule type and time."""
        if schedule_type == "once":
            return {"run_at": remind_at}
        elif schedule_type == "daily":
            return {
                "hour": remind_at.hour,
                "minute": remind_at.minute
            }
        elif schedule_type == "weekly":
            return {
                "weekdays": [remind_at.weekday()],
                "hour": remind_at.hour,
                "minute": remind_at.minute
            }
        elif schedule_type == "monthly":
            return {
                "day": remind_at.day,
                "hour": remind_at.hour,
                "minute": remind_at.minute
            }
        elif schedule_type == "custom":
            return {
                "interval_minutes": 60,  # Default to hourly
                "run_at": remind_at
            }
        else:
            return {"run_at": remind_at}

    @staticmethod
    def format_reminder_list_header(status: str, count: int) -> str:
        """Format reminder list header."""
        return f"📋 {status.title()} reminders ({count} found):\n\n"

    @staticmethod
    def format_reminder_item(task) -> str:
        """Format individual reminder item for display."""
        status_emoji = ReminderInternal._get_status_emoji(task.status)
        next_run = ReminderInternal._format_next_run_time(task.next_run_at)

        result = f"{status_emoji} **{task.title}** (ID: {task.id})\n"
        result += f"   📅 Next run: {next_run}\n"
        result += f"   📝 Status: {task.status}\n"

        if task.description and task.description != task.title:
            result += f"   📄 Description: {task.description}\n"

        result += "\n"
        return result

    @staticmethod
    def _get_status_emoji(status: str) -> str:
        """Get appropriate emoji for reminder status."""
        emoji_map = {"active": "⏰", "completed": "✅", "failed": "❌", "paused": "⏸️"}
        return emoji_map.get(status, "📝")

    @staticmethod
    def _format_next_run_time(next_run_at) -> str:
        """Format next run time for display."""
        if next_run_at:
            return str(next_run_at.strftime("%Y-%m-%d %H:%M"))
        return "No schedule"

    @staticmethod
    def validate_reminder_id(reminder_id) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Validate reminder ID parameter.
        
        Returns:
            Tuple of (is_valid, parsed_id, error_message)
        """
        if not reminder_id:
            return False, None, "❌ Error: 'reminder_id' parameter is required for deleting reminders"
        
        try:
            parsed_id = int(reminder_id)
            return True, parsed_id, None
        except (ValueError, TypeError):
            return False, None, f"❌ Error: reminder_id must be a valid integer, got '{reminder_id}'"

    @staticmethod
    def validate_status(status: str) -> tuple[bool, Optional[str]]:
        """
        Validate status parameter.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_statuses = ["active", "completed", "failed", "paused"]
        if status and status not in valid_statuses:
            return False, f"❌ Error: Invalid status '{status}'. Valid statuses are: {', '.join(valid_statuses)}"
        return True, None

    @staticmethod
    def validate_reminder_inputs(text: str, time: str) -> tuple[bool, Optional[str]]:
        """
        Validate basic reminder input parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "❌ Error: 'text' parameter is required for creating reminders"
        if not time:
            return False, "❌ Error: 'time' parameter is required for creating reminders"
        return True, None

    @staticmethod
    def check_reminder_ownership(task_id: int, user_tasks: list) -> bool:
        """
        Check if a reminder belongs to the user.
        
        Args:
            task_id: ID of the task to check
            user_tasks: List of user's tasks
            
        Returns:
            True if user owns the task, False otherwise
        """
        return any(task.id == task_id for task in user_tasks)

    @staticmethod
    def build_update_data(**kwargs) -> Dict[str, Any]:
        """
        Build update data dictionary from kwargs.
        
        Args:
            **kwargs: Update parameters
            
        Returns:
            Dictionary with update data
        """
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
        return update_data

    @staticmethod
    def format_task_creation_response(task_type: str, text: str, task_id: int, schedule_type: str) -> str:
        """
        Format task creation response message.
        
        Args:
            task_type: Type of task created
            text: Task text
            task_id: Created task ID
            schedule_type: Schedule type
            
        Returns:
            Formatted response message
        """
        return f"✅ {task_type.replace('_', ' ').title()} created: '{text}' (ID: {task_id}) - {schedule_type} schedule"

    @staticmethod
    def format_deletion_response(task_id: int, success: bool) -> str:
        """
        Format deletion response message.
        
        Args:
            task_id: ID of the task
            success: Whether deletion was successful
            
        Returns:
            Formatted response message
        """
        if success:
            return f"✅ Reminder {task_id} deleted successfully"
        else:
            return f"❌ Failed to delete reminder {task_id}"
