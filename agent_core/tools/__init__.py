"""
Collection of tools available to the agent.
"""
from .base import Tool, ToolRegistry
from .emails.email_tool import EmailTool
from .calendar.calendar_tool import CalendarTool


def create_tool_registry() -> ToolRegistry:
    """Creates and configures a ToolRegistry with all available tools."""
    registry = ToolRegistry()

    # Register email tools
    email_tool = EmailTool()
    for tool in email_tool:
        tool.set_category("Email")
        registry.register(tool)

    # Register calendar tools
    calendar_tool = CalendarTool()
    for tool in calendar_tool:
        tool.set_category("Calendar")
        registry.register(tool)

    return registry


# Export all implemented tools
__all__ = [
    'Tool',
    'ToolRegistry',
    'CalendarTool',
    'EmailTool',
    'create_tool_registry'
]
