"""
Internal functions for Enhanced Notes Tool

This module contains internal helper functions and utilities for the Enhanced Notes Tool,
separating internal logic from the main tool interface.
"""

from typing import List, Dict, Optional
from ...config.logging_config import get_logger

logger = get_logger("note_internal")


class NoteInternal:
    """Internal functions and utilities for note operations"""
    
    def __init__(self, llm_enhancer):
        self.llm_enhancer = llm_enhancer
        self.logger = logger
    
    async def select_most_relevant_note(self, query: str, notes: List[Dict]) -> Dict:
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
    
    async def select_best_note_for_deletion(self, notes: List[Dict], search_query: str) -> Dict:
        """Use LLM to select the best note for deletion from multiple matches"""
        try:
            # Prepare note summaries for LLM
            note_summaries = []
            for i, note in enumerate(notes):
                title = (
                    note.get("properties", {})
                    .get("title", {})
                    .get("title", [{}])[0]
                    .get("plain_text", "Untitled")
                )
                note_summaries.append(f"{i+1}. {title}")
            
            # Create selection prompt
            prompt = f"""
You need to select the best note to delete based on the search query.

Search Query: "{search_query}"

Available Notes:
{chr(10).join(note_summaries)}

Select the note number (1-{len(notes)}) that best matches the deletion request.
Consider the search query context and choose the most appropriate note for deletion.

Return ONLY the number (e.g., "2").
"""
            
            response = await self.llm_enhancer._get_llm_response(prompt)
            selected_index = int(response.strip()) - 1
            
            if 0 <= selected_index < len(notes):
                return notes[selected_index]
            else:
                # Fallback to first note
                return notes[0]
                
        except Exception as e:
            self.logger.warning(f"Error in LLM note selection for deletion: {e}")
            # Fallback to first note
            return notes[0]
    
    def generate_simple_title(self, content: str) -> str:
        """Generate a simple title from content"""
        lines = content.split('\n')
        first_line = lines[0].strip()
        if len(first_line) > 50:
            return first_line[:47] + "..."
        return first_line or "Untitled Note"
    
    def extract_note_content(self, blocks: List[Dict]) -> str:
        """Extract text content from Notion blocks"""
        content = ""
        for block in blocks.get("results", []):
            if block["type"] == "paragraph":
                text = block["paragraph"]["rich_text"]
                content += "".join([t["plain_text"] for t in text]) + "\n"
        return content.strip()
    
    def extract_note_title(self, page: Dict) -> str:
        """Extract title from Notion page"""
        return (
            page.get("properties", {})
            .get("title", {})
            .get("title", [{}])[0]
            .get("plain_text", "")
        )
    
    def format_enhancement_summary(self, enhanced_note, domain=None) -> str:
        """Format enhancement summary for display"""
        result = "\n\n📊 Enhancement Summary:"
        result += f"\n• Note Type: {enhanced_note.note_type.value}"
        if domain:
            result += f"\n• Domain: {domain}"
        result += f"\n• Confidence: {enhanced_note.confidence_score:.2f}"
        result += f"\n• Tags: {', '.join(enhanced_note.suggested_tags)}"
        result += f"\n• Key Topics: {', '.join(enhanced_note.key_topics)}"
        if enhanced_note.action_items:
            result += f"\n• Action Items: {', '.join(enhanced_note.action_items)}"
        return result
    
    def format_intelligence_report(self, enhanced_note, title: str) -> str:
        """Format note intelligence report"""
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
    
    def format_search_response(self, selected_note: Dict, notes: List[Dict], query: str) -> Dict:
        """Format search response with clear success indicators"""
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
    
    def format_notes_for_search(self, search_results: Dict, notion_client) -> List[Dict]:
        """Format search results into structured note data"""
        notes = []
        for page in search_results["results"]:
            # Get page title
            page_title = self.extract_note_title(page)
            
            # Get page content preview
            try:
                page_blocks = notion_client.blocks.children.list(page["id"])
                page_content = self.extract_note_content(page_blocks)
            except Exception as e:
                self.logger.warning(f"Could not get page content for {page['id']}: {e}")
                page_content = ""
            
            notes.append({
                "page_id": page["id"],
                "title": page_title,
                "preview": page_content[:200] + "..." if len(page_content) > 200 else page_content,
                "created_time": page.get("created_time", ""),
                "last_edited_time": page.get("last_edited_time", "")
            })
        
        return notes
    
    def validate_enhancement_request(self, enhancement_request: str) -> bool:
        """Validate that enhancement request is not empty"""
        return bool(enhancement_request.strip())
    
    def create_empty_note_content(self, title: str) -> str:
        """Create basic content for empty notes"""
        return f"# {title}\n\nThis note is currently empty. Let's add some content to make it more useful and informative."
    
    def truncate_content_for_notion(self, content: str, max_length: int = 2000) -> str:
        """Truncate content to fit Notion's limits"""
        if len(content) > max_length:
            self.logger.warning(f"Content truncated from {len(content)} to {max_length} characters")
            return content[:max_length-3] + "..."
        return content
    
    def add_metadata_to_content(self, content: str, tags: List[str], note_type: str) -> str:
        """Add metadata section to note content"""
        if not (tags or note_type):
            return content
        
        content_with_metadata = content
        content_with_metadata += "\n\n---\n**Metadata:**\n"
        if note_type:
            content_with_metadata += f"**Category:** {note_type}\n"
        if tags:
            content_with_metadata += f"**Tags:** {', '.join(tags)}\n"
        
        return content_with_metadata
    
    def parse_search_result_for_page_id(self, search_result: str) -> Optional[str]:
        """Parse page ID from old string format search results"""
        import re
        id_match = re.search(r'\*\*ID:\*\* ([a-f0-9-]+)', search_result)
        return id_match.group(1) if id_match else None
    
    def parse_search_result_for_title(self, search_result: str) -> Optional[str]:
        """Parse title from old string format search results"""
        import re
        title_match = re.search(r'\*\*Title:\*\* (.+)', search_result)
        return title_match.group(1) if title_match else None
    
    def clean_page_id(self, page_id: str) -> str:
        """Clean page ID by removing whitespace and newlines"""
        return page_id.strip()
    
    def get_insertion_point_from_strategy(self, insertion_point: str, blocks: List[Dict]) -> Optional[str]:
        """Determine insertion point based on strategy and content analysis"""
        if not insertion_point:
            return None
        
        insertion_point_lower = insertion_point.lower()
        
        if "after" in insertion_point_lower or "end" in insertion_point_lower:
            # Insert at the end
            return blocks[-1]["id"] if blocks else None
        elif "beginning" in insertion_point_lower or "start" in insertion_point_lower:
            # Insert at the beginning
            return None
        else:
            # Try to find a logical insertion point based on content
            for i, block in enumerate(blocks):
                if block["type"] == "paragraph":
                    text_content = ""
                    if "paragraph" in block and "rich_text" in block["paragraph"]:
                        text_content = "".join([t["plain_text"] for t in block["paragraph"]["rich_text"]]).lower()
                    
                    # Look for common section markers
                    if any(marker in text_content for marker in ["overview", "summary", "introduction", "background"]):
                        return block["id"]
                    elif any(marker in text_content for marker in ["action items", "next steps", "todo", "tasks"]):
                        # Insert before action items
                        return blocks[i-1]["id"] if i > 0 else None
        
        return None
