"""
Minimal test to isolate the model issue.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_minimal_imports():
    """Test minimal model imports."""
    print("🧪 Testing Minimal Model Imports")
    print("=" * 40)

    try:
        print("📋 Importing base only...")
        from personal_assistant.database.models.base import Base
        print("   ✅ Base imported successfully")

        print("📋 Creating Base instance...")
        base = Base()
        print("   ✅ Base instance created successfully")

        print("\n🎉 Minimal test passed!")
        return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Minimal Model Test (Task 053)")
    print("=" * 50)

    success = test_minimal_imports()

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed.")
        sys.exit(1)
