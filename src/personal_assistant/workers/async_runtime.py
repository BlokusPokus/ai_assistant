"""
Worker async runtime (Strategy B1).

Provides a dedicated event loop and async DB engine per worker process so Celery
tasks can run async code (e.g. AI/SMS logic) without cross-loop or asyncpg
InterfaceError. Only used in worker processes; does not touch FastAPI's async DB.

See docs/architecture/tasks/101_async_worker_db_stabilization/IMPLEMENTATION_PLAN.md.
"""

import asyncio
import logging
import os
import threading
from typing import Any, Coroutine, TypeVar

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Same URL logic as database.session, without importing it (avoids cycles).
_WORKER_DATABASE_URL = (
    os.getenv("REAL_DB_URL")
    or os.getenv("DATABASE_URL")
    or "postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
)

_loop: asyncio.AbstractEventLoop | None = None
_loop_thread: threading.Thread | None = None
_worker_engine = None
_worker_session_factory = None
_lock = threading.Lock()


def _run_loop(ready: threading.Event) -> None:
    global _loop, _worker_engine, _worker_session_factory
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    try:
        _worker_engine = create_async_engine(
            _WORKER_DATABASE_URL,
            echo=False,
        )
        _worker_session_factory = async_sessionmaker(
            bind=_worker_engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    except Exception as e:
        logger.exception("Worker async runtime failed to create engine/session factory: %s", e)
        ready.set()
        return

    ready.set()
    try:
        _loop.run_forever()
    finally:
        _loop.run_until_complete(_loop.shutdown_asyncgens())
        if _worker_engine is not None:
            _loop.run_until_complete(_worker_engine.dispose())


def _ensure_loop() -> None:
    global _loop, _loop_thread
    with _lock:
        if _loop is not None and _loop_thread is not None and _loop_thread.is_alive():
            return
        ready = threading.Event()
        _loop_thread = threading.Thread(target=_run_loop, args=(ready,), daemon=True)
        _loop_thread.start()
        ready.wait(timeout=10.0)
        if _loop is None:
            raise RuntimeError("Worker async runtime loop did not start in time")


def in_worker_loop_thread() -> bool:
    """True when the current thread is the worker async loop thread (i.e. we're inside run(coro))."""
    global _loop_thread
    if _loop_thread is None:
        return False
    return threading.current_thread() is _loop_thread


def get_worker_session_factory():
    """Return the worker-only async session factory. Only valid when in_worker_loop_thread() is True."""
    _ensure_loop()
    if _worker_session_factory is None:
        raise RuntimeError("Worker session factory not initialized")
    return _worker_session_factory


def run(coro: Coroutine[Any, Any, T], timeout: float | None = 300.0) -> T:
    """
    Run a coroutine on the worker's dedicated event loop (from a sync Celery task).

    Uses run_coroutine_threadsafe. Do not call from async code; use this only from
    synchronous Celery task bodies.
    """
    _ensure_loop()
    if _loop is None:
        raise RuntimeError("Worker async runtime loop not available")
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result(timeout=timeout)
