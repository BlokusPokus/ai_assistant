#!/usr/bin/env python3
"""
Script to create an admin user with phone number authentication.

This script will:
1. Add a phone_number field to the users table if it doesn't exist
2. Create an admin user with your phone number
3. Assign the administrator role to the user
4. Set up the necessary RBAC permissions

Usage:
    python create_admin_user.py --phone "+1234567890" --email "your@email.com" --name "Your Name" --password "SecurePass123!"
"""

from sqlalchemy import select, text
from personal_assistant.auth.password_service import PasswordService
from personal_assistant.database.models.rbac_models import Role, UserRole, Permission, RolePermission
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal
import asyncio
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def create_admin_user(phone_number: str, email: str, full_name: str, password: str):
    """Create an admin user with the specified credentials."""

    try:
        async with await AsyncSessionLocal() as session:
            print(
                f"🔍 Checking if user with phone {phone_number} already exists...")

            # Check if user already exists by phone number
            result = await session.execute(
                select(User).where(User.phone_number == phone_number)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(
                    f"❌ User with phone number {phone_number} already exists")
                return False

            # Check if user already exists by email
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"❌ User with email {email} already exists")
                return False

            print("✅ No existing user found, proceeding with creation...")

            # Hash password
            password_service = PasswordService()
            hashed_password = password_service.hash_password(password)

            # Create admin user
            admin_user = User(
                email=email,
                phone_number=phone_number,
                full_name=full_name,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            print(f"✅ Admin user created with ID: {admin_user.id}")

            # Get or create admin role
            result = await session.execute(
                select(Role).where(Role.name == 'administrator')
            )
            admin_role = result.scalar_one_or_none()

            if not admin_role:
                print("🔧 Creating administrator role...")
                admin_role = Role(
                    name='administrator',
                    description='System administrator with full access',
                    created_at=datetime.utcnow()
                )
                session.add(admin_role)
                await session.commit()
                await session.refresh(admin_role)
                print(f"✅ Administrator role created with ID: {admin_role.id}")
            else:
                print(f"✅ Administrator role found with ID: {admin_role.id}")

            # Assign admin role to user
            user_role = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                is_primary=True,
                granted_at=datetime.utcnow()
            )

            session.add(user_role)
            await session.commit()

            print("✅ Admin role assigned to user")

            # Create basic permissions if they don't exist
            await create_basic_permissions(session, admin_role)

            print("\n🎉 Admin user created successfully!")
            print(f"   ID: {admin_user.id}")
            print(f"   Name: {admin_user.full_name}")
            print(f"   Email: {admin_user.email}")
            print(f"   Phone: {admin_user.phone_number}")
            print(f"   Role: {admin_role.name}")
            print(f"   Status: Active and Verified")

            return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False


async def create_basic_permissions(session, admin_role):
    """Create basic permissions and assign them to the admin role."""

    try:
        # Define basic permissions
        basic_permissions = [
            ('user:read', 'user', 'read', 'Read user profiles'),
            ('user:write', 'user', 'write', 'Write user profiles'),
            ('user:delete', 'user', 'delete', 'Delete users'),
            ('memory:read', 'memory', 'read', 'Read user memories'),
            ('memory:write', 'memory', 'write', 'Write user memories'),
            ('memory:delete', 'memory', 'delete', 'Delete memories'),
            ('system:admin', 'system', 'admin', 'System administration'),
        ]

        for perm_name, resource_type, action, description in basic_permissions:
            # Check if permission exists
            result = await session.execute(
                select(Permission).where(Permission.name == perm_name)
            )
            permission = result.scalar_one_or_none()

            if not permission:
                print(f"🔧 Creating permission: {perm_name}")
                permission = Permission(
                    name=perm_name,
                    resource_type=resource_type,
                    action=action,
                    description=description,
                    created_at=datetime.utcnow()
                )
                session.add(permission)
                await session.commit()
                await session.refresh(permission)
                print(f"✅ Permission {perm_name} created")

            # Check if role-permission relationship exists
            result = await session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == permission.id
                )
            )
            role_permission = result.scalar_one_or_none()

            if not role_permission:
                print(f"🔧 Assigning permission {perm_name} to admin role...")
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    created_at=datetime.utcnow()
                )
                session.add(role_permission)
                await session.commit()
                print(f"✅ Permission {perm_name} assigned to admin role")

        print("✅ Basic permissions created and assigned")

    except Exception as e:
        print(f"⚠️ Warning: Could not create basic permissions: {e}")


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

    print("🚀 Personal Assistant - Admin User Creation")
    print("=" * 50)

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

    # Check database connection
    if not asyncio.run(check_database_connection()):
        print("❌ Cannot proceed without database connection")
        return

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
