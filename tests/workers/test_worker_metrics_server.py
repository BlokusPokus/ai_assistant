"""
Tests for the worker Prometheus metrics HTTP server (Option A: worker exposes /metrics).

Phase 1 TDD: tests drive the implementation of a small HTTP server in the worker process
that serves GET /metrics using the same registry updated by record_task_execution.
"""

import pytest
import requests


class TestWorkerMetricsServer:
    """Test that the worker metrics server returns valid Prometheus exposition format."""

    def test_metrics_endpoint_returns_200_and_prometheus_format(self):
        """GET /metrics returns 200 and body contains Prometheus exposition format (# TYPE)."""
        from personal_assistant.workers.metrics_server import start_metrics_server

        port = start_metrics_server(port=0)
        try:
            response = requests.get(f"http://127.0.0.1:{port}/metrics", timeout=2)
            assert response.status_code == 200
            assert "text/plain" in response.headers.get("Content-Type", "")
            assert "# TYPE" in response.text
        finally:
            from personal_assistant.workers.metrics_server import stop_metrics_server
            stop_metrics_server()

    def test_metrics_includes_task_series_after_record_task_execution(self):
        """After record_task_execution(), GET /metrics body contains at least one task metric series."""
        from personal_assistant.workers.metrics_server import start_metrics_server
        from personal_assistant.monitoring import get_metrics_service

        # Record a task so the worker's registry has task_* series
        get_metrics_service().record_task_execution(
            task_type="test_task", duration=1.0, success=True
        )

        port = start_metrics_server(port=0)
        try:
            response = requests.get(f"http://127.0.0.1:{port}/metrics", timeout=2)
            assert response.status_code == 200
            # Must have at least one actual series (line starting with task_ metric name), not just # HELP / # TYPE
            lines = [line for line in response.text.splitlines() if line and not line.startswith("#")]
            task_series = [l for l in lines if l.startswith("task_execution_duration_seconds") or l.startswith("task_success_rate{")]
            assert len(task_series) >= 1, f"Expected at least one task_* series in metrics, got: {lines[:20]}"
        finally:
            from personal_assistant.workers.metrics_server import stop_metrics_server
            stop_metrics_server()
