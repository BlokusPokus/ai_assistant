"""
Enhanced Notes Tool with Specialized LLM Integration

This module provides the main tool interface for intelligent note management
using specialized LLM calls for content enhancement and analysis.
"""

from typing import Optional, Union, Dict

from .llm_notes_enhancer import LLMNotesEnhancer, StrategyEnhancedNote
from .prompt_templates import NoteType
from .note_internal import NoteInternal
from ..base import Tool
from ...llm.gemini import GeminiLLM
from ...config.logging_config import get_logger
from ...config.settings import settings

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
        
        # Initialize internal functions
        self.note_internal = NoteInternal(self.llm_enhancer)
        
        # Initialize user-specific Notion components
        from .notion_internal_user_specific import UserSpecificNotionInternal
        self.notion_internal = UserSpecificNotionInternal()
        
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
                    "domain": {
                        "type": "string",
                        "description": "Domain specialization: technical, business, creative, academic, general (optional - defaults to general)"
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
            description="ENHANCE NOTES: Find and enhance notes by search query or page ID. Supports smart strategies: replace (modify existing), append (add at end), insert (add at specific location). All strategies are valid and successful. CRITICAL: This tool completes the enhancement in ONE call and returns 'TASK COMPLETED' - NEVER retry if you see success messages. Use this for all note enhancement tasks.",
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
                    "enhancement_request": {
                        "type": "string",
                        "description": "What you want to enhance or add to the note (e.g., 'add recent updates', 'update the timeline section', 'add action items after overview'). The AI will choose the best strategy (append/insert/replace) automatically."
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
        
        # Simple note creation tool
        self.create_simple_note_tool = Tool(
            name="create_simple_note",
            func=self.create_simple_note,
            description="CREATE SIMPLE NOTE: Create a basic note without AI enhancement. Use this for quick notes, simple text, or when you want to preserve the exact content without AI processing.",
            parameters={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Note content - will be saved exactly as provided without AI enhancement (required)"
                    },
                    "title": {
                        "type": "string", 
                        "description": "Note title (optional - will be generated from content if not provided)"
                    }
                },
                "required": ["content"]
            }
        )
        
        # Delete note tool
        self.delete_note_tool = Tool(
            name="delete_note",
            func=self.delete_note,
            description="DELETE NOTES: Delete notes by search query or page ID. Use this to remove notes that are no longer needed. IMPORTANT: This action is irreversible.",
            parameters={
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "Search query to find the note to delete (e.g., 'meeting notes from yesterday', 'old project notes'). Use this when you don't have the page ID."
                    },
                    "page_id": {
                        "type": "string",
                        "description": "Specific Notion page ID of the note to delete. Use this when you know the exact page ID."
                    },
                    "confirm_deletion": {
                        "type": "boolean",
                        "description": "Confirmation flag - must be true to actually delete the note. This prevents accidental deletions."
                    }
                },
                "anyOf": [
                    {"required": ["search_query", "confirm_deletion"]},
                    {"required": ["page_id", "confirm_deletion"]}
                ]
            }
        )
        
        # Bidirectional linking tools
        self.create_link_tool = Tool(
            name="create_link",
            func=self.create_link,
            description="Create a bidirectional link between two notes using Obsidian-style [[Page Name]] syntax",
            parameters={
                "type": "object",
                "properties": {
                    "source_page_id": {
                        "type": "string",
                        "description": "Page ID of the source page (where the link will be added)"
                    },
                    "target_page_title": {
                        "type": "string",
                        "description": "Title of the target page to link to"
                    },
                    "link_text": {
                        "type": "string",
                        "description": "Optional custom text for the link (defaults to target page title)"
                    }
                },
                "required": ["source_page_id", "target_page_title"]
            }
        )
        
        self.get_backlinks_tool = Tool(
            name="get_backlinks",
            func=self.get_backlinks,
            description="Get all pages that link to the specified page (reverse references)",
            parameters={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID to find backlinks for"
                    }
                },
                "required": ["page_id"]
            }
        )
        
        self.get_table_of_contents_tool = Tool(
            name="get_table_of_contents",
            func=self.get_table_of_contents,
            description="Get the current table of contents from the user's Personal Assistant page",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "User ID for the table of contents"
                    }
                },
                "required": ["user_id"]
            }
        )
        
    
    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([
            self.create_enhanced_note_tool,
            self.create_simple_note_tool,
            self.smart_search_tool,
            self.enhance_existing_note_tool,
            self.note_intelligence_tool,
            self.delete_note_tool,
            self.create_link_tool,
            self.get_backlinks_tool,
            self.get_table_of_contents_tool
        ])
    
    
    async def create_enhanced_note(
        self,
        content: str,
        title: Optional[str] = None,
        note_type: Optional[str] = None,
        domain: Optional[str] = None,
        auto_tags: bool = True,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Create a new note with AI-powered enhancement"""
        try:
                        # Create note in user's Notion workspace
            if not user_id:
                return "Error: User ID is required for creating notes"
            # Convert string note_type to enum if provided
            note_type_enum = None
            if note_type:
                try:
                    note_type_enum = NoteType(note_type.lower())
                except ValueError:
                    self.logger.warning(f"Invalid note type: {note_type}")
            
            # Domain will be handled internally by the LLM enhancer
            
            # Enhance content with LLM (always enhanced for this tool)
            enhanced_note = await self.llm_enhancer.enhance_note_content(
                content, title, note_type_enum, domain
            )
            
            # Use enhanced content and title
            content = enhanced_note.enhanced_content
            title = enhanced_note.enhanced_title
            tags = enhanced_note.suggested_tags if auto_tags else []
            note_type = enhanced_note.note_type.value
            
            # Add metadata to content before creating the note
            content_with_metadata = self.note_internal.add_metadata_to_content(content, tags, note_type)
            
            # Ensure content is under 2000 characters for Notion compatibility
            #TODO: This should be done in 2 calls instead of truncating
            content_with_metadata = self.note_internal.truncate_content_for_notion(content_with_metadata)
            

            
            # Get database session (this should be injected from the tool execution context)
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                # Ensure user has Personal Assistant page
                main_page_id = await self.notion_internal.ensure_user_main_page_exists(db, user_id)
                
                # Create the note page in user's workspace
                note_page_id = await self.notion_internal.create_user_page(
                    db, user_id, title, content_with_metadata, main_page_id
                )
            
            result = f"✅ Successfully created enhanced note '{title}' with ID: {note_page_id}"
            
            # Add enhancement summary
            result += self.note_internal.format_enhancement_summary(enhanced_note, domain)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced note: {e}")
            return {
                "error": str(e),
                "message": "Failed to create enhanced note"
            }
    
    async def create_simple_note(
        self,
        content: str,
        title: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Create a simple note without AI enhancement"""
        try:
            if not user_id:
                return "Error: User ID is required for creating notes"
            
            # Generate title from content if not provided
            if not title:
                # Use first line or first 50 characters as title
                first_line = content.split('\n')[0].strip()
                title = first_line[:50] + "..." if len(first_line) > 50 else first_line
                if not title:
                    title = "Untitled Note"
            
            # Ensure content is under 2000 characters for Notion compatibility
            content = self.note_internal.truncate_content_for_notion(content)
            
            # Get database session
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                # Ensure user has Personal Assistant page
                main_page_id = await self.notion_internal.ensure_user_main_page_exists(db, user_id)
                
                # Create the note page in user's workspace
                note_page_id = await self.notion_internal.create_user_page(
                    db, user_id, title, content, main_page_id
                )
            
            return f"✅ Successfully created simple note '{title}' with ID: {note_page_id}"
            
        except Exception as e:
            self.logger.error(f"Error creating simple note: {e}")
            return {
                "error": str(e),
                "message": "Failed to create simple note"
            }
    
    async def smart_search_notes(
        self,
        query: str,
        limit: int = 20,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Search notes using Notion's native search API with LLM-based relevance selection"""
        try:
            self.logger.info(f"Performing smart search: {query}")
            
            if not user_id:
                self.logger.error("User ID is required for note search")
                return {
                    "error": "User ID is required for note search",
                    "message": "Failed to search notes"
                }
            
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Use Notion's native search API
            search_results = notion_client.search(
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
            notes = self.note_internal.format_notes_for_search(search_results, notion_client)
            
            # Use LLM to select the most relevant note
            if len(notes) > 1:
                selected_note = await self.note_internal.select_most_relevant_note(query, notes)
            else:
                selected_note = notes[0]
            
            # Format response with clear success indicators
            return self.note_internal.format_search_response(selected_note, notes, query)
            
        except Exception as e:
            self.logger.error(f"Error searching notes: {e}")
            return {
                "error": str(e),
                "message": "Failed to search notes"
            }
    
    
    async def enhance_existing_note(
        self,
        search_query: str = None,
        page_id: str = None,
        enhancement_request: str = "",
        enhancement_type: str = "all",
        user_id: Optional[int] = None
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
                    if "No notes found" in search_result:
                        return f"❌ No notes found matching '{search_query}'"
                    
                    page_id = self.note_internal.parse_search_result_for_page_id(search_result)
                    if not page_id:
                        return "❌ Error: Could not extract page ID from search results"
                    
                    title = self.note_internal.parse_search_result_for_title(search_result) or "Unknown"
            
            elif not page_id:
                return "❌ Error: Either search_query or page_id must be provided"
            
            # Clean the page_id to remove any newlines or whitespace
            page_id = self.note_internal.clean_page_id(page_id)
            self.logger.info(f"Enhancing existing note: {page_id}")
            self.logger.debug(f"Page ID length: {len(page_id)}, repr: {repr(page_id)}")
            
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Get current note content
            page = notion_client.pages.retrieve(page_id)
            blocks = notion_client.blocks.children.list(page_id)
            
            # Extract content
            content = self.note_internal.extract_note_content(blocks)
            
            # Get title (use from search if available, otherwise get from page)
            if 'title' not in locals():
                title = self.note_internal.extract_note_title(page)
            
            # Handle empty notes by creating content based on the title
            if not content.strip():
                self.logger.info(f"Note '{title}' is empty, creating content based on title")
                content = self.note_internal.create_empty_note_content(title)
            
            # Use strategy-aware enhancement
            if enhancement_type in ["structure", "all"]:
                # Add a simple check to prevent duplicate enhancements
                if not self.note_internal.validate_enhancement_request(enhancement_request):
                    self.logger.warning("No enhancement request provided, skipping enhancement")
                    return f"✅ Note '{title}' accessed successfully (no enhancement requested)"
                
                strategy_note = await self.llm_enhancer.enhance_note_with_strategy(
                    content, title, enhancement_request
                )
                
                # Apply the determined strategy
                result = await self.apply_enhancement_strategy(page_id, strategy_note, notion_client)
                
                # Add explicit completion message at the start
                result = "🎯 ENHANCEMENT TASK COMPLETED SUCCESSFULLY\n" + result
                
                # Add clear completion status with proper formatting
                result += "\n\n🎯 ENHANCEMENT COMPLETED SUCCESSFULLY"
                result += f"\n📊 Strategy Used: {strategy_note.update_strategy.title()}"
                result += f"\n💭 AI Reasoning: {strategy_note.reasoning}"
                if strategy_note.insertion_point:
                    result += f"\n📍 Target Location: {strategy_note.insertion_point}"
                result += f"\n📝 Note Type: {strategy_note.note_type.value.title()}"
                result += f"\n🎯 Confidence: {strategy_note.confidence_score:.2f}"
                if strategy_note.key_topics:
                    result += f"\n🔑 Key Topics: {', '.join(strategy_note.key_topics)}"
                if strategy_note.action_items:
                    result += f"\n✅ Action Items: {', '.join(strategy_note.action_items)}"
                
                result += "\n\n✨ TASK COMPLETED: The note has been successfully enhanced. No further action needed."
                
                return result
            
            if enhancement_type in ["tags", "all"]:
                # Note: Tags cannot be added to regular pages in Notion
                # Only database entries can have custom properties
                # For now, we'll skip tag updates for regular pages
                self.logger.info("Tag updates skipped - regular pages cannot have custom properties")
            
            # If we get here without enhancement, return basic success message
            return f"✅ Note '{title}' processed successfully"
            
        except Exception as e:
            self.logger.error(f"Error enhancing existing note: {e}")
            return f"❌ Error: Failed to enhance note - {str(e)}"
    
    async def apply_enhancement_strategy(
        self, 
        page_id: str, 
        strategy_note: StrategyEnhancedNote,
        notion_client
    ) -> str:
        """Apply the determined enhancement strategy"""
        
        if strategy_note.update_strategy == "replace":
            return await self._apply_replace_strategy(page_id, strategy_note, notion_client)
        elif strategy_note.update_strategy == "append":
            return await self._apply_append_strategy(page_id, strategy_note, notion_client)
        elif strategy_note.update_strategy == "insert":
            return await self._apply_insert_strategy(page_id, strategy_note, notion_client)
        else:
            # Fallback to replace
            self.logger.warning(f"Unknown strategy '{strategy_note.update_strategy}', falling back to replace")
            return await self._apply_replace_strategy(page_id, strategy_note, notion_client)

    async def _apply_replace_strategy(self, page_id: str, strategy_note: StrategyEnhancedNote, notion_client):
        """Apply replace strategy (current behavior)"""
        try:
            # Clear existing content
            blocks = notion_client.blocks.children.list(page_id)
            for block in blocks.get("results", []):
                if not block.get("archived", False):
                    notion_client.blocks.delete(block["id"])
            
            # Add enhanced content
            notion_client.blocks.children.append(
                page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": strategy_note.new_content}}]
                    }
                }]
            )
            return "✅ SUCCESS: Note content replaced with enhanced version. TASK COMPLETED."
        except Exception as e:
            self.logger.error(f"Error in replace strategy: {e}")
            return f"❌ Error applying replace strategy: {str(e)}"

    async def _apply_append_strategy(self, page_id: str, strategy_note: StrategyEnhancedNote, notion_client):
        """Apply append strategy - add new content at the end"""
        try:
            # Add new content at the end
            notion_client.blocks.children.append(
                page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": strategy_note.new_content}}]
                    }
                }]
            )
            return "✅ SUCCESS: New content added to the end of the note. TASK COMPLETED."
        except Exception as e:
            self.logger.error(f"Error in append strategy: {e}")
            return f"❌ Error applying append strategy: {str(e)}"

    async def _apply_insert_strategy(self, page_id: str, strategy_note: StrategyEnhancedNote, notion_client):
        """Apply insert strategy - add content at specific location"""
        try:
            self.logger.info(f"Applying insert strategy at: {strategy_note.insertion_point}")
            
            # Get current blocks to find insertion point
            blocks_response = notion_client.blocks.children.list(page_id)
            blocks = blocks_response.get("results", [])
            
            # Find the best insertion point based on content analysis
            insert_after_block_id = self.note_internal.get_insertion_point_from_strategy(
                strategy_note.insertion_point, blocks
            )
            
            # Insert the new content
            if insert_after_block_id:
                # Insert after the specified block
                notion_client.blocks.children.append(
                    page_id,
                    children=[{
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": strategy_note.new_content}}]
                        }
                    }],
                    after=insert_after_block_id
                )
                return "✅ SUCCESS: New content inserted at the specified location. TASK COMPLETED."
            else:
                # Fall back to append if no specific location found
                return await self._apply_append_strategy(page_id, strategy_note, notion_client)
                
        except Exception as e:
            self.logger.error(f"Error in insert strategy: {e}")
            # Fall back to append on error
            return await self._apply_append_strategy(page_id, strategy_note, notion_client)
    
    async def get_note_content(
        self,
        page_id: str,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Get raw note content for RAG indexing"""
        try:
            self.logger.info(f"Getting note content for: {page_id}")
            
            if not user_id:
                self.logger.error("User ID is required for note content retrieval")
                return {
                    "error": "User ID is required for note content retrieval",
                    "message": "Failed to get note content"
                }
            
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Get note content
            page = notion_client.pages.retrieve(page_id)
            blocks = notion_client.blocks.children.list(page_id)
            
            content = self.note_internal.extract_note_content(blocks)
            title = self.note_internal.extract_note_title(page)
            
            if not content.strip():
                return ""
            
            # Return structured content for RAG system
            return {
                "title": title,
                "content": content,
                "page_id": page_id,
                "user_id": user_id
            }
            
        except Exception as e:
            self.logger.error(f"Error getting note content: {e}")
            return {
                "error": str(e),
                "message": "Failed to get note content"
            }
    
    async def get_note_intelligence(
        self,
        page_id: str,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Get AI-powered insights and suggestions for a note"""
        try:
            self.logger.info(f"Getting note intelligence for: {page_id}")
            
            if not user_id:
                self.logger.error("User ID is required for note intelligence")
                return {
                    "error": "User ID is required for note intelligence",
                    "message": "Failed to get note intelligence"
                }
            
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Get note content
            page = notion_client.pages.retrieve(page_id)
            blocks = notion_client.blocks.children.list(page_id)
            
            content = self.note_internal.extract_note_content(blocks)
            title = self.note_internal.extract_note_title(page)
            
            if not content.strip():
                return "No content found in note to analyze"
            
            # Get AI analysis
            enhanced_note = await self.llm_enhancer.enhance_note_content(content, title)
            
            # Format intelligence report
            return self.note_internal.format_intelligence_report(enhanced_note, title)
            
        except Exception as e:
            self.logger.error(f"Error getting note intelligence: {e}")
            return {
                "error": str(e),
                "message": "Failed to get note intelligence"
            }
    
    async def delete_note(
        self,
        search_query: str = None,
        page_id: str = None,
        confirm_deletion: bool = False,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Delete a note by search query or page ID with confirmation"""
        try:
            # Validate confirmation
            if not confirm_deletion:
                return "❌ Deletion not confirmed. Set confirm_deletion=true to proceed with deletion."
            
            # Determine if we need to search first
            if search_query and not page_id:
                self.logger.info(f"Searching for note to delete: {search_query}")
                
                # Get user's Notion client
                from personal_assistant.config.database import db_config
                async with db_config.get_session_context() as db:
                    notion_client = await self.notion_internal.get_user_client(db, user_id)
                    self.logger.info(f"Successfully obtained Notion client for user {user_id}")
                
                # Search for notes
                search_results = notion_client.search(
                    query=search_query,
                    filter={"property": "object", "value": "page"}
                )
                
                notes = search_results.get("results", [])
                if not notes:
                    return f"❌ No notes found matching search query: '{search_query}'"
                
                # Use LLM to select the best note if multiple found
                if len(notes) > 1:
                    selected_note = await self.note_internal.select_best_note_for_deletion(notes, search_query)
                else:
                    selected_note = notes[0]
                
                page_id = selected_note["id"]
            
            # Validate page_id
            if not page_id:
                return "❌ Error: No page ID provided for deletion"
            
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Get note details before deletion
            try:
                page = notion_client.pages.retrieve(page_id)
                title = self.note_internal.extract_note_title(page) or "Untitled"
            except Exception as e:
                self.logger.warning(f"Could not retrieve page details: {e}")
                title = "Unknown"
            
            # Archive the page (Notion's way of "deleting")
            notion_client.pages.update(
                page_id,
                archived=True
            )
            
            self.logger.info(f"Successfully deleted note: {title} (ID: {page_id})")
            
            return f"✅ Successfully deleted note '{title}' (ID: {page_id})"
            
        except Exception as e:
            self.logger.error(f"Error deleting note: {e}")
            return f"❌ Error: Failed to delete note - {str(e)}"
    
    async def create_link(
        self,
        source_page_id: str,
        target_page_title: str,
        link_text: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Create a bidirectional link between two notes using Obsidian-style syntax"""
        try:
            if not user_id:
                return "Error: User ID is required for creating links"
            
            # Use target page title as link text if not provided
            if not link_text:
                link_text = target_page_title
            
            # Create Obsidian-style link syntax
            link_syntax = f"[[{link_text}]]"
            
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Add the link to the source page
            notion_client.blocks.children.append(
                source_page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": link_syntax}}]
                    }
                }]
            )
            
            return f"✅ Successfully created link '{link_syntax}' in page {source_page_id}"
            
        except Exception as e:
            self.logger.error(f"Error creating link: {e}")
            return f"❌ Error: Failed to create link - {str(e)}"
    
    async def get_backlinks(
        self,
        page_id: str,
        user_id: Optional[int] = None
    ) -> Union[str, Dict]:
        """Get all pages that link to the specified page"""
        try:
            if not user_id:
                return "Error: User ID is required for getting backlinks"
            
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Get the target page to find its title
            target_page = notion_client.pages.retrieve(page_id)
            target_title = self.note_internal.extract_note_title(target_page)
            
            # Search for pages that contain links to this page
            search_results = notion_client.search(
                query=f"[[{target_title}]]",
                filter={"property": "object", "value": "page"}
            )
            
            backlinks = []
            for page in search_results.get("results", []):
                if page["id"] != page_id:  # Don't include the page itself
                    page_title = self.note_internal.extract_note_title(page)
                    backlinks.append({
                        "page_id": page["id"],
                        "title": page_title,
                        "created_time": page.get("created_time", ""),
                        "last_edited_time": page.get("last_edited_time", "")
                    })
            
            if not backlinks:
                return f"No backlinks found for '{target_title}'"
            
            # Format backlinks response
            result = f"📎 Found {len(backlinks)} backlink(s) for '{target_title}':\n\n"
            for i, link in enumerate(backlinks, 1):
                result += f"{i}. **{link['title']}**\n"
                result += f"   ID: {link['page_id']}\n"
                result += f"   Last edited: {link['last_edited_time']}\n\n"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting backlinks: {e}")
            return f"❌ Error: Failed to get backlinks - {str(e)}"
    
    async def get_table_of_contents(
        self,
        user_id: int
    ) -> Union[str, Dict]:
        """Get the current table of contents from the user's Personal Assistant page"""
        try:
            # Get user's Notion client
            from personal_assistant.config.database import db_config
            async with db_config.get_session_context() as db:
                notion_client = await self.notion_internal.get_user_client(db, user_id)
                self.logger.info(f"Successfully obtained Notion client for user {user_id}")
            
            # Get the user's main Personal Assistant page
            main_page_id = await self.notion_internal.ensure_user_main_page_exists(db, user_id)
            
            # Get the page content
            blocks = notion_client.blocks.children.list(main_page_id)
            
            # Extract table of contents
            toc_content = self.note_internal.extract_note_content(blocks)
            
            if not toc_content.strip():
                return "No table of contents found. The Personal Assistant page may be empty."
            
            return f"📋 **Table of Contents**\n\n{toc_content}"
            
        except Exception as e:
            self.logger.error(f"Error getting table of contents: {e}")
            return f"❌ Error: Failed to get table of contents - {str(e)}"
    
    
    
