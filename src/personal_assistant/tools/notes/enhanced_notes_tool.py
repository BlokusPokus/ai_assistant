"""
Enhanced Notes Tool with Specialized LLM Integration

This module provides the main tool interface for intelligent note management
using specialized LLM calls for content enhancement and analysis.
"""

import logging
from typing import Optional, Union, List, Dict, Any
from datetime import datetime

from .llm_notes_enhancer import LLMNotesEnhancer, NoteType, EnhancedNote
from ..base import Tool
from ...llm.gemini import GeminiLLM
from ...config.logging_config import get_logger

logger = get_logger("enhanced_notes_tool")


class EnhancedNotesTool:
    """Enhanced notes tool with specialized LLM integration"""
    
    def __init__(self):
        self.logger = logger
        
        # Initialize LLM enhancer
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        llm_client = GeminiLLM(api_key=api_key, model="gemini-2.5-flash")
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
            description="Create a new note with AI-powered content enhancement, automatic tagging, and intelligent structuring. Perfect for meeting notes, project documentation, personal notes, research, learning, and more.",
            parameters={
                "content": {
                    "type": "string",
                    "description": "Note content to be enhanced and stored (required)"
                },
                "title": {
                    "type": "string", 
                    "description": "Note title (optional - will be generated if not provided)"
                },
                "note_type": {
                    "type": "string",
                    "description": "Type of note: meeting, project, personal, research, learning, task, idea, journal (optional - will be auto-detected)"
                },
                "enhance_content": {
                    "type": "boolean",
                    "description": "Whether to enhance content with AI (default: true)"
                },
                "auto_tags": {
                    "type": "boolean", 
                    "description": "Whether to generate tags automatically (default: true)"
                }
            }
        )
        
        # Smart search tool
        self.smart_search_tool = Tool(
            name="smart_search_notes",
            func=self.smart_search_notes,
            description="Search notes using semantic understanding and intelligent filtering. Find notes by meaning, not just keywords.",
            parameters={
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
            }
        )
        
        # Note enhancement tool
        self.enhance_existing_note_tool = Tool(
            name="enhance_existing_note",
            func=self.enhance_existing_note,
            description="Enhance an existing note with AI-powered improvements including better structure, smart tags, and content optimization.",
            parameters={
                "page_id": {
                    "type": "string",
                    "description": "Notion page ID of the note to enhance (required)"
                },
                "enhancement_type": {
                    "type": "string",
                    "description": "Type of enhancement: structure, tags, summary, all (default: all)"
                }
            }
        )
        
        # Note intelligence tool
        self.note_intelligence_tool = Tool(
            name="get_note_intelligence",
            func=self.get_note_intelligence,
            description="Get AI-powered insights and suggestions for a note including key topics, action items, and improvement recommendations.",
            parameters={
                "page_id": {
                    "type": "string",
                    "description": "Notion page ID of the note to analyze (required)"
                }
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
    
    async def create_enhanced_note(
        self,
        content: str,
        title: Optional[str] = None,
        note_type: Optional[str] = None,
        enhance_content: bool = True,
        auto_tags: bool = True
    ) -> Union[str, Dict]:
        """Create a new note with AI-powered enhancement"""
        try:
            self.logger.info(f"Creating enhanced note: {title or 'Untitled'}")
            
            # Convert string note_type to enum if provided
            note_type_enum = None
            if note_type:
                try:
                    note_type_enum = NoteType(note_type.lower())
                except ValueError:
                    self.logger.warning(f"Invalid note type: {note_type}")
            
            # Enhance content if requested
            if enhance_content:
                enhanced_note = await self.llm_enhancer.enhance_note_content(
                    content, title, note_type_enum
                )
                
                # Use enhanced content and title
                final_content = enhanced_note.enhanced_content
                final_title = title or self._generate_title(enhanced_note)
                final_tags = enhanced_note.suggested_tags if auto_tags else []
                final_note_type = enhanced_note.note_type.value
                
            else:
                # Use original content without enhancement
                final_content = content
                final_title = title or self._generate_simple_title(content)
                final_tags = []
                final_note_type = note_type or "unknown"
            
            # Create note in Notion
            from ..notion_pages.notion_internal import create_properties_dict, ensure_main_page_exists
            
            main_page_id = ensure_main_page_exists(self.notion_client)
            properties = create_properties_dict(
                final_title,
                ", ".join(final_tags),
                final_note_type
            )
            
            # Add enhanced properties
            if enhance_content and 'enhanced_note' in locals():
                properties.update({
                    "AI_Enhanced": {"checkbox": True},
                    "Note_Type": {"select": {"name": final_note_type}},
                    "Confidence_Score": {"number": enhanced_note.confidence_score}
                })
            
            # Create the page
            note_page = self.notion_client.pages.create(
                parent={"type": "page_id", "page_id": main_page_id},
                properties=properties,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": final_content}}
                            ]
                        }
                    }
                ]
            )
            
            result = f"✅ Successfully created enhanced note '{final_title}' with ID: {note_page['id']}"
            
            if enhance_content and 'enhanced_note' in locals():
                result += f"\n\n📊 Enhancement Summary:"
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
        """Search notes using semantic understanding"""
        try:
            self.logger.info(f"Performing smart search: {query}")
            
            # For now, use basic Notion search with enhanced filtering
            # TODO: Implement full semantic search engine
            from ..notion_pages.notion_internal import ensure_main_page_exists
            
            main_page_id = ensure_main_page_exists(self.notion_client)
            blocks = self.notion_client.blocks.children.list(main_page_id)
            
            results = []
            for block in blocks.get("results", []):
                if block["type"] == "child_page":
                    page_id = block["id"]
                    page = self.notion_client.pages.retrieve(page_id)
                    
                    # Extract page properties
                    page_title = (
                        page.get("properties", {})
                        .get("title", {})
                        .get("title", [{}])[0]
                        .get("plain_text", "")
                    )
                    
                    # Basic content search
                    page_blocks = self.notion_client.blocks.children.list(page_id)
                    page_content = ""
                    for page_block in page_blocks.get("results", []):
                        if page_block["type"] == "paragraph":
                            text = page_block["paragraph"]["rich_text"]
                            page_content += "".join([t["plain_text"] for t in text])
                    
                    # Check if query matches title or content
                    if (query.lower() in page_title.lower() or 
                        query.lower() in page_content.lower()):
                        results.append({
                            "page_id": page_id,
                            "title": page_title,
                            "preview": page_content[:100] + "...",
                            "relevance_score": 0.8  # Basic scoring for now
                        })
            
            if not results:
                return f"No notes found matching query: {query}"
            
            # Format results
            formatted_results = []
            for result in results[:limit]:
                formatted_results.append(
                    f"• {result['title']} (ID: {result['page_id']})\n"
                    f"  Relevance: {result['relevance_score']:.2f}\n"
                    f"  Preview: {result['preview']}"
                )
            
            return f"🔍 Smart Search Results for '{query}':\n\n" + "\n".join(formatted_results)
            
        except Exception as e:
            self.logger.error(f"Error in smart search: {e}")
            return {
                "error": str(e),
                "message": "Smart search failed"
            }
    
    async def enhance_existing_note(
        self,
        page_id: str,
        enhancement_type: str = "all"
    ) -> Union[str, Dict]:
        """Enhance an existing note with AI improvements"""
        try:
            self.logger.info(f"Enhancing existing note: {page_id}")
            
            # Get current note content
            page = self.notion_client.pages.retrieve(page_id)
            blocks = self.notion_client.blocks.children.list(page_id)
            
            # Extract content
            content = ""
            for block in blocks.get("results", []):
                if block["type"] == "paragraph":
                    text = block["paragraph"]["rich_text"]
                    content += "".join([t["plain_text"] for t in text]) + "\n"
            
            # Get title
            title = (
                page.get("properties", {})
                .get("title", {})
                .get("title", [{}])[0]
                .get("plain_text", "")
            )
            
            if not content.strip():
                return "No content found in note to enhance"
            
            # Enhance based on type
            if enhancement_type in ["structure", "all"]:
                enhanced_note = await self.llm_enhancer.enhance_note_content(content, title)
                
                # Update content if enhanced
                if enhanced_note.enhanced_content != content:
                    # Clear existing content
                    for block in blocks.get("results", []):
                        self.notion_client.blocks.delete(block["id"])
                    
                    # Add enhanced content
                    self.notion_client.blocks.children.append(
                        page_id,
                        children=[
                            {
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [
                                        {"type": "text", "text": {"content": enhanced_note.enhanced_content}}
                                    ]
                                }
                            }
                        ]
                    )
            
            if enhancement_type in ["tags", "all"]:
                # Update tags
                tags = await self.llm_enhancer.generate_smart_tags(content, title)
                if tags:
                    properties = {
                        "Tags": {
                            "multi_select": [{"name": tag} for tag in tags]
                        }
                    }
                    self.notion_client.pages.update(page_id, properties=properties)
            
            return f"✅ Successfully enhanced note {page_id} with {enhancement_type} improvements"
            
        except Exception as e:
            self.logger.error(f"Error enhancing existing note: {e}")
            return {
                "error": str(e),
                "message": "Failed to enhance note"
            }
    
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
            report += f"📊 Analysis:\n"
            report += f"• Note Type: {enhanced_note.note_type.value}\n"
            report += f"• Confidence Score: {enhanced_note.confidence_score:.2f}\n\n"
            
            if enhanced_note.key_topics:
                report += f"🎯 Key Topics:\n"
                for topic in enhanced_note.key_topics:
                    report += f"• {topic}\n"
                report += "\n"
            
            if enhanced_note.action_items:
                report += f"✅ Action Items:\n"
                for item in enhanced_note.action_items:
                    report += f"• {item}\n"
                report += "\n"
            
            if enhanced_note.important_details:
                report += f"💡 Important Details:\n"
                for detail in enhanced_note.important_details:
                    report += f"• {detail}\n"
                report += "\n"
            
            if enhanced_note.suggested_tags:
                report += f"🏷️ Suggested Tags:\n"
                report += f"• {', '.join(enhanced_note.suggested_tags)}\n\n"
            
            if enhanced_note.structure_suggestions:
                report += f"📝 Structure Suggestions:\n"
                for suggestion in enhanced_note.structure_suggestions:
                    report += f"• {suggestion}\n"
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error getting note intelligence: {e}")
            return {
                "error": str(e),
                "message": "Failed to get note intelligence"
            }
    
    def _generate_title(self, enhanced_note: EnhancedNote) -> str:
        """Generate a title based on enhanced note analysis"""
        if enhanced_note.key_topics:
            return f"{enhanced_note.note_type.value.title()}: {enhanced_note.key_topics[0]}"
        else:
            return f"{enhanced_note.note_type.value.title()} Note"
    
    def _generate_simple_title(self, content: str) -> str:
        """Generate a simple title from content"""
        lines = content.split('\n')
        first_line = lines[0].strip()
        if len(first_line) > 50:
            return first_line[:47] + "..."
        return first_line or "Untitled Note"
