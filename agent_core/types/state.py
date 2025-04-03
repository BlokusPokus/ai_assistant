"""
LangGraph state definitions and related types.

📁 types/state.py
Defines the LangGraph agent state, including memory, tool calls, loop counters, etc.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Any

from agent_core.types.messages import ToolCall


@dataclass
class AgentState:
    user_input: str
    memory_context: List[dict] = field(default_factory=list)
    history: List[Tuple[Any, Any]] = field(default_factory=list)
    step_count: int = 0
    focus: List[str] = field(default_factory=list)
    conversation_history: list = field(default_factory=list)
    last_tool_result: Any = None

    def add_tool_result(self, tool_call: ToolCall, result: Any):
        """Record tool execution and result in conversation history"""
        self.step_count += 1
        self.last_tool_result = result

        # Add tool execution to conversation history
        self.conversation_history.extend([
            {
                "role": "assistant",
                "content": f"I'll help you with that using the {tool_call.name} tool."
            },
            {
                "role": "tool",
                "name": tool_call.name,
                "content": str(result)
            }
        ])

    def get_context_window(self, max_items: int = 5):
        """Gets recent history for context window."""
        return self.history[-max_items:]

    @classmethod
    def from_summary(cls, summary: str) -> "AgentState":
        """
        Create an AgentState from a fallback summary.

        Args:
            summary (str): Summary of previous conversation

        Returns:
            AgentState: Reconstructed state with summary context
        """
        return cls(
            user_input="",  # will be overwritten by the new input
            memory_context=[{"role": "system", "content": summary}],
            history=[],
            step_count=0,
            focus=[],
            conversation_history=[]
        )
