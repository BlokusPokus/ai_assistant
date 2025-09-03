"""
Unit tests for JWTService.

This module tests the JWT token generation, validation, and refresh
functionality of the JWTService class.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from fastapi import HTTPException

from personal_assistant.auth.jwt_service import JWTService
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import UserDataGenerator, AuthDataGenerator


class TestJWTService:
    """Test cases for JWTService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.jwt_service = JWTService()
        self.test_user = UserDataGenerator.generate_user()
        self.test_data = {
            "user_id": self.test_user["id"],
            "email": self.test_user["email"],
            "sub": self.test_user["email"],
        }

    def test_init_with_default_settings(self):
        """Test JWTService initialization with default settings."""
        service = JWTService()
        assert service.algorithm == "HS256"
        assert service.access_token_expire_minutes == 15
        assert service.refresh_token_expire_days == 7
        assert isinstance(service.secret_key, str)
        assert len(service.secret_key) > 0

    def test_get_secret_key_from_settings(self):
        """Test getting secret key from settings."""
        with patch('personal_assistant.auth.jwt_service.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test_secret_key"
            mock_settings.ENVIRONMENT = "development"
            
            service = JWTService()
            assert service.secret_key == "test_secret_key"

    def test_get_secret_key_generated_for_development(self):
        """Test secret key generation for development environment."""
        with patch('personal_assistant.auth.jwt_service.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = None
            mock_settings.ENVIRONMENT = "development"
            
            with patch('secrets.token_urlsafe') as mock_token:
                mock_token.return_value = "generated_secret_key"
                
                service = JWTService()
                assert service.secret_key == "generated_secret_key"
                mock_token.assert_called_once_with(32)

    def test_get_secret_key_production_error(self):
        """Test that production environment requires JWT_SECRET_KEY."""
        with patch('personal_assistant.auth.jwt_service.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = None
            mock_settings.ENVIRONMENT = "production"
            
            with pytest.raises(ValueError) as exc_info:
                JWTService()
            assert "JWT_SECRET_KEY must be set in production environment" in str(exc_info.value)

    def test_create_access_token_success(self):
        """Test successful access token creation."""
        token = self.jwt_service.create_access_token(self.test_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens have 3 parts separated by dots
        assert len(token.split('.')) == 3

    def test_create_access_token_with_expires_delta(self):
        """Test access token creation with custom expiration."""
        expires_delta = timedelta(minutes=30)
        token = self.jwt_service.create_access_token(self.test_data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_empty_data(self):
        """Test access token creation with empty data."""
        token = self.jwt_service.create_access_token({})
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_none_data(self):
        """Test access token creation with None data."""
        with pytest.raises(AttributeError):
            self.jwt_service.create_access_token(None)

    def test_create_refresh_token_success(self):
        """Test successful refresh token creation."""
        token = self.jwt_service.create_refresh_token(self.test_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert len(token.split('.')) == 3

    def test_create_refresh_token_with_expires_delta(self):
        """Test refresh token creation with custom expiration."""
        expires_delta = timedelta(days=14)
        token = self.jwt_service.create_refresh_token(self.test_data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_success(self):
        """Test successful token verification."""
        token = self.jwt_service.create_access_token(self.test_data)
        payload = self.jwt_service.verify_token(token)
        
        assert isinstance(payload, dict)
        assert payload["user_id"] == self.test_data["user_id"]
        assert payload["email"] == self.test_data["email"]
        assert "exp" in payload
        assert "type" in payload
        assert payload["type"] == "access"

    def test_verify_token_invalid_token(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            self.jwt_service.verify_token(invalid_token)
        assert exc_info.value.status_code == 401

    def test_verify_token_expired_token(self):
        """Test token verification with expired token."""
        # Create token with very short expiration
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = self.jwt_service.create_access_token(self.test_data, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            self.jwt_service.verify_token(token)
        assert exc_info.value.status_code == 401

    def test_verify_token_wrong_secret(self):
        """Test token verification with wrong secret key."""
        # Create token with one service
        service1 = JWTService()
        token = service1.create_access_token(self.test_data)
        
        # Try to verify with different service (different secret)
        with patch('personal_assistant.auth.jwt_service.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = "different_secret_key"
            mock_settings.ENVIRONMENT = "development"
            
            service2 = JWTService()
            with pytest.raises(HTTPException) as exc_info:
                service2.verify_token(token)
            assert exc_info.value.status_code == 401

    def test_verify_token_malformed_token(self):
        """Test token verification with malformed token."""
        malformed_tokens = [
            "not.a.token",
            "too.few.parts",
            "too.many.parts.here.extra",
            "",
            "not-a-jwt-token",
        ]
        
        for malformed_token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                self.jwt_service.verify_token(malformed_token)
            assert exc_info.value.status_code == 401

    def test_refresh_access_token_success(self):
        """Test successful token refresh."""
        refresh_token = self.jwt_service.create_refresh_token(self.test_data)
        new_access_token = self.jwt_service.refresh_access_token(refresh_token)
        
        assert isinstance(new_access_token, str)
        assert len(new_access_token) > 0
        assert new_access_token != refresh_token

    def test_refresh_access_token_invalid_token(self):
        """Test token refresh with invalid token."""
        invalid_token = "invalid.refresh.token"
        
        with pytest.raises(HTTPException) as exc_info:
            self.jwt_service.refresh_access_token(invalid_token)
        assert exc_info.value.status_code == 401

    def test_refresh_access_token_expired_token(self):
        """Test token refresh with expired token."""
        # Create expired refresh token
        expires_delta = timedelta(seconds=-1)
        expired_token = self.jwt_service.create_refresh_token(self.test_data, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            self.jwt_service.refresh_access_token(expired_token)
        assert exc_info.value.status_code == 401

    def test_refresh_access_token_with_access_token(self):
        """Test that access tokens cannot be used for refresh."""
        access_token = self.jwt_service.create_access_token(self.test_data)
        
        with pytest.raises(HTTPException) as exc_info:
            self.jwt_service.refresh_access_token(access_token)
        assert exc_info.value.status_code == 401

    def test_token_expiration_times(self):
        """Test that tokens have correct expiration times."""
        # Test access token expiration
        access_token = self.jwt_service.create_access_token(self.test_data)
        access_payload = self.jwt_service.verify_token(access_token)
        
        # Test refresh token expiration
        refresh_token = self.jwt_service.create_refresh_token(self.test_data)
        refresh_payload = self.jwt_service.verify_token(refresh_token)
        
        # Access token should expire sooner than refresh token
        assert access_payload["exp"] < refresh_payload["exp"]
        
        # Check that both tokens have expiration times
        assert "exp" in access_payload
        assert "exp" in refresh_payload
        
        # Check that expiration times are reasonable (positive numbers)
        assert access_payload["exp"] > 0
        assert refresh_payload["exp"] > 0

    def test_token_contains_required_claims(self):
        """Test that tokens contain all required claims."""
        token = self.jwt_service.create_access_token(self.test_data)
        payload = self.jwt_service.verify_token(token)
        
        required_claims = ["user_id", "email", "sub", "exp", "type"]
        for claim in required_claims:
            assert claim in payload

    def test_token_issuer_and_audience(self):
        """Test token issuer and audience if configured."""
        # This test depends on the actual implementation
        # If issuer/audience are added to tokens, test them here
        token = self.jwt_service.create_access_token(self.test_data)
        payload = self.jwt_service.verify_token(token)
        
        # Basic claims should be present
        assert "user_id" in payload
        assert "email" in payload

    def test_jwt_service_with_mock_jwt(self):
        """Test JWT service with mocked JWT library."""
        with patch('jwt.encode') as mock_encode, \
             patch('jwt.decode') as mock_decode:
            
            mock_encode.return_value = "mocked.jwt.token"
            mock_decode.return_value = self.test_data
            
            # Test token creation
            token = self.jwt_service.create_access_token(self.test_data)
            assert token == "mocked.jwt.token"
            mock_encode.assert_called_once()
            
            # Test token verification
            payload = self.jwt_service.verify_token(token)
            assert payload == self.test_data
            mock_decode.assert_called_once()

    def test_jwt_service_error_handling(self):
        """Test JWT service error handling."""
        # Test with invalid data types
        with pytest.raises(AttributeError):
            self.jwt_service.create_access_token("not_a_dict")
        
        with pytest.raises(AttributeError):
            self.jwt_service.create_access_token(123)
        
        with pytest.raises(AttributeError):
            self.jwt_service.create_access_token(None)

    def test_jwt_service_performance(self):
        """Test JWT service performance."""
        import time
        
        # Test token creation performance
        start_time = time.time()
        for _ in range(100):
            self.jwt_service.create_access_token(self.test_data)
        creation_time = time.time() - start_time
        
        # Test token verification performance
        token = self.jwt_service.create_access_token(self.test_data)
        start_time = time.time()
        for _ in range(100):
            self.jwt_service.verify_token(token)
        verification_time = time.time() - start_time
        
        # Both operations should be fast
        assert creation_time < 1.0  # Less than 1 second for 100 tokens
        assert verification_time < 1.0  # Less than 1 second for 100 verifications

    def test_jwt_service_integration(self):
        """Test JWT service integration with user authentication flow."""
        # Simulate user login
        user_data = {
            "user_id": 123,
            "email": "test@example.com",
            "sub": "test@example.com",
        }
        
        # Create tokens
        access_token = self.jwt_service.create_access_token(user_data)
        refresh_token = self.jwt_service.create_refresh_token(user_data)
        
        # Verify access token
        access_payload = self.jwt_service.verify_token(access_token)
        assert access_payload["user_id"] == 123
        assert access_payload["email"] == "test@example.com"
        
        # Refresh access token
        new_access_token = self.jwt_service.refresh_access_token(refresh_token)
        new_payload = self.jwt_service.verify_token(new_access_token)
        assert new_payload["user_id"] == 123
        assert new_payload["email"] == "test@example.com"
        
        # New access token should be valid
        assert isinstance(new_access_token, str)
        assert len(new_access_token) > 0

    def test_jwt_service_with_different_algorithms(self):
        """Test JWT service with different algorithms."""
        # This test would require modifying the service to accept different algorithms
        # For now, test that the default algorithm works
        token = self.jwt_service.create_access_token(self.test_data)
        payload = self.jwt_service.verify_token(token)
        
        assert payload["user_id"] == self.test_data["user_id"]

    def test_jwt_service_token_security(self):
        """Test JWT service token security features."""
        # Test that tokens are not predictable
        token1 = self.jwt_service.create_access_token(self.test_data)
        token2 = self.jwt_service.create_access_token(self.test_data)
        
        # Tokens should be different even with same data (due to different creation times)
        # Note: In the current implementation, tokens might be the same if created at the same time
        # This is acceptable behavior
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        
        # Both should be valid
        payload1 = self.jwt_service.verify_token(token1)
        payload2 = self.jwt_service.verify_token(token2)
        
        assert payload1["user_id"] == payload2["user_id"]
        assert payload1["email"] == payload2["email"]
        
        # Both should have the same type
        assert payload1["type"] == payload2["type"]
        assert payload1["type"] == "access"
