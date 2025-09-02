"""
Simple test to check if the basic models can be imported and created.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_model_imports():
    """Test if the basic models can be imported."""
    print("🧪 Testing Basic Model Imports")
    print("=" * 40)

    try:
        print("📋 Importing base...")
        from personal_assistant.database.models.base import Base
        print("   ✅ Base imported successfully")

        print("📋 Importing conversation_state...")
        from personal_assistant.database.models.conversation_state import ConversationState
        print("   ✅ ConversationState imported successfully")

        print("📋 Importing conversation_message...")
        from personal_assistant.database.models.conversation_message import ConversationMessage
        print("   ✅ ConversationMessage imported successfully")

        print("📋 Importing memory_context_item...")
        from personal_assistant.database.models.memory_context_item import MemoryContextItem
        print("   ✅ MemoryContextItem imported successfully")

        print("📋 Importing users...")
        from personal_assistant.database.models.users import User
        print("   ✅ User imported successfully")

        print("\n🎉 All models imported successfully!")
        return True

    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_model_creation():
    """Test if the basic models can be created."""
    print("\n🧪 Testing Basic Model Creation")
    print("=" * 40)

    try:
        from personal_assistant.database.models.conversation_state import ConversationState
        from personal_assistant.database.models.conversation_message import ConversationMessage
        from personal_assistant.database.models.memory_context_item import MemoryContextItem

        print("📋 Creating ConversationState...")
        state = ConversationState(
            conversation_id="test-123",
            user_id=1,
            user_input="Test input",
            focus_areas=["test"],
            step_count=1
        )
        print("   ✅ ConversationState created successfully")

        print("📋 Creating ConversationMessage...")
        message = ConversationMessage(
            conversation_id="test-123",
            role="user",
            content="Test message",
            message_type="user_input"
        )
        print("   ✅ ConversationMessage created successfully")

        print("📋 Creating MemoryContextItem...")
        context_item = MemoryContextItem(
            conversation_id="test-123",
            source="test",
            content="Test context",
            relevance_score=0.8,
            context_type="test"
        )
        print("   ✅ MemoryContextItem created successfully")

        print("\n🎉 All models created successfully!")
        return True

    except Exception as e:
        print(f"   ❌ Model creation failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Simple Model Test (Task 053)")
    print("=" * 50)

    # Test imports
    imports_ok = test_model_imports()

    if imports_ok:
        # Test model creation
        creation_ok = test_model_creation()

        if creation_ok:
            print("\n🎉 All tests passed! Models are working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Model creation tests failed.")
            sys.exit(1)
    else:
        print("\n❌ Model import tests failed.")
        sys.exit(1)
