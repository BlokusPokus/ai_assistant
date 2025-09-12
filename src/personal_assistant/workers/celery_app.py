"""
Enhanced Celery Application with Advanced Features

This module provides a production-ready Celery application with
advanced scheduling, monitoring, and performance optimization.
"""

import logging
import os
from datetime import datetime

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure, task_postrun, task_prerun
from kombu import Queue
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load configuration files
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
config_file = f"config/{ENVIRONMENT}.env"

# Load the appropriate config file
if os.path.exists(config_file):
    load_dotenv(config_file)
    print(f"✅ Loaded configuration from {config_file}")
else:
    # Fallback to root .env file
    load_dotenv()
    print("⚠️  Using fallback .env file")

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

print(f"🔧 Celery Configuration:")
print(f"   Broker: {CELERY_BROKER_URL}")
print(f"   Backend: {CELERY_RESULT_BACKEND}")
print(f"   Environment: {ENVIRONMENT}")

# Initialize database configuration after environment variables are loaded
try:
    from personal_assistant.config.database import db_config

    print("🔧 Initializing database configuration...")
    # Force database initialization
    db_config._initialize_database()
    print("✅ Database configuration initialized")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")

# Create Celery app
app = Celery(
    "personal_assistant_workers",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Enhanced Celery configuration
app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Enhanced task routing with priorities
    task_routes={
        "personal_assistant.workers.tasks.ai_tasks.*": {
            "queue": "ai_tasks",
            "priority": 10,
        },
        "personal_assistant.workers.tasks.email_tasks.*": {
            "queue": "email_tasks",
            "priority": 5,
        },
        "personal_assistant.workers.tasks.file_tasks.*": {
            "queue": "file_tasks",
            "priority": 3,
        },
        "personal_assistant.workers.tasks.sync_tasks.*": {
            "queue": "sync_tasks",
            "priority": 7,
        },
        "personal_assistant.workers.tasks.maintenance_tasks.*": {
            "queue": "maintenance_tasks",
            "priority": 1,
        },
    },
    # Explicit queue declarations with explicit exchange names
    task_queues=(
        Queue('ai_tasks', exchange='ai_tasks', routing_key='ai_tasks'),
        Queue('email_tasks', exchange='email_tasks', routing_key='email_tasks'),
        Queue('file_tasks', exchange='file_tasks', routing_key='file_tasks'),
        Queue('sync_tasks', exchange='sync_tasks', routing_key='sync_tasks'),
        Queue('maintenance_tasks', exchange='maintenance_tasks', routing_key='maintenance_tasks'),
    ),
    # Default queue configuration
    task_default_queue='ai_tasks',
    task_default_exchange='ai_tasks',
    task_default_exchange_type='direct',
    task_default_routing_key='ai_tasks',
    # Prevent queue naming conflicts
    task_create_missing_queues=True,
    task_default_delivery_mode='persistent',
    # Enhanced beat schedule with dependencies
    beat_schedule={
        # AI tasks (high priority)
        "process-due-ai-tasks": {
            "task": "personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks",
            "schedule": crontab(minute="*/1"),
            "options": {"priority": 10},
        },
        "test-scheduler-connection": {
            "task": "personal_assistant.workers.tasks.ai_tasks.test_scheduler_connection",
            "schedule": crontab(minute="*/30"),
            "options": {"priority": 10},
        },
        "cleanup-old-logs": {
            "task": "personal_assistant.workers.tasks.ai_tasks.cleanup_old_logs",
            "schedule": crontab(hour=2, minute=0),
            "options": {"priority": 10},
        },
        # Email tasks (medium priority)
        "process-email-queue": {
            "task": "personal_assistant.workers.tasks.email_tasks.process_email_queue",
            "schedule": crontab(minute="*/5"),
            "options": {"priority": 5},
        },
        "send-daily-email-summary": {
            "task": "personal_assistant.workers.tasks.email_tasks.send_daily_email_summary",
            "schedule": crontab(hour=8, minute=0),
            "options": {"priority": 5},
        },
        # File tasks (low priority)
        "cleanup-temp-files": {
            "task": "personal_assistant.workers.tasks.file_tasks.cleanup_temp_files",
            "schedule": crontab(hour=2, minute=0),
            "options": {"priority": 3},
        },
        "backup-user-data": {
            "task": "personal_assistant.workers.tasks.file_tasks.backup_user_data",
            "schedule": crontab(day_of_week=0, hour=1, minute=0),
            "options": {"priority": 3},
        },
        # Sync tasks (medium-high priority)
        "sync-calendar-events": {
            "task": "personal_assistant.workers.tasks.sync_tasks.sync_calendar_events",
            "schedule": crontab(minute=0),
            "options": {"priority": 7},
        },
        "sync-notion-pages": {
            "task": "personal_assistant.workers.tasks.sync_tasks.sync_notion_pages",
            "schedule": crontab(minute=0, hour="*/2"),
            "options": {"priority": 7},
        },
        # Maintenance tasks (lowest priority)
        "cleanup-old-logs": {
            "task": "personal_assistant.workers.tasks.maintenance_tasks.cleanup_old_logs",
            "schedule": crontab(hour=3, minute=0),
            "options": {"priority": 1},
        },
        "optimize-database": {
            "task": "personal_assistant.workers.tasks.maintenance_tasks.optimize_database",
            "schedule": crontab(day_of_week=0, hour=3, minute=0),
            "options": {"priority": 1},
        },
        "cleanup-old-sessions": {
            "task": "personal_assistant.workers.tasks.maintenance_tasks.cleanup_old_sessions",
            "schedule": crontab(hour=4, minute=0),
            "options": {"priority": 1},
        },
    },
    # Enhanced worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_ignore_result=False,
    # Enhanced result backend settings
    result_expires=3600,
    result_persistent=True,
    result_chord_join_timeout=3600,
    result_chord_retry_interval=1,
    # Enhanced task settings
    task_always_eager=False,
    task_eager_propagates=True,
    task_remote_tracebacks=True,
    task_compression="gzip",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Enhanced monitoring
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)

# Log the beat schedule configuration
logger.info("🚀 CELERY BEAT SCHEDULE CONFIGURED:")
logger.info(f"📅 process-due-ai-tasks: Every minute (crontab: */1)")
logger.info(f"📅 test-scheduler-connection: Every 30 minutes")
logger.info(f"📅 cleanup-old-logs: Daily at 2:00 AM")
print("🚀 CELERY BEAT SCHEDULE CONFIGURED:")
print(f"📅 process-due-ai-tasks: Every minute (crontab: */1)")
print(f"📅 test-scheduler-connection: Every 30 minutes")
print(f"📅 cleanup-old-logs: Daily at 2:00 AM")

# Log the queue configuration
logger.info("🚀 CELERY QUEUE CONFIGURATION:")
logger.info(f"📋 Default Queue: {app.conf.task_default_queue}")
logger.info(f"📋 Active Queues: {[q.name for q in app.conf.task_queues]}")
logger.info(f"📋 Task Routes: {app.conf.task_routes}")
print("🚀 CELERY QUEUE CONFIGURATION:")
print(f"📋 Default Queue: {app.conf.task_default_queue}")
print(f"📋 Active Queues: {[q.name for q in app.conf.task_queues]}")
print(f"📋 Task Routes: {app.conf.task_routes}")

# Enhanced signal handlers for monitoring


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Handle task pre-run events for monitoring."""
    try:
        if hasattr(app, "metrics_collector"):
            app.metrics_collector.start_task(task_id, task.name)

        # Log task start
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

        # Log task completion
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
            # Get current system metrics for alerting
            from .utils.metrics import get_metrics_collector

            metrics_collector = get_metrics_collector()
            current_metrics = metrics_collector.get_current_system_status()

            # Add task failure information
            current_metrics.update(
                {
                    "failed_task_id": task_id,
                    "failed_task_name": kwargs.get("task_name", "unknown"),
                    "error": str(exception),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            app.alert_manager.check_alerts(current_metrics)

        # Log task failure
        logger.error(
            f"Task failed: {kwargs.get('task_name', 'unknown')} ({task_id}): {exception}"
        )

    except Exception as e:
        logger.error(f"Error in task failure handler: {e}")


# Initialize enhanced components


def initialize_enhanced_features():
    """Initialize enhanced monitoring, alerting, and performance features."""
    try:
        # Initialize metrics collector
        if os.getenv("METRICS_ENABLED", "true").lower() == "true":
            from .utils.metrics import get_metrics_collector

            app.metrics_collector = get_metrics_collector()
            logger.info("Enhanced metrics collection enabled")

        # Initialize alert manager
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

        # Initialize performance optimizer
        if os.getenv("PERFORMANCE_OPTIMIZATION_ENABLED", "true").lower() == "true":
            from .utils.performance import get_performance_optimizer

            app.performance_optimizer = get_performance_optimizer()
            logger.info("Performance optimization enabled")

        # Initialize dependency scheduler
        if os.getenv("DEPENDENCY_SCHEDULING_ENABLED", "true").lower() == "true":
            from .schedulers.dependency_scheduler import DependencyScheduler

            app.dependency_scheduler = DependencyScheduler()
            logger.info("Dependency scheduling enabled")

        logger.info("Enhanced features initialization completed")

    except Exception as e:
        logger.error(f"Error initializing enhanced features: {e}")


# Initialize enhanced features
initialize_enhanced_features()

# Optional: Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app.start()
