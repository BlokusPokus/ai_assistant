"""
Notion OAuth Provider Tests

This module tests the NotionOAuthProvider implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from personal_assistant.oauth.providers.notion import NotionOAuthProvider
from personal_assistant.oauth.exceptions import OAuthProviderError


class TestNotionOAuthProvider:
    """Test cases for NotionOAuthProvider."""

    @pytest.fixture
    def notion_provider(self):
        """Provide a NotionOAuthProvider instance for testing."""
        return NotionOAuthProvider(
            client_id="test_client_id",
            client_secret="test_client_secret", 
            redirect_uri="http://localhost:8000/api/v1/oauth/callback"
        )

    @pytest.fixture
    def mock_notion_credentials(self):
        """Provide mock Notion credentials for testing."""
        return {
            "client_id": "test_notion_client_id",
            "client_secret": "test_notion_client_secret",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/callback"
        }

    def test_provider_name(self, notion_provider):
        """Test that provider name is correctly set."""
        assert notion_provider.provider_name == "notion"

    def test_get_available_scopes(self, notion_provider):
        """Test that available scopes are returned."""
        scopes = notion_provider.get_available_scopes()
        assert isinstance(scopes, list)
        assert len(scopes) > 0
        
        # Check that Notion scopes are present
        scope_names = [scope["name"] for scope in scopes]
        assert "read" in scope_names
        assert "write" in scope_names

    def test_get_authorization_url_success(self, notion_provider, mock_notion_credentials):
        """Test successful authorization URL generation."""
        state = "test_state_123"
        scopes = ["read", "write"]
        
        with patch('personal_assistant.oauth.providers.notion.NotionOAuthProvider._get_credentials') as mock_get_creds:
            mock_get_creds.return_value = mock_notion_credentials
            
            url = notion_provider.get_authorization_url(state, scopes)
            
            assert isinstance(url, str)
            assert "notion.so" in url
            assert "client_id=test_notion_client_id" in url
            assert "state=test_state_123" in url
            assert "response_type=code" in url

    def test_get_authorization_url_missing_credentials(self, notion_provider):
        """Test authorization URL generation with missing credentials."""
        state = "test_state_123"
        scopes = ["read", "write"]
        
        with patch('personal_assistant.oauth.providers.notion.NotionOAuthProvider._get_credentials') as mock_get_creds:
            mock_get_creds.return_value = None
            
            with pytest.raises(OAuthProviderError) as exc_info:
                notion_provider.get_authorization_url(state, scopes)
            
            assert "OAuth credentials not configured" in str(exc_info.value)

    def test_exchange_code_for_tokens_success(self, notion_provider, mock_notion_credentials):
        """Test successful token exchange."""
        auth_code = "test_auth_code_123"
        expected_tokens = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_456",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        with patch('personal_assistant.oauth.providers.notion.NotionOAuthProvider._get_credentials') as mock_get_creds, \
             patch('personal_assistant.oauth.providers.notion.requests.post') as mock_post:
            
            mock_get_creds.return_value = mock_notion_credentials
            mock_response = Mock()
            mock_response.json.return_value = expected_tokens
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            tokens = notion_provider.exchange_code_for_tokens(auth_code)
            
            assert tokens == expected_tokens
            mock_post.assert_called_once()

    def test_exchange_code_for_tokens_error(self, notion_provider, mock_notion_credentials):
        """Test token exchange with error response."""
        auth_code = "test_auth_code_123"
        
        with patch('personal_assistant.oauth.providers.notion.NotionOAuthProvider._get_credentials') as mock_get_creds, \
             patch('personal_assistant.oauth.providers.notion.requests.post') as mock_post:
            
            mock_get_creds.return_value = mock_notion_credentials
            mock_response = Mock()
            mock_response.json.return_value = {"error": "invalid_grant"}
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            with pytest.raises(OAuthProviderError) as exc_info:
                notion_provider.exchange_code_for_tokens(auth_code)
            
            assert "invalid_grant" in str(exc_info.value)

    def test_refresh_access_token_success(self, notion_provider, mock_notion_credentials):
        """Test successful token refresh."""
        refresh_token = "refresh_token_456"
        expected_tokens = {
            "access_token": "new_access_token_789",
            "refresh_token": "new_refresh_token_101",
            "expires_in": 3600
        }
        
        with patch('personal_assistant.oauth.providers.notion.NotionOAuthProvider._get_credentials') as mock_get_creds, \
             patch('personal_assistant.oauth.providers.notion.requests.post') as mock_post:
            
            mock_get_creds.return_value = mock_notion_credentials
            mock_response = Mock()
            mock_response.json.return_value = expected_tokens
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            tokens = notion_provider.refresh_access_token(refresh_token)
            
            assert tokens == expected_tokens
            mock_post.assert_called_once()

    def test_get_user_info_success(self, notion_provider):
        """Test successful user info retrieval."""
        access_token = "access_token_123"
        expected_user_info = {
            "id": "notion_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        with patch('personal_assistant.oauth.providers.notion.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = expected_user_info
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            user_info = notion_provider.get_user_info(access_token)
            
            assert user_info == expected_user_info
            mock_get.assert_called_once()

    def test_validate_token_success(self, notion_provider):
        """Test successful token validation."""
        access_token = "access_token_123"
        
        with patch('personal_assistant.oauth.providers.notion.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            is_valid = notion_provider.validate_token(access_token)
            
            assert is_valid is True
            mock_get.assert_called_once()

    def test_validate_token_invalid(self, notion_provider):
        """Test token validation with invalid token."""
        access_token = "invalid_token"
        
        with patch('personal_assistant.oauth.providers.notion.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            is_valid = notion_provider.validate_token(access_token)
            
            assert is_valid is False
            mock_get.assert_called_once()

    def test_revoke_token_success(self, notion_provider):
        """Test successful token revocation."""
        token = "access_token_123"
        
        with patch('personal_assistant.oauth.providers.notion.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            success = notion_provider.revoke_token(token)
            
            assert success is True
            mock_post.assert_called_once()

    def test_revoke_token_failure(self, notion_provider):
        """Test token revocation failure."""
        token = "invalid_token"
        
        with patch('personal_assistant.oauth.providers.notion.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            success = notion_provider.revoke_token(token)
            
            assert success is False
            mock_post.assert_called_once()

    def test_get_credentials_from_environment(self, notion_provider):
        """Test getting credentials from environment variables."""
        with patch('personal_assistant.oauth.providers.notion.settings') as mock_settings:
            mock_settings.NOTION_OAUTH_CLIENT_ID = "env_client_id"
            mock_settings.NOTION_OAUTH_CLIENT_SECRET = "env_client_secret"
            
            credentials = notion_provider._get_credentials()
            
            assert credentials["client_id"] == "env_client_id"
            assert credentials["client_secret"] == "env_client_secret"

    def test_get_credentials_missing(self, notion_provider):
        """Test getting credentials when environment variables are missing."""
        with patch('personal_assistant.oauth.providers.notion.settings') as mock_settings:
            mock_settings.NOTION_OAUTH_CLIENT_ID = None
            mock_settings.NOTION_OAUTH_CLIENT_SECRET = None
            
            credentials = notion_provider._get_credentials()
            
            assert credentials is None
