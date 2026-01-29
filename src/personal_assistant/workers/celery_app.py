"""
Enhanced Celery Application with Advanced Features

This module now acts as a backward-compatible adapter around the canonical
Celery app defined in `personal_assistant.celery`, while preserving the
advanced signal handlers and feature initialization.
"""

import logging
import os
from datetime import datetime

from celery.signals import task_failure, task_postrun, task_prerun

from personal_assistant.celery import app

logger = logging.getLogger(__name__)


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Handle task pre-run events for monitoring."""
    try:
        if hasattr(app, "metrics_collector"):
            app.metrics_collector.start_task(task_id, task.name)
        logger.info(f"Task started: {task.name} ({task_id})")
    except Exception as e:
        logger.error(f"Error in task prerun handler: {e}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Handle task post-run events for monitoring."""
    try:
        if hasattr(app, "metrics_collector"):
            status = "completed" if kwargs.get("retval") is not None else "failed"
            app.metrics_collector.end_task(task_id, status)
        execution_time = kwargs.get("runtime", 0)
        logger.info(f"Task completed: {task.name} ({task_id}) in {execution_time:.2f}s")
    except Exception as e:
        logger.error(f"Error in task postrun handler: {e}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """Handle task failure events for monitoring and alerting."""
    try:
        if hasattr(app, "metrics_collector"):
            app.metrics_collector.end_task(task_id, "failed", str(exception))

        if hasattr(app, "alert_manager"):
            from .utils.metrics import get_metrics_collector

            metrics_collector = get_metrics_collector()
            current_metrics = metrics_collector.get_current_system_status()
            current_metrics.update(
                {
                    "failed_task_id": task_id,
                    "failed_task_name": kwargs.get("task_name", "unknown"),
                    "error": str(exception),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            app.alert_manager.check_alerts(current_metrics)

        logger.error(
            f"Task failed: {kwargs.get('task_name', 'unknown')} ({task_id}): {exception}"
        )
    except Exception as e:
        logger.error(f"Error in task failure handler: {e}")


def initialize_enhanced_features():
    """Initialize enhanced monitoring, alerting, and performance features."""
    try:
        if os.getenv("METRICS_ENABLED", "true").lower() == "true":
            from .utils.metrics import get_metrics_collector

            app.metrics_collector = get_metrics_collector()
            logger.info("Enhanced metrics collection enabled")

        if os.getenv("ALERTING_ENABLED", "true").lower() == "true":
            from .utils.alerting import get_alert_manager

            alert_config = {
                "email": {
                    "smtp_server": os.getenv("ALERT_SMTP_SERVER"),
                    "smtp_port": int(os.getenv("ALERT_SMTP_PORT", "587")),
                    "username": os.getenv("ALERT_SMTP_USERNAME"),
                    "password": os.getenv("ALERT_SMTP_PASSWORD"),
                    "from_email": os.getenv("ALERT_FROM_EMAIL"),
                    "to_emails": os.getenv("ALERT_TO_EMAILS", "").split(",")
                    if os.getenv("ALERT_TO_EMAILS")
                    else [],
                },
                "slack": {"webhook_url": os.getenv("ALERT_SLACK_WEBHOOK_URL")},
                "webhook": {
                    "url": os.getenv("ALERT_WEBHOOK_URL"),
                    "headers": {},
                    "timeout": 10,
                },
            }
            app.alert_manager = get_alert_manager(alert_config)
            logger.info("Enhanced alerting system enabled")

        if os.getenv("PERFORMANCE_OPTIMIZATION_ENABLED", "true").lower() == "true":
            from .utils.performance import get_performance_optimizer

            app.performance_optimizer = get_performance_optimizer()
            logger.info("Performance optimization enabled")

        if os.getenv("DEPENDENCY_SCHEDULING_ENABLED", "true").lower() == "true":
            from .schedulers.dependency_scheduler import DependencyScheduler

            app.dependency_scheduler = DependencyScheduler()
            logger.info("Dependency scheduling enabled")

        logger.info("Enhanced features initialization completed")

    except Exception as e:
        logger.error(f"Error initializing enhanced features: {e}")


initialize_enhanced_features()