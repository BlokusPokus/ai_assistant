# Task 106: Grafana Dashboards Refinement – Onboarding

Use this file to onboard yourself (or a new session) to the task. It records scope, findings, and references so work can continue without re-discovering everything.

---

## Task goal

Refine the Grafana setup end-to-end:

1. Find every aspect of Grafana that is used (dashboards, datasources, alerting, provisioning).
2. Find issues and possible optimizations.
3. Make a plan (in README).
4. Execute an implementation plan step by step (IMPLEMENTATION_PLAN.md).

---

## Context

- **Task 057** created 6 Grafana dashboards (application, business, oauth, sms, system, task), a single Prometheus datasource, and dashboard provisioning. Alert YAMLs were added under `grafana/alerting/` in Prometheus rule format.
- **Prometheus** in dev scrapes the API (`api:8000/metrics`); postgres and node jobs exist but need exporters (usually no data in dev).
- **Grafana** in dev is at http://localhost:3005; provisioning mounts only `dashboards/` and `datasources/`. The `alerting/` folder is **not** mounted into Prometheus, and `prometheus.yml` has `rule_files` commented out, so **no alerts are loaded**.
- **Loki** runs in dev compose but **no Loki datasource** is provisioned in Grafana.

---

## Every aspect of Grafana in use (catalogue)

### Provisioning

- **Path:** `docker/monitoring/grafana/`
- **dashboards/dashboards.yml:** Provider "Personal Assistant", folder "Personal Assistant", path `/etc/grafana/provisioning/dashboards`, updateIntervalSeconds 10, allowUiUpdates true.
- **dashboards/*.json:** 6 files: application-dashboard.json, business-dashboard.json, oauth-dashboard.json, sms-dashboard.json, system-dashboard.json, task-dashboard.json.
- **datasources/prometheus.yml:** One Prometheus datasource, url `http://prometheus:9090`, access proxy, isDefault true, queryTimeout 60s, timeInterval 15s.

### Alerting (current state)

- **Path:** `docker/monitoring/grafana/alerting/`
- **Files:** critical-alerts.yml, warning-alerts.yml, info-alerts.yml (Prometheus rule format).
- **Loaded by:** Neither Prometheus nor Grafana (Prometheus rule_files not set; Grafana does not mount or use these files). So alerts are defined but never evaluated.

### Runtime

- **Compose:** `docker/docker-compose.dev.yml` – service `grafana`, image grafana/grafana:latest, port 3005:3000, volumes for dashboards and datasources only.
- **Prometheus:** Service `prometheus`, config at `docker/monitoring/prometheus.yml`; no rule_files configured.

---

## Issues and optimizations (summary)

- **Alerts not loaded:** Wire rule_files in Prometheus (or move to Grafana-native) and fix expressions.
- **Alert metric mismatches:** e.g. `task_execution_total` does not exist; app has `task_execution_duration_seconds`, `task_success_rate`, `task_queue_length`. Full audit in Phase 0 of IMPLEMENTATION_PLAN.
- **Loki datasource missing:** Add Loki datasource provisioning when Loki is in use.
- **System panels:** Use API-exposed system metrics (container scope in Docker); clarify or add variables if node_exporter is added later.
- **Postgres/Node panels:** No data without exporters; fix or document/hide those panels.
- **Dashboard JSON:** Normalize datasource refs and IDs; optional variables and default refresh/time range.
- **Docs:** Document Grafana URL, login, and where provisioning lives; optional dashboard map and runbook.

---

## Key codebase references

| What | Where |
|------|--------|
| Metric definitions (names, labels) | `src/personal_assistant/monitoring/prometheus_metrics.py` |
| Prometheus config (scrape + rule_files) | `docker/monitoring/prometheus.yml` |
| Grafana dashboards | `docker/monitoring/grafana/dashboards/*.json` |
| Grafana datasources | `docker/monitoring/grafana/datasources/prometheus.yml` |
| Alert rule YAMLs | `docker/monitoring/grafana/alerting/*.yml` |
| Grafana in compose | `docker/docker-compose.dev.yml` (grafana service) |
| Task 057 (original dashboards) | `docs/architecture/tasks/057_grafana_dashboards_creation/README.md` |

---

## How to run and test

- Start dev stack (from repo root):  
  `docker compose -f docker/docker-compose.dev.yml --env-file config/development.env up -d`
- Open Grafana: http://localhost:3005 (admin / DEV_GRAFANA_ADMIN_PASSWORD from config/development.env).
- Open Prometheus: http://localhost:9090 (targets, rules, graph).
- After changing provisioning (dashboards/datasources), restart Grafana or reload provisioning. After changing Prometheus rule_files, restart Prometheus.

---

## Implementation order

Follow **IMPLEMENTATION_PLAN.md** in this folder:

- **Phase 0:** Audit (metrics inventory, scrape config, all dashboard/alert exprs, gap list).
- **Phase 1:** Load alert rules in Prometheus; fix every alert expr to use existing metrics.
- **Phase 2:** Add Loki datasource; document optional exporters.
- **Phase 3:** Fix dashboard panel queries in all 6 JSONs; handle postgres/node panels.
- **Phase 4:** Variables and default time/refresh.
- **Phase 5:** Documentation and dashboard map.
- **Phase 6:** Validation and cleanup.

---

## Red lines (do not change without explicit scope change)

- Do not remove or rename metrics in `prometheus_metrics.py` that are still used by dashboards or alerts without updating those queries first.
- Do not change Task 057 dashboard *goals* (application, system, sms, oauth, business, task) unless the task scope is extended; refinement = fix and optimize, not replace with a different set of dashboards.

---

## Open questions / decisions

- **Alert ownership:** Recommended to use Prometheus rule_files for the existing YAML; if the team prefers Grafana-native only, Phase 1 would convert YAML to Grafana provisioned or UI-managed rules.
- **feature_usage_total:** Referenced in info-alerts; confirm in prometheus_metrics.py whether it exists and with which labels; if not, remove or add metric in app.
- **Postgres/Node panels:** Decide per dashboard whether to remove, hide, or keep with “No data” + text explanation until exporters are added.

This onboarding is the single place to record further discoveries (e.g. more metric mismatches) so the next session can continue without re-doing the audit.
