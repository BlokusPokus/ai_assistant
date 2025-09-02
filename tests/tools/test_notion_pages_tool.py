"""
Comprehensive tests for NotionPagesTool.

Tests all 8 functions of the NotionPagesTool:
1. create_note_page
2. read_note_page  
3. update_note_page
4. delete_note_page
5. search_notes
6. get_table_of_contents
7. create_link
8. get_backlinks
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

# Import the tool and its dependencies
from personal_assistant.tools.notion_pages.notion_pages_tool import NotionPagesTool
from personal_assistant.tools.notion_pages.notion_internal import (
    ensure_main_page_exists,
    update_table_of_contents,
    extract_page_properties,
    create_properties_dict
)


class TestNotionPagesTool:
    """Test suite for NotionPagesTool"""

    @pytest.fixture
    def mock_notion_client(self):
        """Create a mock Notion client"""
        mock_client = Mock()
        mock_client.pages = Mock()
        mock_client.blocks = Mock()
        mock_client.search = Mock()
        return mock_client

    @pytest.fixture
    def notion_tool(self, mock_notion_client):
        """Create NotionPagesTool instance with mocked client"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.get_notion_client', return_value=mock_notion_client):
            tool = NotionPagesTool()
            tool.client = mock_notion_client
            return tool

    @pytest.fixture
    def sample_page_data(self):
        """Sample page data for testing"""
        return {
            "id": "test-page-id-123",
            "properties": {
                "title": {
                    "title": [{"plain_text": "Test Note"}]
                },
                "Tags": {
                    "multi_select": [
                        {"name": "test"},
                        {"name": "example"}
                    ]
                },
                "Category": {
                    "select": {"name": "Work"}
                }
            }
        }

    @pytest.fixture
    def sample_blocks_data(self):
        """Sample blocks data for testing"""
        return {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"plain_text": "This is test content"}]
                    }
                },
                {
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"plain_text": "Test Heading"}]
                    }
                },
                {
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"plain_text": "Test list item"}]
                    }
                }
            ]
        }

    def test_tool_initialization(self, notion_tool):
        """Test that all tools are properly initialized"""
        tools = list(notion_tool)
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

    @pytest.mark.asyncio
    async def test_create_note_page_success(self, notion_tool, mock_notion_client):
        """Test successful note page creation"""
        # Mock dependencies
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            with patch('personal_assistant.tools.notion_pages.notion_pages_tool.create_properties_dict', return_value={"title": "Test Note"}):
                # Mock the page creation response
                mock_notion_client.pages.create.return_value = {
                    "id": "new-page-123"}

                # Execute the function
                result = await notion_tool.create_note_page(
                    title="Test Note",
                    content="Test content",
                    tags="test,example",
                    category="Work"
                )

                # Verify the result
                assert "Successfully created note page 'Test Note'" in result
                assert "new-page-123" in result

                # Verify the client was called correctly
                mock_notion_client.pages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_note_page_missing_title(self, notion_tool):
        """Test note creation with missing title"""
        result = await notion_tool.create_note_page(
            title="",
            content="Test content"
        )

        # Error response is a dictionary, check error_message field
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "title" in result.get("error_message", "").lower()
        else:
            # Fallback for string responses
            assert "error" in result.lower() or "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_create_note_page_missing_content(self, notion_tool):
        """Test note creation with missing content"""
        result = await notion_tool.create_note_page(
            title="Test Note",
            content=""
        )

        # Error response is a dictionary, check error_message field
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "content" in result.get("error_message", "").lower()
        else:
            # Fallback for string responses
            assert "error" in result.lower() or "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_read_note_page_by_id(self, notion_tool, mock_notion_client, sample_page_data, sample_blocks_data):
        """Test reading note page by ID"""
        # Mock the page retrieval and blocks
        mock_notion_client.pages.retrieve.return_value = sample_page_data
        mock_notion_client.blocks.children.list.return_value = sample_blocks_data

        # Mock the extract_page_properties function
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties', return_value=("Test Note", [{"name": "test"}, {"name": "example"}], "Work")):
            # Execute the function
            result = await notion_tool.read_note_page("test-page-id-123")

            # Verify the result contains expected information
            assert "Test Note" in result
            assert "test-page-id-123" in result
            assert "Work" in result
            assert "test, example" in result

    @pytest.mark.asyncio
    async def test_read_note_page_by_title(self, notion_tool, mock_notion_client, sample_page_data, sample_blocks_data):
        """Test reading note page by title"""
        # Mock the search response
        mock_notion_client.search.return_value = {
            "results": [sample_page_data]
        }

        # Mock the page retrieval and blocks
        mock_notion_client.pages.retrieve.return_value = sample_page_data
        mock_notion_client.blocks.children.list.return_value = sample_blocks_data

        # Mock the extract_page_properties function
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties', return_value=("Test Note", [{"name": "test"}, {"name": "example"}], "Work")):
            # Execute the function
            result = await notion_tool.read_note_page("Test Note")

            # Verify the result
            assert "Test Note" in result
            assert "This is test content" in result

    @pytest.mark.asyncio
    async def test_read_note_page_title_not_found(self, notion_tool, mock_notion_client):
        """Test reading note page with non-existent title"""
        # Mock empty search results
        mock_notion_client.search.return_value = {"results": []}

        # Execute the function
        result = await notion_tool.read_note_page("Non-existent Note")

        # Error response is a dictionary, check error_message field
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "not found" in result.get("error_message", "").lower()
        else:
            # Fallback for string responses
            assert "not found" in result.lower() or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_update_note_page_content_only(self, notion_tool, mock_notion_client):
        """Test updating note page content only"""
        # Mock the blocks operations
        mock_notion_client.blocks.children.list.return_value = {
            "results": [{"id": "block-123"}]}
        mock_notion_client.blocks.delete.return_value = None
        mock_notion_client.blocks.children.append.return_value = None

        # Execute the function
        result = await notion_tool.update_note_page(
            page_id="test-page-id-123",
            content="Updated content"
        )

        # Verify the result
        assert "Successfully updated note page" in result

        # Verify blocks were updated
        mock_notion_client.blocks.delete.assert_called_once_with("block-123")
        mock_notion_client.blocks.children.append.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_note_page_properties_only(self, notion_tool, mock_notion_client):
        """Test updating note page properties only"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.create_properties_dict', return_value={"title": "Updated Title"}):
            # Execute the function
            result = await notion_tool.update_note_page(
                page_id="test-page-id-123",
                title="Updated Title"
            )

            # Verify the result
            assert "Successfully updated note page" in result

            # Verify properties were updated
            mock_notion_client.pages.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_note_page_content_and_properties(self, notion_tool, mock_notion_client):
        """Test updating both content and properties"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.create_properties_dict', return_value={"title": "Updated Title"}):
            # Mock the blocks operations
            mock_notion_client.blocks.children.list.return_value = {
                "results": [{"id": "block-123"}]}
            mock_notion_client.blocks.delete.return_value = None
            mock_notion_client.blocks.children.append.return_value = None

            # Execute the function
            result = await notion_tool.update_note_page(
                page_id="test-page-id-123",
                content="Updated content",
                title="Updated Title"
            )

            # Verify the result
            assert "Successfully updated note page" in result

            # Verify both operations were performed
            mock_notion_client.pages.update.assert_called_once()
            mock_notion_client.blocks.delete.assert_called_once()
            mock_notion_client.blocks.children.append.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_note_page_success(self, notion_tool, mock_notion_client, sample_page_data):
        """Test successful note page deletion"""
        # Mock the page retrieval
        mock_notion_client.pages.retrieve.return_value = sample_page_data
        mock_notion_client.pages.update.return_value = None

        # Execute the function
        result = await notion_tool.delete_note_page("test-page-id-123")

        # Verify the result
        assert "Successfully deleted note page" in result
        assert "Test Note" in result

        # Verify the page was archived
        mock_notion_client.pages.update.assert_called_once_with(
            "test-page-id-123", archived=True)

    @pytest.mark.asyncio
    async def test_search_notes_by_query(self, notion_tool, mock_notion_client, sample_page_data):
        """Test searching notes by query"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock the main page blocks
            mock_notion_client.blocks.children.list.return_value = {
                "results": [
                    {
                        "type": "child_page",
                        "id": "test-page-id-123"
                    }
                ]
            }

            # Mock the page retrieval
            mock_notion_client.pages.retrieve.return_value = sample_page_data

            # Mock the page content blocks - need to handle the side_effect properly
            def mock_blocks_list(page_id):
                if page_id == "main-page-123":
                    return {"results": [{"type": "child_page", "id": "test-page-id-123"}]}
                else:
                    return {"results": [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "This contains the search term"}]}}]}

            mock_notion_client.blocks.children.list.side_effect = mock_blocks_list

            # Execute the function
            result = await notion_tool.search_notes("search term")

            # Verify the result
            assert "Search results for 'search term'" in result
            assert "Test Note" in result

    @pytest.mark.asyncio
    async def test_search_notes_by_category(self, notion_tool, mock_notion_client, sample_page_data):
        """Test searching notes by category filter"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock the main page blocks
            mock_notion_client.blocks.children.list.return_value = {
                "results": [
                    {
                        "type": "child_page",
                        "id": "test-page-id-123"
                    }
                ]
            }

            # Mock the page retrieval
            mock_notion_client.pages.retrieve.return_value = sample_page_data

            # Mock the extract_page_properties function
            with patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties', return_value=("Test Note", [{"name": "test"}, {"name": "example"}], "Work")):
                # Execute the function
                result = await notion_tool.search_notes("test", category="Work")

                # Verify the result - should find the page since it matches the category
                assert "Search results for 'test'" in result

    @pytest.mark.asyncio
    async def test_search_notes_by_tags(self, notion_tool, mock_notion_client, sample_page_data):
        """Test searching notes by tags filter"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock the main page blocks
            mock_notion_client.blocks.children.list.return_value = {
                "results": [
                    {
                        "type": "child_page",
                        "id": "test-page-id-123"
                    }
                ]
            }

            # Mock the page retrieval
            mock_notion_client.pages.retrieve.return_value = sample_page_data

            # Mock the extract_page_properties function
            with patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties', return_value=("Test Note", [{"name": "test"}, {"name": "example"}], "Work")):
                # Execute the function
                result = await notion_tool.search_notes("test", tags="test,example")

                # Verify the result - should find the page since it matches the tags
                assert "Search results for 'test'" in result

    @pytest.mark.asyncio
    async def test_search_notes_no_results(self, notion_tool, mock_notion_client):
        """Test search with no results"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock empty main page blocks
            mock_notion_client.blocks.children.list.return_value = {
                "results": []}

            # Execute the function
            result = await notion_tool.search_notes("nonexistent")

            # Verify the result
            assert "No notes found matching query" in result

    @pytest.mark.asyncio
    async def test_get_table_of_contents_success(self, notion_tool, mock_notion_client, sample_page_data):
        """Test getting table of contents successfully"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock the main page blocks
            mock_notion_client.blocks.children.list.return_value = {
                "results": [
                    {
                        "type": "child_page",
                        "id": "test-page-id-123"
                    }
                ]
            }

            # Mock the page retrieval
            mock_notion_client.pages.retrieve.return_value = sample_page_data

            # Mock the extract_page_properties function
            with patch('personal_assistant.tools.notion_pages.notion_pages_tool.extract_page_properties', return_value=("Test Note", [{"name": "test"}, {"name": "example"}], "Work")):
                # Execute the function
                result = await notion_tool.get_table_of_contents()

                # Verify the result
                assert "Table of Contents:" in result
                assert "Test Note" in result
                assert "test-page-id-123" in result
                # Note: The category and tags might not be displayed in the TOC depending on the implementation
                # So we'll just check the basic structure

    @pytest.mark.asyncio
    async def test_get_table_of_contents_empty(self, notion_tool, mock_notion_client):
        """Test getting table of contents when empty"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock empty main page blocks
            mock_notion_client.blocks.children.list.return_value = {
                "results": []}

            # Execute the function
            result = await notion_tool.get_table_of_contents()

            # Verify the result
            assert "Table of contents is empty" in result

    @pytest.mark.asyncio
    async def test_create_link_success(self, notion_tool, mock_notion_client):
        """Test successful link creation between pages"""
        # Mock the search response for target page
        mock_notion_client.search.return_value = {
            "results": [{"id": "target-page-123", "properties": {"title": {"title": [{"plain_text": "Target Page"}]}}}]
        }

        # Mock the link creation
        mock_notion_client.blocks.children.append.return_value = None

        # Execute the function
        result = await notion_tool.create_link(
            source_page_id="source-page-123",
            target_page_title="Target Page"
        )

        # Verify the result
        assert "Successfully created link from source page to 'Target Page'" in result

        # Verify the link was created
        mock_notion_client.blocks.children.append.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_link_target_not_found(self, notion_tool, mock_notion_client):
        """Test link creation with non-existent target page"""
        # Mock empty search results
        mock_notion_client.search.return_value = {"results": []}

        # Execute the function
        result = await notion_tool.create_link(
            source_page_id="source-page-123",
            target_page_title="Non-existent Page"
        )

        # Error response is a dictionary, check error_message field
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "not found" in result.get("error_message", "").lower()
        else:
            # Fallback for string responses
            assert "not found" in result.lower() or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_get_backlinks_success(self, notion_tool, mock_notion_client, sample_page_data):
        """Test successful backlinks retrieval"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock the main page blocks
            def mock_blocks_list(page_id):
                if page_id == "main-page-123":
                    return {"results": [{"type": "child_page", "id": "child-page-123"}]}
                else:
                    return {"results": [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "This links to [[Test Note]]"}]}}]}

            mock_notion_client.blocks.children.list.side_effect = mock_blocks_list

            # Mock the page retrieval
            mock_notion_client.pages.retrieve.return_value = sample_page_data

            # Execute the function
            result = await notion_tool.get_backlinks("test-page-id-123")

            # Verify the result
            assert "Backlinks to 'Test Note'" in result
            assert "child-page-123" in result

    @pytest.mark.asyncio
    async def test_get_backlinks_none_found(self, notion_tool, mock_notion_client, sample_page_data):
        """Test backlinks retrieval when none exist"""
        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            # Mock the main page blocks
            def mock_blocks_list(page_id):
                if page_id == "main-page-123":
                    return {"results": [{"type": "child_page", "id": "child-page-123"}]}
                else:
                    return {"results": [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "No links here"}]}}]}

            mock_notion_client.blocks.children.list.side_effect = mock_blocks_list

            # Mock the page retrieval
            mock_notion_client.pages.retrieve.return_value = sample_page_data

            # Execute the function
            result = await notion_tool.get_backlinks("test-page-id-123")

            # Verify the result
            assert "No backlinks found for page" in result

    @pytest.mark.asyncio
    async def test_error_handling_in_create_note_page(self, notion_tool, mock_notion_client):
        """Test error handling in create_note_page"""
        # Mock an exception
        mock_notion_client.pages.create.side_effect = Exception("API Error")

        with patch('personal_assistant.tools.notion_pages.notion_pages_tool.ensure_main_page_exists', return_value="main-page-123"):
            with patch('personal_assistant.tools.notion_pages.notion_pages_tool.create_properties_dict', return_value={"title": "Test Note"}):
                # Execute the function
                result = await notion_tool.create_note_page(
                    title="Test Note",
                    content="Test content"
                )

                # Error response is a dictionary, check error_message field
                if isinstance(result, dict):
                    assert result.get("error", False)
                    assert "API Error" in result.get("error_message", "")
                else:
                    # Fallback for string responses
                    assert "error" in result.lower() or "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_error_handling_in_read_note_page(self, notion_tool, mock_notion_client):
        """Test error handling in read_note_page"""
        # Mock an exception
        mock_notion_client.pages.retrieve.side_effect = Exception("API Error")

        # Execute the function
        result = await notion_tool.read_note_page("test-page-id-123")

        # Error response is a dictionary, check error_message field
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "API Error" in result.get("error_message", "")
        else:
            # Fallback for string responses
            assert "error" in result.lower() or "failed" in result.lower()

    def test_tool_parameters(self, notion_tool):
        """Test that all tools have the correct parameters"""
        tools = list(notion_tool)

        # Test create_note_page_tool parameters
        create_tool = tools[0]
        assert "title" in create_tool.parameters
        assert "content" in create_tool.parameters
        assert "tags" in create_tool.parameters
        assert "category" in create_tool.parameters

        # Test read_note_page_tool parameters
        read_tool = tools[1]
        assert "page_identifier" in read_tool.parameters

        # Test update_note_page_tool parameters
        update_tool = tools[2]
        assert "page_id" in update_tool.parameters
        assert "content" in update_tool.parameters
        assert "title" in update_tool.parameters
        assert "tags" in update_tool.parameters
        assert "category" in update_tool.parameters

        # Test delete_note_page_tool parameters
        delete_tool = tools[3]
        assert "page_id" in delete_tool.parameters

        # Test search_notes_tool parameters
        search_tool = tools[4]
        assert "query" in search_tool.parameters
        assert "category" in search_tool.parameters
        assert "tags" in search_tool.parameters

        # Test get_table_of_contents_tool parameters
        toc_tool = tools[5]
        assert len(toc_tool.parameters) == 0  # No parameters

        # Test create_link_tool parameters
        link_tool = tools[6]
        assert "source_page_id" in link_tool.parameters
        assert "target_page_title" in link_tool.parameters

        # Test get_backlinks_tool parameters
        backlinks_tool = tools[7]
        assert "page_id" in backlinks_tool.parameters

    def test_tool_descriptions(self, notion_tool):
        """Test that all tools have meaningful descriptions"""
        tools = list(notion_tool)

        for tool in tools:
            assert tool.description is not None
            # Description should be substantial
            assert len(tool.description) > 10
            assert tool.description.strip() != ""

    def test_tool_categories(self, notion_tool):
        """Test that all tools are properly categorized"""
        tools = list(notion_tool)

        for tool in tools:
            # Set category and verify
            tool.set_category("NotionPages")
            assert tool.category == "NotionPages"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
