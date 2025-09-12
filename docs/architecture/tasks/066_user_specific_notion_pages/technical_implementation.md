# Technical Implementation Guide: User-Specific Notion Pages

## 🏗️ **Architecture Overview**

### **Current System Design (As of September 2024)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Current Notion System                        │
├─────────────────────────────────────────────────────────────────┤
│  User Request → Enhanced Notes Tool → Notion Client            │
│       ↓              ↓                    ↓                    │
│  AI Enhancement → Page Creation → Notion API (Single User)     │
└─────────────────────────────────────────────────────────────────┘
```

### **Target System Design (User-Specific Implementation)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    User-Specific Notion System                  │
├─────────────────────────────────────────────────────────────────┤
│  User Request → SessionService → OAuthTokenService → Notion    │
│       ↓              ↓              ↓              ↓           │
│  Tool Execution → NotionWorkspaceMgr → Page Creation → Notion  │
└─────────────────────────────────────────────────────────────────┘
```

### **Detailed Architecture Flow**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Request  │───▶│  SessionService  │───▶│  User Context   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ OAuthTokenService│◀───│OAuthIntegrationSvc│◀───│  User ID Lookup │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ NotionClient    │◀───│NotionClientFactory│◀───│  Access Token   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Notion API      │◀───│NotionWorkspaceMgr│◀───│  User-Specific  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Key Components**

#### **Current Components (Implemented)**

1. **EnhancedNotesTool**: AI-powered note management with LLM integration
2. **NotionPagesTool**: Basic Notion page management with bidirectional linking
3. **Notion Internal Functions**: Simplified page creation and management

#### **Existing OAuth Infrastructure (Available)**

1. **OAuthManager**: Complete OAuth 2.0 orchestration system
2. **OAuthTokenService**: Encrypted token storage, refresh, and validation
3. **OAuthIntegrationService**: User-specific OAuth connection management
4. **SessionService**: Redis-based user session management
5. **NotionOAuthProvider**: Notion-specific OAuth implementation
6. **OAuthSecurityService**: Token encryption and audit logging

#### **Components To Be Implemented**

1. **NotionClientFactory**: Creates user-specific Notion clients using existing OAuth
2. **NotionWorkspaceManager**: Manages user workspaces and pages
3. **Enhanced Tools**: Updated tools with user context integration

### **Implementation Status Matrix**

| Component                      | Status         | Implementation Effort | Dependencies        |
| ------------------------------ | -------------- | --------------------- | ------------------- |
| **OAuthManager**               | ✅ Complete    | N/A                   | None                |
| **OAuthTokenService**          | ✅ Complete    | N/A                   | None                |
| **OAuthIntegrationService**    | ✅ Complete    | N/A                   | None                |
| **SessionService**             | ✅ Complete    | N/A                   | None                |
| **NotionOAuthProvider**        | ✅ Complete    | N/A                   | None                |
| **OAuthSecurityService**       | ✅ Complete    | N/A                   | None                |
| **NotionClientFactory**        | ❌ Not Started | 1-2 days              | OAuth services      |
| **NotionWorkspaceManager**     | ❌ Not Started | 2-3 days              | NotionClientFactory |
| **Enhanced Tools Integration** | ❌ Not Started | 1-2 days              | Both above          |
| **Testing & Validation**       | ❌ Not Started | 1 day                 | All components      |

**Total Remaining Effort**: 5-8 days (down from original 10 days)

### **OAuth Infrastructure Mapping to Notion Requirements**

| Notion Requirement           | OAuth Component           | Status      | Usage                            |
| ---------------------------- | ------------------------- | ----------- | -------------------------------- |
| **User Identification**      | `SessionService`          | ✅ Complete | Get current user from session    |
| **Token Management**         | `OAuthTokenService`       | ✅ Complete | Get/refresh Notion access tokens |
| **User-Provider Connection** | `OAuthIntegrationService` | ✅ Complete | Manage user's Notion integration |
| **Notion OAuth Flow**        | `NotionOAuthProvider`     | ✅ Complete | Handle Notion-specific OAuth     |
| **Token Security**           | `OAuthSecurityService`    | ✅ Complete | Encrypt/decrypt tokens           |
| **OAuth Orchestration**      | `OAuthManager`            | ✅ Complete | Coordinate all OAuth operations  |
| **Audit Logging**            | `OAuthAuditLog`           | ✅ Complete | Track OAuth operations           |

### **Integration Points for Notion Tools**

```python
# Example: How to integrate existing OAuth with Notion tools
class UserSpecificNotionTool:
    def __init__(self, session_service: SessionService,
                 token_service: OAuthTokenService,
                 integration_service: OAuthIntegrationService):
        self.session_service = session_service
        self.token_service = token_service
        self.integration_service = integration_service

    async def get_user_notion_client(self, session_id: str) -> Client:
        # 1. Get user from session (existing)
        user_id = await self.session_service.get_current_user_id(session_id)

        # 2. Get user's Notion integration (existing)
        integration = await self.integration_service.get_integration_by_provider(
            db, user_id, "notion"
        )

        # 3. Get valid access token (existing)
        token = await self.token_service.get_valid_access_token(
            db, integration.id
        )

        # 4. Create Notion client (new)
        return Client(auth=token)
```

## 📊 **Current Implementation Status**

### **What's Currently Working (September 2024)**

1. **Enhanced Notes Tool** ✅

   - AI-powered note creation and enhancement
   - LLM integration for content improvement
   - Smart search and note intelligence features
   - Registered in main tool registry

2. **Notion Pages Tool** ✅

   - Basic CRUD operations for Notion pages
   - Bidirectional linking between pages
   - Table of contents management
   - Search functionality

3. **Notion Internal Functions** ✅

   - Simplified `ensure_main_page_exists` function
   - Removed async/await complexity
   - Better error handling

4. **Dynamic Page Creation** ✅
   - "Table of Contents" page creation already implemented
   - Auto-creation when page doesn't exist
   - Page structure and content management

### **What Needs to Be Implemented**

1. **User Context Integration** ❌

   - No user-specific context in Notion operations
   - All users share the same Notion workspace
   - No OAuth token management per user

2. **Workspace Isolation** ❌

   - No user-specific "Personal Assistant" pages
   - Hardcoded `settings.NOTION_ROOT_PAGE_ID`
   - No user data separation

3. **Multi-User Support** ❌
   - Single-user architecture
   - No user authentication context
   - Security vulnerabilities

## 🔧 **Implementation Details**

### **0. Using Existing OAuth Infrastructure** ✅ **Already Available**

#### **Getting User Context**

```python
from personal_assistant.auth.session_service import SessionService
from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.services.integration_service import OAuthIntegrationService

# Get current user from session
session_service = SessionService(redis_client)
user_id = await session_service.get_current_user_id(session_id)

# Get user's Notion OAuth integration
integration_service = OAuthIntegrationService()
notion_integration = await integration_service.get_integration_by_provider(
    db, user_id, "notion"
)

# Get user's Notion access token
token_service = OAuthTokenService()
access_token = await token_service.get_valid_access_token(
    db, notion_integration.id
)
```

#### **Creating User-Specific Notion Client**

```python
from notion_client import Client
from personal_assistant.oauth.services.token_service import OAuthTokenService

class UserSpecificNotionClient:
    def __init__(self, user_id: int, db: AsyncSession):
        self.user_id = user_id
        self.db = db
        self.token_service = OAuthTokenService()

    async def get_client(self) -> Client:
        # Get user's Notion integration
        integration = await self.get_notion_integration()

        # Get valid access token
        token = await self.token_service.get_valid_access_token(
            self.db, integration.id
        )

        # Create Notion client with user's token
        return Client(auth=token)
```

### **1. User Context Service** ✅ **Already Available**

#### **File**: `src/personal_assistant/oauth/services/user_context_service.py`

```python
"""
User Context Service for Notion Operations

This service manages user context and OAuth token retrieval for Notion operations.
"""

from typing import Optional, Dict, Any
import logging
from ..models.oauth_connection import OAuthConnection
from ...database.services.oauth_service import OAuthService
from ...config.logging_config import get_logger

logger = get_logger(__name__)

class UserContextService:
    """Service for managing user context in Notion operations"""

    def __init__(self):
        self.oauth_service = OAuthService()
        self.logger = logger

    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user from request context

        Returns:
            User information dictionary or None if not found
        """
        try:
            # Implementation depends on your auth system
            # This is a placeholder - adapt to your actual auth implementation
            from fastapi import Request
            from starlette.requests import Request as StarletteRequest

            # Get user from request context
            # You may need to adapt this based on your auth middleware
            request = getattr(self, '_current_request', None)
            if not request:
                self.logger.warning("No request context available")
                return None

            user = getattr(request.state, 'user', None)
            if not user:
                self.logger.warning("No user in request state")
                return None

            return {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }

        except Exception as e:
            self.logger.error(f"Error getting current user: {e}")
            return None

    async def get_user_notion_token(self, user_id: str) -> Optional[str]:
        """
        Get user's Notion access token from OAuth system

        Args:
            user_id: User identifier

        Returns:
            Notion access token or None if not found
        """
        try:
            # Get OAuth connection for user and Notion provider
            connection = await self.oauth_service.get_connection(
                user_id=user_id,
                provider="notion"
            )

            if not connection:
                self.logger.warning(f"No Notion connection found for user {user_id}")
                return None

            if not connection.access_token:
                self.logger.warning(f"No access token for user {user_id}")
                return None

            # Validate token is not expired
            if connection.is_expired():
                self.logger.info(f"Token expired for user {user_id}, attempting refresh")
                try:
                    refreshed = await self.oauth_service.refresh_token(
                        user_id=user_id,
                        provider="notion"
                    )
                    if refreshed:
                        return refreshed.access_token
                except Exception as refresh_error:
                    self.logger.error(f"Token refresh failed for user {user_id}: {refresh_error}")
                    return None

            return connection.access_token

        except Exception as e:
            self.logger.error(f"Error getting Notion token for user {user_id}: {e}")
            return None

    async def validate_user_workspace(self, user_id: str) -> bool:
        """
        Validate user has access to their Notion workspace

        Args:
            user_id: User identifier

        Returns:
            True if user has valid workspace access
        """
        try:
            access_token = await self.get_user_notion_token(user_id)
            if not access_token:
                return False

            # Test workspace access by making a simple API call
            from notion_client import Client

            client = Client(auth=access_token)

            # Try to search for pages in user's workspace
            response = client.search(
                query="",
                filter={"property": "object", "value": "page"},
                page_size=1
            )

            # If we get a response, the workspace is accessible
            return "results" in response

        except Exception as e:
            self.logger.error(f"Error validating workspace for user {user_id}: {e}")
            return False

    def set_request_context(self, request):
        """Set request context for user identification"""
        self._current_request = request
```

### **2. Notion Client Factory**

#### **File**: `src/personal_assistant/tools/notion_pages/client_factory.py`

```python
"""
Notion Client Factory for User-Specific Clients

This factory creates and manages user-specific Notion clients with caching.
"""

from typing import Optional, Dict
import logging
from notion_client import Client
from ...oauth.services.user_context_service import UserContextService
from ...config.logging_config import get_logger

logger = get_logger(__name__)

class NotionClientFactory:
    """Factory for creating user-specific Notion clients"""

    def __init__(self):
        self.user_context_service = UserContextService()
        self._client_cache: Dict[str, Client] = {}
        self.logger = logger

    def create_user_client(self, access_token: str) -> Client:
        """
        Create Notion client with user's access token

        Args:
            access_token: User's Notion access token

        Returns:
            Configured Notion client
        """
        try:
            client = Client(auth=access_token)
            self.logger.debug("Created Notion client for user")
            return client
        except Exception as e:
            self.logger.error(f"Error creating Notion client: {e}")
            raise

    async def get_user_client(self, user_id: str) -> Client:
        """
        Get or create Notion client for user

        Args:
            user_id: User identifier

        Returns:
            User-specific Notion client

        Raises:
            NotionNotConnectedError: If user hasn't connected Notion
            NotionTokenExpiredError: If token is expired and can't be refreshed
        """
        try:
            # Check cache first
            if user_id in self._client_cache:
                self.logger.debug(f"Using cached Notion client for user {user_id}")
                return self._client_cache[user_id]

            # Get user's access token
            access_token = await self.user_context_service.get_user_notion_token(user_id)
            if not access_token:
                raise NotionNotConnectedError(f"User {user_id} must connect Notion account")

            # Create client
            client = self.create_user_client(access_token)

            # Cache client
            self._client_cache[user_id] = client
            self.logger.info(f"Created and cached Notion client for user {user_id}")

            return client

        except Exception as e:
            self.logger.error(f"Error getting Notion client for user {user_id}: {e}")
            raise

    def invalidate_user_client(self, user_id: str):
        """Invalidate cached client for user (e.g., after token refresh)"""
        if user_id in self._client_cache:
            del self._client_cache[user_id]
            self.logger.debug(f"Invalidated cached client for user {user_id}")

    def clear_cache(self):
        """Clear all cached clients"""
        self._client_cache.clear()
        self.logger.debug("Cleared all cached Notion clients")

# Custom exceptions
class NotionNotConnectedError(Exception):
    """Raised when user hasn't connected Notion account"""
    pass

class NotionTokenExpiredError(Exception):
    """Raised when Notion token is expired and can't be refreshed"""
    pass
```

### **3. Notion Workspace Manager**

#### **File**: `src/personal_assistant/tools/notion_pages/workspace_manager.py`

```python
"""
Notion Workspace Manager for User-Specific Workspaces

This manager handles user-specific Notion workspace operations.
"""

from typing import Optional, Dict, Any
import logging
from notion_client import Client
from ...config.logging_config import get_logger

logger = get_logger(__name__)

class NotionWorkspaceManager:
    """Manages user-specific Notion workspaces"""

    def __init__(self):
        self.logger = logger

    async def ensure_user_root_page(self, client: Client, user_id: str) -> str:
        """
        Ensure user has Personal Assistant page in their workspace

        Args:
            client: User-specific Notion client
            user_id: User identifier

        Returns:
            Page ID of the Personal Assistant page

        Raises:
            NotionWorkspaceError: If workspace is not accessible
            NotionPageCreationError: If page creation fails
        """
        try:
            # First, try to find existing page
            existing_page_id = await self.find_user_root_page(client, user_id)
            if existing_page_id:
                self.logger.info(f"Found existing Personal Assistant page for user {user_id}")
                return existing_page_id

            # Create new page if not found
            self.logger.info(f"Creating Personal Assistant page for user {user_id}")
            return await self.create_user_root_page(client, user_id)

        except Exception as e:
            self.logger.error(f"Error ensuring user root page for user {user_id}: {e}")
            raise

    async def create_user_root_page(self, client: Client, user_id: str) -> str:
        """
        Create Personal Assistant page in user's workspace

        Args:
            client: User-specific Notion client
            user_id: User identifier

        Returns:
            Page ID of the created page
        """
        try:
            # Get user's workspace root (first accessible page)
            workspace_root_id = await self._get_workspace_root(client)

            # Create Personal Assistant page
            personal_assistant_page = client.pages.create(
                parent={"type": "page_id", "page_id": workspace_root_id},
                properties={
                    "title": [{"type": "text", "text": {"content": "Personal Assistant"}}]
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": "Welcome to your personal assistant notes! This page serves as the table of contents for all your note pages."}
                            }]
                        }
                    }
                ]
            )

            page_id = personal_assistant_page["id"]
            self.logger.info(f"Created Personal Assistant page {page_id} for user {user_id}")
            return page_id

        except Exception as e:
            self.logger.error(f"Error creating Personal Assistant page for user {user_id}: {e}")
            raise NotionPageCreationError(f"Failed to create Personal Assistant page: {e}")

    async def find_user_root_page(self, client: Client, user_id: str) -> Optional[str]:
        """
        Find existing Personal Assistant page in user's workspace

        Args:
            client: User-specific Notion client
            user_id: User identifier

        Returns:
            Page ID if found, None otherwise
        """
        try:
            # Search for pages with "Personal Assistant" title
            response = client.search(
                query="Personal Assistant",
                filter={"property": "object", "value": "page"}
            )

            for page in response.get("results", []):
                # Check if page is not archived
                if page.get("archived", False):
                    continue

                # Check if title matches exactly
                title_property = page.get("properties", {}).get("title", {})
                title_text = title_property.get("title", [{}])[0].get("plain_text", "")

                if title_text == "Personal Assistant":
                    self.logger.debug(f"Found Personal Assistant page {page['id']} for user {user_id}")
                    return page["id"]

            return None

        except Exception as e:
            self.logger.error(f"Error finding Personal Assistant page for user {user_id}: {e}")
            return None

    async def _get_workspace_root(self, client: Client) -> str:
        """
        Get the root page of the user's workspace

        Args:
            client: User-specific Notion client

        Returns:
            Page ID of the workspace root
        """
        try:
            # Search for pages in the workspace
            response = client.search(
                query="",
                filter={"property": "object", "value": "page"},
                page_size=1
            )

            if not response.get("results"):
                raise NotionWorkspaceError("No accessible pages found in workspace")

            # Return the first accessible page as workspace root
            workspace_root = response["results"][0]
            return workspace_root["id"]

        except Exception as e:
            self.logger.error(f"Error getting workspace root: {e}")
            raise NotionWorkspaceError(f"Failed to access workspace: {e}")

# Custom exceptions
class NotionWorkspaceError(Exception):
    """Raised when workspace is not accessible"""
    pass

class NotionPageCreationError(Exception):
    """Raised when page creation fails"""
    pass
```

### **4. Updated Enhanced Notes Tool**

#### **File**: `src/personal_assistant/tools/notes/enhanced_notes_tool.py` (Key Changes)

```python
# Add these imports at the top
from ..notion_pages.client_factory import NotionClientFactory, NotionNotConnectedError
from ..notion_pages.workspace_manager import NotionWorkspaceManager
from ...oauth.services.user_context_service import UserContextService

class EnhancedNotesTool:
    def __init__(self):
        # ... existing initialization ...

        # Add new dependencies
        self.user_context_service = UserContextService()
        self.client_factory = NotionClientFactory()
        self.workspace_manager = NotionWorkspaceManager()

    async def create_enhanced_note(
        self,
        content: str,
        title: Optional[str] = None,
        note_type: Optional[str] = None,
        auto_tags: bool = True
    ) -> Union[str, Dict]:
        """Create a new note with AI-powered enhancement"""
        try:
            self.logger.info(f"Creating enhanced note: {title or 'Untitled'}")

            # Get current user context
            user = await self.user_context_service.get_current_user()
            if not user:
                return {
                    "error": "User context not available",
                    "message": "Please ensure you are logged in"
                }

            user_id = user['id']
            self.logger.info(f"Creating note for user: {user_id}")

            # Get user-specific Notion client
            try:
                notion_client = await self.client_factory.get_user_client(user_id)
            except NotionNotConnectedError:
                return {
                    "error": "Notion not connected",
                    "message": "Please connect your Notion account in settings"
                }
            except Exception as e:
                return {
                    "error": "Notion connection failed",
                    "message": f"Failed to connect to Notion: {str(e)}"
                }

            # Ensure user has root page
            try:
                main_page_id = await self.workspace_manager.ensure_user_root_page(
                    notion_client, user_id
                )
            except Exception as e:
                return {
                    "error": "Workspace setup failed",
                    "message": f"Failed to setup Notion workspace: {str(e)}"
                }

            # ... rest of existing logic using notion_client and main_page_id ...

            # Create note in Notion
            note_page = notion_client.pages.create(
                parent={"type": "page_id", "page_id": main_page_id},
                properties=properties,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": final_content}}]
                        }
                    }
                ]
            )

            # ... rest of existing logic ...

        except Exception as e:
            self.logger.error(f"Error creating enhanced note: {e}")
            return {
                "error": "Note creation failed",
                "message": f"Failed to create note: {str(e)}"
            }
```

### **5. Updated Notion Internal Functions**

#### **File**: `src/personal_assistant/tools/notion_pages/notion_internal.py` (Key Changes)

```python
# Update the ensure_main_page_exists function
async def ensure_main_page_exists(
    client: Client,
    user_id: str,  # NEW: User context parameter
    main_page_id: Optional[str] = None
) -> str:
    """
    Ensure the main table of contents page exists, create if it doesn't.

    Args:
        client: User-specific Notion client
        user_id: User identifier
        main_page_id: Optional specific page ID to use

    Returns:
        Page ID of the main table of contents page
    """
    if main_page_id:
        return main_page_id

    try:
        # Use workspace manager to ensure user has root page
        from .workspace_manager import NotionWorkspaceManager
        workspace_manager = NotionWorkspaceManager()

        # Ensure user has Personal Assistant page
        user_root_page_id = await workspace_manager.ensure_user_root_page(client, user_id)

        # Search for existing Table of Contents page under user's root page
        response = client.search(
            query="Table of Contents",
            filter={"property": "object", "value": "page"}
        )

        for page in response.get("results", []):
            page_title = (
                page.get("properties", {})
                .get("title", {})
                .get("title", [{}])[0]
                .get("plain_text", "")
            )
            is_archived = page.get("archived", False)

            if page_title == "Table of Contents" and not is_archived:
                logger.info(f"Found existing Table of Contents page: {page['id']}")
                return page["id"]

        # Create Table of Contents page under user's root page
        logger.info(f"Creating Table of Contents page under user root: {user_root_page_id}")
        main_page = client.pages.create(
            parent={"type": "page_id", "page_id": user_root_page_id},
            properties={
                "title": [{"type": "text", "text": {"content": "Table of Contents"}}]
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Welcome to your notes! This page serves as the table of contents for all your note pages."
                                },
                            }
                        ]
                    },
                }
            ],
        )

        created_main_page_id = main_page["id"]
        logger.info(f"Created Table of Contents page: {created_main_page_id}")
        return created_main_page_id

    except Exception as e:
        logger.error(f"Error ensuring main page exists: {e}")
        raise
```

## 🧪 **Testing Implementation**

### **Unit Tests Example**

#### **File**: `tests/unit/test_user_context_service.py`

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.personal_assistant.oauth.services.user_context_service import UserContextService

class TestUserContextService:
    @pytest.fixture
    def service(self):
        return UserContextService()

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, service):
        """Test successful user retrieval"""
        # Mock request context
        mock_request = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_request.state.user = mock_user

        service.set_request_context(mock_request)

        user = await service.get_current_user()

        assert user is not None
        assert user['id'] == "user123"
        assert user['email'] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_no_context(self, service):
        """Test user retrieval when no context available"""
        user = await service.get_current_user()
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_notion_token_success(self, service):
        """Test successful token retrieval"""
        with patch.object(service.oauth_service, 'get_connection') as mock_get_connection:
            mock_connection = Mock()
            mock_connection.access_token = "test_token"
            mock_connection.is_expired.return_value = False
            mock_get_connection.return_value = mock_connection

            token = await service.get_user_notion_token("user123")

            assert token == "test_token"
            mock_get_connection.assert_called_once_with(
                user_id="user123",
                provider="notion"
            )

    @pytest.mark.asyncio
    async def test_get_user_notion_token_not_connected(self, service):
        """Test token retrieval when user not connected"""
        with patch.object(service.oauth_service, 'get_connection') as mock_get_connection:
            mock_get_connection.return_value = None

            token = await service.get_user_notion_token("user123")

            assert token is None
```

### **Integration Tests Example**

#### **File**: `tests/integration/test_user_specific_notion.py`

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool

class TestUserSpecificNotion:
    @pytest.fixture
    def tool(self):
        return EnhancedNotesTool()

    @pytest.mark.asyncio
    async def test_create_enhanced_note_success(self, tool):
        """Test successful note creation with user context"""
        # Mock user context
        with patch.object(tool.user_context_service, 'get_current_user') as mock_get_user:
            mock_get_user.return_value = {'id': 'user123', 'email': 'test@example.com'}

            # Mock Notion client
            with patch.object(tool.client_factory, 'get_user_client') as mock_get_client:
                mock_client = Mock()
                mock_get_client.return_value = mock_client

                # Mock workspace manager
                with patch.object(tool.workspace_manager, 'ensure_user_root_page') as mock_ensure_root:
                    mock_ensure_root.return_value = "root_page_123"

                    # Mock LLM enhancer
                    with patch.object(tool.llm_enhancer, 'enhance_note_content') as mock_enhance:
                        mock_enhanced_note = Mock()
                        mock_enhanced_note.enhanced_content = "Enhanced content"
                        mock_enhanced_note.enhanced_title = "Enhanced title"
                        mock_enhanced_note.suggested_tags = ["tag1", "tag2"]
                        mock_enhanced_note.note_type.value = "personal"
                        mock_enhance.return_value = mock_enhanced_note

                        # Mock Notion API calls
                        mock_client.pages.create.return_value = {"id": "note_page_123"}
                        mock_client.pages.update.return_value = {}

                        # Test note creation
                        result = await tool.create_enhanced_note("Test content")

                        # Verify success
                        assert "successfully created" in result
                        mock_client.pages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_enhanced_note_notion_not_connected(self, tool):
        """Test note creation when Notion not connected"""
        # Mock user context
        with patch.object(tool.user_context_service, 'get_current_user') as mock_get_user:
            mock_get_user.return_value = {'id': 'user123', 'email': 'test@example.com'}

            # Mock Notion client factory to raise NotionNotConnectedError
            with patch.object(tool.client_factory, 'get_user_client') as mock_get_client:
                from ..notion_pages.client_factory import NotionNotConnectedError
                mock_get_client.side_effect = NotionNotConnectedError("Not connected")

                # Test note creation
                result = await tool.create_enhanced_note("Test content")

                # Verify error handling
                assert "error" in result
                assert "Notion not connected" in result["error"]
```

## 🔒 **Security Considerations**

### **1. Token Security**

```python
def sanitize_logs(data: dict) -> dict:
    """Remove sensitive tokens from logs"""
    sanitized = data.copy()
    sensitive_keys = ['access_token', 'refresh_token', 'client_secret']

    for key in sensitive_keys:
        if key in sanitized:
            sanitized[key] = "***REDACTED***"

    return sanitized

# Use in logging
self.logger.info(f"User context: {sanitize_logs(user_context)}")
```

### **2. User Isolation Validation**

```python
def validate_user_isolation(user_id: str, page_id: str, client: Client) -> bool:
    """Ensure page belongs to user's workspace"""
    try:
        # Get page details
        page = client.pages.retrieve(page_id)

        # Check if page is accessible (belongs to user's workspace)
        # This is implicit - if we can retrieve it, it's in user's workspace
        return True

    except Exception:
        return False
```

### **3. Error Information Sanitization**

```python
def sanitize_error_message(error: Exception) -> str:
    """Sanitize error messages to avoid information leakage"""
    error_str = str(error)

    # Remove sensitive information
    sensitive_patterns = [
        r'access_token=[^\s&]+',
        r'refresh_token=[^\s&]+',
        r'client_secret=[^\s&]+',
    ]

    for pattern in sensitive_patterns:
        error_str = re.sub(pattern, '***REDACTED***', error_str)

    return error_str
```

## 📊 **Performance Optimizations**

### **1. Client Caching**

```python
class NotionClientCache:
    """Advanced caching for Notion clients"""

    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self._clients = {}
        self._timestamps = {}
        self.max_size = max_size
        self.ttl = ttl

    async def get_client(self, user_id: str, token: str) -> Client:
        """Get cached client or create new one"""
        now = time.time()

        # Check if client exists and is not expired
        if user_id in self._clients:
            if now - self._timestamps[user_id] < self.ttl:
                return self._clients[user_id]
            else:
                # Remove expired client
                del self._clients[user_id]
                del self._timestamps[user_id]

        # Create new client
        client = Client(auth=token)

        # Cache client
        self._clients[user_id] = client
        self._timestamps[user_id] = now

        # Clean up if cache is full
        if len(self._clients) > self.max_size:
            self._cleanup_oldest()

        return client
```

### **2. Async Operations**

```python
async def batch_ensure_user_pages(user_ids: List[str]) -> Dict[str, str]:
    """Batch ensure user pages for multiple users"""
    tasks = []
    for user_id in user_ids:
        task = ensure_user_root_page_async(user_id)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        user_id: result for user_id, result in zip(user_ids, results)
        if not isinstance(result, Exception)
    }
```

This technical implementation provides a comprehensive foundation for implementing user-specific Notion pages with proper security, performance, and error handling considerations.
