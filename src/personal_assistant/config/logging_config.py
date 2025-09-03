"""
Centralized logging configuration for the personal assistant framework.

📁 config/logging_config.py
Sets up module-specific loggers with file and console handlers,
configurable log levels, and consistent formatting across all modules.

Usage:
    from personal_assistant.config.logging_config import setup_logging
    setup_logging()
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Optional

from .settings import settings

# Import structured logging components
try:
    from ..logging import StructuredJSONFormatter
    from ..logging.loki_handler import configure_loki_logging

    STRUCTURED_LOGGING_AVAILABLE = True
    LOKI_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False
    LOKI_AVAILABLE = False


def setup_logging(
    log_level: Optional[str] = None, use_structured_logging: Optional[bool] = None
) -> None:
    """
    Set up centralized logging configuration for all modules.

    Args:
        log_level: Optional override for log level (defaults to settings.LOG_LEVEL)
        use_structured_logging: Whether to use structured JSON logging (defaults to settings.STRUCTURED_LOGGING)
    """
    # Use provided log level or default from settings
    level = log_level or settings.LOG_LEVEL

    # Check for environment variable override
    env_log_level = os.getenv("PA_LOG_LEVEL")
    if env_log_level:
        level = env_log_level
        print(f"🔧 Logging level overridden by PA_LOG_LEVEL: {level}")

    # Determine if structured logging should be used
    structured_logging = use_structured_logging
    if structured_logging is None:
        structured_logging = getattr(settings, "STRUCTURED_LOGGING", False)

    # Check environment variable override
    env_structured = os.getenv("PA_STRUCTURED_LOGGING")
    if env_structured:
        structured_logging = env_structured.lower() in ("true", "1", "yes", "on")
        print(
            f"🔧 Structured logging overridden by PA_STRUCTURED_LOGGING: {structured_logging}"
        )

    # Create logs directory if it doesn't exist
    logs_dir = Path(settings.LOG_DIR)
    logs_dir.mkdir(exist_ok=True)

    # Suppress verbose HTTP logging
    _suppress_http_logging()

    # Define module-specific configurations with individual log levels
    module_configs = {
        "core": {
            "file": f"{settings.LOG_DIR}/core.log",
            "level": getattr(logging, settings.CORE_LOG_LEVEL.upper(), logging.INFO),
            "description": "Agent lifecycle, state transitions, tool execution",
        },
        "llm": {
            "file": f"{settings.LOG_DIR}/llm.log",
            "level": getattr(logging, settings.LLM_LOG_LEVEL.upper(), logging.INFO),
            "description": "LLM interactions, prompt building, response parsing",
        },
        "memory": {
            "file": f"{settings.LOG_DIR}/memory.log",
            "level": getattr(logging, settings.MEMORY_LOG_LEVEL.upper(), logging.INFO),
            "description": "Database operations, memory retrieval, conversation management",
        },
        "rag": {
            "file": f"{settings.LOG_DIR}/rag.log",
            "level": getattr(logging, settings.RAG_LOG_LEVEL.upper(), logging.INFO),
            "description": "Document retrieval, vector search, document processing",
        },
        "tools": {
            "file": f"{settings.LOG_DIR}/tools.log",
            "level": getattr(logging, settings.TOOLS_LOG_LEVEL.upper(), logging.INFO),
            "description": "Tool execution, registry operations, tool-specific logic",
        },
        "types": {
            "file": f"{settings.LOG_DIR}/types.log",
            "level": getattr(logging, settings.TYPES_LOG_LEVEL.upper(), logging.INFO),
            "description": "State management, message handling",
        },
        "oauth_audit": {
            "file": f"{settings.LOG_DIR}/oauth_audit.log",
            "level": logging.INFO,
            "description": "OAuth security events, authorization, token management",
        },
    }

    # Apply environment variable overrides if present
    for module_name in module_configs:
        env_module_level = os.getenv(f"PA_{module_name.upper()}_LOG_LEVEL")
        if env_module_level:
            module_configs[module_name]["level"] = getattr(
                logging, env_module_level.upper(), logging.INFO
            )
            print(
                f"🔧 {module_name} logging level overridden by PA_{module_name.upper()}_LOG_LEVEL: {env_module_level}"
            )

    # Configure each module logger
    for module_name, config in module_configs.items():
        _configure_module_logger(module_name, config, structured_logging)

    # Set up root logger for any unhandled logging
    root_level = getattr(logging, level.upper(), logging.INFO)
    _configure_root_logger(root_level)

    # Configure Loki logging if enabled
    if LOKI_AVAILABLE:
        configure_loki_logging()

    logging.info(
        f"Logging configured with level: {level}, structured: {structured_logging}"
    )


def _suppress_http_logging():
    """
    Suppress verbose HTTP logging from external libraries.
    """
    # Suppress httpx/httpcore verbose logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Suppress urllib3 verbose logging
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Suppress requests verbose logging
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Suppress asyncio verbose logging
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Suppress proto deprecation warnings
    logging.getLogger("proto").setLevel(logging.ERROR)


def _configure_module_logger(
    module_name: str, config: Dict, structured_logging: bool = False
) -> None:
    """
    Configure a specific module logger with file and console handlers.

    Args:
        module_name: Name of the module (e.g., 'core', 'llm')
        config: Configuration dictionary with file, level, and description
        structured_logging: Whether to use structured JSON logging
    """
    logger = logging.getLogger(f"personal_assistant.{module_name}")
    logger.setLevel(config["level"])

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter based on logging type
    if structured_logging and STRUCTURED_LOGGING_AVAILABLE:
        formatter = StructuredJSONFormatter()
        print(f"🔧 Using structured JSON logging for module: {module_name}")
    else:
        formatter = logging.Formatter(
            settings.LOG_FORMAT, datefmt=settings.LOG_DATE_FORMAT
        )

    # File handler (if enabled in settings)
    if settings.LOG_TO_FILE:
        file_handler = logging.FileHandler(config["file"])
        file_handler.setLevel(config["level"])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler (if enabled in settings and in development)
    if settings.LOG_TO_CONSOLE and settings.ENVIRONMENT == "development":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(config["level"])
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False


def _configure_root_logger(level: int) -> None:
    """
    Configure the root logger for any unhandled logging.

    Args:
        level: Log level for root logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add console handler for root logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(settings.LOG_FORMAT, datefmt=settings.LOG_DATE_FORMAT)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a configured logger for a specific module.

    Args:
        module_name: Name of the module (e.g., 'core', 'llm')

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"personal_assistant.{module_name}")


def set_log_level(module_name: str, level: str) -> None:
    """
    Set log level for a specific module.

    Args:
        module_name: Name of the module
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger(f"personal_assistant.{module_name}")
    level_num = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level_num)

    # Update all handlers for this logger
    for handler in logger.handlers:
        handler.setLevel(level_num)


def set_quiet_mode():
    """
    Set all module loggers to WARNING level for minimal output.
    """
    modules = ["core", "llm", "memory", "rag", "tools", "types"]
    for module in modules:
        set_log_level(module, "WARNING")

    # Also suppress HTTP logging
    _suppress_http_logging()

    logging.info("Logging set to quiet mode (WARNING level)")


def set_verbose_mode():
    """
    Set all module loggers to DEBUG level for detailed output.
    """
    modules = ["core", "llm", "memory", "rag", "tools", "types"]
    for module in modules:
        set_log_level(module, "DEBUG")

    logging.info("Logging set to verbose mode (DEBUG level)")


def set_normal_mode():
    """
    Set all module loggers to INFO level for balanced output.
    """
    modules = ["core", "llm", "memory", "rag", "tools", "types"]
    for module in modules:
        set_log_level(module, "INFO")

    # Suppress HTTP logging
    _suppress_http_logging()

    logging.info("Logging set to normal mode (INFO level)")


# Auto-setup logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()
