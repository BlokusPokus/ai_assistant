"""
Enhanced Notes Tool OAuth Integration Tests

This module tests the EnhancedNotesTool integration with Notion OAuth.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool
from personal_assistant.tools.notion_pages.client_factory import NotionClientFactory, NotionNotConnectedError, NotionTokenExpiredError
from personal_assistant.tools.notion_pages.notion_internal_user_specific import UserSpecificNotionInternal
from personal_assistant.oauth.models.integration import OAuthIntegration
from personal_assistant.oauth.models.token import OAuthToken


class TestEnhancedNotesToolOAuth:
    """Test cases for EnhancedNotesTool OAuth integration."""

    @pytest.fixture
    def enhanced_notes_tool(self):
        """Provide an EnhancedNotesTool instance for testing."""
        return EnhancedNotesTool()

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
    async def test_create_enhanced_note_success(self, enhanced_notes_tool, mock_db_session, mock_notion_integration, mock_notion_token, mock_notion_client):
        """Test successful note creation with OAuth authentication."""
        user_id = 1
        content = "Test note content"
        title = "Test Note"
        
        # Mock the user-specific Notion internal
        with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
            # Mock ensure_user_main_page_exists
            mock_notion_internal.ensure_user_main_page_exists.return_value = "main_page_123"
            
            # Mock create_user_page
            mock_notion_internal.create_user_page.return_value = "new_page_456"
            
            # Mock database context
            with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                mock_context.return_value.__aenter__.return_value = mock_db_session
                mock_context.return_value.__aexit__.return_value = None
                
                result = await enhanced_notes_tool.create_enhanced_note(
                    content=content,
                    title=title,
                    user_id=user_id
                )
                
                assert "Successfully created enhanced note" in result
                assert "new_page_456" in result
                mock_notion_internal.ensure_user_main_page_exists.assert_called_once_with(mock_db_session, user_id)
                mock_notion_internal.create_user_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_enhanced_note_no_user_id(self, enhanced_notes_tool):
        """Test note creation without user_id."""
        content = "Test note content"
        title = "Test Note"
        
        result = await enhanced_notes_tool.create_enhanced_note(
            content=content,
            title=title,
            user_id=None
        )
        
        assert "Error: User ID is required" in result

    @pytest.mark.asyncio
    async def test_create_enhanced_note_notion_not_connected(self, enhanced_notes_tool, mock_db_session):
        """Test note creation when Notion is not connected."""
        user_id = 1
        content = "Test note content"
        title = "Test Note"
        
        # Mock the user-specific Notion internal to raise NotionNotConnectedError
        with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
            mock_notion_internal.ensure_user_main_page_exists.side_effect = NotionNotConnectedError("User must connect Notion account")
            
            # Mock database context
            with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                mock_context.return_value.__aenter__.return_value = mock_db_session
                mock_context.return_value.__aexit__.return_value = None
                
                result = await enhanced_notes_tool.create_enhanced_note(
                    content=content,
                    title=title,
                    user_id=user_id
                )
                
                assert "Error creating enhanced note" in result
                assert "User must connect Notion account" in result

    @pytest.mark.asyncio
    async def test_create_enhanced_note_token_expired(self, enhanced_notes_tool, mock_db_session):
        """Test note creation when OAuth token is expired."""
        user_id = 1
        content = "Test note content"
        title = "Test Note"
        
        # Mock the user-specific Notion internal to raise NotionTokenExpiredError
        with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
            mock_notion_internal.ensure_user_main_page_exists.side_effect = NotionTokenExpiredError("Token expired")
            
            # Mock database context
            with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                mock_context.return_value.__aenter__.return_value = mock_db_session
                mock_context.return_value.__aexit__.return_value = None
                
                result = await enhanced_notes_tool.create_enhanced_note(
                    content=content,
                    title=title,
                    user_id=user_id
                )
                
                assert "Error creating enhanced note" in result
                assert "Token expired" in result

    @pytest.mark.asyncio
    async def test_create_enhanced_note_database_error(self, enhanced_notes_tool, mock_db_session):
        """Test note creation with database error."""
        user_id = 1
        content = "Test note content"
        title = "Test Note"
        
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Database connection error")
        
        # Mock database context
        with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
            mock_context.return_value.__aenter__.return_value = mock_db_session
            mock_context.return_value.__aexit__.return_value = None
            
            result = await enhanced_notes_tool.create_enhanced_note(
                content=content,
                title=title,
                user_id=user_id
            )
            
            assert "Error creating enhanced note" in result
            assert "Database connection error" in result

    @pytest.mark.asyncio
    async def test_create_enhanced_note_llm_enhancement_success(self, enhanced_notes_tool, mock_db_session):
        """Test note creation with LLM enhancement."""
        user_id = 1
        content = "Meeting notes from today"
        title = "Meeting Notes"
        
        # Mock LLM enhancement
        with patch.object(enhanced_notes_tool.llm_enhancer, 'enhance_note') as mock_enhance:
            mock_enhance.return_value = {
                "enhanced_content": "Enhanced meeting notes with better structure",
                "suggested_title": "Enhanced Meeting Notes",
                "tags": ["meeting", "notes", "work"],
                "confidence_score": 0.9
            }
            
            # Mock the user-specific Notion internal
            with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
                mock_notion_internal.ensure_user_main_page_exists.return_value = "main_page_123"
                mock_notion_internal.create_user_page.return_value = "new_page_456"
                
                # Mock database context
                with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                    mock_context.return_value.__aenter__.return_value = mock_db_session
                    mock_context.return_value.__aexit__.return_value = None
                    
                    result = await enhanced_notes_tool.create_enhanced_note(
                        content=content,
                        title=title,
                        user_id=user_id
                    )
                    
                    assert "Successfully created enhanced note" in result
                    mock_enhance.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_enhanced_note_llm_enhancement_error(self, enhanced_notes_tool, mock_db_session):
        """Test note creation with LLM enhancement error."""
        user_id = 1
        content = "Meeting notes from today"
        title = "Meeting Notes"
        
        # Mock LLM enhancement error
        with patch.object(enhanced_notes_tool.llm_enhancer, 'enhance_note') as mock_enhance:
            mock_enhance.side_effect = Exception("LLM service unavailable")
            
            # Mock the user-specific Notion internal
            with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
                mock_notion_internal.ensure_user_main_page_exists.return_value = "main_page_123"
                mock_notion_internal.create_user_page.return_value = "new_page_456"
                
                # Mock database context
                with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                    mock_context.return_value.__aenter__.return_value = mock_db_session
                    mock_context.return_value.__aexit__.return_value = None
                    
                    result = await enhanced_notes_tool.create_enhanced_note(
                        content=content,
                        title=title,
                        user_id=user_id
                    )
                    
                    # Should still create note with original content
                    assert "Successfully created enhanced note" in result
                    mock_enhance.assert_called_once()

    def test_user_isolation_verification(self, enhanced_notes_tool):
        """Test that EnhancedNotesTool uses user-specific Notion components."""
        # Verify that the tool uses UserSpecificNotionInternal
        assert hasattr(enhanced_notes_tool, 'notion_internal')
        assert isinstance(enhanced_notes_tool.notion_internal, UserSpecificNotionInternal)

    def test_method_signature_compatibility(self, enhanced_notes_tool):
        """Test that create_enhanced_note method accepts user_id parameter."""
        import inspect
        
        # Get method signature
        sig = inspect.signature(enhanced_notes_tool.create_enhanced_note)
        
        # Check that user_id parameter exists
        assert 'user_id' in sig.parameters
        
        # Check parameter type annotation
        user_id_param = sig.parameters['user_id']
        assert user_id_param.annotation == int or user_id_param.annotation == type(None)

    @pytest.mark.asyncio
    async def test_concurrent_user_operations(self, enhanced_notes_tool, mock_db_session):
        """Test concurrent note creation for different users."""
        import asyncio
        
        async def create_note_for_user(user_id, content, title):
            with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
                mock_notion_internal.ensure_user_main_page_exists.return_value = f"main_page_{user_id}"
                mock_notion_internal.create_user_page.return_value = f"new_page_{user_id}"
                
                with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                    mock_context.return_value.__aenter__.return_value = mock_db_session
                    mock_context.return_value.__aexit__.return_value = None
                    
                    return await enhanced_notes_tool.create_enhanced_note(
                        content=content,
                        title=title,
                        user_id=user_id
                    )
        
        # Create notes for multiple users concurrently
        tasks = [
            create_note_for_user(1, "User 1 note", "Note 1"),
            create_note_for_user(2, "User 2 note", "Note 2"),
            create_note_for_user(3, "User 3 note", "Note 3")
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all notes were created successfully
        for i, result in enumerate(results):
            assert "Successfully created enhanced note" in result
            assert f"new_page_{i+1}" in result
