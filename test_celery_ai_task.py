#!/usr/bin/env python3
"""
Test script to send an AI task through Celery and verify it processes.
"""

import os
import sys
import time
from datetime import datetime

# Set environment variables
os.environ['REAL_DB_URL'] = "postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
os.environ['DATABASE_URL'] = "postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
os.environ['DB_POOL_SIZE'] = "10"
os.environ['DB_MAX_OVERFLOW'] = "15"
os.environ['REDIS_URL'] = "redis://:redis_password@localhost:6379"
os.environ['CELERY_BROKER_URL'] = "redis://:redis_password@localhost:6379"
os.environ['CELERY_RESULT_BACKEND'] = "redis://:redis_password@localhost:6379"


def test_celery_ai_task():
    """Test sending an AI task through Celery."""
    print("🧪 Testing Celery AI Task Processing")
    print("=" * 50)

    try:
        # Import Celery app
        from personal_assistant.workers.celery_app import app

        print("✅ Successfully imported Celery app")

        # Send a test task
        print("\n📤 Sending test_scheduler_connection task...")
        task = app.send_task(
            'personal_assistant.workers.tasks.ai_tasks.test_scheduler_connection')

        print(f"✅ Task sent successfully!")
        print(f"📋 Task ID: {task.id}")

        # Wait for result
        print("\n⏳ Waiting for task completion...")
        result = task.get(timeout=30)

        print(f"✅ Task completed successfully!")
        print(f"📊 Result: {result}")

        return True

    except Exception as e:
        print(f"❌ Error testing Celery AI task: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_celery_inspect():
    """Test Celery inspect to see worker status."""
    print("\n🔍 Testing Celery Worker Status...")

    try:
        from personal_assistant.workers.celery_app import app

        # Inspect workers
        inspect = app.control.inspect()

        # Get active workers
        active_workers = inspect.active()
        registered_tasks = inspect.registered()
        stats = inspect.stats()

        print(
            f"✅ Active workers: {len(active_workers) if active_workers else 0}")
        print(
            f"✅ Registered tasks: {len(registered_tasks) if registered_tasks else 0}")

        if active_workers:
            print("\n📋 Active Workers:")
            for worker_name, tasks in active_workers.items():
                print(f"  - {worker_name}: {len(tasks)} active tasks")

        if registered_tasks:
            print("\n📋 Registered Tasks:")
            for worker_name, tasks in registered_tasks.items():
                print(f"  - {worker_name}: {len(tasks)} tasks")

        return True

    except Exception as e:
        print(f"❌ Error inspecting Celery: {e}")
        return False


def main():
    """Main test function."""
    print(
        f"🚀 Celery AI Task Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Test Celery inspect first
    inspect_ok = test_celery_inspect()

    if inspect_ok:
        # Test sending AI task
        task_ok = test_celery_ai_task()

        if task_ok:
            print("\n🎉 ALL TESTS PASSED! Celery AI tasks are working properly.")
        else:
            print("\n⚠️  Celery AI task failed, but worker inspection is working.")
    else:
        print("\n❌ Celery worker inspection failed.")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
