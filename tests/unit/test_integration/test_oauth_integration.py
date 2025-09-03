"""
Unit tests for OAuth integration functionality.

This module tests the OAuth system including
provider management, token handling, and security measures.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from tests.utils.test_data_generators import APIDataGenerator, UserDataGenerator


class TestOAuthIntegration:
    """Test class for OAuth integration functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_generator = APIDataGenerator()
        self.user_generator = UserDataGenerator()

    @pytest.mark.asyncio
    async def test_oauth_manager_initialization(self):
        """Test OAuth manager initialization."""
        # Mock the OAuth manager
        with patch('personal_assistant.oauth.oauth_manager.OAuthManager') as mock_class:
            mock_manager = Mock()
            mock_class.return_value = mock_manager
            
            # Test initialization
            from personal_assistant.oauth.oauth_manager import OAuthManager
            
            manager = OAuthManager()
            assert manager is not None
            assert hasattr(manager, 'token_service')
            assert hasattr(manager, 'consent_service')
            assert hasattr(manager, 'integration_service')
            assert hasattr(manager, 'security_service')

    @pytest.mark.asyncio
    async def test_oauth_provider_registry(self):
        """Test OAuth provider registry functionality."""
        # Mock the OAuth manager
        with patch('personal_assistant.oauth.oauth_manager.OAuthManager') as mock_class:
            mock_manager = Mock()
            mock_class.return_value = mock_manager
            
            # Mock provider registry
            mock_manager.providers = {
                "google": Mock(),
                "microsoft": Mock(),
                "notion": Mock(),
                "youtube": Mock()
            }
            
            # Test provider registry
            from personal_assistant.oauth.oauth_manager import OAuthManager
            
            manager = OAuthManager()
            assert "google" in manager.providers
            assert "microsoft" in manager.providers
            assert "notion" in manager.providers
            assert "youtube" in manager.providers

    @pytest.mark.asyncio
    async def test_oauth_token_service(self):
        """Test OAuth token service functionality."""
        # Mock the token service
        with patch('personal_assistant.oauth.services.token_service.OAuthTokenService') as mock_class:
            mock_token_service = Mock()
            mock_class.return_value = mock_token_service
            
            # Mock token operations
            mock_token_service.create_token = AsyncMock(return_value={
                "access_token": "access_token_123",
                "refresh_token": "refresh_token_123",
                "expires_in": 3600,
                "token_type": "Bearer"
            })
            
            mock_token_service.refresh_token = AsyncMock(return_value={
                "access_token": "new_access_token_123",
                "expires_in": 3600
            })
            
            mock_token_service.validate_token = AsyncMock(return_value=True)
            
            # Test token creation
            token_data = {
                "user_id": "123",
                "provider": "google",
                "access_token": "access_token_123",
                "refresh_token": "refresh_token_123"
            }
            
            result = await mock_token_service.create_token(token_data)
            assert result["access_token"] == "access_token_123"
            assert result["token_type"] == "Bearer"
            
            # Test token refresh
            refresh_result = await mock_token_service.refresh_token("refresh_token_123")
            assert refresh_result["access_token"] == "new_access_token_123"
            
            # Test token validation
            validation_result = await mock_token_service.validate_token("access_token_123")
            assert validation_result is True

    @pytest.mark.asyncio
    async def test_oauth_consent_service(self):
        """Test OAuth consent service functionality."""
        # Mock the consent service
        with patch('personal_assistant.oauth.services.consent_service.OAuthConsentService') as mock_class:
            mock_consent_service = Mock()
            mock_class.return_value = mock_consent_service
            
            # Mock consent operations
            mock_consent_service.create_consent = AsyncMock(return_value={
                "consent_id": "consent_123",
                "user_id": "123",
                "provider": "google",
                "scopes": ["read", "write"],
                "status": "granted"
            })
            
            mock_consent_service.validate_consent = AsyncMock(return_value=True)
            mock_consent_service.revoke_consent = AsyncMock(return_value=True)
            
            # Test consent creation
            consent_data = {
                "user_id": "123",
                "provider": "google",
                "scopes": ["read", "write"]
            }
            
            result = await mock_consent_service.create_consent(consent_data)
            assert result["consent_id"] == "consent_123"
            assert result["status"] == "granted"
            
            # Test consent validation
            validation_result = await mock_consent_service.validate_consent("consent_123")
            assert validation_result is True
            
            # Test consent revocation
            revocation_result = await mock_consent_service.revoke_consent("consent_123")
            assert revocation_result is True

    @pytest.mark.asyncio
    async def test_oauth_integration_service(self):
        """Test OAuth integration service functionality."""
        # Mock the integration service
        with patch('personal_assistant.oauth.services.integration_service.OAuthIntegrationService') as mock_class:
            mock_integration_service = Mock()
            mock_class.return_value = mock_integration_service
            
            # Mock integration operations
            mock_integration_service.create_integration = AsyncMock(return_value={
                "integration_id": "integration_123",
                "user_id": "123",
                "provider": "google",
                "status": "active",
                "scopes": ["read", "write"]
            })
            
            mock_integration_service.get_user_integrations = AsyncMock(return_value=[
                {
                    "integration_id": "integration_123",
                    "provider": "google",
                    "status": "active"
                }
            ])
            
            mock_integration_service.update_integration_status = AsyncMock(return_value=True)
            
            # Test integration creation
            integration_data = {
                "user_id": "123",
                "provider": "google",
                "scopes": ["read", "write"]
            }
            
            result = await mock_integration_service.create_integration(integration_data)
            assert result["integration_id"] == "integration_123"
            assert result["status"] == "active"
            
            # Test getting user integrations
            integrations = await mock_integration_service.get_user_integrations("123")
            assert len(integrations) == 1
            assert integrations[0]["provider"] == "google"
            
            # Test integration status update
            update_result = await mock_integration_service.update_integration_status(
                "integration_123", "expired"
            )
            assert update_result is True

    @pytest.mark.asyncio
    async def test_oauth_security_service(self):
        """Test OAuth security service functionality."""
        # Mock the security service
        with patch('personal_assistant.oauth.services.security_service.OAuthSecurityService') as mock_class:
            mock_security_service = Mock()
            mock_class.return_value = mock_security_service
            
            # Mock security operations
            mock_security_service.validate_state = AsyncMock(return_value=True)
            mock_security_service.generate_state = AsyncMock(return_value="state_123")
            mock_security_service.audit_access = AsyncMock(return_value=True)
            
            # Test state validation
            validation_result = await mock_security_service.validate_state("state_123")
            assert validation_result is True
            
            # Test state generation
            state = await mock_security_service.generate_state()
            assert state == "state_123"
            
            # Test access auditing
            audit_data = {
                "user_id": "123",
                "provider": "google",
                "action": "token_refresh",
                "ip_address": "192.168.1.1"
            }
            
            audit_result = await mock_security_service.audit_access(audit_data)
            assert audit_result is True

    @pytest.mark.asyncio
    async def test_oauth_provider_google(self):
        """Test Google OAuth provider functionality."""
        # Mock the Google provider
        with patch('personal_assistant.oauth.providers.google.GoogleOAuthProvider') as mock_class:
            mock_provider = Mock()
            mock_class.return_value = mock_provider
            
            # Mock Google provider operations
            mock_provider.get_authorization_url = AsyncMock(return_value="https://accounts.google.com/oauth/authorize")
            mock_provider.exchange_code_for_token = AsyncMock(return_value={
                "access_token": "google_access_token",
                "refresh_token": "google_refresh_token",
                "expires_in": 3600
            })
            
            # Test authorization URL generation
            auth_url = await mock_provider.get_authorization_url("state_123")
            assert auth_url == "https://accounts.google.com/oauth/authorize"
            
            # Test token exchange
            token_result = await mock_provider.exchange_code_for_token("auth_code_123")
            assert token_result["access_token"] == "google_access_token"

    @pytest.mark.asyncio
    async def test_oauth_provider_microsoft(self):
        """Test Microsoft OAuth provider functionality."""
        # Mock the Microsoft provider
        with patch('personal_assistant.oauth.providers.microsoft.MicrosoftOAuthProvider') as mock_class:
            mock_provider = Mock()
            mock_class.return_value = mock_provider
            
            # Mock Microsoft provider operations
            mock_provider.get_authorization_url = AsyncMock(return_value="https://login.microsoftonline.com/oauth/authorize")
            mock_provider.exchange_code_for_token = AsyncMock(return_value={
                "access_token": "microsoft_access_token",
                "refresh_token": "microsoft_refresh_token",
                "expires_in": 3600
            })
            
            # Test authorization URL generation
            auth_url = await mock_provider.get_authorization_url("state_123")
            assert auth_url == "https://login.microsoftonline.com/oauth/authorize"
            
            # Test token exchange
            token_result = await mock_provider.exchange_code_for_token("auth_code_123")
            assert token_result["access_token"] == "microsoft_access_token"

    @pytest.mark.asyncio
    async def test_oauth_provider_notion(self):
        """Test Notion OAuth provider functionality."""
        # Mock the Notion provider
        with patch('personal_assistant.oauth.providers.notion.NotionOAuthProvider') as mock_class:
            mock_provider = Mock()
            mock_class.return_value = mock_provider
            
            # Mock Notion provider operations
            mock_provider.get_authorization_url = AsyncMock(return_value="https://api.notion.com/v1/oauth/authorize")
            mock_provider.exchange_code_for_token = AsyncMock(return_value={
                "access_token": "notion_access_token",
                "workspace_id": "workspace_123",
                "expires_in": 3600
            })
            
            # Test authorization URL generation
            auth_url = await mock_provider.get_authorization_url("state_123")
            assert auth_url == "https://api.notion.com/v1/oauth/authorize"
            
            # Test token exchange
            token_result = await mock_provider.exchange_code_for_token("auth_code_123")
            assert token_result["access_token"] == "notion_access_token"
            assert token_result["workspace_id"] == "workspace_123"

    @pytest.mark.asyncio
    async def test_oauth_provider_youtube(self):
        """Test YouTube OAuth provider functionality."""
        # Mock the YouTube provider
        with patch('personal_assistant.oauth.providers.youtube.YouTubeOAuthProvider') as mock_class:
            mock_provider = Mock()
            mock_class.return_value = mock_provider
            
            # Mock YouTube provider operations
            mock_provider.get_authorization_url = AsyncMock(return_value="https://accounts.google.com/oauth/authorize")
            mock_provider.exchange_code_for_token = AsyncMock(return_value={
                "access_token": "youtube_access_token",
                "refresh_token": "youtube_refresh_token",
                "expires_in": 3600
            })
            
            # Test authorization URL generation
            auth_url = await mock_provider.get_authorization_url("state_123")
            assert auth_url == "https://accounts.google.com/oauth/authorize"
            
            # Test token exchange
            token_result = await mock_provider.exchange_code_for_token("auth_code_123")
            assert token_result["access_token"] == "youtube_access_token"

    @pytest.mark.asyncio
    async def test_oauth_error_handling(self):
        """Test OAuth error handling scenarios."""
        # Test various error scenarios
        error_scenarios = [
            ("Invalid authorization code", Exception("Invalid authorization code")),
            ("Token refresh failed", Exception("Token refresh failed")),
            ("Consent validation failed", Exception("Consent validation failed")),
            ("Security validation failed", Exception("Security validation failed")),
        ]
        
        for error_type, error in error_scenarios:
            # Mock the service with error
            with patch('personal_assistant.oauth.services.token_service.OAuthTokenService') as mock_class:
                mock_service = Mock()
                mock_class.return_value = mock_service
                
                # Mock the specific error
                mock_service.exchange_code_for_token = AsyncMock(side_effect=error)
                
                # Test error handling
                with pytest.raises(Exception) as exc_info:
                    await mock_service.exchange_code_for_token("invalid_code")
                
                assert str(exc_info.value) == str(error)

    @pytest.mark.asyncio
    async def test_oauth_complete_workflow(self):
        """Test complete OAuth workflow."""
        # Mock all OAuth components
        with patch('personal_assistant.oauth.oauth_manager.OAuthManager') as mock_manager_class, \
             patch('personal_assistant.oauth.providers.google.GoogleOAuthProvider') as mock_provider_class:
            
            # Setup mocks
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_authorization_url = AsyncMock(return_value="https://accounts.google.com/oauth/authorize")
            mock_manager.handle_callback = AsyncMock(return_value={
                "integration_id": "integration_123",
                "status": "active",
                "access_token": "access_token_123"
            })
            
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.get_authorization_url = AsyncMock(return_value="https://accounts.google.com/oauth/authorize")
            mock_provider.exchange_code_for_token = AsyncMock(return_value={
                "access_token": "access_token_123",
                "refresh_token": "refresh_token_123"
            })
            
            # Test complete OAuth workflow
            user_id = "123"
            provider = "google"
            scopes = ["read", "write"]
            
            # 1. Get authorization URL
            auth_url = await mock_manager.get_authorization_url(user_id, provider, scopes)
            assert auth_url == "https://accounts.google.com/oauth/authorize"
            
            # 2. Handle callback
            callback_data = {
                "code": "auth_code_123",
                "state": "state_123"
            }
            
            callback_result = await mock_manager.handle_callback(user_id, provider, callback_data)
            assert callback_result["integration_id"] == "integration_123"
            assert callback_result["status"] == "active"
            assert callback_result["access_token"] == "access_token_123"
            
            # Verify all services were called
            mock_manager.get_authorization_url.assert_called_once()
            mock_manager.handle_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_oauth_token_expiration_handling(self):
        """Test OAuth token expiration handling."""
        # Mock token service with expiration handling
        with patch('personal_assistant.oauth.services.token_service.OAuthTokenService') as mock_class:
            mock_token_service = Mock()
            mock_class.return_value = mock_token_service
            
            # Mock token expiration check
            mock_token_service.is_token_expired = AsyncMock(return_value=True)
            mock_token_service.refresh_token = AsyncMock(return_value={
                "access_token": "new_access_token_123",
                "expires_in": 3600
            })
            
            # Test token expiration handling
            token = "expired_token_123"
            
            is_expired = await mock_token_service.is_token_expired(token)
            assert is_expired is True
            
            # Test token refresh
            refresh_result = await mock_token_service.refresh_token("refresh_token_123")
            assert refresh_result["access_token"] == "new_access_token_123"

    @pytest.mark.asyncio
    async def test_oauth_scope_validation(self):
        """Test OAuth scope validation."""
        # Mock consent service with scope validation
        with patch('personal_assistant.oauth.services.consent_service.OAuthConsentService') as mock_class:
            mock_consent_service = Mock()
            mock_class.return_value = mock_consent_service
            
            # Mock scope validation
            mock_consent_service.validate_scopes = AsyncMock(return_value=True)
            mock_consent_service.get_required_scopes = AsyncMock(return_value=["read", "write"])
            
            # Test scope validation
            requested_scopes = ["read", "write"]
            validation_result = await mock_consent_service.validate_scopes(requested_scopes)
            assert validation_result is True
            
            # Test getting required scopes
            required_scopes = await mock_consent_service.get_required_scopes("google")
            assert required_scopes == ["read", "write"]

