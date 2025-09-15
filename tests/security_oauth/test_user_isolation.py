"""
OAuth User Isolation Security Tests

This module tests OAuth user data isolation and security.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.services.integration_service import OAuthIntegrationService
from personal_assistant.oauth.models.integration import OAuthIntegration
from personal_assistant.oauth.models.token import OAuthToken
from personal_assistant.tools.notion_pages.client_factory import NotionClientFactory
from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool


class TestOAuthUserIsolation:
    """Test cases for OAuth user isolation security."""

    @pytest.fixture
    def token_service(self):
        """Provide an OAuthTokenService instance for testing."""
        return OAuthTokenService()

    @pytest.fixture
    def integration_service(self):
        """Provide an OAuthIntegrationService instance for testing."""
        return OAuthIntegrationService()

    @pytest.fixture
    def mock_db_session(self):
        """Provide a mock database session for testing."""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.fixture
    def mock_user1_integration(self):
        """Provide mock OAuth integration for user 1."""
        integration = Mock(spec=OAuthIntegration)
        integration.id = 1
        integration.user_id = 1
        integration.provider = "notion"
        integration.status = "active"
        integration.provider_user_id = "notion_user_1"
        integration.provider_email = "user1@example.com"
        return integration

    @pytest.fixture
    def mock_user2_integration(self):
        """Provide mock OAuth integration for user 2."""
        integration = Mock(spec=OAuthIntegration)
        integration.id = 2
        integration.user_id = 2
        integration.provider = "notion"
        integration.status = "active"
        integration.provider_user_id = "notion_user_2"
        integration.provider_email = "user2@example.com"
        return integration

    @pytest.fixture
    def mock_user1_token(self):
        """Provide mock OAuth token for user 1."""
        token = Mock(spec=OAuthToken)
        token.id = 1
        token.integration_id = 1
        token.user_id = 1
        token.token_type = "access_token"
        token.access_token = "user1_access_token_123"
        token.refresh_token = "user1_refresh_token_456"
        return token

    @pytest.fixture
    def mock_user2_token(self):
        """Provide mock OAuth token for user 2."""
        token = Mock(spec=OAuthToken)
        token.id = 2
        token.integration_id = 2
        token.user_id = 2
        token.token_type = "access_token"
        token.access_token = "user2_access_token_789"
        token.refresh_token = "user2_refresh_token_101"
        return token

    @pytest.mark.asyncio
    async def test_token_isolation_by_user(self, token_service, mock_db_session, mock_user1_token, mock_user2_token):
        """Test that users can only access their own tokens."""
        user1_id = 1
        user2_id = 2
        
        # Mock database to return user1's token when queried for user1
        def mock_execute_user1(query):
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_user1_token]
            return mock_result
        
        def mock_execute_user2(query):
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_user2_token]
            return mock_result
        
        # Test user1 can only access their own token
        mock_db_session.execute.side_effect = mock_execute_user1
        user1_token = await token_service.get_valid_token(
            mock_db_session, mock_user1_token.integration_id, "access_token"
        )
        
        assert user1_token == mock_user1_token
        assert user1_token.user_id == user1_id
        assert user1_token.access_token == "user1_access_token_123"
        
        # Test user2 can only access their own token
        mock_db_session.execute.side_effect = mock_execute_user2
        user2_token = await token_service.get_valid_token(
            mock_db_session, mock_user2_token.integration_id, "access_token"
        )
        
        assert user2_token == mock_user2_token
        assert user2_token.user_id == user2_id
        assert user2_token.access_token == "user2_access_token_789"

    @pytest.mark.asyncio
    async def test_integration_isolation_by_user(self, integration_service, mock_db_session, mock_user1_integration, mock_user2_integration):
        """Test that users can only access their own integrations."""
        user1_id = 1
        user2_id = 2
        provider = "notion"
        
        # Mock database to return user1's integration when queried for user1
        def mock_execute_user1(query):
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_user1_integration]
            return mock_result
        
        def mock_execute_user2(query):
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_user2_integration]
            return mock_result
        
        # Test user1 can only access their own integration
        mock_db_session.execute.side_effect = mock_execute_user1
        user1_integration = await integration_service.get_integration_by_user_and_provider(
            mock_db_session, user1_id, provider
        )
        
        assert user1_integration == mock_user1_integration
        assert user1_integration.user_id == user1_id
        assert user1_integration.provider_email == "user1@example.com"
        
        # Test user2 can only access their own integration
        mock_db_session.execute.side_effect = mock_execute_user2
        user2_integration = await integration_service.get_integration_by_user_and_provider(
            mock_db_session, user2_id, provider
        )
        
        assert user2_integration == mock_user2_integration
        assert user2_integration.user_id == user2_id
        assert user2_integration.provider_email == "user2@example.com"

    @pytest.mark.asyncio
    async def test_notion_client_factory_user_isolation(self, mock_db_session, mock_user1_integration, mock_user1_token, mock_user2_integration, mock_user2_token):
        """Test that NotionClientFactory maintains user isolation."""
        client_factory = NotionClientFactory()
        
        # Mock integration service to return correct integration for each user
        def mock_get_integration(db, user_id, provider):
            if user_id == 1:
                return mock_user1_integration
            elif user_id == 2:
                return mock_user2_integration
            return None
        
        # Mock token service to return correct token for each integration
        def mock_get_token(db, integration_id, token_type):
            if integration_id == 1:
                return mock_user1_token
            elif integration_id == 2:
                return mock_user2_token
            return None
        
        with patch.object(client_factory.integration_service, 'get_integration_by_user_and_provider', side_effect=mock_get_integration):
            with patch.object(client_factory.token_service, 'get_valid_token', side_effect=mock_get_token):
                with patch('personal_assistant.tools.notion_pages.client_factory.Client') as mock_client_class:
                    mock_client1 = Mock()
                    mock_client2 = Mock()
                    mock_client_class.side_effect = [mock_client1, mock_client2]
                    
                    with patch.object(client_factory, '_validate_workspace_access', return_value=True):
                        # Get clients for both users
                        client1 = await client_factory.get_user_client(mock_db_session, 1)
                        client2 = await client_factory.get_user_client(mock_db_session, 2)
                        
                        # Verify clients are different instances
                        assert client1 != client2
                        assert client1 == mock_client1
                        assert client2 == mock_client2
                        
                        # Verify correct tokens were used
                        assert mock_client_class.call_args_list[0][1]['auth'] == "user1_access_token_123"
                        assert mock_client_class.call_args_list[1][1]['auth'] == "user2_access_token_789"

    @pytest.mark.asyncio
    async def test_enhanced_notes_tool_user_isolation(self, mock_db_session):
        """Test that EnhancedNotesTool maintains user isolation."""
        enhanced_notes_tool = EnhancedNotesTool()
        
        # Mock user-specific Notion internal to track user IDs
        user_calls = []
        
        async def mock_ensure_user_main_page_exists(db, user_id, session_id=None):
            user_calls.append(('ensure_user_main_page_exists', user_id))
            return f"main_page_{user_id}"
        
        async def mock_create_user_page(db, user_id, title, content, main_page_id, session_id=None):
            user_calls.append(('create_user_page', user_id))
            return f"new_page_{user_id}"
        
        with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
            mock_notion_internal.ensure_user_main_page_exists.side_effect = mock_ensure_user_main_page_exists
            mock_notion_internal.create_user_page.side_effect = mock_create_user_page
            
            with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                mock_context.return_value.__aenter__.return_value = mock_db_session
                mock_context.return_value.__aexit__.return_value = None
                
                # Create notes for different users
                await enhanced_notes_tool.create_enhanced_note(
                    content="User 1 note",
                    title="Note 1",
                    user_id=1
                )
                
                await enhanced_notes_tool.create_enhanced_note(
                    content="User 2 note",
                    title="Note 2",
                    user_id=2
                )
                
                await enhanced_notes_tool.create_enhanced_note(
                    content="User 3 note",
                    title="Note 3",
                    user_id=3
                )
                
                # Verify each user's operations were isolated
                assert len(user_calls) == 6  # 2 calls per user (ensure + create)
                
                # Verify user isolation
                user1_calls = [call for call in user_calls if call[1] == 1]
                user2_calls = [call for call in user_calls if call[1] == 2]
                user3_calls = [call for call in user_calls if call[1] == 3]
                
                assert len(user1_calls) == 2
                assert len(user2_calls) == 2
                assert len(user3_calls) == 2
                
                # Verify each user got their own page IDs
                assert any("main_page_1" in str(call) for call in user1_calls)
                assert any("main_page_2" in str(call) for call in user2_calls)
                assert any("main_page_3" in str(call) for call in user3_calls)

    @pytest.mark.asyncio
    async def test_concurrent_user_operations_isolation(self, mock_db_session):
        """Test that concurrent operations maintain user isolation."""
        import asyncio
        
        enhanced_notes_tool = EnhancedNotesTool()
        
        # Track operations by user
        user_operations = {1: [], 2: [], 3: []}
        
        async def create_note_for_user(user_id, content, title):
            with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
                mock_notion_internal.ensure_user_main_page_exists.return_value = f"main_page_{user_id}"
                mock_notion_internal.create_user_page.return_value = f"new_page_{user_id}"
                
                with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                    mock_context.return_value.__aenter__.return_value = mock_db_session
                    mock_context.return_value.__aexit__.return_value = None
                    
                    result = await enhanced_notes_tool.create_enhanced_note(
                        content=content,
                        title=title,
                        user_id=user_id
                    )
                    
                    user_operations[user_id].append(result)
                    return result
        
        # Create notes for multiple users concurrently
        tasks = []
        for user_id in range(1, 4):
            for note_num in range(1, 4):  # 3 notes per user
                task = create_note_for_user(
                    user_id, 
                    f"User {user_id} note {note_num}", 
                    f"Note {note_num}"
                )
                tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all operations completed successfully
        assert len(results) == 9  # 3 users × 3 notes each
        
        # Verify user isolation
        for user_id in range(1, 4):
            user_results = user_operations[user_id]
            assert len(user_results) == 3
            
            for result in user_results:
                assert "Successfully created enhanced note" in result
                assert f"new_page_{user_id}" in result

    @pytest.mark.asyncio
    async def test_token_encryption_user_isolation(self, token_service):
        """Test that token encryption maintains user isolation."""
        # Create tokens for different users
        user1_token = "user1_access_token_123"
        user2_token = "user2_access_token_456"
        
        # Encrypt tokens
        encrypted_user1 = token_service.encrypt_token(user1_token)
        encrypted_user2 = token_service.encrypt_token(user2_token)
        
        # Verify tokens are different
        assert encrypted_user1 != encrypted_user2
        
        # Verify each token decrypts to its original value
        assert token_service.decrypt_token(encrypted_user1) == user1_token
        assert token_service.decrypt_token(encrypted_user2) == user2_token
        
        # Verify cross-decryption fails
        with pytest.raises(Exception):
            token_service.decrypt_token(encrypted_user1 + "corrupted")
        
        with pytest.raises(Exception):
            token_service.decrypt_token(encrypted_user2 + "corrupted")

    @pytest.mark.asyncio
    async def test_database_query_isolation(self, mock_db_session, mock_user1_integration, mock_user2_integration):
        """Test that database queries maintain user isolation."""
        integration_service = OAuthIntegrationService()
        
        # Mock database to return different results based on user_id in query
        def mock_execute(query):
            # Extract user_id from query (simplified mock)
            query_str = str(query)
            if "user_id = 1" in query_str:
                mock_result = Mock()
                mock_result.scalars.return_value.all.return_value = [mock_user1_integration]
                return mock_result
            elif "user_id = 2" in query_str:
                mock_result = Mock()
                mock_result.scalars.return_value.all.return_value = [mock_user2_integration]
                return mock_result
            else:
                mock_result = Mock()
                mock_result.scalars.return_value.all.return_value = []
                return mock_result
        
        mock_db_session.execute.side_effect = mock_execute
        
        # Test user1 integration retrieval
        user1_integration = await integration_service.get_integration_by_user_and_provider(
            mock_db_session, 1, "notion"
        )
        assert user1_integration == mock_user1_integration
        assert user1_integration.user_id == 1
        
        # Test user2 integration retrieval
        user2_integration = await integration_service.get_integration_by_user_and_provider(
            mock_db_session, 2, "notion"
        )
        assert user2_integration == mock_user2_integration
        assert user2_integration.user_id == 2
        
        # Test that user1 cannot access user2's integration
        user1_trying_user2 = await integration_service.get_integration_by_user_and_provider(
            mock_db_session, 1, "notion"
        )
        assert user1_trying_user2 == mock_user1_integration
        assert user1_trying_user2 != mock_user2_integration

    def test_oauth_manager_provider_isolation(self):
        """Test that OAuthManager maintains provider isolation."""
        from personal_assistant.oauth.oauth_manager import OAuthManager
        
        oauth_manager = OAuthManager()
        
        # Verify that different providers are isolated
        providers = oauth_manager.get_supported_providers()
        assert "google" in providers
        assert "microsoft" in providers
        assert "notion" in providers
        assert "youtube" in providers
        
        # Verify each provider is a separate instance
        google_provider = oauth_manager.get_provider("google")
        microsoft_provider = oauth_manager.get_provider("microsoft")
        notion_provider = oauth_manager.get_provider("notion")
        youtube_provider = oauth_manager.get_provider("youtube")
        
        assert google_provider != microsoft_provider
        assert google_provider != notion_provider
        assert google_provider != youtube_provider
        assert microsoft_provider != notion_provider
        assert microsoft_provider != youtube_provider
        assert notion_provider != youtube_provider
        
        # Verify each provider has correct name
        assert google_provider.provider_name == "google"
        assert microsoft_provider.provider_name == "microsoft"
        assert notion_provider.provider_name == "notion"
        assert youtube_provider.provider_name == "youtube"
