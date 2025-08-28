"""
Tool Metadata Module

This module provides enhanced metadata for tools to improve AI understanding
and tool selection capabilities.
"""

from .tool_metadata import ToolMetadata, ToolMetadataManager
from .ai_enhancements import AIEnhancement, AIEnhancementManager
from .email_metadata import (
    create_email_tool_metadata, 
    create_email_ai_enhancements,
    get_email_tool_metadata,
    get_email_tool_metadata_full
)

__version__ = '1.0.0'
__author__ = 'Personal Assistant Team'

__all__ = [
    'ToolMetadata',
    'ToolMetadataManager', 
    'AIEnhancement',
    'AIEnhancementManager',
    'create_email_tool_metadata',
    'create_email_ai_enhancements',
    'get_email_tool_metadata',
    'get_email_tool_metadata_full'
]
