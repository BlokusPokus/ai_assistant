"""
Base classes for Tool and ToolRegistry implementation.

📁 tools/base.py
Defines Tool and ToolRegistry. Also handles schema generation and safe execution.
"""

from typing import Dict, Any, Callable, TYPE_CHECKING
import jsonschema

# Only import type hints during type checking
if TYPE_CHECKING:
    from agent_core.llm.planner import LLMPlanner


class Tool:
    def __init__(self, name: str, func: Callable, description: str, parameters: Dict):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters

        # Validate parameter schema
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a JSON schema dict")

    def validate_args(self, kwargs: Dict[str, Any]):
        """Validates arguments against parameter schema."""
        try:
            jsonschema.validate(instance=kwargs, schema=self.parameters)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(
                f"Invalid arguments for tool {self.name}: {str(e)}")

    def execute(self, **kwargs):
        """Executes the tool with validation."""
        self.validate_args(kwargs)
        return self.func(**kwargs)


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._llm_planner = None

    def set_planner(self, planner: 'LLMPlanner'):
        """Establish bidirectional relationship with planner"""
        self._llm_planner = planner

    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool

    def get_schema(self) -> dict:
        """Get tool schemas for LLM function calling"""
        return {
            name: {
                "name": name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": list(tool.parameters.keys())
                }
            }
            for name, tool in self.tools.items()
        }

    def run_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        result = self.tools[name].execute(**kwargs)

        # Notify planner of tool execution if needed
        if self._llm_planner:
            self._llm_planner.on_tool_completion(name, result)

        return result
