"""
Test OAuth provider implementations.

This module tests the OAuth provider classes to ensure they work correctly
and can handle OAuth 2.0 flows properly.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.personal_assistant.oauth.providers.google import GoogleOAuthProvider
from src.personal_assistant.oauth.providers.microsoft import MicrosoftOAuthProvider
from src.personal_assistant.oauth.providers.notion import NotionOAuthProvider
from src.personal_assistant.oauth.providers.youtube import YouTubeOAuthProvider


class TestOAuthProviders:
    """Test OAuth provider implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock configuration for testing
        self.config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "https://example.com/callback"
        }

    def test_google_oauth_provider(self):
        """Test Google OAuth provider."""
        provider = GoogleOAuthProvider(**self.config)

        # Test provider attributes
        assert provider.provider_name == "google"
        assert provider.client_id == "test_client_id"
        assert provider.client_secret == "test_client_secret"
        assert provider.redirect_uri == "https://example.com/callback"

        # Test authorization URL generation
        auth_url = provider.get_authorization_url(
            state="test_state",
            scopes=["openid", "email"]
        )

        assert "accounts.google.com" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "state=test_state" in auth_url
        assert "scope=openid+email" in auth_url

    def test_microsoft_oauth_provider(self):
        """Test Microsoft OAuth provider."""
        provider = MicrosoftOAuthProvider(**self.config)

        # Test provider attributes
        assert provider.provider_name == "microsoft"
        assert provider.client_id == "test_client_id"
        assert provider.client_secret == "test_client_secret"

        # Test authorization URL generation
        auth_url = provider.get_authorization_url(
            state="test_state",
            scopes=["openid", "email"]
        )

        assert "login.microsoftonline.com" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "state=test_state" in auth_url

    def test_notion_oauth_provider(self):
        """Test Notion OAuth provider."""
        provider = NotionOAuthProvider(**self.config)

        # Test provider attributes
        assert provider.provider_name == "notion"
        assert provider.client_id == "test_client_id"
        assert provider.client_secret == "test_client_secret"

        # Test authorization URL generation
        auth_url = provider.get_authorization_url(
            state="test_state",
            scopes=["read", "write"]
        )

        assert "api.notion.com" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "state=test_state" in auth_url

    def test_youtube_oauth_provider(self):
        """Test YouTube OAuth provider."""
        provider = YouTubeOAuthProvider(**self.config)

        # Test provider attributes
        assert provider.provider_name == "youtube"
        assert provider.client_id == "test_client_id"
        assert provider.client_secret == "test_client_secret"

        # Test authorization URL generation
        auth_url = provider.get_authorization_url(
            state="test_state",
            scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )

        assert "accounts.google.com" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "state=test_state" in auth_url

    def test_provider_token_exchange(self):
        """Test token exchange functionality."""
        provider = GoogleOAuthProvider(**self.config)

        # Test that real HTTP calls fail with invalid credentials (expected behavior)
        with pytest.raises(Exception) as exc_info:
            tokens = provider.exchange_code_for_tokens("test_auth_code")

        # Should fail with invalid client error
        assert "invalid_client" in str(exc_info.value)

    def test_provider_token_refresh(self):
        """Test token refresh functionality."""
        provider = GoogleOAuthProvider(**self.config)

        # Test that real HTTP calls fail with invalid credentials (expected behavior)
        with pytest.raises(Exception) as exc_info:
            tokens = provider.refresh_access_token("test_refresh_token")

        # Should fail with invalid client error
        assert "invalid_client" in str(exc_info.value)

    def test_provider_error_handling(self):
        """Test error handling in providers."""
        provider = GoogleOAuthProvider(**self.config)

        # Test that invalid code raises exception (real implementation behavior)
        with pytest.raises(Exception) as exc_info:
            tokens = provider.exchange_code_for_tokens("invalid_code")

        # Should fail with invalid client error
        assert "invalid_client" in str(exc_info.value)

    def test_provider_scope_validation(self):
        """Test scope validation in providers."""
        provider = GoogleOAuthProvider(**self.config)

        # Test valid scopes
        valid_scopes = ["openid", "https://www.googleapis.com/auth/userinfo.email",
                        "https://www.googleapis.com/auth/userinfo.profile"]
        is_valid, invalid_scopes = provider.validate_scopes(valid_scopes)
        assert is_valid is True
        assert len(invalid_scopes) == 0

        # Test invalid scopes
        invalid_scopes = ["invalid_scope", "another_invalid"]
        is_valid, invalid_scopes = provider.validate_scopes(invalid_scopes)
        assert is_valid is False
        assert len(invalid_scopes) == 2


if __name__ == "__main__":
    pytest.main([__file__])
