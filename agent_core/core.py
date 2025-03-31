"""
Main AgentCore class that orchestrates memory, tools, LLM, and LangGraph functionality.

📁 agent_core/core.py
Main AgentCore interface. Combines LangGraph runner, memory, tools, and LLM. 
Provides the .run(user_input) method.
"""

from agent_core.graph_runner import LangGraphRunner
from agent_core.tools.base import ToolRegistry
from agent_core.llm.llm_client import LLMClient
from agent_core.llm.planner import LLMPlanner


class AgentCore:
    def __init__(self, tools: 'ToolRegistry', llm: 'LLMClient'):
        """
        Initialize the core agent components.

        Input:
            tools: Registry of available tools
            llm: LLM client for interactions

        Output:
            None

        Description:
            Sets up the core agent by:
            1. Creating planner with LLM client
            2. Creating runner with tools and planner
        """
        # First create the planner with the LLM client
        self.planner = LLMPlanner(llm, tools)
        # Then create runner with planner (not LLM directly)
        self.runner = LangGraphRunner(tools, self.planner)

    async def run(self, user_input: str) -> str:
        """
        Main entry point for processing user input.

        Input:
            user_input: String containing user's message

        Output:
            str: Final response from the agent or error message

        Description:
            1. Passes user input to LangGraphRunner
            2. Handles any exceptions during processing
            3. Returns final response or error message
        """
        try:
            response = await self.runner.run(user_input)
            return response
        except Exception as e:
            return f"An error occurred: {str(e)}"
