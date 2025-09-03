"""
Database session management with enhanced configuration.

This module provides backward compatibility while using the new enhanced
database configuration with connection pooling.
"""

import logging
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from personal_assistant.config.database import (
    db_config,
    get_session,
    get_session_context,
)

DATABASE_URL = (
    os.getenv("REAL_DB_URL")
    or "postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
)

# Set up logging
logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Re-enabled to see full SQL logs
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Re-export for backward compatibility
__all__ = ["get_session", "get_session_context", "db_config"]

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


async def _ensure_database_initialized():
    """Ensure database is initialized in async context."""
    if db_config.session_factory is None:
        await db_config._ensure_initialized()


def get_db():
    """
    FastAPI dependency function that returns an AsyncSession.

    This is a synchronous wrapper that FastAPI can use with Depends().
    It will be called for each request and return the session.
    """

    async def _get_db():
        return AsyncSessionLocal()

    return _get_db


# Export the engine and session factory with lazy initialization


def engine():
    return _get_engine()


# Add these to the module's __dict__ for proper attribute access
sys.modules[__name__].engine = engine
sys.modules[__name__].AsyncSessionLocal = AsyncSessionLocal
sys.modules[__name__].get_db = get_db
