# LTM Tool Package

## Purpose

This package provides the **tool interface** for Long-Term Memory (LTM) operations. It's the "how to use LTM" layer.

## What This Package Does

- **Tool Definition**: Defines LTM as a usable tool in your system
- **Storage Operations**: Basic CRUD operations for LTM memories
- **Tool Management**: Utilities for using LTM in agent workflows
- **User Interface**: How users interact with LTM through tools

## Relationship to LTM Optimization

- **This package** (`tools/ltm/`): "How to use LTM"
- **LTM Optimization** (`memory/ltm_optimization/`): "How to make LTM smarter"

## Key Components

- `ltm_tool.py` - Main tool definition and interface
- `ltm_manager.py` - Tool management utilities
- `ltm_storage.py` - Basic storage operations
- `enhanced_ltm_storage.py` - Advanced storage with context

## Usage

```python
from personal_assistant.tools.ltm import LTMTool

ltm_tool = LTMTool()
# Use LTM as a tool in your agent system
```

## Import Pattern

- **For tool usage**: Import from `tools.ltm`
- **For optimization**: Import from `memory.ltm_optimization`
- **For basic operations**: Use the tool interface
