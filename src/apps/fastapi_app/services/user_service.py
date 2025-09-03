"""
User service layer for business logic operations.

This module provides business logic for user management operations
including CRUD operations, preferences management, and data validation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.auth.password_service import password_service
from personal_assistant.database.models.user_settings import UserSetting
from personal_assistant.database.models.users import User

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _mask_phone_number(self, phone_number: str) -> str:
        """Mask phone number for logging purposes."""
        if not phone_number or len(phone_number) < 4:
            return "***"
        return phone_number[:2] + "*" * (len(phone_number) - 4) + phone_number[-2:]

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID to retrieve

        Returns:
            User object if found, None otherwise
        """
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email to retrieve

        Returns:
            User object if found, None otherwise
        """
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
            return None

    async def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """
        Get user by phone number.

        Args:
            phone_number: User phone number to retrieve

        Returns:
            User object if found, None otherwise
        """
        try:
            result = await self.db.execute(
                select(User).where(User.phone_number == phone_number)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Error retrieving user by phone number {self._mask_phone_number(phone_number)}: {e}"
            )
            return None

    async def list_users(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[List[User], int]:
        """
        List users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            Tuple of (users list, total count)
        """
        try:
            # Get total count
            count_result = await self.db.execute(select(func.count(User.id)))
            total = count_result.scalar()

            # Get users with pagination
            result = await self.db.execute(
                select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
            )
            users = result.scalars().all()

            return list(users), total
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return [], 0

    async def update_user(
        self, user_id: int, user_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Update user profile.

        Args:
            user_id: User ID to update
            user_id: Dictionary of fields to update

        Returns:
            Updated user object if successful, None otherwise
        """
        try:
            # Remove None values and prepare update data
            update_data = {k: v for k, v in user_data.items() if v is not None}

            if not update_data:
                logger.warning(f"No valid data provided for user {user_id} update")
                return await self.get_user_by_id(user_id)

            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()

            # Update user
            await self.db.execute(
                update(User).where(User.id == user_id).values(**update_data)
            )
            await self.db.commit()

            # Return updated user
            return await self.get_user_by_id(user_id)
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error updating user {user_id}: {e}")
            raise ValueError("Update failed due to data integrity constraints")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            return None

    async def deactivate_user(self, user_id: int, reason: Optional[str] = None) -> bool:
        """
        Deactivate a user account.

        Args:
            user_id: User ID to deactivate
            reason: Optional reason for deactivation

        Returns:
            True if successful, False otherwise
        """
        try:
            update_data = {"is_active": False, "updated_at": datetime.utcnow()}

            await self.db.execute(
                update(User).where(User.id == user_id).values(**update_data)
            )
            await self.db.commit()

            logger.info(
                f"User {user_id} deactivated. Reason: {reason or 'No reason provided'}"
            )
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False

    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Get user preferences from user settings.

        Args:
            user_id: User ID to get preferences for

        Returns:
            Dictionary of user preferences
        """
        try:
            result = await self.db.execute(
                select(UserSetting).where(
                    UserSetting.user_id == user_id,
                    UserSetting.category == "preferences",
                )
            )
            settings = result.scalars().all()

            preferences = {}
            for setting in settings:
                preferences[setting.key] = setting.value

            return preferences
        except Exception as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {e}")
            return {}

    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """
        Get user settings from user settings.

        Args:
            user_id: User ID to get settings for

        Returns:
            Dictionary of user settings
        """
        try:
            result = await self.db.execute(
                select(UserSetting).where(
                    UserSetting.user_id == user_id, UserSetting.category == "settings"
                )
            )
            settings = result.scalars().all()

            user_settings = {}
            for setting in settings:
                user_settings[setting.key] = setting.value

            return user_settings
        except Exception as e:
            logger.error(f"Error retrieving settings for user {user_id}: {e}")
            return {}

    async def update_user_preferences(
        self, user_id: int, preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user preferences.

        Args:
            user_id: User ID to update preferences for
            preferences: Dictionary of preferences to update

        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in preferences.items():
                # Check if setting exists
                existing_setting = await self.db.execute(
                    select(UserSetting).where(
                        UserSetting.user_id == user_id,
                        UserSetting.key == key,
                        UserSetting.category == "preferences",
                    )
                )
                existing_setting = existing_setting.scalar_one_or_none()

                if existing_setting:
                    # Update existing setting
                    await self.db.execute(
                        update(UserSetting)
                        .where(
                            UserSetting.user_id == user_id,
                            UserSetting.key == key,
                            UserSetting.category == "preferences",
                        )
                        .values(value=str(value), updated_at=datetime.utcnow())
                    )
                else:
                    # Create new setting
                    new_setting = UserSetting(
                        user_id=user_id,
                        key=key,
                        value=str(value),
                        category="preferences",
                        setting_type="string",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    self.db.add(new_setting)

            await self.db.commit()
            logger.info(f"Updated preferences for user {user_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False

    async def update_user_settings(
        self, user_id: int, settings: Dict[str, Any]
    ) -> bool:
        """
        Update user settings.

        Args:
            user_id: User ID to update settings for
            settings: Dictionary of settings to update

        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in settings.items():
                # Check if setting exists
                existing_setting = await self.db.execute(
                    select(UserSetting).where(
                        UserSetting.user_id == user_id,
                        UserSetting.key == key,
                        UserSetting.category == "settings",
                    )
                )
                existing_setting = existing_setting.scalar_one_or_none()

                if existing_setting:
                    # Update existing setting
                    await self.db.execute(
                        update(UserSetting)
                        .where(
                            UserSetting.user_id == user_id,
                            UserSetting.key == key,
                            UserSetting.category == "settings",
                        )
                        .values(value=str(value), updated_at=datetime.utcnow())
                    )
                else:
                    # Create new setting
                    new_setting = UserSetting(
                        user_id=user_id,
                        key=key,
                        value=str(value),
                        category="settings",
                        setting_type="string",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    self.db.add(new_setting)

            await self.db.commit()
            logger.info(f"Updated settings for user {user_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating settings for user {user_id}: {e}")
            return False

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Create a new user (admin only).

        Args:
            user_data: User data including email, full_name, password

        Returns:
            Created user object if successful, None otherwise
        """
        try:
            # Hash password
            hashed_password = password_service.hash_password(user_data["password"])

            # Create user object
            new_user = User(
                email=user_data["email"],
                phone_number=user_data.get("phone_number"),
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                is_active=user_data.get("is_active", True),
                is_verified=user_data.get("is_verified", False),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            logger.info(f"Created new user: {new_user.email}")
            return new_user
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error creating user: {e}")
            if "email" in str(e).lower():
                raise ValueError("User with this email already exists")
            if "phone_number" in str(e).lower():
                raise ValueError("User with this phone number already exists")
            raise ValueError("Failed to create user due to data constraints")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {e}")
            return None

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user statistics and metadata.

        Args:
            user_id: User ID to get stats for

        Returns:
            Dictionary of user statistics
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return {}

            # Get preferences and settings counts
            prefs_result = await self.db.execute(
                select(func.count(UserSetting.id)).where(
                    UserSetting.user_id == user_id,
                    UserSetting.category == "preferences",
                )
            )
            prefs_count = prefs_result.scalar() or 0

            settings_result = await self.db.execute(
                select(func.count(UserSetting.id)).where(
                    UserSetting.user_id == user_id, UserSetting.category == "settings"
                )
            )
            settings_count = settings_result.scalar() or 0

            return {
                "user_id": user_id,
                "preferences_count": prefs_count,
                "settings_count": settings_count,
                "account_age_days": (datetime.utcnow() - user.created_at).days,
                "last_activity": user.last_login or user.updated_at,
            }
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return {}
