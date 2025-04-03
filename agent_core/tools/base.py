"""
Base classes for Tool and ToolRegistry implementation.

📁 tools/base.py
Defines Tool and ToolRegistry. Also handles schema generation and safe execution.
"""

from typing import Dict, Any, Callable, TYPE_CHECKING
import jsonschema
import asyncio
import logging

# Only import type hints during type checking
if TYPE_CHECKING:
    from agent_core.llm.planner import LLMPlanner


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
            jsonschema.validate(instance=kwargs, schema=self.parameters)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(
                f"Invalid arguments for tool {self.name}: {str(e)}")

    async def execute(self, **kwargs):
        """Executes the tool with validation."""
        self.validate_args(kwargs)
        # Check if the function is a coroutine
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        else:
            return self.func(**kwargs)


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._llm_planner = None
        self._categories: Dict[str, set] = {}  # Track tools by category
        logging.info("ToolRegistry initialized.")

    def set_planner(self, planner: 'LLMPlanner'):
        """Establish bidirectional relationship with planner"""
        self._llm_planner = planner
        logging.info("Planner set for ToolRegistry.")

    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        if tool.category:
            if tool.category not in self._categories:
                self._categories[tool.category] = set()
            self._categories[tool.category].add(tool.name)
        logging.info(
            f"Registered tool: {tool.name} in category: {tool.category}")

    def get_schema(self) -> dict:
        """Get tool schemas for LLM function calling"""
        if not self.tools:
            logging.warning("No tools registered in ToolRegistry.")

        schema = {}
        for name, tool in self.tools.items():
            schema[name] = {
                "name": name,
                "description": tool.description,
                "category": tool.category,  # Include category in schema
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": list(tool.parameters.keys())
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
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        # Await the tool execution
        result = await self.tools[name].execute(**kwargs)

        # Notify planner of tool execution if needed
        if self._llm_planner:
            self._llm_planner.on_tool_completion(name, result)

        return result
