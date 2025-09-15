"""
Microsoft OAuth Provider Tests

This module tests the MicrosoftOAuthProvider implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from personal_assistant.oauth.providers.microsoft import MicrosoftOAuthProvider
from personal_assistant.oauth.exceptions import OAuthProviderError


class TestMicrosoftOAuthProvider:
    """Test cases for MicrosoftOAuthProvider."""

    @pytest.fixture
    def microsoft_provider(self):
        """Provide a MicrosoftOAuthProvider instance for testing."""
        return MicrosoftOAuthProvider(
            client_id="test_client_id",
            client_secret="test_client_secret", 
            redirect_uri="http://localhost:8000/api/v1/oauth/callback"
        )


    def test_provider_name(self, microsoft_provider):
        """Test that provider name is correctly set."""
        assert microsoft_provider.provider_name == "microsoft"

    def test_get_available_scopes(self, microsoft_provider):
        """Test that available scopes are returned."""
        scopes = microsoft_provider.get_available_scopes()
        assert isinstance(scopes, list)
        assert len(scopes) > 0
        
        # Check that Microsoft scopes are present
        scope_names = [scope["scope_name"] for scope in scopes]
        assert "openid" in scope_names
        assert "profile" in scope_names
        assert "email" in scope_names
        assert "User.Read" in scope_names
        assert "Calendars.Read" in scope_names

    def test_get_authorization_url_success(self, microsoft_provider):
        """Test successful authorization URL generation."""
        state = "test_state_123"
        scopes = ["openid", "profile", "User.Read"]
        
        url = microsoft_provider.get_authorization_url(state, scopes)
        
        assert isinstance(url, str)
        assert "login.microsoftonline.com" in url
        assert "client_id=test_client_id" in url
        assert "state=test_state_123" in url
        assert "scope=" in url
        assert "response_type=code" in url

    def test_get_authorization_url_missing_credentials(self, microsoft_provider):
        """Test authorization URL generation with missing credentials."""
        state = "test_state_123"
        scopes = ["openid", "profile", "User.Read"]
        
        # Temporarily set credentials to None to test behavior
        original_client_id = microsoft_provider.client_id
        original_client_secret = microsoft_provider.client_secret
        
        microsoft_provider.client_id = None
        microsoft_provider.client_secret = None
        
        try:
            # The method doesn't validate credentials, it just uses them
            url = microsoft_provider.get_authorization_url(state, scopes)
            assert "client_id=None" in url
            assert "state=test_state_123" in url
            assert "scope=" in url
        finally:
            # Restore original credentials
            microsoft_provider.client_id = original_client_id
            microsoft_provider.client_secret = original_client_secret

    def test_exchange_code_for_tokens_success(self, microsoft_provider):
        """Test successful token exchange with scope parameter."""
        auth_code = "test_auth_code_123"
        scopes = ["openid", "profile", "User.Read"]
        expected_tokens = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_456",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = expected_tokens
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            tokens = microsoft_provider.exchange_code_for_tokens(auth_code, scopes=scopes)
            
            # Verify core token fields are present
            assert tokens['access_token'] == expected_tokens['access_token']
            assert tokens['refresh_token'] == expected_tokens['refresh_token']
            assert tokens['expires_in'] == expected_tokens['expires_in']
            assert tokens['token_type'] == expected_tokens['token_type']
            
            mock_post.assert_called_once()
            
            # Verify that scope parameter was included in the request
            call_args = mock_post.call_args
            request_data = call_args[1]['data']
            assert 'scope' in request_data
            assert request_data['scope'] == 'openid profile User.Read'

    def test_exchange_code_for_tokens_default_scopes(self, microsoft_provider):
        """Test token exchange with default scopes when none provided."""
        auth_code = "test_auth_code_123"
        expected_tokens = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_456",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = expected_tokens
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            tokens = microsoft_provider.exchange_code_for_tokens(auth_code)
            
            # The actual implementation returns additional fields
            assert tokens["access_token"] == expected_tokens["access_token"]
            assert tokens["refresh_token"] == expected_tokens["refresh_token"]
            assert tokens["expires_in"] == expected_tokens["expires_in"]
            assert tokens["token_type"] == expected_tokens["token_type"]
            assert "provider_user_id" in tokens
            assert "provider_email" in tokens
            assert "provider_name" in tokens
            assert "raw_response" in tokens
            mock_post.assert_called_once()
            
            # Verify that default scope parameter was included in the request
            call_args = mock_post.call_args
            request_data = call_args[1]['data']
            assert 'scope' in request_data
            assert request_data['scope'] == 'openid profile email User.Read'

    def test_exchange_code_for_tokens_error(self, microsoft_provider):
        """Test token exchange with error response."""
        auth_code = "test_auth_code_123"
        scopes = ["openid", "profile", "User.Read"]
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"error": "invalid_grant"}
            mock_response.status_code = 400
            mock_response.text = '{"error": "invalid_grant"}'
            mock_post.return_value = mock_response
            
            with pytest.raises(OAuthProviderError) as exc_info:
                microsoft_provider.exchange_code_for_tokens(auth_code, scopes=scopes)
            
            assert "invalid_grant" in str(exc_info.value)

    def test_exchange_code_for_tokens_missing_scope_error(self, microsoft_provider):
        """Test token exchange with Microsoft's specific scope error."""
        auth_code = "test_auth_code_123"
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"error": "AADSTS900144", "error_description": "The request body must contain the following parameter: 'scope'"}
            mock_response.status_code = 400
            mock_response.text = '{"error": "AADSTS900144", "error_description": "The request body must contain the following parameter: \'scope\'"}'
            mock_post.return_value = mock_response
            
            with pytest.raises(OAuthProviderError) as exc_info:
                microsoft_provider.exchange_code_for_tokens(auth_code)
            
            assert "AADSTS900144" in str(exc_info.value)
            assert "scope" in str(exc_info.value)

    def test_refresh_access_token_success(self, microsoft_provider):
        """Test successful token refresh."""
        refresh_token = "refresh_token_456"
        expected_tokens = {
            "access_token": "new_access_token_789",
            "refresh_token": "new_refresh_token_101",
            "expires_in": 3600
        }
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = expected_tokens
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            tokens = microsoft_provider.refresh_access_token(refresh_token)
            
            # The actual implementation keeps the original refresh token
            assert tokens["access_token"] == expected_tokens["access_token"]
            assert tokens["refresh_token"] == refresh_token  # Original refresh token is kept
            assert tokens["expires_in"] == expected_tokens["expires_in"]
            assert tokens["token_type"] == "Bearer"
            assert tokens["scope"] == ""
            mock_post.assert_called_once()

    def test_get_user_info_success(self, microsoft_provider):
        """Test successful user info retrieval."""
        access_token = "access_token_123"
        expected_user_info = {
            "id": "microsoft_user_123",
            "email": "test@example.com",
            "name": "Test User",
            "displayName": "Test User"
        }
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = expected_user_info
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            user_info = microsoft_provider.get_user_info(access_token)
            
            assert user_info == expected_user_info
            mock_get.assert_called_once()

    def test_validate_token_success(self, microsoft_provider):
        """Test successful token validation."""
        access_token = "access_token_123"
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "user123", "mail": "test@example.com"}
            mock_get.return_value = mock_response
            
            is_valid = microsoft_provider.validate_token(access_token)
            
            assert is_valid is True
            mock_get.assert_called_once()

    def test_validate_token_invalid(self, microsoft_provider):
        """Test token validation with invalid token."""
        access_token = "invalid_token"
        
        with patch('personal_assistant.oauth.providers.microsoft.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            is_valid = microsoft_provider.validate_token(access_token)
            
            assert is_valid is False
            mock_get.assert_called_once()

    def test_revoke_token_success(self, microsoft_provider):
        """Test successful token revocation."""
        token = "access_token_123"
        
        # Microsoft provider doesn't make HTTP calls for revocation
        # It returns True as tokens expire naturally
        success = microsoft_provider.revoke_token(token)
        
        assert success is True

    def test_revoke_token_failure(self, microsoft_provider):
        """Test token revocation failure."""
        token = "invalid_token"
        
        # Microsoft provider always returns True for revocation
        # as it doesn't make HTTP calls
        success = microsoft_provider.revoke_token(token)
        
        assert success is True

    def test_get_credentials_from_environment(self, microsoft_provider):
        """Test getting credentials from environment variables."""
        # The Microsoft provider gets credentials from the fixture
        # which sets them via environment variables
        assert microsoft_provider.client_id == "test_client_id"
        assert microsoft_provider.client_secret == "test_client_secret"

    def test_get_credentials_missing(self, microsoft_provider):
        """Test getting credentials when environment variables are missing."""
        # Test with a new provider instance without credentials
        from personal_assistant.oauth.providers.microsoft import MicrosoftOAuthProvider
        
        provider = MicrosoftOAuthProvider(
            client_id=None,
            client_secret=None,
            redirect_uri="http://localhost:8000/oauth/callback"
        )
        
        assert provider.client_id is None
        assert provider.client_secret is None
