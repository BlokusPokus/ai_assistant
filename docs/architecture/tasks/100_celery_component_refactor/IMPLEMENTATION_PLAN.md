## Task 100 – Celery Component Refactor (Option B, TDD Plan)

Goal: **Align the Celery setup with the canonical Celery 5.6 layout** by introducing `personal_assistant.celery` and `personal_assistant.celery.config`, while keeping behavior equivalent and using tests to drive and validate the migration.

**References (Celery 5.6.2 docs used for this plan):**

- API Reference: `https://docs.celeryq.dev/en/main/reference/index.html`
- User Guide: `https://docs.celeryq.dev/en/main/userguide/index.html`

This plan assumes you will follow a **test-driven / test-guided** approach:

- Add or adjust tests first to describe the desired new behavior and structure.
- Run tests, see them fail, then implement the refactor to make them pass.
- Keep changes incremental and re-run tests after each phase.

All paths below are relative to the repo root.

---

### Phase 0 – Safety & baseline

1. **Run the existing Celery-related tests to capture the current baseline:**

   ```bash
   # Unit tests
   python -m pytest tests/unit/test_workers/test_queue_routing.py -v

   # Integration tests (only if Redis and Celery are available locally)
   python -m pytest tests/integration/test_celery_integration.py -v

   # Worker initialization
   python -m pytest tests/workers/test_system_initialization.py -v
   ```

2. **Note the current behavior and any existing skips/failures:**

   - `tests/unit/test_workers/test_celery_app.py` is currently skipped; we will **rewrite it** later to describe the new layout.
   - Integration tests may be skipped if Redis or workers are not running; that is acceptable during early phases.

---

### Phase 1 – Define the new desired structure in tests

Objective: Write/update **tests that describe the new Celery layout** before implementing it.

1. **Create or update a unit test module for the new entrypoint**, e.g. `tests/unit/test_workers/test_celery_entrypoint.py`:

   Desired assertions:

   - `from personal_assistant.celery import app` succeeds.
   - `app.main == "personal_assistant"` (or a clearly defined name for the project Celery app).
   - `app.conf.broker_url` and `app.conf.result_backend` are both Redis URLs and equal.
   - `app.autodiscover_tasks` has loaded tasks from `personal_assistant.workers.tasks`.

2. **Rewrite `tests/unit/test_workers/test_celery_app.py` to match the new world:**

   - Remove the global `@pytest.mark.skip`.
   - Assume `personal_assistant.workers.celery_app.app` is a thin alias/wrapper around `personal_assistant.celery.app`.
   - Test high-level configuration only (not legacy queues):
     - Presence of queues: `ai_tasks`, `sms_tasks`, `grocery_tasks`.
     - Correct `beat_schedule` entries for AI/SMS/grocery tasks.
     - Correct default queue/exchange/routing key.

3. **Add expectations about reduced side effects (structural, not behavioral):**

   - In a new or existing test:
     - Importing `personal_assistant.celery` **should not**:
       - Directly call `db_config._initialize_database()`.
     - (You can use `unittest.mock.patch` to assert that this is not called during import of the new module.)

4. **Run these tests and confirm they fail**, since `personal_assistant.celery` does not exist yet.

---

### Phase 2 – Introduce `personal_assistant.celery.config`

Objective: Create a dedicated Celery config module that mirrors the current configuration but is **pure configuration** (no DB init, no side effects).

1. **Create `src/personal_assistant/celery/config.py` with:**

   - Broker and backend configuration:

     ```python
     import os
     from personal_assistant.config.settings import settings  # if available

     # Prefer settings, fall back to environment variables for compatibility
     CELERY_BROKER_URL = getattr(settings, "CELERY_BROKER_URL", None) or os.getenv(
         "CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379")
     )
     CELERY_RESULT_BACKEND = getattr(settings, "CELERY_RESULT_BACKEND", None) or os.getenv(
         "CELERY_RESULT_BACKEND", CELERY_BROKER_URL
     )
     ```

   - A `CELERY_CONFIG` dict (or module-level variables) containing:
     - `task_serializer`, `accept_content`, `result_serializer`, `timezone`, `enable_utc`.
     - `task_routes`, `task_queues`, `task_default_queue`, `task_default_exchange`, `task_default_exchange_type`, `task_default_routing_key`.
     - `beat_schedule` copied from `workers/celery_app.py` (AI/SMS/grocery tasks only).
     - Worker and result backend settings (`worker_prefetch_multiplier`, `result_expires`, etc.).

   - Keep this module **free of any imports** from:
     - `personal_assistant.config.database` (`db_config`).
     - `personal_assistant.workers.utils` (metrics, alerting, performance).

2. **Run unit tests that import `personal_assistant.celery.config`**:

   - Add a small test in `test_celery_entrypoint.py` that verifies:
     - `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` exist and are Redis URLs.
   - Run tests and ensure they pass (this module should be simple and side-effect free).

---

### Phase 3 – Introduce `personal_assistant.celery` as the main Celery app

Objective: Implement the new canonical entrypoint and make tests that depend on it pass.

1. **Create `src/personal_assistant/celery/__init__.py`** (celery package):

   - Implementation outline:

     ```python
     from celery import Celery

     app = Celery("personal_assistant")

     # Load configuration from celery config module
     app.config_from_object("personal_assistant.celery.config")

     # Autodiscover tasks from workers
     app.autodiscover_tasks(["personal_assistant.workers"])
     ```

   - Optionally, if you decide to keep config in module-level names (not `CELERY_CONFIG` dict), adjust to match Celery’s `config_from_object` expectations (either dict or attribute-based).

2. **Run the new entrypoint tests:**

   - `python -m pytest tests/unit/test_workers/test_celery_entrypoint.py -v`

   - Fix any issues related to:
     - Incorrect module path in `config_from_object`.
     - Missing attributes in `personal_assistant.celery.config`.

3. **Ensure that `app.conf` reflects the same queues, routes, and beat schedule as before.**

   - You can temporarily add assertions in the tests to compare old vs new config if needed.

---

### Phase 4 – Make `workers.celery_app` a thin adapter

Objective: Keep backward compatibility by turning `workers.celery_app` into a wrapper around the new app, while gradually moving side-effectful code out.

1. **Refactor `src/personal_assistant/workers/celery_app.py`:**

   - Replace the current `Celery(...)` instantiation and `app.conf.update(...)` block with:

     ```python
     """
     Backward-compatible adapter for the main Celery app.
     """

     from personal_assistant.celery import app  # re-export
     ```

   - Temporarily **comment out or remove**:
     - The environment `.env` loading logic.
     - The `db_config._initialize_database()` call.
     - The `initialize_enhanced_features()` call.
     - Direct `logging.basicConfig(...)` configuration.
     - The `if __name__ == "__main__": app.start()` block (optional, if not used).

   - If metrics/alerting/performance and signal handlers are still desired, move them into a separate module, e.g. `workers/celery_signals.py`, and import that module from `personal_assistant.celery` (not from `celery_app`), so the wiring is explicit but not coupled to the adapter.

2. **Update `tests/unit/test_workers/test_celery_app.py`:**

   - Confirm:
     - `from personal_assistant.workers.celery_app import app` returns the same object as `from personal_assistant.celery import app` (you can use `is`).
     - Basic configuration expectations (queues, routes, beat schedule) still hold.

3. **Run all Celery unit tests:**

   ```bash
   python -m pytest tests/unit/test_workers/test_celery_entrypoint.py -v
   python -m pytest tests/unit/test_workers/test_celery_app.py -v
   python -m pytest tests/unit/test_workers/test_queue_routing.py -v
   ```

   - Fix any failing tests by adjusting `personal_assistant.celery.config` (not by reintroducing side effects in `celery_app`).

---

### Phase 5 – Update system initialization and health checks

Objective: Ensure that the rest of the worker system (`workers.__init__`, health checks, schedulers) works cleanly with the new app.

1. **Review `src/personal_assistant/workers/__init__.py`:**

   - Ensure that the imported `app` still points to `personal_assistant.celery.app` via the adapter.
   - Confirm that `initialize_workers`, `get_system_status`, and `get_scheduler_status` still behave as expected.

2. **Adjust `src/personal_assistant/workers/utils/health_check.py`:**

   - Consider importing `app` from `personal_assistant.celery` (or leave it as `workers.celery_app` if you prefer the adapter).
   - Optionally deepen the Celery health check to:
     - Use `app.control.inspect()` to verify there are active workers/queues (if appropriate for your environment).
   - Most importantly, **avoid reintroducing** DB initialization or heavy side effects here.

3. **Run worker initialization tests:**

   ```bash
   python -m pytest tests/workers/test_system_initialization.py -v
   ```

   - Fix any issues caused by import path changes.

---

### Phase 6 – Align Docker and operational commands

Objective: Update runtime commands to use the new canonical Celery entrypoint.

1. **Inspect `docker/docker-compose.dev.yml` and any prod/stage compose files:**

   - Find worker and scheduler services that run commands like:

     ```yaml
     command:
       [
         "celery",
         "-A",
         "personal_assistant.workers.celery_app",
         "worker",
         ...
       ]
     ```

2. **Update them to point to the new entrypoint:**

   - Use:

     ```yaml
     command:
       [
         "celery",
         "-A",
         "personal_assistant.celery",
         "worker",
         ...
       ]
     ```

   - Do the same for beat/scheduler services:

     ```yaml
     command:
       [
         "celery",
         "-A",
         "personal_assistant.celery",
         "beat",
         ...
       ]
     ```

3. **If you previously used `TaskScheduler.start_worker` / `start_beat` in `tools/ai_scheduler/core/scheduler.py`:**

   - Decide whether to:
     - Retain it as a thin wrapper around the new `personal_assistant.celery.app`, or
     - Deprecate it in favor of pure CLI/Docker usage.
   - Update any tests or scripts that depend on it accordingly.

4. **Re-run integration tests (if infrastructure is available):**

   ```bash
   python -m pytest tests/integration/test_celery_integration.py -v
   python -m pytest tests/unit/test_workers/test_queue_routing.py -v
   ```

---

### Phase 7 – Documentation and cleanup

Objective: Make sure documentation and legacy artifacts match the new reality.

1. **Update `docs/troubleshooting/celery_queue_issues.md`:**

   - Adjust queue lists to match the current config: `ai_tasks`, `sms_tasks`, `grocery_tasks`.
   - Update example worker/beat commands to use `-A personal_assistant.celery`.
   - Keep historical sections (e.g. suffixed Redis queues) but clearly mark legacy snippets.

2. **Update or add a short section to `onboarding.md` in this task folder:**

   - Note that the refactor has been completed and key differences from the old layout.

3. **Remove or archive any dead code:**

   - Any commented-out legacy Celery config (`docs/architecture/tasks/062_celery_redis_system_validation/old_files/celery_config.py`) can remain as historical reference.
   - Remove unused imports and helpers from `workers/celery_app.py` that are no longer relevant after the adapter change.

4. **Final test run:**

   ```bash
   python -m pytest tests/unit/test_workers -v
   python -m pytest tests/integration/test_celery_integration.py -v  # if infra available
   ```

---

### Notes

- Throughout this refactor, **prefer changing configuration via `personal_assistant.celery.config`** rather than modifying the adapter in `workers.celery_app`.
- If you encounter behavior differences, add **targeted tests** first that describe the desired behavior, then adjust `personal_assistant.celery.config` or task routing to satisfy them.
- Keep DB initialization, metrics, alerting, and performance tuning out of the core Celery entrypoint; wire them via explicit modules or Celery signals where needed. This makes the system easier to test and reason about.

