"""
Base classes for Tool and ToolRegistry implementation.

📁 tools/base.py
Defines Tool and ToolRegistry. Also handles schema generation and safe execution.
"""

from typing import Dict, Any, Callable, TYPE_CHECKING
import jsonschema
import asyncio
from personal_assistant.config.logging_config import get_logger

# Configure module logger
logger = get_logger("tools")

# Only import type hints during type checking
if TYPE_CHECKING:
    from personal_assistant.llm.planner import LLMPlanner


class Tool:
    def __init__(self, name: str, func: Callable, description: str, parameters: Dict):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters
        self.category = None  # Add category for tool organization

        # Validate parameter schema
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a JSON schema dict")

    def set_category(self, category: str):
        """Sets the tool category (e.g., 'Calendar', 'Email', 'Notes', etc.)"""
        self.category = category
        return self

    def validate_args(self, kwargs: Dict[str, Any]):
        """Validates arguments against parameter schema."""
        try:
            # Create a complete JSON schema for validation
            schema = {
                "type": "object",
                "properties": self.parameters,
                "required": []  # All parameters are optional for now
            }
            jsonschema.validate(instance=kwargs, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(
                f"Invalid arguments for tool {self.name}: {str(e)}")

    async def execute(self, **kwargs):
        """Executes the tool with validation and enhanced error handling."""
        try:
            self.validate_args(kwargs)
            # Check if the function is a coroutine
            if asyncio.iscoroutinefunction(self.func):
                return await self.func(**kwargs)
            else:
                return self.func(**kwargs)
        except Exception as e:
            # Import error handling utilities here to avoid circular imports
            try:
                from .error_handling import create_error_context, format_tool_error_response

                # Create rich error context
                error_context = create_error_context(
                    error=e,
                    tool_name=self.name,
                    args=kwargs,
                    user_intent=None  # Could be enhanced to capture user intent
                )

                # Return structured error response with LLM guidance
                return format_tool_error_response(error_context)

            except ImportError:
                # Fallback to basic error handling if error_handling module not available
                logger.error(f"Tool {self.name} execution error: {str(e)}")
                return {
                    "error": True,
                    "error_type": "general_error",
                    "error_message": str(e),
                    "tool_name": self.name,
                    "llm_instructions": f"The tool '{self.name}' failed with error: {str(e)}. Please try again or ask for help."
                }


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._llm_planner = None
        self._categories: Dict[str, set] = {}  # Track tools by category
        logger.info("ToolRegistry initialized.")

    def set_planner(self, planner: 'LLMPlanner'):
        """Establish bidirectional relationship with planner"""
        self._llm_planner = planner
        logger.info("Planner set for ToolRegistry.")

    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        if tool.category:
            if tool.category not in self._categories:
                self._categories[tool.category] = set()
            self._categories[tool.category].add(tool.name)
        logger.info(
            f"Registered tool: {tool.name} in category: {tool.category}")

    def get_schema(self) -> dict:
        """Get tool schemas for LLM function calling"""
        if not self.tools:
            logger.warning("No tools registered in ToolRegistry.")

        schema = {}
        for name, tool in self.tools.items():
            # Determine which parameters are required (only content for create_note, note_id for others)
            required_params = []
            for param_name, param_schema in tool.parameters.items():
                # Only make content and note_id required, others are optional
                if param_name in ['content', 'note_id', 'query', 'to_recipients', 'subject', 'body', 'event_id', 'message_id', 'count', 'start_time', 'text', 'time', 'reminder_id', 'amount']:
                    required_params.append(param_name)

            schema[name] = {
                "name": name,
                "description": tool.description,
                "category": tool.category,  # Include category in schema
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": required_params
                }
            }
        return schema

    def get_tools_by_category(self, category: str) -> Dict[str, Tool]:
        """Get all tools in a specific category"""
        if category not in self._categories:
            return {}
        return {name: self.tools[name]
                for name in self._categories[category]}

    async def run_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name"""
        logger.debug(f"=== TOOL REGISTRY: EXECUTING TOOL {name} ===")
        logger.debug(f"=== TOOL REGISTRY: ARGUMENTS {kwargs} ===")

        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")

        # Await the tool execution
        logger.debug(f"=== TOOL REGISTRY: CALLING TOOL.EXECUTE ===")
        result = await self.tools[name].execute(**kwargs)
        logger.debug(f"=== TOOL REGISTRY: TOOL EXECUTION COMPLETED ===")
        logger.debug(f"=== TOOL REGISTRY: RESULT {result} ===")

        # Notify planner of tool execution if needed
        if self._llm_planner:
            logger.debug(f"=== TOOL REGISTRY: NOTIFYING PLANNER ===")
            self._llm_planner.on_tool_completion(name, result)

        return result
