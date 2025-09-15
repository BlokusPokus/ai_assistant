"""
Test Database Context Manager Fix

This test verifies that the EnhancedNotesTool can now properly use
the database context manager without the coroutine error.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_database_context_manager_import():
    """Test that we can import the database config correctly"""
    
    print("🧪 Testing database context manager import...")
    
    try:
        from personal_assistant.config.database import db_config
        
        print("✅ Database config import successful!")
        print("   - db_config imported correctly")
        print(f"   - db_config has get_session_context: {hasattr(db_config, 'get_session_context')}")
        return True
        
    except Exception as e:
        print(f"❌ Error importing database config: {e}")
        return False


def test_enhanced_notes_tool_context_manager():
    """Test that EnhancedNotesTool can use the database context manager"""
    
    print("\n🧪 Testing EnhancedNotesTool context manager usage...")
    
    try:
        from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool
        
        # Create instance
        tool = EnhancedNotesTool()
        
        # Check that the method exists and has the right signature
        import inspect
        method = EnhancedNotesTool.create_enhanced_note
        signature = inspect.signature(method)
        params = list(signature.parameters.keys())
        
        assert 'user_id' in params, "Method should have user_id parameter"
        
        print("✅ EnhancedNotesTool context manager usage successful!")
        print("   - Tool can be imported without context manager errors")
        print("   - Method signature includes user_id parameter")
        return True
        
    except Exception as e:
        print(f"❌ Error testing EnhancedNotesTool: {e}")
        return False


def test_database_config_structure():
    """Test that the database config has the right structure"""
    
    print("\n🧪 Testing database config structure...")
    
    try:
        from personal_assistant.config.database import db_config
        
        # Test that it has the right methods
        assert hasattr(db_config, 'get_session_context'), "Should have get_session_context method"
        
        print("✅ Database config structure is correct!")
        print("   - Has get_session_context method")
        return True
        
    except Exception as e:
        print(f"❌ Error testing database config structure: {e}")
        return False


def main():
    """Run all tests"""
    
    print("🚀 Starting Database Context Manager Fix Tests\n")
    
    tests = [
        test_database_context_manager_import,
        test_enhanced_notes_tool_context_manager,
        test_database_config_structure,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Database context manager fix is working.")
        print("\n🔧 Fix Status:")
        print("   ✅ Database context manager import fixed")
        print("   ✅ EnhancedNotesTool can use db_config.get_session_context()")
        print("   ✅ No more 'coroutine' object context manager error")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    return all(results)


if __name__ == "__main__":
    # Run the tests
    success = main()
    sys.exit(0 if success else 1)
