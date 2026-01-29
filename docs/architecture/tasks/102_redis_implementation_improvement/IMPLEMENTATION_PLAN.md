# Task 102 – Redis Implementation Improvement (TDD Plan)

Goal: improve Redis configuration so there is a **single source of truth** for the Redis URL, session storage works in Docker/production (env-driven URL), and Celery + config.redis use the same connection source. No change to SessionService or Celery task business logic.

Approach: **Test-Driven Development** — write tests that describe the desired behavior first, then implement until they pass.

All paths below are relative to the repo root.

---

## Phase 0 – Guardrails and baseline

1. **Guardrails**
   - Do **not** change:
     - SessionService key layout, TTL semantics, or concurrency rules.
     - Celery task logic or queue names.
   - Any new env var (e.g. `REDIS_URL`) must be documented in `config/env.example` and task onboarding.

2. **Baseline**
   - Run existing Redis-related tests and note current state:
     ```bash
     python -m pytest tests/unit/test_workers/test_celery_entrypoint.py tests/unit/test_workers/test_queue_routing.py -v
     ```
   - Confirm `config/redis.py` and `celery/config.py` behavior (session URL hardcoded to localhost; Celery from env).

### Phase 0 – Completed

- **Guardrails:** Confirmed (no SessionService or Celery task logic changes; new env vars will be documented).
- **Baseline run:** Using project venv (`venv_personal_assistant`):
  - `tests/unit/test_workers/test_celery_entrypoint.py`: 4 passed.
  - `tests/unit/test_workers/test_queue_routing.py`: 13 passed.
  - **Total: 17 passed**, 4 warnings (unrelated: Pydantic/SQLAlchemy/Gemini).
- **Current behavior confirmed:**
  - `config/redis.py`: `celery_redis` from `settings.CELERY_BROKER_URL`; `session_redis` and `async_session_redis` from hardcoded `redis://localhost:6379/{settings.SESSION_REDIS_DB}`.
  - `celery/config.py`: Broker URL from `settings.CELERY_BROKER_URL` or env `CELERY_BROKER_URL` or `REDIS_URL` (default `redis://localhost:6379`); `result_backend` from settings or env or same as broker.

---

## Phase 1 – Write tests first (TDD Red)

Objective: add a **new test module** that describes the desired Redis config behavior. Run tests and see them **fail** before implementing.

### 1.1 Create test module for Redis config

**File:** `tests/unit/test_config/test_redis_config.py` (create `tests/unit/test_config/` if it does not exist).

**Tests to add:**

1. **`test_redis_url_in_settings`**
   - After implementation, `settings` will have `REDIS_URL`.
   - Test: `from personal_assistant.config.settings import settings` then `assert hasattr(settings, "REDIS_URL")` and `assert "redis" in settings.REDIS_URL.lower()`.
   - (If we keep REDIS_URL optional with default, test the default or that it can be loaded from env.)

2. **`test_session_redis_url_derived_from_redis_url_and_db`**
   - Test that the **session** Redis URL is derived from a base Redis URL and `SESSION_REDIS_DB` (e.g. same host/port, different DB number).
   - You can test a helper like `get_session_redis_url()` or test that `get_async_session_redis()` / client creation uses a URL that contains the correct DB index when given a patched `REDIS_URL` and `SESSION_REDIS_DB`.
   - Example (conceptual): patch `settings.REDIS_URL = "redis://redis:6379/0"` and `settings.SESSION_REDIS_DB = 1`, then assert the session client URL is `redis://redis:6379/1` or equivalent.

3. **`test_celery_and_session_use_same_redis_host`**
   - Test that the Celery broker URL and the session Redis URL refer to the **same host** (and optionally same instance) when both are derived from the same `REDIS_URL` / settings.
   - Prevents drift between Celery and session Redis host.

4. **`test_session_redis_url_not_hardcoded_localhost`**
   - When `REDIS_URL` is set to something other than localhost (e.g. `redis://redis:6379/0`), the session Redis client must **not** use `localhost`.
   - Test by patching `REDIS_URL` and asserting the session URL (or the client’s connection kwargs) contains the expected host.

5. **`test_redis_health_checks_use_same_config`**
   - Optional: test that `check_redis_health()` and `check_async_redis_health()` use the same Redis URLs as the runtime clients (e.g. no second hardcoded URL).

**Run and expect failures:**
```bash
python -m pytest tests/unit/test_config/test_redis_config.py -v
```
Tests should **fail** (REDIS_URL missing, session URL still localhost, etc.). This is the TDD “Red” step.

### Phase 1 – Completed (Red)

- **Created:** `tests/unit/test_config/test_redis_config.py` with 5 tests.
- **Run:** `./venv_personal_assistant/bin/python -m pytest tests/unit/test_config/test_redis_config.py -v`
- **Result:** 5 failed (expected): `REDIS_URL` missing in settings; `get_session_redis_url` not in config.redis.
- TDD Red achieved; ready for Phase 2 (implement to make tests pass).

---

## Phase 2 – Implement to make tests pass (TDD Green)

Objective: change **only** configuration and URL derivation so the Phase 1 tests pass. No change to SessionService logic.

### 2.1 Add REDIS_URL to settings

**File:** `src/personal_assistant/config/settings.py`

- Add:
  - `REDIS_URL: str = "redis://localhost:6379/0"` (or from env with this default).
- Keep:
  - `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` (can later be derived from `REDIS_URL` in Phase 2.3, or left as overrides).
- Ensure:
  - `SESSION_REDIS_DB` remains; session URL will be derived from `REDIS_URL` + `SESSION_REDIS_DB`.

### 2.2 Derive session Redis URL from REDIS_URL + SESSION_REDIS_DB

**File:** `src/personal_assistant/config/redis.py`

- Add a helper (e.g. `get_session_redis_url()`) that:
  - Takes `REDIS_URL` (from settings) and `SESSION_REDIS_DB`.
  - Returns a Redis URL with the same scheme/host/port/password as `REDIS_URL` but with the path/database index set to `SESSION_REDIS_DB` (e.g. `redis://host:6379/1`).
  - Handle edge cases: URL with no path, with password, with `redis://` or `rediss://`.
- Replace the hardcoded `redis://localhost:6379/{settings.SESSION_REDIS_DB}` for:
  - `session_redis`
  - `async_session_redis`
- Use the derived URL when creating both sync and async session clients.

Re-run Phase 1 tests; fix until they pass (session URL derived, not localhost when REDIS_URL is set).

### 2.3 Single source of truth for Celery broker URL (optional but recommended)

**File:** `src/personal_assistant/celery/config.py`

- Use the same source as the rest of the app for the broker URL:
  - Either import `settings` from `personal_assistant.config.settings` and use `settings.REDIS_URL` (or `settings.CELERY_BROKER_URL` if you keep it as override), or
  - Use a shared helper from `config.redis` that returns the broker URL (e.g. from `REDIS_URL` or `CELERY_BROKER_URL`).
- Ensure `result_backend` uses the same source so Celery and `config.redis.celery_redis` never drift.

**File:** `src/personal_assistant/config/redis.py`

- Build `celery_redis` from the **same** URL as Celery (e.g. `settings.REDIS_URL` or the same helper used by `celery/config.py`), so health checks and Celery use one connection source.

Re-run Phase 1 tests and existing Celery tests:
```bash
python -m pytest tests/unit/test_config/test_redis_config.py tests/unit/test_workers/test_celery_entrypoint.py tests/unit/test_workers/test_queue_routing.py -v
```

### 2.4 Env example and Docker

**File:** `config/env.example`

- Document `REDIS_URL` (e.g. `REDIS_URL=redis://localhost:6379/0`).
- Note that `SESSION_REDIS_DB` selects the DB index for session storage (default 1).

**Docker:** Compose already sets `REDIS_URL` (or equivalent); ensure the API and workers receive `REDIS_URL` so session and Celery both use the same Redis host in Docker/production. No need to change Compose if `REDIS_URL` is already passed; otherwise add it alongside existing Celery vars.

---

## Phase 3 – Refine and document

1. **Health checks**
   - Confirm `check_redis_health()` and `check_async_redis_health()` use the same clients (and thus same URLs) as runtime. No second hardcoded URL.

2. **Integration test (optional)**
   - Add or extend an integration test that starts the API (or a test app) with `REDIS_URL` pointing at a test Redis (or mock), creates a session via SessionService, and asserts the session is stored and retrievable. Mark as integration so it can be skipped when Redis is not available.

3. **Documentation**
   - Update `docs/architecture/tasks/102_redis_implementation_improvement/onboarding.md` (and README) to state that:
     - `REDIS_URL` is the single source of truth.
     - Session URL is derived from `REDIS_URL` + `SESSION_REDIS_DB`.
     - Celery broker/result backend and config.redis use the same source.
   - Update deployment/dev docs to mention `REDIS_URL` and `SESSION_REDIS_DB`.

---

## Summary: test → implement order

| Step | Action | Outcome |
|------|--------|---------|
| 1.1 | Add `tests/unit/test_config/test_redis_config.py` with tests for REDIS_URL, derived session URL, same host, no hardcoded localhost | Tests **fail** (Red) |
| 2.1 | Add `REDIS_URL` to settings | One test (REDIS_URL in settings) can pass |
| 2.2 | Derive session URL in config/redis.py; use it for session_redis and async_session_redis | Session URL tests pass |
| 2.3 | Align Celery config and config.redis.celery_redis to same URL source | Celery/session same-host test passes |
| 2.4 | Document REDIS_URL in env.example; ensure Docker passes REDIS_URL | Green; deployable |
| 3 | Health checks, optional integration test, docs | Done |

---

## File checklist

- [x] `tests/unit/test_config/test_redis_config.py` — new tests (Phase 1)
- [x] `src/personal_assistant/config/settings.py` — add `REDIS_URL` (Phase 2.1)
- [x] `src/personal_assistant/config/redis.py` — derive session URL, use for session + optional celery_redis alignment (Phase 2.2, 2.3)
- [x] `src/personal_assistant/celery/config.py` — use shared REDIS_URL source (Phase 2.3)
- [x] `config/env.example` — document REDIS_URL and SESSION_REDIS_DB (Phase 2.4)
- [x] Task 102 onboarding/README — document final behavior (Phase 3)
