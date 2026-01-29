# Task 103 – Redis Client Improvements (TDD Plan)

Goal: improve the Redis **client layer** with lazy init, configurable pooling, and integration tests. Task 102 (single source of truth, derived session URL) is unchanged.

Approach: **Test-Driven Development** — write tests that describe the desired behavior first, then implement until they pass.

All paths below are relative to the repo root.

---

## Phase 0 – Guardrails and baseline

1. **Guardrails**
   - Do **not** change:
     - SessionService key layout, TTL semantics, or concurrency rules.
     - Celery task logic or queue names.
     - URL derivation (Task 102): `REDIS_URL`, `get_session_redis_url()`, derived session URL.
   - Any new env var (e.g. `REDIS_SOCKET_CONNECT_TIMEOUT`) must be documented in `config/env.example` and task onboarding.

2. **Baseline**
   - Run existing Redis-related tests and note current state:
     ```bash
     python -m pytest tests/unit/test_config/test_redis_config.py tests/unit/test_workers/test_celery_entrypoint.py tests/unit/test_workers/test_queue_routing.py -v
     ```
   - Confirm `config/redis.py` creates `celery_redis`, `session_redis`, and `async_session_redis` at **import time** (module-level `from_url()` calls).

### Phase 0 – Completed

- **Guardrails:** Confirmed. No SessionService or Celery task logic changes; no Task 102 URL derivation changes (`REDIS_URL`, `get_session_redis_url()`, derived session URL remain). New env vars (e.g. `REDIS_SOCKET_CONNECT_TIMEOUT`) will be documented in `config/env.example` and task onboarding.
- **Baseline run:** Using project venv (`venv_personal_assistant`):
  - `tests/unit/test_config/test_redis_config.py`: 5 passed.
  - `tests/unit/test_workers/test_celery_entrypoint.py`: 4 passed.
  - `tests/unit/test_workers/test_queue_routing.py`: 13 passed.
  - **Total: 22 passed**, 4 warnings (unrelated: Pydantic/SQLAlchemy/Gemini).
- **Current behavior confirmed:**
  - `config/redis.py` creates clients at **import time**: `celery_redis`, `session_redis`, and `async_session_redis` are assigned via `redis.Redis.from_url()` / `async_redis.Redis.from_url()` at module load (lines 35–65). No getter is required for a connection to be created; importing `personal_assistant.config.redis` triggers `from_url()` immediately.
  - `_session_redis_url` is computed at module level from `settings.REDIS_URL` and `settings.SESSION_REDIS_DB` (no connection).
  - There is no `get_celery_redis()`; `check_redis_health()` uses module-level `celery_redis` and `session_redis` directly.
  - Only `get_session_redis()` and `get_async_session_redis()` exist; they return the module-level instances.

---

## Phase 1 – Write tests first (TDD Red)

Objective: add **new tests** that describe pooling knobs, lazy init, and integration behavior. Run tests and see them **fail** (or skip for integration) before implementing.

### 1.1 Unit tests for pooling knobs

**File:** `tests/unit/test_config/test_redis_config.py` (or new `tests/unit/test_config/test_redis_client.py`).

**Tests to add:**

1. **`test_redis_pool_timeout_settings_exist`**
   - After implementation, `settings` will have `REDIS_SOCKET_CONNECT_TIMEOUT`, `REDIS_SOCKET_TIMEOUT`, and optionally `REDIS_MAX_CONNECTIONS`.
   - Test: `from personal_assistant.config.settings import settings` then `assert hasattr(settings, "REDIS_SOCKET_CONNECT_TIMEOUT")`, same for `REDIS_SOCKET_TIMEOUT`; assert they are numeric (e.g. `>= 0`).
   - **Red:** Fails until these attributes are added to settings.

2. **`test_redis_clients_use_pool_timeout_from_settings`**
   - Clients built by the Redis config should use timeout values from settings (not hardcoded 5).
   - Test: patch `settings.REDIS_SOCKET_CONNECT_TIMEOUT = 10` and `settings.REDIS_SOCKET_TIMEOUT = 15`, then obtain the session client (e.g. via `get_session_redis()`), and assert the client’s connection kwargs or pool reflects 10 and 15 (e.g. `client.connection_pool.connection_kwargs.get("socket_connect_timeout") == 10` or equivalent for your redis-py version).
   - **Red:** Fails until clients are built using these settings instead of hardcoded 5.

### 1.2 Unit tests for lazy init

**Same file as 1.1.**

3. **`test_no_redis_connection_at_import`**
   - Importing `personal_assistant.config.redis` must **not** call `redis.Redis.from_url` (or create a connection).
   - Test: patch `redis.Redis.from_url` (and if needed `redis.asyncio.Redis.from_url`) with a mock; then `import importlib; import personal_assistant.config.redis as mod; importlib.reload(mod)` (or import the module fresh in a subprocess); assert `from_url.mock_called` is False (or call_count == 0). Avoid calling any getter in the test.
   - **Red:** Fails today because clients are created at import time.

4. **`test_get_celery_redis_exists_and_returns_client`**
   - There must be a callable `get_celery_redis()` that returns a Redis client (used for health checks).
   - Test: `from personal_assistant.config.redis import get_celery_redis; client = get_celery_redis(); assert client is not None` and optionally `assert hasattr(client, "ping")`.
   - **Red:** Fails until `get_celery_redis()` exists (today only `celery_redis` exists as a module-level variable).

5. **`test_getters_return_same_instance_on_repeated_calls`**
   - `get_celery_redis()` and `get_session_redis()` must return the **same** instance on repeated calls (lazy singletons).
   - Test: `assert get_celery_redis() is get_celery_redis()`; `assert get_session_redis() is get_session_redis()`. For async, `get_async_session_redis() is get_async_session_redis()` (if not None).
   - **Red:** Once `get_celery_redis()` exists, this may pass if you already cache; the “lazy” part is covered by test 3.

**Run and expect failures:**
```bash
python -m pytest tests/unit/test_config/test_redis_config.py -v -k "pool_timeout or no_redis_connection or get_celery or getters_return_same"
```
(Adjust `-k` to match the new test names.) Tests 1–4 should **fail** (settings missing, clients not using settings, connection at import, no get_celery_redis). Test 5 may fail until getters are lazy singletons. This is the TDD “Red” step.

### 1.3 Integration tests (session + health)

**File:** `tests/integration/test_redis_session_health.py` (create `tests/integration/` if needed; follow existing project layout).

6. **`test_session_create_and_retrieve_with_redis`** (mark with `@pytest.mark.integration`)
   - When Redis is available (e.g. `REDIS_URL` or default), create a session via SessionService and retrieve it; assert data matches.
   - At the start of the test (or in a fixture), try to connect (e.g. `get_async_session_redis().ping()` or equivalent); if it fails, `pytest.skip("Redis not available")`.
   - **Red:** Can fail if Redis is down (skip) or if refactor breaks the path; once implemented, **Green** when Redis is up.

7. **`test_redis_health_returns_true_when_redis_available`** (mark with `@pytest.mark.integration`)
   - When Redis is available, `check_redis_health()` and/or `check_async_redis_health()` return True.
   - Skip when Redis is not available (same as above).
   - **Red:** Skip when no Redis; **Green** when Redis is up and health uses the same clients.

**Run integration tests:**
```bash
python -m pytest tests/integration/test_redis_session_health.py -v -m integration
```
Expect: skipped when Redis unavailable, or pass when Redis is available. Unit tests above should still be **Red** until Phase 2.

### Phase 1 – Completed (Red)

- **Unit tests added** to `tests/unit/test_config/test_redis_config.py`:
  - `test_redis_pool_timeout_settings_exist` — **FAIL** (settings missing REDIS_SOCKET_CONNECT_TIMEOUT / REDIS_SOCKET_TIMEOUT).
  - `test_redis_clients_use_pool_timeout_from_settings` — **FAIL** (AttributeError: settings have no REDIS_SOCKET_*).
  - `test_no_redis_connection_at_import` — **FAIL** (Redis.from_url call_count 2 at import; expected 0 with lazy init).
  - `test_get_celery_redis_exists_and_returns_client` — **FAIL** (ImportError: get_celery_redis does not exist).
  - `test_getters_return_same_instance_on_repeated_calls` — **FAIL** (ImportError: get_celery_redis does not exist).
- **Integration tests added** to `tests/integration/test_redis_session_health.py`:
  - `test_session_create_and_retrieve_with_redis` — **SKIPPED** when Redis not available (expected).
  - `test_redis_health_returns_true_when_redis_available` — **SKIPPED** when Redis not available (expected).
- **Existing tests:** Task 102 + Celery unit tests (22) still **pass** when run without the new Task 103 tests.
- TDD Red achieved; ready for Phase 2 (implement to make tests pass).

---

## Phase 2 – Implement to make tests pass (TDD Green)

Objective: implement **only** what is needed so the Phase 1 unit and integration tests pass. Preserve Task 102 behavior (URL derivation, single source of truth).

### 2.1 Add pool/timeout settings (Green for 1.1, 1.2)

**File:** `src/personal_assistant/config/settings.py`

- Add:
  - `REDIS_SOCKET_CONNECT_TIMEOUT: int = 5` (or from env).
  - `REDIS_SOCKET_TIMEOUT: int = 5` (or from env).
  - `REDIS_MAX_CONNECTIONS: int | None = None` (optional; redis-py default if None).
- Load from env where appropriate.

**File:** `src/personal_assistant/config/redis.py`

- When building Redis clients, pass:
  - `socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT`
  - `socket_timeout=settings.REDIS_SOCKET_TIMEOUT`
  - If redis-py’s `from_url()` accepts pool size, pass `REDIS_MAX_CONNECTIONS` where supported; otherwise document.
- Apply to both sync and async clients (celery and session).

Re-run tests 1.1 and 1.2; fix until they pass.

### 2.2 Lazy client creation (Green for 1.2 and 1.3)

**File:** `src/personal_assistant/config/redis.py`

- Remove module-level creation of `celery_redis`, `session_redis`, `async_session_redis` (no `from_url()` at import).
- Keep `_session_redis_url` computed at module level (no connection; Task 102 behavior).
- Add private module-level caches: e.g. `_celery_redis = None`, `_session_redis = None`, `_async_session_redis = None`.
- Add:
  - **`get_celery_redis()`** — if `_celery_redis is None`, create client with `redis.Redis.from_url(settings.CELERY_BROKER_URL, ..., socket_connect_timeout=..., socket_timeout=...)`, assign to `_celery_redis`, return it; else return `_celery_redis`.
  - **`get_session_redis()`** — same pattern: create from `_session_redis_url` on first call, cache in `_session_redis`, return it.
  - **`get_async_session_redis()`** — same pattern for async client; cache in `_async_session_redis`; return None if async redis is not available.
- Update **`check_redis_health()`** to use `get_celery_redis().ping()` and `get_session_redis().ping()` instead of `celery_redis` / `session_redis`.
- Update **`check_async_redis_health()`** to use `get_async_session_redis()` (and handle None).

**Call sites:** Today only `config/redis.py` uses `celery_redis` and `session_redis` (health and getters). No other file imports them; `sessions.py` uses `get_async_session_redis()` only. So no other call-site changes if health and getters are updated as above.

Re-run unit tests 1.1–1.5; fix until they pass. In particular, test 3 (no connection at import) should pass after lazy init.

### 2.3 Document env vars (Green for guardrails)

**File:** `config/env.example`

- Add commented entries:
  - `REDIS_SOCKET_CONNECT_TIMEOUT=5`
  - `REDIS_SOCKET_TIMEOUT=5`
  - `REDIS_MAX_CONNECTIONS=` (optional).

### 2.4 Integration tests (Green when Redis available)

- Ensure integration test module exists and uses `get_async_session_redis()` / SessionService and `check_redis_health()` / `check_async_redis_health()`.
- When Redis is available, run:
  ```bash
  python -m pytest tests/integration/test_redis_session_health.py -v -m integration
  ```
- Fix any failures (e.g. getters returning None, health using wrong client). When Redis is up, both integration tests should **pass**.

### 2.5 Full test run

Run all Redis and Celery tests to ensure nothing regressed:
```bash
python -m pytest tests/unit/test_config/test_redis_config.py tests/unit/test_workers/test_celery_entrypoint.py tests/unit/test_workers/test_queue_routing.py tests/integration/test_redis_session_health.py -v
```
Unit tests must pass; integration tests pass when Redis is available, skip when not.

### Phase 2 – Completed (Green)

- **2.1** Added `REDIS_SOCKET_CONNECT_TIMEOUT`, `REDIS_SOCKET_TIMEOUT`, `REDIS_MAX_CONNECTIONS` to `settings.py`; clients built via `_redis_client_kwargs()` using these settings.
- **2.2** Lazy singletons: `get_celery_redis()`, `get_session_redis()`, `get_async_session_redis()` create clients on first call; no `from_url()` at import; health checks use getters. Async client uses `_ASYNC_UNAVAILABLE` sentinel when `redis.asyncio` is not available.
- **2.3** Documented `REDIS_SOCKET_CONNECT_TIMEOUT`, `REDIS_SOCKET_TIMEOUT`, `REDIS_MAX_CONNECTIONS` in `config/env.example`.
- **2.4** Integration tests: use sync-only for availability check; async tests use `@pytest.mark.asyncio` and `_reset_async_redis_cache()` so async client is bound to the test’s event loop. Split health into `test_redis_health_sync_when_redis_available` and `test_redis_health_async_when_redis_available`.
- **2.5** Full run: **30 passed** (10 redis config + 4 celery entrypoint + 13 queue routing + 3 integration). Integration tests pass when Redis is available; they skip when Redis is down (verified in Phase 1).

---

## Phase 3 – Refine and document

1. **Optional refactor**
   - If any test or implementation can be simplified (e.g. shared helper for building client options from settings), do it without changing behavior; re-run tests.

2. **Documentation**
   - Update `docs/architecture/tasks/103_redis_client_improvements/onboarding.md` and `README.md` to state:
     - Redis clients are created lazily (on first getter call); no connection at import.
     - Pool/timeout settings are configurable via `REDIS_SOCKET_CONNECT_TIMEOUT`, `REDIS_SOCKET_TIMEOUT`, `REDIS_MAX_CONNECTIONS`.
     - Integration tests require a running Redis; they are skipped when Redis is unavailable; run with `-m integration` (or project’s marker).
   - Update deployment/dev docs if you document Redis tuning (pool size, timeouts).

### Phase 3 – Completed

- **Optional refactor:** Skipped; `_redis_client_kwargs()` already provides shared client options.
- **Documentation:** Updated `onboarding.md` with "Implemented behavior (Task 103 completed)" (lazy init, getters, pool/timeout, health, integration tests) and "Previous state (pre–Task 103)"; updated key files reference. Updated `README.md`: status **Completed**, objective achieved, "Implemented behavior" section, "How to run integration tests" with commands, key files.
- Task 103 complete.

---

## Summary: test → implement order

| Step | Action | Outcome |
|------|--------|---------|
| 0 | Guardrails + baseline run | Established; no Task 102 or business logic changes |
| 1.1 | Add tests: pool/timeout settings exist, clients use them | Tests **fail** (Red) |
| 1.2 | Add tests: no connection at import, get_celery_redis exists, getters return same instance | Tests **fail** (Red) |
| 1.3 | Add integration tests: session create/get, health when Redis up | Skip or pass depending on Redis |
| 2.1 | Add REDIS_* settings; use them in client construction | Pool/timeout tests pass |
| 2.2 | Lazy init: getters, no from_url at import, health uses getters | Lazy and getter tests pass |
| 2.3 | Document new env vars in env.example | Guardrails satisfied |
| 2.4 | Ensure integration tests pass when Redis available | Green for integration |
| 2.5 | Full test run (unit + integration) | All pass / skip as expected |
| 3 | Refine, update task docs | Done |

---

## File checklist

- [x] **Phase 0:** Baseline run and behavior noted in plan.
- [x] `tests/unit/test_config/test_redis_config.py` — new tests for pool/timeout and lazy init (Phase 1).
- [x] `tests/integration/test_redis_session_health.py` — integration tests, skip when Redis unavailable (Phase 1).
- [x] `src/personal_assistant/config/settings.py` — add REDIS_SOCKET_CONNECT_TIMEOUT, REDIS_SOCKET_TIMEOUT, REDIS_MAX_CONNECTIONS (Phase 2.1).
- [x] `src/personal_assistant/config/redis.py` — use pool/timeout in clients; lazy getters; no import-time from_url; health uses getters (Phase 2.2).
- [x] `config/env.example` — document new REDIS_* vars (Phase 2.3).
- [x] Task 103 onboarding/README — document lazy init, pooling knobs, integration tests (Phase 3).
