#!/usr/bin/env python3
"""
Simple test to verify database connection and session management.
"""

from sqlalchemy import select
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal
import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_database_connection():
    """Test database connection and session management."""

    print("🧪 Testing database connection...")

    try:
        async with AsyncSessionLocal() as session:
            print("✅ Database session created successfully")

            # Test a simple query
            result = await session.execute(select(User).limit(1))
            users = result.scalars().all()

            print(f"✅ Database query successful, found {len(users)} users")

            # Test phone number lookup
            if users:
                print(f"✅ First user: {users[0].email}")

            return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run the test."""

    print("🚀 Personal Assistant - Database Connection Test")
    print("=" * 50)

    # Run the test
    success = asyncio.run(test_database_connection())

    if success:
        print("\n🎉 Database connection test passed!")
        print("You can now test SMS functionality")
    else:
        print("\n❌ Database connection test failed!")
        print("Check the error messages above")


if __name__ == "__main__":
    main()
