"""
Main AgentCore class that orchestrates memory, tools, LLM, and AgentRunner functionality.
"""

import os
import time

from personal_assistant.prompts.enhanced_prompt_builder import EnhancedPromptBuilder

from ..config.logging_config import get_logger
from ..llm.gemini import GeminiLLM
from ..llm.planner import LLMPlanner
from ..memory.conversation_manager import (
    create_new_conversation,
    get_conversation_id,
    should_resume_conversation,
)
from ..memory.ltm_optimization import (
    DynamicContextManager,
    EnhancedLTMConfig,
    EnhancedMemoryLifecycleManager,
    LTMLearningManager,
    SmartLTMRetriever,
)
from ..memory.storage_integration import StorageIntegrationManager
from ..rag.retriever import query_knowledge_base
from ..tools import ToolRegistry
from ..tools.ltm.ltm_manager import get_ltm_context_with_tags
from ..types.state import AgentState
from .error_handler import AgentErrorHandler
from .exceptions import ConversationError, ValidationError
from .logging_utils import log_agent_operation, log_performance_metrics
from .runner import AgentRunner

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
        llm = llm or GeminiLLM(api_key=api_key, model="gemini-2.5-flash")
        self.llm = llm

        enhanced_prompt_builder = EnhancedPromptBuilder(self.tools)

        self.planner = LLMPlanner(
            self.llm, self.tools, prompt_builder=enhanced_prompt_builder
        )
        self.runner = AgentRunner(self.tools, self.planner)

        try:
            # Initialize enhanced LTM configuration
            self.ltm_config = EnhancedLTMConfig()

            # Initialize enhanced LTM components
            self.ltm_learning_manager = LTMLearningManager(
                config=self.ltm_config, llm=llm
            )
            self.ltm_retriever = SmartLTMRetriever(config=self.ltm_config)
            self.context_manager = DynamicContextManager(config=self.ltm_config)
            self.lifecycle_manager = EnhancedMemoryLifecycleManager(
                config=self.ltm_config
            )

            logger.info("Enhanced LTM optimization components initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize enhanced LTM optimization: {e}")
            self.ltm_learning_manager = None
            self.ltm_retriever = None
            self.context_manager = None
            self.lifecycle_manager = None

        # Initialize storage integration manager for new normalized storage
        self.storage_manager = StorageIntegrationManager()
        logger.info("Storage integration manager initialized successfully")

        # Initialize error handler
        self.error_handler = AgentErrorHandler(logger)
        logger.info("Error handler initialized successfully")

    async def run(self, user_input: str, user_id: int) -> str:
        """
        Process user input and generate a response using the agent system.

        Args:
            user_input: The user's message
            user_id: Unique identifier for the user (integer)

        Returns:
            str: Agent's response

        Raises:
            ValidationError: If user_input or user_id is invalid
            ConversationError: If conversation management fails
            AgentExecutionError: If agent execution fails
            AgentMemoryError: If memory operations fail
        """
        # Input validation
        if not user_input or not user_input.strip():
            raise ValidationError(
                "User input cannot be empty", "user_input", user_input
            )

        if not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError(
                f"Invalid user_id: {user_id}. Must be a positive integer.",
                "user_id",
                str(user_id),
            )

        start_time = time.time()
        log_agent_operation(
            logger, user_id, "agent_run_start", {"input_length": len(user_input)}
        )

        try:
            conversation_id = await get_conversation_id(user_id)

            if conversation_id is None:
                conversation_id = await create_new_conversation(user_id)
                if conversation_id is None:
                    raise ConversationError(
                        f"Failed to create new conversation for user {user_id}", user_id
                    )
                agent_state = AgentState(user_input=user_input)

            else:
                last_timestamp = await self.storage_manager.get_conversation_timestamp(
                    user_id, conversation_id
                )

                resume_conversation = should_resume_conversation(last_timestamp)
                logger.info(f"Resume decision: {resume_conversation}")

                if resume_conversation:
                    logger.info("Resuming existing conversation")
                    agent_state = await self.storage_manager.load_state(
                        conversation_id, user_id
                    )
                    if agent_state is None:
                        logger.warning(
                            "Failed to load existing conversation state, creating new conversation"
                        )
                        conversation_id = await create_new_conversation(user_id)
                        if conversation_id is None:
                            raise ConversationError(
                                f"Failed to create new conversation for user {user_id}",
                                user_id,
                            )
                        agent_state = AgentState(user_input=user_input)
                    else:
                        agent_state.user_input = user_input
                else:
                    logger.info("Creating new conversation - previous one too old")
                    conversation_id = await create_new_conversation(user_id)
                    if conversation_id is None:
                        raise ConversationError(
                            f"Failed to create new conversation for user {user_id}",
                            user_id,
                        )

                    agent_state = AgentState(user_input=user_input)

            agent_state.reset_for_new_message(user_input)

            try:
                # Use enhanced LTM retriever with state coordination
                if self.ltm_retriever:
                    # Get relevant memories with state context
                    relevant_memories = await self.ltm_retriever.get_relevant_memories(
                        user_id=user_id,
                        context=user_input,
                        state_context=agent_state,
                        query_complexity="medium",  # Default complexity
                    )

                    # Use dynamic context manager to optimize context with state
                    if self.context_manager and relevant_memories:
                        ltm_context = (
                            await self.context_manager.optimize_context_with_state(
                                memories=relevant_memories,
                                user_input=user_input,
                                state_context=agent_state,
                                focus_areas=agent_state.focus
                                if hasattr(agent_state, "focus")
                                else None,
                                query_complexity="medium",
                            )
                        )
                    else:
                        # Fallback to simple context formatting
                        ltm_context = "\n".join(
                            [mem.get("content", "") for mem in relevant_memories[:5]]
                        )
                else:
                    # Fallback to legacy LTM context retrieval
                    ltm_context = await get_ltm_context_with_tags(
                        None,
                        logger,
                        user_id,
                        user_input,
                        list(agent_state.focus)
                        if hasattr(agent_state, "focus") and agent_state.focus
                        else None,
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to get enhanced LTM context for user {user_id}: {e}"
                )
                # Fallback to legacy method
                try:
                    ltm_context = await get_ltm_context_with_tags(
                        None,
                        logger,
                        user_id,
                        user_input,
                        list(agent_state.focus)
                        if hasattr(agent_state, "focus") and agent_state.focus
                        else None,
                    )
                except Exception as fallback_e:
                    logger.warning(
                        f"Fallback LTM context retrieval also failed: {fallback_e}"
                    )
                    ltm_context = None

            try:
                rag_context = await query_knowledge_base(user_id, user_input)
            except Exception as e:
                logger.warning(f"Failed to get RAG context for user {user_id}: {e}")
                rag_context = []

            await self.runner.set_context(agent_state, rag_context, ltm_context)

            response, updated_state = await self.runner.execute_agent_loop(user_input)
            response = str(response)  # Ensure response is a string

            try:
                await self.storage_manager.save_state(
                    conversation_id, updated_state, user_id
                )
            except Exception as e:
                logger.error(f"Failed to save state for user {user_id}: {e}")
                # Continue execution even if state saving fails

            if self.ltm_learning_manager:
                try:
                    # Perform comprehensive LTM optimization
                    await self.ltm_learning_manager.optimize_after_interaction(
                        user_id, user_input, response, updated_state
                    )

                    # Handle explicit memory requests if any
                    if self.ltm_learning_manager.is_memory_request(user_input):
                        await self.ltm_learning_manager.handle_explicit_memory_request(
                            user_id,
                            user_input,
                            response,
                            f"Conversation {conversation_id}",
                        )
                except Exception as e:
                    logger.warning(f"LTM optimization failed for user {user_id}: {e}")
                    # Continue execution even if LTM optimization fails

            # Perform memory lifecycle management with state coordination
            if self.lifecycle_manager:
                try:
                    # Run lifecycle management with state context
                    lifecycle_results = (
                        await self.lifecycle_manager.manage_memory_lifecycle_with_state(
                            user_id, updated_state
                        )
                    )
                    logger.info(
                        f"Memory lifecycle management completed for user {user_id}: {lifecycle_results}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Memory lifecycle management failed for user {user_id}: {e}"
                    )
                    # Continue execution even if lifecycle management fails

            try:
                await self.storage_manager.log_agent_interaction(
                    user_id=user_id,  # user_id is already an integer
                    user_input=updated_state.user_input,
                    agent_response=response,
                    tool_called=None,
                    tool_output=str(updated_state.last_tool_result)
                    if updated_state.last_tool_result
                    else None,
                    memory_used=None,
                )
            except Exception as e:
                logger.warning(
                    f"Failed to log agent interaction for user {user_id}: {e}"
                )
                # Continue execution even if logging fails

            # Log performance metrics
            duration = time.time() - start_time
            log_performance_metrics(
                logger,
                user_id,
                "agent_run_complete",
                duration,
                True,
                {"response_length": len(response) if response else 0},
            )

            return response

        except Exception as e:
            error_response = await self.error_handler.handle_error(
                e, user_id, start_time
            )
            return str(error_response)


# Make this file runnable as a script
if __name__ == "__main__":
    import asyncio

    async def main():
        """Main function to run the agent interactively."""
        print("🤖 Personal Assistant Agent - Interactive Mode")
        print("=" * 50)

        # Initialize the agent
        print("Initializing agent...")
        agent = AgentCore()
        print("✅ Agent initialized successfully!")
        print()

        # Get user ID (you can change this)
        user_id = 1

        print(f"Ready to chat! (User ID: {user_id})")
        print("Type 'quit', 'exit', or 'q' to stop")
        print("Type 'clear' to clear conversation history")
        print("-" * 50)

        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()

                # Check for exit commands
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                # Check for clear command
                if user_input.lower() == "clear":
                    print("🧹 Conversation cleared!")
                    continue

                # Skip empty input
                if not user_input:
                    continue

                # Process the message
                print("🤖 Assistant: ", end="", flush=True)
                response = await agent.run(user_input, user_id)
                print(response)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again...")

    # Run the interactive agent
    asyncio.run(main())
