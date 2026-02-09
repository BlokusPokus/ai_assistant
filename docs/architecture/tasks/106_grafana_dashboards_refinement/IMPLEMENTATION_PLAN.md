# Task 106 – Grafana Dashboards Refinement: Implementation Plan

Apply changes step by step. Each phase can be a single PR or checkpoint.

---

## Phase 0 – Audit (no code changes yet)

**Goal:** Single source of truth for “what exists” vs “what dashboards/alerts use.”

### Step 0.1 – List all metrics and labels from the app

- From `src/personal_assistant/monitoring/prometheus_metrics.py`, list every metric name and its labels (e.g. `http_requests_total{method,endpoint,status}`).
- Optionally run the app, hit `GET /metrics`, and capture one snapshot to confirm names and labels.
- **Output:** `docs/architecture/tasks/106_grafana_dashboards_refinement/METRICS_INVENTORY.md` (or a table in onboarding.md) with: metric name, type (Counter/Gauge/Histogram), labels.

### Step 0.2 – List all Prometheus scrape jobs and targets

- From `docker/monitoring/prometheus.yml`, list job names and targets (api, postgres, node, etc.) and note which have exporters (api has /metrics; postgres/node need exporters).
- **Output:** Short note in METRICS_INVENTORY or README: which jobs actually produce data in dev.

### Step 0.3 – Extract every query and alert expression from Grafana

- For each dashboard JSON in `docker/monitoring/grafana/dashboards/*.json`, list every panel’s `targets[].expr` (and legendFormat if relevant).
- For each alert YAML in `docker/monitoring/grafana/alerting/*.yml`, list every `expr` and the metric names it uses.
- **Output:** List of unique metric names and histogram/counter names used in queries; mark which are in METRICS_INVENTORY and which are not (or have different labels).

### Step 0.4 – Document mismatches

- Create a short “Gap list”: alert exprs or dashboard queries that use non-existent metrics or wrong labels; panels that expect postgres/node data with no exporter.
- **Output:** Add a “Gaps and fix list” section to README or METRICS_INVENTORY; reference it in the next phases.

---

## Phase 1 – Alert rules: load and fix

**Goal:** Alerts are actually evaluated and use only existing metrics.

### Step 1.1 – Decide where alerts run

- **Option A – Prometheus:** Mount alert YAMLs and set `rule_files` in `prometheus.yml`; use Prometheus for evaluation; Grafana can show “Alerting” from Prometheus.
- **Option B – Grafana:** Convert to Grafana-native alert rules (provisioned or in DB) and use Grafana’s alerting engine.
- **Recommendation:** Option A is simpler with existing YAML; keep one place (Prometheus) for rule definitions.

### Step 1.2 – Wire Prometheus to alert rules

- Copy or symlink `docker/monitoring/grafana/alerting/*.yml` into a path Prometheus can read (e.g. `docker/monitoring/prometheus_rules/` or keep under `grafana/alerting` and mount that into the Prometheus container).
- In `docker/monitoring/prometheus.yml`, set `rule_files` to that path (e.g. `rule_files: ["/etc/prometheus/rules/*.yml"]` and mount the dir).
- Restart Prometheus; confirm in Prometheus UI → Status → Rules that rules appear and evaluate (or show “no data” where expected).

### Step 1.3 – Fix critical-alerts.yml

- For each rule in `critical-alerts.yml`, ensure `expr` uses only metrics and labels from METRICS_INVENTORY.
- Fix or remove:
  - `HighCPUUsage` / `HighMemoryUsage` – confirm metric names (e.g. `system_cpu_usage_percent`, `system_memory_usage_bytes`) and unit (bytes vs GB in expr).
  - `DatabaseConnectionFailure` – `database_health_status == 0`; confirm this exists and is updated by the app.
  - `ServiceDown` – `up == 0`; ensure `up` is present for the jobs you care about (e.g. `personal_assistant_api`).
- Re-run Step 0.3/0.4 for this file and validate in Prometheus.

### Step 1.4 – Fix warning-alerts.yml

- `HighResponseTime` – use the actual histogram name (e.g. `http_request_duration_seconds_bucket`) with `histogram_quantile(0.95, rate(...))`; confirm label names.
- `SMSSuccessRateLow` – `sms_success_rate` exists as Gauge; ensure threshold and labels match.
- `OAuthTokenRefreshFailure` – `oauth_token_refresh_total{status="failure"}`; confirm label value.
- `TaskQueueBacklog` – `task_queue_length` exists; confirm label `queue_name` and threshold.
- Fix or drop any expr that references non-existent metrics.

### Step 1.5 – Fix info-alerts.yml

- `UserRegistrationSpike` – `user_registrations_total` (Counter); rate exists.
- `HighSMSCost` – `sms_cost_total` (Counter); alert on increase or use recording rule if needed.
- `FeatureUsageIncrease` – `feature_usage_total`; confirm this metric exists in the app; if not, remove or replace.
- `OAuthIntegrationIncrease` – `oauth_integrations_active` (Gauge); confirm.
- `TaskExecutionSpike` – **remove or replace:** `task_execution_total` does not exist; consider `rate(task_execution_duration_seconds_count[5m])` or similar if you add a counter later.

### Step 1.6 – Smoke test alerts

- Trigger a condition if possible (e.g. high error rate) or at least confirm in Prometheus → Alerts that rules evaluate (no “query error”) and states are OK/Pending/Firing as expected.

---

## Phase 2 – Datasources

**Goal:** Grafana has the right datasources; no broken references.

### Step 2.1 – Add Loki datasource (dev/stage where Loki runs)

- Create `docker/monitoring/grafana/datasources/loki.yml` (or add to existing provisioning) with a Loki datasource pointing to the Loki service URL (e.g. `http://loki:3100` for Docker).
- Ensure Grafana compose volume includes this file (datasources dir is already mounted).
- Restart Grafana; confirm in Configuration → Data sources that Loki appears and “Save & test” succeeds.

### Step 2.2 – Document optional datasources

- In README or monitoring doc, note that postgres_exporter and node_exporter are optional; when added, Prometheus scrape config and (if needed) extra Grafana datasources or panels can be added in a follow-up.

---

## Phase 3 – Dashboards: queries and panels

**Goal:** No panel uses a non-existent metric; “No data” is intentional where exporters are missing.

### Step 3.1 – Application dashboard

- Open `application-dashboard.json`; for each panel, set `expr` and legend to match METRICS_INVENTORY (e.g. `http_requests_total`, `http_request_duration_seconds_bucket` with correct labels).
- Ensure histogram panels use `rate(..._bucket[...])` and `histogram_quantile` where needed.
- Add a short description in the dashboard JSON if desired.

### Step 3.2 – System dashboard

- Confirm every panel uses only app-exposed system metrics (`system_cpu_usage_percent`, `system_memory_usage_bytes`, etc.) or add a note that this is “API container” scope.
- If you later add node_exporter, consider a variable for `job`/`instance` and use it in queries.

### Step 3.3 – SMS, OAuth, Business, Task dashboards

- For each JSON, walk panels and align every `expr` with METRICS_INVENTORY; fix or remove panels that reference missing metrics.
- For task dashboard, use `task_execution_duration_seconds`, `task_success_rate`, `task_queue_length` (not `task_execution_total` unless you add it).

### Step 3.4 – Panels that expect postgres/node

- Either remove panels that depend on postgres or node metrics, or add a text panel explaining “Enable postgres_exporter / node_exporter for data.” Optionally use a variable to hide them when no data.

### Step 3.5 – Dashboard JSON hygiene

- Set consistent `id: null` (or stable UIDs) and `datasource: "Prometheus"` (or `"${datasource}"` variable) so re-provisioning doesn’t duplicate or break panels.
- Set default `refresh` and `time` range in each dashboard JSON if desired.

---

## Phase 4 – Variables and defaults

**Goal:** Easier filtering and consistent UX.

### Step 4.1 – Add dashboard variables where useful

- e.g. `instance`, `job`, `endpoint` from Prometheus labels; add to dashboards that would benefit from filtering.
- Use variables in panel queries (e.g. `job=~"$job"`) and test.

### Step 4.2 – Default time range and refresh

- Set `time.from` / `time.to` and `refresh` in dashboard JSON (e.g. last 1h, 30s refresh) for consistency.

---

## Phase 5 – Documentation and ops

**Goal:** Anyone can find how to use Grafana and where to change things.

### Step 5.1 – Grafana access and config

- In `docker/README.md` (or a dedicated monitoring doc), add: URL (e.g. http://localhost:3005 for dev), login (admin / DEV_GRAFANA_ADMIN_PASSWORD), and where provisioning lives: `docker/monitoring/grafana/` (dashboards, datasources, and that alert rules are in Prometheus rule_files).

### Step 5.2 – Dashboard map

- One-page list: dashboard name → purpose → main metrics used (and which scrape job they come from). Kept in this task folder or under `docs/monitoring/`.

### Step 5.3 – Runbook (optional)

- Short runbook: “Add a new dashboard” (copy JSON, add to provisioning path, restart or reload); “Add a new alert” (add YAML, update rule_files, reload Prometheus).

---

## Phase 6 – Validation and cleanup

### Step 6.1 – Full validation

- Start dev stack with `--env-file config/development.env`; open Grafana; open each dashboard and confirm no “query error” and that panels show data or expected “No data.”
- In Prometheus, confirm all rule_files load and rules evaluate; trigger one alert if possible.

### Step 6.2 – Cleanup

- Remove or archive any unused alert/dashboard files; update README if you moved alert rules to Prometheus only (e.g. “Alert rules now live under prometheus_rules/ and are loaded by Prometheus”).

---

## Order summary

| Phase | Focus |
|-------|--------|
| 0 | Audit: metrics inventory, scrape config, dashboard/alert exprs, gap list |
| 1 | Alerts: load rules in Prometheus; fix all alert exprs to use existing metrics |
| 2 | Datasources: add Loki; document optional exporters |
| 3 | Dashboards: fix queries in all 6 JSONs; handle postgres/node panels |
| 4 | Variables and defaults (time range, refresh) |
| 5 | Documentation and dashboard map |
| 6 | Validation and cleanup |

Work in order; each phase can be a checkpoint before moving to the next.
