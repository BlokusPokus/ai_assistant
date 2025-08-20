"""
Database session management with enhanced configuration.

This module provides backward compatibility while using the new enhanced
database configuration with connection pooling.
"""

import sys
from personal_assistant.config.database import (
    get_session,
    get_session_context,
    db_config
)

# Re-export for backward compatibility
__all__ = [
    "get_session",
    "get_session_context",
    "db_config"
]

# Lazy initialization of engine and session factory


def _get_engine():
    """Get the database engine, initializing if necessary."""
    if db_config.engine is None:
        # This will trigger initialization when first accessed
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, can't initialize here
                return None
            else:
                # We can initialize synchronously
                loop.run_until_complete(db_config._ensure_initialized())
        except RuntimeError:
            # No event loop, can't initialize
            return None
    return db_config.engine


def _get_session_factory():
    """Get the session factory, initializing if necessary."""
    if db_config.session_factory is None:
        # Try to initialize the database config
        engine = _get_engine()
        if engine is None:
            return None
    return db_config.session_factory

# Export the engine and session factory with lazy initialization


def engine():
    return _get_engine()


def AsyncSessionLocal():
    return _get_session_factory()


# Add these to the module's __dict__ for proper attribute access
sys.modules[__name__].engine = engine
sys.modules[__name__].AsyncSessionLocal = AsyncSessionLocal
