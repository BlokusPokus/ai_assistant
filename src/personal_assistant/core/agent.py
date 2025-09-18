"""
Main AgentCore class that orchestrates memory, tools, LLM, and AgentRunner functionality.
"""

import asyncio
import os
import time

from personal_assistant.prompts.enhanced_prompt_builder import EnhancedPromptBuilder

from ..config.logging_config import get_logger
from ..config.settings import settings
from ..llm.gemini import GeminiLLM
from ..llm.planner import LLMPlanner
from ..memory.ltm_optimization import (
    DynamicContextManager,
    EnhancedLTMConfig,
    EnhancedMemoryLifecycleManager,
    LTMLearningManager,
    SmartLTMRetriever,
)
from ..memory.storage_integration import StorageIntegrationManager
from ..tools import ToolRegistry
from .error_handler import AgentErrorHandler
from .logging_utils import log_agent_operation
from .services import ContextService, ConversationService, BackgroundService, ContextInjectionService, ToolExecutionService, AgentLoopService

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
        self.llm = llm or GeminiLLM(api_key=api_key, model=settings.GEMINI_MODEL)

        enhanced_prompt_builder = EnhancedPromptBuilder(self.tools)

        self.planner = LLMPlanner(
            self.llm, self.tools, prompt_builder=enhanced_prompt_builder
        )

        # Initialize LTM components with graceful fallback
        self._initialize_ltm_components(llm)

        # Initialize storage integration manager
        self.storage_manager = StorageIntegrationManager()
        logger.info("Storage integration manager initialized successfully")

        # Initialize services
        self._initialize_services()

        # Initialize error handler
        self.error_handler = AgentErrorHandler(logger)
        logger.info("Error handler initialized successfully")

    def _initialize_services(self):
        """Initialize all service components."""
        # Initialize context service
        self.context_service = ContextService(
            ltm_retriever=self.ltm_retriever,
            context_manager=self.context_manager
        )
        
        # Initialize conversation service
        self.conversation_service = ConversationService(self.storage_manager)
        
        # Initialize background service
        self.background_service = BackgroundService(
            storage_manager=self.storage_manager,
            ltm_learning_manager=self.ltm_learning_manager,
            lifecycle_manager=self.lifecycle_manager
        )
        
        # Initialize runner services (merged from AgentRunner)
        self.context_injection_service = ContextInjectionService()
        self.tool_execution_service = ToolExecutionService(self.tools)
        self.agent_loop_service = AgentLoopService(self.planner, self.tool_execution_service)
        
        # Current state for agent loop execution
        self.current_state = None
        
        logger.info("All services initialized successfully")

    async def run(self, user_input: str, user_id: int) -> str:
        """
        Process user input and generate a response using the agent system.

        Args:
            user_input: The user's message
            user_id: Unique identifier for the user (integer)

        Returns:
            str: Agent's response

        Raises:
            ConversationError: If conversation management fails
            AgentExecutionError: If agent execution fails
            AgentMemoryError: If memory operations fail
        """
        start_time = time.time()
        log_agent_operation(
            logger, user_id, "agent_run_start", {"input_length": len(user_input)}
        )

        try:
            # 1. Get conversation context and agent state
            conversation_id, agent_state = await self.conversation_service.get_conversation_context(
                user_id, user_input
            )

            # 2. Get enhanced context (LTM + RAG)
            context_data = await self.context_service.get_enhanced_context(
                user_id, user_input, agent_state
            )

            # 3. Set context for agent execution
            await self._set_context(
                agent_state, 
                context_data["rag_context"], 
                context_data["ltm_context"]
            )

            # 4. Execute agent loop
            response, updated_state = await self._execute_agent_loop(user_input, user_id)

            # This is very low performance and blocks followup messages, we need to rethink how to save memories
            # 5. Start background processing (non-blocking)
            # asyncio.create_task(self.background_service.process_async(
            #     user_id, user_input, response, updated_state, conversation_id, start_time
            # ))

            return response

        except Exception as e:
            error_response = await self.error_handler.handle_error(
                e, user_id, start_time
            )
            return error_response

    async def _set_context(
        self,
        agent_state,
        rag_context=None,
        ltm_context=None,
    ):
        """
        Inject LTM and RAG context into AgentState's memory_context with limits.

        Args:
            agent_state: The active state object
            rag_context: List of semantic documents from RAG
            ltm_context: Long-term memory context string
        """
        # Store the current state for use in _execute_agent_loop()
        self.current_state = agent_state
        
        # Delegate to context injection service
        await self.context_injection_service.inject_context(
            agent_state, rag_context, ltm_context
        )

    async def _execute_agent_loop(self, user_input: str, user_id: int):
        """
        Execute the main agent loop processing user input with optimized context.

        Args:
            user_input: String containing the user's message or query
            user_id: User identifier for tool execution

        Returns:
            Tuple[str, AgentState]: Final response to user and the final AgentState
        """
        # Use the state that was set up by _set_context()
        state = self.current_state
        if state is None:
            raise ValueError("No current state available. Call _set_context() first.")

        # Delegate to agent loop service with user_id
        return await self.agent_loop_service.execute_loop(state, user_input, user_id)

    def _initialize_ltm_components(self, llm):
        """Initialize LTM components with graceful fallback."""
        try:
            self.ltm_config = EnhancedLTMConfig()
            self.ltm_learning_manager = LTMLearningManager(config=self.ltm_config, llm=llm)
            self.ltm_retriever = SmartLTMRetriever(config=self.ltm_config)
            self.context_manager = DynamicContextManager(config=self.ltm_config)
            self.lifecycle_manager = EnhancedMemoryLifecycleManager(config=self.ltm_config)
            logger.info("Enhanced LTM optimization components initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize enhanced LTM optimization: {e}")
            # Set all LTM components to None for graceful degradation
            self.ltm_learning_manager = None
            self.ltm_retriever = None
            self.context_manager = None
            self.lifecycle_manager = None

