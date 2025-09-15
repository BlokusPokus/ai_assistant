# Technical Implementation Guide: User-Specific Email with Outlook

## 🏗️ **Architecture Overview**

### **Current System Design (As of September 2024)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Current Email System                         │
├─────────────────────────────────────────────────────────────────┤
│  User Request → Email Tool → Microsoft Graph API (Single User) │
│       ↓              ↓                    ↓                    │
│  Email Operations → API Calls → Microsoft Graph (Hardcoded)    │
└─────────────────────────────────────────────────────────────────┘
```

### **Target System Design (User-Specific Implementation)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    User-Specific Email System                   │
├─────────────────────────────────────────────────────────────────┤
│  User Request → SessionService → OAuthTokenService → Microsoft  │
│       ↓              ↓              ↓              ↓           │
│  Tool Execution → EmailWorkspaceMgr → Email Operations → Graph  │
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
│ GraphServiceClient│◀───│EmailClientFactory│◀───│  Access Token   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Microsoft Graph │◀───│EmailWorkspaceMgr│◀───│  User-Specific  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 **Implementation Details**

### **1. Email Client Factory**

#### **File**: `src/personal_assistant/tools/emails/email_client_factory.py`

```python
"""
Email Client Factory for User-Specific Clients

This factory creates and manages user-specific Microsoft Graph email clients using the existing
OAuth infrastructure for secure, user-isolated email operations.
"""

import logging
from typing import Optional, Dict
from msgraph import GraphServiceClient
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.services.integration_service import OAuthIntegrationService
from personal_assistant.auth.session_service import SessionService
from personal_assistant.config.logging_config import get_logger

logger = get_logger(__name__)


class EmailClientFactory:
    """Factory for creating user-specific Microsoft Graph email clients using OAuth services"""

    def __init__(self):
        self.token_service = OAuthTokenService()
        self.integration_service = OAuthIntegrationService()
        self._client_cache: Dict[str, GraphServiceClient] = {}
        self.logger = logger

    async def get_user_client(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: Optional[str] = None
    ) -> GraphServiceClient:
        """
        Get or create Microsoft Graph client for a specific user.

        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session ID for additional validation

        Returns:
            User-specific Microsoft Graph client

        Raises:
            MicrosoftNotConnectedError: If user hasn't connected Microsoft account
            MicrosoftTokenExpiredError: If token is expired and can't be refreshed
            MicrosoftEmailError: If email access is not available
        """
        try:
            # Check cache first
            cache_key = f"user_{user_id}"
            if cache_key in self._client_cache:
                self.logger.debug(f"Using cached Microsoft Graph client for user {user_id}")
                return self._client_cache[cache_key]

            # Get user's Microsoft integration
            integration = await self.integration_service.get_integration_by_user_and_provider(
                db, user_id, "microsoft"
            )

            if not integration:
                raise MicrosoftNotConnectedError(f"User {user_id} must connect Microsoft account")

            # Get valid access token
            access_token = await self.token_service.get_valid_token(
                db, integration.id
            )

            if not access_token:
                raise MicrosoftTokenExpiredError(f"Could not get valid token for user {user_id}")

            # Create Microsoft Graph client
            from msgraph import GraphServiceClient
            from msgraph.generated.models.o_data_errors.o_data_error import ODataError

            # Create credentials
            credentials = {
                'access_token': access_token
            }

            client = GraphServiceClient(credentials=credentials)

            # Validate email access
            if not await self._validate_email_access(client):
                raise MicrosoftEmailError(f"User {user_id} doesn't have email access")

            # Cache client
            self._client_cache[cache_key] = client
            self.logger.info(f"Created and cached Microsoft Graph client for user {user_id}")

            return client

        except Exception as e:
            self.logger.error(f"Error getting Microsoft Graph client for user {user_id}: {e}")
            if isinstance(e, (MicrosoftNotConnectedError, MicrosoftTokenExpiredError, MicrosoftEmailError)):
                raise
            raise MicrosoftEmailError(f"Failed to create Microsoft Graph client: {e}")

    async def _validate_email_access(self, client: GraphServiceClient) -> bool:
        """
        Validate that the client has access to email operations.

        Args:
            client: Microsoft Graph client to validate

        Returns:
            True if email access is available
        """
        try:
            # Test email access by making a simple API call
            from msgraph.generated.users.item.mail_folders.mail_folders_request_builder import MailFoldersRequestBuilder

            # Try to get user's mail folders
            response = await client.me.mail_folders.get()

            # If we get a response, email access is available
            return response is not None

        except Exception as e:
            self.logger.error(f"Error validating email access: {e}")
            return False

    def invalidate_user_client(self, user_id: int):
        """Invalidate cached client for user (e.g., after token refresh)"""
        cache_key = f"user_{user_id}"
        if cache_key in self._client_cache:
            del self._client_cache[cache_key]
            self.logger.debug(f"Invalidated cached client for user {user_id}")

    def clear_cache(self):
        """Clear all cached clients"""
        self._client_cache.clear()
        self.logger.debug("Cleared all cached Microsoft Graph clients")


# Custom exceptions
class MicrosoftNotConnectedError(Exception):
    """Raised when user hasn't connected Microsoft account"""
    pass


class MicrosoftTokenExpiredError(Exception):
    """Raised when Microsoft token is expired and can't be refreshed"""
    pass


class MicrosoftEmailError(Exception):
    """Raised when email operation fails"""
    pass
```

### **2. Email Workspace Manager**

#### **File**: `src/personal_assistant/tools/emails/email_workspace_manager.py`

```python
"""
Email Workspace Manager for User-Specific Email Operations

This manager handles user-specific email operations, including
validating access, managing folders, and handling email operations.
"""

import logging
from typing import Optional, List, Dict, Any
from msgraph import GraphServiceClient
from msgraph.generated.models.mail_folder import MailFolder
from sqlalchemy.ext.asyncio import AsyncSession

from .email_client_factory import EmailClientFactory, MicrosoftNotConnectedError, MicrosoftEmailError
from personal_assistant.config.logging_config import get_logger

logger = get_logger(__name__)


class EmailWorkspaceManager:
    """Manages user-specific email operations and validation"""

    def __init__(self):
        self.client_factory = EmailClientFactory()
        self.logger = logger

    async def validate_user_email_access(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Validate user has access to their email.

        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session ID for additional validation

        Returns:
            True if user has valid email access
        """
        try:
            # Get user-specific Microsoft Graph client
            client = await self.client_factory.get_user_client(db, user_id, session_id)

            # Test email access by making a simple API call
            response = await client.me.mail_folders.get()

            # If we get a response, email access is available
            return response is not None

        except Exception as e:
            self.logger.error(f"Error validating email access for user {user_id}: {e}")
            return False

    async def get_user_folders(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's email folders.

        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session ID for additional validation

        Returns:
            List of email folders
        """
        try:
            # Get user-specific Microsoft Graph client
            client = await self.client_factory.get_user_client(db, user_id, session_id)

            # Get mail folders
            response = await client.me.mail_folders.get()

            folders = []
            for folder in response.value:
                folders.append({
                    'id': folder.id,
                    'name': folder.display_name,
                    'unread_count': folder.unread_item_count,
                    'total_count': folder.total_item_count
                })

            return folders

        except Exception as e:
            self.logger.error(f"Error getting folders for user {user_id}: {e}")
            raise MicrosoftEmailError(f"Failed to get email folders: {e}")

    async def search_user_emails(
        self,
        db: AsyncSession,
        user_id: int,
        query: str = "",
        folder_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for emails in user's account.

        Args:
            db: Database session
            user_id: User identifier
            query: Search query
            folder_id: Optional folder ID to search in
            session_id: Optional session ID for additional validation

        Returns:
            List of emails matching the search criteria
        """
        try:
            # Get user-specific Microsoft Graph client
            client = await self.client_factory.get_user_client(db, user_id, session_id)

            # Build search request
            if folder_id:
                # Search in specific folder
                response = await client.me.mail_folders.by_mail_folder_id(folder_id).messages.get()
            else:
                # Search in all folders
                response = await client.me.messages.get()

            emails = []
            for message in response.value:
                emails.append({
                    'id': message.id,
                    'subject': message.subject,
                    'from': message.from_.email_address.address if message.from_ else None,
                    'to': [recipient.email_address.address for recipient in message.to_recipients] if message.to_recipients else [],
                    'received_time': message.received_date_time.isoformat() if message.received_date_time else None,
                    'is_read': message.is_read,
                    'has_attachments': message.has_attachments
                })

            return emails

        except Exception as e:
            self.logger.error(f"Error searching emails for user {user_id}: {e}")
            raise MicrosoftEmailError(f"Failed to search emails: {e}")

    async def send_user_email(
        self,
        db: AsyncSession,
        user_id: int,
        to: str,
        subject: str,
        body: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email using user's Microsoft account.

        Args:
            db: Database session
            user_id: User identifier
            to: Recipient email address
            subject: Email subject
            body: Email body
            session_id: Optional session ID for additional validation

        Returns:
            Dictionary with send result
        """
        try:
            # Get user-specific Microsoft Graph client
            client = await self.client_factory.get_user_client(db, user_id, session_id)

            # Create email message
            from msgraph.generated.models.message import Message
            from msgraph.generated.models.item_body import ItemBody
            from msgraph.generated.models.body_type import BodyType
            from msgraph.generated.models.recipient import Recipient
            from msgraph.generated.models.email_address import EmailAddress

            message = Message(
                subject=subject,
                body=ItemBody(
                    content_type=BodyType.Text,
                    content=body
                ),
                to_recipients=[
                    Recipient(
                        email_address=EmailAddress(address=to)
                    )
                ]
            )

            # Send email
            response = await client.me.send_mail.post(message)

            return {
                'success': True,
                'message_id': response.id if hasattr(response, 'id') else 'unknown',
                'message': 'Email sent successfully'
            }

        except Exception as e:
            self.logger.error(f"Error sending email for user {user_id}: {e}")
            raise MicrosoftEmailError(f"Failed to send email: {e}")

    def invalidate_user_cache(self, user_id: int):
        """Invalidate cached client for user"""
        self.client_factory.invalidate_user_client(user_id)
```

### **3. User-Specific Email Tool**

#### **File**: `src/personal_assistant/tools/emails/email_tool_user_specific.py`

```python
"""
User-Specific Email Tool - A tool for managing user-specific email operations.

This tool provides email management with:
- User-specific Microsoft Graph API access
- OAuth integration for secure authentication
- Complete user isolation and security
- Send, read, and manage emails through the personal assistant
"""

import logging
from typing import Optional, Union, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.tools.base import Tool
from personal_assistant.auth.session_service import SessionService

# Import email-specific error handling and user-specific internal functions
from .email_error_handler import EmailErrorHandler
from .email_internal_user_specific import (
    UserSpecificEmailInternal,
    MicrosoftNotConnectedError,
    MicrosoftEmailError
)

logger = logging.getLogger(__name__)


class UserSpecificEmailTool:
    """User-specific email tool for managing emails with OAuth integration"""

    def __init__(self):
        # Initialize user-specific email internal operations
        self.email_internal = UserSpecificEmailInternal()

        # Create individual tools following TOOL_TEMPLATE.md pattern
        self.send_email_tool = Tool(
            name="send_email",
            func=self.send_email,
            description="Send an email using the user's Microsoft account",
            parameters={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address (required)",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject (required)",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content (required)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["to", "subject", "body", "session_id"],
            },
        )

        self.read_emails_tool = Tool(
            name="read_emails",
            func=self.read_emails,
            description="Read emails from the user's Microsoft account",
            parameters={
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "Email folder to read from (optional, defaults to inbox)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of emails to retrieve (optional, defaults to 10)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["session_id"],
            },
        )

        self.search_emails_tool = Tool(
            name="search_emails",
            func=self.search_emails,
            description="Search for emails in the user's Microsoft account",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (optional, searches all emails if empty)",
                    },
                    "folder": {
                        "type": "string",
                        "description": "Email folder to search in (optional)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["session_id"],
            },
        )

        self.get_folders_tool = Tool(
            name="get_folders",
            func=self.get_folders,
            description="Get email folders from the user's Microsoft account",
            parameters={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["session_id"],
            },
        )

    async def _get_user_id_from_session(
        self,
        session_id: str,
        db: AsyncSession
    ) -> Optional[int]:
        """Get user ID from session"""
        try:
            session_service = SessionService()
            return await session_service.get_current_user_id(session_id)
        except Exception as e:
            logger.error(f"Error getting user ID from session: {e}")
            return None

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Send an email using the user's Microsoft account.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            session_id: User session ID for authentication
            db: Database session

        Returns:
            Dictionary with send result or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}

            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}

            # Send the email
            result = await self.email_internal.send_user_email(
                db, user_id, to, subject, body, session_id
            )

            return {
                "success": True,
                "message_id": result.get("message_id"),
                "message": "Email sent successfully"
            }

        except MicrosoftNotConnectedError:
            return {"error": "User must connect Microsoft account first"}
        except MicrosoftEmailError as e:
            return {"error": f"Email error: {e}"}
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"error": f"Failed to send email: {e}"}

    async def read_emails(
        self,
        folder: str = "inbox",
        limit: int = 10,
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Read emails from the user's Microsoft account.

        Args:
            folder: Email folder to read from
            limit: Maximum number of emails to retrieve
            session_id: User session ID for authentication
            db: Database session

        Returns:
            Dictionary with emails or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}

            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}

            # Read emails
            emails = await self.email_internal.read_user_emails(
                db, user_id, folder, limit, session_id
            )

            return {
                "success": True,
                "emails": emails,
                "count": len(emails),
                "folder": folder
            }

        except MicrosoftNotConnectedError:
            return {"error": "User must connect Microsoft account first"}
        except MicrosoftEmailError as e:
            return {"error": f"Email error: {e}"}
        except Exception as e:
            logger.error(f"Error reading emails: {e}")
            return {"error": f"Failed to read emails: {e}"}

    async def search_emails(
        self,
        query: str = "",
        folder: Optional[str] = None,
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Search for emails in the user's Microsoft account.

        Args:
            query: Search query
            folder: Email folder to search in
            session_id: User session ID for authentication
            db: Database session

        Returns:
            Dictionary with search results or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}

            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}

            # Search emails
            emails = await self.email_internal.search_user_emails(
                db, user_id, query, folder, session_id
            )

            return {
                "success": True,
                "emails": emails,
                "count": len(emails),
                "query": query,
                "folder": folder
            }

        except MicrosoftNotConnectedError:
            return {"error": "User must connect Microsoft account first"}
        except MicrosoftEmailError as e:
            return {"error": f"Email error: {e}"}
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return {"error": f"Failed to search emails: {e}"}

    async def get_folders(
        self,
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get email folders from the user's Microsoft account.

        Args:
            session_id: User session ID for authentication
            db: Database session

        Returns:
            Dictionary with folders or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}

            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}

            # Get folders
            folders = await self.email_internal.get_user_folders(
                db, user_id, session_id
            )

            return {
                "success": True,
                "folders": folders,
                "count": len(folders)
            }

        except MicrosoftNotConnectedError:
            return {"error": "User must connect Microsoft account first"}
        except MicrosoftEmailError as e:
            return {"error": f"Email error: {e}"}
        except Exception as e:
            logger.error(f"Error getting folders: {e}")
            return {"error": f"Failed to get folders: {e}"}
```

## 🧪 **Testing Implementation**

### **Unit Tests Example**

#### **File**: `tests/unit/test_email_client_factory.py`

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.personal_assistant.tools.emails.email_client_factory import EmailClientFactory

class TestEmailClientFactory:
    @pytest.fixture
    def factory(self):
        return EmailClientFactory()

    @pytest.mark.asyncio
    async def test_get_user_client_success(self, factory):
        """Test successful client creation"""
        # Mock OAuth services
        with patch.object(factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
            mock_integration = Mock()
            mock_integration.id = "integration123"
            mock_get_integration.return_value = mock_integration

            with patch.object(factory.token_service, 'get_valid_token') as mock_get_token:
                mock_get_token.return_value = "access_token_123"

                with patch.object(factory, '_validate_email_access') as mock_validate:
                    mock_validate.return_value = True

                    # Test client creation
                    client = await factory.get_user_client(Mock(), 123, "session123")

                    # Verify success
                    assert client is not None
                    mock_get_integration.assert_called_once_with(Mock(), 123, "microsoft")
                    mock_get_token.assert_called_once_with(Mock(), "integration123")

    @pytest.mark.asyncio
    async def test_get_user_client_not_connected(self, factory):
        """Test client creation when user not connected"""
        with patch.object(factory.integration_service, 'get_integration_by_user_and_provider') as mock_get_integration:
            mock_get_integration.return_value = None

            # Test should raise MicrosoftNotConnectedError
            with pytest.raises(MicrosoftNotConnectedError):
                await factory.get_user_client(Mock(), 123, "session123")
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
def validate_user_isolation(user_id: int, email_id: str, client: GraphServiceClient) -> bool:
    """Ensure email belongs to user's account"""
    try:
        # Get email details
        email = await client.me.messages.by_message_id(email_id).get()

        # Check if email is accessible (belongs to user's account)
        # This is implicit - if we can retrieve it, it's in user's account
        return True

    except Exception:
        return False
```

This technical implementation provides a comprehensive foundation for implementing user-specific email functionality with proper security, performance, and error handling considerations.



