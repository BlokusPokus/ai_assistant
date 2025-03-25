"""
Calculator tool implementation.
"""
from .base import Tool


def calculate(expression: str) -> str:
    """Basic calculator tool"""
    try:
        return str(eval(expression))
    except:
        return "Invalid expression"


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
