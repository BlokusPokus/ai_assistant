"""
Enhanced Todo Tool Module.

This module provides comprehensive todo management with advanced features:
- Missed task counting and threshold detection
- Automatic task segmentation using LLM
- Behavioral analytics and insights
- ADHD-specific productivity features

Components:
- TodoTool: Main tool class with CRUD operations
- MissedCounterManager: Tracks missed tasks and triggers segmentation
- SegmentationEngine: Breaks down complex tasks using LLM
- BehavioralAnalytics: Analyzes patterns and generates insights
"""

from .todo_tool import TodoTool, create_todo_tools
from .missed_counter import MissedCounterManager
from .segmentation_engine import SegmentationEngine
from .behavioral_analytics import BehavioralAnalytics

__all__ = [
    "TodoTool",
    "create_todo_tools",
    "MissedCounterManager",
    "SegmentationEngine",
    "BehavioralAnalytics"
]
