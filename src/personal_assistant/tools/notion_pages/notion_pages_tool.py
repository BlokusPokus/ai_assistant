"""
Notion Pages Tool - A tool for managing note pages with bidirectional linking.

This tool creates a page-based note structure in Notion with:
- Main page as table of contents
- Individual note pages nested under main page
- Obsidian-style bidirectional linking between pages
- Auto-updating table of contents
- Rich text content support
- Preparation for future RAG integration
"""

import logging
from typing import Optional

from notion_client import Client

from personal_assistant.tools.base import Tool
from .notion_internal import (
    get_notion_client,
    ensure_main_page_exists,
    update_table_of_contents,
    extract_page_properties,
    create_properties_dict
)

# Import notion-specific error handling
from .notion_error_handler import NotionErrorHandler

logger = logging.getLogger(__name__)


class NotionPagesTool:
    """Notion tool for managing note pages with bidirectional linking"""

    def __init__(self):
        # Initialize Notion client
        self.client = get_notion_client()

        # Main page ID for table of contents (will be set during initialization)
        self.main_page_id = None

        # Create individual tools following TOOL_TEMPLATE.md pattern
        self.create_note_page_tool = Tool(
            name="create_note_page",
            func=self.create_note_page,
            description="Create a new note page under the main table of contents page",
            parameters={
                "title": {
                    "type": "string",
                    "description": "Title of the note page (required)"
                },
                "content": {
                    "type": "string",
                    "description": "Content of the note page (required)"
                },
                "tags": {
                    "type": "string",
                    "description": "Comma-separated tags for categorization (optional)"
                },
                "category": {
                    "type": "string",
                    "description": "Category for organizing the note (optional)"
                }
            }
        )

        self.read_note_page_tool = Tool(
            name="read_note_page",
            func=self.read_note_page,
            description="Read note content and properties by page ID or title",
            parameters={
                "page_identifier": {
                    "type": "string",
                    "description": "Page ID or page title to read (required)"
                }
            }
        )

        self.update_note_page_tool = Tool(
            name="update_note_page",
            func=self.update_note_page,
            description="Update note content and properties by page ID",
            parameters={
                "page_id": {
                    "type": "string",
                    "description": "Page ID to update (required)"
                },
                "content": {
                    "type": "string",
                    "description": "New content for the note page (optional)"
                },
                "title": {
                    "type": "string",
                    "description": "New title for the note page (optional)"
                },
                "tags": {
                    "type": "string",
                    "description": "New comma-separated tags (optional)"
                },
                "category": {
                    "type": "string",
                    "description": "New category (optional)"
                }
            }
        )

        self.delete_note_page_tool = Tool(
            name="delete_note_page",
            func=self.delete_note_page,
            description="Delete a note page by page ID",
            parameters={
                "page_id": {
                    "type": "string",
                    "description": "Page ID to delete (required)"
                }
            }
        )

        self.search_notes_tool = Tool(
            name="search_notes",
            func=self.search_notes,
            description="Search across all note pages by content, title, or metadata",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query (required)"
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category (optional)"
                },
                "tags": {
                    "type": "string",
                    "description": "Filter by comma-separated tags (optional)"
                }
            }
        )

        self.get_table_of_contents_tool = Tool(
            name="get_table_of_contents",
            func=self.get_table_of_contents,
            description="Get the current table of contents from the main page",
            parameters={}
        )

        self.create_link_tool = Tool(
            name="create_link",
            func=self.create_link,
            description="Create a link between two pages using Obsidian-style syntax",
            parameters={
                "source_page_id": {
                    "type": "string",
                    "description": "Page ID of the source page (required)"
                },
                "target_page_title": {
                    "type": "string",
                    "description": "Title of the target page to link to (required)"
                }
            }
        )

        self.get_backlinks_tool = Tool(
            name="get_backlinks",
            func=self.get_backlinks,
            description="Get all pages that link to the specified page",
            parameters={
                "page_id": {
                    "type": "string",
                    "description": "Page ID to find backlinks for (required)"
                }
            }
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([
            self.create_note_page_tool,
            self.read_note_page_tool,
            self.update_note_page_tool,
            self.delete_note_page_tool,
            self.search_notes_tool,
            self.get_table_of_contents_tool,
            self.create_link_tool,
            self.get_backlinks_tool
        ])

    async def create_note_page(self, title: str, content: str, tags: Optional[str] = None, category: Optional[str] = None) -> str:
        """Create a new note page under the main table of contents page"""
        try:
            # Validate required parameters
            if not title or not title.strip():
                return NotionErrorHandler.handle_notion_error(
                    ValueError("Title is required"),
                    "create_note_page",
                    {"title": title, "content": content,
                        "tags": tags, "category": category}
                )

            if not content or not content.strip():
                return NotionErrorHandler.handle_notion_error(
                    ValueError("Content is required"),
                    "create_note_page",
                    {"title": title, "content": content,
                        "tags": tags, "category": category}
                )

            # Ensure main page exists
            main_page_id = await ensure_main_page_exists(self.client)

            # Create properties dictionary
            properties = create_properties_dict(title, tags, category)

            # Create the note page
            note_page = self.client.pages.create(
                parent={"type": "page_id", "page_id": main_page_id},
                properties=properties,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": content}}]
                        }
                    }
                ]
            )

            # Don't update table of contents automatically - it causes issues
            # await update_table_of_contents(self.client, main_page_id)

            logger.info(
                f"Created note page: {title} with ID: {note_page['id']}")
            return f"Successfully created note page '{title}' with ID: {note_page['id']}"

        except Exception as e:
            logger.error(f"Error creating note page: {e}")
            return NotionErrorHandler.handle_notion_error(e, "create_note_page", {"title": title, "content": content, "tags": tags, "category": category})

    async def read_note_page(self, page_identifier: str) -> str:
        """Read note content and properties by page ID or title"""
        try:
            page_id = None

            # Check if it's a page ID (UUID format)
            if len(page_identifier.replace("-", "")) == 32:
                page_id = page_identifier
            else:
                # Search by title
                response = self.client.search(
                    query=page_identifier,
                    filter={"property": "object", "value": "page"}
                )

                for page in response.get("results", []):
                    page_title = page.get("properties", {}).get(
                        "title", {}).get("title", [{}])[0].get("plain_text", "")
                    if page_title == page_identifier:
                        page_id = page["id"]
                        break

                if not page_id:
                    return NotionErrorHandler.handle_notion_error(
                        ValueError(
                            f"Page with title '{page_identifier}' not found"),
                        "read_note_page",
                        {"page_identifier": page_identifier}
                    )

            # Get page content
            page = self.client.pages.retrieve(page_id)
            blocks = self.client.blocks.children.list(page_id)

            # Extract content
            content = []
            for block in blocks.get("results", []):
                if block["type"] == "paragraph":
                    text = block["paragraph"]["rich_text"]
                    content.append("".join([t["plain_text"] for t in text]))
                elif block["type"] == "heading_1":
                    text = block["heading_1"]["rich_text"]
                    content.append(
                        f"# {' '.join([t['plain_text'] for t in text])}")
                elif block["type"] == "heading_2":
                    text = block["heading_2"]["rich_text"]
                    content.append(
                        f"## {' '.join([t['plain_text'] for t in text])}")
                elif block["type"] == "bulleted_list_item":
                    text = block["bulleted_list_item"]["rich_text"]
                    content.append(
                        f"- {' '.join([t['plain_text'] for t in text])}")

            # Extract properties
            title, tags, category = extract_page_properties(page)

            result = f"Page: {title}\n"
            if category:
                result += f"Category: {category}\n"
            if tags:
                result += f"Tags: {', '.join([tag['name'] for tag in tags])}\n"
            result += f"Page ID: {page_id}\n\nContent:\n" + "\n".join(content)

            return result

        except Exception as e:
            logger.error(f"Error reading note page: {e}")
            return NotionErrorHandler.handle_notion_error(e, "read_note_page", {"page_identifier": page_identifier})

    async def update_note_page(self, page_id: str, content: Optional[str] = None, title: Optional[str] = None, tags: Optional[str] = None, category: Optional[str] = None) -> str:
        """Update note content and properties by page ID"""
        try:
            # Update page properties if provided
            if title or tags or category:
                properties = create_properties_dict(title, tags, category)
                self.client.pages.update(page_id, properties=properties)

            # Update content if provided
            if content:
                # Clear existing content
                blocks = self.client.blocks.children.list(page_id)
                for block in blocks.get("results", []):
                    self.client.blocks.delete(block["id"])

                # Add new content
                self.client.blocks.children.append(
                    page_id,
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": content}}]
                            }
                        }
                    ]
                )

            logger.info(f"Updated note page: {page_id}")
            return f"Successfully updated note page: {page_id}"

        except Exception as e:
            logger.error(f"Error updating note page: {e}")
            return NotionErrorHandler.handle_notion_error(e, "update_note_page", {"page_id": page_id, "content": content, "title": title, "tags": tags, "category": category})

    async def delete_note_page(self, page_id: str) -> str:
        """Delete a note page by page ID"""
        try:
            # Get page title for logging
            page = self.client.pages.retrieve(page_id)
            title = page.get("properties", {}).get("title", {}).get(
                "title", [{}])[0].get("plain_text", "")

            # Delete the page
            self.client.pages.update(page_id, archived=True)

            # Don't update table of contents automatically - it can cause issues
            # await update_table_of_contents(self.client, self.main_page_id)

            logger.info(f"Deleted note page: {title} ({page_id})")
            return f"Successfully deleted note page: {title}"

        except Exception as e:
            logger.error(f"Error deleting note page: {e}")
            return NotionErrorHandler.handle_notion_error(e, "delete_note_page", {"page_id": page_id})

    async def search_notes(self, query: str, category: Optional[str] = None, tags: Optional[str] = None) -> str:
        """Search across all note pages"""
        try:
            # Build search filter
            filter_params = {"property": "object", "value": "page"}

            # Search in main page children
            main_page_id = await ensure_main_page_exists(self.client)
            blocks = self.client.blocks.children.list(main_page_id)

            results = []
            for block in blocks.get("results", []):
                if block["type"] == "child_page":
                    page_id = block["id"]
                    page = self.client.pages.retrieve(page_id)

                    # Check if page matches search criteria
                    page_title, page_tags, page_category = extract_page_properties(
                        page)

                    # Check category filter
                    if category and page_category != category:
                        continue

                    # Check tags filter
                    if tags:
                        tag_list = [tag.strip() for tag in tags.split(",")]
                        if not any(tag in [t["name"] for t in page_tags] for tag in tag_list):
                            continue

                    # Check if query matches title or content
                    if query.lower() in page_title.lower():
                        results.append(
                            f"Title match: {page_title} (ID: {page_id})")
                        continue

                    # Search in page content
                    page_blocks = self.client.blocks.children.list(page_id)
                    for page_block in page_blocks.get("results", []):
                        if page_block["type"] == "paragraph":
                            text = page_block["paragraph"]["rich_text"]
                            content = "".join([t["plain_text"] for t in text])
                            if query.lower() in content.lower():
                                results.append(
                                    f"Content match: {page_title} (ID: {page_id})")
                                break

            if not results:
                return f"No notes found matching query: {query}"

            return f"Search results for '{query}':\n" + "\n".join(results)

        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            return NotionErrorHandler.handle_notion_error(e, "search_notes", {"query": query, "category": category, "tags": tags})

    async def get_table_of_contents(self) -> str:
        """Get the current table of contents from the main page"""
        try:
            main_page_id = await ensure_main_page_exists(self.client)
            blocks = self.client.blocks.children.list(main_page_id)

            toc_items = []
            for block in blocks.get("results", []):
                if block["type"] == "child_page":
                    page_id = block["id"]
                    page = self.client.pages.retrieve(page_id)
                    title, tags, category = extract_page_properties(page)

                    toc_item = f"- {title} (ID: {page_id})"
                    if category:
                        toc_item += f" [Category: {category}]"
                    if tags:
                        toc_item += f" [Tags: {', '.join([tag['name'] for tag in tags])}]"

                    toc_items.append(toc_item)

            if not toc_items:
                return "Table of contents is empty. No note pages found."

            return "Table of Contents:\n" + "\n".join(toc_items)

        except Exception as e:
            logger.error(f"Error getting table of contents: {e}")
            return NotionErrorHandler.handle_notion_error(e, "get_table_of_contents", {})

    async def create_link(self, source_page_id: str, target_page_title: str) -> str:
        """Create a link between two pages using Obsidian-style syntax"""
        try:
            # Find target page
            response = self.client.search(
                query=target_page_title,
                filter={"property": "object", "value": "page"}
            )

            target_page_id = None
            for page in response.get("results", []):
                page_title = page.get("properties", {}).get(
                    "title", {}).get("title", [{}])[0].get("plain_text", "")
                if page_title == target_page_title:
                    target_page_id = page["id"]
                    break

            if not target_page_id:
                return NotionErrorHandler.handle_notion_error(
                    ValueError(f"Target page '{target_page_title}' not found"),
                    "create_link",
                    {"source_page_id": source_page_id,
                        "target_page_title": target_page_title}
                )

            # Add link to source page content
            link_text = f"[[{target_page_title}]]"

            self.client.blocks.children.append(
                source_page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": link_text}}]
                        }
                    }
                ]
            )

            logger.info(
                f"Created link from {source_page_id} to {target_page_title}")
            return f"Successfully created link from source page to '{target_page_title}'"

        except Exception as e:
            logger.error(f"Error creating link: {e}")
            return NotionErrorHandler.handle_notion_error(e, "create_link", {"source_page_id": source_page_id, "target_page_title": target_page_title})

    async def get_backlinks(self, page_id: str) -> str:
        """Get all pages that link to the specified page"""
        try:
            # Get the page title
            page = self.client.pages.retrieve(page_id)
            page_title = page.get("properties", {}).get(
                "title", {}).get("title", [{}])[0].get("plain_text", "")

            # Search for pages containing links to this page
            main_page_id = await ensure_main_page_exists(self.client)
            blocks = self.client.blocks.children.list(main_page_id)

            backlinks = []
            for block in blocks.get("results", []):
                if block["type"] == "child_page":
                    child_page_id = block["id"]
                    child_page_blocks = self.client.blocks.children.list(
                        child_page_id)

                    for child_block in child_page_blocks.get("results", []):
                        if child_block["type"] == "paragraph":
                            text = child_block["paragraph"]["rich_text"]
                            content = "".join([t["plain_text"] for t in text])

                            # Check for Obsidian-style links
                            if f"[[{page_title}]]" in content:
                                child_page = self.client.pages.retrieve(
                                    child_page_id)
                                child_title = child_page.get("properties", {}).get(
                                    "title", {}).get("title", [{}])[0].get("plain_text", "")
                                backlinks.append(
                                    f"- {child_title} (ID: {child_page_id})")

            if not backlinks:
                return f"No backlinks found for page: {page_title}"

            return f"Backlinks to '{page_title}':\n" + "\n".join(backlinks)

        except Exception as e:
            logger.error(f"Error getting backlinks: {e}")
            return NotionErrorHandler.handle_notion_error(e, "get_backlinks", {"page_id": page_id})
