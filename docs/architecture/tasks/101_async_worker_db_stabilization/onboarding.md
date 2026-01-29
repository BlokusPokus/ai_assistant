## Task 101 – Async Worker & DB Stabilization for Celery

### Context

Task 100 refactored the Celery setup to a clean, canonical layout:

- **App**: `personal_assistant.celery`
- **Config**: `personal_assistant.celery.config`
- **Adapter**: `personal_assistant.workers.celery_app` (signals + enhanced features)
- **Entrypoints** (CLI, Docker, docs): `-A personal_assistant.celery`

Real AI and SMS tasks now run end-to-end through this entrypoint.

However, when Celery workers execute **async DB workloads** (AI tasks and SMS analytics) using the async SQLAlchemy + asyncpg stack, the logs show intermittent errors:

- `asyncpg.exceptions._base.InterfaceError: cannot perform operation: another operation is in progress`
- “Task ... got Future <Future pending ...> attached to a different loop”

These are not Celery wiring problems; they are **event-loop and connection usage issues** between:

- Celery’s worker processes (prefork pool, sync task entrypoints)
- `asyncio.run` / `nest_asyncio`
- The async SQLAlchemy engine using asyncpg

This task aims to make Celery workers **natively async-friendly**, so that async DB code and other async dependencies can run reliably without loop/connection conflicts.

### Goal

Design and implement an **Option B** architecture where:

- Celery workers use a **single, well-defined async event loop / worker pool** to run async workloads.
- The async SQLAlchemy + asyncpg stack is created and used **within that loop**, without cross-loop mixing.
- Celery tasks do **not** need to call `asyncio.run` or `nest_asyncio` themselves; instead, they delegate to worker-level async orchestration.

End state: AI + SMS Celery tasks can use the async DB and other async services **without**:

- `InterfaceError: cannot perform operation: another operation is in progress`
- “Future attached to a different loop” warnings.

### Scope

In scope:

- AI tasks and scheduler:
  - `src/personal_assistant/workers/tasks/ai_tasks.py`
  - `src/personal_assistant/tools/ai_scheduler/core/task_manager.py`
  - `src/personal_assistant/tools/ai_scheduler/core/executor.py`
- SMS tasks:
  - `src/personal_assistant/workers/tasks/sms_tasks.py`
  - `src/personal_assistant/sms_router/services/simple_retry_service.py`
  - SMS retry health metrics/queries on `sms_usage_logs`
- Celery worker configuration and initialization:
  - `src/personal_assistant/celery/` (package)
  - `src/personal_assistant/workers/celery_app.py`
  - `docker/docker-compose.*.yml` worker/scheduler concurrency, pool type (if needed)
- Database session/engine usage from workers:
  - `src/personal_assistant/database/session.py`

Out of scope (for this task):

- Changing the canonical Celery layout (`personal_assistant.celery` + `personal_assistant.celery.config`).
- Business logic of AI tasks, SMS router, or Twilio integration.
- Non-Celery async usage in the FastAPI app (that continues to use the existing async DB stack).

### Current behavior (high level)

- Celery workers run with the **default prefork pool**, executing tasks in forked worker processes.
- Many Celery tasks are declared as `async def` and wrapped with `asyncio.run(...)` (and sometimes `nest_asyncio`) from within the task body.
- The async SQLAlchemy engine (`postgresql+asyncpg`) is shared across:
  - FastAPI (main app)
  - Background tasks (Celery worker processes)
- When Celery tasks like `process_due_ai_tasks` and `sms_retry_health_check` query the DB concurrently, asyncpg detects that **multiple operations are being attempted on the same connection / loop** and raises `InterfaceError`.

### Desired behavior

- Celery workers have a **clear async runtime model**:
  - A single event loop per worker process (or per pool) that owns the async DB engine and related clients.
  - Worker tasks delegate to that loop instead of creating their own ad-hoc loops.
- Async DB access from Celery is robust even under concurrent tasks:
  - No `InterfaceError` about “operation in progress”.
  - No cross-loop `Future` warnings.
- The implementation is **well-documented** in this task folder and in the Celery troubleshooting docs, so future changes can follow the same pattern.

### How to use this folder

- Use this `onboarding.md` for context and to understand the problem surface.
- Add detailed observations and design options to `observations.md` (to be created).
- Capture the final implementation steps in `IMPLEMENTATION_PLAN.md`:
  - Option B design choice (exact pool/loop strategy).
  - File-by-file changes.
  - Testing strategy (unit + integration).


