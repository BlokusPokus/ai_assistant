"""
Central Celery Application for Personal Assistant Background Tasks

This module provides a unified Celery application that handles all types
of background tasks with proper routing and configuration.
"""

import logging
import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

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
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

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
    'personal_assistant_workers',
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

    # Task routing for different task types
    task_routes={
        'personal_assistant.workers.tasks.ai_tasks.*': {'queue': 'ai_tasks'},
        'personal_assistant.workers.tasks.email_tasks.*': {'queue': 'email_tasks'},
        'personal_assistant.workers.tasks.file_tasks.*': {'queue': 'file_tasks'},
        'personal_assistant.workers.tasks.sync_tasks.*': {'queue': 'sync_tasks'},
        'personal_assistant.workers.tasks.maintenance_tasks.*': {'queue': 'maintenance_tasks'},
    },

    # Beat schedule for different task types
    beat_schedule={
        # AI tasks (existing functionality)
        'process-due-ai-tasks': {
            'task': 'personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
        },
        'test-scheduler-connection': {
            'task': 'personal_assistant.workers.tasks.ai_tasks.test_scheduler_connection',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
        },
        'cleanup-old-logs': {
            'task': 'personal_assistant.workers.tasks.ai_tasks.cleanup_old_logs',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },

        # Email tasks (new functionality)
        'process-email-queue': {
            'task': 'personal_assistant.workers.tasks.email_tasks.process_email_queue',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'send-daily-email-summary': {
            'task': 'personal_assistant.workers.tasks.email_tasks.send_daily_email_summary',
            'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
        },

        # File tasks (new functionality)
        'cleanup-temp-files': {
            'task': 'personal_assistant.workers.tasks.file_tasks.cleanup_temp_files',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'backup-user-data': {
            'task': 'personal_assistant.workers.tasks.file_tasks.backup_user_data',
            # Weekly on Sunday at 1 AM
            'schedule': crontab(day_of_week=0, hour=1, minute=0),
        },

        # Sync tasks (new functionality)
        'sync-calendar-events': {
            'task': 'personal_assistant.workers.tasks.sync_tasks.sync_calendar_events',
            'schedule': crontab(minute=0),  # Every hour
        },
        'sync-notion-pages': {
            'task': 'personal_assistant.workers.tasks.sync_tasks.sync_notion_pages',
            'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
        },

        # Maintenance tasks (new functionality)
        'optimize-database': {
            'task': 'personal_assistant.workers.tasks.maintenance_tasks.optimize_database',
            # Weekly on Sunday at 3 AM
            'schedule': crontab(day_of_week=0, hour=3, minute=0),
        },
        'cleanup-old-sessions': {
            'task': 'personal_assistant.workers.tasks.maintenance_tasks.cleanup_old_sessions',
            'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
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

if __name__ == '__main__':
    app.start()
