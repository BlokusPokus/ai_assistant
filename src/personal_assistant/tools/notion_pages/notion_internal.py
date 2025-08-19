"""
Internal functions for Notion Pages Tool.

This module contains internal utility functions and helper methods
that are used by the main NotionPagesTool class.
"""

import logging
from typing import List, Tuple

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


async def ensure_main_page_exists(client: Client, main_page_id: str = None) -> str:
    """Ensure the main table of contents page exists, create if it doesn't"""
    if main_page_id:
        return main_page_id

    try:
        # Search for existing main page
        response = client.search(
            query="Table of Contents",
            filter={"property": "object", "value": "page"}
        )

        for page in response.get("results", []):
            if page.get("properties", {}).get("title", {}).get("title", [{}])[0].get("plain_text", "") == "Table of Contents":
                found_main_page_id = page["id"]
                logger.info(f"Found existing main page: {found_main_page_id}")
                return found_main_page_id

        # Create main page if it doesn't exist
        main_page = client.pages.create(
            parent={"type": "page_id", "page_id": settings.NOTION_ROOT_PAGE_ID},
            properties={
                "title": [{"type": "text", "text": {"content": "Table of Contents"}}]
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "Welcome to your notes! This page serves as the table of contents for all your note pages."}}]
                    }
                }
            ]
        )

        created_main_page_id = main_page["id"]
        logger.info(f"Created new main page: {created_main_page_id}")
        return created_main_page_id

    except Exception as e:
        logger.error(f"Error ensuring main page exists: {e}")
        raise


async def update_table_of_contents(client: Client, main_page_id: str) -> None:
    """Update the table of contents on the main page"""
    try:
        # Get all note pages BEFORE clearing content
        note_pages = []
        blocks = client.blocks.children.list(main_page_id)
        for block in blocks.get("results", []):
            if block["type"] == "child_page":
                page_id = block["id"]
                page = client.pages.retrieve(page_id)
                title = page.get("properties", {}).get("title", {}).get(
                    "title", [{}])[0].get("plain_text", "")
                category = page.get("properties", {}).get(
                    "Category", {}).get("select", {}).get("name", "")

                note_pages.append((title, category))

        # Clear existing TOC content (keep the welcome message)
        blocks = client.blocks.children.list(main_page_id)
        welcome_block = None

        for block in blocks.get("results", []):
            if block["type"] == "paragraph":
                text = block["paragraph"]["rich_text"]
                content = "".join([t["plain_text"] for t in text])
                if "Welcome to your notes" in content:
                    welcome_block = block
                    break

        # Delete all blocks except welcome
        for block in blocks.get("results", []):
            if block != welcome_block:
                client.blocks.delete(block["id"])

        # Group by category
        categories = {}
        for title, category in note_pages:
            if category not in categories:
                categories[category] = []
            categories[category].append(title)

        # Add TOC content
        toc_blocks = []

        if categories:
            for category, titles in categories.items():
                # Category heading
                toc_blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": category}}]
                    }
                })

                # Page titles
                for title in sorted(titles):
                    toc_blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": title}}]
                        }
                    })
        else:
            toc_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "No note pages yet. Create your first note!"}}]
                }
            })

        # Add TOC blocks to main page
        if toc_blocks:
            client.blocks.children.append(main_page_id, children=toc_blocks)

        logger.info("Updated table of contents")

    except Exception as e:
        logger.error(f"Error updating table of contents: {e}")
        # Don't raise here as it's not critical for main functionality


def extract_page_properties(page: dict) -> Tuple[str, str, List[str]]:
    """Extract common page properties (title, category, tags)"""
    title = page.get("properties", {}).get("title", {}).get(
        "title", [{}])[0].get("plain_text", "")
    category = page.get("properties", {}).get(
        "Category", {}).get("select", {}).get("name", "")
    tags = page.get("properties", {}).get("Tags", {}).get("multi_select", [])

    return title, category, tags


def create_properties_dict(title: str = None, tags: str = None, category: str = None) -> dict:
    """Create a properties dictionary for Notion pages"""
    properties = {}

    if title:
        properties["title"] = [{"type": "text", "text": {"content": title}}]

    if tags:
        properties["Tags"] = {
            "type": "multi_select",
            "multi_select": [{"name": tag.strip()} for tag in tags.split(",")]
        }

    if category:
        properties["Category"] = {
            "type": "select",
            "select": {"name": category}
        }

    return properties
