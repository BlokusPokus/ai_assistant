"""
Expense tracking and budget tools implementation.
"""
from decimal import Decimal
from typing import Optional

from ..base import Tool


def add_expense(amount: float, category: str, description: Optional[str] = None) -> str:
    """Add a new expense"""
    # TODO: Implement budget app integration
    return f"Added expense of ${amount} in category '{category}'"


def get_budget_summary(category: Optional[str] = None) -> str:
    """Get budget summary"""
    # TODO: Implement budget app integration
    return f"Budget summary for {category or 'all categories'}"


ExpenseAddTool = Tool(
    name="add_expense",
    func=add_expense,
    description="Add a new expense",
    parameters={
        "amount": {
            "type": "number",
            "description": "Expense amount"
        },
        "category": {
            "type": "string",
            "description": "Expense category"
        },
        "description": {
            "type": "string",
            "description": "Optional expense description",
            "optional": True
        }
    }
)

BudgetSummaryTool = Tool(
    name="get_budget_summary",
    func=get_budget_summary,
    description="Get budget summary by category",
    parameters={
        "category": {
            "type": "string",
            "description": "Optional category to filter by",
            "optional": True
        }
    }
)
