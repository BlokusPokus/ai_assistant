# Tool Template for Personal Assistant

This template provides a standardized structure for creating new tools. Use this as a reference when implementing new functionality.

## Patterns Observed

1. **Class-based tools** (EmailTool, CalendarTool, NotionNotesTool) - for complex integrations
2. **Function-based tools** (Grocery, Reminder, Expense) - for simple operations
3. All tools follow the `Tool` class pattern with `name`, `func`, `description`, and `parameters`
4. Required parameters only in tool definitions (no "optional" field)
5. Async functions for better performance
6. Proper error handling and logging

---

## Pattern 1: Class-Based Tool (for complex integrations)

**Use this pattern when you need:**

- Multiple related functions
- Shared state/configuration
- External API integration
- Authentication handling

**Examples:** EmailTool, CalendarTool, NotionNotesTool

### Template Structure

```python
import asyncio
import logging
from typing import Dict, Any, List, Optional
from ..base import Tool

logger = logging.getLogger(__name__)

class ExampleComplexTool:
    """
    Template for complex tools that need:
    - Multiple related functions
    - Shared state/configuration
    - External API integration
    - Authentication handling
    """

    def __init__(self):
        # Initialize any shared resources, tokens, clients, etc.
        self.api_url = "https://api.example.com"
        self._access_token = None

        # Create individual tools
        self.create_item_tool = Tool(
            name="create_item",
            func=self.create_item,
            description="Create a new item in the system",
            parameters={
                "content": {
                    "type": "string",
                    "description": "Item content (required)"
                }
            }
        )

        self.get_item_tool = Tool(
            name="get_item",
            func=self.get_item,
            description="Retrieve a specific item by ID",
            parameters={
                "item_id": {
                    "type": "string",
                    "description": "Item ID to retrieve"
                }
            }
        )

        self.update_item_tool = Tool(
            name="update_item",
            func=self.update_item,
            description="Update an existing item by ID",
            parameters={
                "item_id": {
                    "type": "string",
                    "description": "Item ID to update"
                }
            }
        )

        self.delete_item_tool = Tool(
            name="delete_item",
            func=self.delete_item,
            description="Delete an item by ID",
            parameters={
                "item_id": {
                    "type": "string",
                    "description": "Item ID to delete"
                }
            }
        )

        self.search_items_tool = Tool(
            name="search_items",
            func=self.search_items,
            description="Search for items",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            }
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([
            self.create_item_tool,
            self.get_item_tool,
            self.update_item_tool,
            self.delete_item_tool,
            self.search_items_tool
        ])

    def _initialize_auth(self):
        """Initialize authentication if needed"""
        # Example: Load API keys, tokens, etc.
        pass

    async def create_item(self, content: str) -> str:
        """Create a new item"""
        try:
            # Implementation here
            return f"Successfully created item with content: {content}"
        except Exception as e:
            logger.error(f"Error creating item: {e}")
            return f"Error creating item: {str(e)}"

    async def get_item(self, item_id: str) -> str:
        """Retrieve a specific item"""
        try:
            # Implementation here
            return f"Retrieved item with ID: {item_id}"
        except Exception as e:
            logger.error(f"Error retrieving item: {e}")
            return f"Error retrieving item: {str(e)}"

    async def update_item(self, item_id: str) -> str:
        """Update an existing item"""
        try:
            # Implementation here
            return f"Successfully updated item with ID: {item_id}"
        except Exception as e:
            logger.error(f"Error updating item: {e}")
            return f"Error updating item: {str(e)}"

    async def delete_item(self, item_id: str) -> str:
        """Delete an item"""
        try:
            # Implementation here
            return f"Successfully deleted item with ID: {item_id}"
        except Exception as e:
            logger.error(f"Error deleting item: {e}")
            return f"Error deleting item: {str(e)}"

    async def search_items(self, query: str) -> str:
        """Search for items"""
        try:
            # Implementation here
            return f"Found items matching query: {query}"
        except Exception as e:
            logger.error(f"Error searching items: {e}")
            return f"Error searching items: {str(e)}"
```

---

## Pattern 2: Function-Based Tool (for simple operations)

**Use this pattern when you need:**

- Simple, single-purpose operations
- No shared state management
- Quick implementations

**Examples:** Grocery, Reminder, Expense tools

### Template Structure

```python
from ..base import Tool
from typing import Optional

def simple_operation(param1: str, param2: Optional[int] = None) -> str:
    """
    Template for simple operations that don't need complex state management.

    Guidelines:
    - Keep functions focused and single-purpose
    - Use descriptive parameter names
    - Provide clear return values
    - Handle errors gracefully
    """
    try:
        # Implementation here
        result = f"Processed {param1}"
        if param2:
            result += f" with value {param2}"
        return result
    except Exception as e:
        logger.error(f"Error in simple_operation: {e}")
        return f"Error: {str(e)}"

def get_data(category: Optional[str] = None) -> str:
    """
    Template for data retrieval operations.

    Guidelines:
    - Use optional parameters for filters
    - Return descriptive results
    - Handle empty/missing data gracefully
    """
    try:
        # Implementation here
        if category:
            return f"Retrieved data for category: {category}"
        else:
            return "Retrieved all data"
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        return f"Error retrieving data: {str(e)}"

# Tool definitions for function-based tools
SimpleOperationTool = Tool(
    name="simple_operation",
    func=simple_operation,
    description="Perform a simple operation",
    parameters={
        "param1": {
            "type": "string",
            "description": "Primary parameter"
        }
    }
)

GetDataTool = Tool(
    name="get_data",
    func=get_data,
    description="Retrieve data from the system",
    parameters={
        "category": {
            "type": "string",
            "description": "Optional category filter"
        }
    }
)
```

---

## Pattern 3: Legacy Tool Definitions (for backward compatibility)

**Use this pattern when you need to maintain compatibility with existing code:**

```python
# Legacy tool definitions for backward compatibility
# These wrap the class methods with asyncio.run() for compatibility
LegacyCreateTool = Tool(
    name="legacy_create",
    func=lambda **kwargs: asyncio.run(ExampleComplexTool().create_item(**kwargs)),
    description="Legacy create item function",
    parameters={
        "content": {
            "type": "string",
            "description": "Item content"
        }
    }
).set_category("Example")
```

---

## Tool Registration Template

To register your new tool, add it to `src/personal_assistant/tools/__init__.py`:

```python
# For class-based tools:
from .your_tool.your_tool import YourToolClass

# For function-based tools:
from .your_tool.your_tool import YourTool1, YourTool2

def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    # Register class-based tools
    your_tool = YourToolClass()
    for tool in your_tool:
        tool.set_category("YourCategory")
        registry.register(tool)

    # Register function-based tools
    registry.register(YourTool1)
    registry.register(YourTool2)

    return registry

# Update __all__ exports
__all__ = [
    'YourToolClass',
    'YourTool1',
    'YourTool2',
    # ... other exports
]
```

---

## Parameter Type Reference

### Common Parameter Types

- `"string"` - Text values
- `"integer"` - Whole numbers
- `"number"` - Decimal numbers (float)
- `"boolean"` - True/false values

### Parameter Structure

```python
{
    "param_name": {
        "type": "string|integer|number|boolean",
        "description": "Clear description of what this parameter does"
    }
}
```

**⚠️ IMPORTANT:** Do NOT include `"optional": True` in tool definitions. The LLM will handle optional parameters based on the function signature.

---

## Error Handling Template

### Standard Error Handling Pattern

```python
try:
    # Your implementation
    result = await some_operation()
    return f"Success: {result}"
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return f"Error: {str(e)}"
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return f"Error: {str(e)}"
```

---

## Configuration Template

For tools that need configuration, add to `src/personal_assistant/config/settings.py`:

```python
class Settings(BaseSettings):
    # Your tool settings
    YOUR_API_KEY: Optional[str] = None
    YOUR_DATABASE_URL: Optional[str] = None
    YOUR_TIMEOUT: int = 30

    class Config:
        env_file = config_file
        case_sensitive = False
```

Add to `config/development.env`:

```env
YOUR_API_KEY=your_api_key_here
YOUR_DATABASE_URL=your_database_url_here
YOUR_TIMEOUT=30
```

---

## Testing Template

Create a test script for your tool:

```python
#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from your_tool.your_tool import YourToolClass

async def test_your_tool():
    tool = YourToolClass()

    # Test your functions
    result = await tool.create_item("test content")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_your_tool())
```

---

## Documentation Template

Create documentation for your tool:

````markdown
# Your Tool Documentation

## Overview

Brief description of what your tool does.

## Setup

1. Install dependencies
2. Configure environment variables
3. Set up external services

## Available Tools

### create_item

- **Purpose**: Create new items
- **Parameters**:
  - `content` (required): Item content
- **Returns**: Success/error message

### get_item

- **Purpose**: Retrieve items by ID
- **Parameters**:
  - `item_id` (required): Item ID
- **Returns**: Item details or error message

## Error Handling

- Network errors: Retry with exponential backoff
- Authentication errors: Check API keys
- Validation errors: Verify parameter formats

## Examples

```python
# Create an item
result = await tool.create_item("My content")

# Get an item
result = await tool.get_item("item_123")
```
````

```

---

## Key Guidelines

### ✅ Do's
- Use async functions for better performance
- Provide clear, descriptive parameter names
- Handle errors gracefully with try/catch
- Log errors appropriately
- Return descriptive success/error messages
- Keep functions focused and single-purpose
- Use type hints for better code clarity

### ❌ Don'ts
- Don't include `"optional": True` in tool definitions
- Don't forget to handle exceptions
- Don't return raw error objects to the user
- Don't create overly complex functions
- Don't forget to register tools in `__init__.py`
- Don't skip logging for debugging

### 🔧 Best Practices
- Start with simple function-based tools
- Move to class-based tools when you need shared state
- Test your tools thoroughly before deployment
- Document your tools clearly
- Follow the existing naming conventions
- Use consistent error message formats
```
