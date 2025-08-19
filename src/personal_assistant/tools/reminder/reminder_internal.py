"""
Internal functions for Reminder Tool.

This module contains internal utility functions and helper methods
that are used by the main ReminderTool class.
"""

import logging
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)


def validate_reminder_text(text: str) -> tuple[bool, str]:
    """Validate reminder text input"""
    if not text or not text.strip():
        return False, "❌ Error: Reminder text cannot be empty"
    return True, ""


def validate_reminder_time(time: str) -> tuple[bool, str]:
    """Validate reminder time input"""
    if not time or not time.strip():
        return False, "❌ Error: Time cannot be empty"
    return True, ""


def validate_user_id(user_id) -> tuple[bool, int, str]:
    """Validate and convert user_id to integer"""
    if not isinstance(user_id, int):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return False, 0, f"❌ Error: user_id must be a valid integer, got '{user_id}'"
    return True, user_id, ""


def validate_notification_channel(channel: Optional[str]) -> tuple[bool, str, str]:
    """Validate notification channel parameter"""
    valid_channels = ['sms', 'email', 'in_app']
    if channel and channel not in valid_channels:
        return False, "sms", f"❌ Error: Invalid channel '{channel}'. Valid channels are: {', '.join(valid_channels)}"

    # Return default channel if none specified
    default_channel = channel if channel else "sms"
    return True, default_channel, ""


def validate_reminder_status(status: Optional[str]) -> tuple[bool, str, str]:
    """Validate reminder status parameter"""
    valid_statuses = ['active', 'completed', 'failed', 'paused']
    if status and status not in valid_statuses:
        return False, "active", f"❌ Error: Invalid status '{status}'. Valid statuses are: {', '.join(valid_statuses)}"

    # Return default status if none specified
    default_status = status if status else "active"
    return True, default_status, ""


def validate_reminder_id(reminder_id) -> tuple[bool, int, str]:
    """Validate and convert reminder_id to integer"""
    if not isinstance(reminder_id, int):
        try:
            reminder_id = int(reminder_id)
        except (ValueError, TypeError):
            return False, 0, f"❌ Error: reminder_id must be a valid integer, got '{reminder_id}'"
    return True, reminder_id, ""


def parse_reminder_time(time: str) -> tuple[bool, Optional[datetime], str]:
    """Parse reminder time string to datetime object"""
    try:
        remind_at = datetime.fromisoformat(time)
        return True, remind_at, ""
    except ValueError:
        # If not ISO format, try to parse natural language
        # TODO: Implement natural language time parsing
        return False, None, f"Error: Invalid time format '{time}'. Please use ISO format (YYYY-MM-DDTHH:MM:SS)"


def format_reminder_response(text: str, remind_at: datetime, task_id: int) -> str:
    """Format successful reminder creation response"""
    return f"✅ Reminder set: '{text}' for {remind_at.strftime('%Y-%m-%d %H:%M')} (ID: {task_id})"


def format_reminder_list_header(status: str, count: int) -> str:
    """Format reminder list header"""
    return f"📋 {status.title()} reminders ({count} found):\n\n"


def format_reminder_item(task) -> str:
    """Format individual reminder item for display"""
    status_emoji = get_status_emoji(task.status)
    next_run = format_next_run_time(task.next_run_at)

    result = f"{status_emoji} **{task.title}** (ID: {task.id})\n"
    result += f"   📅 Next run: {next_run}\n"
    result += f"   📝 Status: {task.status}\n"

    if task.description and task.description != task.title:
        result += f"   📄 Description: {task.description}\n"

    result += "\n"
    return result


def get_status_emoji(status: str) -> str:
    """Get appropriate emoji for reminder status"""
    emoji_map = {
        "active": "⏰",
        "completed": "✅",
        "failed": "❌",
        "paused": "⏸️"
    }
    return emoji_map.get(status, "📝")


def format_next_run_time(next_run_at) -> str:
    """Format next run time for display"""
    if next_run_at:
        return next_run_at.strftime('%Y-%m-%d %H:%M')
    return "No schedule"


def format_no_reminders_found(status: str) -> str:
    """Format message when no reminders are found"""
    return f"No {status} reminders found."


def format_reminder_deleted_success(reminder_id: int) -> str:
    """Format successful reminder deletion message"""
    return f"✅ Reminder {reminder_id} deleted successfully"


def format_reminder_deleted_failure(reminder_id: int) -> str:
    """Format failed reminder deletion message"""
    return f"❌ Failed to delete reminder {reminder_id}"


def format_reminder_not_found(reminder_id: int) -> str:
    """Format reminder not found message"""
    return f"❌ Reminder {reminder_id} not found or you don't have permission to delete it"


def check_reminder_exists(reminder_id: int, user_tasks: List) -> bool:
    """Check if a reminder exists in user's task list"""
    return any(task.id == reminder_id for task in user_tasks)


def build_notification_channels(channel: str) -> List[str]:
    """Build notification channels list for task creation"""
    return [channel] if channel else ['sms']
