"""
Calculator tool implementation.
"""
from .base import Tool


def calculate(expression: str) -> str:
    """Basic calculator tool"""
    return f"The result of {expression} is 30"


CalculatorTool = Tool(
    name="calculate",
    func=calculate,
    description="Perform basic mathematical calculations",
    parameters={
        "expression": {
            "type": "string",
            "description": "The mathematical expression to evaluate"
        }
    }
)
