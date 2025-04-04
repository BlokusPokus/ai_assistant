# test_add_user.py
import asyncio
from datetime import datetime
import uuid
from session import AsyncSessionLocal
from models.users import User
from sqlalchemy import select


async def main():
    # Generate a unique email using UUID
    unique_email = f"test_{uuid.uuid4()}@example.com"

    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                # Create a new user with unique email
                new_user = User(
                    email=unique_email,
                    full_name="Test User",
                    created_at=datetime.utcnow()
                )

                session.add(new_user)
                await session.flush()  # Ensure the user is added before querying

                print(f"User added successfully with email: {unique_email}")

                # Query to verify the user was added
                query = select(User).where(User.email == unique_email)
                result = await session.execute(query)
                user = result.scalar_one()

                print("\nVerifying user in database:")
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Full Name: {user.full_name}")
                print(f"Created At: {user.created_at}")

            except Exception as e:
                print(f"Error adding user: {str(e)}")
                raise

if __name__ == "__main__":
    asyncio.run(main())
