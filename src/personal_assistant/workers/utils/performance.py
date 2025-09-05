"""
Performance Optimization Utilities

Provides resource tuning, scaling strategies, and performance
analysis tools for the background task system.
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ResourceUsage:
    """Resource usage snapshot."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    active_processes: int
    load_average: Tuple[float, float, float]


@dataclass
class PerformanceRecommendation:
    """Performance optimization recommendation."""

    category: str
    priority: str  # "low", "medium", "high", "critical"
    description: str
    impact: str  # "low", "medium", "high"
    effort: str  # "low", "medium", "high"
    estimated_improvement: str
    action_items: List[str]


class PerformanceOptimizer:
    """Analyzes performance and provides optimization recommendations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.resource_history: deque = deque(maxlen=1000)  # Keep last 1000 snapshots
        self.performance_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self.optimization_history: List[PerformanceRecommendation] = []
        self.lock = threading.Lock()
        self.monitoring_enabled = True
        self.collection_interval = 60  # seconds

        # Performance thresholds
        self.thresholds = {
            "cpu_warning": 0.7,  # 70%
            "cpu_critical": 0.9,  # 90%
            "memory_warning": 0.8,  # 80%
            "memory_critical": 0.95,  # 95%
            "disk_warning": 0.8,  # 80%
            "disk_critical": 0.95,  # 95%
            "load_warning": 0.8,  # 80% of CPU cores
            "load_critical": 1.2,  # 120% of CPU cores
        }

        # Start background monitoring
        self._start_monitoring()

    def collect_resource_snapshot(self) -> ResourceUsage:
        """Collect current resource usage snapshot."""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()

            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_io_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_io_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0

            # Network I/O
            network_io = psutil.net_io_counters()
            network_io_sent_mb = (
                network_io.bytes_sent / (1024 * 1024) if network_io else 0
            )
            network_io_recv_mb = (
                network_io.bytes_recv / (1024 * 1024) if network_io else 0
            )

            # Process count
            active_processes = len(psutil.pids())

            # Load average (Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                load_avg = (0.0, 0.0, 0.0)

            snapshot = ResourceUsage(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_info.percent,
                memory_available_gb=memory_info.available / (1024**3),
                disk_io_read_mb=disk_io_read_mb,
                disk_io_write_mb=disk_io_write_mb,
                network_io_sent_mb=network_io_sent_mb,
                network_io_recv_mb=network_io_recv_mb,
                active_processes=active_processes,
                load_average=load_avg,
            )

            # Store snapshot
            with self.lock:
                self.resource_history.append(snapshot)

            return snapshot

        except Exception as e:
            self.logger.error(f"Error collecting resource snapshot: {e}")
            # Return a default ResourceUsage object instead of None
            return ResourceUsage(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                disk_io_read_mb=0.0,
                disk_io_write_mb=0.0,
                network_io_sent_mb=0.0,
                network_io_recv_mb=0.0,
                active_processes=0,
                load_average=(0.0, 0.0, 0.0),
            )

    def analyze_performance(self, hours: int = 1) -> Dict[str, Any]:
        """Analyze performance over the specified time period."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            with self.lock:
                recent_snapshots = [
                    s for s in self.resource_history if s.timestamp > cutoff_time
                ]

            if not recent_snapshots:
                return {"error": "No data available for analysis"}

            # Calculate averages and trends
            analysis = {
                "period_hours": hours,
                "snapshots_count": len(recent_snapshots),
                "averages": self._calculate_averages(recent_snapshots),
                "trends": self._calculate_trends(recent_snapshots),
                "peaks": self._find_peaks(recent_snapshots),
                "bottlenecks": self._identify_bottlenecks(recent_snapshots),
                "recommendations": self._generate_recommendations(recent_snapshots),
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            return {"error": str(e)}

    def get_optimization_recommendations(self) -> List[PerformanceRecommendation]:
        """Get current optimization recommendations."""
        try:
            # Analyze recent performance
            analysis = self.analyze_performance(hours=1)

            if "error" in analysis:
                return []

            # Generate fresh recommendations
            recommendations = self._generate_recommendations(
                list(self.resource_history)[-100:]  # Last 100 snapshots
            )

            # Store recommendations
            with self.lock:
                self.optimization_history.extend(recommendations)

                # Keep only recent recommendations
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.optimization_history = [
                    r
                    for r in self.optimization_history
                    if hasattr(r, "timestamp") and r.timestamp > cutoff_time
                ]

            return recommendations

        except Exception as e:
            self.logger.error(f"Error getting optimization recommendations: {e}")
            return []

    def optimize_worker_configuration(
        self, current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize worker configuration based on current performance."""
        try:
            # Get current system status
            snapshot = self.collect_resource_snapshot()
            if not snapshot:
                return current_config

            # Analyze current load
            cpu_cores = psutil.cpu_count() or 4  # Default to 4 if None
            memory_gb = psutil.virtual_memory().total / (1024**3)

            # Calculate optimal worker counts
            optimal_config = current_config.copy()

            # CPU-based optimization
            if snapshot.cpu_percent > self.thresholds["cpu_warning"]:
                # Reduce concurrency if CPU is high
                for queue in [
                    "ai_tasks",
                    "email_tasks",
                    "file_tasks",
                    "sync_tasks",
                    "maintenance_tasks",
                ]:
                    if f"{queue}_concurrency" in optimal_config:
                        current_concurrency = optimal_config[f"{queue}_concurrency"]
                        optimal_config[f"{queue}_concurrency"] = max(
                            1, int(current_concurrency * 0.8)
                        )
                        logger.info(
                            f"Reduced {queue} concurrency from {current_concurrency} to {optimal_config[f'{queue}_concurrency']}"
                        )

            elif snapshot.cpu_percent < 0.3:  # Low CPU usage
                # Increase concurrency if CPU is low
                for queue in [
                    "ai_tasks",
                    "email_tasks",
                    "file_tasks",
                    "sync_tasks",
                    "maintenance_tasks",
                ]:
                    if f"{queue}_concurrency" in optimal_config:
                        current_concurrency = optimal_config[f"{queue}_concurrency"]
                        optimal_config[f"{queue}_concurrency"] = min(
                            cpu_cores * 2,  # Max 2x CPU cores
                            int(current_concurrency * 1.2),
                        )
                        logger.info(
                            f"Increased {queue} concurrency from {current_concurrency} to {optimal_config[f'{queue}_concurrency']}"
                        )

            # Memory-based optimization
            if snapshot.memory_percent > self.thresholds["memory_warning"]:
                # Reduce memory usage
                optimal_config["worker_max_memory_mb"] = int(
                    memory_gb * 1024 * 0.6
                )  # 60% of total memory
                logger.info(
                    f"Set worker max memory to {optimal_config['worker_max_memory_mb']} MB"
                )

            # Load-based optimization
            avg_load = sum(snapshot.load_average) / 3
            if avg_load > cpu_cores * self.thresholds["load_warning"]:
                # High load - reduce worker count
                for queue in [
                    "ai_tasks",
                    "email_tasks",
                    "file_tasks",
                    "sync_tasks",
                    "maintenance_tasks",
                ]:
                    if f"{queue}_concurrency" in optimal_config:
                        current_concurrency = optimal_config[f"{queue}_concurrency"]
                        optimal_config[f"{queue}_concurrency"] = max(
                            1, int(current_concurrency * 0.7)
                        )
                        logger.info(
                            f"High load detected, reduced {queue} concurrency to {optimal_config[f'{queue}_concurrency']}"
                        )

            return optimal_config

        except Exception as e:
            self.logger.error(f"Error optimizing worker configuration: {e}")
            return current_config

    def get_resource_forecast(self, hours: int = 24) -> Dict[str, Any]:
        """Forecast resource usage based on historical data."""
        try:
            with self.lock:
                if len(self.resource_history) < 10:
                    return {"error": "Insufficient data for forecasting"}

                # Get recent snapshots
                recent_snapshots = list(self.resource_history)[-100:]

                # Calculate trends
                cpu_trend = self._calculate_linear_trend(
                    [s.cpu_percent for s in recent_snapshots]
                )
                memory_trend = self._calculate_linear_trend(
                    [s.memory_percent for s in recent_snapshots]
                )

                # Project forward
                forecast_hours = min(hours, 24)  # Max 24 hours
                current_time = datetime.utcnow()

                forecast: Dict[str, Any] = {
                    "forecast_hours": forecast_hours,
                    "current_time": current_time.isoformat(),
                    "predictions": [],
                }

                for hour in range(1, forecast_hours + 1):
                    future_time = current_time + timedelta(hours=hour)

                    # Simple linear projection (can be enhanced with more sophisticated models)
                    predicted_cpu = max(
                        0, min(100, cpu_trend["slope"] * hour + cpu_trend["intercept"])
                    )
                    predicted_memory = max(
                        0,
                        min(
                            100,
                            memory_trend["slope"] * hour + memory_trend["intercept"],
                        ),
                    )

                    forecast["predictions"].append(
                        {
                            "hour": hour,
                            "timestamp": future_time.isoformat(),
                            "predicted_cpu_percent": round(predicted_cpu, 2),
                            "predicted_memory_percent": round(predicted_memory, 2),
                            "confidence": self._calculate_forecast_confidence(
                                recent_snapshots
                            ),
                        }
                    )

                return forecast

        except Exception as e:
            self.logger.error(f"Error generating resource forecast: {e}")
            return {"error": str(e)}

    def export_performance_report(self, format: str = "json") -> str:
        """Export comprehensive performance report."""
        try:
            # Collect current data
            snapshot = self.collect_resource_snapshot()
            analysis = self.analyze_performance(hours=24)
            recommendations = self.get_optimization_recommendations()
            forecast = self.get_resource_forecast(hours=24)

            report = {
                "report_timestamp": datetime.utcnow().isoformat(),
                "current_status": {
                    "cpu_percent": snapshot.cpu_percent if snapshot else 0,
                    "memory_percent": snapshot.memory_percent if snapshot else 0,
                    "active_processes": snapshot.active_processes if snapshot else 0,
                    "load_average": list(snapshot.load_average)
                    if snapshot
                    else [0, 0, 0],
                },
                "performance_analysis": analysis,
                "optimization_recommendations": [
                    {
                        "category": r.category,
                        "priority": r.priority,
                        "description": r.description,
                        "impact": r.impact,
                        "effort": r.effort,
                        "estimated_improvement": r.estimated_improvement,
                        "action_items": r.action_items,
                    }
                    for r in recommendations
                ],
                "resource_forecast": forecast,
                "system_info": {
                    "cpu_cores": psutil.cpu_count(),
                    "memory_gb": psutil.virtual_memory().total / (1024**3),
                    "disk_gb": psutil.disk_usage("/").total / (1024**3),
                },
            }

            if format.lower() == "json":
                return json.dumps(report, indent=2, default=str)
            else:
                return f"Unsupported format: {format}"

        except Exception as e:
            self.logger.error(f"Error exporting performance report: {e}")
            return f"Error exporting performance report: {e}"

    def _calculate_averages(self, snapshots: List[ResourceUsage]) -> Dict[str, float]:
        """Calculate average values from snapshots."""
        try:
            if not snapshots:
                return {}

            averages = {}
            for field in [
                "cpu_percent",
                "memory_percent",
                "memory_available_gb",
                "disk_io_read_mb",
                "disk_io_write_mb",
                "network_io_sent_mb",
                "network_io_recv_mb",
                "active_processes",
            ]:
                values = [getattr(s, field) for s in snapshots]
                averages[field] = sum(values) / len(values)

            # Calculate average load
            load_values = [s.load_average for s in snapshots]
            avg_load_1m = sum(load[0] for load in load_values) / len(load_values)
            avg_load_5m = sum(load[1] for load in load_values) / len(load_values)
            avg_load_15m = sum(load[2] for load in load_values) / len(load_values)

            averages["load_average_1m"] = avg_load_1m
            averages["load_average_5m"] = avg_load_5m
            averages["load_average_15m"] = avg_load_15m

            return averages

        except Exception as e:
            self.logger.error(f"Error calculating averages: {e}")
            return {}

    def _calculate_trends(
        self, snapshots: List[ResourceUsage]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate trends from snapshots."""
        try:
            if len(snapshots) < 2:
                return {}

            trends = {}

            # Calculate trends for key metrics
            for field in ["cpu_percent", "memory_percent"]:
                values = [getattr(s, field) for s in snapshots]
                trend = self._calculate_linear_trend(values)
                trends[field] = trend

            return trends

        except Exception as e:
            self.logger.error(f"Error calculating trends: {e}")
            return {}

    def _calculate_linear_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate linear trend (slope and intercept) for a series of values."""
        try:
            if len(values) < 2:
                return {"slope": 0, "intercept": values[0] if values else 0}

            n = len(values)
            x_values = list(range(n))

            # Calculate means
            x_mean = sum(x_values) / n
            y_mean = sum(values) / n

            # Calculate slope and intercept
            numerator = sum(
                (x - x_mean) * (y - y_mean) for x, y in zip(x_values, values)
            )
            denominator = sum((x - x_mean) ** 2 for x in x_values)

            if denominator == 0:
                slope = 0.0
            else:
                slope = numerator / denominator

            intercept = y_mean - slope * x_mean

            return {
                "slope": slope,
                "intercept": intercept,
                "direction": "increasing"
                if slope > 0.01
                else "decreasing"
                if slope < -0.01
                else "stable",
            }

        except Exception as e:
            self.logger.error(f"Error calculating linear trend: {e}")
            return {"slope": 0.0, "intercept": 0.0, "direction": "unknown"}

    def _find_peaks(self, snapshots: List[ResourceUsage]) -> Dict[str, Any]:
        """Find peak values in snapshots."""
        try:
            if not snapshots:
                return {}

            peaks = {}
            for field in [
                "cpu_percent",
                "memory_percent",
                "memory_available_gb",
                "disk_io_read_mb",
                "disk_io_write_mb",
                "network_io_sent_mb",
                "network_io_recv_mb",
                "active_processes",
            ]:
                values = [getattr(s, field) for s in snapshots]
                peaks[field] = {
                    "max": max(values),
                    "min": min(values),
                    "range": max(values) - min(values),
                }

            return peaks

        except Exception as e:
            self.logger.error(f"Error finding peaks: {e}")
            return {}

    def _identify_bottlenecks(self, snapshots: List[ResourceUsage]) -> List[str]:
        """Identify performance bottlenecks."""
        try:
            bottlenecks: List[str] = []

            if not snapshots:
                return bottlenecks

            # Get latest snapshot
            latest = snapshots[-1]

            # Check CPU bottleneck
            if latest.cpu_percent > self.thresholds["cpu_critical"]:
                bottlenecks.append("Critical CPU bottleneck - system overloaded")
            elif latest.cpu_percent > self.thresholds["cpu_warning"]:
                bottlenecks.append("High CPU usage - potential bottleneck")

            # Check memory bottleneck
            if latest.memory_percent > self.thresholds["memory_critical"]:
                bottlenecks.append("Critical memory bottleneck - system may crash")
            elif latest.memory_percent > self.thresholds["memory_warning"]:
                bottlenecks.append("High memory usage - potential bottleneck")

            # Check load bottleneck
            cpu_cores = psutil.cpu_count() or 4  # Default to 4 if None
            avg_load = sum(latest.load_average) / 3
            if avg_load > cpu_cores * self.thresholds["load_critical"]:
                bottlenecks.append("Critical load bottleneck - system overloaded")
            elif avg_load > cpu_cores * self.thresholds["load_warning"]:
                bottlenecks.append("High system load - potential bottleneck")

            # Check I/O bottlenecks
            if latest.disk_io_read_mb > 100 or latest.disk_io_write_mb > 100:
                bottlenecks.append("High disk I/O activity - potential I/O bottleneck")

            return bottlenecks

        except Exception as e:
            self.logger.error(f"Error identifying bottlenecks: {e}")
            return []

    def _generate_recommendations(
        self, snapshots: List[ResourceUsage]
    ) -> List[PerformanceRecommendation]:
        """Generate performance optimization recommendations."""
        try:
            recommendations: List[PerformanceRecommendation] = []

            if not snapshots:
                return recommendations

            latest = snapshots[-1]
            cpu_cores = psutil.cpu_count() or 4  # Default to 4 if None
            psutil.virtual_memory().total / (1024**3)

            # CPU optimization recommendations
            if latest.cpu_percent > self.thresholds["cpu_critical"]:
                recommendations.append(
                    PerformanceRecommendation(
                        category="CPU",
                        priority="critical",
                        description="CPU usage is critically high, system performance severely degraded",
                        impact="high",
                        effort="medium",
                        estimated_improvement="20-40% performance improvement",
                        action_items=[
                            "Reduce worker concurrency across all queues",
                            "Implement task prioritization",
                            "Consider adding more CPU cores",
                            "Optimize task execution efficiency",
                        ],
                    )
                )
            elif latest.cpu_percent > self.thresholds["cpu_warning"]:
                recommendations.append(
                    PerformanceRecommendation(
                        category="CPU",
                        priority="high",
                        description="CPU usage is high, performance may be degraded",
                        impact="medium",
                        effort="low",
                        estimated_improvement="10-20% performance improvement",
                        action_items=[
                            "Reduce worker concurrency for non-critical queues",
                            "Implement task batching",
                            "Monitor CPU-intensive tasks",
                        ],
                    )
                )

            # Memory optimization recommendations
            if latest.memory_percent > self.thresholds["memory_critical"]:
                recommendations.append(
                    PerformanceRecommendation(
                        category="Memory",
                        priority="critical",
                        description="Memory usage is critically high, system stability at risk",
                        impact="high",
                        effort="medium",
                        estimated_improvement="Prevent system crashes, improve stability",
                        action_items=[
                            "Reduce worker memory limits",
                            "Implement memory monitoring and alerts",
                            "Consider adding more RAM",
                            "Investigate memory leaks",
                        ],
                    )
                )
            elif latest.memory_percent > self.thresholds["memory_warning"]:
                recommendations.append(
                    PerformanceRecommendation(
                        category="Memory",
                        priority="high",
                        description="Memory usage is high, monitor for potential issues",
                        impact="medium",
                        effort="low",
                        estimated_improvement="5-15% stability improvement",
                        action_items=[
                            "Monitor memory usage trends",
                            "Implement memory cleanup tasks",
                            "Review worker memory allocation",
                        ],
                    )
                )

            # Load optimization recommendations
            avg_load = sum(latest.load_average) / 3
            if avg_load > cpu_cores * self.thresholds["load_critical"]:
                recommendations.append(
                    PerformanceRecommendation(
                        category="System Load",
                        priority="critical",
                        description="System load is critically high, immediate action required",
                        impact="high",
                        effort="medium",
                        estimated_improvement="30-50% performance improvement",
                        action_items=[
                            "Reduce worker count immediately",
                            "Implement load balancing",
                            "Consider horizontal scaling",
                            "Review task scheduling",
                        ],
                    )
                )

            # I/O optimization recommendations
            if latest.disk_io_read_mb > 100 or latest.disk_io_write_mb > 100:
                recommendations.append(
                    PerformanceRecommendation(
                        category="I/O",
                        priority="medium",
                        description="High disk I/O activity detected",
                        impact="medium",
                        effort="low",
                        estimated_improvement="5-15% I/O performance improvement",
                        action_items=[
                            "Monitor disk I/O patterns",
                            "Consider SSD storage for high-I/O operations",
                            "Implement I/O batching",
                            "Review database query patterns",
                        ],
                    )
                )

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []

    def _calculate_forecast_confidence(self, snapshots: List[ResourceUsage]) -> str:
        """Calculate confidence level for forecasts."""
        try:
            if len(snapshots) < 10:
                return "low"
            elif len(snapshots) < 50:
                return "medium"
            else:
                return "high"
        except Exception:
            return "unknown"

    def _start_monitoring(self):
        """Start background performance monitoring."""
        try:

            def monitor_performance():
                while self.monitoring_enabled:
                    try:
                        self.collect_resource_snapshot()
                        time.sleep(self.collection_interval)
                    except Exception as e:
                        self.logger.error(f"Error in performance monitoring: {e}")
                        time.sleep(self.collection_interval)

            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
            monitor_thread.start()
            self.logger.info("Performance monitoring started")

        except Exception as e:
            self.logger.error(f"Error starting performance monitoring: {e}")

    def stop_monitoring(self):
        """Stop background performance monitoring."""
        self.monitoring_enabled = False
        self.logger.info("Performance monitoring stopped")

    def reset(self):
        """Reset performance optimizer state."""
        try:
            with self.lock:
                self.resource_history.clear()
                self.performance_metrics.clear()
                self.optimization_history.clear()
                self.logger.info("Performance optimizer reset")

        except Exception as e:
            self.logger.error(f"Error resetting performance optimizer: {e}")


# Global performance optimizer instance
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer(
    config: Optional[Dict[str, Any]] = None
) -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer(config)
    return _performance_optimizer


def analyze_performance(hours: int = 1) -> Dict[str, Any]:
    """Analyze system performance."""
    return get_performance_optimizer().analyze_performance(hours)


def get_optimization_recommendations() -> List[PerformanceRecommendation]:
    """Get performance optimization recommendations."""
    return get_performance_optimizer().get_optimization_recommendations()


def optimize_worker_configuration(current_config: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize worker configuration based on current performance."""
    return get_performance_optimizer().optimize_worker_configuration(current_config)
