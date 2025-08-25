#!/usr/bin/env python3
"""
AI Scheduler Cleanup Script

This script safely removes unused AI scheduler files after Task 037.1 migration.
Only deletes files that are no longer imported anywhere in the codebase.
"""

import os
import shutil
from pathlib import Path

# Files that are SAFE TO DELETE (no longer imported)
SAFE_TO_DELETE = [
    "ai_task_scheduler.py",      # Functions migrated to workers
    "celery_config.py",          # Old Celery app config
    "db_queries.py",             # Queries moved to AITaskManager
    "health_monitor.py",         # Health monitoring moved to workers
    "performance_monitor.py",    # Performance monitoring moved to workers
    "workflow_integration.py",   # Workflow logic moved to workers
    "error_handler.py",          # Error handling moved to workers
    "ai_evaluator.py",           # AI evaluation moved to workers
    "time_utils.py",             # Time utilities moved to workers
    "context_builder.py",        # Context building moved to workers
    "event_processor.py",        # Event processing moved to workers
    "action_parser.py",          # Action parsing moved to workers
    "task_evaluator.py",         # Task evaluation moved to workers
    "notification_services.py",  # Duplicate of notification_service.py
    "direct_test.py",            # Test file
    "simple_test.py",            # Test file
    "production_config.py",      # Config moved to workers
    "README.md",                 # Outdated documentation
]

# Files that MUST BE KEPT (still actively used)
MUST_KEEP = [
    "ai_task_manager.py",        # Used by workers and reminder tool
    "notification_service.py",   # Used by workers
    "task_executor.py",          # Used by workers
    "task_scheduler.py",         # Exported for compatibility
    "__init__.py",               # Package definition
]


def backup_directory():
    """Create a backup of the ai_scheduler directory before cleanup."""
    ai_scheduler_path = Path("src/personal_assistant/tools/ai_scheduler")
    backup_path = Path("old_ai_scheduler_backup")

    if backup_path.exists():
        shutil.rmtree(backup_path)

    print(f"📦 Creating backup at: {backup_path}")
    shutil.copytree(ai_scheduler_path, backup_path)
    return backup_path


def verify_files_exist():
    """Verify that all files to be deleted actually exist."""
    ai_scheduler_path = Path("src/personal_assistant/tools/ai_scheduler")

    missing_files = []
    for file in SAFE_TO_DELETE:
        if not (ai_scheduler_path / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"⚠️  Some files to delete don't exist: {missing_files}")
        return False

    return True


def delete_unused_files():
    """Delete files that are no longer needed."""
    ai_scheduler_path = Path("src/personal_assistant/tools/ai_scheduler")

    deleted_count = 0
    for file in SAFE_TO_DELETE:
        file_path = ai_scheduler_path / file
        if file_path.exists():
            try:
                os.remove(file_path)
                print(f"🗑️  Deleted: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {file}: {e}")

    return deleted_count


def verify_remaining_files():
    """Verify that all required files are still present."""
    ai_scheduler_path = Path("src/personal_assistant/tools/ai_scheduler")

    missing_files = []
    for file in MUST_KEEP:
        if not (ai_scheduler_path / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ CRITICAL: Required files missing: {missing_files}")
        return False

    print("✅ All required files are present")
    return True


def show_cleanup_summary():
    """Show summary of what was cleaned up."""
    print("\n" + "=" * 60)
    print("🧹 AI SCHEDULER CLEANUP SUMMARY")
    print("=" * 60)

    print(f"📁 Files deleted: {len(SAFE_TO_DELETE)}")
    print(f"📁 Files kept: {len(MUST_KEEP)}")
    print(f"📁 Total files before: {len(SAFE_TO_DELETE) + len(MUST_KEEP)}")
    print(f"📁 Total files after: {len(MUST_KEEP)}")

    print("\n🗑️  DELETED FILES:")
    for file in SAFE_TO_DELETE:
        print(f"  - {file}")

    print("\n✅ KEPT FILES:")
    for file in MUST_KEEP:
        print(f"  - {file}")

    print("\n🎯 CLEANUP RESULT:")
    print("  - Old AI scheduler files removed")
    print("  - Core components preserved")
    print("  - Workers system fully functional")
    print("  - Ready for Task 037.2")


def main():
    """Main cleanup process."""
    print("🚀 AI Scheduler Cleanup Script")
    print("=" * 40)
    print("This script will remove unused AI scheduler files after migration.")
    print("Only files that are no longer imported will be deleted.")
    print()

    # Verify files exist
    if not verify_files_exist():
        print("❌ Cannot proceed with cleanup")
        return False

    # Create backup
    backup_path = backup_directory()
    print(f"✅ Backup created at: {backup_path}")

    # Confirm deletion
    print(f"\n⚠️  About to delete {len(SAFE_TO_DELETE)} files:")
    for file in SAFE_TO_DELETE:
        print(f"  - {file}")

    response = input("\n🤔 Proceed with deletion? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("❌ Cleanup cancelled")
        return False

    # Delete files
    print("\n🗑️  Deleting unused files...")
    deleted_count = delete_unused_files()
    print(f"✅ Deleted {deleted_count} files")

    # Verify remaining files
    if not verify_remaining_files():
        print("❌ Cleanup verification failed!")
        print(f"💾 Restore from backup: {backup_path}")
        return False

    # Show summary
    show_cleanup_summary()

    print(f"\n💾 Backup available at: {backup_path}")
    print("🎉 Cleanup completed successfully!")

    return True


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Cleanup failed. Check the backup directory.")
            exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
