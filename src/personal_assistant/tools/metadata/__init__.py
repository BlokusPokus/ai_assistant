"""
Tool Metadata Module

This module provides enhanced metadata for tools to improve AI understanding
and tool selection capabilities.
"""

from .ai_enhancements import AIEnhancement, AIEnhancementManager
from .ai_task_metadata import (
    create_ai_task_ai_enhancements,
    create_ai_task_metadata,
    get_ai_task_metadata,
    get_ai_task_metadata_full,
)
from .email_metadata import (
    create_email_ai_enhancements,
    create_email_tool_metadata,
    get_email_tool_metadata,
    get_email_tool_metadata_full,
)
from .tool_metadata import ToolMetadata, ToolMetadataManager

__version__ = "1.0.0"
__author__ = "Personal Assistant Team"

__all__ = [
    "ToolMetadata",
    "ToolMetadataManager",
    "AIEnhancement",
    "AIEnhancementManager",
    "create_ai_task_metadata",
    "create_ai_task_ai_enhancements",
    "get_ai_task_metadata",
    "get_ai_task_metadata_full",
    "create_email_tool_metadata",
    "create_email_ai_enhancements",
    "get_email_tool_metadata",
    "get_email_tool_metadata_full",
]
