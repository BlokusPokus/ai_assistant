"""
Pydantic models for log entries.

📁 logs/models.py
Pydantic models for structured log entries (e.g. ToolCallLog, MemoryQueryLog, etc.).
"""

from pydantic import BaseModel
from typing import Optional


class LogEntry(BaseModel):
    user_input: str
    memory_used: Optional[list]
    tool_called: Optional[str]
    tool_output: Optional[str]
    agent_response: str
    timestamp: str
