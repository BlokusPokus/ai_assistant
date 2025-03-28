"""
Collection of tools available to the agent.
"""
from .base import Tool, ToolRegistry
from .emails.email_tool import EmailTool

# Export all implemented tools
__all__ = [
    'Tool',
    'ToolRegistry',

    'EmailTool'
]
