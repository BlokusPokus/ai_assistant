"""
Prompt construction utilities.

📁 llm/prompt_builder.py
Builds agent prompts from memory, recent actions, tools, and user input. 
Injects into Gemini calls.
"""

from agent_core.tools.base import ToolRegistry
from agent_core.types.state import AgentState


class PromptBuilder:
    """
    Constructs prompts for LLM interactions by combining system context,
    tool descriptions, memory, conversation history, and user input.
    """

    def __init__(self, tool_registry: 'ToolRegistry'):
        """
        Initialize the prompt builder with a tool registry.

        Input:
            tool_registry: Registry containing all available tools and their metadata

        Output:
            None

        Description:
            Sets up the prompt builder with access to the tool registry for later use
            in constructing prompts that include tool descriptions and capabilities.
        """
        self.tool_registry = tool_registry

    def build(self, state: 'AgentState') -> str:
        """
        Builds a complete prompt for the LLM by combining multiple components.

        Input:
            state: AgentState object containing:
                - user_input: Current user message
                - memory_context: List of relevant memory items
                - history: List of previous actions and their results

        Output:
            str: A formatted prompt string containing:
                1. System context and instructions
                2. Available tools and their descriptions
                3. Relevant memory context
                4. Conversation history
                5. Current user input
                6. Final instruction for decision making

        Description:
            Constructs a comprehensive prompt by:
            1. Adding system context about the AI's role
            2. Including available tools and their parameters
            3. Adding relevant memory items for context
            4. Including previous actions and their results
            5. Adding the current user input
            6. Finishing with decision-making instruction

            The resulting prompt helps the LLM understand the context
            and make informed decisions about whether to use tools
            or respond directly.
        """
        # Build system context
        prompt = [
            "You are an AI assistant that helps users by either responding directly or using tools.",
            "Always try to use tools when available and appropriate.",
            "\nAvailable tools and their descriptions:",
        ]

        # Add tool descriptions
        tool_schema = self.tool_registry.get_schema()
        if not tool_schema:
            prompt.append("No tools are currently available.")
        else:
            for name, info in tool_schema.items():
                desc = info.get('description', 'No description available')
                params = info.get('parameters', {}).get('properties', {})
                param_desc = [f"  - {p}: {details.get('description', 'No description')}"
                              for p, details in params.items()]

                prompt.append(f"- {name}: {desc}")
                if param_desc:
                    prompt.extend(param_desc)

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
