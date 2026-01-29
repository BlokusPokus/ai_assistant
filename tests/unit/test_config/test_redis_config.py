"""
Unit tests for Redis configuration (Task 102) and Redis client improvements (Task 103).

Task 102: REDIS_URL, derived session URL, same host, no hardcoded localhost, health config.
Task 103: Pool/timeout settings, lazy init (no connection at import), get_celery_redis, singleton getters.

These tests describe the desired behavior before implementation:
- REDIS_URL in settings
- Session Redis URL derived from REDIS_URL + SESSION_REDIS_DB
- Celery and session use same Redis host
- Session URL not hardcoded to localhost when REDIS_URL is set
- Health checks use same config as runtime

Run with: pytest tests/unit/test_config/test_redis_config.py -v
Expect failures (Red) until Phase 2 implementation.
"""

import importlib

import pytest


def test_redis_url_in_settings():
    """Settings must expose REDIS_URL for a single source of truth."""
    from personal_assistant.config.settings import settings

    assert hasattr(settings, "REDIS_URL"), "settings should have REDIS_URL"
    assert settings.REDIS_URL, "REDIS_URL should be non-empty"
    assert "redis" in settings.REDIS_URL.lower(), "REDIS_URL should be a Redis URL"


def test_session_redis_url_derived_from_redis_url_and_db():
    """Session Redis URL must be derived from base REDIS_URL and SESSION_REDIS_DB."""
    from personal_assistant.config.redis import get_session_redis_url

    # Same host/port, different DB index
    base = "redis://redis:6379/0"
    session_url = get_session_redis_url(base, 1)
    assert session_url == "redis://redis:6379/1", (
        "session URL should be base URL with DB index 1"
    )

    # With password
    base_with_pass = "redis://:secret@redis:6379/0"
    session_url_2 = get_session_redis_url(base_with_pass, 2)
    assert "/2" in session_url_2 and "redis:6379" in session_url_2
    assert "secret" in session_url_2 or ":secret@" in session_url_2


def test_celery_and_session_use_same_redis_host():
    """Celery broker URL and session Redis URL must refer to the same host."""
    from urllib.parse import urlparse

    from personal_assistant.celery.config import CELERY_BROKER_URL
    from personal_assistant.config.redis import get_session_redis_url
    from personal_assistant.config.settings import settings

    base = getattr(settings, "REDIS_URL", None) or settings.CELERY_BROKER_URL
    session_url = get_session_redis_url(base, settings.SESSION_REDIS_DB)

    broker_host = urlparse(CELERY_BROKER_URL).hostname or "localhost"
    session_host = urlparse(session_url).hostname or "localhost"

    assert broker_host == session_host, (
        f"Celery broker host ({broker_host}) and session Redis host ({session_host}) must match"
    )


def test_session_redis_url_not_hardcoded_localhost():
    """When REDIS_URL is not localhost, session URL must not use localhost."""
    from personal_assistant.config.redis import get_session_redis_url

    base = "redis://redis:6379/0"
    session_url = get_session_redis_url(base, 1)

    assert "localhost" not in session_url, (
        "session URL must not be hardcoded to localhost when base is not localhost"
    )
    assert "redis" in session_url, "session URL should use host from base URL"


def test_redis_health_checks_use_same_config():
    """Session Redis URL must be derived from settings (same config as runtime)."""
    from urllib.parse import urlparse

    from personal_assistant.config.redis import get_session_redis_url
    from personal_assistant.config.settings import settings

    base = getattr(settings, "REDIS_URL", None) or getattr(
        settings, "CELERY_BROKER_URL", "redis://localhost:6379/0"
    )
    session_url = get_session_redis_url(base, settings.SESSION_REDIS_DB)

    base_host = urlparse(base).hostname or "localhost"
    session_host = urlparse(session_url).hostname or "localhost"

    assert base_host == session_host, (
        "session URL must use same host as base (health checks use same config)"
    )


# -----------------------------------------------------------------------------
# Task 103 – Redis client improvements (pooling knobs, lazy init)
# -----------------------------------------------------------------------------


def test_redis_pool_timeout_settings_exist():
    """Settings must expose REDIS_SOCKET_CONNECT_TIMEOUT and REDIS_SOCKET_TIMEOUT (Task 103)."""
    from personal_assistant.config.settings import settings

    assert hasattr(settings, "REDIS_SOCKET_CONNECT_TIMEOUT"), (
        "settings should have REDIS_SOCKET_CONNECT_TIMEOUT"
    )
    assert hasattr(settings, "REDIS_SOCKET_TIMEOUT"), (
        "settings should have REDIS_SOCKET_TIMEOUT"
    )
    assert isinstance(settings.REDIS_SOCKET_CONNECT_TIMEOUT, (int, float)), (
        "REDIS_SOCKET_CONNECT_TIMEOUT should be numeric"
    )
    assert isinstance(settings.REDIS_SOCKET_TIMEOUT, (int, float)), (
        "REDIS_SOCKET_TIMEOUT should be numeric"
    )
    assert settings.REDIS_SOCKET_CONNECT_TIMEOUT >= 0
    assert settings.REDIS_SOCKET_TIMEOUT >= 0


def test_redis_clients_use_pool_timeout_from_settings():
    """Session Redis client must use timeout values from settings (Task 103)."""
    from personal_assistant.config.redis import get_session_redis
    from personal_assistant.config.settings import settings

    client = get_session_redis()
    kwargs = client.connection_pool.connection_kwargs
    assert kwargs.get("socket_connect_timeout") == settings.REDIS_SOCKET_CONNECT_TIMEOUT, (
        "client socket_connect_timeout should match settings"
    )
    assert kwargs.get("socket_timeout") == settings.REDIS_SOCKET_TIMEOUT, (
        "client socket_timeout should match settings"
    )


def test_no_redis_connection_at_import():
    """Importing config.redis must not call Redis.from_url (Task 103 – lazy init)."""
    from unittest.mock import patch

    import personal_assistant.config.redis as redis_mod

    # Patch sync and async from_url, then reload; with lazy init, from_url is not called at import
    with patch("redis.Redis.from_url") as m_sync:
        with patch("redis.asyncio.Redis.from_url", create=True) as m_async:
            importlib.reload(redis_mod)
            assert m_sync.call_count == 0, (
                "Redis.from_url must not be called at import (lazy init)"
            )
            assert m_async.call_count == 0, (
                "redis.asyncio.Redis.from_url must not be called at import (lazy init)"
            )
    # Restore real clients for subsequent tests
    importlib.reload(redis_mod)


def test_get_celery_redis_exists_and_returns_client():
    """get_celery_redis() must exist and return a Redis client (Task 103)."""
    from personal_assistant.config.redis import get_celery_redis

    client = get_celery_redis()
    assert client is not None, "get_celery_redis() should return a client"
    assert hasattr(client, "ping"), "client should have ping method"


def test_getters_return_same_instance_on_repeated_calls():
    """get_celery_redis() and get_session_redis() must return same instance on repeated calls (Task 103)."""
    from personal_assistant.config.redis import (
        get_async_session_redis,
        get_celery_redis,
        get_session_redis,
    )

    assert get_celery_redis() is get_celery_redis(), (
        "get_celery_redis() should return same instance (singleton)"
    )
    assert get_session_redis() is get_session_redis(), (
        "get_session_redis() should return same instance (singleton)"
    )
    async_client = get_async_session_redis()
    if async_client is not None:
        assert get_async_session_redis() is get_async_session_redis(), (
            "get_async_session_redis() should return same instance (singleton)"
        )
