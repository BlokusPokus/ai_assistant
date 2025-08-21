#!/usr/bin/env python3
"""
Simple script to add phone_number field to users table.

This script will add the phone_number column to the users table
if it doesn't already exist.
"""

from sqlalchemy import text
from personal_assistant.database.session import AsyncSessionLocal
import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def check_database_connection():
    """Check if we can connect to the database."""

    try:
        async with await AsyncSessionLocal() as session:
            # Try a simple query
            result = await session.execute(text("SELECT 1"))
            await session.commit()
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def add_phone_number_field():
    """Add phone_number field to users table if it doesn't exist."""

    try:
        async with await AsyncSessionLocal() as session:
            print("🔍 Checking if phone_number field exists in users table...")

            # Check if the column exists
            result = await session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'phone_number'
            """))

            column_exists = result.fetchone()

            if column_exists:
                print("✅ phone_number field already exists in users table")
                return True

            print("🔧 Adding phone_number field to users table...")

            # Add the column
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN phone_number VARCHAR(20) UNIQUE
            """))

            # Create index for performance
            await session.execute(text("""
                CREATE INDEX idx_users_phone_number ON users(phone_number)
            """))

            await session.commit()

            print("✅ phone_number field added successfully")
            print("✅ Index created for phone number lookups")

            return True

    except Exception as e:
        print(f"❌ Error adding phone_number field: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run the database migration."""

    print("🚀 Personal Assistant - Database Migration")
    print("=" * 40)

    # Check database connection
    if not asyncio.run(check_database_connection()):
        print("❌ Cannot proceed without database connection")
        return

    # Add phone number field
    success = asyncio.run(add_phone_number_field())

    if success:
        print("\n🎯 Database migration completed successfully!")
        print("You can now run the create_admin_user.py script to create your admin user.")
    else:
        print("\n❌ Database migration failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
