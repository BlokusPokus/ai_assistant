"""
Enhanced Task Metrics Collection

Provides detailed performance metrics, resource usage tracking,
and performance optimization insights.
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

from personal_assistant.monitoring import get_metrics_service

logger = logging.getLogger(__name__)


@dataclass
class TaskMetrics:
    """Comprehensive metrics for a single task execution."""

    task_id: str
    task_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None
    memory_usage_start: Optional[float] = None
    memory_usage_end: Optional[float] = None
    memory_usage_peak: Optional[float] = None
    cpu_usage_start: Optional[float] = None
    cpu_usage_end: Optional[float] = None
    cpu_usage_peak: Optional[float] = None
    status: str = "running"
    error: Optional[str] = None
    retry_count: int = 0
    queue_time: Optional[float] = None
    worker_id: Optional[str] = None
    queue_name: Optional[str] = None
    priority: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    active_connections: int
    worker_count: int
    queue_lengths: Dict[str, int]


@dataclass
class PerformanceSummary:
    """Performance summary for a specific metric."""

    count: int
    total: float
    average: float
    minimum: float
    maximum: float
    p50: float
    p90: float
    p95: float
    p99: float
    standard_deviation: float


class MetricsCollector:
    """Collects and aggregates task execution metrics."""

    def __init__(self, max_history_size: int = 10000):
        self.metrics: Dict[str, TaskMetrics] = {}
        self.aggregate_stats: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history_size)
        )
        # Keep last 1000 system snapshots
        self.system_metrics: deque = deque(maxlen=1000)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.enabled = True
        self.collection_interval = 30  # seconds

        # Collect initial system metrics
        self._collect_system_metrics()

        # Start background monitoring
        self._start_system_monitoring()

    def start_task(self, task_id: str, task_name: str, **kwargs) -> str:
        """Start tracking a new task execution."""
        if not self.enabled:
            return task_id

        try:
            with self.lock:
                # Get current system metrics
                memory_info = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=0.1)

                metrics = TaskMetrics(
                    task_id=task_id,
                    task_name=task_name,
                    start_time=datetime.utcnow(),
                    memory_usage_start=memory_info.percent,
                    cpu_usage_start=cpu_percent,
                    **kwargs,
                )

                self.metrics[task_id] = metrics
                self.logger.debug(f"Started metrics collection for task: {task_id}")
                return task_id

        except Exception as e:
            self.logger.error(f"Error starting task metrics: {e}")
            return task_id

    def end_task(
        self, task_id: str, status: str = "completed", error: Optional[str] = None
    ):
        """End tracking a task execution."""
        if not self.enabled:
            return

        try:
            with self.lock:
                if task_id in self.metrics:
                    metrics = self.metrics[task_id]
                    metrics.end_time = datetime.utcnow()
                    metrics.execution_time = (
                        metrics.end_time - metrics.start_time
                    ).total_seconds()
                    metrics.status = status
                    metrics.error = error

                    # Get final system metrics
                    memory_info = psutil.virtual_memory()
                    cpu_percent = psutil.cpu_percent(interval=0.1)

                    metrics.memory_usage_end = memory_info.percent
                    metrics.cpu_usage_end = cpu_percent

                    # Calculate peak usage (simplified - in production you'd track this continuously)
                    metrics.memory_usage_peak = max(
                        metrics.memory_usage_start or 0, metrics.memory_usage_end or 0
                    )
                    metrics.cpu_usage_peak = max(
                        metrics.cpu_usage_start or 0, metrics.cpu_usage_end or 0
                    )

                    # Record aggregate statistics
                    if metrics.execution_time is not None:
                        self.aggregate_stats[metrics.task_name].append(
                            metrics.execution_time
                        )

                    # Update Prometheus metrics
                    try:
                        metrics_service = get_metrics_service()
                        metrics_service.record_task_execution(
                            task_type=metrics.task_name,
                            duration=metrics.execution_time,
                            success=(status == "completed"),
                        )
                    except Exception as metrics_error:
                        self.logger.warning(
                            f"Failed to update Prometheus task metrics: {metrics_error}"
                        )

                    # Archive metrics but keep in memory for a short time
                    self._archive_metrics(metrics)

                    # Don't immediately delete - let tests access the completed metrics
                    # In production, you might want to move to a separate completed_metrics dict
                    # del self.metrics[task_id]

                    self.logger.debug(
                        f"Completed metrics collection for task: {task_id} - {status}"
                    )

        except Exception as e:
            self.logger.error(f"Error ending task metrics: {e}")

    def update_task_metrics(self, task_id: str, **kwargs):
        """Update metrics for a running task."""
        if not self.enabled:
            return

        try:
            with self.lock:
                if task_id in self.metrics:
                    metrics = self.metrics[task_id]
                    for key, value in kwargs.items():
                        if hasattr(metrics, key):
                            setattr(metrics, key, value)

        except Exception as e:
            self.logger.error(f"Error updating task metrics: {e}")

    def get_performance_summary(
        self, task_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get performance summary for tasks."""
        try:
            with self.lock:
                if task_name:
                    return self._calculate_summary_for_task(task_name)

                summary = {}
                for task_name, times in self.aggregate_stats.items():
                    summary[task_name] = self._calculate_summary_for_task(task_name)

                return summary

        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {}

    def get_system_metrics(self, hours: int = 1) -> List[SystemMetrics]:
        """Get system metrics for the specified time period."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            with self.lock:
                return [
                    metrics
                    for metrics in self.system_metrics
                    if metrics.timestamp > cutoff_time
                ]

        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return []

    def get_current_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage("/")
            network_info = psutil.net_io_counters()

            # Count active workers (simplified - in production you'd get this from Celery)
            active_workers = len(
                [m for m in self.metrics.values() if m.status == "running"]
            )

            # Get queue lengths (simplified - in production you'd get this from Redis)
            queue_lengths = {
                "ai_tasks": 0,
            }

            system_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": memory_info.percent,
                "memory_available_gb": memory_info.available / (1024**3),
                "disk_usage_percent": disk_info.percent,
                "network_io_bytes_sent": network_info.bytes_sent,
                "network_io_bytes_recv": network_info.bytes_recv,
                "active_workers": active_workers,
                "queue_lengths": queue_lengths,
                "total_tasks_tracked": len(self.metrics),
            }

            # Update Prometheus metrics
            try:
                metrics_service = get_metrics_service()
                metrics_service.update_task_metrics(queue_lengths)
            except Exception as metrics_error:
                self.logger.warning(
                    f"Failed to update Prometheus task metrics: {metrics_error}"
                )

            return system_status

        except Exception as e:
            self.logger.error(f"Error getting current system status: {e}")
            return {}

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in the specified format."""
        try:
            with self.lock:
                if format.lower() == "json":
                    data = {
                        "export_timestamp": datetime.utcnow().isoformat(),
                        "current_tasks": [asdict(m) for m in self.metrics.values()],
                        "performance_summary": self.get_performance_summary(),
                        "system_status": self.get_current_system_status(),
                    }
                    return json.dumps(data, indent=2, default=str)

                elif format.lower() == "csv":
                    # TODO: Implement CSV export
                    return "CSV export not yet implemented"

                else:
                    return f"Unsupported format: {format}"

        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return f"Error exporting metrics: {e}"

    def cleanup_old_metrics(self, max_age_hours: int = 24):
        """Clean up old metrics data."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

            with self.lock:
                # Clean up old system metrics
                original_count = len(self.system_metrics)
                self.system_metrics = deque(
                    [m for m in self.system_metrics if m.timestamp > cutoff_time],
                    maxlen=self.system_metrics.maxlen,
                )

                cleaned_count = original_count - len(self.system_metrics)
                if cleaned_count > 0:
                    self.logger.info(f"Cleaned up {cleaned_count} old system metrics")

        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")

    def reset(self):
        """Reset all metrics data."""
        try:
            with self.lock:
                self.metrics.clear()
                self.aggregate_stats.clear()
                self.system_metrics.clear()
                self.logger.info("Metrics collector reset")

        except Exception as e:
            self.logger.error(f"Error resetting metrics collector: {e}")

    def _calculate_summary_for_task(self, task_name: str) -> Dict[str, Any]:
        """Calculate performance summary for a specific task."""
        try:
            times = self.aggregate_stats.get(task_name, deque())
            if not times:
                return {
                    "count": 0,
                    "total": 0,
                    "average": 0,
                    "minimum": 0,
                    "maximum": 0,
                    "p50": 0,
                    "p90": 0,
                    "p95": 0,
                    "p99": 0,
                    "standard_deviation": 0,
                }

            times_list = list(times)
            times_list.sort()

            count = len(times_list)
            total = sum(times_list)
            average = total / count
            minimum = times_list[0]
            maximum = times_list[-1]

            # Calculate percentiles
            p50 = times_list[int(count * 0.5)]
            p90 = times_list[int(count * 0.9)]
            p95 = times_list[int(count * 0.95)]
            p99 = times_list[int(count * 0.99)]

            # Calculate standard deviation
            variance = sum((x - average) ** 2 for x in times_list) / count
            standard_deviation = variance**0.5

            return {
                "count": count,
                "total": total,
                "average": average,
                "minimum": minimum,
                "maximum": maximum,
                "p50": p50,
                "p90": p90,
                "p95": p95,
                "p99": p99,
                "standard_deviation": standard_deviation,
            }

        except Exception as e:
            self.logger.error(f"Error calculating summary for task {task_name}: {e}")
            return {}

    def _archive_metrics(self, metrics: TaskMetrics):
        """Archive completed task metrics."""
        try:
            # In a production system, you might want to store these in a database
            # or send them to a metrics aggregation service
            pass

        except Exception as e:
            self.logger.error(f"Error archiving metrics: {e}")

    def _start_system_monitoring(self):
        """Start background system monitoring."""
        try:

            def monitor_system():
                while self.enabled:
                    try:
                        self._collect_system_metrics()
                        time.sleep(self.collection_interval)
                    except Exception as e:
                        self.logger.error(f"Error in system monitoring: {e}")
                        time.sleep(self.collection_interval)

            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=monitor_system, daemon=True)
            monitor_thread.start()
            self.logger.info("System monitoring started")

        except Exception as e:
            self.logger.error(f"Error starting system monitoring: {e}")

    def _collect_system_metrics(self):
        """Collect current system metrics."""
        try:
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage("/")
            network_info = psutil.net_io_counters()

            # Get active connections (simplified)
            try:
                connections = len(psutil.net_connections())
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                connections = 0

            # Count active workers
            with self.lock:
                active_workers = len(
                    [m for m in self.metrics.values() if m.status == "running"]
                )

            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=psutil.cpu_percent(interval=0.1),
                memory_percent=memory_info.percent,
                memory_available=memory_info.available / (1024**3),  # GB
                disk_usage_percent=disk_info.percent,
                network_io={
                    "bytes_sent": network_info.bytes_sent,
                    "bytes_recv": network_info.bytes_recv,
                    "packets_sent": network_info.packets_sent,
                    "packets_recv": network_info.packets_recv,
                },
                active_connections=connections,
                worker_count=active_workers,
                queue_lengths={
                    "ai_tasks": 0,
                },
            )

            with self.lock:
                self.system_metrics.append(metrics)

        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")

    def enable(self):
        """Enable metrics collection."""
        self.enabled = True
        self.logger.info("Metrics collection enabled")

    def disable(self):
        """Disable metrics collection."""
        self.enabled = False
        self.logger.info("Metrics collection disabled")

    def stop_monitoring(self):
        """Stop background system monitoring."""
        self.enabled = False
        self.logger.info("System monitoring stopped")


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def start_task_metrics(task_id: str, task_name: str, **kwargs) -> str:
    """Start metrics collection for a task."""
    return get_metrics_collector().start_task(task_id, task_name, **kwargs)


def end_task_metrics(
    task_id: str, status: str = "completed", error: Optional[str] = None
):
    """End metrics collection for a task."""
    get_metrics_collector().end_task(task_id, status, error)


def update_task_metrics(task_id: str, **kwargs):
    """Update metrics for a running task."""
    get_metrics_collector().update_task_metrics(task_id, **kwargs)
