"""
Celery configuration module for the Personal Assistant project.

This module is intentionally limited to **pure configuration**:
- No environment .env loading
- No database initialization
- No metrics/alerting/performance wiring

It mirrors the effective configuration currently defined in
`personal_assistant.workers.celery_app`, but in a form suitable for
`personal_assistant.celery` to consume.
"""

import os

from celery.schedules import crontab
from kombu import Queue

from personal_assistant.config.settings import settings


# ---------------------------------------------------------------------------
# Broker / backend configuration
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = getattr(settings, "CELERY_BROKER_URL", None) or os.getenv(
    "CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379")
)

# Celery 5 prefers the new-style ``result_backend`` setting name. We avoid
# defining ``CELERY_RESULT_BACKEND`` to prevent mixing old/new styles.
result_backend = getattr(settings, "CELERY_RESULT_BACKEND", None) or os.getenv(
    "CELERY_RESULT_BACKEND", CELERY_BROKER_URL
)


# ---------------------------------------------------------------------------
# Core Celery settings
# ---------------------------------------------------------------------------

task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"
timezone = "UTC"
enable_utc = True

# ---------------------------------------------------------------------------
# Routing and queues
# ---------------------------------------------------------------------------

task_routes = {
    "personal_assistant.workers.tasks.ai_tasks.*": {
        "queue": "ai_tasks",
        "priority": 10,
    },
    "personal_assistant.workers.tasks.sms_tasks.*": {
        "queue": "sms_tasks",
        "priority": 8,
    },
    "personal_assistant.workers.tasks.grocery_tasks.*": {
        "queue": "grocery_tasks",
        "priority": 6,
    },
}

task_queues = (
    Queue("ai_tasks", exchange="ai_tasks", routing_key="ai_tasks"),
    Queue("sms_tasks", exchange="sms_tasks", routing_key="sms_tasks"),
    Queue("grocery_tasks", exchange="grocery_tasks", routing_key="grocery_tasks"),
)

task_default_queue = "ai_tasks"
task_default_exchange = "ai_tasks"
task_default_exchange_type = "direct"
task_default_routing_key = "ai_tasks"

task_create_missing_queues = True
task_default_delivery_mode = "persistent"


# ---------------------------------------------------------------------------
# Beat schedule
# ---------------------------------------------------------------------------

beat_schedule = {
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
    # SMS retry tasks (high priority)
    "sms-retry-processor": {
        "task": "personal_assistant.workers.tasks.sms_tasks.process_sms_retries",
        "schedule": crontab(minute="*/2"),
        "options": {"priority": 8},
    },
    "sms-retry-cleanup": {
        "task": "personal_assistant.workers.tasks.sms_tasks.cleanup_old_retries",
        "schedule": crontab(hour=3, minute=0),
        "options": {"priority": 5},
    },
    "sms-retry-health-check": {
        "task": "personal_assistant.workers.tasks.sms_tasks.sms_retry_health_check",
        "schedule": crontab(minute="*/15"),
        "options": {"priority": 7},
    },
    # Grocery tasks (medium priority)
    "fetch-iga-flyer-data": {
        "task": "personal_assistant.workers.tasks.grocery_tasks.fetch_iga_flyer_data",
        "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday 6 AM
        "options": {"priority": 6},
    },
    "test-grocery-task-connection": {
        "task": "personal_assistant.workers.tasks.grocery_tasks.test_grocery_task_connection",
        "schedule": crontab(minute="*/30"),
        "options": {"priority": 6},
    },
    "cleanup-expired-grocery-deals": {
        "task": "personal_assistant.workers.tasks.grocery_tasks.cleanup_expired_grocery_deals",
        "schedule": crontab(hour=7, minute=0),  # Daily at 7 AM (safety cleanup)
        "options": {"priority": 5},
    },
}


# ---------------------------------------------------------------------------
# Worker and result backend settings
# ---------------------------------------------------------------------------

worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False
worker_send_task_events = True

task_send_sent_event = True
task_ignore_result = False

result_expires = 3600
result_persistent = True
result_chord_join_timeout = 3600
result_chord_retry_interval = 1

task_always_eager = False
task_eager_propagates = True
task_remote_tracebacks = True
task_compression = "gzip"
task_acks_late = True
task_reject_on_worker_lost = True

task_track_started = True
task_time_limit = 3600
task_soft_time_limit = 3000

worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
worker_task_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] "
    "[%(task_name)s(%(task_id)s)] %(message)s"
)
