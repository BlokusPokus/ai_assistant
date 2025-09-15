"""
OAuth Token Service Tests

This module tests the OAuthTokenService implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.models.token import OAuthToken
from personal_assistant.oauth.exceptions import OAuthTokenError


class TestOAuthTokenService:
    """Test cases for OAuthTokenService."""

    @pytest.fixture
    def token_service(self):
        """Provide an OAuthTokenService instance for testing."""
        return OAuthTokenService()

    @pytest.fixture
    def mock_db_session(self):
        """Provide a mock database session for testing."""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.fixture
    def mock_token_data(self):
        """Provide mock token data for testing."""
        return {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_456",
            "expires_in": 3600,
            "token_type": "Bearer",
            "scope": "read write"
        }

    def test_encrypt_token_success(self, token_service):
        """Test successful token encryption."""
        plain_token = "test_token_123"
        
        encrypted_token = token_service.encrypt_token(plain_token)
        
        assert isinstance(encrypted_token, str)
        assert encrypted_token != plain_token
        assert len(encrypted_token) > len(plain_token)

    def test_decrypt_token_success(self, token_service):
        """Test successful token decryption."""
        plain_token = "test_token_123"
        encrypted_token = token_service.encrypt_token(plain_token)
        
        decrypted_token = token_service.decrypt_token(encrypted_token)
        
        assert decrypted_token == plain_token

    def test_encrypt_token_error(self, token_service):
        """Test token encryption with invalid input."""
        with pytest.raises(OAuthTokenError) as exc_info:
            token_service.encrypt_token(None)
        
        assert "Failed to encrypt token" in str(exc_info.value)

    def test_decrypt_token_error(self, token_service):
        """Test token decryption with invalid input."""
        with pytest.raises(OAuthTokenError) as exc_info:
            token_service.decrypt_token("invalid_encrypted_token")
        
        assert "Failed to decrypt token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_store_tokens_success(self, token_service, mock_db_session, mock_token_data):
        """Test successful token storage."""
        integration_id = 1
        
        # Mock the database result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        # Mock the OAuthToken model
        with patch('personal_assistant.oauth.services.token_service.OAuthToken') as mock_token_model:
            mock_token_instance = Mock()
            mock_token_model.return_value = mock_token_instance
            
            tokens = await token_service.store_tokens(
                mock_db_session, integration_id, mock_token_data
            )
            
            assert isinstance(tokens, list)
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_tokens_error(self, token_service, mock_db_session, mock_token_data):
        """Test token storage with database error."""
        integration_id = 1
        
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Database error")
        
        with pytest.raises(OAuthTokenError) as exc_info:
            await token_service.store_tokens(
                mock_db_session, integration_id, mock_token_data
            )
        
        assert "Failed to store tokens" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_valid_token_success(self, token_service, mock_db_session):
        """Test successful token retrieval."""
        integration_id = 1
        token_type = "access_token"
        
        # Mock valid token
        mock_token = Mock()
        mock_token.expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_token.access_token = "valid_token_123"
        
        # Mock database result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_token]
        mock_db_session.execute.return_value = mock_result
        
        token = await token_service.get_valid_token(
            mock_db_session, integration_id, token_type
        )
        
        assert token == mock_token

    @pytest.mark.asyncio
    async def test_get_valid_token_expired(self, token_service, mock_db_session):
        """Test token retrieval with expired token."""
        integration_id = 1
        token_type = "access_token"
        
        # Mock expired token
        mock_token = Mock()
        mock_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        
        # Mock database result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_token]
        mock_db_session.execute.return_value = mock_result
        
        token = await token_service.get_valid_token(
            mock_db_session, integration_id, token_type
        )
        
        assert token is None

    @pytest.mark.asyncio
    async def test_get_valid_token_not_found(self, token_service, mock_db_session):
        """Test token retrieval when no token exists."""
        integration_id = 1
        token_type = "access_token"
        
        # Mock empty result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        token = await token_service.get_valid_token(
            mock_db_session, integration_id, token_type
        )
        
        assert token is None

    @pytest.mark.asyncio
    async def test_get_valid_token_error(self, token_service, mock_db_session):
        """Test token retrieval with database error."""
        integration_id = 1
        token_type = "access_token"
        
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Database error")
        
        with pytest.raises(OAuthTokenError) as exc_info:
            await token_service.get_valid_token(
                mock_db_session, integration_id, token_type
            )
        
        assert "Failed to retrieve token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, token_service, mock_db_session):
        """Test successful token refresh."""
        integration_id = 1
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.refresh_access_token.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        
        # Mock refresh token retrieval
        mock_refresh_token = Mock()
        mock_refresh_token.refresh_token = "old_refresh_token"
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_refresh_token]
        mock_db_session.execute.return_value = mock_result
        
        # Mock token storage
        with patch.object(token_service, 'store_tokens') as mock_store:
            mock_store.return_value = []
            
            new_token = await token_service.refresh_access_token(
                mock_db_session, integration_id, mock_provider
            )
            
            assert new_token == "new_access_token"
            mock_provider.refresh_access_token.assert_called_once_with("old_refresh_token")

    @pytest.mark.asyncio
    async def test_refresh_access_token_no_refresh_token(self, token_service, mock_db_session):
        """Test token refresh when no refresh token exists."""
        integration_id = 1
        
        # Mock empty result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        mock_provider = Mock()
        
        new_token = await token_service.refresh_access_token(
            mock_db_session, integration_id, mock_provider
        )
        
        assert new_token is None
        mock_provider.refresh_access_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_access_token_provider_error(self, token_service, mock_db_session):
        """Test token refresh with provider error."""
        integration_id = 1
        
        # Mock refresh token
        mock_refresh_token = Mock()
        mock_refresh_token.refresh_token = "old_refresh_token"
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_refresh_token]
        mock_db_session.execute.return_value = mock_result
        
        # Mock provider error
        mock_provider = Mock()
        mock_provider.refresh_access_token.side_effect = Exception("Provider error")
        
        new_token = await token_service.refresh_access_token(
            mock_db_session, integration_id, mock_provider
        )
        
        assert new_token is None

    @pytest.mark.asyncio
    async def test_revoke_tokens_success(self, token_service, mock_db_session):
        """Test successful token revocation."""
        integration_id = 1
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.revoke_token.return_value = True
        
        # Mock token retrieval
        mock_token = Mock()
        mock_token.access_token = "access_token_123"
        mock_token.refresh_token = "refresh_token_456"
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_token]
        mock_db_session.execute.return_value = mock_result
        
        success = await token_service.revoke_tokens(
            mock_db_session, integration_id, mock_provider
        )
        
        assert success is True
        mock_provider.revoke_token.assert_called()

    @pytest.mark.asyncio
    async def test_revoke_tokens_no_tokens(self, token_service, mock_db_session):
        """Test token revocation when no tokens exist."""
        integration_id = 1
        
        # Mock empty result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        mock_provider = Mock()
        
        success = await token_service.revoke_tokens(
            mock_db_session, integration_id, mock_provider
        )
        
        assert success is True
        mock_provider.revoke_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_revoke_tokens_error(self, token_service, mock_db_session):
        """Test token revocation with error."""
        integration_id = 1
        
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Database error")
        
        mock_provider = Mock()
        
        with pytest.raises(OAuthTokenError) as exc_info:
            await token_service.revoke_tokens(
                mock_db_session, integration_id, mock_provider
            )
        
        assert "Failed to revoke tokens" in str(exc_info.value)
