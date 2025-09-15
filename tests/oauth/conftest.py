"""
OAuth Test Configuration and Fixtures

This module provides shared test fixtures and configuration for OAuth testing.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.oauth.oauth_manager import OAuthManager
from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.services.integration_service import OAuthIntegrationService
from personal_assistant.oauth.services.security_service import OAuthSecurityService
from personal_assistant.oauth.services.consent_service import OAuthConsentService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for testing."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def oauth_manager() -> OAuthManager:
    """Provide an OAuth manager instance for testing."""
    return OAuthManager()


@pytest.fixture
def token_service() -> OAuthTokenService:
    """Provide a token service instance for testing."""
    return OAuthTokenService()


@pytest.fixture
def integration_service() -> OAuthIntegrationService:
    """Provide an integration service instance for testing."""
    return OAuthIntegrationService()


@pytest.fixture
def security_service() -> OAuthSecurityService:
    """Provide a security service instance for testing."""
    return OAuthSecurityService()


@pytest.fixture
def consent_service() -> OAuthConsentService:
    """Provide a consent service instance for testing."""
    return OAuthConsentService()


@pytest.fixture
def mock_oauth_provider():
    """Provide a mock OAuth provider for testing."""
    provider = Mock()
    provider.get_authorization_url = Mock(return_value="https://example.com/auth")
    provider.exchange_code_for_tokens = Mock(return_value={
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600,
        "token_type": "Bearer"
    })
    provider.refresh_access_token = Mock(return_value={
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600
    })
    provider.get_user_info = Mock(return_value={
        "id": "test_user_id",
        "email": "test@example.com",
        "name": "Test User"
    })
    provider.validate_token = Mock(return_value=True)
    return provider


@pytest.fixture
def mock_user_data() -> Dict[str, Any]:
    """Provide mock user data for testing."""
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True
    }


@pytest.fixture
def mock_oauth_tokens() -> Dict[str, Any]:
    """Provide mock OAuth tokens for testing."""
    return {
        "access_token": "mock_access_token_123",
        "refresh_token": "mock_refresh_token_456",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "read write"
    }


@pytest.fixture
def mock_oauth_integration() -> Dict[str, Any]:
    """Provide mock OAuth integration data for testing."""
    return {
        "id": 1,
        "user_id": 1,
        "provider": "google",
        "status": "active",
        "scopes": ["read", "write"],
        "provider_user_id": "google_user_123",
        "provider_email": "test@example.com",
        "provider_name": "Test User"
    }


@pytest.fixture
def mock_notion_client():
    """Provide a mock Notion client for testing."""
    client = Mock()
    client.pages.create = AsyncMock(return_value={"id": "page_123"})
    client.pages.retrieve = AsyncMock(return_value={"id": "page_123", "title": "Test Page"})
    client.pages.update = AsyncMock(return_value={"id": "page_123"})
    client.search = AsyncMock(return_value={"results": []})
    return client


@pytest.fixture
def mock_google_calendar_client():
    """Provide a mock Google Calendar client for testing."""
    client = Mock()
    client.events().list = Mock()
    client.events().list().execute = Mock(return_value={"items": []})
    client.events().insert = Mock()
    client.events().insert().execute = Mock(return_value={"id": "event_123"})
    return client


@pytest.fixture
def mock_gmail_client():
    """Provide a mock Gmail client for testing."""
    client = Mock()
    client.users().messages().list = Mock()
    client.users().messages().list().execute = Mock(return_value={"messages": []})
    client.users().messages().send = Mock()
    client.users().messages().send().execute = Mock(return_value={"id": "message_123"})
    return client


@pytest.fixture
def mock_youtube_client():
    """Provide a mock YouTube client for testing."""
    client = Mock()
    client.channels().list = Mock()
    client.channels().list().execute = Mock(return_value={"items": []})
    client.videos().list = Mock()
    client.videos().list().execute = Mock(return_value={"items": []})
    return client


@pytest.fixture
def mock_microsoft_graph_client():
    """Provide a mock Microsoft Graph client for testing."""
    client = Mock()
    client.me.calendar.events.get = Mock(return_value={"value": []})
    client.me.messages.get = Mock(return_value={"value": []})
    client.me.send_mail = Mock()
    return client


@pytest.fixture
def oauth_test_config() -> Dict[str, Any]:
    """Provide OAuth test configuration."""
    return {
        "google": {
            "client_id": "test_google_client_id",
            "client_secret": "test_google_client_secret",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/callback",
            "scopes": ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/gmail.readonly"]
        },
        "microsoft": {
            "client_id": "test_microsoft_client_id",
            "client_secret": "test_microsoft_client_secret",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/callback",
            "scopes": ["https://graph.microsoft.com/calendars.read", "https://graph.microsoft.com/mail.read"]
        },
        "notion": {
            "client_id": "test_notion_client_id",
            "client_secret": "test_notion_client_secret",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/callback",
            "scopes": ["read", "write"]
        },
        "youtube": {
            "client_id": "test_youtube_client_id",
            "client_secret": "test_youtube_client_secret",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/callback",
            "scopes": ["https://www.googleapis.com/auth/youtube.readonly"]
        }
    }


@pytest.fixture
def mock_oauth_state() -> Dict[str, Any]:
    """Provide mock OAuth state data for testing."""
    return {
        "id": 1,
        "state_token": "test_state_token_123",
        "provider": "google",
        "user_id": 1,
        "scopes": ["read", "write"],
        "redirect_uri": "http://localhost:8000/api/v1/oauth/callback",
        "is_used": False,
        "expires_at": None
    }
