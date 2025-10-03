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
from .todo_metadata import (
    create_todo_ai_enhancements,
    create_todo_tool_metadata,
    todo_ai_enhancements,
    todo_metadata,
)
from .grocery_deals_metadata import (
    create_grocery_deals_ai_enhancements,
    create_grocery_deals_tool_metadata,
    grocery_deals_ai_enhancements,
    grocery_deals_metadata,
)
from .final_answer_metadata import (
    create_final_answer_metadata,
    get_final_answer_metadata,
    FINAL_ANSWER_METADATA,
)

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
    "create_todo_tool_metadata",
    "create_todo_ai_enhancements",
    "todo_metadata",
    "todo_ai_enhancements",
    "create_grocery_deals_tool_metadata",
    "create_grocery_deals_ai_enhancements",
    "grocery_deals_metadata",
    "grocery_deals_ai_enhancements",
    "create_final_answer_metadata",
    "get_final_answer_metadata",
    "FINAL_ANSWER_METADATA",
]
