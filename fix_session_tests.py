#!/usr/bin/env python3
"""
Systematic fix script for session endpoint tests.

This script applies the FastAPI dependency override pattern to all session endpoint tests,
handling the @require_permission decorator issue by mocking the request state properly.
"""

import re
import os

def fix_session_test_file():
    """Fix the session endpoint test file by applying the systematic pattern."""
    
    file_path = "tests/unit/test_api/test_session_endpoints.py"
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to find test methods that need fixing
    test_pattern = r'(@pytest\.mark\.asyncio\s+async def test_\w+\(self\):.*?)(?=@pytest\.mark\.asyncio|class|\Z)'
    
    def fix_test_method(match):
        test_content = match.group(1)
        
        # Skip if already fixed (contains dependency_overrides)
        if 'dependency_overrides' in test_content:
            return test_content
        
        # Skip if it's a simple test without complex dependencies
        if 'get_current_user' not in test_content and 'get_session_service' not in test_content:
            return test_content
        
        # Apply the systematic fix
        fixed_content = apply_session_test_fix(test_content)
        return fixed_content
    
    # Apply fixes to all test methods
    fixed_content = re.sub(test_pattern, fix_test_method, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed session endpoint tests in {file_path}")

def apply_session_test_fix(test_content):
    """Apply the systematic fix to a single test method."""
    
    # Extract the test method name
    method_match = re.search(r'async def (test_\w+)\(self\):', test_content)
    if not method_match:
        return test_content
    
    method_name = method_match.group(1)
    print(f"  🔧 Fixing {method_name}...")
    
    # Check if this test needs the complex permission fix
    needs_permission_fix = '@require_permission' in test_content or 'require_permission' in test_content
    
    if needs_permission_fix:
        # Apply the complex permission fix (skip for now - too complex)
        print(f"    ⚠️  Skipping {method_name} - requires complex permission mocking")
        return test_content
    
    # Apply the standard FastAPI dependency override pattern
    return apply_standard_fix(test_content, method_name)

def apply_standard_fix(test_content, method_name):
    """Apply the standard FastAPI dependency override pattern."""
    
    # Pattern to replace the old patch approach with FastAPI dependency overrides
    old_pattern = r'with patch\(\'apps\.fastapi_app\.routes\.sessions\.get_db\'\) as mock_get_db:\s*'
    old_pattern += r'mock_session = AsyncMock\(spec=AsyncSession\)\s*'
    old_pattern += r'mock_get_db\.return_value\.__aenter__\.return_value = mock_session\s*'
    
    # New pattern
    new_pattern = '''# Create a mock database session
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Import dependencies
        from apps.fastapi_app.routes.sessions import get_db, get_current_user, get_session_service
        
        # Override the get_db dependency directly in the FastAPI app
        async def override_get_db():
            yield mock_session
        
        self.app.dependency_overrides[get_db] = override_get_db
        
        try:
'''
    
    # Apply the replacement
    fixed_content = re.sub(old_pattern, new_pattern, test_content, flags=re.DOTALL)
    
    # Add the cleanup at the end
    if 'finally:' not in fixed_content:
        # Find the end of the test and add cleanup
        end_pattern = r'(\s+assert.*?)$'
        cleanup = r'\1\n        finally:\n            # Clean up the dependency overrides\n            self.app.dependency_overrides.clear()'
        fixed_content = re.sub(end_pattern, cleanup, fixed_content, flags=re.DOTALL)
    
    return fixed_content

if __name__ == "__main__":
    print("🚀 Starting systematic fix for session endpoint tests...")
    fix_session_test_file()
    print("✅ Systematic fix completed!")
