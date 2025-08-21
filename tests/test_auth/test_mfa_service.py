"""
Unit tests for MFA Service.

Tests the TOTP-based Multi-Factor Authentication service including:
- TOTP secret generation
- QR code generation
- TOTP validation
- Backup codes
- Device trust management
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import pyotp

from personal_assistant.auth.mfa_service import MFAService


class TestMFAService:
    """Test cases for MFAService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mfa_service = MFAService()
        self.test_user_id = "user123"
        self.test_email = "test@example.com"

    def test_generate_totp_secret(self):
        """Test TOTP secret generation."""
        secret = self.mfa_service.generate_totp_secret(self.test_user_id)

        # Check secret format and length
        assert len(secret) == 32
        assert secret.isalnum()
        assert secret.isupper()

        # Check it's different each time
        secret2 = self.mfa_service.generate_totp_secret(self.test_user_id)
        assert secret != secret2

    def test_generate_qr_code(self):
        """Test QR code generation."""
        secret = self.mfa_service.generate_totp_secret(self.test_user_id)
        qr_code = self.mfa_service.generate_qr_code(secret, self.test_email)

        # Check QR code format
        assert qr_code.startswith("data:image/png;base64,")
        assert len(qr_code) > 100  # Base64 encoded PNG should be substantial

        # Verify the QR code was generated (we can't easily decode it in tests)
        # The important thing is that it generates a valid base64 PNG image
        assert len(qr_code) > 200  # Base64 PNG should be substantial

        # Test that the secret works with pyotp
        totp = pyotp.TOTP(secret)
        current_token = totp.now()
        assert len(current_token) == 6  # TOTP tokens are 6 digits

    def test_verify_totp_valid(self):
        """Test TOTP validation with valid token."""
        secret = self.mfa_service.generate_totp_secret(self.test_user_id)

        # Generate current TOTP
        totp = pyotp.TOTP(secret)
        current_token = totp.now()

        # Verify token
        result = self.mfa_service.verify_totp(secret, current_token)
        assert result is True

    def test_verify_totp_invalid(self):
        """Test TOTP validation with invalid token."""
        secret = self.mfa_service.generate_totp_secret(self.test_user_id)

        # Test with invalid token
        result = self.mfa_service.verify_totp(secret, "000000")
        assert result is False

    def test_verify_totp_with_window(self):
        """Test TOTP validation with custom window."""
        secret = self.mfa_service.generate_totp_secret(self.test_user_id)

        # Generate current TOTP
        totp = pyotp.TOTP(secret)
        current_token = totp.now()

        # Verify with custom window
        result = self.mfa_service.verify_totp(secret, current_token, window=2)
        assert result is True

    def test_generate_backup_codes(self):
        """Test backup codes generation."""
        codes = self.mfa_service.generate_backup_codes()

        # Check number of codes
        assert len(codes) == self.mfa_service.backup_codes_count

        # Check each code format
        for code in codes:
            assert len(code) == 8
            assert code.isalnum()
            assert code.isupper()

        # Check codes are unique
        assert len(set(codes)) == len(codes)

    def test_generate_backup_codes_custom_count(self):
        """Test backup codes generation with custom count."""
        custom_count = 5
        codes = self.mfa_service.generate_backup_codes(custom_count)

        assert len(codes) == custom_count

        # Check each code format
        for code in codes:
            assert len(code) == 8
            assert code.isalnum()
            assert code.isupper()

    def test_verify_backup_code_valid(self):
        """Test backup code verification with valid code."""
        stored_codes = ["ABC12345", "DEF67890", "GHI11111"]
        original_count = len(stored_codes)

        # Verify valid code
        result = self.mfa_service.verify_backup_code(
            self.test_user_id,
            "ABC12345",
            stored_codes
        )

        assert result is True
        assert len(stored_codes) == original_count - 1  # Code consumed
        assert "ABC12345" not in stored_codes

    def test_verify_backup_code_invalid(self):
        """Test backup code verification with invalid code."""
        stored_codes = ["ABC12345", "DEF67890", "GHI11111"]
        original_count = len(stored_codes)

        # Verify invalid code
        result = self.mfa_service.verify_backup_code(
            self.test_user_id,
            "INVALID",
            stored_codes
        )

        assert result is False
        assert len(stored_codes) == original_count  # No codes consumed

    def test_verify_backup_code_case_insensitive(self):
        """Test backup code verification is case insensitive."""
        stored_codes = ["ABC12345", "DEF67890", "GHI11111"]

        # Verify with lowercase
        result = self.mfa_service.verify_backup_code(
            self.test_user_id,
            "abc12345",
            stored_codes
        )

        assert result is True
        assert "ABC12345" not in stored_codes

    def test_verify_backup_code_with_spaces(self):
        """Test backup code verification handles spaces."""
        stored_codes = ["ABC12345", "DEF67890", "GHI11111"]

        # Verify with spaces
        result = self.mfa_service.verify_backup_code(
            self.test_user_id,
            " ABC12345 ",
            stored_codes
        )

        assert result is True
        assert "ABC12345" not in stored_codes

    def test_verify_backup_code_empty_stored(self):
        """Test backup code verification with empty stored codes."""
        stored_codes = []

        result = self.mfa_service.verify_backup_code(
            self.test_user_id,
            "ABC12345",
            stored_codes
        )

        assert result is False

    def test_generate_device_hash(self):
        """Test device hash generation."""
        device_info = {
            'browser': 'Chrome',
            'os': 'Windows',
            'device': 'Desktop'
        }

        hash1 = self.mfa_service.generate_device_hash(device_info)
        hash2 = self.mfa_service.generate_device_hash(device_info)

        # Hash should be consistent for same device info
        assert hash1 == hash2
        assert len(hash1) > 0

    def test_is_device_trusted(self):
        """Test device trust checking."""
        trusted_devices = [
            {
                'hash': 'device_hash_123',
                'trusted_until': (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
        ]

        # Test trusted device
        result = self.mfa_service.is_device_trusted(
            'device_hash_123', trusted_devices)
        assert result is True

        # Test untrusted device
        result = self.mfa_service.is_device_trusted(
            'unknown_hash', trusted_devices)
        assert result is False

    def test_is_device_trusted_expired(self):
        """Test device trust checking with expired trust."""
        trusted_devices = [
            {
                'hash': 'device_hash_123',
                'trusted_until': (datetime.utcnow() - timedelta(days=1)).isoformat()
            }
        ]

        # Test expired device
        result = self.mfa_service.is_device_trusted(
            'device_hash_123', trusted_devices)
        assert result is False

    def test_add_trusted_device(self):
        """Test adding trusted device."""
        trusted_devices = []
        device_info = {
            'browser': 'Chrome',
            'os': 'Windows',
            'device': 'Desktop'
        }

        # Add device
        updated_devices = self.mfa_service.add_trusted_device(
            device_info, trusted_devices)

        assert len(updated_devices) == 1
        assert 'hash' in updated_devices[0]
        assert 'trusted_until' in updated_devices[0]
        assert updated_devices[0]['device_info'] == device_info

    def test_add_trusted_device_duplicate(self):
        """Test adding duplicate trusted device."""
        device_info = {
            'browser': 'Chrome',
            'os': 'Windows',
            'device': 'Desktop'
        }

        # Add device twice
        trusted_devices = []
        updated_devices = self.mfa_service.add_trusted_device(
            device_info, trusted_devices)
        updated_devices = self.mfa_service.add_trusted_device(
            device_info, updated_devices)

        # Should only have one device
        assert len(updated_devices) == 1

    def test_remove_trusted_device(self):
        """Test removing trusted device."""
        trusted_devices = [
            {
                'hash': 'device_hash_123',
                'device_info': {'browser': 'Chrome'}
            },
            {
                'hash': 'device_hash_456',
                'device_info': {'browser': 'Firefox'}
            }
        ]

        # Remove device
        updated_devices = self.mfa_service.remove_trusted_device(
            'device_hash_123', trusted_devices)

        assert len(updated_devices) == 1
        assert updated_devices[0]['hash'] == 'device_hash_456'

    def test_cleanup_expired_trusted_devices(self):
        """Test cleanup of expired trusted devices."""
        now = datetime.utcnow()
        trusted_devices = [
            {
                'hash': 'device_hash_123',
                'trusted_until': (now + timedelta(days=30)).isoformat()
            },
            {
                'hash': 'device_hash_456',
                'trusted_until': (now - timedelta(days=1)).isoformat()
            }
        ]

        # Cleanup expired devices
        active_devices = self.mfa_service.cleanup_expired_trusted_devices(
            trusted_devices)

        assert len(active_devices) == 1
        assert active_devices[0]['hash'] == 'device_hash_123'

    def test_custom_issuer(self):
        """Test custom issuer configuration."""
        custom_issuer = "Custom Company"
        custom_mfa_service = MFAService(issuer=custom_issuer)

        assert custom_mfa_service.issuer == custom_issuer

    def test_default_settings(self):
        """Test default settings are loaded correctly."""
        assert self.mfa_service.backup_codes_count > 0
        assert self.mfa_service.trusted_device_days > 0
