"""
AgentLoopService handles the main agent conversation loop execution.
"""

from typing import Tuple

from personal_assistant.config.logging_config import get_logger
from personal_assistant.config.settings import settings
from personal_assistant.llm.planner import LLMPlanner
from personal_assistant.types.messages import FinalAnswer, ToolCall
from personal_assistant.types.state import AgentState

logger = get_logger("agent_loop_service")


class AgentLoopService:
    """Service for managing the main agent conversation loop."""
    
    def __init__(self, planner: LLMPlanner, tool_execution_service):
        """
        Initialize the agent loop service.
        
        Args:
            planner: LLM-based planner for decision making
            tool_execution_service: Service for executing tools
        """
        self.planner = planner
        self.tool_execution_service = tool_execution_service
        self.max_steps = settings.LOOP_LIMIT
    
    async def execute_loop(self, state: AgentState, user_input: str) -> Tuple[str, AgentState]:
        """
        Execute the main agent loop processing user input.
        
        Args:
            state: Current agent state
            user_input: User's input message
            
        Returns:
            Tuple of (response, updated_state)
        """
        logger.debug(f"Starting run with input: {user_input}")

        # Add the current user input to conversation history if not already there
        if (
            not state.conversation_history
            or state.conversation_history[-1].get("content") != user_input
        ):
            state.conversation_history.append({"role": "user", "content": user_input})

        # Apply size limits after adding new input
        state._apply_size_limits()

        while state.step_count < self.max_steps:
            logger.debug(f"Step {state.step_count}")

            # Get action from planner
            action = await self._get_next_action(state)
            
            # Process the action
            if isinstance(action, FinalAnswer):
                return await self._handle_final_answer(action, state)
            elif isinstance(action, ToolCall):
                success = await self._handle_tool_call(action, state)
                if not success:
                    # Tool execution failed, return error response
                    return action.name, state
            else:
                logger.warning(f"Unknown action type: {type(action)} - {action}")
                logger.warning("This action will be ignored and the loop will continue")

        # Loop limit reached
        logger.warning("Loop limit reached, forcing finish.")
        forced_response = self.planner.force_finish(state)
        state._apply_size_limits()
        return forced_response, state
    
    async def _get_next_action(self, state: AgentState):
        """Get the next action from the planner."""
        logger.debug("=== CALLING PLANNER.CHOOSE_ACTION ===")
        action = self.planner.choose_action(state)
        logger.debug(f"=== PLANNER RETURNED ACTION: {type(action).__name__} ===")
        logger.debug(f"Chosen action: {action}")
        logger.debug(f"Action type: {type(action)}")
        logger.debug(f"Is ToolCall: {isinstance(action, ToolCall)}")
        logger.debug(f"Is FinalAnswer: {isinstance(action, FinalAnswer)}")
        return action
    
    async def _handle_final_answer(self, action: FinalAnswer, state: AgentState) -> Tuple[str, AgentState]:
        """Handle a final answer action."""
        logger.debug("Got final answer")
        state.conversation_history.append({"role": "assistant", "content": action.output})
        state._apply_size_limits()
        return action.output, state
    
    async def _handle_tool_call(self, action: ToolCall, state: AgentState) -> bool:
        """Handle a tool call action."""
        result, success = await self.tool_execution_service.execute_and_update(action, state)
        
        if not success:
            logger.error(f"Tool execution failed: {result}")
            return False
        
        return True
