#!/usr/bin/env python3
"""
Test script to verify SMS functionality works with the admin user.
"""

from personal_assistant.memory.user import get_user_id_by_phone
import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_user_lookup():
    """Test if we can find the admin user by phone number."""

    print("🧪 Testing SMS functionality...")

    # Test phone number lookup
    phone_number = "+14388290590"
    print(f"🔍 Looking up user with phone: {phone_number}")

    try:
        user_id = await get_user_id_by_phone(phone_number)

        if user_id:
            print(f"✅ Found user with ID: {user_id}")
            print("🎉 SMS functionality should work!")
        else:
            print("❌ User not found - SMS won't work")
            print("💡 Make sure you ran the SQL script to create the admin user")

    except Exception as e:
        print(f"❌ Error looking up user: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to run the test."""

    print("🚀 Personal Assistant - SMS Functionality Test")
    print("=" * 50)

    # Run the test
    asyncio.run(test_user_lookup())

    print("\n📱 Next steps:")
    print("1. If the test passed, try sending an SMS to your Twilio number")
    print("2. The system should respond with AI-generated content")
    print("3. If it fails, check the logs for authentication errors")


if __name__ == "__main__":
    main()
