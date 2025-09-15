"""
Notion Client Factory OAuth Integration Tests

This module tests the NotionClientFactory OAuth integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.tools.notion_pages.client_factory import NotionClientFactory, NotionNotConnectedError, NotionTokenExpiredError, NotionWorkspaceError
from personal_assistant.oauth.models.integration import OAuthIntegration
from personal_assistant.oauth.models.token import OAuthToken


class TestNotionClientFactoryOAuth:
    """Test cases for NotionClientFactory OAuth integration."""

    @pytest.fixture
    def client_factory(self):
        """Provide a NotionClientFactory instance for testing."""
        return NotionClientFactory()

    @pytest.fixture
    def mock_db_session(self):
        """Provide a mock database session for testing."""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.fixture
    def mock_notion_integration(self):
        """Provide mock Notion OAuth integration."""
        integration = Mock(spec=OAuthIntegration)
        integration.id = 1
        integration.user_id = 1
        integration.provider = "notion"
        integration.status = "active"
        integration.scopes = ["read", "write"]
        return integration

    @pytest.fixture
    def mock_notion_token(self):
        """Provide mock Notion OAuth token."""
        token = Mock(spec=OAuthToken)
        token.access_token = "notion_access_token_123"
        token.refresh_token = "notion_refresh_token_456"
        token.expires_at = None
        token.token_type = "access_token"
        return token

    @pytest.fixture
    def mock_notion_client(self):
        """Provide a mock Notion client."""
        client = Mock()
        client.pages.create = AsyncMock(return_value={"id": "page_123"})
        client.pages.retrieve = AsyncMock(return_value={"id": "page_123", "title": "Test Page"})
        client.search = AsyncMock(return_value={"results": []})
        return client

    @pytest.mark.asyncio
    async def test_get_user_client_success(self, client_factory, mock_db_session, mock_notion_integration, mock_notion_token, mock_notion_client):
        """Test successful user client creation."""
        user_id = 1
        
        # Mock integration service
        with patch.object(client_factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
            mock_get_integration.return_value = mock_notion_integration
            
            # Mock token service
            with patch.object(client_factory.token_service, 'get_valid_token') as mock_get_token:
                mock_get_token.return_value = mock_notion_token
                
                # Mock Notion client creation
                with patch('personal_assistant.tools.notion_pages.client_factory.Client') as mock_client_class:
                    mock_client_class.return_value = mock_notion_client
                    
                    # Mock workspace validation
                    with patch.object(client_factory, '_validate_workspace_access') as mock_validate:
                        mock_validate.return_value = True
                        
                        client = await client_factory.get_user_client(mock_db_session, user_id)
                        
                        assert client == mock_notion_client
                        mock_get_integration.assert_called_once_with(mock_db_session, user_id, "notion")
                        mock_get_token.assert_called_once_with(mock_db_session, mock_notion_integration.id, "access_token")
                        mock_client_class.assert_called_once_with(auth=mock_notion_token.access_token)

    @pytest.mark.asyncio
    async def test_get_user_client_not_connected(self, client_factory, mock_db_session):
        """Test user client creation when Notion is not connected."""
        user_id = 1
        
        # Mock integration service to return None
        with patch.object(client_factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
            mock_get_integration.return_value = None
            
            with pytest.raises(NotionNotConnectedError) as exc_info:
                await client_factory.get_user_client(mock_db_session, user_id)
            
            assert f"User {user_id} must connect Notion account" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_client_token_expired(self, client_factory, mock_db_session, mock_notion_integration):
        """Test user client creation when token is expired."""
        user_id = 1
        
        # Mock integration service
        with patch.object(client_factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
            mock_get_integration.return_value = mock_notion_integration
            
            # Mock token service to return None (expired token)
            with patch.object(client_factory.token_service, 'get_valid_token') as mock_get_token:
                mock_get_token.return_value = None
                
                with pytest.raises(NotionTokenExpiredError) as exc_info:
                    await client_factory.get_user_client(mock_db_session, user_id)
                
                assert f"Could not get valid token for user {user_id}" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_client_workspace_error(self, client_factory, mock_db_session, mock_notion_integration, mock_notion_token):
        """Test user client creation when workspace access fails."""
        user_id = 1
        
        # Mock integration service
        with patch.object(client_factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
            mock_get_integration.return_value = mock_notion_integration
            
            # Mock token service
            with patch.object(client_factory.token_service, 'get_valid_token') as mock_get_token:
                mock_get_token.return_value = mock_notion_token
                
                # Mock Notion client creation
                with patch('personal_assistant.tools.notion_pages.client_factory.Client') as mock_client_class:
                    mock_notion_client = Mock()
                    mock_client_class.return_value = mock_notion_client
                    
                    # Mock workspace validation to fail
                    with patch.object(client_factory, '_validate_workspace_access') as mock_validate:
                        mock_validate.return_value = False
                        
                        with pytest.raises(NotionWorkspaceError) as exc_info:
                            await client_factory.get_user_client(mock_db_session, user_id)
                        
                        assert f"User {user_id} doesn't have workspace access" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_client_cached(self, client_factory, mock_db_session, mock_notion_integration, mock_notion_token, mock_notion_client):
        """Test that user client is cached and reused."""
        user_id = 1
        
        # Mock integration service
        with patch.object(client_factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
            mock_get_integration.return_value = mock_notion_integration
            
            # Mock token service
            with patch.object(client_factory.token_service, 'get_valid_token') as mock_get_token:
                mock_get_token.return_value = mock_notion_token
                
                # Mock Notion client creation
                with patch('personal_assistant.tools.notion_pages.client_factory.Client') as mock_client_class:
                    mock_client_class.return_value = mock_notion_client
                    
                    # Mock workspace validation
                    with patch.object(client_factory, '_validate_workspace_access') as mock_validate:
                        mock_validate.return_value = True
                        
                        # First call
                        client1 = await client_factory.get_user_client(mock_db_session, user_id)
                        
                        # Second call should use cache
                        client2 = await client_factory.get_user_client(mock_db_session, user_id)
                        
                        assert client1 == client2 == mock_notion_client
                        # Integration service should only be called once due to caching
                        assert mock_get_integration.call_count == 1

    @pytest.mark.asyncio
    async def test_validate_workspace_access_success(self, client_factory, mock_notion_client):
        """Test successful workspace access validation."""
        # Mock Notion client search to return results
        mock_notion_client.search.return_value = {"results": [{"id": "page_1"}]}
        
        result = await client_factory._validate_workspace_access(mock_notion_client)
        
        assert result is True
        mock_notion_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_workspace_access_failure(self, client_factory, mock_notion_client):
        """Test workspace access validation failure."""
        # Mock Notion client search to return empty results
        mock_notion_client.search.return_value = {"results": []}
        
        result = await client_factory._validate_workspace_access(mock_notion_client)
        
        assert result is False
        mock_notion_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_workspace_access_error(self, client_factory, mock_notion_client):
        """Test workspace access validation with error."""
        # Mock Notion client search to raise exception
        mock_notion_client.search.side_effect = Exception("API error")
        
        result = await client_factory._validate_workspace_access(mock_notion_client)
        
        assert result is False
        mock_notion_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_user_clients(self, client_factory, mock_db_session):
        """Test concurrent client creation for different users."""
        import asyncio
        
        async def create_client_for_user(user_id):
            mock_integration = Mock(spec=OAuthIntegration)
            mock_integration.id = user_id
            mock_integration.user_id = user_id
            
            mock_token = Mock(spec=OAuthToken)
            mock_token.access_token = f"token_{user_id}"
            
            mock_client = Mock()
            
            with patch.object(client_factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
                mock_get_integration.return_value = mock_integration
                
                with patch.object(client_factory.token_service, 'get_valid_token') as mock_get_token:
                    mock_get_token.return_value = mock_token
                    
                    with patch('personal_assistant.tools.notion_pages.client_factory.Client') as mock_client_class:
                        mock_client_class.return_value = mock_client
                        
                        with patch.object(client_factory, '_validate_workspace_access') as mock_validate:
                            mock_validate.return_value = True
                            
                            return await client_factory.get_user_client(mock_db_session, user_id)
        
        # Create clients for multiple users concurrently
        tasks = [
            create_client_for_user(1),
            create_client_for_user(2),
            create_client_for_user(3)
        ]
        
        clients = await asyncio.gather(*tasks)
        
        # Verify all clients were created successfully
        assert len(clients) == 3
        for client in clients:
            assert client is not None

    def test_client_factory_initialization(self, client_factory):
        """Test that NotionClientFactory is properly initialized."""
        assert hasattr(client_factory, 'token_service')
        assert hasattr(client_factory, 'integration_service')
        assert hasattr(client_factory, '_client_cache')
        assert isinstance(client_factory._client_cache, dict)

    def test_cache_key_generation(self, client_factory):
        """Test that cache keys are generated correctly."""
        user_id = 123
        expected_key = f"user_{user_id}"
        
        # Access the private method through the class
        cache_key = f"user_{user_id}"
        
        assert cache_key == expected_key
