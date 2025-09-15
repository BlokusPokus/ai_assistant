"""
Complete OAuth Flow End-to-End Tests

This module tests complete OAuth user journeys from initiation to agent usage.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.oauth.oauth_manager import OAuthManager
from personal_assistant.oauth.models.integration import OAuthIntegration
from personal_assistant.oauth.models.token import OAuthToken
from personal_assistant.oauth.models.state import OAuthState
from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool


class TestCompleteOAuthFlow:
    """Test cases for complete OAuth user journeys."""

    @pytest.fixture
    def oauth_manager(self):
        """Provide an OAuthManager instance for testing."""
        return OAuthManager()

    @pytest.fixture
    def mock_db_session(self):
        """Provide a mock database session for testing."""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.fixture
    def mock_user_data(self):
        """Provide mock user data for testing."""
        return {
            "id": 1,
            "email": "test@example.com",
            "full_name": "Test User"
        }

    @pytest.fixture
    def mock_oauth_state(self):
        """Provide mock OAuth state for testing."""
        state = Mock(spec=OAuthState)
        state.id = 1
        state.state_token = "test_state_token_123"
        state.provider = "notion"
        state.user_id = 1
        state.scopes = ["read", "write"]
        state.redirect_uri = "http://localhost:8000/api/v1/oauth/callback"
        state.is_used = False
        state.expires_at = None
        return state

    @pytest.fixture
    def mock_oauth_integration(self):
        """Provide mock OAuth integration for testing."""
        integration = Mock(spec=OAuthIntegration)
        integration.id = 1
        integration.user_id = 1
        integration.provider = "notion"
        integration.status = "active"
        integration.scopes = ["read", "write"]
        integration.provider_user_id = "notion_user_123"
        integration.provider_email = "test@example.com"
        integration.provider_name = "Test User"
        return integration

    @pytest.fixture
    def mock_oauth_token(self):
        """Provide mock OAuth token for testing."""
        token = Mock(spec=OAuthToken)
        token.id = 1
        token.integration_id = 1
        token.token_type = "access_token"
        token.access_token = "notion_access_token_123"
        token.refresh_token = "notion_refresh_token_456"
        token.expires_at = None
        token.scope = "read write"
        return token

    @pytest.mark.asyncio
    async def test_complete_notion_oauth_flow(self, oauth_manager, mock_db_session, mock_user_data, mock_oauth_state, mock_oauth_integration, mock_oauth_token):
        """Test complete Notion OAuth flow from initiation to agent usage."""
        user_id = 1
        provider = "notion"
        scopes = ["read", "write"]
        
        # Step 1: Initiate OAuth flow
        with patch.object(oauth_manager.security_service, 'create_state') as mock_create_state:
            mock_create_state.return_value = mock_oauth_state
            
            with patch.object(oauth_manager, 'get_provider') as mock_get_provider:
                mock_provider = Mock()
                mock_provider.get_authorization_url.return_value = "https://notion.so/oauth/authorize?client_id=test&state=test_state_token_123"
                mock_get_provider.return_value = mock_provider
                
                result = await oauth_manager.initiate_oauth_flow(
                    db=mock_db_session,
                    user_id=user_id,
                    provider_name=provider,
                    scopes=scopes
                )
                
                assert "authorization_url" in result
                assert "state_token" in result
                assert result["provider"] == provider

        # Step 2: Handle OAuth callback
        state_token = "test_state_token_123"
        auth_code = "test_auth_code_456"
        
        with patch.object(oauth_manager.security_service, 'validate_state') as mock_validate_state:
            mock_validate_state.return_value = mock_oauth_state
            
            with patch.object(oauth_manager, 'get_provider') as mock_get_provider:
                mock_provider = Mock()
                mock_provider.exchange_code_for_tokens.return_value = {
                    "access_token": "notion_access_token_123",
                    "refresh_token": "notion_refresh_token_456",
                    "expires_in": 3600,
                    "token_type": "Bearer"
                }
                mock_provider.get_user_info.return_value = {
                    "id": "notion_user_123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
                mock_get_provider.return_value = mock_provider
                
                with patch.object(oauth_manager.integration_service, 'create_integration') as mock_create_integration:
                    mock_create_integration.return_value = mock_oauth_integration
                    
                    with patch.object(oauth_manager.token_service, 'store_tokens') as mock_store_tokens:
                        mock_store_tokens.return_value = [mock_oauth_token]
                        
                        result = await oauth_manager.handle_oauth_callback(
                            db=mock_db_session,
                            state_token=state_token,
                            authorization_code=auth_code,
                            provider_name=provider
                        )
                        
                        assert "integration_id" in result
                        assert result["provider"] == provider
                        assert result["status"] == "active"

        # Step 3: Use OAuth-protected agent tool
        enhanced_notes_tool = EnhancedNotesTool()
        
        with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
            mock_notion_internal.ensure_user_main_page_exists.return_value = "main_page_123"
            mock_notion_internal.create_user_page.return_value = "new_page_456"
            
            with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                mock_context.return_value.__aenter__.return_value = mock_db_session
                mock_context.return_value.__aexit__.return_value = None
                
                result = await enhanced_notes_tool.create_enhanced_note(
                    content="Test note content",
                    title="Test Note",
                    user_id=user_id
                )
                
                assert "Successfully created enhanced note" in result
                assert "new_page_456" in result

    @pytest.mark.asyncio
    async def test_complete_google_oauth_flow(self, oauth_manager, mock_db_session, mock_user_data):
        """Test complete Google OAuth flow."""
        user_id = 1
        provider = "google"
        scopes = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/gmail.readonly"]
        
        # Mock OAuth state
        mock_state = Mock(spec=OAuthState)
        mock_state.state_token = "google_state_token_123"
        mock_state.provider = provider
        mock_state.user_id = user_id
        
        # Step 1: Initiate OAuth flow
        with patch.object(oauth_manager.security_service, 'create_state') as mock_create_state:
            mock_create_state.return_value = mock_state
            
            with patch.object(oauth_manager, 'get_provider') as mock_get_provider:
                mock_provider = Mock()
                mock_provider.get_authorization_url.return_value = "https://accounts.google.com/oauth/authorize?client_id=test&state=google_state_token_123"
                mock_get_provider.return_value = mock_provider
                
                result = await oauth_manager.initiate_oauth_flow(
                    db=mock_db_session,
                    user_id=user_id,
                    provider_name=provider,
                    scopes=scopes
                )
                
                assert "authorization_url" in result
                assert "accounts.google.com" in result["authorization_url"]

        # Step 2: Handle OAuth callback
        with patch.object(oauth_manager.security_service, 'validate_state') as mock_validate_state:
            mock_validate_state.return_value = mock_state
            
            with patch.object(oauth_manager, 'get_provider') as mock_get_provider:
                mock_provider = Mock()
                mock_provider.exchange_code_for_tokens.return_value = {
                    "access_token": "google_access_token_123",
                    "refresh_token": "google_refresh_token_456",
                    "expires_in": 3600,
                    "token_type": "Bearer"
                }
                mock_provider.get_user_info.return_value = {
                    "id": "google_user_123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
                mock_get_provider.return_value = mock_provider
                
                with patch.object(oauth_manager.integration_service, 'create_integration') as mock_create_integration:
                    mock_integration = Mock(spec=OAuthIntegration)
                    mock_integration.id = 1
                    mock_create_integration.return_value = mock_integration
                    
                    with patch.object(oauth_manager.token_service, 'store_tokens') as mock_store_tokens:
                        mock_token = Mock(spec=OAuthToken)
                        mock_store_tokens.return_value = [mock_token]
                        
                        result = await oauth_manager.handle_oauth_callback(
                            db=mock_db_session,
                            state_token="google_state_token_123",
                            authorization_code="google_auth_code_456",
                            provider_name=provider
                        )
                        
                        assert "integration_id" in result
                        assert result["provider"] == provider

    @pytest.mark.asyncio
    async def test_oauth_flow_with_token_refresh(self, oauth_manager, mock_db_session, mock_oauth_integration, mock_oauth_token):
        """Test OAuth flow with automatic token refresh."""
        integration_id = 1
        
        # Mock expired token
        expired_token = Mock(spec=OAuthToken)
        expired_token.expires_at = None  # Expired
        expired_token.refresh_token = "refresh_token_456"
        
        # Mock refreshed token
        refreshed_token = Mock(spec=OAuthToken)
        refreshed_token.access_token = "new_access_token_789"
        refreshed_token.expires_at = None
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.refresh_access_token.return_value = {
            "access_token": "new_access_token_789",
            "refresh_token": "new_refresh_token_101",
            "expires_in": 3600
        }
        
        with patch.object(oauth_manager.token_service, 'get_valid_token') as mock_get_token:
            mock_get_token.return_value = None  # No valid token
            
            with patch.object(oauth_manager.token_service, 'refresh_access_token') as mock_refresh:
                mock_refresh.return_value = "new_access_token_789"
                
                with patch.object(oauth_manager.token_service, 'store_tokens') as mock_store:
                    mock_store.return_value = [refreshed_token]
                    
                    success = await oauth_manager.refresh_integration_tokens(
                        db=mock_db_session,
                        integration_id=integration_id
                    )
                    
                    assert success is True
                    mock_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_oauth_flow_error_handling(self, oauth_manager, mock_db_session):
        """Test OAuth flow error handling."""
        user_id = 1
        provider = "notion"
        scopes = ["read", "write"]
        
        # Test invalid provider
        with pytest.raises(Exception):
            await oauth_manager.initiate_oauth_flow(
                db=mock_db_session,
                user_id=user_id,
                provider_name="invalid_provider",
                scopes=scopes
            )
        
        # Test invalid state token
        with patch.object(oauth_manager.security_service, 'validate_state') as mock_validate_state:
            mock_validate_state.side_effect = Exception("Invalid state token")
            
            with pytest.raises(Exception):
                await oauth_manager.handle_oauth_callback(
                    db=mock_db_session,
                    state_token="invalid_state_token",
                    authorization_code="test_code",
                    provider_name=provider
                )

    @pytest.mark.asyncio
    async def test_multi_provider_oauth_flow(self, oauth_manager, mock_db_session):
        """Test OAuth flow with multiple providers."""
        user_id = 1
        providers = ["google", "microsoft", "notion", "youtube"]
        
        integrations = []
        
        for provider in providers:
            # Mock state
            mock_state = Mock(spec=OAuthState)
            mock_state.state_token = f"{provider}_state_token_123"
            mock_state.provider = provider
            mock_state.user_id = user_id
            
            # Initiate flow
            with patch.object(oauth_manager.security_service, 'create_state') as mock_create_state:
                mock_create_state.return_value = mock_state
                
                with patch.object(oauth_manager, 'get_provider') as mock_get_provider:
                    mock_provider = Mock()
                    mock_provider.get_authorization_url.return_value = f"https://{provider}.com/oauth/authorize"
                    mock_get_provider.return_value = mock_provider
                    
                    result = await oauth_manager.initiate_oauth_flow(
                        db=mock_db_session,
                        user_id=user_id,
                        provider_name=provider,
                        scopes=["read", "write"]
                    )
                    
                    assert "authorization_url" in result
                    assert result["provider"] == provider
            
            # Handle callback
            with patch.object(oauth_manager.security_service, 'validate_state') as mock_validate_state:
                mock_validate_state.return_value = mock_state
                
                with patch.object(oauth_manager, 'get_provider') as mock_get_provider:
                    mock_provider = Mock()
                    mock_provider.exchange_code_for_tokens.return_value = {
                        "access_token": f"{provider}_access_token_123",
                        "refresh_token": f"{provider}_refresh_token_456",
                        "expires_in": 3600,
                        "token_type": "Bearer"
                    }
                    mock_provider.get_user_info.return_value = {
                        "id": f"{provider}_user_123",
                        "email": "test@example.com",
                        "name": "Test User"
                    }
                    mock_get_provider.return_value = mock_provider
                    
                    with patch.object(oauth_manager.integration_service, 'create_integration') as mock_create_integration:
                        mock_integration = Mock(spec=OAuthIntegration)
                        mock_integration.id = len(integrations) + 1
                        mock_integration.provider = provider
                        mock_create_integration.return_value = mock_integration
                        integrations.append(mock_integration)
                        
                        with patch.object(oauth_manager.token_service, 'store_tokens') as mock_store_tokens:
                            mock_token = Mock(spec=OAuthToken)
                            mock_store_tokens.return_value = [mock_token]
                            
                            result = await oauth_manager.handle_oauth_callback(
                                db=mock_db_session,
                                state_token=f"{provider}_state_token_123",
                                authorization_code=f"{provider}_auth_code_456",
                                provider_name=provider
                            )
                            
                            assert "integration_id" in result
                            assert result["provider"] == provider
        
        # Verify all providers were integrated
        assert len(integrations) == len(providers)
        for i, integration in enumerate(integrations):
            assert integration.provider == providers[i]

    @pytest.mark.asyncio
    async def test_oauth_flow_with_agent_tool_usage(self, oauth_manager, mock_db_session):
        """Test OAuth flow followed by agent tool usage."""
        user_id = 1
        provider = "notion"
        
        # Complete OAuth flow (simplified)
        mock_integration = Mock(spec=OAuthIntegration)
        mock_integration.id = 1
        mock_integration.user_id = user_id
        mock_integration.provider = provider
        mock_integration.status = "active"
        
        mock_token = Mock(spec=OAuthToken)
        mock_token.access_token = "notion_access_token_123"
        mock_token.refresh_token = "notion_refresh_token_456"
        
        # Use agent tool
        enhanced_notes_tool = EnhancedNotesTool()
        
        with patch.object(enhanced_notes_tool, 'notion_internal') as mock_notion_internal:
            mock_notion_internal.ensure_user_main_page_exists.return_value = "main_page_123"
            mock_notion_internal.create_user_page.return_value = "new_page_456"
            
            with patch('personal_assistant.config.database.db_config.get_session_context') as mock_context:
                mock_context.return_value.__aenter__.return_value = mock_db_session
                mock_context.return_value.__aexit__.return_value = None
                
                # Create multiple notes
                notes = [
                    ("Meeting notes", "Meeting Notes"),
                    ("Project ideas", "Project Ideas"),
                    ("Daily tasks", "Daily Tasks")
                ]
                
                results = []
                for content, title in notes:
                    result = await enhanced_notes_tool.create_enhanced_note(
                        content=content,
                        title=title,
                        user_id=user_id
                    )
                    results.append(result)
                
                # Verify all notes were created successfully
                assert len(results) == 3
                for result in results:
                    assert "Successfully created enhanced note" in result
                    assert "new_page_456" in result
