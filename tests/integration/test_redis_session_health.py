"""
Integration tests for Redis session storage and health (Task 103).

When Redis is available, SessionService can create/retrieve sessions and health checks return True.
Tests are skipped when Redis is not available (e.g. no Redis server running).
Run with: pytest tests/integration/test_redis_session_health.py -v -m integration
"""

import pytest


def _redis_available():
    """Return True if Redis is reachable; used to skip tests when Redis is down. Uses sync client only to avoid binding async client to a short-lived loop."""
    try:
        from personal_assistant.config.redis import get_session_redis

        get_session_redis().ping()
        return True
    except Exception:
        return False


def _reset_async_redis_cache():
    """Reset lazy async client cache so next get_async_session_redis() creates a client in the current event loop."""
    import personal_assistant.config.redis as redis_mod

    redis_mod._async_session_redis = None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_session_create_and_retrieve_with_redis():
    """When Redis is available, SessionService can create a session and retrieve it (Task 103)."""
    if not _redis_available():
        pytest.skip("Redis not available")

    _reset_async_redis_cache()
    from personal_assistant.auth.session_service import SessionService
    from personal_assistant.config.redis import get_async_session_redis

    redis_client = get_async_session_redis()
    assert redis_client is not None
    service = SessionService(redis_client)

    device_info = {"device": "test", "browser": "pytest"}
    session_id = await service.create_session(user_id=1, device_info=device_info)
    assert session_id
    data = await service.get_session(session_id)
    assert data is not None
    assert data.get("user_id") == 1
    assert data.get("device_info") == device_info
    await service.invalidate_session(session_id)


@pytest.mark.integration
def test_redis_health_sync_when_redis_available():
    """When Redis is available, check_redis_health() returns True (Task 103)."""
    if not _redis_available():
        pytest.skip("Redis not available")

    from personal_assistant.config.redis import check_redis_health

    assert check_redis_health() is True, "sync health check should return True when Redis is up"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_health_async_when_redis_available():
    """When Redis is available, check_async_redis_health() returns True (Task 103)."""
    if not _redis_available():
        pytest.skip("Redis not available")

    _reset_async_redis_cache()
    from personal_assistant.config.redis import check_async_redis_health

    async_ok = await check_async_redis_health()
    assert async_ok is True, "async health check should return True when Redis is up"
