"""
Main AgentCore class that orchestrates memory, tools, LLM, and AgentRunner functionality.
"""

from .runner import AgentRunner
from ..tools import ToolRegistry
from ..tools.ltm.ltm_manager import (
    get_ltm_context_with_tags,
)
from ..llm.gemini import GeminiLLM
from ..llm.planner import LLMPlanner
from ..types.state import AgentState
from ..memory.conversation_manager import get_conversation_id, create_new_conversation, should_resume_conversation
from ..memory.memory_storage import save_state, load_state, get_conversation_timestamp
from ..memory.memory_storage import log_agent_interaction
from ..rag.retriever import query_knowledge_base
from ..config.logging_config import get_logger

from ..memory.ltm_optimization import (
    LTMLearningManager,
)
import os


logger = get_logger("core")


class AgentCore:
    def __init__(self, tools=None, llm=None):
        """
        Initialize the core agent components.

        Args:
            tools: Registry of available tools (optional)
            llm: LLM client for interactions (optional)
        """
        self.tools = tools or ToolRegistry()

        api_key = os.getenv("GEMINI_API_KEY")
        llm = llm or GeminiLLM(api_key=api_key, model="gemini-2.0-flash")
        self.llm = llm
        self.planner = LLMPlanner(self.llm, self.tools)
        self.runner = AgentRunner(self.tools, self.planner)

        try:
            self.ltm_learning_manager = LTMLearningManager(
                config=None, llm=llm)
            logger.info("LTM optimization components initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize LTM optimization: {e}")
            self.ltm_learning_manager = None

    async def run(self, user_input: str, user_id: str) -> str:
        """
        Process user input and generate a response using the agent system.

        Args:
            user_input: The user's message
            user_id: Unique identifier for the user (string)

        Returns:
            str: Agent's response
        """

        try:
            # TODO: correct type of user_id
            user_id_str = str(user_id)

            conversation_id = await get_conversation_id(user_id_str)

            if conversation_id is None:
                conversation_id = await create_new_conversation(user_id_str)
                if conversation_id is None:
                    error_msg = f"Failed to create new conversation for user {user_id_str}"
                    logger.error(error_msg)
                    return f"An error occurred: {error_msg}"
                agent_state = AgentState(user_input=user_input)

            else:
                last_timestamp = await get_conversation_timestamp(user_id_str, conversation_id)

                # TODO: Seems like it always returns true
                resume_conversation = should_resume_conversation(
                    last_timestamp)
                logger.info(f"Resume decision: {resume_conversation}")

                if resume_conversation:
                    logger.info("Resuming existing conversation")
                    agent_state = await load_state(conversation_id)
                    agent_state.user_input = user_input
                else:
                    logger.info(
                        "Creating new conversation - previous one too old")
                    conversation_id = await create_new_conversation(user_id_str)
                    if conversation_id is None:
                        logger.error(
                            f"Failed to create new conversation for user {user_id_str}")
                        return f"An error occurred: Failed to create new conversation for user {user_id_str}"

                    agent_state = AgentState(user_input=user_input)

            agent_state.reset_for_new_message(user_input)

            ltm_context = await get_ltm_context_with_tags(
                None, logger, user_id_str, user_input,
                agent_state.focus if hasattr(agent_state, 'focus') else None
            )

            rag_context = await query_knowledge_base(user_id_str, user_input)

            self.runner.set_context(agent_state, rag_context, ltm_context)

            response, updated_state = await self.runner.execute_agent_loop(user_input)

            await save_state(conversation_id, updated_state, user_id_str)

            if self.ltm_learning_manager:
                # Perform comprehensive LTM optimization
                await self.ltm_learning_manager.optimize_after_interaction(
                    user_id_str, user_input, response, updated_state
                )

                # Handle explicit memory requests if any
                if self.ltm_learning_manager.is_memory_request(user_input):
                    await self.ltm_learning_manager.handle_explicit_memory_request(
                        user_id_str, user_input, response, f"Conversation {conversation_id}"
                    )

            await log_agent_interaction(
                user_id=int(user_id_str),
                user_input=updated_state.user_input,
                agent_response=response,
                tool_called=None,
                tool_output=str(
                    updated_state.last_tool_result) if updated_state.last_tool_result else None,
                memory_used=None
            )
            return response

        except Exception as e:
            logger.error(f"Error in AgentCore.run: {str(e)}")
            return f"An error occurred: {str(e)}"
