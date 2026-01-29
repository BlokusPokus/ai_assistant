"""
Redis configuration for the personal assistant framework.

This module provides Redis client configurations for:
- Celery broker and result backend
- Session management
- Health checks and monitoring

Session Redis URL is derived from REDIS_URL + SESSION_REDIS_DB (Task 102).
Clients are created lazily on first getter call (Task 103).
"""

from urllib.parse import urlparse, urlunparse

import redis

from .settings import settings


def get_session_redis_url(base_url: str, db_index: int) -> str:
    """
    Derive session Redis URL from a base Redis URL and DB index.

    Same scheme/host/port/password as base_url, with path set to /{db_index}.
    """
    parsed = urlparse(base_url)
    # Replace path (e.g. /0) with /{db_index}
    new = parsed._replace(path=f"/{db_index}")
    return urlunparse(new)


# Session Redis URL derived from REDIS_URL + SESSION_REDIS_DB (no connection at import)
_session_redis_url = get_session_redis_url(settings.REDIS_URL, settings.SESSION_REDIS_DB)

# Lazy singletons (Task 103): created on first getter call
_celery_redis = None
_session_redis = None
_async_session_redis = None


def _redis_client_kwargs():
    """Common kwargs for Redis clients from settings (Task 103)."""
    return {
        "decode_responses": True,
        "socket_connect_timeout": settings.REDIS_SOCKET_CONNECT_TIMEOUT,
        "socket_timeout": settings.REDIS_SOCKET_TIMEOUT,
        "retry_on_timeout": True,
    }


def get_celery_redis():
    """
    Get the Redis client for Celery broker/result backend (lazy singleton).

    Returns:
        Redis client for Celery health checks and broker access.
    """
    global _celery_redis
    if _celery_redis is None:
        _celery_redis = redis.Redis.from_url(
            settings.CELERY_BROKER_URL,
            **_redis_client_kwargs(),
        )
    return _celery_redis


def get_session_redis():
    """
    Get the sync Redis client for session management (lazy singleton).

    Returns:
        Redis client for session storage.
    """
    global _session_redis
    if _session_redis is None:
        _session_redis = redis.Redis.from_url(
            _session_redis_url,
            **_redis_client_kwargs(),
        )
    return _session_redis


# Sentinel when redis.asyncio is not available (avoid retrying ImportError every call)
_ASYNC_UNAVAILABLE = object()


def get_async_session_redis():
    """
    Get the async Redis client for session management (lazy singleton).

    Returns:
        AsyncRedis client or None if redis.asyncio is not available.
    """
    global _async_session_redis
    if _async_session_redis is None:
        try:
            import redis.asyncio as async_redis

            _async_session_redis = async_redis.Redis.from_url(
                _session_redis_url,
                **_redis_client_kwargs(),
            )
        except ImportError:
            _async_session_redis = _ASYNC_UNAVAILABLE
    return None if _async_session_redis is _ASYNC_UNAVAILABLE else _async_session_redis


def check_redis_health() -> bool:
    """
    Check Redis health for both Celery and Session instances.

    Returns:
        bool: True if both Redis instances are healthy
    """
    try:
        get_celery_redis().ping()
        get_session_redis().ping()
        return True
    except Exception:
        return False


async def check_async_redis_health() -> bool:
    """
    Async check Redis health for session management.

    Returns:
        bool: True if async Redis is healthy
    """
    client = get_async_session_redis()
    if client is None:
        return False

    try:
        await client.ping()
        return True
    except Exception:
        return False
