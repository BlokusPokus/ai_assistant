"""
Unit tests for PasswordService.

This module tests the password hashing, verification, and validation
functionality of the PasswordService class.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException

from personal_assistant.auth.password_service import PasswordService
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import UserDataGenerator


class TestPasswordService:
    """Test cases for PasswordService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.password_service = PasswordService(salt_rounds=4)  # Lower rounds for faster testing
        self.test_password = "TestPassword123!"
        self.user_generator = UserDataGenerator()
        self.test_user = self.user_generator.generate_user()

    def test_init_with_default_salt_rounds(self):
        """Test PasswordService initialization with default salt rounds."""
        service = PasswordService()
        assert service.salt_rounds == 12

    def test_init_with_custom_salt_rounds(self):
        """Test PasswordService initialization with custom salt rounds."""
        service = PasswordService(salt_rounds=8)
        assert service.salt_rounds == 8

    def test_hash_password_success(self):
        """Test successful password hashing."""
        hashed = self.password_service.hash_password(self.test_password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != self.test_password
        assert hashed.startswith("$2b$")  # bcrypt hash format

    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        hash1 = self.password_service.hash_password(self.test_password)
        hash2 = self.password_service.hash_password(self.test_password)
        
        assert hash1 != hash2  # Different salts should produce different hashes

    def test_hash_password_weak_password(self):
        """Test that weak passwords are rejected."""
        weak_passwords = [
            "123",  # Too short
            "password",  # No numbers/special chars
            "12345678",  # No letters
            "Password",  # No numbers/special chars
            "password123",  # No special chars
            "",  # Empty password
        ]
        
        for weak_password in weak_passwords:
            with pytest.raises(HTTPException) as exc_info:
                self.password_service.hash_password(weak_password)
            assert exc_info.value.status_code == 400

    def test_hash_password_strong_passwords(self):
        """Test that strong passwords are accepted."""
        strong_passwords = [
            "TestPassword123!",
            "MySecure@Pass1",
            "Complex#Pass99",
            "Strong$Password2024",
        ]
        
        for strong_password in strong_passwords:
            hashed = self.password_service.hash_password(strong_password)
            assert isinstance(hashed, str)
            assert len(hashed) > 0

    def test_verify_password_success(self):
        """Test successful password verification."""
        hashed = self.password_service.hash_password(self.test_password)
        result = self.password_service.verify_password(self.test_password, hashed)
        
        assert result is True

    def test_verify_password_wrong_password(self):
        """Test password verification with wrong password."""
        hashed = self.password_service.hash_password(self.test_password)
        wrong_password = "WrongPassword123!"
        result = self.password_service.verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash."""
        invalid_hash = "invalid_hash_format"
        result = self.password_service.verify_password(self.test_password, invalid_hash)
        
        assert result is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        hashed = self.password_service.hash_password(self.test_password)
        result = self.password_service.verify_password("", hashed)
        
        assert result is False

    def test_verify_password_none_password(self):
        """Test password verification with None password."""
        hashed = self.password_service.hash_password(self.test_password)
        result = self.password_service.verify_password(None, hashed)
        
        assert result is False

    def test_verify_password_none_hash(self):
        """Test password verification with None hash."""
        result = self.password_service.verify_password(self.test_password, None)
        
        assert result is False

    def test_password_validation_regex_patterns(self):
        """Test password validation regex patterns."""
        # Test various password patterns
        test_cases = [
            ("ValidPass123!", True),
            ("Another@Pass99", True),
            ("Complex#Password2024", True),
            ("short", False),  # Too short
            ("nouppercase123!", False),  # No uppercase
            ("NOLOWERCASE123!", False),  # No lowercase
            ("NoNumbers!", False),  # No numbers
            ("NoSpecialChars123", False),  # No special characters
            ("", False),  # Empty
        ]
        
        for password, should_pass in test_cases:
            if should_pass:
                # Should not raise exception
                hashed = self.password_service.hash_password(password)
                assert isinstance(hashed, str)
            else:
                # Should raise HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    self.password_service.hash_password(password)
                assert exc_info.value.status_code == 400

    def test_hash_password_with_mock_bcrypt(self):
        """Test password hashing with mocked bcrypt."""
        with patch('bcrypt.gensalt') as mock_gensalt, \
             patch('bcrypt.hashpw') as mock_hashpw:
            
            mock_gensalt.return_value = b"$2b$04$test_salt"
            mock_hashpw.return_value = b"$2b$04$test_salt$hashed_password"
            
            result = self.password_service.hash_password(self.test_password)
            
            mock_gensalt.assert_called_once_with(rounds=4)
            mock_hashpw.assert_called_once()
            assert result == "$2b$04$test_salt$hashed_password"

    def test_verify_password_with_mock_bcrypt(self):
        """Test password verification with mocked bcrypt."""
        with patch('bcrypt.checkpw') as mock_checkpw:
            mock_checkpw.return_value = True
            
            result = self.password_service.verify_password(
                self.test_password, 
                "hashed_password"
            )
            
            mock_checkpw.assert_called_once()
            assert result is True

    def test_verify_password_bcrypt_exception(self):
        """Test password verification when bcrypt raises exception."""
        with patch('bcrypt.checkpw') as mock_checkpw:
            mock_checkpw.side_effect = Exception("bcrypt error")
            
            result = self.password_service.verify_password(
                self.test_password, 
                "hashed_password"
            )
            
            assert result is False

    def test_password_service_with_different_salt_rounds(self):
        """Test password service with different salt rounds."""
        service_4 = PasswordService(salt_rounds=4)
        service_8 = PasswordService(salt_rounds=8)
        
        password = "TestPassword123!"
        hash_4 = service_4.hash_password(password)
        hash_8 = service_8.hash_password(password)
        
        # Both should work
        assert service_4.verify_password(password, hash_4) is True
        assert service_8.verify_password(password, hash_8) is True
        
        # Hashes should be different due to different salt rounds
        assert hash_4 != hash_8

    def test_password_service_performance(self):
        """Test password service performance with timing."""
        import time
        
        start_time = time.time()
        hashed = self.password_service.hash_password(self.test_password)
        hash_time = time.time() - start_time
        
        start_time = time.time()
        result = self.password_service.verify_password(self.test_password, hashed)
        verify_time = time.time() - start_time
        
        assert result is True
        # Hash should take reasonable time (not too fast, not too slow)
        assert 0.0001 < hash_time < 1.0  # Between 0.1ms and 1s
        assert 0.0001 < verify_time < 0.1  # Between 0.1ms and 100ms

    def test_password_service_edge_cases(self):
        """Test password service with edge cases."""
        # Very long password (with lowercase letters)
        long_password = "A" * 500 + "a" * 500 + "123!"
        hashed = self.password_service.hash_password(long_password)
        assert self.password_service.verify_password(long_password, hashed) is True
        
        # Password with special characters
        special_password = "Test@#$%^&*()_+-=[]{}|;':\",./<>?123!"
        hashed = self.password_service.hash_password(special_password)
        assert self.password_service.verify_password(special_password, hashed) is True
        
        # Unicode password
        unicode_password = "TestPassword123!测试"
        hashed = self.password_service.hash_password(unicode_password)
        assert self.password_service.verify_password(unicode_password, hashed) is True

    def test_password_service_consistency(self):
        """Test that password service produces consistent results."""
        # Hash the same password multiple times
        hashes = []
        for _ in range(5):
            hashed = self.password_service.hash_password(self.test_password)
            hashes.append(hashed)
        
        # All hashes should be different (due to salt)
        assert len(set(hashes)) == 5
        
        # But all should verify correctly
        for hashed in hashes:
            assert self.password_service.verify_password(self.test_password, hashed) is True

    def test_password_service_error_handling(self):
        """Test password service error handling."""
        # Test with None inputs
        with pytest.raises(TypeError):
            self.password_service.hash_password(None)
        
        # Test with non-string input
        with pytest.raises(TypeError):
            self.password_service.hash_password(123)
        
        # Test with list input - this will actually work because Python allows len() on lists
        # but it will fail validation, so we test for HTTPException instead
        with pytest.raises(HTTPException):
            self.password_service.hash_password(["password"])

    def test_password_service_integration(self):
        """Test password service integration with user data."""
        # Simulate user registration
        user_password = "NewUserPassword123!"
        hashed_password = self.password_service.hash_password(user_password)
        
        # Simulate user login
        login_success = self.password_service.verify_password(user_password, hashed_password)
        assert login_success is True
        
        # Simulate wrong password attempt
        wrong_password = "WrongPassword123!"
        login_failure = self.password_service.verify_password(wrong_password, hashed_password)
        assert login_failure is False
        
        # Simulate password change
        new_password = "NewPassword456!"
        new_hashed = self.password_service.hash_password(new_password)
        
        # Old password should fail
        assert self.password_service.verify_password(user_password, new_hashed) is False
        
        # New password should succeed
        assert self.password_service.verify_password(new_password, new_hashed) is True
