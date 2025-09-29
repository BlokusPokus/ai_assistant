"""
Notion Client Factory for User-Specific Clients

This factory creates and manages user-specific Notion clients using the existing
OAuth infrastructure for secure, user-isolated Notion operations.
"""

from typing import Optional, Dict
from notion_client import Client
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.services.integration_service import OAuthIntegrationService
from personal_assistant.auth.session_service import SessionService
from personal_assistant.config.logging_config import get_logger

logger = get_logger(__name__)


class NotionClientFactory:
    """Factory for creating user-specific Notion clients using OAuth services"""

    def __init__(self):
        self.token_service = OAuthTokenService()
        self.integration_service = OAuthIntegrationService()
        self._client_cache: Dict[str, Client] = {}
        self.logger = logger

    async def get_user_client(
        self, 
        db: AsyncSession, 
        user_id: int, 
        session_id: Optional[str] = None
    ) -> Client:
        """
        Get or create Notion client for a specific user.

        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session ID for additional validation

        Returns:
            User-specific Notion client

        Raises:
            NotionNotConnectedError: If user hasn't connected Notion account
            NotionTokenExpiredError: If token is expired and can't be refreshed
            NotionWorkspaceError: If user doesn't have workspace access
        """
        try:
            # Check cache first
            cache_key = f"user_{user_id}"
            if cache_key in self._client_cache:
                self.logger.debug(f"Using cached Notion client for user {user_id}")
                return self._client_cache[cache_key]

            # Get user's Notion integration
            integration = await self.integration_service.get_integration_by_user_and_provider(
                db, user_id, "notion"
            )

            if not integration:
                raise NotionNotConnectedError(f"User {user_id} must connect Notion account")

            # Get valid access token
            access_token = await self.token_service.get_valid_token(
                db, integration.id, "access_token"
            )

            # If no valid access token, try to refresh it
            if not access_token:
                self.logger.info(f"Access token expired or not found for user {user_id}, attempting to refresh...")
                
                # Import OAuth manager to get Notion provider
                from personal_assistant.oauth.oauth_manager import OAuthManager
                oauth_manager = OAuthManager()
                provider = oauth_manager.get_provider("notion")
                
                # Attempt to refresh the access token
                new_access_token = await self.token_service.refresh_access_token(
                    db, integration.id, provider
                )
                
                if new_access_token:
                    self.logger.info(f"Successfully refreshed access token for user {user_id}")
                    # Create Notion client with new token
                    client = Client(auth=new_access_token)
                else:
                    raise NotionTokenExpiredError(f"Could not refresh access token for user {user_id}. Please reconnect your Notion account.")
            else:
                # Create Notion client with existing token
                client = Client(auth=access_token.access_token)

            # Validate workspace access with better error handling
            try:
                if not await self._validate_workspace_access(client):
                    raise NotionWorkspaceError(f"User {user_id} doesn't have workspace access")
            except Exception as validation_error:
                # Check if it's a token expiration issue
                if "API token is invalid" in str(validation_error) or "unauthorized" in str(validation_error).lower():
                    self.logger.warning(f"Notion token appears to be expired for user {user_id}, attempting refresh...")
                    
                    # Try to refresh the token
                    from personal_assistant.oauth.oauth_manager import OAuthManager
                    oauth_manager = OAuthManager()
                    provider = oauth_manager.get_provider("notion")
                    
                    new_access_token = await self.token_service.refresh_access_token(
                        db, integration.id, provider
                    )
                    
                    if new_access_token:
                        self.logger.info(f"Successfully refreshed access token for user {user_id} after validation failure")
                        # Create new client with refreshed token
                        client = Client(auth=new_access_token)
                        # Invalidate cached client
                        self.invalidate_user_client(user_id)
                        
                        # Try validation again with new token
                        if not await self._validate_workspace_access(client):
                            raise NotionWorkspaceError(f"User {user_id} doesn't have workspace access")
                    else:
                        self.logger.warning(f"Could not refresh Notion token for user {user_id}, marking integration as expired")
                        # Mark the integration as expired so user knows to reconnect
                        await self.integration_service.update_integration(
                            db, integration.id, 
                            status="expired",
                            error_message="Access token expired and refresh failed. Please reconnect your Notion account.",
                            error_count=integration.error_count + 1 if integration.error_count else 1
                        )
                        raise NotionTokenExpiredError(f"Notion access token expired for user {user_id}. Please reconnect your Notion account.")
                else:
                    raise NotionWorkspaceError(f"User {user_id} doesn't have workspace access: {validation_error}")

            # Cache client
            self._client_cache[cache_key] = client
            self.logger.info(f"Created and cached Notion client for user {user_id}")

            return client

        except Exception as e:
            self.logger.error(f"Error getting Notion client for user {user_id}: {e}")
            if isinstance(e, (NotionNotConnectedError, NotionTokenExpiredError, NotionWorkspaceError)):
                raise
            raise NotionWorkspaceError(f"Failed to create Notion client: {e}")

    async def _validate_workspace_access(self, client: Client) -> bool:
        """
        Validate that the client has access to the Notion workspace.

        Args:
            client: Notion client to validate

        Returns:
            True if workspace is accessible
        """
        try:
            # Test workspace access by making a simple API call
            response = client.search(
                query="",
                filter={"property": "object", "value": "page"},
                page_size=1
            )

            # If we get a response, the workspace is accessible
            return "results" in response

        except Exception as e:
            self.logger.error(f"Error validating workspace access: {e}")
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
        self.logger.debug("Cleared all cached Notion clients")

    async def get_user_id_from_session(
        self, 
        session_service: SessionService, 
        session_id: str
    ) -> Optional[int]:
        """
        Get user ID from session using SessionService.

        Args:
            session_service: SessionService instance
            session_id: Session identifier

        Returns:
            User ID if session is valid, None otherwise
        """
        try:
            return await session_service.get_current_user_id(session_id)
        except Exception as e:
            self.logger.error(f"Error getting user ID from session: {e}")
            return None


# Custom exceptions
class NotionNotConnectedError(Exception):
    """Raised when user hasn't connected Notion account"""
    pass


class NotionTokenExpiredError(Exception):
    """Raised when Notion token is expired and can't be refreshed"""
    pass


class NotionWorkspaceError(Exception):
    """Raised when user doesn't have workspace access"""
    pass
