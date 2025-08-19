"""
State optimization module for intelligent memory management.

This module provides classes and utilities for optimizing conversation state
before saving to prevent memory explosion and improve performance.
"""

from .optimization_manager import StateOptimizationManager
from .conversation_compressor import ConversationCompressor
from .context_manager import ContextManager
from .error_analyzer import ErrorPatternAnalyzer

__all__ = [
    "StateOptimizationManager",
    "ConversationCompressor",
    "ContextManager",
    "ErrorPatternAnalyzer"
]
