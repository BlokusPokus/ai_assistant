# Place this in a suitable file, e.g., memory/client.py or a new users.py

from sqlalchemy import select

from ..database.models.users import (
    User,  # adjust import path as needed
)
from ..database.session import AsyncSessionLocal

# WILL NEED TO CHANGE THIS TO PHONE NUMBER


async def get_user_id_by_phone(phone_number: str) -> int | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == 4)
        )
        user = result.scalar_one_or_none()

        return user.id if user else None
