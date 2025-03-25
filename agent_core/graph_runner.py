"""
LangGraph definition and runner logic for the agent's workflow.

📁 agent_core/graph_runner.py
Defines and runs the LangGraph execution flow. Handles node registration, 
agent loop, planner/tool/reflect transitions.
"""


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
        state = initialize_state(user_input, self.memory)
        for _ in range(self.max_steps):
            tool_or_final = self.llm.choose_action(state)
            if tool_or_final.is_final():
                return tool_or_final.output
            result = self.tools.run_tool(
                tool_or_final.name, **tool_or_final.args)
            state = update_state(state, tool_or_final, result)
        return self.llm.force_finish(state)
