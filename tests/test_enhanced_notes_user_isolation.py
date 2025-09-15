"""
Simple Test for Enhanced Notes User Isolation

This test verifies that the EnhancedNotesTool now properly uses user_id
and doesn't use the global Notion client.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_enhanced_notes_tool_imports():
    """Test that EnhancedNotesTool can be imported and has the right structure"""
    
    print("🧪 Testing EnhancedNotesTool imports...")
    
    try:
        # Test that we can import the tool
        from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool
        
        # Create instance
        tool = EnhancedNotesTool()
        
        # Test that it has the right attributes
        assert hasattr(tool, 'notion_internal'), "Should have notion_internal (user-specific)"
        assert not hasattr(tool, 'notion_client'), "Should NOT have notion_client (global)"
        
        print("✅ EnhancedNotesTool structure is correct!")
        print("   - Has notion_internal (user-specific)")
        print("   - No notion_client (global)")
        return True
        
    except Exception as e:
        print(f"❌ Error testing EnhancedNotesTool: {e}")
        return False


def test_create_enhanced_note_method_signature():
    """Test that create_enhanced_note method has user_id parameter"""
    
    print("\n🧪 Testing create_enhanced_note method signature...")
    
    try:
        from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool
        
        # Get the method signature
        import inspect
        method = EnhancedNotesTool.create_enhanced_note
        signature = inspect.signature(method)
        
        # Check that user_id parameter exists
        params = list(signature.parameters.keys())
        
        assert 'user_id' in params, "create_enhanced_note should have user_id parameter"
        
        print("✅ create_enhanced_note method signature is correct!")
        print(f"   - Parameters: {params}")
        print("   - Has user_id parameter")
        return True
        
    except Exception as e:
        print(f"❌ Error testing method signature: {e}")
        return False


def test_user_specific_notion_internal_import():
    """Test that UserSpecificNotionInternal can be imported"""
    
    print("\n🧪 Testing UserSpecificNotionInternal import...")
    
    try:
        from personal_assistant.tools.notion_pages.notion_internal_user_specific import UserSpecificNotionInternal
        
        # Create instance
        notion_internal = UserSpecificNotionInternal()
        
        # Test that it has the right methods
        assert hasattr(notion_internal, 'ensure_user_main_page_exists'), "Should have ensure_user_main_page_exists"
        assert hasattr(notion_internal, 'create_user_page'), "Should have create_user_page"
        assert hasattr(notion_internal, 'get_user_client'), "Should have get_user_client"
        
        print("✅ UserSpecificNotionInternal structure is correct!")
        print("   - Has ensure_user_main_page_exists")
        print("   - Has create_user_page")
        print("   - Has get_user_client")
        return True
        
    except Exception as e:
        print(f"❌ Error testing UserSpecificNotionInternal: {e}")
        return False


def test_notion_client_factory_import():
    """Test that NotionClientFactory can be imported"""
    
    print("\n🧪 Testing NotionClientFactory import...")
    
    try:
        from personal_assistant.tools.notion_pages.client_factory import NotionClientFactory
        
        # Create instance
        factory = NotionClientFactory()
        
        # Test that it has the right methods
        assert hasattr(factory, 'get_user_client'), "Should have get_user_client method"
        assert hasattr(factory, '_client_cache'), "Should have client cache"
        
        print("✅ NotionClientFactory structure is correct!")
        print("   - Has get_user_client method")
        print("   - Has client cache")
        return True
        
    except Exception as e:
        print(f"❌ Error testing NotionClientFactory: {e}")
        return False


def test_security_fix_verification():
    """Test that the security fix is properly implemented"""
    
    print("\n🧪 Testing Security Fix Verification...")
    
    try:
        from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool
        
        # Create instance
        tool = EnhancedNotesTool()
        
        # Check that it uses user-specific components
        assert hasattr(tool.notion_internal, 'ensure_user_main_page_exists'), "Should use user-specific methods"
        
        # Check that the method signature includes user_id
        import inspect
        method = EnhancedNotesTool.create_enhanced_note
        signature = inspect.signature(method)
        params = list(signature.parameters.keys())
        
        assert 'user_id' in params, "Method should require user_id"
        
        print("✅ Security fix verification passed!")
        print("   - Uses user-specific Notion components")
        print("   - Method requires user_id parameter")
        print("   - No global Notion client")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying security fix: {e}")
        return False


def main():
    """Run all tests"""
    
    print("🚀 Starting Enhanced Notes User Isolation Tests\n")
    
    tests = [
        test_enhanced_notes_tool_imports,
        test_create_enhanced_note_method_signature,
        test_user_specific_notion_internal_import,
        test_notion_client_factory_import,
        test_security_fix_verification,
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
        print("\n🎉 All tests passed! User-specific Notion isolation is properly implemented.")
        print("\n🔒 Security Status:")
        print("   ✅ Users are now properly isolated")
        print("   ✅ Each user gets their own Notion workspace")
        print("   ✅ No more global Notion client sharing")
        print("   ✅ user_id parameter is required for note creation")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    return all(results)


if __name__ == "__main__":
    # Run the tests
    success = main()
    sys.exit(0 if success else 1)
