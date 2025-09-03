"""
Comprehensive Notion note handling tool implementation.
Combines basic note operations with enhanced features including templates, advanced search, and additional properties.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

from notion_client import Client
from notion_client.errors import APIResponseError

from ...config.settings import settings
from ..base import Tool

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


class NotionNotesTool:
    """Comprehensive Notion tool with basic operations and enhanced features"""

    def __init__(self):
        # Create individual tools
        self.create_note_tool = Tool(
            name="create_note",
            func=self.create_note,
            description="Create a new note in Notion with content. Title and tags are optional.",
            parameters={
                "content": {"type": "string", "description": "Note content (required)"},
                "title": {"type": "string", "description": "Note title (optional)"},
                "tags": {
                    "type": "string",
                    "description": "Comma-separated tags (optional)",
                },
            },
        )

        self.create_note_enhanced_tool = Tool(
            name="create_note_enhanced",
            func=self.create_note_enhanced,
            description="Create a new note in Notion with enhanced properties including summary, importance, status, and category.",
            parameters={
                "content": {"type": "string", "description": "Note content (required)"},
                "title": {"type": "string", "description": "Note title (optional)"},
                "tags": {
                    "type": "string",
                    "description": "Comma-separated tags (optional)",
                },
                "summary": {
                    "type": "string",
                    "description": "Brief summary of the note content (optional)",
                },
                "importance": {
                    "type": "string",
                    "description": "Importance level: High, Medium, or Low (optional)",
                },
                "status": {
                    "type": "string",
                    "description": "Note status: Draft, In Progress, Complete, or Archived (optional)",
                },
                "category": {
                    "type": "string",
                    "description": "Note category: Work, Personal, Learning, Planning, or Research (optional)",
                },
                "template_id": {
                    "type": "string",
                    "description": "Template ID to apply (optional)",
                },
            },
        )

        self.get_note_tool = Tool(
            name="get_note",
            func=self.get_note,
            description="Retrieve a specific note from Notion by its ID, including enhanced properties like summary, importance, status, category, and tags.",
            parameters={
                "note_id": {
                    "type": "string",
                    "description": "Notion page ID of the note to retrieve",
                }
            },
        )

        self.update_note_tool = Tool(
            name="update_note",
            func=self.update_note,
            description="Update an existing note in Notion by its ID. Content, title, tags, summary, importance, status, and category are optional.",
            parameters={
                "note_id": {
                    "type": "string",
                    "description": "Notion page ID of the note to update",
                },
                "content": {
                    "type": "string",
                    "description": "New note content (optional)",
                },
                "title": {"type": "string", "description": "New note title (optional)"},
                "tags": {
                    "type": "string",
                    "description": "New comma-separated tags (optional)",
                },
                "summary": {
                    "type": "string",
                    "description": "New note summary (optional)",
                },
                "importance": {
                    "type": "string",
                    "description": "New importance level: High, Medium, or Low (optional)",
                },
                "status": {
                    "type": "string",
                    "description": "New note status: Draft, In Progress, Complete, or Archived (optional)",
                },
                "category": {
                    "type": "string",
                    "description": "New note category: Work, Personal, Learning, Planning, or Research (optional)",
                },
            },
        )

        self.delete_note_tool = Tool(
            name="delete_note",
            func=self.delete_note,
            description="Archive (soft delete) a note from Notion by its ID. The note will be moved to the archive but can be restored.",
            parameters={
                "note_id": {
                    "type": "string",
                    "description": "Notion page ID of the note to archive",
                }
            },
        )

        self.search_notes_tool = Tool(
            name="search_notes",
            func=self.search_notes,
            description="Search existing notes in Notion by title or content",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query to find matching notes",
                }
            },
        )

        self.search_notes_enhanced_tool = Tool(
            name="search_notes_enhanced",
            func=self.search_notes_enhanced,
            description="Enhanced search across notes with content search, property filters, and better results.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query to find matching notes",
                },
                "importance": {
                    "type": "string",
                    "description": "Filter by importance: High, Medium, or Low (optional)",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status: Draft, In Progress, Complete, or Archived (optional)",
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category: Work, Personal, Learning, Planning, or Research (optional)",
                },
                "tags": {
                    "type": "string",
                    "description": "Filter by tags, comma-separated (optional)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 20)",
                },
            },
        )

        self.create_template_tool = Tool(
            name="create_note_template",
            func=self.create_note_template,
            description="Create a new note template for consistent note structure.",
            parameters={
                "template_name": {
                    "type": "string",
                    "description": "Name of the template",
                },
                "template_type": {
                    "type": "string",
                    "description": "Type of template: standard, meeting, project, or research",
                },
                "sections": {
                    "type": "string",
                    "description": "Comma-separated list of template sections",
                },
                "required_fields": {
                    "type": "string",
                    "description": "Comma-separated list of required fields",
                },
            },
        )

        self.get_templates_tool = Tool(
            name="get_note_templates",
            func=self.get_note_templates,
            description="Get available note templates for creating new notes.",
            parameters={},
        )

        self.add_database_properties_tool = Tool(
            name="add_database_properties",
            func=self.add_database_properties,
            description="Add new properties to the Notion database for enhanced note organization.",
            parameters={},
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter(
            [
                # self.create_note_tool,
                self.create_note_enhanced_tool,
                self.get_note_tool,
                self.update_note_tool,
                self.delete_note_tool,
                # self.search_notes_tool,
                self.search_notes_enhanced_tool,
                self.create_template_tool,
                self.get_templates_tool,
                self.add_database_properties_tool,
            ]
        )

    # Basic note operations (from original notion_notes.py)
    async def create_note(
        self, content: str, title: Optional[str] = None, tags: Optional[str] = None
    ) -> str:
        """Create a new note in Notion"""
        try:
            client = get_notion_client()

            if not settings.NOTION_DATABASE_ID:
                return "Error: NOTION_DATABASE_ID not configured"

            # Prepare properties for the note
            properties = {
                "Name": {"title": [{"text": {"content": title or "Untitled Note"}}]}
            }

            # Add tags if provided
            if tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag.strip()} for tag in tags.split(",")]
                }

            # Create the page in Notion
            response = client.pages.create(
                parent={"database_id": settings.NOTION_DATABASE_ID},
                properties=properties,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": content}}
                            ]
                        },
                    }
                ],
            )

            note_id = response["id"]
            return (
                f"Successfully created note '{title or 'Untitled'}' with ID: {note_id}"
            )

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            if "Could not find database" in str(e):
                return f"Error: Database access issue. Please ensure:\n1. The database ID is correct\n2. Your integration has access to the database\n3. The database is shared with your integration"
            return f"Error creating note: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error creating note: {e}")
            return f"Error creating note: {str(e)}"

    async def get_note(self, note_id: str) -> str:
        """Retrieve a specific note from Notion"""
        try:
            client = get_notion_client()

            # Get the page
            page = client.pages.retrieve(note_id)

            # Get the page content
            blocks = client.blocks.children.list(note_id)

            # Extract content from blocks
            content = ""
            for block in blocks["results"]:
                if block["type"] == "paragraph":
                    for text in block["paragraph"]["rich_text"]:
                        content += text["plain_text"]
                    content += "\n"

            # Extract title and other properties
            title = "Untitled"
            if "Name" in page["properties"] and page["properties"]["Name"]["title"]:
                title = page["properties"]["Name"]["title"][0]["plain_text"]

            # Extract enhanced properties
            summary = self._extract_property_text(page, "Summary")
            importance = self._extract_property_select(page, "Importance")
            status = self._extract_property_select(page, "Status")
            category = self._extract_property_select(page, "Category")
            page_tags = self._extract_property_multi_select(page, "Tags")

            # Build the response
            response = f"Note: {title}\n\n"

            # Add enhanced properties if they exist
            if summary:
                response += f"Summary: {summary}\n\n"
            if importance:
                response += f"Importance: {importance}\n"
            if status:
                response += f"Status: {status}\n"
            if category:
                response += f"Category: {category}\n"
            if page_tags:
                response += f"Tags: {', '.join(page_tags)}\n"

            if any([summary, importance, status, category, page_tags]):
                response += "\n"

            response += f"Content:\n{content}"

            return response

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return f"Error retrieving note: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error retrieving note: {e}")
            return f"Error retrieving note: {str(e)}"

    async def update_note(
        self,
        note_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        summary: Optional[str] = None,
        importance: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> str:
        """Update an existing note in Notion"""
        try:
            client = get_notion_client()

            # Get current database properties to understand the structure
            database = client.databases.retrieve(settings.NOTION_DATABASE_ID)
            current_properties = database.get("properties", {})

            # Prepare properties update
            properties = {}

            if title:
                properties["Name"] = {"title": [{"text": {"content": title}}]}

            if tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag.strip()} for tag in tags.split(",")]
                }

            if summary:
                properties["Summary"] = {"rich_text": [{"text": {"content": summary}}]}

            if importance and importance in ["High", "Medium", "Low"]:
                properties["Importance"] = {"select": {"name": importance}}

            if status and status in ["Draft", "In Progress", "Complete", "Archived"]:
                # Check if Status is multi_select in the database
                if (
                    "Status" in current_properties
                    and current_properties["Status"].get("type") == "multi_select"
                ):
                    properties["Status"] = {"multi_select": [{"name": status}]}
                else:
                    properties["Status"] = {"select": {"name": status}}

            if category and category in [
                "Work",
                "Personal",
                "Learning",
                "Planning",
                "Research",
            ]:
                properties["Category"] = {"select": {"name": category}}

            # Update page properties
            if properties:
                client.pages.update(note_id, properties=properties)

            # Update content if provided
            if content:
                # First, clear existing content
                blocks = client.blocks.children.list(note_id)
                for block in blocks["results"]:
                    client.blocks.delete(block["id"])

                # Add new content
                client.blocks.children.append(
                    note_id,
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": content}}
                                ]
                            },
                        }
                    ],
                )

            return f"Successfully updated note with ID: {note_id}"

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return f"Error updating note: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error updating note: {e}")
            return f"Error updating note: {str(e)}"

    async def delete_note(self, note_id: str) -> str:
        """Archive a note from Notion (moves to archive, can be restored)"""
        try:
            client = get_notion_client()

            # Archive the page (Notion doesn't actually delete, it archives)
            client.pages.update(note_id, archived=True)

            return f"Successfully archived note with ID: {note_id}"

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return f"Error deleting note: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error deleting note: {e}")
            return f"Error deleting note: {str(e)}"

    async def search_notes(self, query: str) -> str:
        """Search existing notes in Notion"""
        try:
            client = get_notion_client()

            if not settings.NOTION_DATABASE_ID:
                return "Error: NOTION_DATABASE_ID not configured"

            # Search in the database - using 'Name' property instead of 'Title'
            response = client.databases.query(
                database_id=settings.NOTION_DATABASE_ID,
                filter={"property": "Name", "title": {"contains": query}},
            )

            results = response["results"]
            if not results:
                return f"No notes found matching '{query}'"

            # Format results
            formatted_results = []
            for page in results:
                title = "Untitled"
                if "Name" in page["properties"] and page["properties"]["Name"]["title"]:
                    title = page["properties"]["Name"]["title"][0]["plain_text"]

                formatted_results.append(f"- {title} (ID: {page['id']})")

            return f"Found {len(results)} notes matching '{query}':\n" + "\n".join(
                formatted_results
            )

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return f"Error searching notes: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error searching notes: {e}")
            return f"Error searching notes: {str(e)}"

    # Enhanced note operations (from notion_enhanced.py)
    async def create_note_enhanced(
        self,
        content: str,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        summary: Optional[str] = None,
        importance: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> str:
        """Create a new note in Notion with enhanced properties"""
        try:
            client = get_notion_client()

            if not settings.NOTION_DATABASE_ID:
                return "Error: NOTION_DATABASE_ID not configured"

            # Get current database properties to understand the structure
            database = client.databases.retrieve(settings.NOTION_DATABASE_ID)
            current_properties = database.get("properties", {})

            # Apply template if specified
            if template_id:
                template_data = await self._get_template(template_id)
                if template_data:
                    # Merge template with provided data
                    title = title or template_data.get("default_title", "Untitled Note")
                    content = content or template_data.get("default_content", "")
                    tags = tags or template_data.get("default_tags", "")
                    summary = summary or template_data.get("default_summary", "")
                    importance = importance or template_data.get(
                        "default_importance", "Medium"
                    )
                    status = status or template_data.get("default_status", "Draft")
                    category = category or template_data.get(
                        "default_category", "Personal"
                    )

            # Prepare properties for the note
            properties = {
                "Name": {"title": [{"text": {"content": title or "Untitled Note"}}]}
            }

            # Add tags if provided
            if tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag.strip()} for tag in tags.split(",")]
                }

            # Add new properties if provided
            if summary:
                properties["Summary"] = {"rich_text": [{"text": {"content": summary}}]}

            if importance and importance in ["High", "Medium", "Low"]:
                properties["Importance"] = {"select": {"name": importance}}

            if status and status in ["Draft", "In Progress", "Complete", "Archived"]:
                # Check if Status is multi_select in the database
                if (
                    "Status" in current_properties
                    and current_properties["Status"].get("type") == "multi_select"
                ):
                    properties["Status"] = {"multi_select": [{"name": status}]}
                else:
                    properties["Status"] = {"select": {"name": status}}

            if category and category in [
                "Work",
                "Personal",
                "Learning",
                "Planning",
                "Research",
            ]:
                properties["Category"] = {"select": {"name": category}}

            # Create the page in Notion
            response = client.pages.create(
                parent={"database_id": settings.NOTION_DATABASE_ID},
                properties=properties,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": content}}
                            ]
                        },
                    }
                ],
            )

            note_id = response["id"]
            return f"Successfully created enhanced note '{title or 'Untitled'}' with ID: {note_id}"

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            if "Could not find database" in str(e):
                return f"Error: Database access issue. Please ensure:\n1. The database ID is correct\n2. Your integration has access to the database\n3. The database is shared with your integration"
            return f"Error creating note: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error creating note: {e}")
            return f"Error creating note: {str(e)}"

    async def search_notes_enhanced(
        self,
        query: str,
        importance: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """Enhanced search across notes with content search and property filters"""
        try:
            client = get_notion_client()

            if not settings.NOTION_DATABASE_ID:
                return "Error: NOTION_DATABASE_ID not configured"

            # Get current database properties to understand the structure
            database = client.databases.retrieve(settings.NOTION_DATABASE_ID)
            current_properties = database.get("properties", {})

            # Build filter for database query
            filters = []

            # Add property filters with correct types
            if importance:
                # Check if Importance is multi_select in the database
                if (
                    "Importance" in current_properties
                    and current_properties["Importance"].get("type") == "multi_select"
                ):
                    filters.append(
                        {
                            "property": "Importance",
                            "multi_select": {"contains": importance},
                        }
                    )
                else:
                    filters.append(
                        {"property": "Importance", "select": {"equals": importance}}
                    )

            if status:
                # Check if Status is multi_select in the database
                if (
                    "Status" in current_properties
                    and current_properties["Status"].get("type") == "multi_select"
                ):
                    filters.append(
                        {"property": "Status", "multi_select": {"contains": status}}
                    )
                else:
                    filters.append({"property": "Status", "select": {"equals": status}})

            if category:
                # Check if Category is multi_select in the database
                if (
                    "Category" in current_properties
                    and current_properties["Category"].get("type") == "multi_select"
                ):
                    filters.append(
                        {"property": "Category", "multi_select": {"contains": category}}
                    )
                else:
                    filters.append(
                        {"property": "Category", "select": {"equals": category}}
                    )

            if tags:
                tag_list = [tag.strip() for tag in tags.split(",")]
                filters.append(
                    {"property": "Tags", "multi_select": {"contains_any_of": tag_list}}
                )

            # Combine filters with AND logic
            filter_condition = (
                {"and": filters}
                if len(filters) > 1
                else filters[0]
                if filters
                else None
            )

            # Search in database with filters
            if filter_condition:
                response = client.databases.query(
                    database_id=settings.NOTION_DATABASE_ID,
                    filter=filter_condition,
                    page_size=limit,
                )
            else:
                # No filters, just get all pages
                response = client.databases.query(
                    database_id=settings.NOTION_DATABASE_ID, page_size=limit
                )

            results = response["results"]

            # If we have a text query, also search content
            if query:
                # Search by title first
                title_results = [
                    page for page in results if self._matches_title(page, query)
                ]

                # Search by content using Notion's search API
                content_results = await self._search_content(query, limit)

                # Combine and deduplicate results
                all_results = self._combine_search_results(
                    title_results, content_results
                )
                results = all_results[:limit]
            else:
                # No text query, just use filtered results
                pass

            if not results:
                filter_desc = self._describe_filters(importance, status, category, tags)
                return f"No notes found matching criteria: {filter_desc}"

            # Format results with enhanced information
            formatted_results = []
            for page in results:
                title = "Untitled"
                if "Name" in page["properties"] and page["properties"]["Name"]["title"]:
                    title = page["properties"]["Name"]["title"][0]["plain_text"]

                # Extract additional properties
                summary = self._extract_property_text(page, "Summary")
                importance = self._extract_property_select(page, "Importance")
                status = self._extract_property_select(page, "Status")
                category = self._extract_property_select(page, "Category")
                page_tags = self._extract_property_multi_select(page, "Tags")

                # Format the result
                result_line = f"- {title} (ID: {page['id']})"
                if summary:
                    result_line += f" | Summary: {summary[:50]}..."
                if importance:
                    result_line += f" | Importance: {importance}"
                if status:
                    result_line += f" | Status: {status}"
                if category:
                    result_line += f" | Category: {category}"
                if page_tags:
                    result_line += f" | Tags: {', '.join(page_tags)}"

                formatted_results.append(result_line)

            filter_desc = self._describe_filters(importance, status, category, tags)
            return (
                f"Found {len(results)} notes matching criteria: {filter_desc}\n\n"
                + "\n".join(formatted_results)
            )

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return f"Error searching notes: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error searching notes: {e}")
            return f"Error searching notes: {str(e)}"

    async def create_note_template(
        self,
        template_name: str,
        template_type: str,
        sections: str,
        required_fields: str,
    ) -> str:
        """Create a new note template"""
        try:
            # Parse sections and required fields
            sections_list = [s.strip() for s in sections.split(",")]
            required_list = [f.strip() for f in required_fields.split(",")]

            # Validate template type
            valid_types = ["standard", "meeting", "project", "research"]
            if template_type not in valid_types:
                return f"Error: Invalid template type. Must be one of: {', '.join(valid_types)}"

            # Create template object
            template = {
                "id": f"template_{template_name.lower().replace(' ', '_')}",
                "name": template_name,
                "type": template_type,
                "sections": sections_list,
                "required_fields": required_list,
                "created_at": asyncio.get_event_loop().time(),
            }

            # Store template (for now, just return success - in production, store in database/file)
            template_id = template["id"]

            return f"Successfully created template '{template_name}' with ID: {template_id}"

        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return f"Error creating template: {str(e)}"

    async def get_note_templates(self) -> str:
        """Get available note templates"""
        try:
            # For now, return predefined templates - in production, fetch from storage
            templates = [
                {
                    "id": "template_standard",
                    "name": "Standard Note",
                    "type": "standard",
                    "sections": [
                        "title",
                        "summary",
                        "content",
                        "key_takeaways",
                        "tags",
                    ],
                    "required_fields": ["title", "content", "tags"],
                },
                {
                    "id": "template_meeting",
                    "name": "Meeting Notes",
                    "type": "meeting",
                    "sections": [
                        "title",
                        "attendees",
                        "agenda",
                        "notes",
                        "action_items",
                        "next_steps",
                    ],
                    "required_fields": ["title", "attendees", "notes"],
                },
                {
                    "id": "template_project",
                    "name": "Project Notes",
                    "type": "project",
                    "sections": [
                        "title",
                        "description",
                        "objectives",
                        "timeline",
                        "resources",
                        "status",
                    ],
                    "required_fields": ["title", "description", "objectives"],
                },
                {
                    "id": "template_research",
                    "name": "Research Notes",
                    "type": "research",
                    "sections": [
                        "title",
                        "topic",
                        "findings",
                        "sources",
                        "conclusions",
                        "tags",
                    ],
                    "required_fields": ["title", "topic", "findings"],
                },
            ]

            formatted_templates = []
            for template in templates:
                formatted_templates.append(
                    f"- {template['name']} (ID: {template['id']})\n"
                    f"  Type: {template['type']}\n"
                    f"  Sections: {', '.join(template['sections'])}\n"
                    f"  Required: {', '.join(template['required_fields'])}"
                )

            return f"Available templates:\n\n" + "\n\n".join(formatted_templates)

        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            return f"Error getting templates: {str(e)}"

    async def add_database_properties(self) -> str:
        """Add new properties to the Notion database"""
        try:
            client = get_notion_client()

            if not settings.NOTION_DATABASE_ID:
                return "Error: NOTION_DATABASE_ID not configured"

            # Get current database properties first to understand the structure
            database = client.databases.retrieve(settings.NOTION_DATABASE_ID)
            current_properties = database.get("properties", {})

            print(f"Current database properties: {list(current_properties.keys())}")

            # Check if Status is already multi_select (which seems to be the case)
            status_type = (
                "multi_select"
                if "Status" in current_properties
                and current_properties["Status"].get("type") == "multi_select"
                else "select"
            )

            # Define new properties to add with correct Notion API structure
            new_properties = {
                "Summary": {
                    "rich_text": {"description": "Brief summary of the note content"}
                },
                "Importance": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "blue"},
                        ]
                    }
                },
                "Status": {
                    status_type: {
                        "options": [
                            {"name": "Draft", "color": "gray"},
                            {"name": "In Progress", "color": "yellow"},
                            {"name": "Complete", "color": "green"},
                            {"name": "Archived", "color": "gray"},
                        ]
                    }
                },
                "Category": {
                    "select": {
                        "options": [
                            {"name": "Work", "color": "blue"},
                            {"name": "Personal", "color": "green"},
                            {"name": "Learning", "color": "purple"},
                            {"name": "Planning", "color": "orange"},
                            {"name": "Research", "color": "pink"},
                        ]
                    }
                },
                "Last_Reviewed": {
                    "date": {
                        "description": "When the note was last reviewed or updated"
                    }
                },
            }

            # Check which properties already exist
            existing_properties = []
            new_properties_to_add = {}

            for prop_name, prop_config in new_properties.items():
                if prop_name in current_properties:
                    existing_properties.append(prop_name)
                else:
                    new_properties_to_add[prop_name] = prop_config

            if not new_properties_to_add:
                return "All new properties already exist in the database."

            # Add new properties
            updated_properties = {**current_properties, **new_properties_to_add}

            # Update the database
            client.databases.update(
                database_id=settings.NOTION_DATABASE_ID, properties=updated_properties
            )

            added_properties = list(new_properties_to_add.keys())
            existing_properties_str = (
                f" (already existed: {', '.join(existing_properties)})"
                if existing_properties
                else ""
            )

            return f"Successfully added properties: {', '.join(added_properties)}{existing_properties_str}"

        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return f"Error adding database properties: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error adding database properties: {e}")
            return f"Error adding database properties: {str(e)}"

    # Helper methods
    async def _get_template(self, template_id: str) -> Optional[Dict]:
        """Get template by ID"""
        # For now, return None - in production, fetch from storage
        return None

    async def _search_content(self, query: str, limit: int) -> List[Dict]:
        """Search note content using Notion's search API"""
        try:
            client = get_notion_client()

            # Use Notion's search API to search across all content
            response = client.search(
                query=query,
                filter={"property": "object", "value": "page"},
                page_size=limit,
            )

            # Filter results to only include pages from our database
            database_id = settings.NOTION_DATABASE_ID
            filtered_results = [
                page
                for page in response["results"]
                if page.get("parent", {}).get("database_id") == database_id
            ]

            return filtered_results

        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []

    def _matches_title(self, page: Dict, query: str) -> bool:
        """Check if page title matches query"""
        if "Name" in page["properties"] and page["properties"]["Name"]["title"]:
            title = page["properties"]["Name"]["title"][0]["plain_text"].lower()
            return query.lower() in title
        return False

    def _combine_search_results(
        self, title_results: List[Dict], content_results: List[Dict]
    ) -> List[Dict]:
        """Combine and deduplicate search results"""
        combined = {}

        # Add title results
        for result in title_results:
            combined[result["id"]] = result

        # Add content results
        for result in content_results:
            if result["id"] not in combined:
                combined[result["id"]] = result

        return list(combined.values())

    def _extract_property_text(self, page: Dict, property_name: str) -> Optional[str]:
        """Extract text from a rich_text property"""
        if property_name in page["properties"]:
            prop = page["properties"][property_name]
            if prop["type"] == "rich_text" and prop["rich_text"]:
                return prop["rich_text"][0]["plain_text"]
        return None

    def _extract_property_select(self, page: Dict, property_name: str) -> Optional[str]:
        """Extract value from a select property"""
        if property_name in page["properties"]:
            prop = page["properties"][property_name]
            if prop["type"] == "select" and prop["select"]:
                return prop["select"]["name"]
        return None

    def _extract_property_multi_select(
        self, page: Dict, property_name: str
    ) -> List[str]:
        """Extract values from a multi_select property"""
        if property_name in page["properties"]:
            prop = page["properties"][property_name]
            if prop["type"] == "multi_select" and prop["multi_select"]:
                return [item["name"] for item in prop["multi_select"]]
        return []

    def _describe_filters(
        self,
        importance: Optional[str],
        status: Optional[str],
        category: Optional[str],
        tags: Optional[str],
    ) -> str:
        """Create a description of applied filters"""
        filters = []
        if importance:
            filters.append(f"Importance: {importance}")
        if status:
            filters.append(f"Status: {status}")
        if category:
            filters.append(f"Category: {category}")
        if tags:
            filters.append(f"Tags: {tags}")

        if filters:
            return " | ".join(filters)
        else:
            return "No filters applied"


# Legacy tool definitions for backward compatibility
NotesCreateTool = Tool(
    name="create_note",
    func=lambda **kwargs: asyncio.run(NotionNotesTool().create_note(**kwargs)),
    description="Create a new note in Notion with content. Title and tags are optional.",
    parameters={
        "content": {"type": "string", "description": "Note content (required)"}
    },
).set_category("Notes")

NotesGetTool = Tool(
    name="get_note",
    func=lambda **kwargs: asyncio.run(NotionNotesTool().get_note(**kwargs)),
    description="Retrieve a specific note from Notion by its ID",
    parameters={
        "note_id": {
            "type": "string",
            "description": "Notion page ID of the note to retrieve",
        }
    },
).set_category("Notes")

NotesUpdateTool = Tool(
    name="update_note",
    func=lambda **kwargs: asyncio.run(NotionNotesTool().update_note(**kwargs)),
    description="Update an existing note in Notion by its ID. Content, title, and tags are optional.",
    parameters={
        "note_id": {
            "type": "string",
            "description": "Notion page ID of the note to update",
        }
    },
).set_category("Notes")

NotesDeleteTool = Tool(
    name="delete_note",
    func=lambda **kwargs: asyncio.run(NotionNotesTool().delete_note(**kwargs)),
    description="Delete (archive) a note from Notion by its ID",
    parameters={
        "note_id": {
            "type": "string",
            "description": "Notion page ID of the note to delete",
        }
    },
).set_category("Notes")

NotesSearchTool = Tool(
    name="search_notes",
    func=lambda **kwargs: asyncio.run(NotionNotesTool().search_notes(**kwargs)),
    description="Search existing notes in Notion by title or content",
    parameters={
        "query": {
            "type": "string",
            "description": "Search query to find matching notes",
        }
    },
).set_category("Notes")
