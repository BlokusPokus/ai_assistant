"""
Unit tests for UserSpecificNotionPagesTool
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific import (
    UserSpecificNotionPagesTool
)
from src.personal_assistant.tools.notion_pages.client_factory import (
    NotionNotConnectedError,
    NotionWorkspaceError
)


class TestUserSpecificNotionPagesTool:
    """Test cases for UserSpecificNotionPagesTool"""

    @pytest.fixture
    def tool(self):
        """Create UserSpecificNotionPagesTool instance for testing"""
        return UserSpecificNotionPagesTool()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def mock_session_service(self):
        """Create mock session service"""
        service = Mock()
        service.get_current_user_id = AsyncMock(return_value=456)
        return service

    @pytest.mark.asyncio
    async def test_create_note_page_success(self, tool, mock_db, mock_session_service):
        """Test successful note page creation"""
        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch.object(tool.notion_internal, 'create_user_page', return_value="new_page_id"), \
             patch.object(tool, '_update_table_of_contents', return_value=None) as mock_update_toc, \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.ensure_user_main_page_exists', return_value="main_page_id"):

            result = await tool.create_note_page(
                title="Test Page",
                content="Test content",
                session_id="session123",
                db=mock_db
            )

            assert result["success"] is True
            assert result["page_id"] == "new_page_id"
            assert result["title"] == "Test Page"
            assert "created successfully" in result["message"]
            mock_update_toc.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_note_page_not_connected(self, tool, mock_db, mock_session_service):
        """Test note page creation when user not connected to Notion"""
        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.ensure_user_main_page_exists', 
                   side_effect=NotionNotConnectedError("Not connected")):

            result = await tool.create_note_page(
                title="Test Page",
                session_id="session123",
                db=mock_db
            )

            assert result["error"] == "User must connect Notion account first"

    @pytest.mark.asyncio
    async def test_create_note_page_invalid_session(self, tool, mock_db):
        """Test note page creation with invalid session"""
        mock_session_service = Mock()
        mock_session_service.get_current_user_id = AsyncMock(return_value=None)
        
        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service):

            result = await tool.create_note_page(
                title="Test Page",
                session_id="invalid_session",
                db=mock_db
            )

            assert result["error"] == "Invalid session or user not found"

    @pytest.mark.asyncio
    async def test_read_note_page_success(self, tool, mock_db, mock_session_service):
        """Test successful note page reading"""
        mock_client = Mock()
        mock_client.pages.retrieve.return_value = {
            "id": "page123",
            "properties": {
                "title": {
                    "title": [{"plain_text": "Test Page"}]
                }
            },
            "url": "https://notion.so/page123",
            "created_time": "2024-01-01T00:00:00Z",
            "last_edited_time": "2024-01-01T00:00:00Z"
        }
        mock_client.blocks.children.list.return_value = {
            "results": [{
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "Test content"}]
                }
            }]
        }

        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.get_user_notion_client', return_value=mock_client):

            result = await tool.read_note_page(
                page_id="page123",
                session_id="session123",
                db=mock_db
            )

            assert result["success"] is True
            assert result["page_id"] == "page123"
            assert result["title"] == "Test Page"
            assert result["content"] == "Test content"

    @pytest.mark.asyncio
    async def test_update_note_page_success(self, tool, mock_db, mock_session_service):
        """Test successful note page update"""
        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch.object(tool.notion_internal, 'update_user_page', return_value=True), \
             patch.object(tool, '_update_table_of_contents', return_value=None) as mock_update_toc:

            result = await tool.update_note_page(
                page_id="page123",
                title="Updated Title",
                content="Updated content",
                session_id="session123",
                db=mock_db
            )

            assert result["success"] is True
            assert "updated successfully" in result["message"]
            mock_update_toc.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_note_page_success(self, tool, mock_db, mock_session_service):
        """Test successful note page deletion"""
        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch.object(tool.notion_internal, 'delete_user_page', return_value=True), \
             patch.object(tool, '_update_table_of_contents', return_value=None) as mock_update_toc:

            result = await tool.delete_note_page(
                page_id="page123",
                session_id="session123",
                db=mock_db
            )

            assert result["success"] is True
            assert "deleted successfully" in result["message"]
            mock_update_toc.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_note_pages_success(self, tool, mock_db, mock_session_service):
        """Test successful note pages search"""
        mock_pages = [
            {"id": "page1", "title": "Page 1", "url": "https://notion.so/page1"},
            {"id": "page2", "title": "Page 2", "url": "https://notion.so/page2"}
        ]

        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch.object(tool.notion_internal, 'search_user_pages', return_value=mock_pages):

            result = await tool.search_note_pages(
                query="test",
                session_id="session123",
                db=mock_db
            )

            assert result["success"] is True
            assert result["pages"] == mock_pages
            assert result["count"] == 2
            assert result["query"] == "test"

    @pytest.mark.asyncio
    async def test_get_table_of_contents_success(self, tool, mock_db, mock_session_service):
        """Test successful table of contents retrieval"""
        mock_pages = [
            {"id": "page1", "title": "Page 1", "url": "https://notion.so/page1"},
            {"id": "page2", "title": "Page 2", "url": "https://notion.so/page2"}
        ]

        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.ensure_user_main_page_exists', return_value="main_page_id"), \
             patch.object(tool.notion_internal, 'search_user_pages', return_value=mock_pages):

            result = await tool.get_table_of_contents(
                session_id="session123",
                db=mock_db
            )

            assert result["success"] is True
            assert result["main_page_id"] == "main_page_id"
            assert result["pages"] == mock_pages
            assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_get_table_of_contents_filters_main_page(self, tool, mock_db, mock_session_service):
        """Test that table of contents filters out the main page"""
        mock_pages = [
            {"id": "main_page_id", "title": "Personal Assistant", "url": "https://notion.so/main"},
            {"id": "page1", "title": "Page 1", "url": "https://notion.so/page1"},
            {"id": "page2", "title": "Page 2", "url": "https://notion.so/page2"}
        ]

        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.ensure_user_main_page_exists', return_value="main_page_id"), \
             patch.object(tool.notion_internal, 'search_user_pages', return_value=mock_pages):

            result = await tool.get_table_of_contents(
                session_id="session123",
                db=mock_db
            )

            assert result["success"] is True
            assert result["count"] == 2
            assert all(page["id"] != "main_page_id" for page in result["pages"])

    @pytest.mark.asyncio
    async def test_workspace_error_handling(self, tool, mock_db, mock_session_service):
        """Test workspace error handling"""
        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.ensure_user_main_page_exists', 
                   side_effect=NotionWorkspaceError("Workspace error")):

            result = await tool.create_note_page(
                title="Test Page",
                session_id="session123",
                db=mock_db
            )

            assert result["error"] == "Notion workspace error: Workspace error"

    @pytest.mark.asyncio
    async def test_no_database_session(self, tool):
        """Test error when no database session provided"""
        result = await tool.create_note_page(
            title="Test Page",
            session_id="session123",
            db=None
        )

        assert result["error"] == "Database session required"

    @pytest.mark.asyncio
    async def test_update_table_of_contents(self, tool, mock_db, mock_session_service):
        """Test table of contents update"""
        mock_client = Mock()
        mock_client.blocks.children.list.return_value = {
            "results": [{
                "id": "block1",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "Table of Contents"}]
                }
            }]
        }
        mock_client.blocks.delete.return_value = None
        mock_client.blocks.children.append.return_value = None

        mock_pages = [
            {"id": "page1", "title": "Page 1", "url": "https://notion.so/page1"},
            {"id": "page2", "title": "Page 2", "url": "https://notion.so/page2"}
        ]

        with patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.SessionService', return_value=mock_session_service), \
             patch.object(tool.notion_internal, 'search_user_pages', return_value=mock_pages), \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.ensure_user_main_page_exists', return_value="main_page_id"), \
             patch('src.personal_assistant.tools.notion_pages.notion_pages_tool_user_specific.get_user_notion_client', return_value=mock_client):

            await tool._update_table_of_contents(mock_db, 456, "session123")

            # Verify blocks were deleted and new content was added
            mock_client.blocks.delete.assert_called_once()
            mock_client.blocks.children.append.assert_called_once()
