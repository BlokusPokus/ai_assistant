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
from agent_core.memory.interface import MemoryInterface
from agent_core.llm.planner import LLMPlanner


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
        # Initialize state
        state = AgentState(user_input=user_input)

        # Skip memory query for now
        # state.memory_context = self.memory.query(user_input)

        while state.step_count < self.max_steps:
            # Get next action from planner
            action = self.planner.choose_action(state)

            if isinstance(action, FinalAnswer):
                return action.output

            if isinstance(action, ToolCall):
                try:
                    # Convert arguments to integers if necessary
                    args = {k: int(v) if isinstance(v, float)
                            else v for k, v in action.args.items()}

                    # Await the execution of the tool
                    result = await self.tools.run_tool(action.name, **args)
                    print(f"Executed tool {action.name} with result: {result}")
                    # Add to memory
                    # self.memory.add(str(result), {
                    #     "tool": action.name,
                    #     "args": action.args
                    # })
                    # Update state
                    state.add_tool_result(action, result)
                except Exception as e:
                    return f"Error executing tool {action.name}: {str(e)}"

        # Hit loop limit
        return self.planner.force_finish(state)
