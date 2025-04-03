"""
Prompt construction utilities.

📁 llm/prompt_builder.py
Builds agent prompts from memory, recent actions, tools, and user input. 
Injects into Gemini calls.
"""

from agent_core.tools.base import ToolRegistry
from agent_core.types.state import AgentState
from typing import Dict, Any
from datetime import datetime


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

    def build(self, state: AgentState) -> str:
        """Build prompt from current state."""
        current_time = datetime.now()
        base_prompt = f"""
Current date and time: {current_time.strftime('%Y-%m-%d %H:%M')}

User request: {state.user_input}

Previous actions and results:
{self._format_history(state.conversation_history)}

Current status:
- Steps taken so far: {state.step_count}
- Last tool used: {state.last_tool_result if state.last_tool_result else 'None'}

Available tools:
{self._format_tools()}

Instructions:
1. Review what has been done so far
2. Evaluate if the user's request is fully addressed
3. If needed, use additional tools to complete the request
4. Only give a final answer when ALL necessary actions are complete
5. When giving a final answer, summarize all actions taken
6. When scheduling events:
   - Use the current date and time as reference
   - Schedule events in the near future unless specified otherwise
   - Default to business hours (9 AM - 5 PM) if no specific time given

How would you like to proceed? You can:
1. Use another tool if more actions are needed
2. Give a final answer if the request is fully addressed
3. Ask for clarification if needed

Remember: Before asking new questions, acknowledge previous actions and explain why additional information is needed.
"""
        return base_prompt

    def _format_history(self, history: list) -> str:
        """Format conversation history for prompt."""
        if not history:
            return "No previous actions"

        formatted = []
        for entry in history:
            if entry["role"] == "assistant":
                formatted.append(f"Assistant: {entry['content']}")
            elif entry["role"] == "tool":
                formatted.append(f"Tool ({entry['name']}): {entry['content']}")

        return "\n".join(formatted)

    def _format_tools(self) -> str:
        """Format available tools for prompt."""
        tool_schema = self.tool_registry.get_schema()
        if not tool_schema:
            return "No tools are currently available."
        else:
            tool_descriptions = [f"- {name}: {info.get('description', 'No description available')}"
                                 for name, info in tool_schema.items()]
            return "\n".join(tool_descriptions)
