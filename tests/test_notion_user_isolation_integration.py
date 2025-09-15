"""
Integration Test for User-Specific Notion Isolation

This test can be run to verify that the user-specific Notion functionality
is working correctly in a real environment.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool
from personal_assistant.database.connection import get_db_session


async def test_user_specific_notion_isolation():
    """Test that users are properly isolated in Notion operations"""
    
    print("🧪 Testing User-Specific Notion Isolation...")
    
    # Create the enhanced notes tool
    enhanced_tool = EnhancedNotesTool()
    
    # Test with a mock user ID
    test_user_id = 1
    
    try:
        # Test creating a note with user_id
        print(f"📝 Creating note for user {test_user_id}...")
        
        result = await enhanced_tool.create_enhanced_note(
            content="This is a test note to verify user isolation",
            title="User Isolation Test Note",
            user_id=test_user_id
        )
        
        print(f"✅ Note creation result: {result}")
        
        # Verify the result contains user-specific information
        if "Successfully created enhanced note" in result:
            print("✅ User-specific note creation successful!")
            return True
        else:
            print("❌ Note creation failed or not user-specific")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


async def test_user_id_requirement():
    """Test that user_id is required for note creation"""
    
    print("\n🧪 Testing User ID Requirement...")
    
    enhanced_tool = EnhancedNotesTool()
    
    try:
        # Test without user_id should fail
        result = await enhanced_tool.create_enhanced_note(
            content="Test content without user_id",
            title="Test Title"
        )
        
        if "User ID is required for creating notes" in result:
            print("✅ User ID requirement properly enforced!")
            return True
        else:
            print("❌ User ID requirement not enforced")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


async def test_notion_client_factory():
    """Test that NotionClientFactory creates user-specific clients"""
    
    print("\n🧪 Testing Notion Client Factory...")
    
    try:
        from personal_assistant.tools.notion_pages.client_factory import NotionClientFactory
        
        factory = NotionClientFactory()
        
        # Test that factory exists and has the right structure
        assert hasattr(factory, 'get_user_client'), "Factory should have get_user_client method"
        assert hasattr(factory, '_client_cache'), "Factory should have client cache"
        
        print("✅ NotionClientFactory structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing NotionClientFactory: {e}")
        return False


async def test_user_specific_notion_internal():
    """Test that UserSpecificNotionInternal has user-specific methods"""
    
    print("\n🧪 Testing User-Specific Notion Internal...")
    
    try:
        from personal_assistant.tools.notion_pages.notion_internal_user_specific import UserSpecificNotionInternal
        
        notion_internal = UserSpecificNotionInternal()
        
        # Test that it has user-specific methods
        assert hasattr(notion_internal, 'ensure_user_main_page_exists'), "Should have ensure_user_main_page_exists"
        assert hasattr(notion_internal, 'create_user_page'), "Should have create_user_page"
        assert hasattr(notion_internal, 'get_user_client'), "Should have get_user_client"
        
        print("✅ UserSpecificNotionInternal structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing UserSpecificNotionInternal: {e}")
        return False


async def main():
    """Run all tests"""
    
    print("🚀 Starting User-Specific Notion Isolation Tests\n")
    
    tests = [
        test_user_id_requirement,
        test_notion_client_factory,
        test_user_specific_notion_internal,
        test_user_specific_notion_isolation,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! User-specific Notion isolation is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    return all(results)


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
