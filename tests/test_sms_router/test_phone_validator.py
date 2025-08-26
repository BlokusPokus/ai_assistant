"""
Unit tests for PhoneValidator service.
"""

import pytest
from personal_assistant.sms_router.services.phone_validator import PhoneValidator


class TestPhoneValidator:
    """Test cases for PhoneValidator service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PhoneValidator()

    def test_normalize_phone_number_valid_us(self):
        """Test normalization of valid US phone numbers."""
        test_cases = [
            ("+1-555-123-4567", "+15551234567"),
            ("(555) 123-4567", "+15551234567"),
            ("555.123.4567", "+15551234567"),
            ("555 123 4567", "+15551234567"),
            ("+15551234567", "+15551234567"),
            ("15551234567", "+15551234567"),
            ("5551234567", "+15551234567"),
        ]
        
        for input_phone, expected in test_cases:
            result = self.validator.normalize_phone_number(input_phone)
            assert result == expected, f"Failed for input: {input_phone}"

    def test_normalize_phone_number_invalid(self):
        """Test normalization of invalid phone numbers."""
        invalid_numbers = [
            "",  # Empty string
            None,  # None
            "123",  # Too short
            "abc",  # Non-numeric
            "+1234567890123456",  # Too long
            "555-123",  # Incomplete
        ]
        
        for invalid_phone in invalid_numbers:
            result = self.validator.normalize_phone_number(invalid_phone)
            assert result is None, f"Should return None for: {invalid_phone}"

    def test_is_valid_phone_number(self):
        """Test phone number validation."""
        valid_numbers = [
            "+15551234567",
            "+44 20 7946 0958",
            "+81 3-1234-5678",
        ]
        
        invalid_numbers = [
            "123",
            "abc",
            "+1234567890123456",
            "",
            None,
        ]
        
        for valid_phone in valid_numbers:
            assert self.validator.is_valid_phone_number(valid_phone), f"Should be valid: {valid_phone}"
            
        for invalid_phone in invalid_numbers:
            assert not self.validator.is_valid_phone_number(invalid_phone), f"Should be invalid: {invalid_phone}"

    def test_format_phone_number(self):
        """Test phone number formatting."""
        # Test E.164 format (default)
        result = self.validator.format_phone_number("555-123-4567")
        assert result == "+15551234567"
        
        # Test national format
        result = self.validator.format_phone_number("555-123-4567", "national")
        assert result == "(555) 123-4567"
        
        # Test international format
        result = self.validator.format_phone_number("555-123-4567", "international")
        assert result == "+15551234567"
        
        # Test invalid number
        result = self.validator.format_phone_number("invalid")
        assert result is None

    def test_international_numbers(self):
        """Test international phone number handling."""
        international_numbers = [
            ("+44 20 7946 0958", "+442079460958"),  # UK
            ("+81 3-1234-5678", "+81312345678"),   # Japan
            ("+49 30 12345678", "+493012345678"),  # Germany
            ("+33 1 42 86 53 00", "+33142865300"), # France
        ]
        
        for input_phone, expected in international_numbers:
            result = self.validator.normalize_phone_number(input_phone)
            assert result == expected, f"Failed for international number: {input_phone}"

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with spaces and special characters
        result = self.validator.normalize_phone_number("  +1  (555)  123  -  4567  ")
        assert result == "+15551234567"
        
        # Test with leading zeros
        result = self.validator.normalize_phone_number("+1-0555-123-4567")
        assert result == "+105551234567"
        
        # Test with multiple plus signs (should handle gracefully)
        result = self.validator.normalize_phone_number("++1-555-123-4567")
        assert result == "+15551234567"
