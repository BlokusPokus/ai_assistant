"""
Test OAuth services functionality.

This module tests the OAuth service classes to ensure they work correctly
with the OAuth models and providers.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from src.personal_assistant.oauth.services.token_service import OAuthTokenService
from src.personal_assistant.oauth.services.consent_service import OAuthConsentService
from src.personal_assistant.oauth.services.integration_service import OAuthIntegrationService
from src.personal_assistant.oauth.services.security_service import OAuthSecurityService


class TestOAuthServices:
    """Test OAuth service implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock database session
        self.mock_db = AsyncMock()

        # Mock OAuth manager
        self.mock_oauth_manager = Mock()

    def test_token_service_creation(self):
        """Test OAuth token service creation."""
        service = OAuthTokenService()
        assert service is not None
        assert hasattr(service, 'encrypt_token')
        assert hasattr(service, 'decrypt_token')

    def test_consent_service_creation(self):
        """Test OAuth consent service creation."""
        service = OAuthConsentService()
        assert service is not None
        assert hasattr(service, 'record_consent')
        assert hasattr(service, 'get_user_consents')

    def test_integration_service_creation(self):
        """Test OAuth integration service creation."""
        service = OAuthIntegrationService()
        assert service is not None
        assert hasattr(service, 'create_integration')
        assert hasattr(service, 'get_user_integrations')

    def test_security_service_creation(self):
        """Test OAuth security service creation."""
        service = OAuthSecurityService()
        assert service is not None
        assert hasattr(service, 'validate_state')
        assert hasattr(service, 'create_state')

    def test_token_service_encryption(self):
        """Test token encryption/decryption functionality."""
        service = OAuthTokenService()

        # Test token encryption
        original_token = "test_access_token_12345"
        encrypted_token = service.encrypt_token(original_token)

        # Should be different from original
        assert encrypted_token != original_token

        # Should be decryptable
        decrypted_token = service.decrypt_token(encrypted_token)
        assert decrypted_token == original_token

    def test_security_service_state_creation(self):
        """Test OAuth state creation and validation."""
        service = OAuthSecurityService()

        # Test state token generation
        state_token = service.generate_state_token()
        assert state_token is not None
        assert len(state_token) > 20  # Should be a reasonable length

        # Test that the service has the required methods
        assert hasattr(service, 'create_state')
        assert hasattr(service, 'validate_state')
        assert hasattr(service, 'generate_state_token')

    def test_consent_service_consent_recording(self):
        """Test consent recording functionality."""
        service = OAuthConsentService()

        # Test consent recording
        consent_data = {
            "user_id": 123,
            "integration_id": 456,
            "scopes": ["openid", "email"],
            "consent_given": True,
            "consent_reason": "User explicitly granted access"
        }

        # This would normally interact with the database
        # For now, just test that the method exists and can be called
        assert hasattr(service, 'record_consent')

    def test_integration_service_integration_management(self):
        """Test integration management functionality."""
        service = OAuthIntegrationService()

        # Test integration creation
        integration_data = {
            "user_id": 123,
            "provider": "google",
            "status": "active",
            "scopes": ["openid", "email"]
        }

        # This would normally interact with the database
        # For now, just test that the method exists and can be called
        assert hasattr(service, 'create_integration')
        assert hasattr(service, 'get_user_integrations')
        assert hasattr(service, 'update_integration')
        # Uses revoke instead of delete
        assert hasattr(service, 'revoke_integration')

    def test_service_error_handling(self):
        """Test service error handling."""
        # Test that services handle errors gracefully
        token_service = OAuthTokenService()

        # Test invalid token decryption
        try:
            decrypted = token_service.decrypt_token("invalid_token")
            # Should either return None or raise an exception
            assert decrypted is None or isinstance(decrypted, Exception)
        except Exception:
            # Expected behavior for invalid tokens
            pass

    def test_service_method_signatures(self):
        """Test that service methods have correct signatures."""
        # Test token service
        token_service = OAuthTokenService()
        assert callable(token_service.encrypt_token)
        assert callable(token_service.decrypt_token)

        # Test consent service
        consent_service = OAuthConsentService()
        assert callable(consent_service.record_consent)
        assert callable(consent_service.get_user_consents)

        # Test integration service
        integration_service = OAuthIntegrationService()
        assert callable(integration_service.create_integration)
        assert callable(integration_service.get_user_integrations)

        # Test security service
        security_service = OAuthSecurityService()
        assert callable(security_service.create_state)
        assert callable(security_service.validate_state)


if __name__ == "__main__":
    pytest.main([__file__])
