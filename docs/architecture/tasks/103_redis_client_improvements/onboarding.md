# Task 103 Onboarding: Redis Client Improvements (Lazy Init, Pooling, Integration Tests)

## Context and goal

This task follows **Task 102 (Redis implementation improvement)**. Task 102 established a single source of truth for Redis URL, derived session URL from `REDIS_URL` + `SESSION_REDIS_DB`, and aligned Celery with the same config. **Task 103** improves the **client layer** only: how and when clients are created, how pools are configured, and how we test against a real Redis.

**Goal:**

1. **Lazy or factory-based client creation** — Avoid creating Redis clients at import time so tests can patch or set env before any connection, and so multi-environment usage is explicit.
2. **Pooling knobs** — Make connection pool size and socket timeouts configurable via settings/env and use them when building clients.
3. **Integration tests** — Add tests that run the app with a real (or test) Redis and verify session create/get and health; skip when Redis is unavailable.

Business logic (SessionService, Celery tasks) and URL derivation from Task 102 are **out of scope**.

---

## Implemented behavior (Task 103 completed)

- **Lazy init:** Redis clients are **not** created at import time. Importing `personal_assistant.config.redis` only computes `_session_redis_url` (no connection). The first call to `get_celery_redis()`, `get_session_redis()`, or `get_async_session_redis()` creates the client from settings and caches it (lazy singletons).
- **Getters:** `get_celery_redis()` (new), `get_session_redis()`, and `get_async_session_redis()` return the same instance on repeated calls. `get_async_session_redis()` returns `None` if `redis.asyncio` is not available (uses `_ASYNC_UNAVAILABLE` sentinel to avoid retrying ImportError every call).
- **Pool/timeout settings:** `settings.REDIS_SOCKET_CONNECT_TIMEOUT`, `settings.REDIS_SOCKET_TIMEOUT`, and `settings.REDIS_MAX_CONNECTIONS` (optional) are used when building clients via `_redis_client_kwargs()`. Documented in `config/env.example`.
- **Health checks:** `check_redis_health()` and `check_async_redis_health()` use the getters, so they use the same clients as the rest of the app.
- **Integration tests:** `tests/integration/test_redis_session_health.py` — session create/retrieve, sync health, async health. Marked `@pytest.mark.integration`. Skip when Redis is unavailable (sync ping used for availability check). Run with: `pytest tests/integration/test_redis_session_health.py -v -m integration`.

---

## Previous state (pre–Task 103, post–Task 102)

### Client creation (`config/redis.py`)

- **At import time:** The module built `celery_redis`, `session_redis`, and `async_session_redis` via `redis.Redis.from_url()` at module load.
- **Timeouts:** Hardcoded `socket_connect_timeout=5`, `socket_timeout=5`; no configurable pool size.
- **Getters:** Returned module-level instances; no `get_celery_redis()`.

### Implications (addressed by Task 103)

- Import triggered client creation; now fixed with lazy init.
- Pool/timeout not tunable; now configurable via settings.
- No integration test; now `test_redis_session_health.py` with session + health, skip when Redis down.

---

## What to implement

### 1. Lazy or factory-based client creation

**Options:**

- **Option A — Lazy singletons:** Replace module-level `celery_redis`, `session_redis`, `async_session_redis` with getter functions (or cached properties) that create the client on first call and reuse it afterward. Callers keep using `get_session_redis()`, `get_async_session_redis()` and a new `get_celery_redis()`; health checks and SessionService continue to use the same clients.
- **Option B — Factory:** Provide functions like `create_session_redis()`, `create_celery_redis()` that return new clients each time (or from a pool), and have a single place (e.g. FastAPI app state or a small registry) hold the “app” instances. This is more flexible but may require more call-site changes.

**Recommendation:** Start with **Option A** (lazy singletons) to minimize call-site churn. Ensure:
- No Redis connection is made when the module is imported.
- First call to `get_celery_redis()`, `get_session_redis()`, or `get_async_session_redis()` builds the client from current settings and caches it.
- Health checks use these getters so they still see the same clients as the rest of the app.

**Files:** `src/personal_assistant/config/redis.py` (and any code that today imports `celery_redis` directly; switch to `get_celery_redis()` if you introduce a getter).

### 2. Pooling knobs

- **Settings:** Add optional settings, for example:
  - `REDIS_SOCKET_CONNECT_TIMEOUT` (default 5)
  - `REDIS_SOCKET_TIMEOUT` (default 5)
  - `REDIS_MAX_CONNECTIONS` (default from redis-py, or e.g. 50 for the connection pool)
- **Usage:** When building sync/async Redis clients (in the lazy getters or factory), pass these into `from_url()` or the connection pool. redis-py supports `socket_connect_timeout`, `socket_timeout`, and `max_connections` (on the connection pool).
- **Documentation:** Document in `config/env.example` and in this task’s README/onboarding.

**Files:** `src/personal_assistant/config/settings.py`, `src/personal_assistant/config/redis.py`, `config/env.example`.

### 3. Integration tests

- **Goal:** Verify that with a real Redis (or a test Redis), the app can:
  - Create and retrieve a session via SessionService (using the Redis client from config).
  - Return healthy status from health checks that use the same Redis clients.
- **Placement:** e.g. `tests/integration/test_redis_session.py` or under `tests/e2e/`; follow existing project layout for integration tests.
- **Redis availability:** Use a fixed URL (e.g. `REDIS_URL=redis://localhost:6379/0` or from env). Skip the test(s) if Redis is unreachable (e.g. try `ping()` once and `pytest.skip()` if it fails), or use a marker like `@pytest.mark.integration` and document that integration tests require Redis.
- **Scope:** No need to test Celery task execution in this task; focus on session + health. Optional: use testcontainers or a dedicated test Redis DB index to avoid polluting dev data.

**Files:** New test module(s) under `tests/integration/` (or as per project convention); possibly `pytest.ini` or `conftest.py` for skip/marker logic.

---

## Implementation order (suggested)

1. **Pooling knobs** — Add settings and pass them into existing client construction; keep module-level creation for now. Ensures new options are used and documented.
2. **Lazy init** — Refactor to lazy singletons (getters that create on first use). Update any direct references to `celery_redis` to use `get_celery_redis()` (or equivalent). Run existing unit tests and Celery/Redis tests to confirm nothing breaks.
3. **Integration tests** — Add integration test(s) for session + health; document how to run them and when they are skipped.

---

## Key files reference

| Path | Role |
|------|------|
| `src/personal_assistant/config/redis.py` | Lazy getters (`get_celery_redis`, `get_session_redis`, `get_async_session_redis`), `_redis_client_kwargs()`, health checks. No connection at import. |
| `src/personal_assistant/config/settings.py` | `REDIS_SOCKET_CONNECT_TIMEOUT`, `REDIS_SOCKET_TIMEOUT`, `REDIS_MAX_CONNECTIONS` (Task 103). |
| `src/personal_assistant/celery/config.py` | Celery broker/backend; no change. |
| `src/personal_assistant/auth/session_service.py` | Consumes async Redis client via getter; unchanged. |
| `src/apps/fastapi_app/routes/sessions.py` | Uses `get_async_session_redis()`; unchanged. |
| `config/env.example` | Documents REDIS_SOCKET_CONNECT_TIMEOUT, REDIS_SOCKET_TIMEOUT, REDIS_MAX_CONNECTIONS. |
| `tests/unit/test_config/test_redis_config.py` | Unit tests for Task 102 + Task 103 (pool/timeout, lazy init, getters). |
| `tests/integration/test_redis_session_health.py` | Integration tests: session create/retrieve, sync and async health; skip when Redis unavailable. |
| `tests/unit/test_workers/test_celery_entrypoint.py`, `test_queue_routing.py` | Celery unit tests; unchanged by Task 103. |

---

## References

- Task 102: `docs/architecture/tasks/102_redis_implementation_improvement/` — single source of truth, derived session URL, Celery alignment.
- redis-py connection: https://redis.readthedocs.io/en/stable/connections.html (pool, timeouts).
- Project integration test patterns: see `tests/integration/` or `tests/e2e/` for existing structure and markers.
