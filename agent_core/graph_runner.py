"""
LangGraph definition and runner logic for the agent's workflow.

📁 agent_core/graph_runner.py
Defines and runs the LangGraph execution flow. Handles node registration, 
agent loop, planner/tool/reflect transitions.
"""

from agent_core.types.state import AgentState

from agent_core.tools.base import ToolRegistry
from agent_core.types.messages import FinalAnswer, ToolCall
from agent_core.config import LOOP_LIMIT
from agent_core.memory.interface import MemoryInterface
from agent_core.llm.planner import LLMPlanner


class LangGraphRunner:
    def __init__(self, tools: 'ToolRegistry', planner: 'LLMPlanner'):
        # self.memory = memory
        self.tools = tools
        self.planner = planner
        self.max_steps = LOOP_LIMIT

    async def run(self, user_input: str) -> str:
        """
        Runs the LangGraph agent loop.

        Args:
            user_input (str): Initial user message

        Returns:
            str: Final output or answer
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
