"""
Middleware to record HTTP request metrics for Prometheus/Grafana.

Records request count, status, and duration so the Application dashboard
shows HTTP Request Rate, Response Time Percentiles, and Error Rate.
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """Records http_requests_total and http_request_duration_seconds for every request."""

    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        try:
            from personal_assistant.monitoring import get_metrics_service

            metrics = get_metrics_service()
            method = request.method
            path = request.url.path or "/"
            status = response.status_code
            metrics.record_http_request(
                method=method,
                endpoint=path,
                status_code=status,
                duration=duration,
            )
        except Exception as e:
            logger.debug("Failed to record HTTP metrics: %s", e)
        return response
