"""
Google OAuth Provider Tests

This module tests the GoogleOAuthProvider implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from personal_assistant.oauth.providers.google import GoogleOAuthProvider
from personal_assistant.oauth.exceptions import OAuthProviderError


class TestGoogleOAuthProvider:
    """Test cases for GoogleOAuthProvider."""

    @pytest.fixture
    def google_provider(self):
        """Provide a GoogleOAuthProvider instance for testing."""
        return GoogleOAuthProvider(
            client_id="test_client_id",
            client_secret="test_client_secret", 
            redirect_uri="http://localhost:8000/api/v1/oauth/callback"
        )

    @pytest.fixture
    def mock_google_credentials(self):
        """Provide mock Google credentials for testing."""
        return {
            "client_id": "test_google_client_id",
            "client_secret": "test_google_client_secret",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/callback"
        }

    def test_provider_name(self, google_provider):
        """Test that provider name is correctly set."""
        assert google_provider.provider_name == "google"

    def test_get_available_scopes(self, google_provider):
        """Test that available scopes are returned."""
        scopes = google_provider.get_available_scopes()
        assert isinstance(scopes, list)
        assert len(scopes) > 0
        
        # Check that common Google scopes are present
        scope_names = [scope["name"] for scope in scopes]
        assert "https://www.googleapis.com/auth/calendar" in scope_names
        assert "https://www.googleapis.com/auth/gmail.readonly" in scope_names

    def test_get_authorization_url_success(self, google_provider, mock_google_credentials):
        """Test successful authorization URL generation."""
        state = "test_state_123"
        scopes = ["https://www.googleapis.com/auth/calendar"]
        
        with patch('personal_assistant.oauth.providers.google.GoogleOAuthProvider._get_credentials') as mock_get_creds:
            mock_get_creds.return_value = mock_google_credentials
            
            url = google_provider.get_authorization_url(state, scopes)
            
            assert isinstance(url, str)
            assert "accounts.google.com" in url
            assert "client_id=test_google_client_id" in url
            assert "state=test_state_123" in url
            assert "scope=" in url
            assert "response_type=code" in url

    def test_get_authorization_url_missing_credentials(self, google_provider):
        """Test authorization URL generation with missing credentials."""
        state = "test_state_123"
        scopes = ["https://www.googleapis.com/auth/calendar"]
        
        with patch('personal_assistant.oauth.providers.google.GoogleOAuthProvider._get_credentials') as mock_get_creds:
            mock_get_creds.return_value = None
            
            with pytest.raises(OAuthProviderError) as exc_info:
                google_provider.get_authorization_url(state, scopes)
            
            assert "OAuth credentials not configured" in str(exc_info.value)

    def test_exchange_code_for_tokens_success(self, google_provider, mock_google_credentials):
        """Test successful token exchange."""
        auth_code = "test_auth_code_123"
        expected_tokens = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_456",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        with patch('personal_assistant.oauth.providers.google.GoogleOAuthProvider._get_credentials') as mock_get_creds, \
             patch('personal_assistant.oauth.providers.google.requests.post') as mock_post:
            
            mock_get_creds.return_value = mock_google_credentials
            mock_response = Mock()
            mock_response.json.return_value = expected_tokens
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            tokens = google_provider.exchange_code_for_tokens(auth_code)
            
            assert tokens == expected_tokens
            mock_post.assert_called_once()

    def test_exchange_code_for_tokens_error(self, google_provider, mock_google_credentials):
        """Test token exchange with error response."""
        auth_code = "test_auth_code_123"
        
        with patch('personal_assistant.oauth.providers.google.GoogleOAuthProvider._get_credentials') as mock_get_creds, \
             patch('personal_assistant.oauth.providers.google.requests.post') as mock_post:
            
            mock_get_creds.return_value = mock_google_credentials
            mock_response = Mock()
            mock_response.json.return_value = {"error": "invalid_grant"}
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            with pytest.raises(OAuthProviderError) as exc_info:
                google_provider.exchange_code_for_tokens(auth_code)
            
            assert "invalid_grant" in str(exc_info.value)

    def test_refresh_access_token_success(self, google_provider, mock_google_credentials):
        """Test successful token refresh."""
        refresh_token = "refresh_token_456"
        expected_tokens = {
            "access_token": "new_access_token_789",
            "refresh_token": "new_refresh_token_101",
            "expires_in": 3600
        }
        
        with patch('personal_assistant.oauth.providers.google.GoogleOAuthProvider._get_credentials') as mock_get_creds, \
             patch('personal_assistant.oauth.providers.google.requests.post') as mock_post:
            
            mock_get_creds.return_value = mock_google_credentials
            mock_response = Mock()
            mock_response.json.return_value = expected_tokens
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            tokens = google_provider.refresh_access_token(refresh_token)
            
            assert tokens == expected_tokens
            mock_post.assert_called_once()

    def test_get_user_info_success(self, google_provider):
        """Test successful user info retrieval."""
        access_token = "access_token_123"
        expected_user_info = {
            "id": "google_user_123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg"
        }
        
        with patch('personal_assistant.oauth.providers.google.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = expected_user_info
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            user_info = google_provider.get_user_info(access_token)
            
            assert user_info == expected_user_info
            mock_get.assert_called_once()

    def test_validate_token_success(self, google_provider):
        """Test successful token validation."""
        access_token = "access_token_123"
        
        with patch('personal_assistant.oauth.providers.google.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            is_valid = google_provider.validate_token(access_token)
            
            assert is_valid is True
            mock_get.assert_called_once()

    def test_validate_token_invalid(self, google_provider):
        """Test token validation with invalid token."""
        access_token = "invalid_token"
        
        with patch('personal_assistant.oauth.providers.google.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            is_valid = google_provider.validate_token(access_token)
            
            assert is_valid is False
            mock_get.assert_called_once()

    def test_revoke_token_success(self, google_provider):
        """Test successful token revocation."""
        token = "access_token_123"
        
        with patch('personal_assistant.oauth.providers.google.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            success = google_provider.revoke_token(token)
            
            assert success is True
            mock_post.assert_called_once()

    def test_revoke_token_failure(self, google_provider):
        """Test token revocation failure."""
        token = "invalid_token"
        
        with patch('personal_assistant.oauth.providers.google.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            success = google_provider.revoke_token(token)
            
            assert success is False
            mock_post.assert_called_once()

    def test_get_credentials_from_environment(self, google_provider):
        """Test getting credentials from environment variables."""
        with patch('personal_assistant.oauth.providers.google.settings') as mock_settings:
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = "env_client_id"
            mock_settings.GOOGLE_OAUTH_CLIENT_SECRET = "env_client_secret"
            
            credentials = google_provider._get_credentials()
            
            assert credentials["client_id"] == "env_client_id"
            assert credentials["client_secret"] == "env_client_secret"

    def test_get_credentials_missing(self, google_provider):
        """Test getting credentials when environment variables are missing."""
        with patch('personal_assistant.oauth.providers.google.settings') as mock_settings:
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = None
            mock_settings.GOOGLE_OAUTH_CLIENT_SECRET = None
            
            credentials = google_provider._get_credentials()
            
            assert credentials is None
