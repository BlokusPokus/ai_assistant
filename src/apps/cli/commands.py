import asyncio
import os
import sys
from datetime import datetime

import click

from personal_assistant.auth.password_service import PasswordService
from personal_assistant.config.settings import settings
from personal_assistant.core.agent import AgentCore
from personal_assistant.database.models.rbac_models import Role, UserRole
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


@click.group()
def cli():
    """Personal Assistant CLI"""


@cli.command()
def status():
    """Check system status"""
    click.echo("Personal Assistant Status:")
    click.echo(f"Environment: {settings.ENVIRONMENT}")
    click.echo(f"Debug: {settings.DEBUG}")
    click.echo(f"Log Level: {settings.LOG_LEVEL}")


@cli.command()
@click.argument("message")
def process(message):
    """Process a message through the assistant"""
    agent = AgentCore()
    response = agent.process_message(message)
    click.echo(f"Response: {response}")


@cli.command()
@click.option("--phone", "-p", required=True, help="Phone number for the admin user")
@click.option("--email", "-e", required=True, help="Email for the admin user")
@click.option("--name", "-n", required=True, help="Full name for the admin user")
@click.option("--password", "-pw", required=True, help="Password for the admin user")
def create_admin(phone, email, name, password):
    """Create an admin user with phone number authentication"""

    async def _create_admin():
        try:
            async with AsyncSessionLocal() as session:
                # Check if user already exists
                from sqlalchemy import select

                # Check by phone number
                result = await session.execute(
                    select(User).where(User.phone_number == phone)
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    click.echo(f"❌ User with phone number {phone} already exists")
                    return

                # Check by email
                result = await session.execute(select(User).where(User.email == email))
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    click.echo(f"❌ User with email {email} already exists")
                    return

                # Hash password
                password_service = PasswordService()
                hashed_password = password_service.hash_password(password)

                # Create admin user
                admin_user = User(
                    email=email,
                    phone_number=phone,
                    full_name=name,
                    hashed_password=hashed_password,
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                session.add(admin_user)
                await session.commit()
                await session.refresh(admin_user)

                # Get or create admin role
                result = await session.execute(
                    select(Role).where(Role.name == "administrator")
                )
                admin_role = result.scalar_one_or_none()

                if not admin_role:
                    # Create admin role if it doesn't exist
                    admin_role = Role(
                        name="administrator",
                        description="System administrator with full access",
                        created_at=datetime.utcnow(),
                    )
                    session.add(admin_role)
                    await session.commit()
                    await session.refresh(admin_role)

                # Assign admin role to user
                user_role = UserRole(
                    user_id=admin_user.id,
                    role_id=admin_role.id,
                    is_primary=True,
                    granted_at=datetime.utcnow(),
                )

                session.add(user_role)
                await session.commit()

                click.echo(f"✅ Admin user created successfully!")
                click.echo(f"   ID: {admin_user.id}")
                click.echo(f"   Name: {admin_user.full_name}")
                click.echo(f"   Email: {admin_user.email}")
                click.echo(f"   Phone: {admin_user.phone_number}")
                click.echo(f"   Role: {admin_role.name}")

        except Exception as e:
            click.echo(f"❌ Error creating admin user: {e}")
            import traceback

            traceback.print_exc()

    # Run the async function
    asyncio.run(_create_admin())


if __name__ == "__main__":
    cli()
