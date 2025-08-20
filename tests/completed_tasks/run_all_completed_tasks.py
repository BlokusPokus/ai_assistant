#!/usr/bin/env python3
"""
Comprehensive test runner for all completed tasks.

This script runs all tests from completed tasks to ensure no breaking changes
have been introduced. Run this after completing any new task.

Completed Tasks:
- Task 030: Authentication System
- Task 031: MFA & Security  
- Task 032: RBAC System
- Task 033: Database Migration & Optimization

Usage:
    python -m tests.completed_tasks.run_all_completed_tasks
    pytest tests/completed_tasks/run_all_completed_tasks.py -v
"""

import sys
import subprocess
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def run_test_suite(test_path, description):
    """Run a specific test suite and return the result."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")

    try:
        # Run pytest on the specific test path
        result = subprocess.run([
            sys.executable, "-m", "pytest", str(test_path),
            "-v", "--tb=short", "--color=yes"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            print(f"✅ {description} - ALL TESTS PASSED")
            return True
        else:
            print(f"❌ {description} - TESTS FAILED")
            print("STDOUT:")
            print(result.stdout)
            print("STDERR:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ {description} - ERROR RUNNING TESTS: {e}")
        return False


def main():
    """Run all completed task tests."""
    print("🚀 Running Comprehensive Test Suite for All Completed Tasks")
    print("=" * 70)

    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / "tests"

    # Define test suites to run
    test_suites = [
        {
            "path": tests_dir / "test_auth",
            "description": "Task 030-032: Authentication, MFA & RBAC System Tests"
        },
        {
            "path": tests_dir / "test_task_033_database_optimization.py",
            "description": "Task 033: Database Migration & Optimization Tests"
        }
    ]

    # Track results
    results = []
    total_tests = len(test_suites)

    # Run each test suite
    for test_suite in test_suites:
        success = run_test_suite(test_suite["path"], test_suite["description"])
        results.append((test_suite["description"], success))

    # Print summary
    print(f"\n{'='*70}")
    print("📊 TEST SUITE SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for _, success in results if success)
    failed = total_tests - passed

    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")

    print(f"\nOverall Result: {passed}/{total_tests} test suites passed")

    if failed > 0:
        print(
            f"\n❌ {failed} test suite(s) failed. Please fix the issues before proceeding.")
        sys.exit(1)
    else:
        print(
            f"\n🎉 All {total_tests} test suites passed! No breaking changes detected.")
        print("✅ Safe to proceed with next task.")


if __name__ == "__main__":
    main()
