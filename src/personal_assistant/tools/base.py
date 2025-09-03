"""
Base classes for Tool and ToolRegistry implementation.

📁 tools/base.py
Defines Tool and ToolRegistry. Also handles schema generation and safe execution.
"""

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Dict

import jsonschema

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
        self._last_user_intent = None  # Store last user intent for error context

        # Validate parameter schema
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a JSON schema dict")

    def set_category(self, category: str):
        """Sets the tool category (e.g., 'Calendar', 'Email', 'Notes', etc.)"""
        self.category = category
        return self

    def set_user_intent(self, user_intent: str):
        """Sets the user intent for better error context and recovery guidance."""
        self._last_user_intent = user_intent
        return self

    def get_user_intent(self) -> str:
        """Gets the stored user intent for error context."""
        return self._last_user_intent or "Unknown user intent"

    def validate_args(self, kwargs: Dict[str, Any]):
        """Validates arguments against parameter schema."""
        try:
            # Use the parameters schema directly since it's already a complete JSON schema
            jsonschema.validate(instance=kwargs, schema=self.parameters)
        except jsonschema.exceptions.ValidationError as e:
            # Provide more helpful error messages
            error_msg = str(e)

            # Handle specific validation error types
            if "is not of type" in error_msg:
                # Extract the problematic field and provide better guidance
                field_name = (
                    error_msg.split("'")[1] if "'" in error_msg else "unknown field"
                )
                expected_type = (
                    error_msg.split("'")[3] if "'" in error_msg else "unknown type"
                )

                # Get the expected type from the schema for better guidance
                schema_props = self.parameters.get("properties", {})
                field_schema = schema_props.get(field_name, {})
                expected_format = field_schema.get("description", "")

                raise ValueError(
                    f"Invalid argument '{field_name}' for tool {self.name}. "
                    f"Expected type: {expected_type}. "
                    f"{expected_format}. "
                    f"Received: {kwargs.get(field_name, 'None')}"
                )

            elif "is a required property" in error_msg:
                # Handle missing required fields
                field_name = (
                    error_msg.split("'")[1] if "'" in error_msg else "unknown field"
                )
                raise ValueError(
                    f"Missing required argument '{field_name}' for tool {self.name}. "
                    f"Please provide this parameter."
                )

            elif "is not one of" in error_msg:
                # Handle enum validation errors
                # Extract field name and received value from error message
                parts = error_msg.split("'")
                if len(parts) >= 4:
                    received_value = parts[1]
                    field_name = parts[3] if len(parts) > 3 else "unknown field"
                else:
                    field_name = "unknown field"
                    received_value = "unknown value"

                schema_props = self.parameters.get("properties", {})
                field_schema = schema_props.get(field_name, {})
                allowed_values = field_schema.get("enum", [])
                raise ValueError(
                    f"Invalid value '{received_value}' for '{field_name}' in tool {self.name}. "
                    f"Allowed values: {allowed_values}. "
                    f"Please use one of the allowed values."
                )
            else:
                raise ValueError(f"Invalid arguments for tool {self.name}: {error_msg}")

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
                from .error_handling import (
                    create_error_context,
                    enhance_prompt_with_error,
                    format_tool_error_response,
                )

                # Create rich error context
                error_context = create_error_context(
                    error=e,
                    tool_name=self.name,
                    args=kwargs,
                    user_intent=self.get_user_intent(),  # Use the new method
                )

                # Enhance the LLM instructions with detailed error context for better AI recovery
                enhanced_instructions = enhance_prompt_with_error(
                    error_context.get(
                        "llm_instructions",
                        f"The tool '{self.name}' failed with error: {str(e)}",
                    ),
                    error_context,
                )
                error_context["llm_instructions"] = enhanced_instructions

                # Return structured error response with enhanced LLM guidance
                return format_tool_error_response(error_context)

            except ImportError:
                # Fallback to basic error handling if error_handling module not available
                logger.error(f"Tool {self.name} execution error: {str(e)}")

                # Provide enhanced fallback guidance for better AI recovery
                fallback_instructions = f"""
The tool '{self.name}' failed with the following error:
- Error: {str(e)}
- Tool: {self.name}
- Arguments: {kwargs}

Recovery Hints:
- Check if the arguments are valid for this tool
- Verify that required parameters are provided
- Consider using different parameter values
- Try breaking down the request into simpler steps

Suggested Actions:
- Review the tool's parameter requirements
- Ask the user for clarification on missing parameters
- Try an alternative approach if available
- Provide specific guidance on what went wrong

Please use this information to guide your next action and help the user resolve the issue.
"""

                return {
                    "error": True,
                    "error_type": "general_error",
                    "error_message": str(e),
                    "tool_name": self.name,
                    "llm_instructions": fallback_instructions,
                }


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._llm_planner = None
        self._categories: Dict[str, set] = {}  # Track tools by category
        logger.info("ToolRegistry initialized.")

    def set_planner(self, planner: "LLMPlanner"):
        """Establish bidirectional relationship with planner"""
        self._llm_planner = planner
        logger.info("Planner set for ToolRegistry.")

    def set_user_intent_for_all_tools(self, user_intent: str):
        """Set user intent for all registered tools to improve error context and recovery guidance."""
        for tool in self.tools.values():
            tool.set_user_intent(user_intent)
        logger.info(
            f"Set user intent for {len(self.tools)} tools: {user_intent[:100]}..."
        )

    def set_user_intent_for_category(self, category: str, user_intent: str):
        """Set user intent for tools in a specific category."""
        if category in self._categories:
            for tool_name in self._categories[category]:
                self.tools[tool_name].set_user_intent(user_intent)
            logger.info(
                f"Set user intent for {len(self._categories[category])} tools in category '{category}': {user_intent[:100]}..."
            )
        else:
            logger.warning(f"Category '{category}' not found in ToolRegistry")

    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        if tool.category:
            if tool.category not in self._categories:
                self._categories[tool.category] = set()
            self._categories[tool.category].add(tool.name)
        logger.info(f"Registered tool: {tool.name} in category: {tool.category}")

    def get_schema(self) -> dict:
        """Get tool schemas for LLM function calling"""
        if not self.tools:
            logger.warning("No tools registered in ToolRegistry.")

        schema = {}
        for name, tool in self.tools.items():
            # Use the tool's parameters directly as they already contain the full JSON schema
            schema[name] = {
                "name": name,
                "description": tool.description,
                "category": tool.category,  # Include category in schema
                "parameters": tool.parameters,  # Use the full parameters schema
            }
        return schema

    def get_tools_by_category(self, category: str) -> Dict[str, Tool]:
        """Get all tools in a specific category"""
        if category not in self._categories:
            return {}
        return {name: self.tools[name] for name in self._categories[category]}

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
