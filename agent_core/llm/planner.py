"""
LLM-based planning and tool selection logic.

📁 llm/planner.py
LLM planner step. Decides whether to respond, call a tool, or reflect.
"""

from agent_core.llm.llm_client import LLMClient
from agent_core.tools.base import ToolRegistry
from ..types.messages import ToolCall, FinalAnswer
from typing import Union, Any
from agent_core.types.state import AgentState
from agent_core.llm.prompt_builder import PromptBuilder
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LLMPlanner:
    """
    Manages the decision-making process for agent actions using LLM.
    Coordinates between LLM responses and tool execution.
    """

    # ------------------------
    # Initialization
    # ------------------------
    def __init__(self, llm_client: LLMClient, tool_registry: 'ToolRegistry'):
        """
        Initialize the LLM-based planner.

        Args:
            llm_client (LLMClient): Client for LLM interactions
            tool_registry (ToolRegistry): Registry of available tools
        """
        logger.info("Initializing LLMPlanner")
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.prompt_builder = PromptBuilder(tool_registry)
        # Set up bidirectional relationship
        self.tool_registry.set_planner(self)
        logger.debug("LLMPlanner initialized successfully")

    # ------------------------
    # Core Planning Logic
    # ------------------------
    def choose_action(self, state: 'AgentState') -> Union[ToolCall, FinalAnswer]:
        """
        Choose next action based on current agent state.

        Args:
            state (AgentState): Current state of the agent including conversation history

        Returns:
            Union[ToolCall, FinalAnswer]: Either a tool call action or final response
        """
        logger.info("Starting action selection process")

        # Build prompt
        logger.debug("Building prompt from state")
        prompt = self.prompt_builder.build(state)
        logger.debug(f"Built prompt of length: {len(prompt)}")

        # Get available tools schema
        logger.debug("Fetching tool schema")
        functions = self.tool_registry.get_schema()
        logger.debug(f"Available tools: {list(functions.keys())}")

        # Get LLM response
        logger.info("Requesting completion from LLM")
        response = self.llm_client.complete(prompt, functions)
        logger.debug(f"Received LLM response: {response}")

        # Parse into action
        logger.debug("Parsing LLM response into action")
        action = self.llm_client.parse_response(response)

        # Log the chosen action for debugging
        if isinstance(action, ToolCall):
            logger.info(f"Selected action: ToolCall - {action.name}")
            logger.debug(f"ToolCall arguments: {action.args}")
        else:
            logger.info("Selected action: FinalAnswer")
            logger.debug(f"FinalAnswer content: {action.output}")

        return action

    # ------------------------
    # Fallback Handling
    # ------------------------
    def force_finish(self, state: 'AgentState') -> str:
        """
        Forces the agent to finish after hitting loop limit.

        Args:
            state (AgentState): Current state of the agent

        Returns:
            str: Final response message
        """
        logger.warning("Forcing conversation to finish due to loop limit")

        prompt = self.prompt_builder.build({
            **state,
            "force_finish": True
        })
        logger.debug("Generated force finish prompt")

        response = self.llm_client.complete(prompt, [])
        logger.debug(f"Received force finish response: {response}")

        final_message = f"I need to wrap up now. {self.llm_client.parse_response(response).output}"
        logger.info(f"Force finish message: {final_message}")
        return final_message

    # ------------------------
    # Tool Callbacks
    # ------------------------
    def on_tool_completion(self, tool_name: str, result: Any):
        """
        Called by ToolRegistry after tool execution.

        Args:
            tool_name (str): Name of the completed tool
            result (Any): Result returned by the tool
        """
        logger.debug(f"Tool completion callback: {tool_name}")
        logger.debug(f"Tool result: {result}")
        pass  # Can be used to update internal state or trigger additional actions
