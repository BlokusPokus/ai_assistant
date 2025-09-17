"""
Notion Workspace Manager for User-Specific Workspaces

This manager handles user-specific Notion workspace operations, including
creating and managing "Personal Assistant" pages for each user.
"""

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
            # Get user's workspace root (smart detection)
            workspace_root_id = await self._get_workspace_root(client)

            # Determine parent based on workspace root detection
            if workspace_root_id is None:
                # Create at workspace root level (not under any existing page)
                parent = {"type": "workspace", "workspace": True}
                self.logger.info("Creating Personal Assistant page at workspace root level")
            else:
                # Create under the detected suitable page
                parent = {"type": "page_id", "page_id": workspace_root_id}
                self.logger.info(f"Creating Personal Assistant page under existing page: {workspace_root_id}")

            # Create Personal Assistant page
            personal_assistant_page = client.pages.create(
                parent=parent,
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

    async def _get_workspace_root(self, client: Client) -> Optional[str]:
        """
        Get the root page of the user's workspace.
        
        This method now uses a smarter approach:
        1. First, try to find an existing "Personal Assistant" page at workspace root level
        2. If found, return it (so we reuse the existing page)
        3. If not found, return None (so we create a new one at workspace root level)
        
        The Personal Assistant page should ALWAYS be at workspace root level,
        not nested under other pages.

        Args:
            client: User-specific Notion client

        Returns:
            Page ID of existing Personal Assistant page, or None if we should create new one

        Raises:
            NotionWorkspaceError: If workspace is not accessible
        """
        try:
            # Look for existing Personal Assistant page at workspace root level
            existing_pa_page = await self._find_existing_personal_assistant_page_at_root(client)
            if existing_pa_page:
                self.logger.info("Found existing Personal Assistant page at workspace root, reusing it")
                return existing_pa_page
            
            # No existing PA page found, we'll create a new one at workspace root
            self.logger.info("No existing Personal Assistant page found, will create new one at workspace root")
            return None

        except Exception as e:
            self.logger.error(f"Error getting workspace root: {e}")
            raise NotionWorkspaceError(f"Failed to access workspace: {e}")
    
    async def _find_existing_personal_assistant_page_at_root(self, client: Client) -> Optional[str]:
        """Find an existing Personal Assistant page at workspace root level."""
        try:
            response = client.search(
                query="Personal Assistant",
                filter={"property": "object", "value": "page"},
                page_size=10
            )
            
            for page in response.get("results", []):
                # Check if page is at workspace root level
                parent = page.get("parent", {})
                if parent.get("type") != "workspace":
                    continue
                
                # Check if it's a Personal Assistant page
                title = page.get("properties", {}).get("title", {}).get("title", [])
                if title:
                    page_title = title[0].get("text", {}).get("content", "").lower()
                    if "personal assistant" in page_title:
                        return page["id"]
            return None
        except Exception as e:
            self.logger.warning(f"Error searching for existing Personal Assistant page at root: {e}")
            return None
    
    async def _find_existing_personal_assistant_page(self, client: Client) -> Optional[str]:
        """Find an existing Personal Assistant page anywhere in the workspace."""
        try:
            response = client.search(
                query="Personal Assistant",
                filter={"property": "object", "value": "page"},
                page_size=10
            )
            
            for page in response.get("results", []):
                title = page.get("properties", {}).get("title", {}).get("title", [])
                if title:
                    page_title = title[0].get("text", {}).get("content", "").lower()
                    if "personal assistant" in page_title:
                        return page["id"]
            return None
        except Exception as e:
            self.logger.warning(f"Error searching for existing Personal Assistant page: {e}")
            return None
    
    async def _find_suitable_workspace_root(self, client: Client) -> Optional[str]:
        """
        Find a suitable workspace root page.
        
        Looks for pages that are:
        1. At workspace root level (not nested under other pages)
        2. Have generic names like "Home", "Dashboard", "Main", etc.
        3. Are not project-specific or dated pages
        """
        try:
            response = client.search(
                query="",
                filter={"property": "object", "value": "page"},
                page_size=50
            )
            
            suitable_pages = []
            generic_names = ["home", "dashboard", "main", "workspace", "root", "index"]
            
            for page in response.get("results", []):
                # Check if page is at workspace root level
                parent = page.get("parent", {})
                if parent.get("type") != "workspace":
                    continue
                
                # Check if page has a generic name
                title = page.get("properties", {}).get("title", {}).get("title", [])
                if title:
                    page_title = title[0].get("text", {}).get("content", "").lower()
                    
                    # Skip project-specific or dated pages
                    if any(keyword in page_title for keyword in ["phase", "project", "meeting", "task", "2024", "2025"]):
                        continue
                    
                    # Prefer generic names
                    if any(generic_name in page_title for generic_name in generic_names):
                        suitable_pages.insert(0, page)  # Higher priority
                    else:
                        suitable_pages.append(page)
            
            # Return the first suitable page, or None if none found
            return suitable_pages[0]["id"] if suitable_pages else None
            
        except Exception as e:
            self.logger.warning(f"Error finding suitable workspace root: {e}")
            return None

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
