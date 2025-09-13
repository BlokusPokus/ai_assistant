"""
ToolExecutionService handles tool calling and result processing.
"""

from typing import Any, Dict, Optional, Tuple

from personal_assistant.config.logging_config import get_logger
from personal_assistant.tools.base import ToolRegistry
from personal_assistant.types.messages import ToolCall
from personal_assistant.types.state import AgentState

logger = get_logger("tool_execution_service")


class ToolExecutionService:
    """Service for executing tools and processing results."""
    
    def __init__(self, tools: ToolRegistry):
        """
        Initialize the tool execution service.
        
        Args:
            tools: Registry containing all available tools
        """
        self.tools = tools
    
    async def execute_tool(self, action: ToolCall, state: AgentState, user_id: int) -> Tuple[Any, bool]:
        """
        Execute a tool call and return the result.
        
        Args:
            action: The tool call action to execute
            state: Current agent state
            user_id: User identifier to inject into tool calls
            
        Returns:
            Tuple of (result, success_flag)
        """
        try:
            logger.debug(f"=== EXECUTING TOOL: {action.name} ===")
            logger.debug(f"Tool args: {action.args}")

            # Automatically inject user_id into tool arguments
            tool_args = action.args.copy()
            tool_args['user_id'] = user_id
            logger.debug(f"Injected user_id {user_id} into tool call")

            # Execute tool with injected user_id
            result = await self.tools.run_tool(action.name, **tool_args)
            logger.debug("=== TOOL EXECUTION COMPLETED ===")
            logger.debug(f"Tool result: {result}")

            return result, True

        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return f"Error executing tool {action.name}: {str(e)}", False
    
    def update_state_with_result(self, state: AgentState, action: ToolCall, result: Any) -> None:
        """
        Update agent state with tool execution result.
        
        Args:
            state: Current agent state
            action: The tool call that was executed
            result: The result from tool execution
        """
        logger.debug("=== UPDATING STATE WITH TOOL RESULT ===")
        state.add_tool_result(action, result)
        
        # Log state without embedding vectors to reduce log noise
        state_summary = {
            "user_input": state.user_input,
            "memory_context_count": len(state.memory_context),
            "history_count": len(state.history),
            "step_count": state.step_count,
            "focus": state.focus,
            "conversation_history_count": len(state.conversation_history),
            "last_tool_result_type": type(state.last_tool_result).__name__ if state.last_tool_result else None
        }
        logger.debug(f"Updated state: {state_summary}")
    
    async def execute_and_update(self, action: ToolCall, state: AgentState, user_id: int) -> Tuple[Any, bool]:
        """
        Execute a tool and update the state with the result.
        
        Args:
            action: The tool call action to execute
            state: Current agent state
            user_id: User identifier to inject into tool calls
            
        Returns:
            Tuple of (result, success_flag)
        """
        result, success = await self.execute_tool(action, state, user_id)
        
        if success:
            self.update_state_with_result(state, action, result)
        
        return result, success
