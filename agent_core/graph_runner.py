"""
LangGraph definition and runner logic for the agent's workflow.

📁 agent_core/graph_runner.py
Defines and runs the LangGraph execution flow. Handles node registration, 
agent loop, planner/tool/reflect transitions.
"""

from .logs.logger import log_interaction
from .types.state import AgentState
from .logs.models import LogEntry
from datetime import datetime


class LangGraphRunner:
    def __init__(self, memory, tools, llm):
        self.memory = memory
        self.tools = tools
        self.llm = llm
        self.max_steps = 5

    def run(self, user_input: str) -> str:
        """
        Runs the LangGraph agent loop.

        Args:
            user_input (str): Initial user message

        Returns:
            str: Final output or answer
        """
        # Initialize state with memory context
        state = AgentState(user_input)
        state.memory_context = self.memory.query(user_input)

        for step in range(self.max_steps):
            # Get next action from LLM
            action = self.llm.choose_action(state)

            # Enhanced logging with structured LogEntry
            log_entry = LogEntry(
                user_input=user_input,
                memory_used=state.memory_context,
                tool_called=action.name if not action.is_final() else None,
                tool_output=None,  # Will be updated if tool is called
                agent_response=action.output if action.is_final() else None,
                timestamp=datetime.now().isoformat()
            )

            # Log the interaction
            if action.is_final():
                log_interaction(log_entry)
                return action.output

            # Execute tool and update state
            try:
                result = self.tools.run_tool(action.name, **action.args)
                log_entry.tool_output = str(result)
                log_interaction(log_entry)

                self.memory.add(str(result), {
                    "tool": action.name,
                    "args": action.args
                })
                state.add_tool_result(action, result)
            except Exception as e:
                error_msg = f"Error executing tool {action.name}: {str(e)}"
                log_entry.tool_output = error_msg
                log_interaction(log_entry)
                return error_msg

        # If we hit the loop limit, force a finish
        final_response = self.llm.force_finish(state)
        log_interaction(LogEntry(
            user_input=user_input,
            memory_used=state.memory_context,
            tool_called=None,
            tool_output=None,
            agent_response=final_response,
            timestamp=datetime.now().isoformat()
        ))
        return final_response
