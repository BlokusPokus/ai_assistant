"""
LLM-based planning and tool selection logic.

📁 llm/planner.py
LLM planner step. Decides whether to respond, call a tool, or reflect.
"""

from agent_core.llm.llm_client import LLMClient
from agent_core.llm.prompt_builder import PromptBuilder
from agent_core.tools.base import ToolRegistry
from ..types.messages import ToolCall, FinalAnswer
from typing import Union, Any
from agent_core.types.state import AgentState


class LLMPlanner:
    def __init__(self, llm_client: LLMClient, prompt_builder: PromptBuilder, tool_registry: 'ToolRegistry'):
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder
        self.tool_registry = tool_registry
        # Set up bidirectional relationship
        self.tool_registry.set_planner(self)

    def choose_action(self, state: 'AgentState') -> Union[ToolCall, FinalAnswer]:
        """
        Decides next action based on current state.
        """
        # Build prompt
        prompt = self.prompt_builder.build(state)

        # Get available tools schema
        functions = self.tool_registry.get_schema()

        # Get LLM response
        response = self.llm_client.complete(prompt, functions)

        # Parse into action
        return self.llm_client.parse_response(response)

    def force_finish(self, state: 'AgentState') -> str:
        """Forces the agent to finish after hitting loop limit."""
        prompt = self.prompt_builder.build({
            **state,
            "force_finish": True
        })
        response = self.llm_client.complete(prompt, [])
        return f"I need to wrap up now. {self.llm_client.parse_response(response).output}"

    def on_tool_completion(self, tool_name: str, result: Any):
        """Called by ToolRegistry after tool execution"""
        pass  # Can be used to update internal state or trigger additional actions
