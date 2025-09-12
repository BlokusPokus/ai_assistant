"""
User-Specific Internal functions for Notion Pages Tool.

This module contains internal utility functions and helper methods
that are used by the main NotionPagesTool class with user-specific
Notion clients and workspaces.
"""

import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from notion_client import Client

from .workspace_manager import NotionWorkspaceManager
from .client_factory import NotionClientFactory, NotionNotConnectedError, NotionWorkspaceError

logger = logging.getLogger(__name__)


class UserSpecificNotionInternal:
    """User-specific Notion internal operations"""
    
    def __init__(self):
        self.workspace_manager = NotionWorkspaceManager()
        self.client_factory = NotionClientFactory()
    
    async def ensure_user_main_page_exists(
        self, 
        db: AsyncSession, 
        user_id: int, 
        session_id: Optional[str] = None
    ) -> str:
        """
        Ensure the user's Personal Assistant page exists, create if it doesn't.
        
        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session ID for additional validation
            
        Returns:
            Page ID of the user's Personal Assistant page
            
        Raises:
            NotionNotConnectedError: If user hasn't connected Notion account
            NotionWorkspaceError: If workspace is not accessible
        """
        try:
            # Use workspace manager to ensure user has Personal Assistant page
            return await self.workspace_manager.ensure_user_root_page(
                db, user_id, session_id
            )
            
        except Exception as e:
            logger.error(f"Error ensuring user main page exists for user {user_id}: {e}")
            if isinstance(e, (NotionNotConnectedError, NotionWorkspaceError)):
                raise
            raise NotionWorkspaceError(f"Failed to ensure user main page: {e}")
    
    async def get_user_client(
        self, 
        db: AsyncSession, 
        user_id: int, 
        session_id: Optional[str] = None
    ) -> Client:
        """
        Get user-specific Notion client.
        
        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session ID for additional validation
            
        Returns:
            User-specific Notion client
            
        Raises:
            NotionNotConnectedError: If user hasn't connected Notion account
            NotionWorkspaceError: If workspace is not accessible
        """
        return await self.client_factory.get_user_client(db, user_id, session_id)
    
    async def find_user_page_by_title(
        self, 
        db: AsyncSession, 
        user_id: int, 
        title: str, 
        session_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Find a page by title in the user's workspace.
        
        Args:
            db: Database session
            user_id: User identifier
            title: Page title to search for
            session_id: Optional session ID for additional validation
            
        Returns:
            Page ID if found, None otherwise
        """
        try:
            client = await self.get_user_client(db, user_id, session_id)
            
            # Search for pages with the specified title
            response = client.search(
                query=title,
                filter={"property": "object", "value": "page"}
            )
            
            for page in response.get("results", []):
                # Check if page is not archived
                if page.get("archived", False):
                    continue
                
                # Check if title matches exactly
                title_property = page.get("properties", {}).get("title", {})
                title_text = title_property.get("title", [{}])[0].get("plain_text", "")
                
                if title_text == title:
                    logger.debug(f"Found page '{title}' with ID {page['id']} for user {user_id}")
                    return page["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding page '{title}' for user {user_id}: {e}")
            return None
    
    async def create_user_page(
        self, 
        db: AsyncSession, 
        user_id: int, 
        title: str, 
        content: Optional[str] = None,
        parent_page_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create a new page in the user's workspace.
        
        Args:
            db: Database session
            user_id: User identifier
            title: Page title
            content: Optional page content
            parent_page_id: Optional parent page ID (defaults to user's Personal Assistant page)
            session_id: Optional session ID for additional validation
            
        Returns:
            Page ID of the created page
        """
        try:
            client = await self.get_user_client(db, user_id, session_id)
            
            # Use Personal Assistant page as parent if not specified
            if not parent_page_id:
                parent_page_id = await self.ensure_user_main_page_exists(db, user_id, session_id)
            
            # Prepare page content
            children = []
            if content:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": content}
                        }]
                    }
                })
            
            # Create the page
            page = client.pages.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                properties={
                    "title": [{"type": "text", "text": {"content": title}}]
                },
                children=children
            )
            
            page_id = page["id"]
            logger.info(f"Created page '{title}' with ID {page_id} for user {user_id}")
            return page_id
            
        except Exception as e:
            logger.error(f"Error creating page '{title}' for user {user_id}: {e}")
            raise NotionWorkspaceError(f"Failed to create page: {e}")
    
    async def update_user_page(
        self, 
        db: AsyncSession, 
        user_id: int, 
        page_id: str, 
        title: Optional[str] = None,
        content: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Update a page in the user's workspace.
        
        Args:
            db: Database session
            user_id: User identifier
            page_id: Page ID to update
            title: Optional new title
            content: Optional new content
            session_id: Optional session ID for additional validation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self.get_user_client(db, user_id, session_id)
            
            # Update page properties if title is provided
            if title:
                client.pages.update(
                    page_id=page_id,
                    properties={
                        "title": [{"type": "text", "text": {"content": title}}]
                    }
                )
            
            # Update page content if provided
            if content:
                # Get existing blocks
                blocks_response = client.blocks.children.list(block_id=page_id)
                existing_blocks = blocks_response.get("results", [])
                
                # Remove existing content blocks (keep structural blocks)
                for block in existing_blocks:
                    if block.get("type") == "paragraph":
                        client.blocks.delete(block_id=block["id"])
                
                # Add new content
                client.blocks.children.append(
                    block_id=page_id,
                    children=[{
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": content}
                            }]
                        }
                    }]
                )
            
            logger.info(f"Updated page {page_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating page {page_id} for user {user_id}: {e}")
            return False
    
    async def delete_user_page(
        self, 
        db: AsyncSession, 
        user_id: int, 
        page_id: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Delete (archive) a page in the user's workspace.
        
        Args:
            db: Database session
            user_id: User identifier
            page_id: Page ID to delete
            session_id: Optional session ID for additional validation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self.get_user_client(db, user_id, session_id)
            
            # Archive the page
            client.pages.update(
                page_id=page_id,
                archived=True
            )
            
            logger.info(f"Archived page {page_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting page {page_id} for user {user_id}: {e}")
            return False
    
    async def search_user_pages(
        self, 
        db: AsyncSession, 
        user_id: int, 
        query: str = "",
        session_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for pages in the user's workspace.
        
        Args:
            db: Database session
            user_id: User identifier
            query: Search query
            session_id: Optional session ID for additional validation
            
        Returns:
            List of page dictionaries
        """
        try:
            client = await self.get_user_client(db, user_id, session_id)
            
            response = client.search(
                query=query,
                filter={"property": "object", "value": "page"}
            )
            
            pages = []
            for page in response.get("results", []):
                if not page.get("archived", False):
                    title_property = page.get("properties", {}).get("title", {})
                    title = title_property.get("title", [{}])[0].get("plain_text", "Untitled")
                    
                    pages.append({
                        "id": page["id"],
                        "title": title,
                        "url": page.get("url", ""),
                        "created_time": page.get("created_time", ""),
                        "last_edited_time": page.get("last_edited_time", "")
                    })
            
            logger.debug(f"Found {len(pages)} pages for user {user_id} with query '{query}'")
            return pages
            
        except Exception as e:
            logger.error(f"Error searching pages for user {user_id}: {e}")
            return []


# Global instance for backward compatibility
_user_specific_notion = UserSpecificNotionInternal()


# Convenience functions that maintain backward compatibility
async def ensure_user_main_page_exists(
    db: AsyncSession, 
    user_id: int, 
    session_id: Optional[str] = None
) -> str:
    """Ensure the user's Personal Assistant page exists"""
    return await _user_specific_notion.ensure_user_main_page_exists(db, user_id, session_id)


async def get_user_notion_client(
    db: AsyncSession, 
    user_id: int, 
    session_id: Optional[str] = None
) -> Client:
    """Get user-specific Notion client"""
    return await _user_specific_notion.get_user_client(db, user_id, session_id)
