"""
Test User-Specific Notion Isolation

This test verifies that:
1. Users can only access their own Notion workspaces
2. Notes created by one user are not visible to other users
3. The EnhancedNotesTool properly uses user-specific Notion clients
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool
from src.personal_assistant.tools.notion_pages.notion_internal_user_specific import UserSpecificNotionInternal
from src.personal_assistant.tools.notion_pages.client_factory import NotionClientFactory
from src.personal_assistant.tools.notion_pages.workspace_manager import NotionWorkspaceManager


class TestUserSpecificNotionIsolation:
    """Test suite for user-specific Notion isolation"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def enhanced_notes_tool(self):
        """Create EnhancedNotesTool instance"""
        return EnhancedNotesTool()

    @pytest.fixture
    def user_specific_notion_internal(self):
        """Create UserSpecificNotionInternal instance"""
        return UserSpecificNotionInternal()

    @pytest.mark.asyncio
    async def test_user_isolation_in_enhanced_notes_tool(self, enhanced_notes_tool, mock_db_session):
        """Test that EnhancedNotesTool uses user-specific Notion operations"""
        
        # Mock the user-specific Notion internal
        with patch.object(enhanced_notes_tool.notion_internal, 'ensure_user_main_page_exists') as mock_ensure_page, \
             patch.object(enhanced_notes_tool.notion_internal, 'create_user_page') as mock_create_page:
            
            # Configure mocks
            mock_ensure_page.return_value = "user_123_main_page_id"
            mock_create_page.return_value = "user_123_note_page_id"
            
            # Test creating a note for user 123
            result = await enhanced_notes_tool.create_enhanced_note(
                content="Test note content",
                title="Test Note",
                user_id=123
            )
            
            # Verify user-specific operations were called
            mock_ensure_page.assert_called_once_with(mock_db_session, 123)
            mock_create_page.assert_called_once_with(
                mock_db_session, 
                123, 
                "Test Note", 
                pytest.any(str),  # Enhanced content
                "user_123_main_page_id"
            )
            
            # Verify result contains user-specific page ID
            assert "user_123_note_page_id" in result
            assert "✅ Successfully created enhanced note" in result

    @pytest.mark.asyncio
    async def test_different_users_get_different_workspaces(self, user_specific_notion_internal, mock_db_session):
        """Test that different users get different Notion workspaces"""
        
        with patch.object(user_specific_notion_internal.client_factory, 'get_user_client') as mock_get_client:
            
            # Mock different clients for different users
            client_user_1 = MagicMock()
            client_user_2 = MagicMock()
            
            mock_get_client.side_effect = lambda db, user_id, session_id=None: {
                1: client_user_1,
                2: client_user_2
            }[user_id]
            
            # Test user 1 operations
            await user_specific_notion_internal.ensure_user_main_page_exists(mock_db_session, 1)
            await user_specific_notion_internal.ensure_user_main_page_exists(mock_db_session, 2)
            
            # Verify different clients were used
            assert mock_get_client.call_count == 2
            calls = mock_get_client.call_args_list
            assert calls[0][0][1] == 1  # First call was for user 1
            assert calls[1][0][1] == 2  # Second call was for user 2

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_users_pages(self, user_specific_notion_internal, mock_db_session):
        """Test that users cannot access pages created by other users"""
        
        with patch.object(user_specific_notion_internal.client_factory, 'get_user_client') as mock_get_client:
            
            # Mock client for user 1
            client_user_1 = MagicMock()
            client_user_1.search.return_value = {"results": []}  # No pages found
            mock_get_client.return_value = client_user_1
            
            # User 1 tries to find a page that was created by user 2
            result = await user_specific_notion_internal.find_user_page_by_title(
                mock_db_session, 1, "User 2's Secret Note"
            )
            
            # Should return None because user 1 can't see user 2's pages
            assert result is None
            
            # Verify the search was performed with user 1's client
            client_user_1.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_notion_client_factory_user_isolation(self, mock_db_session):
        """Test that NotionClientFactory creates isolated clients per user"""
        
        factory = NotionClientFactory()
        
        with patch.object(factory, 'integration_service') as mock_integration_service, \
             patch.object(factory, 'token_service') as mock_token_service:
            
            # Mock different integrations and tokens for different users
            integration_1 = MagicMock()
            integration_1.id = "integration_1"
            integration_2 = MagicMock()
            integration_2.id = "integration_2"
            
            mock_integration_service.get_integration_by_user_and_provider.side_effect = lambda db, user_id, provider: {
                1: integration_1,
                2: integration_2
            }[user_id]
            
            mock_token_service.get_valid_token.side_effect = lambda db, integration_id: {
                "integration_1": "token_user_1",
                "integration_2": "token_user_2"
            }[integration_id]
            
            # Get clients for different users
            client_1 = await factory.get_user_client(mock_db_session, 1)
            client_2 = await factory.get_user_client(mock_db_session, 2)
            
            # Verify different tokens were used
            assert client_1.auth == "token_user_1"
            assert client_2.auth == "token_user_2"
            
            # Verify clients are cached separately
            assert factory._client_cache["user_1"] == client_1
            assert factory._client_cache["user_2"] == client_2

    @pytest.mark.asyncio
    async def test_workspace_manager_user_isolation(self, mock_db_session):
        """Test that NotionWorkspaceManager creates user-specific workspaces"""
        
        manager = NotionWorkspaceManager()
        
        with patch.object(manager.client_factory, 'get_user_client') as mock_get_client:
            
            # Mock different clients for different users
            client_user_1 = MagicMock()
            client_user_1.pages.create.return_value = {"id": "user_1_workspace"}
            client_user_2 = MagicMock()
            client_user_2.pages.create.return_value = {"id": "user_2_workspace"}
            
            mock_get_client.side_effect = lambda db, user_id, session_id=None: {
                1: client_user_1,
                2: client_user_2
            }[user_id]
            
            # Create workspaces for different users
            workspace_1 = await manager.ensure_user_root_page(mock_db_session, 1)
            workspace_2 = await manager.ensure_user_root_page(mock_db_session, 2)
            
            # Verify different workspaces were created
            assert workspace_1 == "user_1_workspace"
            assert workspace_2 == "user_2_workspace"
            
            # Verify different clients were used
            assert mock_get_client.call_count == 2

    @pytest.mark.asyncio
    async def test_enhanced_notes_tool_requires_user_id(self, enhanced_notes_tool):
        """Test that EnhancedNotesTool requires user_id parameter"""
        
        # Test without user_id should return error
        result = await enhanced_notes_tool.create_enhanced_note(
            content="Test content",
            title="Test Title"
        )
        
        assert "Error: User ID is required for creating notes" in result

    @pytest.mark.asyncio
    async def test_user_specific_page_creation(self, user_specific_notion_internal, mock_db_session):
        """Test that pages are created in the correct user's workspace"""
        
        with patch.object(user_specific_notion_internal.client_factory, 'get_user_client') as mock_get_client:
            
            # Mock client for user 123
            client_user_123 = MagicMock()
            client_user_123.pages.create.return_value = {"id": "page_123_created"}
            mock_get_client.return_value = client_user_123
            
            # Create page for user 123
            page_id = await user_specific_notion_internal.create_user_page(
                mock_db_session, 123, "My Note", "Content", "parent_page_123"
            )
            
            # Verify page was created with user 123's client
            assert page_id == "page_123_created"
            client_user_123.pages.create.assert_called_once()
            
            # Verify the call was made with correct parameters
            call_args = client_user_123.pages.create.call_args
            assert call_args[1]["parent"]["page_id"] == "parent_page_123"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
