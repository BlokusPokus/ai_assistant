"""
Phone management service for user phone number operations.

This service provides business logic for managing user phone numbers including
CRUD operations, verification, and primary phone selection.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.exc import IntegrityError

from personal_assistant.database.models.users import User
from personal_assistant.sms_router.models.sms_models import UserPhoneMapping
from personal_assistant.sms_router.services.phone_validator import PhoneValidator
from personal_assistant.communication.twilio_integration.twilio_client import TwilioService
from personal_assistant.core import AgentCore

logger = logging.getLogger(__name__)


class PhoneManagementService:
    """Service class for phone number management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.phone_validator = PhoneValidator()
        # Initialize TwilioService for verification SMS
        self.twilio_service = TwilioService(agent_core=None)  # We don't need AgentCore for this service

    async def get_user_phone_numbers(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all phone numbers associated with a user.

        Args:
            user_id: User ID to retrieve phone numbers for

        Returns:
            List of phone number dictionaries
        """
        try:
            # Get primary phone number from users table
            user_result = await self.db.execute(
                select(User.phone_number)
                .where(User.id == user_id)
            )
            primary_phone = user_result.scalar_one_or_none()

            # Get additional phone numbers from user_phone_mappings
            mappings_result = await self.db.execute(
                select(UserPhoneMapping)
                .where(UserPhoneMapping.user_id == user_id)
                .order_by(UserPhoneMapping.is_primary.desc(), UserPhoneMapping.created_at)
            )
            mappings = mappings_result.scalars().all()

            phone_numbers = []

            # Add primary phone from users table if exists
            if primary_phone:
                phone_numbers.append({
                    'id': 'primary',
                    'user_id': user_id,
                    'phone_number': primary_phone,
                    'is_primary': True,
                    'is_verified': True,
                    'verification_method': 'primary',
                    'created_at': datetime.now(timezone.utc),
                    'updated_at': None
                })

            # Add additional phone numbers
            for mapping in mappings:
                phone_numbers.append({
                    'id': mapping.id,
                    'user_id': mapping.user_id,
                    'phone_number': mapping.phone_number,
                    'is_primary': mapping.is_primary,
                    'is_verified': mapping.is_verified,
                    'verification_method': mapping.verification_method,
                    'created_at': mapping.created_at,
                    'updated_at': mapping.updated_at
                })

            return phone_numbers

        except Exception as e:
            logger.error(f"Error getting phone numbers for user {user_id}: {e}")
            return []

    async def add_user_phone_number(
        self, 
        user_id: int, 
        phone_number: str, 
        is_primary: bool = False,
        verification_method: str = 'sms'
    ) -> Optional[Dict[str, Any]]:
        """
        Add a new phone number for a user.

        Args:
            user_id: User ID to add phone number for
            phone_number: Phone number to add
            is_primary: Whether this should be the primary number
            verification_method: Method of verification

        Returns:
            Phone number mapping dict if successful, None otherwise
        """
        try:
            # Validate phone number format
            normalized_phone = self.phone_validator.normalize_phone_number(phone_number)
            if not normalized_phone:
                logger.error(f"Invalid phone number format: {phone_number}")
                return None

            # Check if phone number already exists for this user
            existing_primary = await self.db.execute(
                select(User.phone_number)
                .where(User.id == user_id)
            )
            existing_primary = existing_primary.scalar_one_or_none()

            existing_mapping = await self.db.execute(
                select(UserPhoneMapping)
                .where(
                    and_(
                        UserPhoneMapping.user_id == user_id,
                        UserPhoneMapping.phone_number == normalized_phone
                    )
                )
            )
            existing_mapping = existing_mapping.scalar_one_or_none()

            if existing_primary == normalized_phone or existing_mapping:
                logger.warning(f"Phone number {normalized_phone} already exists for user {user_id}")
                return None

            # Check if phone number is used by another user
            other_user_primary = await self.db.execute(
                select(User.id)
                .where(User.phone_number == normalized_phone)
            )
            other_user_primary = other_user_primary.scalar_one_or_none()

            other_user_mapping = await self.db.execute(
                select(UserPhoneMapping.user_id)
                .where(UserPhoneMapping.phone_number == normalized_phone)
            )
            other_user_mapping = other_user_mapping.scalar_one_or_none()

            if other_user_primary or other_user_mapping:
                logger.warning(f"Phone number {normalized_phone} already used by another user")
                return None

            # Create new phone mapping
            new_mapping = UserPhoneMapping(
                user_id=user_id,
                phone_number=normalized_phone,
                is_primary=is_primary,
                is_verified=False,
                verification_method=verification_method
            )

            self.db.add(new_mapping)
            await self.db.commit()
            await self.db.refresh(new_mapping)

            logger.info(f"Added phone number {normalized_phone} for user {user_id}")

            return {
                'id': new_mapping.id,
                'user_id': new_mapping.user_id,
                'phone_number': new_mapping.phone_number,
                'is_primary': new_mapping.is_primary,
                'is_verified': new_mapping.is_verified,
                'verification_method': new_mapping.verification_method,
                'created_at': new_mapping.created_at,
                'updated_at': new_mapping.updated_at
            }

        except IntegrityError as e:
            logger.error(f"Integrity error adding phone number for user {user_id}: {e}")
            await self.db.rollback()
            return None
        except Exception as e:
            logger.error(f"Error adding phone number for user {user_id}: {e}")
            await self.db.rollback()
            return None

    async def update_user_phone_number(
        self, 
        user_id: int, 
        phone_id: int, 
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a user's phone number.

        Args:
            user_id: User ID
            phone_id: Phone number mapping ID
            updates: Dictionary of fields to update

        Returns:
            Updated phone number mapping dict if successful, None otherwise
        """
        try:
            # Verify the phone number belongs to the user
            mapping_result = await self.db.execute(
                select(UserPhoneMapping)
                .where(
                    and_(
                        UserPhoneMapping.id == phone_id,
                        UserPhoneMapping.user_id == user_id
                    )
                )
            )
            mapping = mapping_result.scalar_one_or_none()

            if not mapping:
                logger.warning(f"Phone mapping {phone_id} not found for user {user_id}")
                return None

            # Update fields
            update_data = {}
            if 'phone_number' in updates:
                normalized_phone = self.phone_validator.normalize_phone_number(updates['phone_number'])
                if not normalized_phone:
                    logger.error(f"Invalid phone number format: {updates['phone_number']}")
                    return None
                update_data['phone_number'] = normalized_phone

            if 'is_primary' in updates:
                update_data['is_primary'] = updates['is_primary']

            if not update_data:
                logger.warning("No valid updates provided")
                return mapping

            # Update the mapping
            await self.db.execute(
                update(UserPhoneMapping)
                .where(UserPhoneMapping.id == phone_id)
                .values(**update_data, updated_at=datetime.now(timezone.utc))
            )

            await self.db.commit()

            # Refresh the mapping
            await self.db.refresh(mapping)

            logger.info(f"Updated phone mapping {phone_id} for user {user_id}")

            return {
                'id': mapping.id,
                'user_id': mapping.user_id,
                'phone_number': mapping.phone_number,
                'is_primary': mapping.is_primary,
                'is_verified': mapping.is_verified,
                'verification_method': mapping.verification_method,
                'created_at': mapping.created_at,
                'updated_at': mapping.updated_at
            }

        except Exception as e:
            logger.error(f"Error updating phone mapping {phone_id} for user {user_id}: {e}")
            await self.db.rollback()
            return None

    async def delete_user_phone_number(self, user_id: int, phone_id: int) -> bool:
        """
        Delete a user's phone number.

        Args:
            user_id: User ID
            phone_id: Phone number mapping ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify the phone number belongs to the user
            mapping_result = await self.db.execute(
                select(UserPhoneMapping)
                .where(
                    and_(
                        UserPhoneMapping.id == phone_id,
                        UserPhoneMapping.user_id == user_id
                    )
                )
            )
            mapping = mapping_result.scalar_one_or_none()

            if not mapping:
                logger.warning(f"Phone mapping {phone_id} not found for user {user_id}")
                return False

            # Delete the mapping
            await self.db.delete(mapping)
            await self.db.commit()

            logger.info(f"Deleted phone mapping {phone_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting phone mapping {phone_id} for user {user_id}: {e}")
            await self.db.rollback()
            return False

    async def set_primary_phone_number(self, user_id: int, phone_id: int) -> bool:
        """
        Set a phone number as the primary for a user.

        Args:
            user_id: User ID
            phone_id: Phone number mapping ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify the phone number belongs to the user
            mapping_result = await self.db.execute(
                select(UserPhoneMapping)
                .where(
                    and_(
                        UserPhoneMapping.id == phone_id,
                        UserPhoneMapping.user_id == user_id
                    )
                )
            )
            mapping = mapping_result.scalar_one_or_none()

            if not mapping:
                logger.warning(f"Phone mapping {phone_id} not found for user {user_id}")
                return False

            # Set all other mappings to non-primary
            await self.db.execute(
                update(UserPhoneMapping)
                .where(
                    and_(
                        UserPhoneMapping.user_id == user_id,
                        UserPhoneMapping.id != phone_id
                    )
                )
                .values(is_primary=False, updated_at=datetime.now(timezone.utc))
            )

            # Set this mapping as primary
            await self.db.execute(
                update(UserPhoneMapping)
                .where(UserPhoneMapping.id == phone_id)
                .values(is_primary=True, updated_at=datetime.now(timezone.utc))
            )

            await self.db.commit()

            logger.info(f"Set phone mapping {phone_id} as primary for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error setting primary phone for user {user_id}: {e}")
            await self.db.rollback()
            return False

    async def send_verification_code(self, user_id: int, phone_number: str) -> Optional[str]:
        """
        Send verification code to a phone number.

        Args:
            user_id: User ID
            phone_number: Phone number to send verification to

        Returns:
            Verification code if successful, None otherwise
        """
        try:
            # Generate 6-digit verification code
            verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))

            # Store verification code (in a real implementation, this would go to a separate table)
            # For now, we'll just log it
            logger.info(f"Generated verification code {verification_code} for user {user_id}")

            # Send verification SMS
            await self.twilio_service.send_verification_sms(phone_number, verification_code)

            logger.info(f"Sent verification code to {phone_number} for user {user_id}")
            return verification_code

        except Exception as e:
            logger.error(f"Error sending verification code to {phone_number} for user {user_id}: {e}")
            return None

    async def verify_phone_number(
        self, 
        user_id: int, 
        phone_number: str, 
        verification_code: str
    ) -> bool:
        """
        Verify a phone number with the provided code.

        Args:
            user_id: User ID
            phone_number: Phone number to verify
            verification_code: Verification code to check

        Returns:
            True if verification successful, False otherwise
        """
        try:
            # In a real implementation, this would check against stored verification codes
            # For now, we'll just mark the phone number as verified
            mapping_result = await self.db.execute(
                select(UserPhoneMapping)
                .where(
                    and_(
                        UserPhoneMapping.user_id == user_id,
                        UserPhoneMapping.phone_number == phone_number
                    )
                )
            )
            mapping = mapping_result.scalar_one_or_none()

            if not mapping:
                logger.warning(f"Phone mapping not found for user {user_id} and phone {phone_number}")
                return False

            # Mark as verified
            await self.db.execute(
                update(UserPhoneMapping)
                .where(UserPhoneMapping.id == mapping.id)
                .values(is_verified=True, updated_at=datetime.now(timezone.utc))
            )

            await self.db.commit()

            logger.info(f"Verified phone number {phone_number} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error verifying phone number {phone_number} for user {user_id}: {e}")
            await self.db.rollback()
            return False
