"""
Enhanced database configuration with connection pooling, health monitoring, and optimization.

This module provides:
- Connection pooling configuration
- Health check endpoints
- Performance monitoring
- Connection pool statistics
- Environment-based configuration
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

logger = logging.getLogger(__name__)


@dataclass
class PoolStats:
    """Connection pool statistics."""

    pool_size: int
    max_overflow: int
    checked_in: int
    checked_out: int
    overflow: int
    invalid: int
    total_connections: int
    utilization_percentage: float
    last_updated: datetime


class DatabaseConfig:
    """Enhanced database configuration with connection pooling and monitoring."""

    def __init__(self, auto_initialize: bool = True):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self.pool_stats: Optional[PoolStats] = None
        self.health_status: str = "unknown"
        self.last_health_check: Optional[datetime] = None
        self.performance_metrics: Dict[str, Any] = {}
        self._initialized = False

        # Connection pool configuration
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "30"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

        # Performance thresholds
        self.slow_query_threshold = float(
            os.getenv("DB_SLOW_QUERY_THRESHOLD", "0.1")
        )  # 100ms
        self.max_connection_wait = float(
            os.getenv("DB_MAX_CONNECTION_WAIT", "5.0")
        )  # 5 seconds

        # Health check configuration
        self.health_check_interval = int(
            os.getenv("DB_HEALTH_CHECK_INTERVAL", "30")
        )  # 30 seconds

        # Initialize the database if auto_initialize is True
        if auto_initialize:
            self._initialize_database()

    def _initialize_database(self):
        """Initialize the database engine with connection pooling."""
        try:
            database_url = (
                os.getenv("REAL_DB_URL")
                or os.getenv("DATABASE_URL")
                or "postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
            )

            # Ensure we're using an async driver
            if not database_url.startswith(
                ("postgresql+asyncpg://", "postgresql+psycopg://")
            ):
                # Convert to async driver if needed
                if database_url.startswith("postgresql://"):
                    database_url = database_url.replace(
                        "postgresql://", "postgresql+asyncpg://", 1
                    )
                elif database_url.startswith("postgres://"):
                    database_url = database_url.replace(
                        "postgres://", "postgresql+asyncpg://", 1
                    )

            # Create async engine with connection pooling
            self.engine = create_async_engine(
                database_url,
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
                poolclass=AsyncAdaptedQueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=self.pool_pre_ping,
                connect_args={
                    "server_settings": {
                        "application_name": "personal_assistant",
                        "jit": "off",  # Disable JIT for better performance
                        "work_mem": "4MB",  # Optimize work memory
                        "maintenance_work_mem": "64MB",  # Optimize maintenance
                    }
                },
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            # Set up connection pool event listeners
            self._setup_pool_event_listeners()

            # Start health monitoring
            asyncio.create_task(self._start_health_monitoring())

            self._initialized = True
            logger.info(
                "Database engine initialized successfully with connection pooling"
            )

        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            self.health_status = "error"
            # Don't raise here, just log the error
            logger.warning("Database initialization failed, will retry on first use")

    def _setup_pool_event_listeners(self):
        """Set up event listeners for connection pool monitoring."""
        if not self.engine:
            return

        # For async engines, we need to use the sync engine for event listeners
        sync_engine = self.engine.sync_engine

        @event.listens_for(sync_engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Log when a new connection is created."""
            logger.debug("New database connection created")

        @event.listens_for(sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log when a connection is checked out."""
            logger.debug("Database connection checked out")

        @event.listens_for(sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log when a connection is checked in."""
            logger.debug("Database connection checked in")

        @event.listens_for(sync_engine, "close")
        def receive_close(dbapi_connection, connection_record):
            """Log when a connection is closed."""
            logger.debug("Database connection closed")

    async def _ensure_initialized(self):
        """Ensure the database is initialized before use."""
        if not self._initialized or not self.engine:
            try:
                self._initialize_database()
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                raise RuntimeError(f"Database not initialized: {e}")

    async def get_session(self) -> AsyncSession:
        """Get a database session from the pool."""
        await self._ensure_initialized()

        start_time = time.time()
        try:
            if self.session_factory is None:
                raise RuntimeError("Database not initialized")

            session = self.session_factory()

            # Track connection wait time
            wait_time = time.time() - start_time
            if wait_time > self.max_connection_wait:
                logger.warning(f"Slow connection acquisition: {wait_time:.3f}s")

            return session  # type: ignore

        except Exception as e:
            logger.error(f"Failed to get database session: {e}")
            raise

    @asynccontextmanager
    async def get_session_context(self):
        """Context manager for database sessions."""
        session = await self.get_session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_pool_stats(self) -> PoolStats:
        """Get current connection pool statistics."""
        await self._ensure_initialized()

        if not self.engine:
            return PoolStats(
                pool_size=0,
                max_overflow=0,
                checked_in=0,
                checked_out=0,
                overflow=0,
                invalid=0,
                total_connections=0,
                utilization_percentage=0.0,
                last_updated=datetime.now(),
            )

        pool = self.engine.pool

        # Get pool statistics - handle both sync and async pools
        checked_in = getattr(pool, "checkedin", lambda: 0)()
        checked_out = getattr(pool, "checkedout", lambda: 0)()
        overflow = getattr(pool, "overflow", lambda: 0)()

        # Handle invalid method availability for different pool types
        try:
            invalid = getattr(pool, "invalid", lambda: 0)()
        except AttributeError:
            # AsyncAdaptedQueuePool doesn't have invalid() method
            invalid = 0

        total_connections = checked_in + checked_out + overflow
        utilization_percentage = (
            (checked_out / (self.pool_size + self.max_overflow)) * 100
            if (self.pool_size + self.max_overflow) > 0
            else 0
        )

        self.pool_stats = PoolStats(
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            checked_in=checked_in,
            checked_out=checked_out,
            overflow=overflow,
            invalid=invalid,
            total_connections=total_connections,
            utilization_percentage=utilization_percentage,
            last_updated=datetime.now(),
        )

        return self.pool_stats

    async def check_health(self) -> Dict[str, Any]:
        """Check database health status."""
        try:
            await self._ensure_initialized()

            start_time = time.time()

            # Test connection
            async with self.get_session_context() as session:
                from sqlalchemy import text

                await session.execute(text("SELECT 1"))

            response_time = time.time() - start_time

            # Update health status
            if response_time < self.slow_query_threshold:
                self.health_status = "healthy"
            elif response_time < self.slow_query_threshold * 2:
                self.health_status = "degraded"
            else:
                self.health_status = "unhealthy"

            self.last_health_check = datetime.now()

            # Get pool stats
            pool_stats = await self.get_pool_stats()

            health_data = {
                "status": self.health_status,
                "response_time": response_time,
                "last_check": self.last_health_check.isoformat(),
                "pool_stats": {
                    "pool_size": pool_stats.pool_size,
                    "max_overflow": pool_stats.max_overflow,
                    "checked_in": pool_stats.checked_in,
                    "checked_out": pool_stats.checked_out,
                    "overflow": pool_stats.overflow,
                    "invalid": pool_stats.invalid,
                    "total_connections": pool_stats.total_connections,
                    "utilization_percentage": round(
                        pool_stats.utilization_percentage, 2
                    ),
                },
                "performance": {
                    "slow_query_threshold": self.slow_query_threshold,
                    "max_connection_wait": self.max_connection_wait,
                    "pool_timeout": self.pool_timeout,
                    "pool_recycle": self.pool_recycle,
                },
            }

            # Update performance metrics
            self.performance_metrics = {
                "response_time": response_time,
                "health_status": self.health_status,
                "pool_utilization": pool_stats.utilization_percentage,
                "timestamp": datetime.now().isoformat(),
            }

            return health_data

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            self.health_status = "error"
            self.last_health_check = datetime.now()

            return {
                "status": "error",
                "error": str(e),
                "last_check": self.last_health_check.isoformat(),
                "pool_stats": None,
                "performance": None,
            }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        if not self.performance_metrics:
            await self.check_health()

        return {
            "current_metrics": self.performance_metrics,
            "pool_configuration": {
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                "pool_timeout": self.pool_timeout,
                "pool_recycle": self.pool_recycle,
                "pool_pre_ping": self.pool_pre_ping,
            },
            "thresholds": {
                "slow_query_threshold": self.slow_query_threshold,
                "max_connection_wait": self.max_connection_wait,
            },
        }

    async def _start_health_monitoring(self):
        """Start background health monitoring."""
        while True:
            try:
                await self.check_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)  # Shorter interval on error

    async def close(self):
        """Close the database engine and cleanup."""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database engine closed")


# Global database configuration instance - don't auto-initialize to avoid import issues
db_config = DatabaseConfig(auto_initialize=False)


# Backward compatibility functions
async def get_session() -> AsyncSession:
    """Get a database session (backward compatibility)."""
    return await db_config.get_session()


async def get_session_context():
    """Get a database session context (backward compatibility)."""
    return db_config.get_session_context()


# Export the engine for backward compatibility - these will be None until initialized
engine = None
AsyncSessionLocal = None
