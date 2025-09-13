"""
Enhanced Notes Tool with Specialized LLM Integration

This module provides the main tool interface for intelligent note management
using specialized LLM calls for content enhancement and analysis.
"""

from typing import Optional, Union, Dict, List

from .llm_notes_enhancer import LLMNotesEnhancer, NoteType
from ..base import Tool
from ...llm.gemini import GeminiLLM
from ...config.logging_config import get_logger
from ...config.settings import settings
from ..notion_pages.notion_internal import create_properties_dict, ensure_main_page_exists

logger = get_logger("enhanced_notes_tool")


class EnhancedNotesTool:
    """Enhanced notes tool with specialized LLM integration"""
    
    def __init__(self):
        self.logger = logger
        
        # Initialize LLM enhancer
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        llm_client = GeminiLLM(api_key=api_key, model=settings.GEMINI_MODEL)
        self.llm_enhancer = LLMNotesEnhancer(llm_client)
        
        # Initialize Notion client
        from ..notion_pages.notion_internal import get_notion_client
        self.notion_client = get_notion_client()
        
        # Create tool instances
        self._create_tools()
    
    def _create_tools(self):
        """Create individual tool instances"""
        
        # Enhanced note creation tool
        self.create_enhanced_note_tool = Tool(
            name="create_enhanced_note",
            func=self.create_enhanced_note,
            description="CREATE NEW: Create a brand new AI-enhanced note from basic content/ideas. Use this when the user wants to create a new note. For enhancing existing notes, use 'find_and_enhance_note' instead.",
            parameters={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Basic content, ideas, or topics for the note - the AI will expand and structure this into a complete note (required)"
                    },
                    "title": {
                        "type": "string", 
                        "description": "Note title (optional - will be generated if not provided)"
                    },
                    "note_type": {
                        "type": "string",
                        "description": "Type of note: meeting, project, personal, research, learning, task, idea, journal (optional - will be auto-detected)"
                    },
                    "auto_tags": {
                        "type": "boolean", 
                        "description": "Whether to generate tags automatically (default: true)"
                    }
                },
                "required": ["content"]
            }
        )
        
        # Smart search tool
        self.smart_search_tool = Tool(
            name="smart_search_notes",
            func=self.smart_search_notes,
            description="SEARCH ONLY: Find and return the most relevant note(s) based on a search query. Use this when you need to find notes but NOT enhance them. For search + enhance in one step, use 'find_and_enhance_note' instead.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - can be natural language (required)"
                    },
                    "note_type": {
                        "type": "string",
                        "description": "Filter by note type: meeting, project, personal, research, learning, task, idea, journal (optional)"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Filter by tags, comma-separated (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        )
        
        # Note enhancement tool (now handles both search + enhance)
        self.enhance_existing_note_tool = Tool(
            name="enhance_existing_note",
            func=self.enhance_existing_note,
            description="ENHANCE NOTES: Find and enhance notes by search query or page ID. Use this for all note enhancement tasks. Can search by description or use specific page ID.",
            parameters={
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "Search query to find the note to enhance (e.g., 'meeting notes from yesterday', 'project timeline'). Use this when you don't have the page ID."
                    },
                    "page_id": {
                        "type": "string",
                        "description": "Specific Notion page ID of the note to enhance. Use this when you know the exact page ID."
                    },
                    "enhancement_type": {
                        "type": "string",
                        "description": "Type of enhancement: structure, tags, summary, all (default: all)"
                    }
                },
                "anyOf": [
                    {"required": ["search_query"]},
                    {"required": ["page_id"]}
                ]
            }
        )
        
        # Note intelligence tool
        self.note_intelligence_tool = Tool(
            name="get_note_intelligence",
            func=self.get_note_intelligence,
            description="Get AI-powered insights and suggestions for a note including key topics, action items, and improvement recommendations.",
            parameters={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Notion page ID of the note to analyze (required)"
                    }
                },
                "required": ["page_id"]
            }
        )
        
    
    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([
            self.create_enhanced_note_tool,
            self.smart_search_tool,
            self.enhance_existing_note_tool,
            self.note_intelligence_tool
        ])
    
    def _create_notion_page(self, main_page_id: str, properties: dict, content: str):
        """Create a Notion page with the given properties and content"""
        return self.notion_client.pages.create(
            parent={"type": "page_id", "page_id": main_page_id},
            properties=properties,
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }]
        )
    
    async def create_enhanced_note(
        self,
        content: str,
        title: Optional[str] = None,
        note_type: Optional[str] = None,
        auto_tags: bool = True
    ) -> Union[str, Dict]:
        """Create a new note with AI-powered enhancement"""
        try:
            # Convert string note_type to enum if provided
            note_type_enum = None
            if note_type:
                try:
                    note_type_enum = NoteType(note_type.lower())
                except ValueError:
                    self.logger.warning(f"Invalid note type: {note_type}")
            
            # Enhance content with LLM (always enhanced for this tool)
            enhanced_note = await self.llm_enhancer.enhance_note_content(
                content, title, note_type_enum
            )
            
            # Use enhanced content and title
            content = enhanced_note.enhanced_content
            title = enhanced_note.enhanced_title
            tags = enhanced_note.suggested_tags if auto_tags else []
            note_type = enhanced_note.note_type.value
            
            # Add metadata to content before creating the note
            content_with_metadata = content
            if tags or note_type:
                content_with_metadata += "\n\n---\n**Metadata:**\n"
                if note_type:
                    content_with_metadata += f"**Category:** {note_type}\n"
                if tags:
                    content_with_metadata += f"**Tags:** {', '.join(tags)}\n"
            
            # Ensure content is under 2000 characters for Notion compatibility
            if len(content_with_metadata) > 2000:
                self.logger.warning(f"Content truncated from {len(content_with_metadata)} to 2000 characters")
                content_with_metadata = content_with_metadata[:1997] + "..."
            
            # Create note in Notion
            main_page_id = await ensure_main_page_exists(self.notion_client)
            properties = create_properties_dict(
                title,
                ", ".join(tags),
                note_type
            )
            
            # Create the page with content including metadata
            note_page = self._create_notion_page(main_page_id, properties, content_with_metadata)
            
            result = f"✅ Successfully created enhanced note '{title}' with ID: {note_page['id']}"
            
            # Update table of contents
            try:
                from ..notion_pages.notion_internal import update_table_of_contents
                await update_table_of_contents(self.notion_client, main_page_id)
            except Exception as toc_error:
                self.logger.warning(f"Failed to update table of contents: {toc_error}")
                result += f"\n⚠️ Note created but table of contents update failed: {toc_error}"
            
            # Add enhancement summary
            result += "\n\n📊 Enhancement Summary:"
            result += f"\n• Note Type: {enhanced_note.note_type.value}"
            result += f"\n• Confidence: {enhanced_note.confidence_score:.2f}"
            result += f"\n• Tags: {', '.join(enhanced_note.suggested_tags)}"
            result += f"\n• Key Topics: {', '.join(enhanced_note.key_topics)}"
            if enhanced_note.action_items:
                result += f"\n• Action Items: {', '.join(enhanced_note.action_items)}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced note: {e}")
            return {
                "error": str(e),
                "message": "Failed to create enhanced note"
            }
    
    async def smart_search_notes(
        self,
        query: str,
        note_type: Optional[str] = None,
        tags: Optional[str] = None,
        limit: int = 20
    ) -> Union[str, Dict]:
        """Search notes using Notion's native search API with LLM-based relevance selection"""
        try:
            self.logger.info(f"Performing smart search: {query}")
            
            # Use Notion's native search API
            search_results = self.notion_client.search(
                query=query,
                filter={"property": "object", "value": "page"},
                page_size=min(limit, 100)  # Notion API limit
            )
            
            if not search_results.get("results"):
                return {
                    "status": "no_results",
                    "action": "search_completed",
                    "message": f"No notes found matching '{query}'",
                    "query": query
                }
            
            # Extract note information
            notes = []
            for page in search_results["results"]:
                # Get page title
                page_title = (
                    page.get("properties", {})
                    .get("title", {})
                    .get("title", [{}])[0]
                    .get("plain_text", "")
                )
                
                # Get page content preview
                try:
                    page_blocks = self.notion_client.blocks.children.list(page["id"])
                    page_content = ""
                    for block in page_blocks.get("results", []):
                        if block["type"] == "paragraph":
                            text = block["paragraph"]["rich_text"]
                            page_content += "".join([t["plain_text"] for t in text])
                except Exception:
                    page_content = ""
                
                notes.append({
                    "page_id": page["id"],
                    "title": page_title,
                    "preview": page_content[:200] + "..." if len(page_content) > 200 else page_content,
                    "created_time": page.get("created_time", ""),
                    "last_edited_time": page.get("last_edited_time", "")
                })
            
            # Use LLM to select the most relevant note
            if len(notes) > 1:
                selected_note = await self._select_most_relevant_note(query, notes)
            else:
                selected_note = notes[0]
            
            # Format response with clear success indicators
            response = {
                "status": "success",
                "action": "note_found",
                "message": "Successfully found and selected the most relevant note",
                "note": {
                    "title": selected_note['title'],
                    "page_id": selected_note['page_id'],
                    "preview": selected_note['preview']
                },
                "search_stats": {
                    "total_matches": len(notes),
                    "query": query
                }
            }
            
            if len(notes) > 1:
                response["search_stats"]["selection_method"] = "LLM-based relevance selection"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error searching notes: {e}")
            return {
                "error": str(e),
                "message": "Failed to search notes"
            }
    
    async def _select_most_relevant_note(self, query: str, notes: List[Dict]) -> Dict:
        """Use LLM to select the most relevant note from search results"""
        try:
            # Prepare notes data for LLM
            notes_text = ""
            for i, note in enumerate(notes, 1):
                notes_text += f"{i}. **{note['title']}**\n"
                notes_text += f"   Preview: {note['preview']}\n"
                notes_text += f"   Created: {note['created_time']}\n\n"
            
            # Create LLM prompt for note selection
            prompt = f"""
You are a helpful assistant that selects the most relevant note based on a user's search query.

User Query: "{query}"

Available Notes:
{notes_text}

Please analyze the user query and the available notes, then select the most relevant one.

Return ONLY the number (1, 2, 3, etc.) of the most relevant note. No explanation needed.
"""
            
            # Get LLM response
            response = await self.llm_enhancer._get_llm_response(prompt)
            
            # Extract the selected number
            try:
                selected_number = int(response.strip())
                if 1 <= selected_number <= len(notes):
                    return notes[selected_number - 1]
                else:
                    # Fallback to first note if invalid selection
                    return notes[0]
            except (ValueError, IndexError):
                # Fallback to first note if parsing fails
                return notes[0]
                
        except Exception as e:
            self.logger.warning(f"Error in LLM note selection: {e}")
            # Fallback to first note
            return notes[0]
    
    async def enhance_existing_note(
        self,
        search_query: str = None,
        page_id: str = None,
        enhancement_type: str = "all"
    ) -> Union[str, Dict]:
        """Enhance an existing note with AI improvements - can search by query or use page ID"""
        try:
            # Determine if we need to search first
            if search_query and not page_id:
                self.logger.info(f"Searching for note to enhance: {search_query}")
                
                # Search for the note first
                search_result = await self.smart_search_notes(search_query, limit=5)
                
                # Check if search was successful
                if isinstance(search_result, dict):
                    if search_result.get("status") == "no_results":
                        return f"❌ No notes found matching '{search_query}'"
                    elif search_result.get("status") == "success":
                        page_id = search_result["note"]["page_id"]
                        title = search_result["note"]["title"]
                    else:
                        return f"❌ Search failed: {search_result.get('message', 'Unknown error')}"
                else:
                    # Fallback for old string format
                    import re
                    if "No notes found" in search_result:
                        return f"❌ No notes found matching '{search_query}'"
                    
                    id_match = re.search(r'\*\*ID:\*\* ([a-f0-9-]+)', search_result)
                    if not id_match:
                        return "❌ Error: Could not extract page ID from search results"
                    
                    page_id = id_match.group(1)
                    title_match = re.search(r'\*\*Title:\*\* (.+)', search_result)
                    title = title_match.group(1) if title_match else "Unknown"
            
            elif not page_id:
                return "❌ Error: Either search_query or page_id must be provided"
            
            # Clean the page_id to remove any newlines or whitespace
            page_id = page_id.strip()
            self.logger.info(f"Enhancing existing note: {page_id}")
            self.logger.debug(f"Page ID length: {len(page_id)}, repr: {repr(page_id)}")
            
            # Get current note content
            page = self.notion_client.pages.retrieve(page_id)
            blocks = self.notion_client.blocks.children.list(page_id)
            
            # Extract content
            content = ""
            for block in blocks.get("results", []):
                if block["type"] == "paragraph":
                    text = block["paragraph"]["rich_text"]
                    content += "".join([t["plain_text"] for t in text]) + "\n"
            
            # Clean up content - remove excessive newlines and strip
            content = content.strip()
            
            # Get title (use from search if available, otherwise get from page)
            if 'title' not in locals():
                title = (
                    page.get("properties", {})
                    .get("title", {})
                    .get("title", [{}])[0]
                    .get("plain_text", "")
                )
            
            # Handle empty notes by creating content based on the title
            if not content.strip():
                self.logger.info(f"Note '{title}' is empty, creating content based on title")
                # Create basic content from the title for enhancement
                content = f"# {title}\n\nThis note is currently empty. Let's add some content to make it more useful and informative."
            
            # Enhance based on type
            if enhancement_type in ["structure", "all"]:
                enhanced_note = await self.llm_enhancer.enhance_existing_note_content(content, title)
                
                # Update content if enhanced
                if enhanced_note.enhanced_content != content:
                    # Ensure content is under 2000 characters for Notion compatibility
                    enhanced_content = enhanced_note.enhanced_content
                    if len(enhanced_content) > 2000:
                        self.logger.warning(f"Enhanced content truncated from {len(enhanced_content)} to 2000 characters")
                        enhanced_content = enhanced_content[:1997] + "..."
                    
                    # Clear existing content (skip archived blocks)
                    for block in blocks.get("results", []):
                        try:
                            # Check if block is archived before trying to delete
                            if not block.get("archived", False):
                                self.notion_client.blocks.delete(block["id"])
                        except Exception as e:
                            self.logger.warning(f"Could not delete block {block['id']}: {e}")
                            # Continue with other blocks even if one fails
                    
                    # Add enhanced content
                    self.notion_client.blocks.children.append(
                        page_id,
                        children=[
                            {
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [
                                        {"type": "text", "text": {"content": enhanced_content}}
                                    ]
                                }
                            }
                        ]
                    )
            
            if enhancement_type in ["tags", "all"]:
                # Note: Tags cannot be added to regular pages in Notion
                # Only database entries can have custom properties
                # For now, we'll skip tag updates for regular pages
                self.logger.info("Tag updates skipped - regular pages cannot have custom properties")
            
            # Create a clear success message similar to create_enhanced_note
            result = f"✅ Successfully enhanced note '{title}' with {enhancement_type} improvements"
            result += f"\n• Note ID: {page_id}"
            result += f"\n• Enhancement Type: {enhancement_type}"
            
            # Add enhancement details if available
            if 'enhanced_note' in locals():
                result += f"\n• Key Topics: {', '.join(enhanced_note.key_topics)}"
                if enhanced_note.action_items:
                    result += f"\n• Action Items: {', '.join(enhanced_note.action_items)}"
                if enhanced_note.suggested_tags:
                    result += f"\n• Suggested Tags: {', '.join(enhanced_note.suggested_tags)}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error enhancing existing note: {e}")
            return f"❌ Error: Failed to enhance note - {str(e)}"
    
    async def get_note_intelligence(
        self,
        page_id: str
    ) -> Union[str, Dict]:
        """Get AI-powered insights and suggestions for a note"""
        try:
            self.logger.info(f"Getting note intelligence for: {page_id}")
            
            # Get note content
            page = self.notion_client.pages.retrieve(page_id)
            blocks = self.notion_client.blocks.children.list(page_id)
            
            content = ""
            for block in blocks.get("results", []):
                if block["type"] == "paragraph":
                    text = block["paragraph"]["rich_text"]
                    content += "".join([t["plain_text"] for t in text]) + "\n"
            
            title = (
                page.get("properties", {})
                .get("title", {})
                .get("title", [{}])[0]
                .get("plain_text", "")
            )
            
            if not content.strip():
                return "No content found in note to analyze"
            
            # Get AI analysis
            enhanced_note = await self.llm_enhancer.enhance_note_content(content, title)
            
            # Format intelligence report
            report = f"🧠 Note Intelligence Report for '{title}':\n\n"
            report += "📊 Analysis:\n"
            report += f"• Note Type: {enhanced_note.note_type.value}\n"
            report += f"• Confidence Score: {enhanced_note.confidence_score:.2f}\n\n"
            
            if enhanced_note.key_topics:
                report += "🎯 Key Topics:\n"
                for topic in enhanced_note.key_topics:
                    report += f"• {topic}\n"
                report += "\n"
            
            if enhanced_note.action_items:
                report += "✅ Action Items:\n"
                for item in enhanced_note.action_items:
                    report += f"• {item}\n"
                report += "\n"
            
            if enhanced_note.important_details:
                report += "💡 Important Details:\n"
                for detail in enhanced_note.important_details:
                    report += f"• {detail}\n"
                report += "\n"
            
            if enhanced_note.suggested_tags:
                report += "🏷️ Suggested Tags:\n"
                report += f"• {', '.join(enhanced_note.suggested_tags)}\n\n"
            
            if enhanced_note.structure_suggestions:
                report += "📝 Structure Suggestions:\n"
                for suggestion in enhanced_note.structure_suggestions:
                    report += f"• {suggestion}\n"
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error getting note intelligence: {e}")
            return {
                "error": str(e),
                "message": "Failed to get note intelligence"
            }
    
    
    def _generate_simple_title(self, content: str) -> str:
        """Generate a simple title from content"""
        lines = content.split('\n')
        first_line = lines[0].strip()
        if len(first_line) > 50:
            return first_line[:47] + "..."
        return first_line or "Untitled Note"
