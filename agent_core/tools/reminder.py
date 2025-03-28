"""
Reminder tool implementation.
"""
from .base import Tool
from typing import Optional


def set_reminder(text: str, time: str, channel: Optional[str] = "sms") -> str:
    """Set a new reminder"""
    # TODO: Implement reminder scheduling
    return f"Set reminder '{text}' for {time} via {channel}"


def list_reminders(status: Optional[str] = "pending") -> str:
    """List active reminders"""
    # TODO: Implement reminder retrieval
    return f"Listing {status} reminders"


ReminderSetTool = Tool(
    name="set_reminder",
    func=set_reminder,
    description="Set a new reminder",
    parameters={
        "text": {
            "type": "string",
            "description": "Reminder text"
        },
        "time": {
            "type": "string",
            "description": "When to send the reminder (ISO format or natural language)"
        },
        "channel": {
            "type": "string",
            "description": "Optional notification channel (sms/email)",
            "optional": True
        }
    }
)

ReminderListTool = Tool(
    name="list_reminders",
    func=list_reminders,
    description="List active reminders",
    parameters={
        "status": {
            "type": "string",
            "description": "Optional status filter (pending/completed)",
            "optional": True
        }
    }
)
