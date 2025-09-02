#!/usr/bin/env python3
"""
Test runner for NotionPagesTool tests.

This script runs all tests for the NotionPagesTool and provides a summary.
"""

import sys
import os
import subprocess
import pytest


def run_tests():
    """Run the NotionPagesTool tests and return results."""
    print("🧪 Running NotionPagesTool Tests...")
    print("=" * 50)
    
    # Get the directory of this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the test directory
    os.chdir(test_dir)
    
    # Run pytest with basic options (no coverage for now)
    cmd = [
        sys.executable, "-m", "pytest",
        "test_notion_pages_tool.py",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "--durations=10",  # Show top 10 slowest tests
        "-W", "ignore::DeprecationWarning",  # Ignore deprecation warnings
        "-W", "ignore::PendingDeprecationWarning"  # Ignore pending deprecation warnings
    ]
    
    try:
        # Run the tests
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"Exit Code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_specific_test(test_name):
    """Run a specific test by name."""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "test_notion_pages_tool.py",
        f"-k{test_name}",  # Run only tests matching this name
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def list_tests():
    """List all available tests."""
    print("📋 Available Tests:")
    print("=" * 50)
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "test_notion_pages_tool.py",
        "--collect-only",  # Only collect tests, don't run them
        "-q"  # Quiet mode
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            # Parse and display test names nicely
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('test_notion_pages_tool.py::'):
                    test_name = line.split('::')[1]
                    print(f"  • {test_name}")
        else:
            print("  No tests found")
            
    except Exception as e:
        print(f"❌ Error listing tests: {e}")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_tests()
        elif command == "run":
            if len(sys.argv) > 2:
                test_name = sys.argv[2]
                success = run_specific_test(test_name)
                sys.exit(0 if success else 1)
            else:
                print("Usage: python run_notion_tests.py run <test_name>")
                sys.exit(1)
        elif command == "help":
            print("NotionPagesTool Test Runner")
            print("=" * 30)
            print("Commands:")
            print("  list    - List all available tests")
            print("  run     - Run all tests")
            print("  run <test_name> - Run a specific test")
            print("  help    - Show this help message")
            print("\nExamples:")
            print("  python run_notion_tests.py list")
            print("  python run_notion_tests.py run")
            print("  python run_notion_tests.py run test_create_note_page_success")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python run_notion_tests.py help' for usage information")
            sys.exit(1)
    else:
        # Default: run all tests
        success = run_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
