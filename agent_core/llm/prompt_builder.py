"""
Prompt construction utilities.

📁 llm/prompt_builder.py
Builds agent prompts from memory, recent actions, tools, and user input. 
Injects into Gemini calls.
"""

from agent_core.tools.base import ToolRegistry
from agent_core.types.state import AgentState


class PromptBuilder:
    def __init__(self, tool_registry: 'ToolRegistry'):
        self.tool_registry = tool_registry

    def build(self, state: 'AgentState') -> str:
        """
        Builds the final prompt for the LLM.

        Args:
            state: Current agent state containing input, memory, and history

        Returns:
            str: LLM-ready prompt
        """
        # Build system context
        prompt = [
            "You are an AI assistant that helps users by either responding directly or using tools.",
            "\nAvailable tools and their descriptions:",
        ]

        # Add tool descriptions
        tool_schema = self.tool_registry.get_schema()
        for name, info in tool_schema.items():
            prompt.append(f"- {name}: {info['description']}")

        prompt.append("\nContext from memory:")
        # Add memory context
        for mem in state.memory_context:
            prompt.append(f"- {mem}")

        # Add conversation history
        if state.history:
            prompt.append("\nPrevious actions:")
            for action, result in state.history:
                prompt.append(f"Tool: {action.name}")
                prompt.append(f"Result: {result}")

        # Add current user input
        prompt.append(f"\nUser input: {state.user_input}")
        prompt.append("\nDecide whether to respond directly or use a tool.")

        return "\n".join(prompt)
