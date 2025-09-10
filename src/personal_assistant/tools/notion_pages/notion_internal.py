"""
Internal functions for Notion Pages Tool.

This module contains internal utility functions and helper methods
that are used by the main NotionPagesTool class.
"""

import logging
from typing import Dict, List, Optional, Tuple

from notion_client import Client

from personal_assistant.config.settings import settings

logger = logging.getLogger(__name__)

# Global Notion client instance
_notion_client = None


def get_notion_client() -> Client:
    """Get or create Notion client instance"""
    global _notion_client
    if _notion_client is None:
        if not settings.NOTION_API_KEY:
            raise ValueError("NOTION_API_KEY not configured")
        _notion_client = Client(auth=settings.NOTION_API_KEY)
    return _notion_client


async def _find_or_create_valid_parent(client: Client) -> str:
    """Find or create a valid parent page for the main page"""
    logger.info("Searching for valid parent page...")
    
    try:
        # First, try to find any non-archived page in the workspace
        response = client.search(
            query="", filter={"property": "object", "value": "page"}
        )
        
        for page in response.get("results", []):
            if not page.get("archived", False):
                page_id = page["id"]
                page_title = (
                    page.get("properties", {})
                    .get("title", {})
                    .get("title", [{}])[0]
                    .get("plain_text", "Untitled")
                )
                logger.info(f"Found valid parent page: '{page_title}' (ID: {page_id})")
                return page_id
        
        # If no valid page found, try to create a new root page
        logger.warning("No valid parent pages found, attempting to create a new root page...")
        
        # Try to create a page at the workspace root
        try:
            new_root = client.pages.create(
                parent={"type": "workspace"},
                properties={
                    "title": [{"type": "text", "text": {"content": "Personal Assistant Notes"}}]
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
                                        "content": "This page serves as the root for all Personal Assistant notes and pages."
                                    },
                                }
                            ]
                        },
                    }
                ],
            )
            new_root_id = new_root["id"]
            logger.info(f"Created new root page: {new_root_id}")
            return new_root_id
            
        except Exception as create_error:
            logger.error(f"Failed to create new root page: {create_error}")
            raise ValueError(f"Cannot find or create a valid parent page. Original root page is archived and no alternative found: {create_error}")
            
    except Exception as e:
        logger.error(f"Error finding valid parent: {e}")
        raise ValueError(f"Cannot find a valid parent page: {e}")


def _extract_page_title(page: dict) -> str:
    """Extract title from Notion page properties"""
    title_property = page.get("properties", {}).get("title", {})
    if title_property.get("type") == "title":
        title_rich_text = title_property.get("title", [])
        if title_rich_text:
            return title_rich_text[0].get("plain_text", "")
    return ""


async def _get_valid_parent_id(client: Client) -> str:
    """Get a valid parent page ID for creating the main page"""
    try:
        root_page = client.pages.retrieve(settings.NOTION_ROOT_PAGE_ID)
        if not root_page.get("archived", False):
            logger.info(f"Using root page as parent: {settings.NOTION_ROOT_PAGE_ID}")
            return settings.NOTION_ROOT_PAGE_ID
    except Exception as root_error:
        logger.warning(f"Failed to retrieve root page {settings.NOTION_ROOT_PAGE_ID}: {root_error}")
    
    logger.warning("Root page unavailable, finding alternative parent...")
    return await _find_or_create_valid_parent(client)


async def _find_existing_main_page(client: Client) -> Optional[str]:
    """Search for existing 'Table of Contents' page"""
    response = client.search(
        query="Table of Contents", 
        filter={"property": "object", "value": "page"}
    )
    logger.debug(f"Found {len(response.get('results', []))} pages matching 'Table of Contents'")
    
    for page in response.get("results", []):
        page_title = _extract_page_title(page)
        is_archived = page.get("archived", False)
        logger.debug(f"Found page: '{page_title}' (ID: {page['id']}, Archived: {is_archived})")
        
        if page_title == "Table of Contents" and not is_archived:
            logger.info(f"Found existing main page: {page['id']}")
            return page["id"]
        elif page_title == "Table of Contents" and is_archived:
            logger.warning(f"Found archived main page {page['id']}, will create a new one")
    
    return None


async def _create_new_main_page(client: Client, parent_id: str) -> str:
    """Create a new 'Table of Contents' main page"""
    logger.info(f"Creating new main page under parent: {parent_id}")
    
    main_page = client.pages.create(
        parent={"type": "page_id", "page_id": parent_id},
        properties={"title": [{"type": "text", "text": {"content": "Table of Contents"}}]},
        children=[{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Welcome to your notes! This page serves as the table of contents for all your note pages."}
                }]
            }
        }]
    )
    
    logger.info(f"Created new main page: {main_page['id']}")
    return main_page["id"]


async def ensure_main_page_exists(client: Client, main_page_id: Optional[str] = None) -> str:
    """Ensure the main table of contents page exists, create if it doesn't.
    
    If an existing main page is found but it's archived, a new one will be created
    instead of trying to use the archived page.
    """
    if main_page_id:
        return main_page_id
    
    try:
        # Try to find existing main page
        existing_page_id = await _find_existing_main_page(client)
        if existing_page_id:
            return existing_page_id
        
        # Create new main page
        parent_id = await _get_valid_parent_id(client)
        return await _create_new_main_page(client, parent_id)
        
    except Exception as e:
        logger.error(f"Error ensuring main page exists: {e}")
        raise


async def _fetch_note_pages(client: Client, main_page_id: str) -> List[Tuple[str, str]]:
    """Fetch all note pages and extract their titles and categories"""
    note_pages = []
    blocks = client.blocks.children.list(main_page_id)
    logger.debug(f"Found {len(blocks.get('results', []))} blocks in main page")
    
    for block in blocks.get("results", []):
        if block["type"] == "child_page":
            page_id = block["id"]
            page = await client.pages.retrieve(page_id)
            
            # Use centralized title extraction
            title = _extract_page_title(page)
            
            # Extract category
            category = (
                page.get("properties", {})
                .get("Category", {})
                .get("select", {})
                .get("name", "")
            )
            
            note_pages.append((title, category))
    
    return note_pages


async def _clear_toc_content(client: Client, main_page_id: str) -> None:
    """Clear existing TOC content while preserving welcome message"""
    blocks = client.blocks.children.list(main_page_id)
    welcome_block = None
    
    # Find welcome block to preserve
    for block in blocks.get("results", []):
        if block["type"] == "paragraph":
            text = block["paragraph"]["rich_text"]
            content = "".join([t["plain_text"] for t in text])
            if "Welcome to your notes" in content:
                welcome_block = block
                break
    
    # Delete all blocks except welcome (skip archived blocks)
    logger.debug(f"Attempting to delete {len(blocks.get('results', []))} blocks (excluding welcome block)")
    for block in blocks.get("results", []):
        if block != welcome_block:
            block_id = block["id"]
            is_archived = block.get("archived", False)
            logger.debug(f"Processing block {block_id} (archived: {is_archived})")
            
            try:
                if not is_archived:
                    logger.debug(f"Deleting block {block_id}")
                    client.blocks.delete(block_id)
                    logger.debug(f"Successfully deleted block {block_id}")
                else:
                    logger.debug(f"Skipping archived block {block_id}")
            except Exception as e:
                logger.warning(f"Could not delete block {block_id}: {e}")


def _group_pages_by_category(note_pages: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Group note pages by category"""
    categories: Dict[str, List[str]] = {}
    for title, category in note_pages:
        if category not in categories:
            categories[category] = []
        categories[category].append(title)
    return categories


def _build_toc_blocks(categories: Dict[str, List[str]]) -> List[dict]:
    """Build table of contents blocks from categorized pages"""
    toc_blocks = []
    
    if categories:
        for category, titles in categories.items():
            # Category heading
            toc_blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": category}}]
                },
            })
            
            # Page titles
            for title in sorted(titles):
                toc_blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": title}}]
                    },
                })
    else:
        # No pages message
        toc_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "No note pages yet. Create your first note!"}
                }]
            },
        })
    
    return toc_blocks


async def update_table_of_contents(client: Client, main_page_id: str) -> None:
    """Update the table of contents on the main page"""
    try:
        logger.info(f"Updating table of contents for main page: {main_page_id}")
        
        # Fetch note pages
        note_pages = await _fetch_note_pages(client, main_page_id)
        
        # Clear existing TOC content
        await _clear_toc_content(client, main_page_id)
        
        # Group pages by category and build TOC blocks
        categories = _group_pages_by_category(note_pages)
        toc_blocks = _build_toc_blocks(categories)
        
        # Add TOC blocks to main page
        if toc_blocks:
            client.blocks.children.append(main_page_id, children=toc_blocks)
        
        logger.info("Updated table of contents")
        
    except Exception as e:
        logger.error(f"Error updating table of contents: {e}")
        # Don't raise here as it's not critical for main functionality


def extract_page_properties(page: dict) -> Tuple[str, str, List[str]]:
    """Extract common page properties (title, category, tags)"""
    # Use the centralized title extraction function
    title = _extract_page_title(page)
    
    category = (
        page.get("properties", {}).get("Category", {}).get("select", {}).get("name", "")
    )
    # Extract tag names from multi_select structure
    tags_raw = page.get("properties", {}).get("Tags", {}).get("multi_select", [])
    tags = [tag.get("name", "") for tag in tags_raw if isinstance(tag, dict)]

    return title, category, tags


def create_properties_dict(
    title: Optional[str] = None,
    tags: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """Create a properties dictionary for Notion pages"""
    properties = {}

    if title:
        properties["title"] = [{"type": "text", "text": {"content": title}}]

    # Note: Tags and Category properties are not included in initial creation
    # because the parent page may not have these properties configured.
    # They should be added after page creation using update_page_properties.

    return properties
