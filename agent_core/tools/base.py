"""
Base classes for Tool and ToolRegistry implementation.

📁 tools/base.py
Defines Tool and ToolRegistry. Also handles schema generation and safe execution.
"""


class Tool:
    def __init__(self, name, func, description, parameters):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters

    def execute(self, **kwargs):
        """
        Executes the tool function.

        Args:
            kwargs: Arguments for the tool

        Returns:
            Any: Result of tool execution
        """
        return self.func(**kwargs)


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_schema(self):
        """
        Returns schemas for all tools.

        Returns:
            dict: Tool names and JSON schema
        """
        return {name: tool.parameters for name, tool in self.tools.items()}

    def run_tool(self, name: str, **kwargs):
        """
        Executes a tool by name.

        Args:
            name (str): Tool name
            kwargs: Tool arguments

        Returns:
            Any: Tool output
        """
        return self.tools[name].execute(**kwargs)
