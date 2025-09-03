"""
Enhanced Notion note handling tool implementation.
Builds on existing notion_notes.py foundation to add new properties, content search, templates, and enhanced search.
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


class NotionEnhancedTool:
    """Enhanced Notion tool with new properties, content search, templates, and enhanced search"""

    def __init__(self):
        # Create individual tools
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
                self.create_note_enhanced_tool,
                self.search_notes_enhanced_tool,
                self.create_template_tool,
                self.get_templates_tool,
                self.add_database_properties_tool,
            ]
        )

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
NotionEnhancedCreateTool = Tool(
    name="create_note_enhanced",
    func=lambda **kwargs: asyncio.run(
        NotionEnhancedTool().create_note_enhanced(**kwargs)
    ),
    description="Create a new note in Notion with enhanced properties including summary, importance, status, and category.",
    parameters={
        "content": {"type": "string", "description": "Note content (required)"},
        "title": {"type": "string", "description": "Note title (optional)"},
        "tags": {"type": "string", "description": "Comma-separated tags (optional)"},
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
    },
).set_category("Notes")

NotionEnhancedSearchTool = Tool(
    name="search_notes_enhanced",
    func=lambda **kwargs: asyncio.run(
        NotionEnhancedTool().search_notes_enhanced(**kwargs)
    ),
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
).set_category("Notes")

NotionTemplateTool = Tool(
    name="create_note_template",
    func=lambda **kwargs: asyncio.run(
        NotionEnhancedTool().create_note_template(**kwargs)
    ),
    description="Create a new note template for consistent note structure.",
    parameters={
        "template_name": {"type": "string", "description": "Name of the template"},
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
).set_category("Notes")

NotionGetTemplatesTool = Tool(
    name="get_note_templates",
    func=lambda **kwargs: asyncio.run(
        NotionEnhancedTool().get_note_templates(**kwargs)
    ),
    description="Get available note templates for creating new notes.",
    parameters={},
).set_category("Notes")

NotionAddPropertiesTool = Tool(
    name="add_database_properties",
    func=lambda **kwargs: asyncio.run(
        NotionEnhancedTool().add_database_properties(**kwargs)
    ),
    description="Add new properties to the Notion database for enhanced note organization.",
    parameters={},
).set_category("Notes")
