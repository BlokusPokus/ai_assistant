"""
Unit tests for AuthUtils.

This module tests the authentication utility functions including
token extraction, user context management, and other helpers.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import Request, HTTPException

from personal_assistant.auth.auth_utils import AuthUtils
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import UserDataGenerator, AuthDataGenerator


class TestAuthUtils:
    """Test cases for AuthUtils."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_user = UserDataGenerator.generate_user()
        self.test_token = "test_jwt_token_here"
        self.test_payload = {
            "user_id": self.test_user["id"],
            "email": self.test_user["email"],
            "sub": self.test_user["email"],
            "exp": 1640995200,
            "iat": 1640991600,
        }

    def test_extract_token_from_header_success(self):
        """Test successful token extraction from Authorization header."""
        # Create mock request with Bearer token
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {self.test_token}"}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        
        assert result == self.test_token

    def test_extract_token_from_header_no_bearer_prefix(self):
        """Test token extraction without Bearer prefix."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": self.test_token}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        
        assert result is None

    def test_extract_token_from_header_no_authorization_header(self):
        """Test token extraction when Authorization header is missing."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        
        assert result is None

    def test_extract_token_from_header_none_authorization(self):
        """Test token extraction when Authorization header is None."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": None}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        
        assert result is None

    def test_extract_token_from_header_empty_authorization(self):
        """Test token extraction with empty Authorization header."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": ""}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        
        assert result is None

    def test_extract_token_from_header_malformed_bearer(self):
        """Test token extraction with malformed Bearer token."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer"}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        
        assert result is None

    def test_extract_token_from_header_extra_spaces(self):
        """Test token extraction with extra spaces in Bearer token."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer  {self.test_token}  "}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        
        # The implementation uses startswith("Bearer ") so it matches "Bearer " followed by anything
        # It returns everything after "Bearer " (7 characters)
        assert result == f" {self.test_token}  "

    def test_extract_token_from_cookie_success(self):
        """Test successful token extraction from cookies."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {"access_token": self.test_token}
        
        result = AuthUtils.extract_token_from_cookie(mock_request)
        
        assert result == self.test_token

    def test_extract_token_from_cookie_custom_name(self):
        """Test token extraction from cookies with custom cookie name."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {"custom_token": self.test_token}
        
        result = AuthUtils.extract_token_from_cookie(mock_request, "custom_token")
        
        assert result == self.test_token

    def test_extract_token_from_cookie_no_cookie(self):
        """Test token extraction when cookie is missing."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {}
        
        result = AuthUtils.extract_token_from_cookie(mock_request)
        
        assert result is None

    def test_extract_token_from_cookie_none_cookies(self):
        """Test token extraction when cookies is None."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = None
        
        # This will raise an AttributeError because cookies is None
        with pytest.raises(AttributeError):
            AuthUtils.extract_token_from_cookie(mock_request)

    def test_extract_token_from_cookie_empty_cookie(self):
        """Test token extraction with empty cookie value."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {"access_token": ""}
        
        result = AuthUtils.extract_token_from_cookie(mock_request)
        
        assert result == ""

    def test_get_user_id_from_token_success(self):
        """Test successful user ID extraction from token payload."""
        result = AuthUtils.get_user_id_from_token(self.test_payload)
        
        assert result == self.test_user["id"]

    def test_get_user_id_from_token_no_user_id(self):
        """Test user ID extraction when user_id is missing."""
        payload_without_user_id = {"email": "test@example.com"}
        
        result = AuthUtils.get_user_id_from_token(payload_without_user_id)
        
        assert result is None

    def test_get_user_id_from_token_none_payload(self):
        """Test user ID extraction with None payload."""
        # This will raise an AttributeError because None doesn't have a get method
        with pytest.raises(AttributeError):
            AuthUtils.get_user_id_from_token(None)

    def test_get_user_id_from_token_empty_payload(self):
        """Test user ID extraction with empty payload."""
        result = AuthUtils.get_user_id_from_token({})
        
        assert result is None

    def test_get_user_id_from_token_string_user_id(self):
        """Test user ID extraction with string user_id."""
        payload_with_string_id = {"user_id": "123"}
        
        result = AuthUtils.get_user_id_from_token(payload_with_string_id)
        
        assert result == "123"

    def test_get_user_email_from_token_success(self):
        """Test successful user email extraction from token payload."""
        result = AuthUtils.get_user_email_from_token(self.test_payload)
        
        assert result == self.test_user["email"]

    def test_get_user_email_from_token_no_email(self):
        """Test user email extraction when email is missing."""
        payload_without_email = {"user_id": 123}
        
        result = AuthUtils.get_user_email_from_token(payload_without_email)
        
        assert result is None

    def test_get_user_email_from_token_none_payload(self):
        """Test user email extraction with None payload."""
        # This will raise an AttributeError because None doesn't have a get method
        with pytest.raises(AttributeError):
            AuthUtils.get_user_email_from_token(None)

    def test_get_user_email_from_token_empty_payload(self):
        """Test user email extraction with empty payload."""
        result = AuthUtils.get_user_email_from_token({})
        
        assert result is None

    def test_get_user_email_from_token_sub_field(self):
        """Test user email extraction using sub field."""
        payload_with_sub = {"sub": "test@example.com"}
        
        result = AuthUtils.get_user_email_from_token(payload_with_sub)
        
        # The implementation only looks for "email" field, not "sub"
        assert result is None

    def test_auth_utils_integration(self):
        """Test AuthUtils integration with complete authentication flow."""
        # Simulate request with Bearer token
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {self.test_token}"}
        mock_request.cookies = {"access_token": self.test_token}
        
        # Extract token from header
        header_token = AuthUtils.extract_token_from_header(mock_request)
        assert header_token == self.test_token
        
        # Extract token from cookie
        cookie_token = AuthUtils.extract_token_from_cookie(mock_request)
        assert cookie_token == self.test_token
        
        # Extract user info from payload
        user_id = AuthUtils.get_user_id_from_token(self.test_payload)
        user_email = AuthUtils.get_user_email_from_token(self.test_payload)
        
        assert user_id == self.test_user["id"]
        assert user_email == self.test_user["email"]

    def test_auth_utils_with_different_token_formats(self):
        """Test AuthUtils with different token formats."""
        # Test with JWT-like token
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {jwt_token}"}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        assert result == jwt_token
        
        # Test with custom token format
        custom_token = "custom_token_format_12345"
        mock_request.headers = {"Authorization": f"Bearer {custom_token}"}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        assert result == custom_token

    def test_auth_utils_error_handling(self):
        """Test AuthUtils error handling with invalid inputs."""
        # Test with non-Request object
        with pytest.raises(AttributeError):
            AuthUtils.extract_token_from_header("not_a_request")
        
        # Test with Request object without headers
        mock_request = Mock(spec=Request)
        del mock_request.headers
        
        with pytest.raises(AttributeError):
            AuthUtils.extract_token_from_header(mock_request)

    def test_auth_utils_performance(self):
        """Test AuthUtils performance with multiple operations."""
        import time
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {self.test_token}"}
        mock_request.cookies = {"access_token": self.test_token}
        
        # Test performance of token extraction
        start_time = time.time()
        for _ in range(1000):
            AuthUtils.extract_token_from_header(mock_request)
            AuthUtils.extract_token_from_cookie(mock_request)
        extraction_time = time.time() - start_time
        
        # Test performance of payload processing
        start_time = time.time()
        for _ in range(1000):
            AuthUtils.get_user_id_from_token(self.test_payload)
            AuthUtils.get_user_email_from_token(self.test_payload)
        processing_time = time.time() - start_time
        
        # Both operations should be very fast
        assert extraction_time < 0.1  # Less than 100ms for 1000 operations
        assert processing_time < 0.1  # Less than 100ms for 1000 operations

    def test_auth_utils_with_mock_request(self):
        """Test AuthUtils with mocked Request object."""
        with patch('fastapi.Request') as mock_request_class:
            mock_request = Mock()
            mock_request.headers = {"Authorization": f"Bearer {self.test_token}"}
            mock_request.cookies = {"access_token": self.test_token}
            mock_request_class.return_value = mock_request
            
            # Test token extraction
            header_token = AuthUtils.extract_token_from_header(mock_request)
            cookie_token = AuthUtils.extract_token_from_cookie(mock_request)
            
            assert header_token == self.test_token
            assert cookie_token == self.test_token

    def test_auth_utils_edge_cases(self):
        """Test AuthUtils with edge cases."""
        # Test with very long token
        long_token = "a" * 10000
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {long_token}"}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        assert result == long_token
        
        # Test with special characters in token
        special_token = "token-with-special-chars!@#$%^&*()"
        mock_request.headers = {"Authorization": f"Bearer {special_token}"}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        assert result == special_token
        
        # Test with Unicode characters in token
        unicode_token = "token-with-unicode-测试"
        mock_request.headers = {"Authorization": f"Bearer {unicode_token}"}
        
        result = AuthUtils.extract_token_from_header(mock_request)
        assert result == unicode_token

    def test_auth_utils_static_methods(self):
        """Test that AuthUtils methods are static."""
        # Verify that methods can be called without instance
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {self.test_token}"}
        
        # These should work without creating an instance
        result1 = AuthUtils.extract_token_from_header(mock_request)
        result2 = AuthUtils.get_user_id_from_token(self.test_payload)
        result3 = AuthUtils.get_user_email_from_token(self.test_payload)
        
        assert result1 == self.test_token
        assert result2 == self.test_user["id"]
        assert result3 == self.test_user["email"]

    def test_auth_utils_with_complex_payload(self):
        """Test AuthUtils with complex token payload."""
        complex_payload = {
            "user_id": 123,
            "email": "test@example.com",
            "sub": "test@example.com",
            "roles": ["user", "admin"],
            "permissions": ["read", "write", "delete"],
            "exp": 1640995200,
            "iat": 1640991600,
            "iss": "personal-assistant",
            "aud": "api",
            "custom_field": "custom_value",
        }
        
        user_id = AuthUtils.get_user_id_from_token(complex_payload)
        user_email = AuthUtils.get_user_email_from_token(complex_payload)
        
        assert user_id == 123
        assert user_email == "test@example.com"
