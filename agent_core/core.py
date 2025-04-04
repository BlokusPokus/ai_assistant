"""
Main AgentCore class that orchestrates memory, tools, LLM, and AgentRunner functionality.
Handles the full lifecycle of processing user input and generating responses.

📁 agent_core/core.py
Main AgentCore interface. Combines AgentRunner, memory, tools, and LLM. 
Provides the .run(user_input) method.
"""

from agent_core.agent_runner import AgentRunner
from agent_core.tools.base import ToolRegistry
from agent_core.llm.llm_client import LLMClient
from agent_core.llm.planner import LLMPlanner
from agent_core.types.state import AgentState
from memory.conversation_manager import get_conversation_id, should_resume_conversation
from memory.memory_storage import save_state, load_state, load_latest_summary, get_conversation_timestamp
from memory.memory_storage import query_ltm
from rag.retriever import query_knowledge_base
import logging

logger = logging.getLogger(__name__)


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
        self.runner = AgentRunner(tools, self.planner)

    async def run(self, user_input: str, user_id: str) -> str:
        """
        Process user input and generate a response using the agent system.

        Flow:
        1. Context Resolution
           - Get conversation ID
           - Check conversation recency
           - Load appropriate state/summary
        2. Knowledge Gathering
           - Fetch long-term memory
           - Get relevant RAG context
        3. Response Generation
           - Set context for runner
           - Generate response
        4. State Management
           - Save updated state

        Args:
            user_input: The user's message
            user_id: Unique identifier for the user

        Returns:
            str: Agent's response
        """
        try:
            # Step 1: Resolve conversation context
            # Generate unique conversation ID from user+message
            conversation_id = get_conversation_id(user_id, user_input)

            # Get last activity timestamp (async database operation)
            last_timestamp = await get_conversation_timestamp(conversation_id)

            # Determine if we should resume existing conversation or start new
            if should_resume_conversation(last_timestamp):
                # Load existing conversation state
                agent_state = await load_state(conversation_id)
            else:
                # Start new conversation with context from latest summary
                summary = await load_latest_summary(user_id)
                agent_state = AgentState.from_summary(summary)

            # Step 2: Gather knowledge context
            # Query long-term memory based on current focus
            ltm_context = await query_ltm(user_id, tags=agent_state.focus)

            # Get relevant knowledge base entries
            rag_context = await query_knowledge_base(user_id, user_input)

            # Step 3: Set up context for response generation
            self.runner.set_context(agent_state, ltm_context, rag_context)

            # Generate response using the agent runner
            response = await self.runner.run(user_input)

            # Step 4: Persist updated state
            await save_state(conversation_id, agent_state)

            return response

        except Exception as e:
            # Log error and return user-friendly message
            logger.error(f"Error in AgentCore.run: {str(e)}")
            return f"An error occurred: {str(e)}"
