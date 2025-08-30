#!/usr/bin/env python3
"""
Test runner for Internet Tools.

This script runs all tests related to the internet tools functionality.
"""

import sys
import os
import subprocess
import pytest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


def run_tests_with_pytest():
    """Run tests using pytest directly."""
    print("🚀 Running Internet Tools Tests with pytest...")
    print("=" * 60)

    # Get the directory containing this script
    test_dir = Path(__file__).parent

    # Test files to run
    test_files = [
        test_dir / "test_internet_tools.py",
        test_dir / "test_internet_internal.py",
        test_dir / "test_internet_error_handler.py"
    ]

    # Check which test files exist
    existing_tests = [f for f in test_files if f.exists()]

    if not existing_tests:
        print("❌ No test files found!")
        return False

    print(f"📁 Found {len(existing_tests)} test files:")
    for test_file in existing_tests:
        print(f"   - {test_file.name}")

    print("\n" + "=" * 60)

    # Run pytest on each test file
    all_passed = True

    for test_file in existing_tests:
        print(f"\n🧪 Running tests in {test_file.name}...")
        print("-" * 40)

        try:
            # Run pytest with verbose output
            result = pytest.main([
                str(test_file),
                "-v",
                "--tb=short",
                "--strict-markers",
                "--disable-warnings"
            ])

            if result == 0:
                print(f"✅ {test_file.name} - All tests passed!")
            else:
                print(f"❌ {test_file.name} - Some tests failed!")
                all_passed = False

        except Exception as e:
            print(f"💥 Error running {test_file.name}: {e}")
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 All Internet Tools tests completed successfully!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

    return all_passed


def run_tests_with_subprocess():
    """Run tests using subprocess (alternative method)."""
    print("🚀 Running Internet Tools Tests with subprocess...")
    print("=" * 60)

    test_dir = Path(__file__).parent

    # Test files to run
    test_files = [
        test_dir / "test_internet_tools.py",
        test_dir / "test_internet_internal.py",
        test_dir / "test_internet_error_handler.py"
    ]

    # Check which test files exist
    existing_tests = [f for f in test_files if f.exists()]

    if not existing_tests:
        print("❌ No test files found!")
        return False

    print(f"📁 Found {len(existing_tests)} test files:")
    for test_file in existing_tests:
        print(f"   - {test_file.name}")

    print("\n" + "=" * 60)

    # Run pytest on each test file using subprocess
    all_passed = True

    for test_file in existing_tests:
        print(f"\n🧪 Running tests in {test_file.name}...")
        print("-" * 40)

        try:
            # Run pytest using subprocess
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                str(test_file),
                "-v",
                "--tb=short",
                "--strict-markers",
                "--disable-warnings"
            ], capture_output=True, text=True, cwd=test_dir)

            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            if result.returncode == 0:
                print(f"✅ {test_file.name} - All tests passed!")
            else:
                print(f"❌ {test_file.name} - Some tests failed!")
                all_passed = False

        except Exception as e:
            print(f"💥 Error running {test_file.name}: {e}")
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 All Internet Tools tests completed successfully!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

    return all_passed


def run_specific_test_file(test_file_name):
    """Run tests for a specific test file."""
    print(f"🚀 Running tests for {test_file_name}...")
    print("=" * 60)

    test_dir = Path(__file__).parent
    test_file = test_dir / test_file_name

    if not test_file.exists():
        print(f"❌ Test file {test_file_name} not found!")
        return False

    print(f"📁 Running tests in {test_file.name}")
    print("=" * 60)

    try:
        # Run pytest on the specific file
        result = pytest.main([
            str(test_file),
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings"
        ])

        if result == 0:
            print(f"✅ {test_file.name} - All tests passed!")
            return True
        else:
            print(f"❌ {test_file.name} - Some tests failed!")
            return False

    except Exception as e:
        print(f"💥 Error running {test_file.name}: {e}")
        return False


def show_test_summary():
    """Show a summary of available tests."""
    print("📋 Internet Tools Test Summary")
    print("=" * 60)

    test_dir = Path(__file__).parent

    # Test files
    test_files = [
        "test_internet_tools.py",
        "test_internet_internal.py",
        "test_internet_error_handler.py"
    ]

    print("Available test files:")
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            print(f"   ✅ {test_file}")
        else:
            print(f"   ❌ {test_file} (not found)")

    print("\nTest categories:")
    print("   🧪 test_internet_tools.py - Main tool functionality tests")
    print("   🔧 test_internet_internal.py - Internal function tests")
    print("   🚨 test_internet_error_handler.py - Error handling tests")

    print("\nUsage:")
    print("   python run_internet_tests.py                    # Run all tests")
    print("   python run_internet_tests.py --summary         # Show test summary")
    print("   python run_internet_tests.py --file FILENAME   # Run specific test file")
    print("   python run_internet_tests.py --subprocess      # Use subprocess method")


def main():
    """Main function to run tests."""
    if len(sys.argv) == 1:
        # No arguments, run all tests
        success = run_tests_with_pytest()
        sys.exit(0 if success else 1)

    elif len(sys.argv) == 2:
        if sys.argv[1] == "--summary":
            show_test_summary()
        elif sys.argv[1] == "--subprocess":
            success = run_tests_with_subprocess()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            show_test_summary()
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)

    elif len(sys.argv) == 3 and sys.argv[1] == "--file":
        # Run specific test file
        success = run_specific_test_file(sys.argv[2])
        sys.exit(0 if success else 1)

    else:
        print("❌ Invalid arguments")
        print("Use --help for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()

