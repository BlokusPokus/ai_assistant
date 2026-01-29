"""
Canonical Celery application entrypoint for the Personal Assistant project.

This package:
- Exposes the main Celery `app` in this __init__ (so `-A personal_assistant.celery` still works).
- Keeps configuration in `personal_assistant.celery.config`.
- Autodiscovers tasks from the workers package.

It is intentionally kept free of:
- .env loading
- Database initialization
- Metrics/alerting/performance wiring

Those concerns should be handled in separate modules or via Celery signals.
"""

from celery import Celery

from . import config as celeryconfig


# Create the main Celery app for the project
app = Celery(
    "personal_assistant",
    broker=celeryconfig.CELERY_BROKER_URL,
    backend=celeryconfig.result_backend,
)

# Load configuration from config module (uses module-level attributes)
app.config_from_object("personal_assistant.celery.config")

# Autodiscover tasks from workers package
app.autodiscover_tasks(["personal_assistant.workers"])
