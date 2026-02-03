# Frontend AI Tasks API Endpoints – Backend Alignment

The dashboard AI tasks flow uses **DB-backed tasks** (integer `id` from `ai_tasks` table). Several backend routes were still using the **in-memory** `ai_task_service` (UUID task ids), which caused 404s when the frontend sent integer ids.

## Frontend endpoints (from `src/apps/frontend/src/stores/aiTaskStore.ts`)

| Method | Path | Frontend sends | Backend before fix | Status |
|--------|------|----------------|--------------------|--------|
| GET | `/api/v1/ai-tasks/` | — | GET / with auth, returns DB tasks | ✅ OK |
| POST | `/api/v1/ai-tasks/` | DB-style body (title, task_type, …) | POST / with `AITaskDBCreateRequest` + auth | ✅ Fixed earlier |
| PUT | `/api/v1/ai-tasks/{id}` | `id: number`, `updates: Partial<AITask>` | Used `ai_task_service.update_task(task_id: str)` → UUID only | ❌ 404 |
| DELETE | `/api/v1/ai-tasks/{id}` | `id: number` | Used `ai_task_service.delete_task(task_id: str)` → UUID only | ❌ 404 |
| POST | `/api/v1/ai-tasks/{id}/execute` | `id: number` | Added with DB lookup by int `task_id` | ✅ Fixed earlier |
| POST | `/api/v1/ai-tasks/{id}/pause` | `id: number` | **No route existed** | ❌ 404 |

## Root cause

- **GET /** and **POST /** (create)** were updated to use the DB and auth.
- **PUT /{task_id}**, **DELETE /{task_id}**, and **POST /{task_id}/pause** still used the in-memory service (string UUIDs) or were missing, while the frontend always sends **integer** task ids from the DB.

## Backend fixes applied (in `src/apps/fastapi_app/routes/ai_tasks.py`)

1. **DELETE /{task_id}** – Load `DBAITask` by integer `task_id`, verify `user_id == current_user.id`, delete row, return 200.
2. **PUT /{task_id}** – Load `DBAITask` by integer `task_id`, verify ownership, accept `AITaskDBUpdateRequest` (title, description, task_type, schedule_type, status, ai_context, notification_channels, etc.), update row, return `{"task": ...}` in list shape.
3. **POST /{task_id}/pause** – New route: load by integer `task_id`, verify ownership, set `status="paused"`, return 200.

All three routes use `Depends(get_current_user)` and the shared `get_db` session so they operate on the same DB model as GET / and POST /.
