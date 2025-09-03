"""
User identification service for SMS Router.
"""

import logging
import re
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models.users import User
from ...database.session import AsyncSessionLocal
from ..models.sms_models import UserPhoneMapping
from .cache_manager import CacheManager
from .phone_validator import PhoneValidator

logger = logging.getLogger(__name__)


class UserIdentificationService:
    """Service for identifying users by phone number."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.phone_validator = PhoneValidator()
        self.cache_manager = cache_manager or CacheManager()

    async def identify_user_by_phone(
        self, phone_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Identify user by phone number.

        Args:
            phone_number: Raw phone number from SMS

        Returns:
            User information dict or None if not found
        """
        try:
            # Normalize phone number
            normalized_phone = self.phone_validator.normalize_phone_number(phone_number)
            if not normalized_phone:
                logger.warning(f"Invalid phone number format: {phone_number}")
                return None

            # Check cache first
            cache_key = f"user_phone:{normalized_phone}"
            cached_user = await self.cache_manager.get(cache_key)
            if cached_user:
                logger.info(f"User found in cache for phone: {normalized_phone}")
                return cached_user

            # Database lookup - check users.phone_number (primary)
            user = await self._lookup_user_in_database(normalized_phone)
            if user:
                # Cache the result
                # 1 hour
                await self.cache_manager.set(cache_key, user, ttl=3600)
                logger.info(
                    f"User identified: {user['id']} for phone: {normalized_phone}"
                )
                return user

            logger.warning(f"No user found for phone number: {normalized_phone}")
            return None

        except Exception as e:
            logger.error(f"Error identifying user by phone {phone_number}: {e}")
            return None

    async def _lookup_user_in_database(
        self, phone_number: str
    ) -> Optional[Dict[str, Any]]:
        """Look up user in database by phone number."""
        async with AsyncSessionLocal() as session:
            try:
                # First check users.phone_number (primary)
                result = await session.execute(
                    select(User.id, User.email, User.full_name, User.is_active).where(
                        User.phone_number == phone_number
                    )
                )
                user = result.first()

                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "is_active": user.is_active,
                        "phone_number": phone_number,
                        "source": "primary",
                    }

                # Then check user_phone_mappings (additional numbers)
                result = await session.execute(
                    select(
                        User.id,
                        User.email,
                        User.full_name,
                        User.is_active,
                        UserPhoneMapping.phone_number,
                    )
                    .join(UserPhoneMapping, User.id == UserPhoneMapping.user_id)
                    .where(UserPhoneMapping.phone_number == phone_number)
                )
                user = result.first()

                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "is_active": user.is_active,
                        "phone_number": phone_number,
                        "source": "mapping",
                    }

                return None

            except Exception as e:
                logger.error(f"Database error looking up user by phone: {e}")
                return None

    async def get_user_phone_numbers(self, user_id: int) -> list[str]:
        """
        Get all phone numbers associated with a user.

        Args:
            user_id: User ID to look up

        Returns:
            List of phone numbers
        """
        async with AsyncSessionLocal() as session:
            try:
                # Get primary phone number
                result = await session.execute(
                    select(User.phone_number).where(User.id == user_id)
                )
                primary_phone = result.scalar_one_or_none()

                # Get additional phone numbers
                result = await session.execute(
                    select(UserPhoneMapping.phone_number).where(
                        UserPhoneMapping.user_id == user_id
                    )
                )
                additional_phones = [row[0] for row in result.fetchall()]

                # Combine and filter out None values
                all_phones = []
                if primary_phone:
                    all_phones.append(primary_phone)
                all_phones.extend(additional_phones)

                return all_phones

            except Exception as e:
                logger.error(f"Error getting phone numbers for user {user_id}: {e}")
                return []

    async def add_phone_mapping(
        self,
        user_id: int,
        phone_number: str,
        is_primary: bool = False,
        verification_method: str = "manual",
    ) -> bool:
        """
        Add a phone number mapping for a user.

        Args:
            user_id: User ID
            phone_number: Phone number to add
            is_primary: Whether this is the primary number
            verification_method: How the number was verified

        Returns:
            True if successful, False otherwise
        """
        try:
            normalized_phone = self.phone_validator.normalize_phone_number(phone_number)
            if not normalized_phone:
                logger.error(f"Invalid phone number: {phone_number}")
                return False

            async with AsyncSessionLocal() as session:
                # Check if phone number already exists
                existing = await session.execute(
                    select(UserPhoneMapping).where(
                        UserPhoneMapping.phone_number == normalized_phone
                    )
                )

                if existing.scalar_one_or_none():
                    logger.warning(
                        f"Phone number {normalized_phone} already mapped to another user"
                    )
                    return False

                # Create new mapping
                new_mapping = UserPhoneMapping(
                    user_id=user_id,
                    phone_number=normalized_phone,
                    is_primary=is_primary,
                    is_verified=True,
                    verification_method=verification_method,
                )

                session.add(new_mapping)
                await session.commit()

                # Clear cache for this phone number
                cache_key = f"user_phone:{normalized_phone}"
                await self.cache_manager.delete(cache_key)

                logger.info(
                    f"Added phone mapping for user {user_id}: {normalized_phone}"
                )
                return True

        except Exception as e:
            logger.error(f"Error adding phone mapping for user {user_id}: {e}")
            return False
