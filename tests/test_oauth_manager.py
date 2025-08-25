"""
Test OAuthManager integration and orchestration.

This module tests the OAuthManager class to ensure it can properly
orchestrate all OAuth services and providers.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from src.personal_assistant.oauth.oauth_manager import OAuthManager


class TestOAuthManager:
    """Test OAuthManager integration and orchestration."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock database session
        self.mock_db = AsyncMock()

        # Create OAuthManager instance
        self.oauth_manager = OAuthManager()

    def test_oauth_manager_creation(self):
        """Test OAuthManager creation and initialization."""
        assert self.oauth_manager is not None
        assert hasattr(self.oauth_manager, 'token_service')
        assert hasattr(self.oauth_manager, 'consent_service')
        assert hasattr(self.oauth_manager, 'integration_service')
        assert hasattr(self.oauth_manager, 'security_service')

    def test_oauth_manager_providers(self):
        """Test that OAuthManager has all required providers."""
        assert hasattr(self.oauth_manager, 'providers')
        assert 'google' in self.oauth_manager.providers
        assert 'microsoft' in self.oauth_manager.providers
        assert 'notion' in self.oauth_manager.providers
        assert 'youtube' in self.oauth_manager.providers

    def test_oauth_manager_services(self):
        """Test that OAuthManager has all required services."""
        assert hasattr(self.oauth_manager, 'token_service')
        assert hasattr(self.oauth_manager, 'consent_service')
        assert hasattr(self.oauth_manager, 'integration_service')
        assert hasattr(self.oauth_manager, 'security_service')

    def test_oauth_manager_methods(self):
        """Test that OAuthManager has all required methods."""
        required_methods = [
            'initiate_oauth_flow',
            'handle_oauth_callback',
            'refresh_integration_tokens',
            'revoke_integration',
            'sync_all_integrations',
            'get_user_integrations'
        ]

        for method_name in required_methods:
            assert hasattr(self.oauth_manager,
                           method_name), f"Missing method: {method_name}"

    def test_oauth_manager_provider_initialization(self):
        """Test that OAuth providers are properly initialized."""
        # Test that providers are registered as classes
        assert 'google' in self.oauth_manager.providers
        assert 'microsoft' in self.oauth_manager.providers
        assert 'notion' in self.oauth_manager.providers
        assert 'youtube' in self.oauth_manager.providers

        # Test that we can get provider instances
        google_provider = self.oauth_manager.get_provider('google')
        assert google_provider is not None
        assert hasattr(google_provider, 'get_authorization_url')
        assert hasattr(google_provider, 'exchange_code_for_tokens')

        microsoft_provider = self.oauth_manager.get_provider('microsoft')
        assert microsoft_provider is not None
        assert hasattr(microsoft_provider, 'get_authorization_url')
        assert hasattr(microsoft_provider, 'exchange_code_for_tokens')

    def test_oauth_manager_service_initialization(self):
        """Test that OAuth services are properly initialized."""
        # Test token service
        assert self.oauth_manager.token_service is not None
        assert hasattr(self.oauth_manager.token_service, 'encrypt_token')
        assert hasattr(self.oauth_manager.token_service, 'decrypt_token')

        # Test consent service
        assert self.oauth_manager.consent_service is not None
        assert hasattr(self.oauth_manager.consent_service, 'record_consent')
        assert hasattr(self.oauth_manager.consent_service, 'get_user_consents')

        # Test integration service
        assert self.oauth_manager.integration_service is not None
        assert hasattr(self.oauth_manager.integration_service,
                       'create_integration')
        assert hasattr(self.oauth_manager.integration_service,
                       'get_user_integrations')

        # Test security service
        assert self.oauth_manager.security_service is not None
        assert hasattr(self.oauth_manager.security_service, 'create_state')
        assert hasattr(self.oauth_manager.security_service, 'validate_state')

    def test_oauth_manager_authorization_url_generation(self):
        """Test OAuth authorization URL generation."""
        # Test that we can get a Google provider instance
        google_provider = self.oauth_manager.get_provider('google')

        # Test authorization URL generation directly on provider
        auth_url = google_provider.get_authorization_url(
            state='test_state',
            scopes=['openid', 'email']
        )

        # Verify authorization URL
        assert auth_url is not None
        assert 'accounts.google.com' in auth_url
        assert 'response_type=code' in auth_url
        assert 'client_id=' in auth_url

    def test_oauth_manager_provider_support(self):
        """Test that OAuthManager supports all required providers."""
        supported_providers = ['google', 'microsoft', 'notion', 'youtube']

        for provider in supported_providers:
            # Test that provider exists
            assert provider in self.oauth_manager.providers

            # Test that we can get provider instances
            provider_instance = self.oauth_manager.get_provider(provider)
            assert provider_instance is not None

            # Test that provider can generate authorization URL
            auth_url = provider_instance.get_authorization_url(
                state='test_state',
                scopes=['openid', 'email']
            )

            assert auth_url is not None
            assert 'response_type=code' in auth_url

    def test_oauth_manager_error_handling(self):
        """Test OAuthManager error handling."""
        # Test with invalid provider
        with pytest.raises(Exception):
            self.oauth_manager.get_provider('invalid_provider')

    def test_oauth_manager_integration_methods(self):
        """Test OAuthManager integration management methods."""
        # Test that all integration methods exist and are callable
        integration_methods = [
            'get_user_integrations',
            'refresh_integration_tokens',
            'revoke_integration',
            'sync_all_integrations'
        ]

        for method_name in integration_methods:
            method = getattr(self.oauth_manager, method_name)
            assert callable(method), f"Method {method_name} is not callable"


if __name__ == "__main__":
    pytest.main([__file__])
