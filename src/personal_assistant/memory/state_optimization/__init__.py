"""
State optimization module for intelligent memory management.

This module provides classes and utilities for optimizing conversation state
before saving to prevent memory explosion and improve performance.
"""

from .context_manager import ContextManager
from .conversation_compressor import ConversationCompressor
from .error_analyzer import ErrorPatternAnalyzer
from .optimization_manager import StateOptimizationManager

__all__ = [
    "StateOptimizationManager",
    "ConversationCompressor",
    "ContextManager",
    "ErrorPatternAnalyzer",
]
