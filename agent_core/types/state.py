"""
LangGraph state definitions and related types.

📁 types/state.py
Defines the LangGraph agent state, including memory, tool calls, loop counters, etc.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Any


@dataclass
class AgentState:
    user_input: str
    memory_context: List[dict] = field(default_factory=list)
    history: List[Tuple[Any, Any]] = field(default_factory=list)
    step_count: int = 0

    def add_tool_result(self, tool_call, result):
        """Adds a tool execution result to history."""
        self.history.append((tool_call, result))
        self.step_count += 1

    def get_context_window(self, max_items: int = 5):
        """Gets recent history for context window."""
        return self.history[-max_items:]
