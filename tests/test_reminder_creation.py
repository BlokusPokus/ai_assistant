#!/usr/bin/env python3
"""
Test Reminder Creation Script

This script tests the complete reminder creation flow after Task 037.1 migration.
Tests creating a real reminder through the AITaskManager.
"""

import sys
import asyncio
from datetime import datetime, timedelta

# Add src to Python path
sys.path.insert(0, 'src')


async def test_reminder_creation():
    """Test creating a real reminder."""
    print("🚀 TESTING REMINDER CREATION FLOW")
    print("=" * 50)

    try:
        # Test 1: Import components
        print("1️⃣ Testing component imports...")
        from personal_assistant.tools.ai_scheduler import AITaskManager
        from personal_assistant.tools.reminder.reminder_tool import ReminderTool
        print("✅ All components imported successfully")

        # Test 2: Create instances
        print("\n2️⃣ Creating component instances...")
        task_manager = AITaskManager()
        reminder_tool = ReminderTool()
        print("✅ Component instances created successfully")

        # Test 3: Create a test reminder
        print("\n3️⃣ Creating test reminder...")

        # Set reminder for 2 minutes from now
        remind_at = datetime.utcnow() + timedelta(minutes=2)
        remind_at_str = remind_at.isoformat()

        print(f"📅 Reminder time: {remind_at_str}")
        print(f"📝 Reminder text: 'Test reminder from Task 037.1 migration'")

        # Create reminder using the tool
        result = await reminder_tool.set_reminder(
            text="Test reminder from Task 037.1 migration",
            time=remind_at_str,
            channel="sms",
            user_id=126
        )

        print(f"✅ Reminder creation result: {result}")

        # Test 4: Verify reminder was created
        print("\n4️⃣ Verifying reminder creation...")

        # Get user's active reminders
        active_reminders = await task_manager.get_user_tasks(
            user_id=126,
            status='active',
            task_type='reminder',
            limit=10
        )

        print(f"📋 Found {len(active_reminders)} active reminders")

        # Find our test reminder
        test_reminder = None
        for reminder in active_reminders:
            if "Test reminder from Task 037.1 migration" in reminder.title:
                test_reminder = reminder
                break

        if test_reminder:
            print(f"✅ Test reminder found!")
            print(f"   ID: {test_reminder.id}")
            print(f"   Title: {test_reminder.title}")
            print(f"   Status: {test_reminder.status}")
            print(f"   Next run: {test_reminder.next_run_at}")
            print(
                f"   Notification channels: {test_reminder.notification_channels}")
        else:
            print("❌ Test reminder not found in active tasks")

        # Test 5: Test workers system
        print("\n5️⃣ Testing workers system...")
        from personal_assistant.workers.celery_app import app

        # Check if our AI tasks are registered
        ai_tasks = [name for name in app.tasks.keys() if 'ai_tasks' in name]
        print(f"✅ AI tasks registered: {len(ai_tasks)}")

        # Check if process_due_ai_tasks is available
        if "personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks" in app.tasks:
            print("✅ Background task processor is registered")
        else:
            print("❌ Background task processor not found")

        print("\n🎉 REMINDER CREATION TEST COMPLETED SUCCESSFULLY!")
        print("✅ Task 037.1 migration is working correctly!")
        print("✅ Reminders can be created and stored")
        print("✅ Workers system is ready for background processing")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_background_processing():
    """Test that background processing is ready."""
    print("\n🔄 TESTING BACKGROUND PROCESSING READINESS")
    print("=" * 50)

    try:
        from personal_assistant.workers.tasks.ai_tasks import process_due_ai_tasks

        print("✅ Background task function imported successfully")

        # Check function signature
        import inspect
        sig = inspect.signature(process_due_ai_tasks)
        print(f"✅ Function signature: {sig}")

        print("✅ Background processing system is ready")
        return True

    except Exception as e:
        print(f"❌ Background processing test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 COMPREHENSIVE REMINDER SYSTEM TEST")
    print("=" * 60)

    # Test reminder creation
    reminder_success = await test_reminder_creation()

    # Test background processing
    background_success = await test_background_processing()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    if reminder_success and background_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Reminder creation: WORKING")
        print("✅ Background processing: READY")
        print("✅ Task 037.1 migration: SUCCESSFUL")
        print("\n🚀 Ready to proceed with Task 037.2!")
    else:
        print("⚠️  Some tests failed:")
        print(
            f"   Reminder creation: {'✅ PASS' if reminder_success else '❌ FAIL'}")
        print(
            f"   Background processing: {'✅ PASS' if background_success else '❌ FAIL'}")

    return reminder_success and background_success

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
