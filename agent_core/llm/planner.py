"""
LLM-based planning and tool selection logic.

📁 llm/planner.py
LLM planner step. Decides whether to respond, call a tool, or reflect.
"""


class LLMPlanner:
    def __init__(self, model):
        self.model = model

    def choose_action(self, state):
        """
        Uses the LLM to decide next step.

        Args:
            state (dict): Current LangGraph state

        Returns:
            ToolCall or FinalAnswer: Either a tool to call or a final response
        """
        pass

    def force_finish(self, state):
        """
        Forces the agent to finish after hitting loop limit.

        Args:
            state (dict): LangGraph state

        Returns:
            str: Final fallback answer
        """
        pass
