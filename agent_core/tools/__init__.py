"""
Collection of tools available to the agent.
"""
from .base import Tool, ToolRegistry
from .emails.email_tool import EmailTool
from .calendar.calendar_tool import CalendarTool
# Export all implemented tools
__all__ = [
    'Tool',
    'ToolRegistry',
    'CalendarTool',
    'EmailTool'
]
