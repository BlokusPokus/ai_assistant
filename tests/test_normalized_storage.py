"""
Test script for Task 053: Normalized Storage Layer

This script tests the new normalized storage layer implementation,
validating save_state, load_state, and other operations.
"""

from personal_assistant.config.feature_flags import (
    get_feature_flag_manager,
    use_normalized_storage,
    normalized_storage_fallback
)
from personal_assistant.memory.normalized_storage import (
    save_state_normalized,
    load_state_normalized,
    update_state_partial,
    delete_conversation_normalized
)
from personal_assistant.types.state import AgentState, StateConfig
import asyncio
import json
import sys
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


async def test_normalized_storage():
    """Test the normalized storage layer functionality."""
    print("🧪 Testing Normalized Storage Layer for Task 053")
    print("=" * 60)

    # Test 1: Feature Flag System
    print("\n📋 Test 1: Feature Flag System")
    feature_manager = get_feature_flag_manager()

    # Check current feature flags
    all_flags = feature_manager.get_all_flags()
    print(f"   Current feature flags: {len(all_flags)} flags")
    for flag_name, value in all_flags.items():
        print(f"   🚩 {flag_name}: {value}")

    # Test normalized storage flag
    use_normalized = use_normalized_storage()
    print(f"   Use normalized storage: {use_normalized}")

    if not use_normalized:
        print(
            "   ⚠️  Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")
        print("   🧪 Continuing with tests to validate functionality...")

    # Test 2: Create Test AgentState
    print("\n📝 Test 2: Create Test AgentState")

    # Create a comprehensive test state
    test_state = AgentState(
        user_input="Test user input for normalized storage validation",
        memory_context=[
            {
                'content': 'Test context item 1',
                'source': 'test_source',
                'relevance_score': 0.8,
                'context_type': 'test_context'
            },
            {
                'content': 'Test context item 2',
                'source': 'test_source',
                'relevance_score': 0.6,
                'context_type': 'test_context'
            }
        ],
        conversation_history=[
            {
                'role': 'user',
                'content': 'Hello, this is a test conversation',
                'timestamp': '2024-12-01T10:00:00Z'
            },
            {
                'role': 'assistant',
                'content': 'Hello! I understand this is a test conversation.',
                'timestamp': '2024-12-01T10:00:01Z'
            },
            {
                'role': 'tool',
                'content': 'Tool execution result',
                'tool_name': 'test_tool',
                'tool_success': 'success',
                'timestamp': '2024-12-01T10:00:02Z'
            }
        ],
        focus=['testing', 'validation', 'storage'],
        step_count=3,
        last_tool_result={'status': 'success', 'data': 'test_data'}
    )

    print(f"   ✅ Created test state with:")
    print(f"     - User input: {test_state.user_input}")
    print(f"     - Memory context: {len(test_state.memory_context)} items")
    print(
        f"     - Conversation history: {len(test_state.conversation_history)} messages")
    print(f"     - Focus areas: {test_state.focus}")
    print(f"     - Step count: {test_state.step_count}")

    # Test 3: Save State Using Normalized Storage
    print("\n💾 Test 3: Save State Using Normalized Storage")

    test_conversation_id = f"test-normalized-storage-{int(time.time())}"
    test_user_id = 1  # Test user ID

    try:
        await save_state_normalized(test_conversation_id, test_state, test_user_id)
        print(
            f"   ✅ Successfully saved state for conversation: {test_conversation_id}")
    except Exception as e:
        print(f"   ❌ Failed to save state: {e}")
        print("   🔄 Skipping remaining tests due to save failure")
        return False

    # Test 4: Load State Using Normalized Storage
    print("\n📂 Test 4: Load State Using Normalized Storage")

    try:
        loaded_state = await load_state_normalized(
            test_conversation_id,
            test_user_id,
            max_messages=50,
            max_context_items=20,
            min_relevance_score=0.3
        )

        if loaded_state:
            print(
                f"   ✅ Successfully loaded state for conversation: {test_conversation_id}")
            print(f"     - Loaded user input: {loaded_state.user_input}")
            print(
                f"     - Loaded memory context: {len(loaded_state.memory_context)} items")
            print(
                f"     - Loaded conversation history: {len(loaded_state.conversation_history)} messages")
            print(f"     - Loaded focus areas: {loaded_state.focus}")
            print(f"     - Loaded step count: {loaded_state.step_count}")

            # Validate data integrity
            data_integrity_ok = True

            if loaded_state.user_input != test_state.user_input:
                print(
                    f"   ⚠️  User input mismatch: expected '{test_state.user_input}', got '{loaded_state.user_input}'")
                data_integrity_ok = False

            if len(loaded_state.memory_context) != len(test_state.memory_context):
                print(
                    f"   ⚠️  Memory context count mismatch: expected {len(test_state.memory_context)}, got {len(loaded_state.memory_context)}")
                data_integrity_ok = False

            if len(loaded_state.conversation_history) != len(test_state.conversation_history):
                print(
                    f"   ⚠️  Conversation history count mismatch: expected {len(test_state.conversation_history)}, got {len(loaded_state.conversation_history)}")
                data_integrity_ok = False

            if set(loaded_state.focus) != set(test_state.focus):
                print(
                    f"   ⚠️  Focus areas mismatch: expected {test_state.focus}, got {loaded_state.focus}")
                data_integrity_ok = False

            if loaded_state.step_count != test_state.step_count:
                print(
                    f"   ⚠️  Step count mismatch: expected {test_state.step_count}, got {loaded_state.step_count}")
                data_integrity_ok = False

            if data_integrity_ok:
                print("   ✅ Data integrity validation passed")
            else:
                print("   ❌ Data integrity validation failed")
                return False
        else:
            print(
                f"   ❌ Failed to load state for conversation: {test_conversation_id}")
            return False

    except Exception as e:
        print(f"   ❌ Failed to load state: {e}")
        return False

    # Test 5: Partial State Update
    print("\n🔄 Test 5: Partial State Update")

    try:
        # Update specific fields
        updates = {
            'user_input': 'Updated user input for partial update test',
            'step_count': 5,
            'new_messages': [
                {
                    'role': 'user',
                    'content': 'This is a new message from partial update',
                    'timestamp': '2024-12-01T10:05:00Z'
                }
            ],
            'new_context_items': [
                {
                    'content': 'New context item from partial update',
                    'source': 'partial_update',
                    'relevance_score': 0.9,
                    'context_type': 'update_test'
                }
            ]
        }

        update_success = await update_state_partial(test_conversation_id, updates, test_user_id)

        if update_success:
            print("   ✅ Successfully updated state partially")

            # Verify the updates
            updated_state = await load_state_normalized(test_conversation_id, test_user_id)
            if updated_state:
                print(f"   📋 Verification of updates:")
                print(f"     - Updated user input: {updated_state.user_input}")
                print(f"     - Updated step count: {updated_state.step_count}")
                print(
                    f"     - Total messages after update: {len(updated_state.conversation_history)}")
                print(
                    f"     - Total context items after update: {len(updated_state.memory_context)}")

                # Check if new message was added
                new_message_found = any(
                    msg.get(
                        'content') == 'This is a new message from partial update'
                    for msg in updated_state.conversation_history
                )
                if new_message_found:
                    print("   ✅ New message from partial update found")
                else:
                    print("   ❌ New message from partial update not found")

                # Check if new context item was added
                new_context_found = any(
                    ctx.get('content') == 'New context item from partial update'
                    for ctx in updated_state.memory_context
                )
                if new_context_found:
                    print("   ✅ New context item from partial update found")
                else:
                    print("   ❌ New context item from partial update not found")
            else:
                print("   ❌ Failed to load updated state for verification")
                return False
        else:
            print("   ❌ Failed to update state partially")
            return False

    except Exception as e:
        print(f"   ❌ Failed to update state partially: {e}")
        return False

    # Test 6: Load State with Limits
    print("\n📊 Test 6: Load State with Limits")

    try:
        # Test loading with different limits
        limited_state = await load_state_normalized(
            test_conversation_id,
            test_user_id,
            max_messages=2,  # Only load 2 messages
            max_context_items=1,  # Only load 1 context item
            min_relevance_score=0.8  # Only load high-relevance items
        )

        if limited_state:
            print(f"   ✅ Successfully loaded state with limits:")
            print(
                f"     - Messages loaded: {len(limited_state.conversation_history)} (limited to 2)")
            print(
                f"     - Context items loaded: {len(limited_state.memory_context)} (limited to 1)")

            # Verify limits were respected
            if len(limited_state.conversation_history) <= 2:
                print("   ✅ Message limit respected")
            else:
                print("   ❌ Message limit not respected")
                return False

            if len(limited_state.memory_context) <= 1:
                print("   ✅ Context item limit respected")
            else:
                print("   ❌ Context item limit not respected")
                return False

            # Verify relevance score filter
            all_high_relevance = all(
                ctx.get('relevance_score', 0) >= 0.8
                for ctx in limited_state.memory_context
            )
            if all_high_relevance:
                print("   ✅ Relevance score filter working")
            else:
                print("   ❌ Relevance score filter not working")
                return False
        else:
            print("   ❌ Failed to load state with limits")
            return False

    except Exception as e:
        print(f"   ❌ Failed to load state with limits: {e}")
        return False

    # Test 7: Cleanup - Delete Test Conversation
    print("\n🧹 Test 7: Cleanup - Delete Test Conversation")

    try:
        delete_success = await delete_conversation_normalized(test_conversation_id, test_user_id)

        if delete_success:
            print(
                f"   ✅ Successfully deleted test conversation: {test_conversation_id}")

            # Verify deletion
            deleted_state = await load_state_normalized(test_conversation_id, test_user_id)
            if deleted_state is None:
                print(
                    "   ✅ Deletion verification passed - conversation no longer exists")
            else:
                print("   ❌ Deletion verification failed - conversation still exists")
                return False
        else:
            print(
                f"   ❌ Failed to delete test conversation: {test_conversation_id}")
            return False

    except Exception as e:
        print(f"   ❌ Failed to delete conversation: {e}")
        return False

    # All tests passed
    print("\n🎉 All Normalized Storage Tests Passed Successfully!")
    print("✅ The new normalized storage layer is working correctly")
    print("✅ Ready for integration with existing code")

    return True


async def main():
    """Main test function."""
    try:
        success = await test_normalized_storage()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test execution failed with error: {e}")
        return 1


if __name__ == "__main__":
    # Run the async test
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
