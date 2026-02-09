# Task 106: Grafana Dashboards Refinement

## Task overview

**Task ID:** 106  
**Title:** Grafana dashboards refinement  
**Status:** Implemented (Phases 0–5 done; Phase 6 checklist in VALIDATION_CHECKLIST.md)  
**Dependencies:** Task 057 (Grafana dashboards creation) completed; Prometheus metrics (Task 056) and dev/stage/prod monitoring stack in place.

### Goal

Refine the existing Grafana setup end-to-end: catalogue every aspect in use, find issues and optimization opportunities, agree a plan, then execute an implementation plan step by step so dashboards, datasources, and alerting are correct, consistent, and maintainable.

---

## Scope: every aspect of Grafana in use

### 1. Provisioning and config

| Aspect | Location | Purpose |
|--------|----------|--------|
| **Dashboard provisioning** | `docker/monitoring/grafana/dashboards/dashboards.yml` | Provider config: folder "Personal Assistant", path to JSON dashboards, update interval, allow UI updates. |
| **Dashboard JSONs** | `docker/monitoring/grafana/dashboards/*.json` | 6 dashboards: application, business, oauth, sms, system, task. |
| **Datasource provisioning** | `docker/monitoring/grafana/datasources/` | Prometheus and Loki; path contains `prometheus.yml`, `loki.yml`. |

### 2. Datasources

| Datasource | Provisioned | Used by | Notes |
|------------|-------------|---------|--------|
| **Prometheus** | Yes (`datasources/prometheus.yml`) | All dashboards | Scrapes `api:8000/metrics`; postgres and node jobs present but require exporters (often no data in dev). |
| **Loki** | Yes (`datasources/loki.yml`) | Log panels / Explore | Provisioned; points to `http://loki:3100`. |

### 3. Dashboards (6)

- **application-dashboard.json** – HTTP request rate, response times, errors (Prometheus).
- **business-dashboard.json** – Business metrics (users, features, etc.).
- **oauth-dashboard.json** – OAuth integrations, token refresh, errors.
- **sms-dashboard.json** – SMS volume, success rate, costs.
- **system-dashboard.json** – CPU, memory, disk (app-exposed system metrics).
- **task-dashboard.json** – Task execution, queues.

### 4. Alerting

| Aspect | Location | Loaded by | Notes |
|--------|----------|-----------|--------|
| **Critical alerts** | `docker/monitoring/grafana/alerting/critical-alerts.yml` | Prometheus (rule_files) | Mounted into Prometheus; rules fixed to use existing metrics. |
| **Warning alerts** | `docker/monitoring/grafana/alerting/warning-alerts.yml` | Prometheus (rule_files) | Same as above. |
| **Info alerts** | `docker/monitoring/grafana/alerting/info-alerts.yml` | Prometheus (rule_files) | Mounted into Prometheus; rules fixed to use existing metrics. |

### 5. Runtime (dev)

- **Compose:** `docker/docker-compose.dev.yml` – Grafana service; volumes for `dashboards/` and `datasources/` only (no alerting volume).
- **Port:** 3005 → 3000 (Grafana at http://localhost:3005).
- **Prometheus:** Scrapes API only reliably; postgres/node jobs need exporters for data.

---

## Findings: issues and optimizations

### Critical / blocking

1. **Alert rules never loaded**  
   All alert YAMLs under `grafana/alerting/` are Prometheus-format rules. They are not loaded by Prometheus (`rule_files` commented out in `prometheus.yml`) and are not mounted or used by Grafana. Alerts are effectively disabled.

2. **Alert expressions reference missing or wrong metrics**  
   - `task_execution_total` (info-alerts) – not defined in `prometheus_metrics.py`; app has `task_execution_duration_seconds`, `task_success_rate`, `task_queue_length`.  
   - Other expressions may use labels or metric names that don’t match the app (e.g. `http_request_duration_seconds` vs `http_request_duration_seconds_bucket` for histograms). Need full audit of every alert expr vs `PrometheusMetricsService`.

3. **Loki datasource missing**  
   Loki runs in dev but no Loki datasource is provisioned in Grafana, so no log-based panels or explore.

### High priority

4. **System dashboard scope**  
   System panels use `system_cpu_usage_percent`, `system_memory_usage_bytes` from the **API** container. In Docker this is container-level, not host. If node_exporter is added later, dashboards may need job/label selection (e.g. by `instance` or `job`) to avoid confusion.

5. **Postgres/Node panels**  
   Prometheus is configured to scrape `postgres:5432` and `host.docker.internal:9100` but without postgres_exporter and node_exporter there is no metrics data; any dashboard panels for these will show "No data". Either add exporters, or document and optionally hide/remove those panels for dev.

6. **Dashboard JSON hygiene**  
   - Standardize `id: null` vs fixed IDs to avoid duplicates on re-provisioning.  
   - Ensure all panels use `datasource: "Prometheus"` (or a variable) so they survive datasource renames.  
   - Optional: add a short description/title in dashboard JSON for easier navigation.

### Medium / nice-to-have

7. **Refresh and time range**  
   Dashboards could set a default refresh (e.g. 15s or 30s) and default time range (e.g. last 1h) for consistency.

8. **Variables**  
   Add dashboard variables where useful (e.g. instance, job, endpoint) to filter panels without editing queries.

9. **Folder and naming**  
   dashboards.yml uses folder "Personal Assistant"; align naming with other environments (stage/prod) if different.

10. **Documentation**  
    - README or runbook: how to open Grafana (URL, login), which datasources exist, where provisioning lives.  
    - Optional: one-page “dashboard map” (which dashboard shows what and which metrics it uses).

---

## Plan (high level)

1. **Audit** – List every metric name and label used in dashboards and alert YAMLs; compare to `PrometheusMetricsService` and Prometheus scrape config; document mismatches and fix list.
2. **Alerts** – Decide ownership: Prometheus (rule_files) vs Grafana (provisioned or UI alert rules). Then fix alert rule loading and correct every expression to use existing metrics/labels.
3. **Datasources** – Add Loki datasource provisioning when Loki is in use; optionally add a note or placeholder for future postgres_exporter/node_exporter.
4. **Dashboards** – Fix panels that use wrong/missing metrics; add variables and defaults where useful; normalize IDs and datasource references; handle “No data” for postgres/node until exporters exist.
5. **Docs and ops** – Document URL, login, and “where things live”; add a short dashboard map; optional runbook for adding a new dashboard or alert.

---

## Implementation plan

See **IMPLEMENTATION_PLAN.md** in this folder for a step-by-step implementation plan to apply the changes.

---

## Implemented (Phases 0–5)

- **Phase 0:** **METRICS_INVENTORY.md** added with full app metrics list, scrape jobs, and gap table (dashboard panels + alert rules).
- **Phase 1 – Alerts:** Prometheus loads alert rules from `docker/monitoring/grafana/alerting/` (volume mounted as `/etc/prometheus/rules`). `prometheus.yml` `rule_files` point to critical-, warning-, and info-alerts.yml. Alert expressions fixed: HighSMSCost uses `increase(sms_cost_total[1h])`; FeatureUsageIncrease commented out (metric missing); OAuthIntegrationIncrease uses `sum(oauth_integrations_active)`; TaskExecutionSpike uses `sum(rate(task_execution_duration_seconds_count[5m]))`.
- **Phase 2 – Datasources:** **Loki** datasource added at `docker/monitoring/grafana/datasources/loki.yml` (url `http://loki:3100`). Grafana already mounts the datasources dir.
- **Phase 3 – Dashboards:** Panel exprs updated: system-dashboard `system_network_bytes_total` → `system_network_io_bytes`; application-dashboard `application_active_users` → `active_sessions`; task-dashboard `task_execution_total` → `sum(rate(task_execution_duration_seconds_count[5m])) by (task_type)`; business-dashboard `feature_usage_total` → `user_registrations_total`, `business_revenue_total` → `oauth_adoption_rate` (placeholders until those metrics exist).
- **Phase 4 – Variables and defaults:** Dashboards use default refresh (15s) and time range (last 1h). Application dashboard has an `instance` variable for filtering. docker/README.md corrected to Grafana dev port 3005.
- **Phase 5 – Documentation:** **docker/README.md** updated with Grafana URL (dev 3005), login (admin / DEV_GRAFANA_ADMIN_PASSWORD), and provisioning paths (dashboards, datasources, alert rules in Prometheus). **DASHBOARD_MAP.md** (one-page dashboard → purpose → metrics → scrape job) and **RUNBOOK.md** (add dashboard, add/change alert, add datasource) added in this task folder.

---

## Success criteria

- All alert rules that should be active are loaded (by Prometheus or Grafana) and use only existing metrics/labels.
- Dashboard panels that are kept show correct data or a clear “no exporter” state; no broken queries for metrics that don’t exist.
- Loki datasource provisioned when Loki is part of the stack.
- One place (README or monitoring doc) describes how to access Grafana and where provisioning/config live.
- Implementation is done in small, reviewable steps (see IMPLEMENTATION_PLAN.md).

---

## Grafana logs: "Public dashboard not found" 404

When you open a dashboard, Grafana’s UI requests `/api/dashboards/uid/.../public-dashboards` to see if a public (shareable) link exists. Our dashboards don’t use that feature, so the API returns **404**. That is expected and does not mean the dashboard failed to load. You can ignore these log lines.

## Key files

| Purpose | Path |
|--------|------|
| Dashboard provider | `docker/monitoring/grafana/dashboards/dashboards.yml` |
| Dashboard JSONs | `docker/monitoring/grafana/dashboards/*.json` |
| Datasources | `docker/monitoring/grafana/datasources/` (prometheus.yml, loki.yml) |
| Alert YAMLs | `docker/monitoring/grafana/alerting/*.yml` |
| Prometheus config | `docker/monitoring/prometheus.yml` |
| App metrics definitions | `src/personal_assistant/monitoring/prometheus_metrics.py` |
| Grafana in compose | `docker/docker-compose.dev.yml` (grafana service) |
| **Task docs** | **DASHBOARD_MAP.md**, **RUNBOOK.md**, **METRICS_INVENTORY.md**, **VALIDATION_CHECKLIST.md**, **DIAGNOSTIC.md** (dashboard data troubleshooting) |

---

## Onboarding

Use **onboarding.md** in this folder for full context: scope, findings, and references so a new session can continue the refinement work.
