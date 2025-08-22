# """
# Performance monitoring for the AI-first calendar scheduler system.

# This module provides comprehensive performance monitoring and optimization
# capabilities for the workflow execution.
# """

# import logging
# import statistics
# import time
# from collections import defaultdict
# from dataclasses import dataclass, field
# from datetime import datetime, timedelta
# from typing import Any, Callable, Dict, List, Optional

# logger = logging.getLogger(__name__)


# @dataclass
# class PerformanceMetrics:
#     """Performance metrics for workflow execution."""
#     execution_time: float
#     success: bool
#     event_id: int
#     workflow_type: str
#     timestamp: datetime = field(default_factory=datetime.utcnow)
#     error: Optional[str] = None
#     additional_metrics: Dict[str, Any] = field(default_factory=dict)


# class PerformanceMonitor:
#     """
#     Monitor system performance and optimize processing.

#     This class tracks performance metrics for workflow execution
#     and provides optimization recommendations.
#     """

#     def __init__(self):
#         self.logger = logger
#         self.metrics: List[PerformanceMetrics] = []
#         self.start_time: Optional[float] = None
#         self.current_metrics: Dict[str, Any] = {}

#     async def monitor_workflow_performance(self, workflow_func: Callable, *args, **kwargs) -> Dict[str, Any]:
#         """
#         Monitor performance of workflow execution.

#         Args:
#             workflow_func: Function to monitor
#             *args: Arguments for the function
#             **kwargs: Keyword arguments for the function

#         Returns:
#             Dictionary with performance metrics and function result
#         """
#         self.start_time = time.time()

#         try:
#             # Execute the workflow function
#             result = await workflow_func(*args, **kwargs)
#             execution_time = time.time() - self.start_time

#             # Create performance metrics
#             metrics = PerformanceMetrics(
#                 execution_time=execution_time,
#                 success=result.get('success', False),
#                 event_id=result.get('event_id', 0),
#                 workflow_type=workflow_func.__name__,
#                 additional_metrics=self.current_metrics
#             )

#             # Store metrics
#             self.metrics.append(metrics)

#             # Log performance metrics
#             self.logger.info(f"Workflow execution time: {execution_time:.2f}s")

#             # Check for performance issues
#             if execution_time > 30:  # More than 30 seconds
#                 self.logger.warning(
#                     f"Slow workflow execution: {execution_time:.2f}s")

#             return {
#                 'result': result,
#                 'performance': {
#                     'execution_time': execution_time,
#                     'success': result.get('success', False),
#                     'metrics': metrics
#                 }
#             }

#         except Exception as e:
#             execution_time = time.time() - self.start_time if self.start_time else 0

#             # Create error metrics
#             metrics = PerformanceMetrics(
#                 execution_time=execution_time,
#                 success=False,
#                 event_id=kwargs.get('event_id', 0),
#                 workflow_type=workflow_func.__name__,
#                 error=str(e),
#                 additional_metrics=self.current_metrics
#             )

#             # Store metrics
#             self.metrics.append(metrics)

#             self.logger.error(
#                 f"Workflow failed after {execution_time:.2f}s: {e}")
#             raise

#     def get_performance_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
#         """
#         Get performance summary for the specified time window.

#         Args:
#             time_window: Time window to analyze (default: all metrics)

#         Returns:
#             Dictionary with performance summary
#         """
#         if not self.metrics:
#             return {
#                 'total_executions': 0,
#                 'successful_executions': 0,
#                 'failed_executions': 0,
#                 'average_execution_time': 0,
#                 'median_execution_time': 0,
#                 'min_execution_time': 0,
#                 'max_execution_time': 0,
#                 'success_rate': 0
#             }

#         # Filter metrics by time window
#         if time_window:
#             cutoff_time = datetime.utcnow() - time_window
#             filtered_metrics = [
#                 m for m in self.metrics if m.timestamp >= cutoff_time]
#         else:
#             filtered_metrics = self.metrics

#         if not filtered_metrics:
#             return {
#                 'total_executions': 0,
#                 'successful_executions': 0,
#                 'failed_executions': 0,
#                 'average_execution_time': 0,
#                 'median_execution_time': 0,
#                 'min_execution_time': 0,
#                 'max_execution_time': 0,
#                 'success_rate': 0
#             }

#         # Calculate statistics
#         execution_times = [m.execution_time for m in filtered_metrics]
#         successful = [m for m in filtered_metrics if m.success]
#         failed = [m for m in filtered_metrics if not m.success]

#         return {
#             'total_executions': len(filtered_metrics),
#             'successful_executions': len(successful),
#             'failed_executions': len(failed),
#             'average_execution_time': statistics.mean(execution_times),
#             'median_execution_time': statistics.median(execution_times),
#             'min_execution_time': min(execution_times),
#             'max_execution_time': max(execution_times),
#             'success_rate': len(successful) / len(filtered_metrics) if filtered_metrics else 0
#         }

#     def get_workflow_type_performance(self, workflow_type: str) -> Dict[str, Any]:
#         """
#         Get performance metrics for a specific workflow type.

#         Args:
#             workflow_type: Type of workflow to analyze

#         Returns:
#             Dictionary with workflow-specific performance metrics
#         """
#         workflow_metrics = [
#             m for m in self.metrics if m.workflow_type == workflow_type]

#         if not workflow_metrics:
#             return {
#                 'workflow_type': workflow_type,
#                 'total_executions': 0,
#                 'successful_executions': 0,
#                 'failed_executions': 0,
#                 'average_execution_time': 0,
#                 'success_rate': 0
#             }

#         execution_times = [m.execution_time for m in workflow_metrics]
#         successful = [m for m in workflow_metrics if m.success]

#         return {
#             'workflow_type': workflow_type,
#             'total_executions': len(workflow_metrics),
#             'successful_executions': len(successful),
#             'failed_executions': len(workflow_metrics) - len(successful),
#             'average_execution_time': statistics.mean(execution_times),
#             'success_rate': len(successful) / len(workflow_metrics)
#         }

#     def get_performance_trends(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
#         """
#         Get performance trends over time.

#         Args:
#             time_window: Time window to analyze

#         Returns:
#             Dictionary with performance trends
#         """
#         cutoff_time = datetime.utcnow() - time_window
#         recent_metrics = [
#             m for m in self.metrics if m.timestamp >= cutoff_time]

#         if not recent_metrics:
#             return {
#                 'trend': 'no_data',
#                 'message': 'No metrics available for trend analysis'
#             }

#         # Group metrics by hour
#         hourly_metrics = defaultdict(list)
#         for metric in recent_metrics:
#             hour_key = metric.timestamp.replace(
#                 minute=0, second=0, microsecond=0)
#             hourly_metrics[hour_key].append(metric)

#         # Calculate trends
#         hours = sorted(hourly_metrics.keys())
#         if len(hours) < 2:
#             return {
#                 'trend': 'insufficient_data',
#                 'message': 'Insufficient data for trend analysis'
#             }

#         # Calculate average execution times per hour
#         avg_times = []
#         success_rates = []

#         for hour in hours:
#             hour_metrics = hourly_metrics[hour]
#             avg_time = statistics.mean(
#                 [m.execution_time for m in hour_metrics])
#             success_rate = len(
#                 [m for m in hour_metrics if m.success]) / len(hour_metrics)

#             avg_times.append(avg_time)
#             success_rates.append(success_rate)

#         # Determine trends
#         if len(avg_times) >= 2:
#             time_trend = 'improving' if avg_times[-1] < avg_times[0] else 'degrading'
#             success_trend = 'improving' if success_rates[-1] > success_rates[0] else 'degrading'
#         else:
#             time_trend = 'stable'
#             success_trend = 'stable'

#         return {
#             'trend': 'analyzed',
#             'time_trend': time_trend,
#             'success_trend': success_trend,
#             'current_avg_time': avg_times[-1] if avg_times else 0,
#             'current_success_rate': success_rates[-1] if success_rates else 0,
#             'data_points': len(hours)
#         }

#     def get_optimization_recommendations(self) -> List[str]:
#         """
#         Get performance optimization recommendations.

#         Returns:
#             List of optimization recommendations
#         """
#         recommendations = []

#         if not self.metrics:
#             return ['No performance data available for recommendations']

#         # Get recent performance (last hour)
#         recent_summary = self.get_performance_summary(timedelta(hours=1))

#         # Check for slow execution times
#         if recent_summary['average_execution_time'] > 10:
#             recommendations.append(
#                 'Consider optimizing workflow execution - average time is high')

#         # Check for low success rates
#         if recent_summary['success_rate'] < 0.9:
#             recommendations.append(
#                 'Investigate failed executions - success rate is below 90%')

#         # Check for high variance in execution times
#         recent_metrics = [m for m in self.metrics if m.timestamp >=
#                           datetime.utcnow() - timedelta(hours=1)]
#         if recent_metrics:
#             execution_times = [m.execution_time for m in recent_metrics]
#             if len(execution_times) > 1:
#                 variance = statistics.variance(execution_times)
#                 if variance > 100:  # High variance
#                     recommendations.append(
#                         'High variance in execution times - consider standardizing workflows')

#         # Check for memory or resource issues
#         if len(self.metrics) > 1000:
#             recommendations.append(
#                 'Consider implementing metrics cleanup to prevent memory issues')

#         if not recommendations:
#             recommendations.append('Performance is within acceptable ranges')

#         return recommendations

#     def clear_old_metrics(self, max_age: timedelta = timedelta(days=7)):
#         """
#         Clear old metrics to prevent memory issues.

#         Args:
#             max_age: Maximum age of metrics to keep
#         """
#         cutoff_time = datetime.utcnow() - max_age
#         original_count = len(self.metrics)

#         self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]

#         cleared_count = original_count - len(self.metrics)
#         if cleared_count > 0:
#             self.logger.info(
#                 f"Cleared {cleared_count} old performance metrics")


# def create_performance_monitor() -> PerformanceMonitor:
#     """
#     Factory function to create a performance monitor instance.

#     Returns:
#         PerformanceMonitor instance
#     """
#     return PerformanceMonitor()
