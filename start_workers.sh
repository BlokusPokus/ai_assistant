#!/bin/bash

# Personal Assistant Background Task System Startup Script

echo "🚀 Starting Personal Assistant Background Task System..."

# Set Database Environment Variables
export REAL_DB_URL="postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
export DATABASE_URL="postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
export DB_POOL_SIZE=10
export DB_MAX_OVERFLOW=15
export DB_POOL_TIMEOUT=30
export DB_POOL_RECYCLE=3600
export DB_POOL_PRE_PING=true

# Set Redis Environment Variables
export REDIS_URL="redis://:redis_password@localhost:6379"
export CELERY_BROKER_URL="redis://:redis_password@localhost:6379"
export CELERY_RESULT_BACKEND="redis://:redis_password@localhost:6379"

# Set Celery Environment Variables
export CELERY_TASK_SERIALIZER=json
export CELERY_RESULT_SERIALIZER=json
export CELERY_ACCEPT_CONTENT=json
export CELERY_TIMEZONE=UTC
export CELERY_ENABLE_UTC=true

# Set Worker Environment Variables
export CELERY_WORKER_CONCURRENCY=1
export CELERY_WORKER_MAX_TASKS_PER_CHILD=1000
export CELERY_WORKER_PREFETCH_MULTIPLIER=1

# Set Logging
export PA_LOG_LEVEL=INFO

echo "✅ Environment variables set successfully"
echo "📊 Database: $DATABASE_URL"
echo "📊 Redis: $REDIS_URL"
echo "📊 Celery: $CELERY_BROKER_URL"

# Activate virtual environment
source venv_personal_assistant/bin/activate

echo "🐍 Virtual environment activated"

# Start Celery Beat Scheduler in background
echo "⏰ Starting Celery Beat Scheduler..."
celery -A personal_assistant.workers.celery_app beat -l info &
BEAT_PID=$!
echo "✅ Beat scheduler started (PID: $BEAT_PID)"

# Start Celery Worker in background
echo "👷 Starting Celery Worker..."
celery -A personal_assistant.workers.celery_app worker -Q ai_tasks,email_tasks,file_tasks,sync_tasks,maintenance_tasks -l info --concurrency=1 &
WORKER_PID=$!
echo "✅ Worker started (PID: $WORKER_PID)"

echo ""
echo "🎉 Background Task System Started Successfully!"
echo "📋 Beat Scheduler PID: $BEAT_PID"
echo "📋 Worker PID: $WORKER_PID"
echo ""
echo "To stop the system, run:"
echo "  kill $BEAT_PID $WORKER_PID"
echo ""
echo "To view logs, run:"
echo "  tail -f /dev/null  # Replace with actual log file path if configured"
echo ""
echo "System is now running and processing tasks..." 