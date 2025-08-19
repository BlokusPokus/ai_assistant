import logging
import os

from celery import Celery
from celery.schedules import crontab

# Get Redis URL from environment or use default
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# Create Celery app
app = Celery(
    'ai_scheduler',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery configuration
app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task routing
    task_routes={
        'personal_assistant.tools.ai_scheduler.ai_task_scheduler.*': {'queue': 'ai_tasks'},
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        'process-due-ai-tasks': {
            'task': 'personal_assistant.tools.ai_scheduler.ai_task_scheduler.process_due_ai_tasks',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
        },
        'test-scheduler-connection': {
            'task': 'personal_assistant.tools.ai_scheduler.ai_task_scheduler.test_scheduler_connection',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
        },
        'cleanup-old-logs': {
            'task': 'personal_assistant.tools.ai_scheduler.ai_task_scheduler.cleanup_old_logs',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
    },

    # Task execution settings
    task_always_eager=False,  # Set to True for testing without Redis
    task_eager_propagates=True,

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour

    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

# Optional: Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app.start()
