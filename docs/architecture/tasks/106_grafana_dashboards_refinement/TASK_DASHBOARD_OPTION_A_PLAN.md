# Option A: Worker exposes /metrics — TDD implementation plan

**Goal:** Celery worker exposes an HTTP `/metrics` endpoint; Prometheus scrapes it; Task dashboard shows task execution data.

**TDD approach:** Define acceptance criteria and tests first (Red), then implement until they pass (Green), then refactor if needed.

---

## Acceptance criteria (what “done” looks like)

1. **AC1** When the worker process is running, `GET http://worker:9091/metrics` returns 200 and a response body in Prometheus exposition format.
2. **AC2** After at least one task has been executed by the worker, the response includes at least one **series** for a task metric (e.g. a line starting with `task_execution_duration_seconds_` or `task_success_rate{`).
3. **AC3** Prometheus has a scrape job for the worker target; the target is UP and Prometheus stores task_* series.
4. **AC4** Grafana Task dashboard shows data (e.g. Task Execution Count or Task Success Rate) when the worker has run tasks in the selected time range.

---

## Test-first (Red) and implementation (Green)

### Phase 1: Metrics HTTP server in the worker process

**Red — write failing tests**

1. **Test: metrics server returns 200 and Prometheus format**
   - **Where:** e.g. `tests/workers/test_worker_metrics_server.py` (new).
   - **What:** Start the worker metrics HTTP server (or call the function that generates the response); `GET /metrics`; assert status 200, `Content-Type: text/plain; charset=utf-8` (or whatever the Prometheus client uses), and body contains `# TYPE` (so it’s exposition format).
   - **Run:** `pytest tests/workers/test_worker_metrics_server.py -v` → **fails** (no server or no module yet).

2. **Test: after recording a task, /metrics includes task metric series**
   - **What:** In the same process, get the metrics service, call `record_task_execution(task_type="test_task", duration=1.0, success=True)`, then GET /metrics (or call the same generator the server uses). Assert response body contains a line matching `task_execution_duration_seconds_count{` or `task_success_rate{` (i.e. at least one task series).
   - **Run:** → **fails** (no server, or server doesn’t use the same registry the worker updates).

**Green — implement**

1. Add a small HTTP server that serves `GET /metrics` by calling `get_metrics_service().generate_metrics()` (and appropriate `Content-Type`). Run it in a **daemon thread** so it doesn’t block the Celery worker.
2. Server should bind to `0.0.0.0` and a configurable port (e.g. env `WORKER_METRICS_PORT=9091`).
3. Start the server when the worker process starts (e.g. on Celery `worker_ready` signal, or from `initialize_enhanced_features()` in `workers/celery_app.py`, or from the Celery app’s `worker_init`).
4. Re-run the two tests → **pass**.

**Refactor (if needed)**

- Extract port and host to config/env; keep the server startup in one place.

---

### Phase 2: Docker and Prometheus scrape

**Red — define expectations (tests or checklist)**

1. **Checklist (manual or e2e):** After `docker compose -f docker/docker-compose.dev.yml up -d`:
   - `curl -s http://localhost:9091/metrics` (or the host-mapped port) returns 200 and body with `# TYPE` and, if a task has run, `task_` series.  
   - So: **test** could be “script or e2e test that starts compose, waits for worker up, triggers one task, then curls worker metrics and asserts task_ in body”. If you prefer not to automate Docker, this stays a **manual checklist** and “Red” is “curl fails / no task_ series”.

**Green — implement**

1. **docker-compose.dev.yml**
   - Worker service: expose port `9091:9091` (or map to a host port if you prefer).
   - Ensure worker and Prometheus are on the same network (already are: `personal_assistant_network`).
2. **prometheus.yml**
   - Add a new scrape job, e.g.:
     ```yaml
     - job_name: "celery_worker"
       static_configs:
         - targets: ["worker:9091"]
       metrics_path: "/metrics"
       scrape_interval: 30s
     ```
3. Reload Prometheus (or restart stack). Confirm in Prometheus → Status → Targets that `celery_worker` / `worker:9091` is **UP**.
4. Run the Phase 1 tests again in CI (they don’t depend on Docker). Run the checklist (manual or e2e) → **pass**.

**Refactor**

- Document in `docker/README.md` and/or `DASHBOARD_MAP.md` that the Task dashboard’s task metrics come from the `celery_worker` job.

---

### Phase 3: Task dashboard panels (optional fix)

**Context:** The first panel currently uses `task_execution_duration_seconds` (raw). For a histogram, Prometheus exposes `_bucket`, `_count`, `_sum`. So “Task Execution Duration” may need a query like `histogram_quantile(0.95, sum(rate(task_execution_duration_seconds_bucket[5m])) by (le, task_type))` or similar to show latency percentiles. “Task Execution Count” already uses `task_execution_duration_seconds_count` and is correct.

**Red**

- Open Task dashboard; confirm “Task Execution Count” (or another panel) shows “No data” when no worker metrics exist, and shows data after worker has run tasks and Prometheus has scraped.

**Green**

- If any panel query is wrong (e.g. raw histogram name), fix the panel JSON to use the correct metric (e.g. `_bucket` + `histogram_quantile` for duration percentiles).
- Re-check AC4: Task dashboard shows data when worker has run tasks.

---

## Order summary (TDD)

| Phase | Red (test / checklist) | Green (implement) |
|-------|------------------------|-------------------|
| 1 | Tests: GET /metrics returns 200 + exposition format; after record_task_execution, body contains task_ series | Worker process starts an HTTP server on 9091 serving get_metrics_service().generate_metrics(); start on worker_ready or equivalent. |
| 2 | Curl worker:9091/metrics fails or Prometheus has no worker target | Expose worker port 9091 in compose; add celery_worker scrape job; verify target UP. |
| 3 | Task dashboard still wrong or empty for duration | Fix panel queries if needed; confirm dashboard shows data. |

---

## Files to add or touch (implementation hints)

- **New:** `src/personal_assistant/workers/metrics_server.py` (or under `workers/utils/`) — HTTP server in a daemon thread, binding to `0.0.0.0:<port>`, serving `GET /metrics` via `get_metrics_service().generate_metrics()`.
- **Touch:** `src/personal_assistant/workers/celery_app.py` (or Celery app entry point) — start the metrics server thread on worker ready (e.g. `worker_ready` signal or after `initialize_enhanced_features()`).
- **New:** `tests/workers/test_worker_metrics_server.py` — tests for 200, Content-Type, and task_ series after `record_task_execution`.
- **Touch:** `docker/docker-compose.dev.yml` — worker service: add `ports: ["9091:9091"]`.
- **Touch:** `docker/monitoring/prometheus.yml` — add `celery_worker` job targeting `worker:9091`.
- **Touch (optional):** `docker/monitoring/grafana/dashboards/task-dashboard.json` — fix “Task Execution Duration” panel if it uses the raw histogram name instead of `_bucket` + `histogram_quantile`.

---

## Out of scope for this plan

- Pushing metrics to a Pushgateway (Option B).
- Pushing metrics to the API (Option C).
- Changing how `record_task_execution` or `update_task_metrics` work (they stay as-is; we only expose the existing registry over HTTP).
