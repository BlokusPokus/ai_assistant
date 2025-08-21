# Place this in a suitable file, e.g., memory/client.py or a new users.py

from sqlalchemy import select

from ..database.models.users import (
    User,  # adjust import path as needed
)
from ..database.session import AsyncSessionLocal


async def get_user_id_by_phone(phone_number: str) -> int | None:
    """Get user ID by phone number."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id).where(User.phone_number == phone_number)
        )
        user_id = result.scalar_one_or_none()

        return user_id
