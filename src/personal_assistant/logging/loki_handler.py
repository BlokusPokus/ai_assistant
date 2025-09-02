"""
Loki logging handler for centralized log aggregation.

📁 logging/loki_handler.py
Provides Loki integration for shipping structured logs to centralized log storage.
"""

import logging
import os
from typing import Optional, Dict, Any

try:
    from python_logging_loki import LokiHandler
    LOKI_AVAILABLE = True
except ImportError:
    LOKI_AVAILABLE = False
    LokiHandler = None

from ..config.settings import settings


def create_loki_handler(
    url: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    version: str = "1"
) -> Optional[LokiHandler]:
    """
    Create a Loki handler for shipping logs to Loki.

    Args:
        url: Loki push URL (defaults to settings.LOKI_URL)
        tags: Tags to include with all logs
        version: Loki API version

    Returns:
        LokiHandler instance or None if Loki is not available
    """
    if not LOKI_AVAILABLE:
        print("⚠️  Loki handler not available - python-logging-loki not installed")
        return None

    # Use provided URL or default from settings
    loki_url = url or settings.LOKI_URL

    # Check environment variable override
    env_loki_url = os.getenv("PA_LOKI_URL")
    if env_loki_url:
        loki_url = env_loki_url

    # Default tags
    default_tags = {
        "application": "personal_assistant",
        "environment": settings.ENVIRONMENT,
        "service": "api"
    }

    # Merge with provided tags
    if tags:
        default_tags.update(tags)

    try:
        handler = LokiHandler(
            url=loki_url,
            tags=default_tags,
            version=version
        )
        print(f"🔧 Loki handler created successfully: {loki_url}")
        return handler
    except Exception as e:
        print(f"❌ Failed to create Loki handler: {e}")
        return None


def add_loki_handler_to_logger(
    logger: logging.Logger,
    url: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    level: int = logging.INFO
) -> bool:
    """
    Add Loki handler to a logger.

    Args:
        logger: Logger to add handler to
        url: Loki push URL
        tags: Tags for the handler
        level: Log level for the handler

    Returns:
        True if handler was added successfully, False otherwise
    """
    handler = create_loki_handler(url, tags)
    if not handler:
        return False

    handler.setLevel(level)
    logger.addHandler(handler)
    print(f"🔧 Loki handler added to logger: {logger.name}")
    return True


def configure_loki_logging(
    use_loki: Optional[bool] = None,
    url: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
) -> bool:
    """
    Configure Loki logging for all module loggers.

    Args:
        use_loki: Whether to enable Loki logging (defaults to settings.LOG_TO_LOKI)
        url: Loki push URL
        tags: Tags for all handlers

    Returns:
        True if Loki logging was configured successfully, False otherwise
    """
    # Determine if Loki should be used
    if use_loki is None:
        use_loki = getattr(settings, 'LOG_TO_LOKI', False)

    # Check environment variable override
    env_loki = os.getenv("PA_LOG_TO_LOKI")
    if env_loki:
        use_loki = env_loki.lower() in ('true', '1', 'yes', 'on')

    if not use_loki:
        print("🔧 Loki logging disabled")
        return False

    if not LOKI_AVAILABLE:
        print("❌ Loki logging requested but python-logging-loki not available")
        return False

    # Module names to configure
    modules = ["core", "llm", "memory", "rag", "tools", "types"]

    success_count = 0
    for module_name in modules:
        logger = logging.getLogger(f"personal_assistant.{module_name}")

        # Add module-specific tags
        module_tags = tags.copy() if tags else {}
        module_tags["module"] = module_name

        if add_loki_handler_to_logger(logger, url, module_tags):
            success_count += 1

    print(
        f"🔧 Loki logging configured for {success_count}/{len(modules)} modules")
    return success_count > 0


def test_loki_connection(url: Optional[str] = None) -> bool:
    """
    Test connection to Loki.

    Args:
        url: Loki URL to test (defaults to settings.LOKI_URL)

    Returns:
        True if connection successful, False otherwise
    """
    if not LOKI_AVAILABLE:
        print("❌ Cannot test Loki connection - python-logging-loki not available")
        return False

    loki_url = url or settings.LOKI_URL

    try:
        # Create a test handler
        handler = create_loki_handler(loki_url)
        if not handler:
            return False

        # Create a test logger
        test_logger = logging.getLogger("loki_test")
        test_logger.setLevel(logging.INFO)
        test_logger.addHandler(handler)

        # Send a test log
        test_logger.info("Loki connection test", extra={"test": True})

        print(f"✅ Loki connection test successful: {loki_url}")
        return True

    except Exception as e:
        print(f"❌ Loki connection test failed: {e}")
        return False
