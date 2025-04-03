"""
Agent runner logic for managing the conversation workflow.

📁 agent_core/graph_runner.py
Implements the main agent loop that manages the conversation flow between
user input, planner decisions, and tool executions. Handles state transitions
and enforces loop limits.
"""

from agent_core.types.state import AgentState

from agent_core.tools.base import ToolRegistry
from agent_core.types.messages import FinalAnswer, ToolCall
from agent_core.config import LOOP_LIMIT
from agent_core.llm.planner import LLMPlanner
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class AgentRunner:
    def __init__(self, tools: 'ToolRegistry', planner: 'LLMPlanner'):
        """
        Initialize the agent runner.

        Input:
            tools: Registry containing all available tools
            planner: LLM-based planner for decision making

        Output:
            None

        Description:
            Sets up the runner with tools and planner, configures max steps from LOOP_LIMIT
        """
        # self.memory = memory
        self.tools = tools
        self.planner = planner
        self.max_steps = LOOP_LIMIT
        logging.info("AgentRunner initialized with tools and planner.")

    def set_context(self, agent_state: AgentState, ltm_context: list, rag_context: list):
        """
        Inject LTM and RAG context into AgentState's memory_context.

        Args:
            agent_state (AgentState): The active state object
            ltm_context (list): List of structured LTM entries
            rag_context (list): List of semantic documents from RAG
        """
        memory_blocks = []

        for item in ltm_context:
            memory_blocks.append({
                "role": "memory",
                "source": "ltm",
                "content": item.get("content", "")
            })

        for doc in rag_context:
            memory_blocks.append({
                "role": "memory",
                "source": "rag",
                "content": doc.get("document", "")
            })

        agent_state.memory_context.extend(memory_blocks)
        logging.debug(
            f"Context set with {len(ltm_context)} LTM entries and {len(rag_context)} RAG documents.")

    async def run(self, user_input: str) -> str:
        """
        Runs the main agent loop processing user input.

        Input:
            user_input: String containing the user's message or query

        Output:
            str: Final response to user, either from:
                - FinalAnswer from planner
                - Tool execution result
                - Error message
                - Forced finish message if loop limit reached

        Description:
            1. Creates initial state with user input
            2. Enters main loop (limited by LOOP_LIMIT):
                - Gets next action from planner
                - If FinalAnswer, returns it
                - If ToolCall, executes tool and updates state
            3. If loop limit reached, forces finish
        """
        state = AgentState(user_input=user_input)
        logging.debug(f"Starting run with input: {user_input}")

        while state.step_count < self.max_steps:
            logging.debug(f"Step {state.step_count}")
            action = self.planner.choose_action(state)
            logging.debug(f"Chosen action: {action}")

            if isinstance(action, FinalAnswer):
                logging.debug("Got final answer")
                return action.output

            if isinstance(action, ToolCall):
                try:
                    logging.debug(
                        f"Executing tool: {action.name} with args: {action.args}")
                    result = await self.tools.run_tool(action.name, **action.args)
                    logging.debug(f"Tool result: {result}")
                    state.add_tool_result(action, result)
                    logging.debug(f"Updated state: {state}")
                except Exception as e:
                    logging.error(f"Tool execution error: {str(e)}")
                    return f"Error executing tool {action.name}: {str(e)}"

        logging.warning("Loop limit reached, forcing finish.")
        return self.planner.force_finish(state)
