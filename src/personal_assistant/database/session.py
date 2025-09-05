"""
Database session management with enhanced configuration.

This module provides backward compatibility while using the new enhanced
database configuration with connection pooling.
"""

import logging
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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


# Create async engine function
def engine():
    """Get the database engine, creating if necessary."""
    if not hasattr(engine, "_engine"):
        engine._engine = create_async_engine(
            DATABASE_URL,
            echo=False,  # Re-enabled to see full SQL logs
        )
    return engine._engine


# Create async session factory
def _get_session_factory():
    """Get the session factory, creating if necessary."""
    if not hasattr(_get_session_factory, "_factory"):
        _get_session_factory._factory = async_sessionmaker(
            bind=engine(),
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _get_session_factory._factory


# For backward compatibility, create a callable that returns the factory
class AsyncSessionLocal:
    def __call__(self, *args, **kwargs):
        return _get_session_factory()(*args, **kwargs)

    def configure(self, **kwargs):
        return _get_session_factory().configure(**kwargs)

    @property
    def kw(self):
        return _get_session_factory().kw

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = _get_session_factory()()
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, "_session"):
            await self._session.close()


# Create an instance for backward compatibility
async_session_local = AsyncSessionLocal()

# Re-export for backward compatibility
__all__ = [
    "get_session",
    "get_session_context",
    "db_config",
    "AsyncSessionLocal",
    "async_session_local",
]

# Lazy initialization of engine and session factory


def _get_engine():
    """Get the database engine, initializing if necessary."""
    return engine()


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
        session = _get_session_factory()()
        try:
            yield session
        finally:
            await session.close()

    return _get_db


# Export the engine and session factory with lazy initialization


def get_engine():
    return _get_engine()


# Export the functions directly
__all__.extend(["engine", "AsyncSessionLocal", "get_db"])
