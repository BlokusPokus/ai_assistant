"""
Main AgentCore class that orchestrates memory, tools, LLM, and AgentRunner functionality.

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
        user_id = "test_user_001"

        try:
            # Step 1: Resolve conversation context
            conversation_id = get_conversation_id(user_id, user_input)
            last_timestamp = get_conversation_timestamp(conversation_id)

            if should_resume_conversation(last_timestamp):
                agent_state = load_state(conversation_id)
            else:
                summary = load_latest_summary(user_id)
                agent_state = AgentState.from_summary(summary)

            # Optional: fetch long-term knowledge
            ltm_context = query_ltm(user_id, tags=agent_state.focus)

            # Optional: use RAG for related unstructured notes
            rag_context = query_knowledge_base(user_id, user_input)

            # Step 2: Inject context (STM + LTM + RAG)
            self.runner.set_context(agent_state, ltm_context, rag_context)

            # Step 3: Run agent as usual
            response = await self.runner.run(user_input)

            # Step 4: Save STM + maybe summary + maybe LTM entry
            save_state(conversation_id, agent_state)

            return response
        except Exception as e:
            return f"An error occurred: {str(e)}"
