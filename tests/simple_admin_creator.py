#!/usr/bin/env python3
"""
Simple script to create an admin user with phone number authentication.

This script directly connects to PostgreSQL to avoid configuration issues.
"""

import asyncio
import asyncpg
import bcrypt
import sys
import os
from datetime import datetime


async def create_admin_user(phone_number: str, email: str, full_name: str, password: str):
    """Create an admin user with the specified credentials."""

    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'ianleblanc',
        'password': 'password',
        'database': 'postgres'
    }

    try:
        print("🔌 Connecting to PostgreSQL...")
        conn = await asyncpg.connect(**db_params)
        print("✅ Database connection successful")

        # Check if phone_number column exists
        print("🔍 Checking if phone_number field exists...")
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'phone_number'
        """)

        if not columns:
            print("🔧 Adding phone_number field to users table...")
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN phone_number VARCHAR(20) UNIQUE
            """)
            print("✅ phone_number field added")

            # Create index
            await conn.execute("""
                CREATE INDEX idx_users_phone_number ON users(phone_number)
            """)
            print("✅ Index created")
        else:
            print("✅ phone_number field already exists")

        # Check if user already exists
        print(
            f"🔍 Checking if user with phone {phone_number} already exists...")
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE phone_number = $1 OR email = $2",
            phone_number, email
        )

        if existing_user:
            print("❌ User with this phone number or email already exists")
            await conn.close()
            return False

        print("✅ No existing user found, proceeding with creation...")

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt(12))

        # Create admin user
        print("🔧 Creating admin user...")
        user_id = await conn.fetchval("""
            INSERT INTO users (email, phone_number, full_name, hashed_password, is_active, is_verified, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """, email, phone_number, full_name, hashed_password.decode('utf-8'), True, True, datetime.utcnow(), datetime.utcnow())

        print(f"✅ Admin user created with ID: {user_id}")

        # Check if roles table exists and create admin role
        print("🔍 Checking for roles table...")
        roles_exist = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'roles'
            )
        """)

        if roles_exist:
            print("🔍 Checking for administrator role...")
            admin_role = await conn.fetchrow(
                "SELECT id FROM roles WHERE name = 'administrator'"
            )

            if not admin_role:
                print("🔧 Creating administrator role...")
                role_id = await conn.fetchval("""
                    INSERT INTO roles (name, description, created_at)
                    VALUES ($1, $2, $3)
                    RETURNING id
                """, 'administrator', 'System administrator with full access', datetime.utcnow())
                print(f"✅ Administrator role created with ID: {role_id}")
            else:
                role_id = admin_role['id']
                print(f"✅ Administrator role found with ID: {role_id}")

            # Check if user_roles table exists
            user_roles_exist = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_roles'
                )
            """)

            if user_roles_exist:
                print("🔧 Assigning admin role to user...")
                await conn.execute("""
                    INSERT INTO user_roles (user_id, role_id, is_primary, granted_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, role_id) DO NOTHING
                """, user_id, role_id, True, datetime.utcnow())
                print("✅ Admin role assigned to user")
        else:
            print("⚠️ Roles table not found - user created without role assignment")

        await conn.close()

        print("\n🎉 Admin user created successfully!")
        print(f"   ID: {user_id}")
        print(f"   Name: {full_name}")
        print(f"   Email: {email}")
        print(f"   Phone: {phone_number}")
        print(f"   Status: Active and Verified")

        return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run the admin user creation."""

    import argparse

    parser = argparse.ArgumentParser(
        description='Create an admin user with phone number authentication')
    parser.add_argument('--phone', '-p', required=True,
                        help='Phone number for the admin user')
    parser.add_argument('--email', '-e', required=True,
                        help='Email for the admin user')
    parser.add_argument('--name', '-n', required=True,
                        help='Full name for the admin user')
    parser.add_argument('--password', '-pw', required=True,
                        help='Password for the admin user')

    args = parser.parse_args()

    print("🚀 Personal Assistant - Simple Admin User Creation")
    print("=" * 55)

    # Validate phone number format
    phone = args.phone.strip()
    if not phone.startswith('+') and not phone.isdigit():
        print("❌ Phone number must start with + or contain only digits")
        return

    if len(phone) < 10 or len(phone) > 15:
        print("❌ Phone number must be between 10 and 15 characters")
        return

    # Validate password strength
    if len(args.password) < 8:
        print("❌ Password must be at least 8 characters long")
        return

    print(f"📱 Phone: {phone}")
    print(f"📧 Email: {args.email}")
    print(f"👤 Name: {args.name}")
    print(f"🔒 Password: {'*' * len(args.password)}")
    print()

    # Create admin user
    success = asyncio.run(create_admin_user(
        phone_number=phone,
        email=args.email,
        full_name=args.name,
        password=args.password
    ))

    if success:
        print("\n🎯 Next steps:")
        print("1. You can now log in using your phone number or email")
        print("2. Use the FastAPI app or CLI to access the system")
        print("3. Your admin role gives you full system access")
    else:
        print("\n❌ Failed to create admin user. Please check the error messages above.")


if __name__ == "__main__":
    main()
