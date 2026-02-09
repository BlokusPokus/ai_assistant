# Grafana dashboard map

One-page reference: dashboard name, purpose, main metrics, and scrape job. API metrics come from **`personal_assistant_api`** (api:8000/metrics); task metrics come from **`celery_worker`** (worker:9091/metrics).

| Dashboard | Purpose | Main metrics | Scrape job |
|-----------|---------|--------------|------------|
| **System** | Infrastructure and resource utilization (API container scope) | `system_cpu_usage_percent`, `system_memory_usage_bytes`, `system_disk_usage_percent`, `system_network_io_bytes`, `system_uptime_seconds` | personal_assistant_api |
| **Application** | API performance and health | `http_requests_total`, `http_request_duration_seconds`, `active_sessions`, `database_health_status`, `database_connections_active`, `application_health_status`, `api_response_time_seconds`, `api_error_rate` | personal_assistant_api |
| **Business** | User engagement and adoption | `user_registrations_total`, `oauth_adoption_rate` (placeholders for feature/revenue metrics if added later) | personal_assistant_api |
| **SMS** | SMS routing and Twilio integration | `sms_messages_total`, `sms_processing_duration_seconds`, `sms_queue_length`, `sms_success_rate`, `sms_cost_total` | personal_assistant_api |
| **OAuth** | OAuth provider integrations | `oauth_integrations_active`, `oauth_token_refresh_total`, `oauth_errors_total`, `oauth_operation_duration_seconds` | personal_assistant_api |
| **Task** | Background task processing | `task_execution_duration_seconds` (rate/count), `task_success_rate`, `task_queue_length` | **celery_worker** (worker:9091) |

**Note:** The **celery_worker** job scrapes `worker:9091` (worker exposes `/metrics` via a daemon HTTP server; see Task 106 Option A). The **postgres** job is scraped from `postgres_exporter:9187` (postgres_exporter service in `docker-compose.dev.yml`; connects to Postgres on the host). **node** job: for host-level metrics, run [node_exporter](https://github.com/prometheus/node_exporter) on your machine and ensure port 9100 is reachable from Docker (e.g. `host.docker.internal:9100`); otherwise those panels show "No data".
