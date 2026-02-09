# Phase 6 – Validation checklist

Use this after Phases 0–5 to confirm the dev stack is correct.

## Config wiring (already verified)

- **Prometheus** `docker/monitoring/prometheus.yml`: `rule_files` point to `/etc/prometheus/rules/*.yml`.
- **Compose** `docker/docker-compose.dev.yml`: Prometheus mounts `./monitoring/grafana/alerting:/etc/prometheus/rules:ro`.
- **Alert YAMLs** exist: `critical-alerts.yml`, `warning-alerts.yml`, `info-alerts.yml`.
- **Datasources**: `grafana/datasources/prometheus.yml`, `loki.yml`.
- **Dashboards**: 6 JSONs in `grafana/dashboards/` + `dashboards.yml`.

## Manual validation (run when you have the dev stack up)

1. **Start dev stack**  
   From repo root:  
   `docker compose -f docker/docker-compose.dev.yml --env-file config/development.env up -d`

2. **Prometheus rules**  
   - Open http://localhost:9090 → Status → Rules.  
   - Confirm all three rule files are listed and rules show state (OK / Pending / no "query error").  
   - If any rule shows a query error, fix the `expr` in the corresponding YAML (see METRICS_INVENTORY.md).

3. **Grafana**  
   - Open http://localhost:3005, log in (admin / DEV_GRAFANA_ADMIN_PASSWORD).  
   - Configuration → Data sources: Prometheus and Loki should be present; "Save & test" for each should succeed.  
   - Dashboards → Personal Assistant: open each of the 6 dashboards.  
   - Confirm no panel shows "query error"; panels either show data (from `personal_assistant_api`) or expected "No data" (e.g. postgres/node if exporters are not running).

4. **Optional: trigger an alert**  
   If you can trigger a condition (e.g. high error rate or bring API down), check Prometheus → Alerts and confirm the alert state changes as expected.

## Cleanup

No files were moved or archived. Alert rules remain under `docker/monitoring/grafana/alerting/` and are loaded by Prometheus via the mount above. If you later add a separate `prometheus_rules/` directory and move rules there, update `prometheus.yml` and this README accordingly.
