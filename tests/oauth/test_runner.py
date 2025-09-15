"""
OAuth Test Runner

This script runs all OAuth tests and provides a comprehensive test report.
"""

import pytest
import sys
import os
from pathlib import Path


def run_oauth_tests():
    """Run all OAuth tests and return results."""
    
    # Add the project root to the Python path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Test directories to run
    test_dirs = [
        "tests/oauth",
        "tests/agent_oauth", 
        "tests/e2e_oauth",
        "tests/security_oauth"
    ]
    
    # Run tests with verbose output
    args = [
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker handling
        "--disable-warnings",  # Disable warnings for cleaner output
    ]
    
    # Add test directories
    args.extend(test_dirs)
    
    print("🚀 Starting OAuth Test Suite...")
    print("=" * 60)
    
    # Run pytest
    exit_code = pytest.main(args)
    
    print("=" * 60)
    if exit_code == 0:
        print("✅ All OAuth tests passed!")
    else:
        print("❌ Some OAuth tests failed!")
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_oauth_tests()
    sys.exit(exit_code)
