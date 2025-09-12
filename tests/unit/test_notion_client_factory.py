"""
Unit tests for NotionClientFactory
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from notion_client import Client

from src.personal_assistant.tools.notion_pages.client_factory import (
    NotionClientFactory,
    NotionNotConnectedError,
    NotionTokenExpiredError,
    NotionWorkspaceError
)


class TestNotionClientFactory:
    """Test cases for NotionClientFactory"""

    @pytest.fixture
    def factory(self):
        """Create NotionClientFactory instance for testing"""
        return NotionClientFactory()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock()

    @pytest.fixture
    def mock_integration(self):
        """Create mock OAuth integration"""
        integration = Mock()
        integration.id = 123
        integration.provider = "notion"
        integration.user_id = 456
        return integration

    @pytest.mark.asyncio
    async def test_get_user_client_success(self, factory, mock_db, mock_integration):
        """Test successful client creation"""
        # Mock OAuth services
        with patch.object(factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration, \
             patch.object(factory.token_service, 'get_valid_token') as mock_get_token, \
             patch.object(factory, '_validate_workspace_access', return_value=True) as mock_validate, \
             patch('src.personal_assistant.tools.notion_pages.client_factory.Client') as mock_client_class:

            # Setup mocks
            mock_get_integration.return_value = mock_integration
            mock_get_token.return_value = "test_access_token"
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Test
            result = await factory.get_user_client(mock_db, 456)

            # Assertions
            assert result == mock_client
            mock_get_integration.assert_called_once_with(mock_db, 456, "notion")
            mock_get_token.assert_called_once_with(mock_db, 123)
            mock_validate.assert_called_once_with(mock_client)
            mock_client_class.assert_called_once_with(auth="test_access_token")

    @pytest.mark.asyncio
    async def test_get_user_client_not_connected(self, factory, mock_db):
        """Test error when user hasn't connected Notion"""
        with patch.object(factory.integration_service, 'get_integration_by_user_and_provider', return_value=None):
            with pytest.raises(NotionNotConnectedError, match="User 456 must connect Notion account"):
                await factory.get_user_client(mock_db, 456)

    @pytest.mark.asyncio
    async def test_get_user_client_token_expired(self, factory, mock_db, mock_integration):
        """Test error when token is expired"""
        with patch.object(factory.integration_service, 'get_integration_by_user_and_provider', return_value=mock_integration), \
             patch.object(factory.token_service, 'get_valid_token', return_value=None):
            with pytest.raises(NotionTokenExpiredError, match="Could not get valid token for user 456"):
                await factory.get_user_client(mock_db, 456)

    @pytest.mark.asyncio
    async def test_get_user_client_workspace_error(self, factory, mock_db, mock_integration):
        """Test error when workspace is not accessible"""
        with patch.object(factory.integration_service, 'get_integration_by_user_and_provider', return_value=mock_integration), \
             patch.object(factory.token_service, 'get_valid_token', return_value="test_token"), \
             patch.object(factory, '_validate_workspace_access', return_value=False), \
             patch('notion_client.Client'):
            with pytest.raises(NotionWorkspaceError, match="User 456 doesn't have workspace access"):
                await factory.get_user_client(mock_db, 456)

    @pytest.mark.asyncio
    async def test_get_user_client_caching(self, factory, mock_db, mock_integration):
        """Test client caching functionality"""
        with patch.object(factory.integration_service, 'get_integration_by_user_and_provider', return_value=mock_integration), \
             patch.object(factory.token_service, 'get_valid_token', return_value="test_token"), \
             patch.object(factory, '_validate_workspace_access', return_value=True), \
             patch('src.personal_assistant.tools.notion_pages.client_factory.Client') as mock_client_class:

            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # First call
            result1 = await factory.get_user_client(mock_db, 456)
            
            # Second call should use cache
            result2 = await factory.get_user_client(mock_db, 456)

            # Assertions
            assert result1 == result2 == mock_client
            assert mock_client_class.call_count == 1  # Only called once due to caching

    @pytest.mark.asyncio
    async def test_validate_workspace_access_success(self, factory):
        """Test successful workspace validation"""
        mock_client = Mock()
        mock_client.search.return_value = {"results": [{"id": "test_page"}]}

        result = await factory._validate_workspace_access(mock_client)

        assert result is True
        mock_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_workspace_access_failure(self, factory):
        """Test failed workspace validation"""
        mock_client = Mock()
        mock_client.search.side_effect = Exception("API Error")

        result = await factory._validate_workspace_access(mock_client)

        assert result is False

    def test_invalidate_user_client(self, factory):
        """Test client cache invalidation"""
        # Add client to cache
        factory._client_cache["user_456"] = Mock()
        
        # Invalidate
        factory.invalidate_user_client(456)
        
        # Check cache is empty
        assert "user_456" not in factory._client_cache

    def test_clear_cache(self, factory):
        """Test cache clearing"""
        # Add clients to cache
        factory._client_cache["user_456"] = Mock()
        factory._client_cache["user_789"] = Mock()
        
        # Clear cache
        factory.clear_cache()
        
        # Check cache is empty
        assert len(factory._client_cache) == 0

    @pytest.mark.asyncio
    async def test_get_user_id_from_session_success(self, factory):
        """Test successful user ID retrieval from session"""
        mock_session_service = Mock()
        mock_session_service.get_current_user_id = AsyncMock(return_value=456)

        result = await factory.get_user_id_from_session(mock_session_service, "session123")

        assert result == 456
        mock_session_service.get_current_user_id.assert_called_once_with("session123")

    @pytest.mark.asyncio
    async def test_get_user_id_from_session_failure(self, factory):
        """Test failed user ID retrieval from session"""
        mock_session_service = Mock()
        mock_session_service.get_current_user_id = AsyncMock(side_effect=Exception("Session error"))

        result = await factory.get_user_id_from_session(mock_session_service, "session123")

        assert result is None
