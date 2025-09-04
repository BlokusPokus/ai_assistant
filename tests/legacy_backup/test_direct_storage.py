"""
Direct test of storage functions without importing full package.
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


async def test_direct_storage():
    """Test storage functions directly."""
    print("🧪 Testing Direct Storage Functions")
    print("=" * 50)

    try:
        print("📋 Testing direct imports...")

        # Import only what we need
        from personal_assistant.config.feature_flags import get_feature_flag_manager
        print("   ✅ Feature flags imported successfully")

        from personal_assistant.types.state import AgentState
        print("   ✅ AgentState imported successfully")

        print("📋 Testing feature flags...")
        feature_manager = get_feature_flag_manager()
        all_flags = feature_manager.get_all_flags()

        print(f"   Current feature flags: {len(all_flags)} flags")
        for flag_name, value in all_flags.items():
            print(f"   🚩 {flag_name}: {value}")

        # Check if normalized storage is enabled
        use_normalized = feature_manager.get_value("USE_NORMALIZED_STORAGE")
        if use_normalized:
            print("   ✅ Normalized storage is enabled")
        else:
            print("   ❌ Normalized storage is disabled")
            return False

        print("📋 Testing AgentState creation...")
        test_state = AgentState(
            user_input="Test user input for direct storage test",
            memory_context=[
                {
                    'content': 'Test context item 1',
                    'source': 'test_source',
                    'relevance_score': 0.9,
                    'context_type': 'test_context'
                }
            ],
            conversation_history=[
                {
                    'role': 'user',
                    'content': 'Hello, testing direct storage',
                    'timestamp': '2024-12-01T10:00:00Z'
                }
            ],
            focus=['testing', 'direct', 'storage'],
            step_count=1,
            last_tool_result={'status': 'success', 'data': 'test_data'}
        )

        print(f"   ✅ Created test state with:")
        print(f"     - User input: {test_state.user_input}")
        print(f"     - Memory context: {len(test_state.memory_context)} items")
        print(
            f"     - Conversation history: {len(test_state.conversation_history)} messages")
        print(f"     - Focus areas: {test_state.focus}")
        print(f"     - Step count: {test_state.step_count}")

        print("\n🎉 Direct storage test passed!")
        return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    try:
        success = await test_direct_storage()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test execution failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Run the async test
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
