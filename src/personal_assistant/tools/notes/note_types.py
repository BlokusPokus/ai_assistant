"""
Note Types Enum

Defines the supported note types for classification and enhancement.
"""

from enum import Enum


class NoteType(Enum):
    """Supported note types for classification"""
    MEETING = "meeting"
    PROJECT = "project"
    PERSONAL = "personal"
    RESEARCH = "research"
    LEARNING = "learning"
    TASK = "task"
    IDEA = "idea"
    JOURNAL = "journal"
    UNKNOWN = "unknown"
