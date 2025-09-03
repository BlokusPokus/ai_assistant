"""
Grocery list management tool implementation.
"""
from typing import List, Optional

from .base import Tool


def add_grocery_item(
    item: str, quantity: Optional[int] = 1, notes: Optional[str] = None
) -> str:
    """Add item to grocery list"""
    # TODO: Implement grocery list storage
    return f"Added {quantity}x {item} to grocery list"


def get_deals(store: Optional[str] = None) -> str:
    """Get current grocery deals"""
    # TODO: Implement grocery deals extraction
    return f"Current deals at {store or 'all stores'}"


GroceryAddTool = Tool(
    name="add_grocery_item",
    func=add_grocery_item,
    description="Add item to grocery list",
    parameters={
        "item": {"type": "string", "description": "Item name"},
        "quantity": {
            "type": "integer",
            "description": "Optional quantity",
            "optional": True,
        },
        "notes": {
            "type": "string",
            "description": "Optional notes about the item",
            "optional": True,
        },
    },
)

GroceryDealsTool = Tool(
    name="get_deals",
    func=get_deals,
    description="Get current grocery deals",
    parameters={
        "store": {
            "type": "string",
            "description": "Optional store name to filter deals",
            "optional": True,
        }
    },
)
