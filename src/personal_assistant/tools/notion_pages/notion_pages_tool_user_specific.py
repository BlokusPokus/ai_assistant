"""
User-Specific Notion Pages Tool - A tool for managing user-specific note pages.

This tool creates a page-based note structure in Notion with:
- User-specific Personal Assistant page as table of contents
- Individual note pages nested under user's Personal Assistant page
- Obsidian-style bidirectional linking between pages
- Auto-updating table of contents
- Rich text content support
- User isolation and security
"""

import logging
from typing import Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.tools.base import Tool
from personal_assistant.auth.session_service import SessionService

# Import notion-specific error handling and user-specific internal functions
from .notion_error_handler import NotionErrorHandler
from .notion_internal_user_specific import (
    UserSpecificNotionInternal,
    ensure_user_main_page_exists,
    get_user_notion_client,
    NotionNotConnectedError,
    NotionWorkspaceError
)

logger = logging.getLogger(__name__)


class UserSpecificNotionPagesTool:
    """User-specific Notion tool for managing note pages with bidirectional linking"""

    def __init__(self):
        # Initialize user-specific Notion internal operations
        self.notion_internal = UserSpecificNotionInternal()
        
        # Create individual tools following TOOL_TEMPLATE.md pattern
        self.create_note_page_tool = Tool(
            name="create_note_page",
            func=self.create_note_page,
            description="Create a new note page under the user's Personal Assistant page",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note page (required)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Initial content for the note page (optional)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["title", "session_id"],
            },
        )

        self.read_note_page_tool = Tool(
            name="read_note_page",
            func=self.read_note_page,
            description="Read content from a note page",
            parameters={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "ID of the page to read (required)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["page_id", "session_id"],
            },
        )

        self.update_note_page_tool = Tool(
            name="update_note_page",
            func=self.update_note_page,
            description="Update content of a note page",
            parameters={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "ID of the page to update (required)",
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the page (optional)",
                    },
                    "content": {
                        "type": "string",
                        "description": "New content for the page (optional)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["page_id", "session_id"],
            },
        )

        self.delete_note_page_tool = Tool(
            name="delete_note_page",
            func=self.delete_note_page,
            description="Delete (archive) a note page",
            parameters={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "ID of the page to delete (required)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["page_id", "session_id"],
            },
        )

        self.search_note_pages_tool = Tool(
            name="search_note_pages",
            func=self.search_note_pages,
            description="Search for note pages in the user's workspace",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (optional, searches all pages if empty)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "User session ID for authentication (required)",
                    },
                },
                "required": ["session_id"],
            },
        )

        self.get_table_of_contents_tool = Tool(
            name="get_table_of_contents",
            func=self.get_table_of_contents,
            description="Get the table of contents from the user's Personal Assistant page",
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

    async def create_note_page(
        self, 
        title: str, 
        content: Optional[str] = None, 
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Create a new note page under the user's Personal Assistant page.
        
        Args:
            title: Title of the note page
            content: Initial content for the note page
            session_id: User session ID for authentication
            db: Database session
            
        Returns:
            Dictionary with page information or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}
            
            # Ensure user has Personal Assistant page
            main_page_id = await ensure_user_main_page_exists(db, user_id, session_id)
            
            # Create the note page
            page_id = await self.notion_internal.create_user_page(
                db, user_id, title, content, main_page_id, session_id
            )
            
            # Update table of contents
            await self._update_table_of_contents(db, user_id, session_id)
            
            return {
                "success": True,
                "page_id": page_id,
                "title": title,
                "message": f"Note page '{title}' created successfully"
            }
            
        except NotionNotConnectedError:
            return {"error": "User must connect Notion account first"}
        except NotionWorkspaceError as e:
            return {"error": f"Notion workspace error: {e}"}
        except Exception as e:
            logger.error(f"Error creating note page: {e}")
            return {"error": f"Failed to create note page: {e}"}

    async def read_note_page(
        self, 
        page_id: str, 
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Read content from a note page.
        
        Args:
            page_id: ID of the page to read
            session_id: User session ID for authentication
            db: Database session
            
        Returns:
            Dictionary with page content or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}
            
            # Get user-specific client
            client = await get_user_notion_client(db, user_id, session_id)
            
            # Get page properties
            page = client.pages.retrieve(page_id=page_id)
            
            # Get page content
            blocks_response = client.blocks.children.list(block_id=page_id)
            content_blocks = blocks_response.get("results", [])
            
            # Extract content
            content = ""
            for block in content_blocks:
                if block.get("type") == "paragraph":
                    rich_text = block.get("paragraph", {}).get("rich_text", [])
                    for text_obj in rich_text:
                        content += text_obj.get("plain_text", "")
                    content += "\n"
            
            # Extract title
            title_property = page.get("properties", {}).get("title", {})
            title = title_property.get("title", [{}])[0].get("plain_text", "Untitled")
            
            return {
                "success": True,
                "page_id": page_id,
                "title": title,
                "content": content.strip(),
                "url": page.get("url", ""),
                "created_time": page.get("created_time", ""),
                "last_edited_time": page.get("last_edited_time", "")
            }
            
        except NotionNotConnectedError:
            return {"error": "User must connect Notion account first"}
        except NotionWorkspaceError as e:
            return {"error": f"Notion workspace error: {e}"}
        except Exception as e:
            logger.error(f"Error reading note page: {e}")
            return {"error": f"Failed to read note page: {e}"}

    async def update_note_page(
        self, 
        page_id: str, 
        title: Optional[str] = None, 
        content: Optional[str] = None,
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Update content of a note page.
        
        Args:
            page_id: ID of the page to update
            title: New title for the page
            content: New content for the page
            session_id: User session ID for authentication
            db: Database session
            
        Returns:
            Dictionary with success status or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}
            
            # Update the page
            success = await self.notion_internal.update_user_page(
                db, user_id, page_id, title, content, session_id
            )
            
            if success:
                # Update table of contents if title changed
                if title:
                    await self._update_table_of_contents(db, user_id, session_id)
                
                return {
                    "success": True,
                    "message": f"Note page {page_id} updated successfully"
                }
            else:
                return {"error": "Failed to update note page"}
            
        except NotionNotConnectedError:
            return {"error": "User must connect Notion account first"}
        except NotionWorkspaceError as e:
            return {"error": f"Notion workspace error: {e}"}
        except Exception as e:
            logger.error(f"Error updating note page: {e}")
            return {"error": f"Failed to update note page: {e}"}

    async def delete_note_page(
        self, 
        page_id: str, 
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Delete (archive) a note page.
        
        Args:
            page_id: ID of the page to delete
            session_id: User session ID for authentication
            db: Database session
            
        Returns:
            Dictionary with success status or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}
            
            # Delete the page
            success = await self.notion_internal.delete_user_page(
                db, user_id, page_id, session_id
            )
            
            if success:
                # Update table of contents
                await self._update_table_of_contents(db, user_id, session_id)
                
                return {
                    "success": True,
                    "message": f"Note page {page_id} deleted successfully"
                }
            else:
                return {"error": "Failed to delete note page"}
            
        except NotionNotConnectedError:
            return {"error": "User must connect Notion account first"}
        except NotionWorkspaceError as e:
            return {"error": f"Notion workspace error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting note page: {e}")
            return {"error": f"Failed to delete note page: {e}"}

    async def search_note_pages(
        self, 
        query: str = "", 
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Search for note pages in the user's workspace.
        
        Args:
            query: Search query
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
            
            # Search for pages
            pages = await self.notion_internal.search_user_pages(
                db, user_id, query, session_id
            )
            
            return {
                "success": True,
                "pages": pages,
                "count": len(pages),
                "query": query
            }
            
        except NotionNotConnectedError:
            return {"error": "User must connect Notion account first"}
        except NotionWorkspaceError as e:
            return {"error": f"Notion workspace error: {e}"}
        except Exception as e:
            logger.error(f"Error searching note pages: {e}")
            return {"error": f"Failed to search note pages: {e}"}

    async def get_table_of_contents(
        self, 
        session_id: str = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get the table of contents from the user's Personal Assistant page.
        
        Args:
            session_id: User session ID for authentication
            db: Database session
            
        Returns:
            Dictionary with table of contents or error details
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get user ID from session
            user_id = await self._get_user_id_from_session(session_id, db)
            if not user_id:
                return {"error": "Invalid session or user not found"}
            
            # Ensure user has Personal Assistant page
            main_page_id = await ensure_user_main_page_exists(db, user_id, session_id)
            
            # Get all pages under the Personal Assistant page
            pages = await self.notion_internal.search_user_pages(
                db, user_id, "", session_id
            )
            
            # Filter out the Personal Assistant page itself
            toc_pages = [page for page in pages if page["id"] != main_page_id]
            
            return {
                "success": True,
                "main_page_id": main_page_id,
                "pages": toc_pages,
                "count": len(toc_pages)
            }
            
        except NotionNotConnectedError:
            return {"error": "User must connect Notion account first"}
        except NotionWorkspaceError as e:
            return {"error": f"Notion workspace error: {e}"}
        except Exception as e:
            logger.error(f"Error getting table of contents: {e}")
            return {"error": f"Failed to get table of contents: {e}"}

    async def _update_table_of_contents(
        self, 
        db: AsyncSession, 
        user_id: int, 
        session_id: str
    ) -> None:
        """Update the table of contents in the user's Personal Assistant page"""
        try:
            # Get all pages under the Personal Assistant page
            pages = await self.notion_internal.search_user_pages(
                db, user_id, "", session_id
            )
            
            # Get Personal Assistant page ID
            main_page_id = await ensure_user_main_page_exists(db, user_id, session_id)
            
            # Filter out the Personal Assistant page itself
            toc_pages = [page for page in pages if page["id"] != main_page_id]
            
            # Get user-specific client
            client = await get_user_notion_client(db, user_id, session_id)
            
            # Get existing blocks
            blocks_response = client.blocks.children.list(block_id=main_page_id)
            existing_blocks = blocks_response.get("results", [])
            
            # Remove existing table of contents blocks
            for block in existing_blocks:
                if (block.get("type") == "paragraph" and 
                    "Table of Contents" in str(block.get("paragraph", {}).get("rich_text", []))):
                    client.blocks.delete(block_id=block["id"])
            
            # Add new table of contents
            toc_content = "## Table of Contents\n\n"
            for page in toc_pages:
                toc_content += f"- [{page['title']}]({page['url']})\n"
            
            client.blocks.children.append(
                block_id=main_page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": toc_content}
                        }]
                    }
                }]
            )
            
        except Exception as e:
            logger.error(f"Error updating table of contents: {e}")
            # Don't raise exception as this is not critical
