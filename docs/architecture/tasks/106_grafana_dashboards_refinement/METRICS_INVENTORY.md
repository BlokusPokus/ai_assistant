# Task 106 – Metrics inventory and gaps

Source: `src/personal_assistant/monitoring/prometheus_metrics.py` and Prometheus scrape config. Histograms expose `_bucket`, `_count`, `_sum`.

## App metrics (from API /metrics)

| Metric name | Type | Labels | Exposed by job |
|-------------|------|--------|----------------|
| http_requests_total | Counter | method, endpoint, status | personal_assistant_api |
| http_request_duration_seconds | Histogram | method, endpoint | personal_assistant_api |
| sms_messages_total | Counter | status, provider | personal_assistant_api |
| sms_processing_duration_seconds | Histogram | provider | personal_assistant_api |
| sms_queue_length | Gauge | — | personal_assistant_api |
| sms_success_rate | Gauge | — | personal_assistant_api |
| sms_cost_total | Counter | provider | personal_assistant_api |
| oauth_integrations_active | Gauge | provider | personal_assistant_api |
| oauth_token_refresh_total | Counter | provider, status | personal_assistant_api |
| oauth_errors_total | Counter | provider, error_type | personal_assistant_api |
| oauth_operation_duration_seconds | Histogram | provider, operation | personal_assistant_api |
| database_connections_active | Gauge | — | personal_assistant_api |
| database_connection_pool_utilization | Gauge | — | personal_assistant_api |
| database_response_time_seconds | Histogram | — | personal_assistant_api |
| database_query_duration_seconds | Histogram | query_type | personal_assistant_api |
| database_health_status | Gauge | — | personal_assistant_api |
| system_cpu_usage_percent | Gauge | — | personal_assistant_api |
| system_memory_usage_bytes | Gauge | — | personal_assistant_api |
| system_disk_usage_percent | Gauge | — | personal_assistant_api |
| system_network_io_bytes | Counter | direction | personal_assistant_api |
| system_uptime_seconds | Gauge | — | personal_assistant_api |
| active_sessions | Gauge | — | personal_assistant_api |
| api_response_time_seconds | Histogram | endpoint | personal_assistant_api |
| api_error_rate | Gauge | endpoint | personal_assistant_api |
| application_health_status | Gauge | — | personal_assistant_api |
| user_registrations_total | Counter | — | personal_assistant_api |
| phone_verifications_total | Counter | status | personal_assistant_api |
| oauth_adoption_rate | Gauge | — | personal_assistant_api |
| sms_usage_per_user | Gauge | — | personal_assistant_api |
| task_execution_duration_seconds | Histogram | task_type | personal_assistant_api |
| task_success_rate | Gauge | task_type | personal_assistant_api |
| task_queue_length | Gauge | queue_name | personal_assistant_api |

Also from Prometheus: `up` (1 if scrape succeeded) for each job.

## Prometheus scrape jobs (dev)

| Job | Target | Has data in dev? |
|-----|--------|------------------|
| prometheus | localhost:9090 | Yes (self) |
| personal_assistant_api | api:8000 | Yes (/metrics) |
| postgres | postgres_exporter:9187 | Yes (postgres_exporter service in docker-compose.dev.yml; connects to host Postgres) |
| node | host.docker.internal:9100 | Optional: run node_exporter on host for host-level system metrics |

## Gaps: dashboard panels

| Dashboard | Panel expr | Issue | Fix |
|-----------|------------|--------|-----|
| system-dashboard | system_network_bytes_total | Metric is system_network_io_bytes (Counter, direction) | Use system_network_io_bytes or sum by (direction) |
| application-dashboard | application_active_users | Metric is active_sessions | Use active_sessions |
| business-dashboard | feature_usage_total | Not defined in app | Remove or use placeholder; add metric later if needed |
| business-dashboard | business_revenue_total | Not defined in app | Remove or use placeholder |
| task-dashboard | task_execution_total | Not defined in app | Use rate(task_execution_duration_seconds_count[5m]) or remove panel |

## Gaps: alert rules

| Alert | Expr | Issue | Fix |
|-------|------|--------|-----|
| HighSMSCost | sms_cost_total > 100 | Counter; value is cumulative. For "cost in period" use increase(sms_cost_total[1h]) | Use increase(sms_cost_total[1h]) > 100 or keep for "total ever" |
| FeatureUsageIncrease | rate(feature_usage_total[1h]) | feature_usage_total does not exist | Remove rule or add metric to app |
| TaskExecutionSpike | rate(task_execution_total[5m]) | task_execution_total does not exist | Use rate(task_execution_duration_seconds_count[5m]) or remove |
| OAuthIntegrationIncrease | oauth_integrations_active > 1000 | Gauge has provider label; need sum() if multiple providers | sum(oauth_integrations_active) > 1000 |

All other alert exprs use existing metrics; critical/warning alert names and thresholds are kept.
