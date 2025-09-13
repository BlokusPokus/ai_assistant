"""
Notion Workspace Manager for User-Specific Workspaces

This manager handles user-specific Notion workspace operations, including
creating and managing "Personal Assistant" pages for each user.
"""

import logging
from typing import Optional
from notion_client import Client
from sqlalchemy.ext.asyncio import AsyncSession

from .client_factory import NotionClientFactory, NotionNotConnectedError, NotionWorkspaceError
from personal_assistant.config.logging_config import get_logger

logger = get_logger(__name__)


class NotionWorkspaceManager:
    """Manages user-specific Notion workspaces and pages"""

    def __init__(self):
        self.client_factory = NotionClientFactory()
        self.logger = logger

    async def ensure_user_root_page(
        self, 
        db: AsyncSession, 
        user_id: int, 
        session_id: Optional[str] = None
    ) -> str:
        """
        Ensure user has Personal Assistant page in their workspace.

        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session ID for additional validation

        Returns:
            Page ID of the Personal Assistant page

        Raises:
            NotionNotConnectedError: If user hasn't connected Notion account
            NotionWorkspaceError: If workspace is not accessible
            NotionPageCreationError: If page creation fails
        """
        try:
            # Get user-specific Notion client
            client = await self.client_factory.get_user_client(db, user_id, session_id)

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
            if isinstance(e, (NotionNotConnectedError, NotionWorkspaceError)):
                raise
            raise NotionWorkspaceError(f"Failed to ensure user root page: {e}")

    async def create_user_root_page(self, client: Client, user_id: int) -> str:
        """
        Create Personal Assistant page in user's workspace.

        Args:
            client: User-specific Notion client
            user_id: User identifier

        Returns:
            Page ID of the created page

        Raises:
            NotionPageCreationError: If page creation fails
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
                                "text": {
                                    "content": "Welcome to your personal assistant notes! This page serves as the table of contents for all your note pages."
                                }
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

    async def find_user_root_page(self, client: Client, user_id: int) -> Optional[str]:
        """
        Find existing Personal Assistant page in user's workspace.

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
        Get the root page of the user's workspace.

        Args:
            client: User-specific Notion client

        Returns:
            Page ID of the workspace root

        Raises:
            NotionWorkspaceError: If workspace is not accessible
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

    async def validate_user_workspace(self, client: Client, user_id: int) -> bool:
        """
        Validate user has access to their Notion workspace.

        Args:
            client: User-specific Notion client
            user_id: User identifier

        Returns:
            True if user has valid workspace access
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
            self.logger.error(f"Error validating workspace for user {user_id}: {e}")
            return False

    def invalidate_user_cache(self, user_id: int):
        """Invalidate cached client for user"""
        self.client_factory.invalidate_user_client(user_id)


# Custom exceptions
class NotionPageCreationError(Exception):
    """Raised when page creation fails"""
    pass
