"""
LangGraph state definitions and related types.

📁 types/state.py
Defines the LangGraph agent state, including memory, tool calls, loop counters, etc.
"""


class AgentState:
    def __init__(self, user_input):
        self.user_input = user_input
        self.memory_context = []
        self.history = []
