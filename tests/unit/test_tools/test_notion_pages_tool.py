"""
Unit tests for Notion Pages Tool.

This module tests the Notion Pages tool functionality including
page creation, reading, updating, deletion, search, table of contents,
linking, and backlinks.
"""

import pytest
from unittest.mock import patch, MagicMock

from personal_assistant.tools.notion_pages.notion_pages_tool import NotionPagesTool


@pytest.fixture(autouse=True)
def mock_notion_client():
    """Mock Notion client to avoid API key validation in tests."""
    with patch('personal_assistant.tools.notion_pages.notion_internal.get_notion_client') as mock_get_client, \
         patch('personal_assistant.tools.notion_pages.notion_pages_tool.get_notion_client') as mock_get_client_2, \
         patch('personal_assistant.config.settings.settings.NOTION_API_KEY', 'test-api-key'):
        
        # Create a mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_get_client_2.return_value = mock_client
        
        yield mock_client


class TestNotionPagesTool:
    """Test cases for Notion Pages Tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.notion_tool = NotionPagesTool()
        self.test_page_id = "12345678-1234-1234-1234-123456789012"
        self.test_title = "Test Note"
        self.test_content = "This is test content for the note."
        self.test_tags = "test,example,notes"
        self.test_category = "Testing"

    def test_notion_tool_initialization(self):
        """Test Notion Pages tool initialization."""
        assert self.notion_tool is not None
        assert hasattr(self.notion_tool, 'create_note_page_tool')
        assert hasattr(self.notion_tool, 'read_note_page_tool')
        assert hasattr(self.notion_tool, 'update_note_page_tool')
        assert hasattr(self.notion_tool, 'delete_note_page_tool')
        assert hasattr(self.notion_tool, 'search_notes_tool')
        assert hasattr(self.notion_tool, 'get_table_of_contents_tool')
        assert hasattr(self.notion_tool, 'create_link_tool')
        assert hasattr(self.notion_tool, 'get_backlinks_tool')
        assert self.notion_tool.main_page_id is None

    def test_notion_tool_iteration(self):
        """Test that Notion Pages tool is iterable and returns all tools."""
        tools = list(self.notion_tool)
        assert len(tools) == 8
        
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "create_note_page",
            "read_note_page",
            "update_note_page",
            "delete_note_page",
            "search_notes",
            "get_table_of_contents",
            "create_link",
            "get_backlinks"
        ]
        
        for expected_name in expected_names:
            assert expected_name in tool_names

    def test_create_note_page_tool_properties(self):
        """Test create note page tool properties."""
        tool = self.notion_tool.create_note_page_tool
        assert tool.name == "create_note_page"
        assert "Create a new note page" in tool.description
        assert "title" in tool.parameters
        assert "content" in tool.parameters
        assert "tags" in tool.parameters
        assert "category" in tool.parameters

    def test_read_note_page_tool_properties(self):
        """Test read note page tool properties."""
        tool = self.notion_tool.read_note_page_tool
        assert tool.name == "read_note_page"
        assert "Read note content and properties" in tool.description
        assert "page_identifier" in tool.parameters

    def test_update_note_page_tool_properties(self):
        """Test update note page tool properties."""
        tool = self.notion_tool.update_note_page_tool
        assert tool.name == "update_note_page"
        assert "Update note content and properties" in tool.description
        assert "page_id" in tool.parameters
        assert "content" in tool.parameters
        assert "title" in tool.parameters
        assert "tags" in tool.parameters
        assert "category" in tool.parameters

    def test_delete_note_page_tool_properties(self):
        """Test delete note page tool properties."""
        tool = self.notion_tool.delete_note_page_tool
        assert tool.name == "delete_note_page"
        assert "Delete a note page by page ID" in tool.description
        assert "page_id" in tool.parameters

    def test_search_notes_tool_properties(self):
        """Test search notes tool properties."""
        tool = self.notion_tool.search_notes_tool
        assert tool.name == "search_notes"
        assert "Search across all note pages" in tool.description
        assert "query" in tool.parameters
        assert "category" in tool.parameters
        assert "tags" in tool.parameters

    def test_get_table_of_contents_tool_properties(self):
        """Test get table of contents tool properties."""
        tool = self.notion_tool.get_table_of_contents_tool
        assert tool.name == "get_table_of_contents"
        assert "Get the current table of contents" in tool.description
        assert tool.parameters == {}

    def test_create_link_tool_properties(self):
        """Test create link tool properties."""
        tool = self.notion_tool.create_link_tool
        assert tool.name == "create_link"
        assert "Create a link between two pages" in tool.description
        assert "source_page_id" in tool.parameters
        assert "target_page_title" in tool.parameters

    def test_get_backlinks_tool_properties(self):
        """Test get backlinks tool properties."""
        tool = self.notion_tool.get_backlinks_tool
        assert tool.name == "get_backlinks"
        assert "Get all pages that link to the specified page" in tool.description
        assert "page_id" in tool.parameters

    @pytest.mark.asyncio
    async def test_create_note_page_empty_title(self):
        """Test create note page with empty title."""
        result = await self.notion_tool.create_note_page("", self.test_content)
        
        # Check if result is a dict (error response) or string
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "Title is required" in result.get("error_message", "")
        else:
            assert "Error" in result or "Title is required" in result

    @pytest.mark.asyncio
    async def test_create_note_page_empty_content(self):
        """Test create note page with empty content."""
        result = await self.notion_tool.create_note_page(self.test_title, "")
        
        # Check if result is a dict (error response) or string
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "Content is required" in result.get("error_message", "")
        else:
            assert "Error" in result or "Content is required" in result

    @pytest.mark.asyncio
    async def test_create_note_page_success(self):
        """Test successful note page creation."""
        mock_page = {"id": self.test_page_id}
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.create_properties_dict') as mock_props, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_props.return_value = {"title": {"title": [{"text": {"content": self.test_title}}]}}
            mock_client.pages.create.return_value = mock_page
            
            result = await self.notion_tool.create_note_page(
                self.test_title,
                self.test_content,
                self.test_tags,
                self.test_category
            )
            
            assert "Successfully created note page" in result
            assert self.test_title in result
            assert self.test_page_id in result

    @pytest.mark.asyncio
    async def test_create_note_page_exception(self):
        """Test create note page with exception."""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure:
            mock_ensure.side_effect = Exception("Notion API error")
            
            result = await self.notion_tool.create_note_page(
                self.test_title,
                self.test_content
            )
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_read_note_page_by_id(self):
        """Test reading note page by page ID."""
        mock_page = {
            "id": self.test_page_id,
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]},
                "tags": {"multi_select": [{"name": "test"}]},
                "category": {"select": {"name": self.test_category}}
            }
        }
        
        mock_blocks = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": self.test_content}]}
                }
            ]
        }
        
        with patch.object(self.notion_tool, 'client') as mock_client, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties') as mock_extract:
            
            mock_client.pages.retrieve.return_value = mock_page
            mock_client.blocks.children.list.return_value = mock_blocks
            mock_extract.return_value = (self.test_title, self.test_category, ["test"])
            
            result = await self.notion_tool.read_note_page(self.test_page_id)
            
            assert self.test_title in result
            assert self.test_content in result
            assert self.test_page_id in result

    @pytest.mark.asyncio
    async def test_read_note_page_by_title(self):
        """Test reading note page by title."""
        mock_search_response = {
            "results": [
                {
                    "id": self.test_page_id,
                    "properties": {
                        "title": {"title": [{"plain_text": self.test_title}]}
                    }
                }
            ]
        }
        
        mock_page = {
            "id": self.test_page_id,
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        mock_blocks = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": self.test_content}]}
                }
            ]
        }
        
        with patch.object(self.notion_tool, 'client') as mock_client, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties') as mock_extract:
            
            mock_client.search.return_value = mock_search_response
            mock_client.pages.retrieve.return_value = mock_page
            mock_client.blocks.children.list.return_value = mock_blocks
            mock_extract.return_value = (self.test_title, [], None)
            
            result = await self.notion_tool.read_note_page(self.test_title)
            
            assert self.test_title in result
            assert self.test_content in result

    @pytest.mark.asyncio
    async def test_read_note_page_not_found(self):
        """Test reading note page that doesn't exist."""
        mock_search_response = {"results": []}
        
        with patch.object(self.notion_tool, 'client') as mock_client:
            mock_client.search.return_value = mock_search_response
            
            result = await self.notion_tool.read_note_page("Non-existent Page")
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
                assert "not found" in result.get("error_message", "").lower()
            else:
                assert "Error" in result or "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_update_note_page_success(self):
        """Test successful note page update."""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.create_properties_dict') as mock_props, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_props.return_value = {"title": {"title": [{"text": {"content": "New Title"}}]}}
            mock_client.pages.update.return_value = {}
            mock_client.blocks.children.list.return_value = {"results": []}
            mock_client.blocks.delete.return_value = {}
            mock_client.blocks.children.append.return_value = {}
            
            result = await self.notion_tool.update_note_page(
                self.test_page_id,
                content="New content",
                title="New Title",
                tags="new,updated",
                category="Updated"
            )
            
            assert "Successfully updated note page" in result
            assert self.test_page_id in result

    @pytest.mark.asyncio
    async def test_update_note_page_exception(self):
        """Test update note page with exception."""
        with patch.object(self.notion_tool, 'client') as mock_client:
            # Mock the blocks.children.append to raise an exception when updating content
            mock_client.blocks.children.append.side_effect = Exception("Update failed")
            
            result = await self.notion_tool.update_note_page(
                self.test_page_id,
                content="New content"
            )
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_delete_note_page_success(self):
        """Test successful note page deletion."""
        mock_page = {
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        with patch.object(self.notion_tool, 'client') as mock_client:
            mock_client.pages.retrieve.return_value = mock_page
            mock_client.pages.update.return_value = {}
            
            result = await self.notion_tool.delete_note_page(self.test_page_id)
            
            assert "Successfully deleted note page" in result
            assert self.test_title in result

    @pytest.mark.asyncio
    async def test_delete_note_page_exception(self):
        """Test delete note page with exception."""
        with patch.object(self.notion_tool, 'client') as mock_client:
            mock_client.pages.retrieve.side_effect = Exception("Delete failed")
            
            result = await self.notion_tool.delete_note_page(self.test_page_id)
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_search_notes_success(self):
        """Test successful note search."""
        mock_main_page_blocks = {
            "results": [
                {
                    "type": "child_page",
                    "id": self.test_page_id
                }
            ]
        }
        
        mock_page = {
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        mock_page_blocks = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": self.test_content}]}
                }
            ]
        }
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties') as mock_extract, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_extract.return_value = (self.test_title, [], None)
            mock_client.blocks.children.list.side_effect = [mock_main_page_blocks, mock_page_blocks]
            mock_client.pages.retrieve.return_value = mock_page
            
            result = await self.notion_tool.search_notes("test")
            
            assert "Search results" in result
            assert self.test_title in result

    @pytest.mark.asyncio
    async def test_search_notes_no_results(self):
        """Test note search with no results."""
        mock_main_page_blocks = {"results": []}
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_client.blocks.children.list.return_value = mock_main_page_blocks
            
            result = await self.notion_tool.search_notes("nonexistent")
            
            assert "No notes found" in result

    @pytest.mark.asyncio
    async def test_get_table_of_contents_success(self):
        """Test successful table of contents retrieval."""
        mock_main_page_blocks = {
            "results": [
                {
                    "type": "child_page",
                    "id": self.test_page_id
                }
            ]
        }
        
        mock_page = {
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties') as mock_extract, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_extract.return_value = (self.test_title, [], None)
            mock_client.blocks.children.list.return_value = mock_main_page_blocks
            mock_client.pages.retrieve.return_value = mock_page
            
            result = await self.notion_tool.get_table_of_contents()
            
            assert "Table of Contents" in result
            assert self.test_title in result

    @pytest.mark.asyncio
    async def test_get_table_of_contents_empty(self):
        """Test table of contents when empty."""
        mock_main_page_blocks = {"results": []}
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_client.blocks.children.list.return_value = mock_main_page_blocks
            
            result = await self.notion_tool.get_table_of_contents()
            
            assert "Table of contents is empty" in result

    @pytest.mark.asyncio
    async def test_create_link_success(self):
        """Test successful link creation."""
        mock_search_response = {
            "results": [
                {
                    "id": "target_page_id",
                    "properties": {
                        "title": {"title": [{"plain_text": "Target Page"}]}
                    }
                }
            ]
        }
        
        with patch.object(self.notion_tool, 'client') as mock_client:
            mock_client.search.return_value = mock_search_response
            mock_client.blocks.children.append.return_value = {}
            
            result = await self.notion_tool.create_link(
                self.test_page_id,
                "Target Page"
            )
            
            assert "Successfully created link" in result
            assert "Target Page" in result

    @pytest.mark.asyncio
    async def test_create_link_target_not_found(self):
        """Test link creation when target page not found."""
        mock_search_response = {"results": []}
        
        with patch.object(self.notion_tool, 'client') as mock_client:
            mock_client.search.return_value = mock_search_response
            
            result = await self.notion_tool.create_link(
                self.test_page_id,
                "Non-existent Page"
            )
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
                assert "not found" in result.get("error_message", "").lower()
            else:
                assert "Error" in result or "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_get_backlinks_success(self):
        """Test successful backlinks retrieval."""
        mock_page = {
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        mock_main_page_blocks = {
            "results": [
                {
                    "type": "child_page",
                    "id": "other_page_id"
                }
            ]
        }
        
        mock_other_page_blocks = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": f"Link to [[{self.test_title}]]"}]}
                }
            ]
        }
        
        mock_other_page = {
            "properties": {
                "title": {"title": [{"plain_text": "Other Page"}]}
            }
        }
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_client.pages.retrieve.side_effect = [mock_page, mock_other_page]
            mock_client.blocks.children.list.side_effect = [mock_main_page_blocks, mock_other_page_blocks]
            
            result = await self.notion_tool.get_backlinks(self.test_page_id)
            
            assert "Backlinks to" in result
            assert self.test_title in result
            assert "Other Page" in result

    @pytest.mark.asyncio
    async def test_get_backlinks_no_backlinks(self):
        """Test backlinks when none exist."""
        mock_page = {
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        mock_main_page_blocks = {"results": []}
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_client.pages.retrieve.return_value = mock_page
            mock_client.blocks.children.list.return_value = mock_main_page_blocks
            
            result = await self.notion_tool.get_backlinks(self.test_page_id)
            
            assert "No backlinks found" in result
            assert self.test_title in result

    def test_tool_parameter_validation(self):
        """Test that tool parameters are properly defined."""
        # Test create_note_page_tool parameters
        create_params = self.notion_tool.create_note_page_tool.parameters
        assert create_params["title"]["type"] == "string"
        assert create_params["content"]["type"] == "string"
        assert create_params["tags"]["type"] == "string"
        assert create_params["category"]["type"] == "string"
        
        # Test read_note_page_tool parameters
        read_params = self.notion_tool.read_note_page_tool.parameters
        assert read_params["page_identifier"]["type"] == "string"
        
        # Test update_note_page_tool parameters
        update_params = self.notion_tool.update_note_page_tool.parameters
        assert update_params["page_id"]["type"] == "string"
        assert update_params["content"]["type"] == "string"
        assert update_params["title"]["type"] == "string"
        assert update_params["tags"]["type"] == "string"
        assert update_params["category"]["type"] == "string"

    def test_tool_descriptions(self):
        """Test that tool descriptions are informative."""
        # Test that descriptions contain key information
        assert "note page" in self.notion_tool.create_note_page_tool.description
        assert "Read note content" in self.notion_tool.read_note_page_tool.description
        assert "Update note content" in self.notion_tool.update_note_page_tool.description
        assert "Delete a note page" in self.notion_tool.delete_note_page_tool.description
        assert "Search across all note pages" in self.notion_tool.search_notes_tool.description
        assert "table of contents" in self.notion_tool.get_table_of_contents_tool.description
        assert "link between two pages" in self.notion_tool.create_link_tool.description
        assert "pages that link to" in self.notion_tool.get_backlinks_tool.description

    def test_tool_categories(self):
        """Test that tools can have categories set."""
        tool = self.notion_tool.create_note_page_tool
        tool.set_category("NotionPages")
        assert tool.category == "NotionPages"
        
        # Test that category is returned correctly
        assert tool.category == "NotionPages"

    def test_tool_user_intent_tracking(self):
        """Test that tools can track user intent."""
        tool = self.notion_tool.create_note_page_tool
        
        # Test setting user intent
        tool.set_user_intent("Create a new note")
        assert tool.get_user_intent() == "Create a new note"
        
        # Test default user intent
        new_tool = NotionPagesTool().create_note_page_tool
        assert new_tool.get_user_intent() == "Unknown user intent"

    @pytest.mark.asyncio
    async def test_create_note_page_with_optional_params(self):
        """Test create note page with optional parameters."""
        mock_page = {"id": self.test_page_id}
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.create_properties_dict') as mock_props, \
             patch.object(self.notion_tool, 'client') as mock_client:
            
            mock_ensure.return_value = "main_page_id"
            mock_props.return_value = {"title": {"title": [{"text": {"content": self.test_title}}]}}
            mock_client.pages.create.return_value = mock_page
            
            result = await self.notion_tool.create_note_page(
                self.test_title,
                self.test_content,
                tags=self.test_tags,
                category=self.test_category
            )
            
            assert "Successfully created note page" in result
            # Verify that create_properties_dict was called with the right parameters
            mock_props.assert_called_once_with(self.test_title, self.test_tags, self.test_category)

    @pytest.mark.asyncio
    async def test_search_notes_with_filters(self):
        """Test note search with category and tag filters."""
        mock_main_page_blocks = {
            "results": [
                {
                    "type": "child_page",
                    "id": self.test_page_id
                }
            ]
        }
        
        mock_page = {
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists') as mock_ensure, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties') as mock_extract, \
             patch.object(self.notion_tool, 'client') as mock_client:

            mock_ensure.return_value = "main_page_id"
            mock_extract.return_value = (self.test_title, ["test"], self.test_category)
            mock_client.blocks.children.list.return_value = mock_main_page_blocks
            mock_client.pages.retrieve.return_value = mock_page
            
            result = await self.notion_tool.search_notes(
                "test",
                category=self.test_category,
                tags="test,example"
            )
            
            assert "Search results for 'test':" in result
            # Verify that extract_page_properties was called
            mock_extract.assert_called()

    @pytest.mark.asyncio
    async def test_read_note_page_different_block_types(self):
        """Test reading note page with different block types."""
        mock_page = {
            "id": self.test_page_id,
            "properties": {
                "title": {"title": [{"plain_text": self.test_title}]}
            }
        }
        
        mock_blocks = {
            "results": [
                {
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"plain_text": "Main Heading"}]}
                },
                {
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"plain_text": "Sub Heading"}]}
                },
                {
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"plain_text": "List item"}]}
                }
            ]
        }
        
        with patch.object(self.notion_tool, 'client') as mock_client, \
             patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties') as mock_extract:
            
            mock_client.pages.retrieve.return_value = mock_page
            mock_client.blocks.children.list.return_value = mock_blocks
            mock_extract.return_value = (self.test_title, [], None)
            
            result = await self.notion_tool.read_note_page(self.test_page_id)
            
            assert self.test_title in result
            assert "# Main Heading" in result
            assert "## Sub Heading" in result
            assert "- List item" in result
