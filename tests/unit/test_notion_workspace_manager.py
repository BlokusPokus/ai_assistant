"""
Unit tests for NotionWorkspaceManager
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from notion_client import Client

from src.personal_assistant.tools.notion_pages.workspace_manager import (
    NotionWorkspaceManager,
    NotionPageCreationError
)
from src.personal_assistant.tools.notion_pages.client_factory import (
    NotionNotConnectedError,
    NotionWorkspaceError
)


class TestNotionWorkspaceManager:
    """Test cases for NotionWorkspaceManager"""

    @pytest.fixture
    def manager(self):
        """Create NotionWorkspaceManager instance for testing"""
        return NotionWorkspaceManager()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock()

    @pytest.fixture
    def mock_client(self):
        """Create mock Notion client"""
        client = Mock()
        client.search = Mock()
        client.pages = Mock()
        client.pages.create = Mock()
        return client

    @pytest.mark.asyncio
    async def test_ensure_user_root_page_existing_page(self, manager, mock_db, mock_client):
        """Test when user already has a Personal Assistant page"""
        with patch.object(manager.client_factory, 'get_user_client', return_value=mock_client), \
             patch.object(manager, 'find_user_root_page', return_value="existing_page_id"):

            result = await manager.ensure_user_root_page(mock_db, 456)

            assert result == "existing_page_id"
            manager.client_factory.get_user_client.assert_called_once_with(mock_db, 456, None)

    @pytest.mark.asyncio
    async def test_ensure_user_root_page_create_new(self, manager, mock_db, mock_client):
        """Test creating new Personal Assistant page"""
        with patch.object(manager.client_factory, 'get_user_client', return_value=mock_client), \
             patch.object(manager, 'find_user_root_page', return_value=None), \
             patch.object(manager, 'create_user_root_page', return_value="new_page_id"):

            result = await manager.ensure_user_root_page(mock_db, 456)

            assert result == "new_page_id"
            manager.create_user_root_page.assert_called_once_with(mock_client, 456)

    @pytest.mark.asyncio
    async def test_ensure_user_root_page_not_connected(self, manager, mock_db):
        """Test error when user hasn't connected Notion"""
        with patch.object(manager.client_factory, 'get_user_client', 
                         side_effect=NotionNotConnectedError("Not connected")):
            with pytest.raises(NotionNotConnectedError):
                await manager.ensure_user_root_page(mock_db, 456)

    @pytest.mark.asyncio
    async def test_create_user_root_page_success(self, manager, mock_client):
        """Test successful page creation"""
        # Mock workspace root discovery
        with patch.object(manager, '_get_workspace_root', return_value="workspace_root_id"):
            # Mock page creation
            mock_page_response = {"id": "new_page_id"}
            mock_client.pages.create.return_value = mock_page_response

            result = await manager.create_user_root_page(mock_client, 456)

            assert result == "new_page_id"
            mock_client.pages.create.assert_called_once()
            
            # Verify page creation parameters
            call_args = mock_client.pages.create.call_args
            assert call_args[1]["parent"]["page_id"] == "workspace_root_id"
            assert call_args[1]["properties"]["title"][0]["text"]["content"] == "Personal Assistant"

    @pytest.mark.asyncio
    async def test_create_user_root_page_failure(self, manager, mock_client):
        """Test page creation failure"""
        with patch.object(manager, '_get_workspace_root', return_value="workspace_root_id"), \
             patch.object(mock_client.pages, 'create', side_effect=Exception("API Error")):
            
            with pytest.raises(NotionPageCreationError, match="Failed to create Personal Assistant page"):
                await manager.create_user_root_page(mock_client, 456)

    @pytest.mark.asyncio
    async def test_find_user_root_page_success(self, manager, mock_client):
        """Test finding existing Personal Assistant page"""
        mock_search_response = {
            "results": [
                {
                    "id": "page1",
                    "archived": False,
                    "properties": {
                        "title": {
                            "title": [{"plain_text": "Personal Assistant"}]
                        }
                    }
                },
                {
                    "id": "page2",
                    "archived": False,
                    "properties": {
                        "title": {
                            "title": [{"plain_text": "Other Page"}]
                        }
                    }
                }
            ]
        }
        mock_client.search.return_value = mock_search_response

        result = await manager.find_user_root_page(mock_client, 456)

        assert result == "page1"
        mock_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_user_root_page_not_found(self, manager, mock_client):
        """Test when Personal Assistant page is not found"""
        mock_client.search.return_value = {"results": []}

        result = await manager.find_user_root_page(mock_client, 456)

        assert result is None

    @pytest.mark.asyncio
    async def test_find_user_root_page_archived(self, manager, mock_client):
        """Test when Personal Assistant page is archived"""
        mock_search_response = {
            "results": [
                {
                    "id": "page1",
                    "archived": True,
                    "properties": {
                        "title": {
                            "title": [{"plain_text": "Personal Assistant"}]
                        }
                    }
                }
            ]
        }
        mock_client.search.return_value = mock_search_response

        result = await manager.find_user_root_page(mock_client, 456)

        assert result is None

    @pytest.mark.asyncio
    async def test_find_user_root_page_error(self, manager, mock_client):
        """Test error during page search"""
        mock_client.search.side_effect = Exception("Search error")

        result = await manager.find_user_root_page(mock_client, 456)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_workspace_root_success(self, manager, mock_client):
        """Test successful workspace root discovery"""
        mock_search_response = {
            "results": [{"id": "workspace_root_id"}]
        }
        mock_client.search.return_value = mock_search_response

        result = await manager._get_workspace_root(mock_client)

        assert result == "workspace_root_id"
        mock_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_workspace_root_no_pages(self, manager, mock_client):
        """Test when no pages are found in workspace"""
        mock_client.search.return_value = {"results": []}

        with pytest.raises(NotionWorkspaceError, match="No accessible pages found in workspace"):
            await manager._get_workspace_root(mock_client)

    @pytest.mark.asyncio
    async def test_get_workspace_root_error(self, manager, mock_client):
        """Test error during workspace root discovery"""
        mock_client.search.side_effect = Exception("API Error")

        with pytest.raises(NotionWorkspaceError, match="Failed to access workspace"):
            await manager._get_workspace_root(mock_client)

    @pytest.mark.asyncio
    async def test_validate_user_workspace_success(self, manager, mock_client):
        """Test successful workspace validation"""
        mock_client.search.return_value = {"results": [{"id": "test_page"}]}

        result = await manager.validate_user_workspace(mock_client, 456)

        assert result is True
        mock_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_user_workspace_failure(self, manager, mock_client):
        """Test failed workspace validation"""
        mock_client.search.side_effect = Exception("API Error")

        result = await manager.validate_user_workspace(mock_client, 456)

        assert result is False

    def test_invalidate_user_cache(self, manager):
        """Test user cache invalidation"""
        with patch.object(manager.client_factory, 'invalidate_user_client') as mock_invalidate:
            manager.invalidate_user_cache(456)
            mock_invalidate.assert_called_once_with(456)
