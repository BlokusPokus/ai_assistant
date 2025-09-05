"""
Tests for PhoneManagementService.

This module tests the phone management service functionality including
CRUD operations, verification, and primary phone selection.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.services.phone_management_service import PhoneManagementService
from personal_assistant.communication.twilio_integration.twilio_client import (
    TwilioService,
)
from personal_assistant.sms_router.models.sms_models import UserPhoneMapping
from personal_assistant.sms_router.services.phone_validator import PhoneValidator


class TestPhoneManagementService(unittest.IsolatedAsyncioTestCase):
    """Test cases for PhoneManagementService."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Mock database session
        self.mock_db = Mock(spec=AsyncSession)
        self.mock_db.execute = AsyncMock()
        self.mock_db.add = Mock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.rollback = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        self.mock_db.delete = AsyncMock()  # Make delete async
        self.mock_db.close = AsyncMock()

        # Mock the UserPhoneMapping constructor
        self.mock_mapping_class = Mock()
        self.mock_mapping_class.return_value = Mock(spec=UserPhoneMapping)

        # Configure mock database to handle async operations properly
        self.mock_db.execute.side_effect = None  # Reset side effect
        self.mock_db.commit.side_effect = None  # Reset side effect

        # Ensure all async methods return proper values
        self.mock_db.commit.return_value = None
        self.mock_db.rollback.return_value = None
        self.mock_db.refresh.return_value = None

        # Mock phone validator
        self.mock_phone_validator = Mock(spec=PhoneValidator)
        self.mock_phone_validator.normalize_phone_number = Mock()

        # Mock TwilioService
        self.mock_twilio_service = Mock(spec=TwilioService)
        self.mock_twilio_service.send_verification_sms = AsyncMock()

        # Create service instance with mocked dependencies
        with patch(
            "apps.fastapi_app.services.phone_management_service.PhoneValidator"
        ) as mock_validator_class, patch(
            "apps.fastapi_app.services.phone_management_service.TwilioService"
        ) as mock_twilio_class, patch(
            "apps.fastapi_app.services.phone_management_service.UserPhoneMapping"
        ) as mock_mapping_class:
            mock_validator_class.return_value = self.mock_phone_validator
            mock_twilio_class.return_value = self.mock_twilio_service
            mock_mapping_class.return_value = self.mock_mapping_class.return_value

            self.service = PhoneManagementService(self.mock_db)

    async def test_get_user_phone_numbers_with_primary_and_mappings(self):
        """Test getting user phone numbers with both primary and additional numbers."""
        # Mock primary phone from users table
        primary_phone_result = Mock()
        primary_phone_result.scalar_one_or_none.return_value = "+1234567890"
        self.mock_db.execute.return_value = primary_phone_result

        # Mock additional phone mappings
        mapping1 = Mock(spec=UserPhoneMapping)
        mapping1.id = 1
        mapping1.user_id = 123
        mapping1.phone_number = "+1987654321"
        mapping1.is_primary = False
        mapping1.is_verified = True
        mapping1.verification_method = "sms"
        mapping1.created_at = datetime.now(timezone.utc)
        mapping1.updated_at = None

        mapping2 = Mock(spec=UserPhoneMapping)
        mapping2.id = 2
        mapping2.user_id = 123
        mapping2.phone_number = "+1555123456"
        mapping2.is_primary = True
        mapping2.is_verified = False
        mapping2.verification_method = "manual"
        mapping2.created_at = datetime.now(timezone.utc)
        mapping2.updated_at = None

        mappings_result = Mock()
        mappings_result.scalars.return_value.all.return_value = [mapping1, mapping2]
        self.mock_db.execute.side_effect = [primary_phone_result, mappings_result]

        # Call the method
        result = await self.service.get_user_phone_numbers(123)

        # Verify results
        self.assertEqual(len(result), 3)  # 1 primary + 2 mappings

        # Check primary phone
        primary_phone = result[0]
        # Primary phone from users table has ID 0
        self.assertEqual(primary_phone["id"], 0)
        self.assertEqual(primary_phone["phone_number"], "+1234567890")
        self.assertTrue(primary_phone["is_primary"])
        self.assertTrue(primary_phone["is_verified"])

        # Check first mapping
        first_mapping = result[1]
        self.assertEqual(first_mapping["id"], 1)
        self.assertEqual(first_mapping["phone_number"], "+1987654321")
        self.assertFalse(first_mapping["is_primary"])
        self.assertTrue(first_mapping["is_verified"])

        # Check second mapping
        second_mapping = result[2]
        self.assertEqual(second_mapping["id"], 2)
        self.assertEqual(second_mapping["phone_number"], "+1555123456")
        self.assertTrue(second_mapping["is_primary"])
        self.assertFalse(second_mapping["is_verified"])

    async def test_get_user_phone_numbers_no_primary(self):
        """Test getting user phone numbers with no primary phone."""
        # Mock no primary phone from users table
        primary_phone_result = Mock()
        primary_phone_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = primary_phone_result

        # Mock no additional phone mappings
        mappings_result = Mock()
        mappings_result.scalars.return_value.all.return_value = []
        self.mock_db.execute.side_effect = [primary_phone_result, mappings_result]

        # Call the method
        result = await self.service.get_user_phone_numbers(123)

        # Verify results
        self.assertEqual(len(result), 0)

    async def test_add_user_phone_number_success(self):
        """Test successfully adding a new phone number."""
        # Mock phone validation
        self.mock_phone_validator.normalize_phone_number.return_value = "+1234567890"

        # Mock no existing primary phone
        primary_phone_result = Mock()
        primary_phone_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = primary_phone_result

        # Mock no existing mapping
        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.side_effect = [
            primary_phone_result,
            mapping_result,
            mapping_result,
        ]

        # Mock no other user using this phone
        other_user_result = Mock()
        other_user_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.side_effect = [
            primary_phone_result,
            mapping_result,
            mapping_result,
            other_user_result,
            other_user_result,
        ]

        # Mock the new mapping object
        new_mapping = Mock(spec=UserPhoneMapping)
        new_mapping.id = 1
        new_mapping.user_id = 123
        new_mapping.phone_number = "+1234567890"
        new_mapping.is_primary = False
        new_mapping.is_verified = False
        new_mapping.verification_method = "sms"
        new_mapping.created_at = datetime.now(timezone.utc)
        new_mapping.updated_at = None

        # Call the method
        result = await self.service.add_user_phone_number(
            123, "+1234567890", False, "sms"
        )

        # Verify results
        self.assertIsNotNone(result)
        self.assertEqual(result["phone_number"], "+1234567890")
        self.assertEqual(result["user_id"], 123)
        self.assertFalse(result["is_primary"])
        self.assertFalse(result["is_verified"])
        self.assertEqual(result["verification_method"], "sms")

        # Verify database operations
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()

    async def test_add_user_phone_number_invalid_format(self):
        """Test adding phone number with invalid format."""
        # Mock phone validation failure
        self.mock_phone_validator.normalize_phone_number.return_value = None

        # Call the method
        result = await self.service.add_user_phone_number(123, "invalid", False, "sms")

        # Verify result
        self.assertIsNone(result)

    async def test_add_user_phone_number_already_exists(self):
        """Test adding phone number that already exists for the user."""
        # Mock phone validation
        self.mock_phone_validator.normalize_phone_number.return_value = "+1234567890"

        # Mock existing primary phone
        primary_phone_result = Mock()
        primary_phone_result.scalar_one_or_none.return_value = "+1234567890"
        self.mock_db.execute.return_value = primary_phone_result

        # Call the method
        result = await self.service.add_user_phone_number(
            123, "+1234567890", False, "sms"
        )

        # Verify result
        self.assertIsNone(result)

    async def test_add_user_phone_number_used_by_other_user(self):
        """Test adding phone number that's used by another user."""
        # Mock phone validation
        self.mock_phone_validator.normalize_phone_number.return_value = "+1234567890"

        # Mock no existing primary phone
        primary_phone_result = Mock()
        primary_phone_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = primary_phone_result

        # Mock no existing mapping
        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.side_effect = [
            primary_phone_result,
            mapping_result,
            mapping_result,
        ]

        # Mock other user using this phone
        other_user_result = Mock()
        other_user_result.scalar_one_or_none.return_value = 456  # Other user ID
        self.mock_db.execute.side_effect = [
            primary_phone_result,
            mapping_result,
            mapping_result,
            other_user_result,
            other_user_result,
        ]

        # Call the method
        result = await self.service.add_user_phone_number(
            123, "+1234567890", False, "sms"
        )

        # Verify result
        self.assertIsNone(result)

    async def test_update_user_phone_number_success(self):
        """Test successfully updating a phone number."""
        # Mock existing mapping
        existing_mapping = Mock(spec=UserPhoneMapping)
        existing_mapping.id = 1
        existing_mapping.user_id = 123
        existing_mapping.phone_number = "+1234567890"
        existing_mapping.is_primary = False
        existing_mapping.is_verified = True
        existing_mapping.verification_method = "sms"
        existing_mapping.created_at = datetime.now(timezone.utc)
        existing_mapping.updated_at = None

        # Create updated mapping for after the update
        updated_mapping = Mock(spec=UserPhoneMapping)
        updated_mapping.id = 1
        updated_mapping.user_id = 123
        updated_mapping.phone_number = "+1987654321"
        updated_mapping.is_primary = True
        updated_mapping.is_verified = True
        updated_mapping.verification_method = "sms"
        updated_mapping.created_at = datetime.now(timezone.utc)
        updated_mapping.updated_at = datetime.now(timezone.utc)

        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = existing_mapping
        self.mock_db.execute.return_value = mapping_result

        # Mock refresh to return updated mapping
        self.mock_db.refresh.side_effect = lambda obj: setattr(
            obj, "phone_number", "+1987654321"
        ) or setattr(obj, "is_primary", True)

        # Mock phone validation
        self.mock_phone_validator.normalize_phone_number.return_value = "+1987654321"

        # Call the method
        result = await self.service.update_user_phone_number(
            123, 1, {"phone_number": "+1987654321", "is_primary": True}
        )

        # Verify results
        self.assertIsNotNone(result)
        # The mock object should reflect the updated values after refresh
        self.assertEqual(result["phone_number"], "+1987654321")
        self.assertTrue(result["is_primary"])

        # Verify database operations
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()

    async def test_update_user_phone_number_not_found(self):
        """Test updating phone number that doesn't exist."""
        # Mock no existing mapping
        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mapping_result

        # Call the method
        result = await self.service.update_user_phone_number(
            123, 999, {"phone_number": "+1987654321"}
        )

        # Verify result
        self.assertIsNone(result)

    async def test_delete_user_phone_number_success(self):
        """Test successfully deleting a phone number."""
        # Mock existing mapping
        existing_mapping = Mock(spec=UserPhoneMapping)
        existing_mapping.id = 1
        existing_mapping.user_id = 123
        existing_mapping.phone_number = "+1234567890"

        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = existing_mapping
        self.mock_db.execute.return_value = mapping_result

        # Mock the delete and commit operations to work properly
        self.mock_db.delete.return_value = None
        self.mock_db.commit.return_value = None

        # Call the method
        result = await self.service.delete_user_phone_number(123, 1)

        # Verify result
        self.assertTrue(result)

        # Verify database operations
        self.mock_db.delete.assert_called_once_with(existing_mapping)
        self.mock_db.commit.assert_called_once()

    async def test_delete_user_phone_number_not_found(self):
        """Test deleting phone number that doesn't exist."""
        # Mock no existing mapping
        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mapping_result

        # Call the method
        result = await self.service.delete_user_phone_number(123, 999)

        # Verify result
        self.assertFalse(result)

    async def test_set_primary_phone_number_success(self):
        """Test successfully setting a phone number as primary."""
        # Mock existing mapping
        existing_mapping = Mock(spec=UserPhoneMapping)
        existing_mapping.id = 1
        existing_mapping.user_id = 123
        existing_mapping.phone_number = "+1234567890"

        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = existing_mapping
        self.mock_db.execute.return_value = mapping_result

        # Call the method
        result = await self.service.set_primary_phone_number(123, 1)

        # Verify result
        self.assertTrue(result)

        # Verify database operations
        # 1 for verification, 2 for updates (set others to false, set this to true)
        self.assertEqual(self.mock_db.execute.call_count, 3)
        self.mock_db.commit.assert_called_once()

    async def test_set_primary_phone_number_not_found(self):
        """Test setting primary phone number that doesn't exist."""
        # Mock no existing mapping
        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mapping_result

        # Call the method
        result = await self.service.set_primary_phone_number(123, 999)

        # Verify result
        self.assertFalse(result)

    async def test_send_verification_code_success(self):
        """Test successfully sending verification code."""
        # Mock TwilioService
        self.mock_twilio_service.send_verification_sms.return_value = "SM1234567890"

        # Call the method
        result = await self.service.send_verification_code(123, "+1234567890")

        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 6)  # 6-digit code

        # Verify TwilioService was called
        self.mock_twilio_service.send_verification_sms.assert_called_once_with(
            "+1234567890", result
        )

    async def test_send_verification_code_twilio_error(self):
        """Test sending verification code with Twilio error."""
        # Mock TwilioService error
        self.mock_twilio_service.send_verification_sms.side_effect = Exception(
            "Twilio error"
        )

        # Call the method
        result = await self.service.send_verification_code(123, "+1234567890")

        # Verify result
        self.assertIsNone(result)

    async def test_verify_phone_number_success(self):
        """Test successfully verifying a phone number."""
        # Mock existing mapping
        existing_mapping = Mock(spec=UserPhoneMapping)
        existing_mapping.id = 1
        existing_mapping.user_id = 123
        existing_mapping.phone_number = "+1234567890"

        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = existing_mapping
        self.mock_db.execute.return_value = mapping_result

        # Call the method
        result = await self.service.verify_phone_number(123, "+1234567890", "123456")

        # Verify result
        self.assertTrue(result)

        # Verify database operations
        self.mock_db.commit.assert_called_once()

    async def test_verify_phone_number_not_found(self):
        """Test verifying phone number that doesn't exist."""
        # Mock no existing mapping
        mapping_result = Mock()
        mapping_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mapping_result

        # Call the method
        result = await self.service.verify_phone_number(123, "+1234567890", "123456")

        # Verify result
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
