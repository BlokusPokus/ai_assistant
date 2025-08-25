# Logging Controls

This document explains how to control logging verbosity in your personal assistant to make logs more readable.

## Quick Logging Level Changes

### Method 1: Environment Variables (Recommended)

Set these environment variables before running your application:

```bash
# Set overall logging level
export PA_LOG_LEVEL=WARNING

# Or set specific module levels
export PA_CORE_LOG_LEVEL=WARNING
export PA_LLM_LOG_LEVEL=INFO
export PA_TOOLS_LOG_LEVEL=WARNING
export PA_MEMORY_LOG_LEVEL=INFO
```

**Available levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Method 2: Python Script

Use the provided script to toggle logging levels:

```bash
# Minimal logging (WARNING level)
python scripts/toggle_logging.py quiet

# Balanced logging (INFO level) - recommended for development
python scripts/toggle_logging.py normal

# Detailed logging (DEBUG level) - for troubleshooting
python scripts/toggle_logging.py verbose
```

### Method 3: Code Changes

Modify your `config/development.env` file:

```env
# Reduce verbosity
LOG_LEVEL=INFO
CORE_LOG_LEVEL=INFO
LLM_LOG_LEVEL=INFO
MEMORY_LOG_LEVEL=INFO
RAG_LOG_LEVEL=INFO
TOOLS_LOG_LEVEL=INFO
TYPES_LOG_LEVEL=INFO
```

## What Each Level Shows

- **CRITICAL**: Only critical errors that might crash the system
- **ERROR**: Errors that prevent normal operation
- **WARNING**: Issues that don't stop operation but should be addressed
- **INFO**: General information about what's happening (recommended)
- **DEBUG**: Detailed information for troubleshooting (very verbose)

## Recommended Settings

### For Normal Development

```env
LOG_LEVEL=INFO
CORE_LOG_LEVEL=INFO
LLM_LOG_LEVEL=INFO
TOOLS_LOG_LEVEL=INFO
```

### For Troubleshooting

```env
LOG_LEVEL=DEBUG
CORE_LOG_LEVEL=DEBUG
LLM_LOG_LEVEL=DEBUG
TOOLS_LOG_LEVEL=DEBUG
```

### For Production/Quiet Operation

```env
LOG_LEVEL=WARNING
CORE_LOG_LEVEL=WARNING
LLM_LOG_LEVEL=WARNING
TOOLS_LOG_LEVEL=WARNING
```

## What Gets Suppressed

The logging system automatically suppresses verbose output from:

- HTTP libraries (httpx, httpcore, urllib3)
- Asyncio operations
- Proto deprecation warnings
- External API request/response details

## Example Usage

```bash
# Start with quiet logging
export PA_LOG_LEVEL=WARNING
python your_app.py

# Switch to verbose when you need to debug
export PA_LOG_LEVEL=DEBUG
python your_app.py

# Or use the script
python scripts/toggle_logging.py verbose
```

## Troubleshooting

If you're still seeing too many logs:

1. Check if any modules are still set to DEBUG in your config
2. Use `PA_LOG_LEVEL=WARNING` to override all levels
3. Check for any custom loggers in your code that might bypass the configuration

## Log Files

Logs are saved to the `logs/` directory with separate files for each module:

- `core.log` - Agent lifecycle and state transitions
- `llm.log` - LLM interactions and responses
- `tools.log` - Tool execution and registry operations
- `memory.log` - Database and memory operations
- `rag.log` - Document retrieval and processing
