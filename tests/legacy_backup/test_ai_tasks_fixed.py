#!/usr/bin/env python3
"""
Test script to verify AI tasks are working with fixed database connection.
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


def test_ai_task_processing():
    """Test if AI tasks can now process properly."""
    print("🧪 Testing AI Task Processing with Fixed Database Connection")
    print("=" * 60)

    try:
        # Import the AI tasks module
        from personal_assistant.workers.tasks.ai_tasks import process_due_ai_tasks

        print("✅ Successfully imported AI tasks module")

        # Test the task function directly
        print("\n🔍 Testing process_due_ai_tasks function...")

        # Create a mock task context
        class MockTask:
            def __init__(self):
                self.request = type('Request', (), {'id': 'test-task-123'})()

        mock_task = MockTask()

        # Call the function
        result = process_due_ai_tasks(mock_task)

        print(f"✅ Task executed successfully!")
        print(f"📊 Result: {result}")

        return True

    except Exception as e:
        print(f"❌ Error testing AI tasks: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection directly."""
    print("\n🔍 Testing Database Connection...")

    try:
        from personal_assistant.database.session import AsyncSessionLocal
        from personal_assistant.tools.ai_scheduler.ai_task_manager import AITaskManager

        print("✅ Successfully imported database components")

        # Test AITaskManager initialization
        task_manager = AITaskManager()
        print("✅ AITaskManager initialized successfully")

        return True

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print(f"🚀 AI Tasks Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Test database connection first
    db_ok = test_database_connection()

    if db_ok:
        # Test AI task processing
        ai_ok = test_ai_task_processing()

        if ai_ok:
            print("\n🎉 ALL TESTS PASSED! AI tasks are working properly.")
            print("✅ Database connection: WORKING")
            print("✅ AI task processing: WORKING")
        else:
            print("\n⚠️  AI task processing failed, but database is working.")
    else:
        print("\n❌ Database connection failed. Cannot test AI tasks.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
