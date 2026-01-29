"""
Unit tests for the worker async runtime (Strategy B1).

Validates that async_runtime provides a dedicated event loop and run()
for Celery tasks without requiring a real database in tests.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch


def test_in_worker_loop_thread_false_without_loop():
    """When the worker loop has never been started, in_worker_loop_thread() is False."""
    from personal_assistant.workers import async_runtime

    # Reset module state so no loop is running (fresh import or ensure no prior _ensure_loop)
    with patch.object(async_runtime, "_loop", None), patch.object(
        async_runtime, "_loop_thread", None
    ):
        assert async_runtime.in_worker_loop_thread() is False


def test_run_executes_coroutine_on_worker_loop():
    """run(coro) executes the coroutine on the worker's event loop and returns the result."""
    from personal_assistant.workers import async_runtime

    mock_engine = MagicMock()
    mock_session_factory = MagicMock()

    with patch(
        "personal_assistant.workers.async_runtime.create_async_engine",
        return_value=mock_engine,
    ), patch(
        "personal_assistant.workers.async_runtime.async_sessionmaker",
        return_value=mock_session_factory,
    ):
        async def returns_42():
            return 42

        result = async_runtime.run(returns_42(), timeout=5.0)
        assert result == 42


def test_run_executes_async_sleep():
    """run() can run coroutines that use asyncio.sleep (validates loop is used)."""
    from personal_assistant.workers import async_runtime

    mock_engine = MagicMock()
    mock_session_factory = MagicMock()

    with patch(
        "personal_assistant.workers.async_runtime.create_async_engine",
        return_value=mock_engine,
    ), patch(
        "personal_assistant.workers.async_runtime.async_sessionmaker",
        return_value=mock_session_factory,
    ):
        async def sleep_and_return():
            await asyncio.sleep(0.01)
            return "ok"

        result = async_runtime.run(sleep_and_return(), timeout=5.0)
        assert result == "ok"


def test_in_worker_loop_thread_true_inside_run():
    """While a coro is running via run(), the loop thread sees in_worker_loop_thread() True."""
    from personal_assistant.workers import async_runtime

    mock_engine = MagicMock()
    mock_session_factory = MagicMock()
    seen_in_worker = []

    with patch(
        "personal_assistant.workers.async_runtime.create_async_engine",
        return_value=mock_engine,
    ), patch(
        "personal_assistant.workers.async_runtime.async_sessionmaker",
        return_value=mock_session_factory,
    ):

        async def check_thread():
            seen_in_worker.append(async_runtime.in_worker_loop_thread())
            return 1

        result = async_runtime.run(check_thread(), timeout=5.0)
        assert result == 1
        assert seen_in_worker == [True]


def test_get_worker_session_factory_after_run():
    """After run() has started the loop, get_worker_session_factory() returns a factory."""
    from personal_assistant.workers import async_runtime

    mock_engine = MagicMock()
    mock_session_factory = MagicMock()

    with patch(
        "personal_assistant.workers.async_runtime.create_async_engine",
        return_value=mock_engine,
    ), patch(
        "personal_assistant.workers.async_runtime.async_sessionmaker",
        return_value=mock_session_factory,
    ):
        async def noop():
            return None

        async_runtime.run(noop(), timeout=5.0)
        factory = async_runtime.get_worker_session_factory()
        assert factory is not None
