"""
Redis configuration for the personal assistant framework.

This module provides Redis client configurations for:
- Celery broker and result backend
- Session management
- Health checks and monitoring
"""

from typing import Optional

import redis

from .settings import settings

# Celery Redis (existing configuration)
celery_redis = redis.Redis.from_url(
    settings.CELERY_BROKER_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)

# Session Redis (new configuration)
session_redis = redis.Redis.from_url(
    f"redis://localhost:6379/{settings.SESSION_REDIS_DB}",
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)

# Async Redis for session management (if using async operations)
try:
    import redis.asyncio as async_redis

    async_session_redis = async_redis.Redis.from_url(
        f"redis://localhost:6379/{settings.SESSION_REDIS_DB}",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )
except ImportError:
    # Fallback if async redis is not available
    async_session_redis = None


def check_redis_health() -> bool:
    """
    Check Redis health for both Celery and Session instances.

    Returns:
        bool: True if both Redis instances are healthy
    """
    try:
        celery_redis.ping()
        session_redis.ping()
        return True
    except Exception:
        return False


async def check_async_redis_health() -> bool:
    """
    Async check Redis health for session management.

    Returns:
        bool: True if async Redis is healthy
    """
    if async_session_redis is None:
        return False

    try:
        await async_session_redis.ping()
        return True
    except Exception:
        return False


def get_session_redis():
    """
    Get the appropriate Redis client for session management.

    Returns:
        Redis client (sync or async based on context)
    """
    return session_redis


def get_async_session_redis():
    """
    Get the async Redis client for session management.

    Returns:
        AsyncRedis client or None if not available
    """
    return async_session_redis
