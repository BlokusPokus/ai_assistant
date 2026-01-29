## Task 101 – Async Worker & DB Stabilization (Option B Plan)

Goal: make Celery workers first-class async citizens so that async SQLAlchemy + asyncpg and other async services can run without event-loop/connection errors, while keeping the canonical Celery layout from Task 100.

This plan focuses on **Option B**: a proper async worker loop / strategy, rather than introducing sync DB facades.

All paths below are relative to the repo root.

---

### Phase 0 – Baseline and guardrails

1. **Baseline reproduction in dev**

   - With the current setup (after Task 100), confirm:

     ```bash
     source venv_personal_assistant/bin/activate
     docker compose -f docker/docker-compose.dev.yml up -d redis api worker scheduler
     docker compose -f docker/docker-compose.dev.yml logs -f worker
     ```

   - Observe:
     - AI task flow can complete successfully (as seen for “AI summary of my day”).
     - Periodic errors from:
       - `AITaskManager.get_due_tasks` on `ai_tasks`
       - `sms_retry_health_check` on `sms_usage_logs`
     - Error shape:

       - `asyncpg.InterfaceError: cannot perform operation: another operation is in progress`
       - “Task ... got Future <Future pending ...> attached to a different loop”

2. **Guardrails**

   - Do **not** change:
     - `personal_assistant.celery` (entrypoint) and `personal_assistant.celery.config` semantics.
     - Queue names (`ai_tasks`, `sms_tasks`, `grocery_tasks`) or routing.
   - Any change that impacts worker pool type / concurrency must be:
     - Explicitly called out in this plan.
     - Reflected in `docs/troubleshooting/celery_queue_issues.md` and the new Task 101 docs.

---

### Phase 1 – Analyze async usage in workers

Objective: map exactly where and how async code is used in Celery workers, and how it interacts with event loops and the DB engine.

1. **Map async Celery tasks and helpers**

   - `src/personal_assistant/workers/tasks/ai_tasks.py`:
     - `process_due_ai_tasks` → wrapped around `_process_due_ai_tasks_async`.
     - Uses `AITaskManager`, `NotificationService`, `TaskExecutor`.
     - Currently uses `asyncio` event-loop management (including `nest_asyncio`) inside the Celery task.

   - `src/personal_assistant/workers/tasks/sms_tasks.py`:
     - `process_sms_retries`, `cleanup_old_retries`, `sms_retry_health_check` now wrap async helpers via `asyncio.run(...)`.

   - `src/personal_assistant/tools/ai_scheduler/core/task_manager.py`:
     - Async methods: `create_task`, `get_due_tasks`, `update_task_status`, etc.
     - All use `AsyncSessionLocal` / `_get_session_factory()` from `database.session`.

   - `src/personal_assistant/sms_router/services/simple_retry_service.py`:
     - Async methods for retry queue processing and cleanup using async DB sessions.

2. **Map DB engine creation and sharing**

   - `src/personal_assistant/database/session.py`:
     - Creates an async engine via `create_async_engine(DATABASE_URL, ...)`.
     - Provides `_get_session_factory()` and `AsyncSessionLocal`.
     - Engine/session factories are **module-level singletons**, shared across app and workers.

3. **Identify the problem pattern**

   - Workers are forking and then:
     - Creating or reusing async engines/sessions bound to the main event loop or another loop.
     - Running async work via `asyncio.run(...)` or `nest_asyncio` inside Celery tasks.
   - asyncpg connections created in one loop/greenlet context are being driven from another, causing:
     - “operation is in progress” when a second query arrives.
     - “Future attached to a different loop” when the Future was created on one loop and awaited on another.

Outcome: we have a clear target: **one event loop / async engine context per worker process**, no cross-loop engine sharing, no ad-hoc loops inside tasks.

---

### Phase 2 – Choose an async worker strategy

Objective: pick one concrete Option B strategy and codify it.

Candidate strategies:

1. **Strategy B1 – Single loop per worker process with centralized orchestration**

   - Each Celery worker process:
     - Starts a single `asyncio` event loop on boot.
     - Creates the async SQLAlchemy engine and other async clients in that loop.
     - Exposes a small helper API (e.g. `run_in_worker_loop(coro)`) that Celery tasks can call from their sync context.

   - Implementation sketch:
     - Create a module, e.g. `src/personal_assistant/workers/async_runtime.py`, that:
       - Spawns a background loop thread when imported in a worker process.
       - Owns the async engine and `AsyncSessionLocal` for worker use.
       - Provides `run(coro)` that safely submits coroutines to that loop and waits for results.

   - Pros:
     - Works with the default Celery pool (sync task dispatch).
     - Centralizes event-loop and engine management.
   - Cons:
     - Slightly more moving parts (background loop thread per worker).

2. **Strategy B2 – Celery eventlet/gevent pool for async**

   - Run Celery with an eventlet/gevent pool and adapt async code accordingly.
   - This generally plays poorly with native `asyncio` and asyncpg; **not preferred** here.

**Decision for this task:** proceed with **Strategy B1** (single background loop + async runtime helper per worker process).

---

### Phase 3 – Implement worker async runtime helper

Objective: create a small, well-encapsulated async runtime for workers.

1. **Create `workers/async_runtime.py`**

   - Responsibilities:
     - Start a background thread with an `asyncio` event loop when first used in a worker.
     - Initialize an async SQLAlchemy engine & session factory **for worker use only**.
     - Provide:
       - `async def get_session()` or a context manager for sessions.
       - `def run(coro: Coroutine) -> Any` that:
         - Submits `coro` to the background loop via `asyncio.run_coroutine_threadsafe`.
         - Waits for and returns the result (or raises the exception).

   - Ensure:
     - This module is **only imported in worker processes** (e.g. from Celery tasks or from `workers.celery_app` under a `if app.conf.worker` guard, if needed).
     - It does not affect FastAPI’s async DB usage; keep the existing `database.session` intact for the main app.

2. **Wire worker-only DB usage through `async_runtime`**

   - For Celery workers, we have two options:
     - **Option B1a:** Worker async runtime imports and reuses the existing `database.session` engine, but only from the new loop.
     - **Option B1b (safer):** Worker async runtime creates its own engine using the same `DATABASE_URL`, separate from FastAPI.

   - This plan recommends **B1b** to avoid cross-loop engine sharing:
     - In `async_runtime.py`, call `create_async_engine` with `DATABASE_URL` from config.
     - Use a separate async session factory for worker queries.

---

### Phase 4 – Refactor Celery tasks to use the async runtime

Objective: stop using ad-hoc `asyncio.run` / `nest_asyncio` in tasks, and delegate to the worker async runtime.

1. **AI tasks (`ai_tasks.py`)**

   - Replace internal loop management in `process_due_ai_tasks`:
     - Instead of:

       ```python
       # simplified
       result = loop.run_until_complete(_process_due_ai_tasks_async(task_id))
       ```

     - Use the worker async runtime:

       ```python
       from personal_assistant.workers.async_runtime import run as run_in_worker_loop

       @app.task(bind=True, max_retries=3, default_retry_delay=60)
       def process_due_ai_tasks(self) -> Dict[str, Any]:
           return run_in_worker_loop(_process_due_ai_tasks_async(self.request.id))
       ```

   - Ensure `_process_due_ai_tasks_async` and `AITaskManager` use the worker’s async session factory when invoked from Celery (details in Phase 5).

2. **SMS tasks (`sms_tasks.py`)**

   - Replace `asyncio.run(...)` wrappers with worker runtime calls:

     ```python
     from personal_assistant.workers.async_runtime import run as run_in_worker_loop

     @app.task(bind=True, max_retries=3, default_retry_delay=300)
     def process_sms_retries(self) -> Dict[str, Any]:
         return run_in_worker_loop(_process_sms_retries_async(self.request.id))

     @app.task(bind=True, max_retries=3, default_retry_delay=300)
     def sms_retry_health_check(self) -> Dict[str, Any]:
         return run_in_worker_loop(_sms_retry_health_check_async(self.request.id))
     ```

   - Remove any `nest_asyncio` usage from worker paths.

---

### Phase 5 – Point worker DB usage at the worker async runtime

Objective: ensure that AI and SMS Celery paths use the worker’s async engine/sessions, not the main app’s.

1. **Worker-aware session factory**

   - In `ai_scheduler.task_manager` and `simple_retry_service`, introduce an abstraction over the session factory:

     - For example, a small helper function:

     ```python
     from personal_assistant.database.session import _get_session_factory as get_app_session_factory
     from personal_assistant.workers.async_runtime import get_worker_session_factory, in_worker_process

     def _get_session_factory():
         if in_worker_process():
             return get_worker_session_factory()
         return get_app_session_factory()
     ```

   - Update their usages to call this helper instead of importing `_get_session_factory` directly from `database.session`.

2. **Ensure no cross-loop engine reuse**

   - Confirm that worker async runtime does **not** ever hand its engine/sessions to FastAPI code and vice versa.
   - The only shared configuration is the DB URL; actual engine objects should be distinct.

---

### Phase 6 – Testing and validation

Objective: verify that the new async worker model is stable and does not regress behavior.

1. **Unit tests**

   - Add focused tests for:
     - `workers.async_runtime.run` – submit a simple coroutine and ensure it runs correctly.
     - `process_due_ai_tasks` – using a fake `AITaskManager` and DB stub, verify it calls the async implementation through the runtime.
     - `sms_retry_health_check` – similar structure.

2. **Dev integration tests**

   - In dev environment:

     ```bash
     docker compose -f docker/docker-compose.dev.yml up -d redis api worker scheduler
     docker compose -f docker/docker-compose.dev.yml logs -f worker
     ```

   - Scenarios:
     - Create multiple AI tasks with `next_run_at` in the recent past and ensure:
       - They are picked up and processed without `InterfaceError`.
     - Ensure `sms_retry_health_check` runs periodically without DB errors.
     - Run both AI + SMS flows concurrently and watch for:
       - No asyncpg `InterfaceError`.
       - No “Future attached to a different loop” warnings.

3. **Optional: dedicated integration test**

   - Add a small integration test (marked as requiring DB/Redis) that:
     - Schedules one AI task and triggers `process_due_ai_tasks`.
     - Runs `sms_retry_health_check` in close temporal proximity.
     - Asserts that both complete successfully and no DB errors are logged (captured via a test logger).

---

### Phase 7 – Documentation and cleanup

1. **Task 101 docs**

   - Update this folder:
     - `observations.md` – record any gotchas about asyncpg, greenlet usage, and event loops.
     - `IMPLEMENTATION_PLAN.md` (this file) – keep in sync with actual implementation.

2. **Celery docs**

   - `docs/troubleshooting/celery_queue_issues.md`:
     - Add a short section for “Async DB issues in workers” that:
       - Mentions the previous `InterfaceError` symptoms.
       - Notes that workers now use a dedicated async runtime and what to check if issues reappear.

3. **Code cleanup**

   - Remove any now-unnecessary `nest_asyncio` or ad-hoc loop management from Celery tasks.
   - Ensure comments around Celery tasks clearly describe:
     - That they delegate async work to the worker async runtime.
     - Where to look if async DB or Twilio issues reappear.

