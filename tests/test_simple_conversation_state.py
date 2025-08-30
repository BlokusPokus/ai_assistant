"""
Test with simplified ConversationState model.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_simple_conversation_state():
    """Test with simplified ConversationState model."""
    print("🧪 Testing Simplified ConversationState Model")
    print("=" * 50)

    try:
        print("📋 Importing base...")
        from personal_assistant.database.models.base import Base
        print("   ✅ Base imported successfully")

        print("📋 Creating simplified ConversationState...")
        from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql import func
        from datetime import datetime, timezone

        class SimpleConversationState(Base):
            __tablename__ = 'conversation_states'

            id = Column(Integer, primary_key=True)
            conversation_id = Column(
                String(255), unique=True, nullable=False, index=True)
            user_id = Column(Integer, ForeignKey('users.id'),
                             nullable=False, index=True)
            user_input = Column(Text)
            focus_areas = Column(JSON)
            step_count = Column(Integer, default=0)
            last_tool_result = Column(JSON)
            created_at = Column(DateTime(timezone=True),
                                server_default=func.now())
            updated_at = Column(DateTime(timezone=True),
                                server_default=func.now(), onupdate=func.now())

        print("   ✅ Simplified ConversationState created successfully")

        print("📋 Creating instance...")
        state = SimpleConversationState(
            conversation_id="test-123",
            user_id=1,
            user_input="Test input",
            focus_areas=["test"],
            step_count=1
        )
        print("   ✅ Instance created successfully")

        print("\n🎉 Simplified model test passed!")
        return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Simple ConversationState Test (Task 053)")
    print("=" * 60)

    success = test_simple_conversation_state()

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed.")
        sys.exit(1)
