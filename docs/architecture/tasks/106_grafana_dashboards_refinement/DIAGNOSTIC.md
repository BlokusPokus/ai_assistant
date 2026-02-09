# Dashboard data diagnostic (no code changes)

Use this to find why Application dashboard (and others) show no data. Work through each step; the step that fails is the break in the chain.

**Important:** If `curl localhost:8000/metrics` shows only `# HELP http_requests_total` and `# TYPE http_requests_total counter` but **no line starting with `http_requests_total{`** (no actual series), then the metric is defined but **no request has been recorded**. That usually means either (1) the process you’re curling doesn’t have the metrics middleware (e.g. API running locally from venv while Prometheus scrapes the Docker API), or (2) the middleware isn’t running for requests (e.g. old container without the middleware). Check **who** is on port 8000 (Docker vs local) and that the **same** process is scraped by Prometheus and receives traffic.

---

## Data flow (what we’re checking)

```
API requests → PrometheusMetricsMiddleware → http_requests_total / http_request_duration_seconds
       → GET /metrics (API) → Prometheus scrapes api:8000/metrics
       → Grafana queries Prometheus → Application dashboard panels
```

---

## Step 1: Does the API expose the metrics?

**Check:** Does the API’s `/metrics` response include **actual series** (not just HELP/TYPE) for `http_requests_total` and `http_request_duration_seconds`?

From your host:

```bash
# Must show at least one line starting with the metric name (actual data)
curl -s http://localhost:8000/metrics | grep "^http_requests_total"
curl -s http://localhost:8000/metrics | grep "^http_request_duration_seconds"
```

**Expected:** Lines like:

- `http_requests_total{method="GET",endpoint="/metrics",status="200"} 1`
- `http_request_duration_seconds_bucket{method="GET",endpoint="/metrics",le="0.005"} 1`

If you only see `# HELP http_requests_total` and `# TYPE http_requests_total counter` but **no line starting with `http_requests_total{`**, then the metric exists but **no request has been recorded**. Common causes:

- You’re curling **localhost:8000** (e.g. API running **locally** in venv) while **Prometheus** scrapes the **Docker** API at **api:8000**. They are different processes; only the one Prometheus scrapes needs to have series.
- The API that Prometheus scrapes (the **container**) was started before the metrics middleware was added, or its code/image doesn’t include it.

**Who is on 8000?** If you run the API in Docker (`docker compose up`), then `localhost:8000` is the container. If you also run `uvicorn` in your venv on 8000, the host port is your local process and Prometheus (in Docker) never sees it. Ensure the **same** API that serves `localhost:8000` when you curl is the one Prometheus scrapes (e.g. only start the API in Docker, or point Prometheus at your host if you run API locally).

**If you see at least one series:** Metrics are emitted; continue to Step 2.

---

## Step 2: Is Prometheus scraping the API?

**Check:** Is the `personal_assistant_api` target UP and are we getting the same metrics in Prometheus?

1. Open **Prometheus UI**: http://localhost:9090  
2. Go to **Status → Targets**.  
3. Find job **personal_assistant_api**, target **api:8000**. It should be **UP**.  
4. Then go to **Graph** and run:

   ```promql
   up{job="personal_assistant_api"}
   ```

   Should be `1` for `instance="api:8000"`.

5. Then run:

   ```promql
   http_requests_total
   ```

   or

   ```promql
   rate(http_requests_total[5m])
   ```

**Expected:**  
- Target UP.  
- `up{job="personal_assistant_api"}` = 1.  
- `http_requests_total` (and/or its rate) returns series (possibly only after some traffic and a couple of scrape intervals).

**If target is DOWN:** Prometheus can’t reach `api:8000` (network/DNS in Docker). Check compose network and that the API container is up.  
**If target UP but no `http_requests_total`:** Either the API’s `/metrics` doesn’t expose them (back to Step 1) or scrape path is wrong (we use `metrics_path: /metrics`).  
**If you get data in Prometheus:** Continue to Step 3.

---

## Step 3: Is Grafana using the right Prometheus?

**Check:** Grafana’s Prometheus datasource and a direct query.

1. Open **Grafana**: http://localhost:3005  
2. **Connections → Data sources → Prometheus.**  
3. Confirm URL is **http://prometheus:9090** (from Grafana’s perspective inside Docker).  
4. Click **Save & test** — should succeed.  
5. Go to **Explore**, select **Prometheus**, and run the same query as in Step 2:

   ```promql
   rate(http_requests_total[5m])
   ```

   Time range: **Last 1 hour** (or when you had traffic).

**Expected:** Same (or similar) series as in Prometheus UI.

**If “Save & test” fails:** Grafana can’t reach Prometheus (network/URL).  
**If Explore returns no data:** Either Grafana is pointing at a different Prometheus or there’s a proxy/timeout issue.  
**If Explore returns data:** Continue to Step 4.

---

## Step 4: Application dashboard query and time range

**Check:** The dashboard panel query and time range.

1. Open **Dashboards → Personal Assistant → Application**.  
2. **HTTP Request Rate** panel uses:

   ```promql
   rate(http_requests_total[5m])
   ```

   (No `job` or `instance` filter — so it should show all scraped `http_requests_total`.)

3. Set time range to **Last 1 hour** (or when you had traffic).  
4. Open the panel’s **Query** (edit panel) and confirm the datasource is **Prometheus** and the expression is exactly as above.  
5. Optionally run the same query in **Explore** with the same time range to confirm Prometheus has data in that window.

**Expected:** If Step 3 shows data for that time range, the panel should show it too.

**If panel is “No data” but Explore has data:** Check for a typo in the panel expr, or a hidden filter (e.g. template variable `instance` set to a value that doesn’t exist).  
**If both panel and Explore have no data for “last 1h”:** Either there was no traffic in that window or the metrics weren’t being scraped yet (e.g. short time after restart). Try “Last 6 hours” and generate a few requests, then wait 1–2 scrape intervals (30s each).

---

## Step 5: Worker / Task dashboard (why task runs don’t show)

**Check:** Where task metrics come from.

- **Task dashboard** panels use metrics such as `task_execution_duration_seconds`, `task_success_rate`, `task_queue_length`.  
- These are **only exposed by the API** at `GET /metrics` if something in the **API process** updates them.  
- **Celery workers** run in a **different process**; they call `record_task_execution()` in their own process, so their metrics live in the **worker’s** in-memory registry.  
- Prometheus only scrapes **api:8000**, not the workers. So **worker task completions are not in Prometheus** and will never appear on the Task dashboard with the current setup.

**Conclusion:** “Task completed” lines in worker logs are expected **not** to appear in Grafana until workers expose `/metrics` (or push metrics) and Prometheus scrapes them. This is a design gap, not a misconfiguration.

---

## Summary table

| Step | What to check | If it fails |
|------|----------------|-------------|
| 1 | `curl localhost:8000/metrics \| grep http_requests_total` | Metrics not emitted (middleware not in use or not recording). |
| 2 | Prometheus **Targets** (api:8000 UP) and **Graph** `http_requests_total` / `rate(...)` | Scrape target down or wrong; or metrics not in scrape. |
| 3 | Grafana **Data sources** (Prometheus, Save & test) and **Explore** `rate(http_requests_total[5m])` | Grafana can’t reach Prometheus or wrong datasource. |
| 4 | Application dashboard **time range** and **panel query** (same as Explore) | Wrong time range or panel query/filter. |
| 5 | Task dashboard / worker logs | By design, worker metrics are not scraped; Task dashboard only shows API-side task metrics. |

Run Steps 1–4 in order; the first step that doesn’t match “Expected” is where the link is broken.

---

## Task dashboard diagnostic (no code changes)

Use this to see why the Task dashboard shows no data. The goal is to find **where the chain breaks** (who produces the metrics vs who Prometheus scrapes).

### Data flow for task metrics

```
Celery workers run tasks
  → workers call get_metrics_service().record_task_execution(task_type, duration, success)
  → workers call get_metrics_service().update_task_metrics(queue_lengths)
  → metrics live in the **worker process** in-memory registry
  → worker process does **not** expose HTTP /metrics

Prometheus scrapes only api:8000/metrics (the API container)
  → API process has its own registry; it never calls record_task_execution (only workers do)
  → So task_* series either don’t exist on the API or are never updated

Grafana Task dashboard queries Prometheus for task_* metrics
  → No (or empty) series → “No data”
```

### Task dashboard panels and queries

| Panel | PromQL | Metric type |
|-------|--------|-------------|
| Task Execution Duration | `task_execution_duration_seconds` | Histogram (exposes _bucket, _count, _sum) |
| Task Success Rate | `task_success_rate` | Gauge |
| Task Queue Length | `task_queue_length` | Gauge |
| Task Execution Count | `sum(rate(task_execution_duration_seconds_count[5m])) by (task_type)` | From histogram _count |

All of these are **produced** when workers call `record_task_execution()` and `update_task_metrics()` in `personal_assistant.workers.utils.metrics`. That code runs in the **worker process**. The **API process** does not run Celery tasks and does not call those methods, so the API’s `/metrics` does not get updated with task execution data.

### Step-by-step checks (diagnosis only)

1. **Does the API expose any task_* series?**  
   From the host (API = whatever is on port 8000 when you use the app):
   ```bash
   curl -s http://localhost:8000/metrics | grep "^task_"
   ```
   **Expected (current setup):** You may see `# HELP` / `# TYPE` for `task_execution_duration_seconds`, `task_success_rate`, `task_queue_length`, but **no lines starting with `task_execution_duration_seconds{` or `task_success_rate{`** (no series), because the API process never records task completions. If the API is in Docker and never gets task updates from workers, its task metrics stay empty.

2. **Who is scraped by Prometheus?**  
   In Prometheus → **Status → Targets**, the only application target is **personal_assistant_api** → **api:8000**. There is **no** scrape job for the Celery worker(s). So whatever the workers have in memory is never collected.

3. **Where does record_task_execution run?**  
   In code, `record_task_execution()` is called from `personal_assistant.workers.utils.metrics` (the task metrics collector used when a **worker** finishes a task). So the only process that has non-empty task metrics is the worker; that process has no HTTP `/metrics` endpoint.

### Conclusion (Task dashboard)

| Check | Result | Meaning |
|-------|--------|--------|
| API /metrics has task_* HELP/TYPE but no task_*{...} series | Expected | API never records task runs; only workers do. |
| Prometheus only scrapes api:8000 | By design | Workers are not scrape targets. |
| Task dashboard shows “No data” | Expected | Prometheus has no task execution data because workers don’t expose metrics. |

**Break in the chain:** Task metrics are updated in the **worker process**. Prometheus only scrapes the **API process**. Workers do not expose `/metrics`, so their task data never reaches Prometheus or the Task dashboard. Fixing this later would require either (a) exposing `/metrics` from the worker and adding a Prometheus scrape job for it, or (b) pushing worker metrics to the API or a pushgateway.
