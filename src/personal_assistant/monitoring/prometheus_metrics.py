"""
Prometheus Metrics Service

This module provides comprehensive Prometheus metrics collection for the Personal Assistant
application, including custom business metrics, application health checks, and OAuth
integration metrics.

Key Features:
- HTTP request metrics
- SMS performance metrics
- OAuth integration metrics
- Database health metrics
- System resource metrics
- Business metrics
- Real-time metrics collection
"""

import logging
import time
from typing import Any, Dict, Optional

import psutil
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from prometheus_client.core import CollectorRegistry

logger = logging.getLogger(__name__)


class PrometheusMetricsService:
    """Service for collecting and exposing Prometheus metrics."""

    def __init__(self):
        """Initialize the Prometheus metrics service."""
        self.registry = CollectorRegistry()
        self._initialize_metrics()
        self._start_time = time.time()

    def _initialize_metrics(self):
        """Initialize all Prometheus metrics."""

        # HTTP Request Metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # SMS Metrics
        self.sms_messages_total = Counter(
            "sms_messages_total",
            "Total SMS messages processed",
            ["status", "provider"],
            registry=self.registry,
        )

        self.sms_processing_duration_seconds = Histogram(
            "sms_processing_duration_seconds",
            "SMS processing duration in seconds",
            ["provider"],
            registry=self.registry,
        )

        self.sms_queue_length = Gauge(
            "sms_queue_length", "Current SMS queue length", registry=self.registry
        )

        self.sms_success_rate = Gauge(
            "sms_success_rate", "SMS success rate percentage", registry=self.registry
        )

        self.sms_cost_total = Counter(
            "sms_cost_total",
            "Total SMS costs in USD",
            ["provider"],
            registry=self.registry,
        )

        # OAuth Metrics
        self.oauth_integrations_active = Gauge(
            "oauth_integrations_active",
            "Number of active OAuth integrations",
            ["provider"],
            registry=self.registry,
        )

        self.oauth_token_refresh_total = Counter(
            "oauth_token_refresh_total",
            "Total OAuth token refresh attempts",
            ["provider", "status"],
            registry=self.registry,
        )

        self.oauth_errors_total = Counter(
            "oauth_errors_total",
            "Total OAuth errors",
            ["provider", "error_type"],
            registry=self.registry,
        )

        self.oauth_operation_duration_seconds = Histogram(
            "oauth_operation_duration_seconds",
            "OAuth operation duration in seconds",
            ["provider", "operation"],
            registry=self.registry,
        )

        # Database Metrics
        self.database_connections_active = Gauge(
            "database_connections_active",
            "Number of active database connections",
            registry=self.registry,
        )

        self.database_connection_pool_utilization = Gauge(
            "database_connection_pool_utilization",
            "Database connection pool utilization percentage",
            registry=self.registry,
        )

        self.database_response_time_seconds = Histogram(
            "database_response_time_seconds",
            "Database response time in seconds",
            registry=self.registry,
        )

        self.database_query_duration_seconds = Histogram(
            "database_query_duration_seconds",
            "Database query duration in seconds",
            ["query_type"],
            registry=self.registry,
        )

        self.database_health_status = Gauge(
            "database_health_status",
            "Database health status (1=healthy, 0=unhealthy)",
            registry=self.registry,
        )

        # System Metrics
        self.system_cpu_usage_percent = Gauge(
            "system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )

        self.system_memory_usage_bytes = Gauge(
            "system_memory_usage_bytes",
            "System memory usage in bytes",
            registry=self.registry,
        )

        self.system_disk_usage_percent = Gauge(
            "system_disk_usage_percent",
            "System disk usage percentage",
            registry=self.registry,
        )

        self.system_network_io_bytes = Counter(
            "system_network_io_bytes",
            "System network I/O bytes",
            ["direction"],
            registry=self.registry,
        )

        self.system_uptime_seconds = Gauge(
            "system_uptime_seconds", "System uptime in seconds", registry=self.registry
        )

        # Application Metrics
        self.active_sessions = Gauge(
            "active_sessions", "Number of active user sessions", registry=self.registry
        )

        self.api_response_time_seconds = Histogram(
            "api_response_time_seconds",
            "API response time in seconds",
            ["endpoint"],
            registry=self.registry,
        )

        self.api_error_rate = Gauge(
            "api_error_rate",
            "API error rate percentage",
            ["endpoint"],
            registry=self.registry,
        )

        self.application_health_status = Gauge(
            "application_health_status",
            "Application health status (1=healthy, 0=unhealthy)",
            registry=self.registry,
        )

        # Business Metrics
        self.user_registrations_total = Counter(
            "user_registrations_total",
            "Total user registrations",
            registry=self.registry,
        )

        self.phone_verifications_total = Counter(
            "phone_verifications_total",
            "Total phone number verifications",
            ["status"],
            registry=self.registry,
        )

        self.oauth_adoption_rate = Gauge(
            "oauth_adoption_rate",
            "OAuth integration adoption rate percentage",
            registry=self.registry,
        )

        self.sms_usage_per_user = Gauge(
            "sms_usage_per_user", "Average SMS usage per user", registry=self.registry
        )

        # Task Metrics
        self.task_execution_duration_seconds = Histogram(
            "task_execution_duration_seconds",
            "Task execution duration in seconds",
            ["task_type"],
            registry=self.registry,
        )

        self.task_success_rate = Gauge(
            "task_success_rate",
            "Task success rate percentage",
            ["task_type"],
            registry=self.registry,
        )

        self.task_queue_length = Gauge(
            "task_queue_length",
            "Current task queue length",
            ["queue_name"],
            registry=self.registry,
        )

    def update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage_percent.set(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage_bytes.set(memory.used)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self.system_disk_usage_percent.set(disk_percent)

            # Network I/O
            network = psutil.net_io_counters()
            self.system_network_io_bytes.labels(direction="sent").inc(
                network.bytes_sent
            )
            self.system_network_io_bytes.labels(direction="received").inc(
                network.bytes_recv
            )

            # Uptime
            uptime = time.time() - self._start_time
            self.system_uptime_seconds.set(uptime)

        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")

    def record_http_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status=str(status_code)
        ).inc()

        self.http_request_duration_seconds.labels(
            method=method, endpoint=endpoint
        ).observe(duration)

    def record_sms_message(
        self, status: str, provider: str, duration: Optional[float] = None, cost: Optional[float] = None
    ):
        """Record SMS message metrics."""
        self.sms_messages_total.labels(status=status, provider=provider).inc()

        if duration is not None:
            self.sms_processing_duration_seconds.labels(provider=provider).observe(
                duration
            )

        if cost is not None:
            self.sms_cost_total.labels(provider=provider).inc(cost)

    def record_oauth_operation(
        self, provider: str, operation: str, duration: float, success: bool
    ):
        """Record OAuth operation metrics."""
        self.oauth_operation_duration_seconds.labels(
            provider=provider, operation=operation
        ).observe(duration)

        if not success:
            self.oauth_errors_total.labels(
                provider=provider, error_type=operation
            ).inc()

    def record_oauth_token_refresh(self, provider: str, success: bool):
        """Record OAuth token refresh metrics."""
        status = "success" if success else "failure"
        self.oauth_token_refresh_total.labels(provider=provider, status=status).inc()

    def record_database_operation(self, query_type: str, duration: float):
        """Record database operation metrics."""
        self.database_query_duration_seconds.labels(query_type=query_type).observe(
            duration
        )

    def record_task_execution(self, task_type: str, duration: float, success: bool):
        """Record task execution metrics."""
        self.task_execution_duration_seconds.labels(task_type=task_type).observe(
            duration
        )

    def update_oauth_integrations(self, provider_counts: Dict[str, int]):
        """Update OAuth integration counts."""
        for provider, count in provider_counts.items():
            self.oauth_integrations_active.labels(provider=provider).set(count)

    def update_database_health(
        self, healthy: bool, connections: Optional[int] = None, pool_utilization: Optional[float] = None
    ):
        """Update database health metrics."""
        self.database_health_status.set(1 if healthy else 0)

        if connections is not None:
            self.database_connections_active.set(connections)

        if pool_utilization is not None:
            self.database_connection_pool_utilization.set(pool_utilization)

    def update_application_health(self, healthy: bool, active_sessions: Optional[int] = None):
        """Update application health metrics."""
        self.application_health_status.set(1 if healthy else 0)

        if active_sessions is not None:
            self.active_sessions.set(active_sessions)

    def update_business_metrics(self, metrics: Dict[str, Any]):
        """Update business metrics."""
        if "user_registrations" in metrics:
            self.user_registrations_total.inc(metrics["user_registrations"])

        if "phone_verifications" in metrics:
            for status, count in metrics["phone_verifications"].items():
                self.phone_verifications_total.labels(status=status).inc(count)

        if "oauth_adoption_rate" in metrics:
            self.oauth_adoption_rate.set(metrics["oauth_adoption_rate"])

        if "sms_usage_per_user" in metrics:
            self.sms_usage_per_user.set(metrics["sms_usage_per_user"])

    def update_sms_metrics(self, queue_length: Optional[int] = None, success_rate: Optional[float] = None):
        """Update SMS metrics."""
        if queue_length is not None:
            self.sms_queue_length.set(queue_length)

        if success_rate is not None:
            self.sms_success_rate.set(success_rate)

    def update_task_metrics(
        self,
        queue_lengths: Optional[Dict[str, int]] = None,
        success_rates: Optional[Dict[str, float]] = None,
    ):
        """Update task metrics."""
        if queue_lengths:
            for queue_name, length in queue_lengths.items():
                self.task_queue_length.labels(queue_name=queue_name).set(length)

        if success_rates:
            for task_type, rate in success_rates.items():
                self.task_success_rate.labels(task_type=task_type).set(rate)

    def generate_metrics(self) -> str:
        """Generate Prometheus-formatted metrics."""
        # Update system metrics before generating
        self.update_system_metrics()

        return generate_latest(self.registry).decode('utf-8')

    def get_metrics_content_type(self) -> str:
        """Get the content type for metrics response."""
        return CONTENT_TYPE_LATEST


# Global metrics service instance
metrics_service = PrometheusMetricsService()


def get_metrics_service() -> PrometheusMetricsService:
    """Get the global metrics service instance."""
    return metrics_service
