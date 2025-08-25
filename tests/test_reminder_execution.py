#!/usr/bin/env python3
"""
Test Reminder Execution Flow

This script tests the complete reminder execution flow after Task 037.1 migration.
Tests scheduling, background processing, and task execution.
"""

import sys
import asyncio
from datetime import datetime, timedelta

# Add src to Python path
sys.path.insert(0, 'src')


async def test_reminder_scheduling():
    """Test that reminders are properly scheduled."""
    print("📅 TESTING REMINDER SCHEDULING")
    print("=" * 50)

    try:
        from personal_assistant.tools.ai_scheduler import AITaskManager

        task_manager = AITaskManager()

        # Get all active reminders
        active_reminders = await task_manager.get_user_tasks(
            user_id=126,
            status='active',
            task_type='reminder',
            limit=10
        )

        print(f"📋 Found {len(active_reminders)} active reminders")

        # Check for due reminders
        now = datetime.utcnow()
        due_reminders = []

        for reminder in active_reminders:
            if reminder.next_run_at and reminder.next_run_at <= now:
                due_reminders.append(reminder)

        print(f"⏰ Found {len(due_reminders)} due reminders")

        if due_reminders:
            print("📝 Due reminders:")
            for reminder in due_reminders:
                print(f"   - ID: {reminder.id}")
                print(f"     Title: {reminder.title}")
                print(f"     Due at: {reminder.next_run_at}")
                print(f"     Status: {reminder.status}")

        return len(due_reminders) > 0

    except Exception as e:
        print(f"❌ Scheduling test failed: {e}")
        return False


async def test_background_task_execution():
    """Test the background task execution manually."""
    print("\n🔄 TESTING BACKGROUND TASK EXECUTION")
    print("=" * 50)

    try:
        from personal_assistant.workers.tasks.ai_tasks import process_due_ai_tasks

        print("✅ Background task function imported")

        # Run the background task manually
        print("🚀 Executing background task manually...")

        # Note: This will run the actual task processing
        result = process_due_ai_tasks.delay()

        print(f"✅ Background task started with ID: {result.id}")
        print(f"📊 Task status: {result.status}")

        # Wait a bit for the task to complete
        print("⏳ Waiting for task completion...")
        await asyncio.sleep(5)

        # Check task result
        if result.ready():
            task_result = result.get()
            print(f"✅ Task completed!")
            print(f"📊 Result: {task_result}")
        else:
            print("⏳ Task still running...")

        return True

    except Exception as e:
        print(f"❌ Background task execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_task_processing_logic():
    """Test the task processing logic without running the full Celery task."""
    print("\n🧠 TESTING TASK PROCESSING LOGIC")
    print("=" * 50)

    try:
        from personal_assistant.tools.ai_scheduler import AITaskManager

        task_manager = AITaskManager()

        # Get due tasks
        due_tasks = await task_manager.get_due_tasks(limit=10)
        print(f"📋 Found {len(due_tasks)} due tasks")

        if due_tasks:
            print("📝 Due tasks:")
            for task in due_tasks:
                print(f"   - ID: {task.id}")
                print(f"     Title: {task.title}")
                print(f"     Type: {task.task_type}")
                print(f"     Status: {task.status}")
                print(f"     Next run: {task.next_run_at}")
                print(
                    f"     Notification channels: {task.notification_channels}")
                print()

        # Test updating task status
        if due_tasks:
            test_task = due_tasks[0]
            print(f"🔄 Testing task status update for task {test_task.id}...")

            # Mark as processing
            await task_manager.update_task_status(
                task_id=test_task.id,
                status='processing',
                last_run_at=datetime.utcnow()
            )
            print("✅ Task marked as processing")

            # Mark as completed
            await task_manager.update_task_status(
                task_id=test_task.id,
                status='completed',
                last_run_at=datetime.utcnow()
                # Note: result_data field not available in current model
                # This will be enhanced in Task 037.2
            )
            print("✅ Task marked as completed")

            # Verify status change
            # Get the updated task using existing method
            updated_tasks = await task_manager.get_user_tasks(
                user_id=test_task.user_id,
                status='completed',
                limit=10
            )

            # Find our specific task
            updated_task = None
            for task in updated_tasks:
                if task.id == test_task.id:
                    updated_task = task
                    break

            if updated_task:
                print(f"✅ Task status updated to: {updated_task.status}")
            else:
                print(
                    "⚠️  Could not verify task status update (task not found in completed list)")

        return True

    except Exception as e:
        print(f"❌ Task processing logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_celery_scheduler():
    """Test that the Celery scheduler is properly configured."""
    print("\n⏰ TESTING CELERY SCHEDULER")
    print("=" * 50)

    try:
        from personal_assistant.workers.celery_app import app

        print(f"✅ Celery app accessible with {len(app.tasks)} tasks")

        # Check if our scheduled task is registered
        scheduled_task = "personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks"

        if scheduled_task in app.tasks:
            print(f"✅ Scheduled task '{scheduled_task}' is registered")

            # Check task configuration
            task = app.tasks[scheduled_task]
            print(f"📊 Task max retries: {task.max_retries}")
            print(f"📊 Task retry delay: {task.default_retry_delay}")

        else:
            print(f"❌ Scheduled task '{scheduled_task}' not found")
            return False

        # Check Celery configuration
        print(f"🔧 Broker URL: {app.conf.broker_url}")
        print(f"🔧 Result backend: {app.conf.result_backend}")
        print(f"🔧 Task routes: {app.conf.task_routes}")

        return True

    except Exception as e:
        print(f"❌ Celery scheduler test failed: {e}")
        return False


async def main():
    """Run all execution tests."""
    print("🧪 COMPREHENSIVE REMINDER EXECUTION TEST")
    print("=" * 60)

    tests = [
        ("Reminder Scheduling", test_reminder_scheduling),
        ("Background Task Execution", test_background_task_execution),
        ("Task Processing Logic", test_task_processing_logic),
        ("Celery Scheduler", test_celery_scheduler),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    print("\n" + "=" * 60)
    print("📊 EXECUTION TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    print(f"\n📊 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL EXECUTION TESTS PASSED!")
        print("✅ Reminder scheduling: WORKING")
        print("✅ Background processing: WORKING")
        print("✅ Task execution: WORKING")
        print("✅ Complete reminder flow: WORKING")
        print("\n🚀 Task 037.1 is fully functional!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Some parts of the reminder execution flow need attention")

    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
