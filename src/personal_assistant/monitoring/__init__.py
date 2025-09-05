"""
Personal Assistant Monitoring Module

This module provides comprehensive monitoring capabilities for the Personal Assistant
application, including Prometheus metrics collection, health monitoring, and performance
tracking.

Key Components:
- PrometheusMetricsService: Prometheus metrics collection and exposure
- Health monitoring integration
- Performance metrics collection
- System resource monitoring
"""

from .prometheus_metrics import (
    PrometheusMetricsService,
    get_metrics_service,
    metrics_service,
)

__all__ = ["PrometheusMetricsService", "metrics_service", "get_metrics_service"]
