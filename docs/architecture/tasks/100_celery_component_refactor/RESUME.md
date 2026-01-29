# Task 100 – Celery Refactor: Resume of Changes and What’s Left

## Summary

The Celery setup now follows **Option B**: one canonical app in `personal_assistant.celery` + config in `personal_assistant.celery.config`, with `personal_assistant.workers.celery_app` as a backward-compatible adapter. Worker and beat in Docker use `-A personal_assistant.celery`. The integration is **working**; a few doc and test cleanups remain for a fully consistent “clean” state.

---

## Changes Already Made

### 1. New canonical layout

| File | Role |
|------|------|
| `src/personal_assistant/celery/__init__.py` | **Canonical app.** `Celery("personal_assistant", broker=..., backend=...)`, `app.config_from_object("personal_assistant.celery.config")`, `app.autodiscover_tasks(["personal_assistant.workers"])`. |
| `src/personal_assistant/celery/config.py` | **Pure config.** Broker/result backend (from `settings.CELERY_BROKER_URL` + env fallback), queues `ai_tasks` / `sms_tasks` / `grocery_tasks`, routes, `beat_schedule`, worker/result settings. No app creation, no DB/metrics imports. |

### 2. Adapter (backward compatibility)

| File | Change |
|------|--------|
| `src/personal_assistant/workers/celery_app.py` | No longer creates an app. Imports `app` from `personal_assistant.celery`, keeps `task_prerun` / `task_postrun` / `task_failure` and `initialize_enhanced_features()`. Task and health code that imports from here still get the same app. |

### 3. Package root

| File | Change |
|------|--------|
| `src/personal_assistant/__init__.py` | Celery is no longer imported or exposed at package level. `import personal_assistant` does not pull in workers or the Celery chain. |

### 4. Docker / CLI (Phase 6)

| File | Change |
|------|--------|
| `docker/docker-compose.dev.yml` | Worker and scheduler `command`: `-A personal_assistant.celery`. Worker: `--queues=ai_tasks,sms_tasks,grocery_tasks`. |
| `docker/docker-compose.stage.yml` | Worker and scheduler: `-A personal_assistant.celery`. |
| `docker/docker-compose.prod.yml` | Beat and `ai_worker`: `-A personal_assistant.celery`. |

### 5. Tests

| File | Change |
|------|--------|
| `tests/unit/test_workers/test_celery_entrypoint.py` | **New.** Covers: import from `personal_assistant.celery`, broker/backend/serialization, autodiscovery of `personal_assistant.workers.tasks.*`, and that importing `personal_assistant.celery` does not call `db_config._initialize_database()`. |
| `tests/unit/test_workers/test_queue_routing.py` | Expectations for beat/worker queues aligned with `ai_tasks` / `sms_tasks` / `grocery_tasks`. |

### 6. Documentation (Phase 7)

| File | Change |
|------|--------|
| `docs/troubleshooting/celery_queue_issues.md` | Queues set to `ai_tasks`, `sms_tasks`, `grocery_tasks`; all examples use `-A personal_assistant.celery` and reference `personal_assistant.celery.config`; legacy queue names noted. |
| `docs/architecture/tasks/100_celery_component_refactor/onboarding.md` | “Key code locations” updated for the new layout; “Refactor completed (Option B)” section added. |

---

## Current Runtime Behavior

- **App entrypoint:** `personal_assistant.celery` (used by `celery -A personal_assistant.celery worker/beat`).
- **Config:** `personal_assistant.celery.config` only.
- **Tasks** (`ai_tasks`, `sms_tasks`, `grocery_tasks`) import `app` from `..celery_app`; that resolves to `personal_assistant.celery.app`.
- **Health / scheduler:** `workers.utils.health_check` and `tools.ai_scheduler.core.scheduler` import from `workers.celery_app` → same app.
- **Unit tests:** `test_celery_entrypoint` (4) and `test_queue_routing` (11 of 12) pass. The single failure is the integration test `test_queue_names_are_clean` when local Redis already has suffixed keys (e.g. `grocery_tasks\x06\x163`).

---

## What’s Left for a Working and Clean Celery Integration

### Must-have (fully consistent “clean” state)

1. **Docs that still show the old app path**  
   These still use `personal_assistant.workers.celery_app` in example commands. Updating them keeps behavior the same but makes docs match the new entrypoint:

   - **`docs/development/setup.md`**  
     - Around lines 205–208 and 296–299: worker/beat examples.  
     - Around 541–544: detached worker/beat.  
     Replace `personal_assistant.workers.celery_app` with `personal_assistant.celery` and use `--queues=ai_tasks,sms_tasks,grocery_tasks` for a single dev worker if that’s what you document.
   - **`docs/deployment/docker-setup.md`**  
     - Around 295 and 325: compose `command` examples.  
     Use `-A personal_assistant.celery` for worker and beat.
   - **`docs/deployment/troubleshooting.md`**  
     - Around 353–363 and 389–392: `celery -A ... inspect` examples.  
     Use `-A personal_assistant.celery`.

### Nice-to-have

2. **`test_queue_names_are_clean` (integration)**  
   - It fails when Redis already has suffixed queue keys.  
   - Options: skip when Redis is “dirty”, or document that it requires a clean Redis / a dedicated test Redis.  
   - No code change is required for correctness; this is environment/CI clarity.

3. **`tests/unit/test_workers/test_celery_app.py`**  
   - Still skipped and written for the old app-in-`workers.celery_app` layout.  
   - Either: remove it and rely on `test_celery_entrypoint` + queue tests, or rewrite it to assert behavior of `personal_assistant.celery` / `workers.celery_app` as adapter. Optional cleanup.

4. **Legacy task docs (062, 070, 037, etc.)**  
   - Various docs under `docs/architecture/tasks/` still show `personal_assistant.workers.celery_app` and old queue lists.  
   - Leave as historical or add a one-line note: “For current app entrypoint and queues, see `docs/troubleshooting/celery_queue_issues.md` and task 100.”

---

## Quick Reference: Correct Usage Going Forward

| Action | Use |
|--------|-----|
| Run worker (dev, all queues) | `celery -A personal_assistant.celery worker --queues=ai_tasks,sms_tasks,grocery_tasks --loglevel=info` |
| Run worker (prod AI only) | `celery -A personal_assistant.celery worker --queues=ai_tasks --loglevel=info` |
| Run beat | `celery -A personal_assistant.celery beat --loglevel=info` |
| Inspect / debug | `celery -A personal_assistant.celery inspect active_queues` (etc.) |
| Import in Python | `from personal_assistant.celery import app` for scripts/tests; task code can keep `from ..celery_app import app` (same app). |
| Config changes | Edit `src/personal_assistant/celery/config.py` only. |

---

## Checklist for “Working and Clean”

- [x] Canonical app in `personal_assistant.celery`, config in `personal_assistant.celery.config`
- [x] Adapter in `workers.celery_app` re-exports app and keeps signals/features
- [x] Docker (dev/stage/prod) uses `-A personal_assistant.celery`
- [x] `docs/troubleshooting/celery_queue_issues.md` updated
- [x] Task 100 onboarding describes the new layout
- [ ] **`docs/development/setup.md`** – worker/beat examples use `personal_assistant.celery`
- [ ] **`docs/deployment/docker-setup.md`** – compose examples use `personal_assistant.celery`
- [ ] **`docs/deployment/troubleshooting.md`** – inspect/debug examples use `personal_assistant.celery`
- [ ] (Optional) `test_queue_names_are_clean`: skip or document Redis cleanliness; optional `test_celery_app.py` rewrite or removal
