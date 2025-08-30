"""
Basic database test to validate connection and simple operations.
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


async def test_database_basic():
    """Test basic database operations."""
    print("🧪 Testing Basic Database Operations")
    print("=" * 50)

    try:
        print("📋 Testing database connection...")

        # Import database connection
        from personal_assistant.database.session import AsyncSessionLocal
        print("   ✅ Database connection imported successfully")

        print("📋 Testing database session...")
        async with AsyncSessionLocal() as session:
            print("   ✅ Database session created successfully")

            # Test a simple query
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row.test == 1:
                print("   ✅ Basic SQL query executed successfully")
            else:
                print("   ❌ Basic SQL query failed")
                return False

        print("📋 Testing feature flags...")
        from personal_assistant.config.feature_flags import get_feature_flag_manager
        feature_manager = get_feature_flag_manager()
        use_normalized = feature_manager.get_value("USE_NORMALIZED_STORAGE")

        if use_normalized:
            print("   ✅ Normalized storage is enabled")
        else:
            print("   ❌ Normalized storage is disabled")
            return False

        print("📋 Testing AgentState creation...")
        from personal_assistant.types.state import AgentState
        test_state = AgentState(
            user_input="Test user input for database test",
            memory_context=[],
            conversation_history=[],
            focus=['testing', 'database'],
            step_count=1,
            last_tool_result={'status': 'success'}
        )
        print("   ✅ AgentState created successfully")

        print("\n🎉 Basic database test passed!")
        print("✅ Database connection working")
        print("✅ Feature flags working")
        print("✅ AgentState creation working")
        print("✅ Ready to proceed with storage implementation")

        return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    try:
        success = await test_database_basic()
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
