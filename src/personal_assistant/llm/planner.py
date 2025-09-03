"""
LLM-based planning and tool selection logic.

📁 llm/planner.py
LLM planner step. Decides whether to respond, call a tool, or reflect.
"""

from typing import Any, Union

from ..config.logging_config import get_logger

# from ..prompts.prompt_builder import PromptBuilder  # No longer needed - using custom prompt builders
from ..tools.base import ToolRegistry
from ..types.messages import FinalAnswer, ToolCall
from ..types.state import AgentState
from ..utils.text_cleaner import clean_text_for_logging
from .llm_client import LLMClient

# Configure module logger
logger = get_logger("llm")


class LLMPlanner:
    """
    Manages the decision-making process for agent actions using LLM.
    Coordinates between LLM responses and tool execution.
    """

    # ------------------------
    # Initialization
    # ------------------------
    def __init__(
        self, llm_client: LLMClient, tool_registry: "ToolRegistry", prompt_builder=None
    ):
        """
        Initialize the LLM-based planner.

        Args:
            llm_client (LLMClient): Client for LLM interactions
            tool_registry (ToolRegistry): Registry of available tools
            prompt_builder: Custom prompt builder (optional, defaults to PromptBuilder)
        """
        logger.info("Initializing LLMPlanner")
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        # Always use EnhancedPromptBuilder - auto-create if none provided
        if prompt_builder:
            self.prompt_builder = prompt_builder
            logger.info("✅ Using provided EnhancedPromptBuilder")
        else:
            # Auto-create EnhancedPromptBuilder for everyone
            from ..prompts.enhanced_prompt_builder import EnhancedPromptBuilder

            self.prompt_builder = EnhancedPromptBuilder(tool_registry)
            logger.info("✅ Auto-created EnhancedPromptBuilder with metadata")

        # Set up bidirectional relationship
        self.tool_registry.set_planner(self)
        logger.debug("LLMPlanner initialized successfully")

    # ------------------------
    # Core Planning Logic
    # ------------------------
    def choose_action(self, state: "AgentState") -> Union[ToolCall, FinalAnswer]:
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
        logger.info(f"Using prompt builder: {type(self.prompt_builder).__name__}")

        # Show exactly which class we're calling
        logger.info(f"Prompt builder class: {self.prompt_builder.__class__.__name__}")
        logger.info(
            f"Prompt builder module: {self.prompt_builder.__class__.__module__}"
        )

        prompt = self.prompt_builder.build(state)
        logger.debug(f"Built prompt of length: {len(prompt)}")

        # Log if this is an enhanced prompt
        if "ENHANCED TOOL GUIDANCE" in prompt:
            logger.info("✅ Enhanced prompt with metadata was built!")
            logger.info(
                f"Metadata section found: {prompt.count('ENHANCED TOOL GUIDANCE')} times"
            )
        else:
            logger.info("⚠️ Basic prompt without metadata was built")
            logger.warning(
                "Expected enhanced prompt but got basic one - check metadata system"
            )

        # Get available tools schema
        logger.debug("Fetching tool schema")
        functions = self.tool_registry.get_schema()
        logger.debug(f"Available tools: {list(functions.keys())}")

        # Get LLM response
        logger.info("=== REQUESTING COMPLETION FROM LLM ===")
        response = self.llm_client.complete(prompt, functions)

        # Clean response before logging
        clean_response = clean_text_for_logging(str(response))
        logger.debug(f"=== RECEIVED LLM RESPONSE: {clean_response} ===")

        # Parse into action
        logger.debug("=== PARSING LLM RESPONSE INTO ACTION ===")
        action = self.llm_client.parse_response(response)
        logger.debug(f"=== PARSED ACTION: {type(action).__name__} ===")

        # Log the chosen action for debugging
        if isinstance(action, ToolCall):
            logger.info(f"Selected action: ToolCall - {action.name}")
            logger.debug(f"ToolCall arguments: {action.args}")
        else:
            logger.info("Selected action: FinalAnswer")
            # Clean content before logging
            clean_output = clean_text_for_logging(action.output)
            logger.debug(f"FinalAnswer content: {clean_output}")

        return action

    # ------------------------
    # Fallback Handling
    # ------------------------
    def force_finish(self, state: "AgentState") -> str:
        """
        Forces the agent to finish after hitting loop limit.

        Args:
            state (AgentState): Current state of the agent

        Returns:
            str: Final response message
        """
        logger.warning("Forcing conversation to finish due to loop limit")

        # Pass the AgentState object directly to the prompt builder
        prompt = self.prompt_builder.build(state)
        logger.debug("Generated force finish prompt")

        response = self.llm_client.complete(prompt, [])

        # Clean response before logging
        clean_response = clean_text_for_logging(str(response))
        logger.debug(f"Received force finish response: {clean_response}")

        final_message = (
            f"I need to wrap up now. {self.llm_client.parse_response(response).output}"
        )
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

        # Clean result before logging
        clean_result = clean_text_for_logging(str(result))
        logger.debug(f"Tool result: {clean_result}")
        pass  # Can be used to update internal state or trigger additional actions
