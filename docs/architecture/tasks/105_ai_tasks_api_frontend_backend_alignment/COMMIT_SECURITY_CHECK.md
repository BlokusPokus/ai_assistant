# Pre-commit confidentiality check (changed files)

Checked all files changed in this branch/session for secrets and personal data.

## Files with **no** confidential info (safe to commit as-is)

- `docker/monitoring/prometheus.yml` – config only, no credentials
- `src/apps/fastapi_app/routes/ai_tasks.py` – application code only
- `src/personal_assistant/tools/ai_scheduler/core/task_manager.py` – code only
- `src/personal_assistant/workers/tasks/ai_tasks.py` – code only
- `docs/architecture/tasks/105_ai_tasks_api_frontend_backend_alignment/FRONTEND_ENDPOINTS_OUT_OF_DATE.md` – documentation only
- New section in `docs/deployment/troubleshooting.md` (Docker log errors) – no credentials

## Files that contained dev credentials (adjusted)

- **`docker/docker-compose.dev.yml`**  
  Previously contained:
  - DB URL with username `ianleblanc` and password `password` (personal name + literal password)
  - Redis password `redis_password` in command and healthcheck
  - Grafana `GF_SECURITY_ADMIN_PASSWORD=admin`  
  These have been replaced with **env var substitution** and generic defaults so the compose file does not contain your real username or real passwords. The variable names and defaults are documented in **`docker/env.dev.example`** and in **`docker/README.md`** (Development Environment). Set `DEV_DB_USER`, `DEV_DB_PASSWORD`, `DEV_REDIS_PASSWORD`, `DEV_GRAFANA_ADMIN_PASSWORD` in a local `.env` (e.g. in `docker/` or project root) if you need custom values; otherwise the defaults (e.g. `postgres`, `password`, `redis_password`, `admin`) are used for local dev only.

## Other files (unchanged by this check)

- **`docs/deployment/troubleshooting.md`** – Existing examples elsewhere in the file still use `ianleblanc` and `password` in sample commands (e.g. `psql -U ianleblanc`). Those are documentation examples only; consider generalizing to `postgres` or `$DB_USER` in a later pass if you want the doc to be fully generic.
