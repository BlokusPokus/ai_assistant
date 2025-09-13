"""
LLM Notes Enhancer - Core LLM service for note enhancement and analysis.

This module provides specialized LLM capabilities for:
- Content analysis and enhancement
- Automatic tag generation
- Note type detection
- Content structuring
"""

import json
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from ...llm.llm_client import LLMClient
from ...config.logging_config import get_logger

logger = get_logger("notes_enhancer")


class NoteType(Enum):
    """Supported note types for classification"""
    MEETING = "meeting"
    PROJECT = "project"
    PERSONAL = "personal"
    RESEARCH = "research"
    LEARNING = "learning"
    TASK = "task"
    IDEA = "idea"
    JOURNAL = "journal"
    UNKNOWN = "unknown"


@dataclass
class EnhancedNote:
    """Enhanced note with LLM-processed content"""
    original_content: str
    enhanced_content: str
    enhanced_title: str
    note_type: NoteType
    suggested_tags: List[str]
    key_topics: List[str]
    action_items: List[str]
    important_details: List[str]
    structure_suggestions: List[str]
    confidence_score: float


class LLMNotesEnhancer:
    """Specialized LLM service for note enhancement and analysis"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.logger = logger
        
        # Initialize specialized prompts
        self._init_prompts()
    
    def _init_prompts(self):
        """Initialize specialized prompts for different note operations"""
        self.prompts = {
            "comprehensive_analysis": """
You are a specialized note analysis AI. Analyze the following note content and provide a comprehensive response.

Note Content: {content}
Note Title: {title}

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: Choose from meeting, project, personal, research, learning, task, idea, journal, or unknown
2. Key Topics: List 3-5 main subjects or themes
3. Action Items: Extract any tasks, follow-ups, or action items mentioned
4. Important Details: List 3-5 critical pieces of information
5. Structure Suggestions: How to better organize this content (2-3 suggestions)
6. Smart Tags: Generate 3-5 relevant tags for organization and searchability
7. Enhanced Content: Improve the content structure and formatting while preserving meaning
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive title for this note (if no title provided, create one)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Consider the note type when enhancing content:
- Meeting notes: Include date, attendees, discussion points, action items
- Project notes: Include overview, requirements, timeline, next steps
- Personal notes: Include context, details, reminders, follow-up
- Learning notes: Include source, key concepts, examples, practice exercises
- Task notes: Include priorities, completion status, deadlines, dependencies

Return ONLY valid JSON in this exact format:
{{
    "note_type": "string",
    "key_topics": ["topic1", "topic2"],
    "action_items": ["action1", "action2"],
    "important_details": ["detail1", "detail2"],
    "structure_suggestions": ["suggestion1", "suggestion2"],
    "smart_tags": ["tag1", "tag2", "tag3"],
    "enhanced_content": "improved content with better structure",
    "enhanced_title": "clear, descriptive title for the note",
    "confidence_score": 0.85
}}
""",
            "existing_note_enhancement": """
You are a specialized note improvement AI. You are enhancing an EXISTING note that the user has already created. Your job is to improve what's already there, not create something new.

EXISTING Note Content: {content}
EXISTING Note Title: {title}

IMPORTANT: This is an existing note that needs improvement. Focus on:
- Preserving the original meaning and intent
- Improving structure and organization
- Adding missing context or details
- Enhancing readability and clarity
- Making it more actionable and useful

SPECIAL CASE: If the note is empty or has minimal content (like a placeholder), treat it as a fresh start and create comprehensive, well-structured content based on the title and any existing context.

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: Choose from meeting, project, personal, research, learning, task, idea, journal, or unknown
2. Key Topics: List 3-5 main subjects or themes from the existing content
3. Action Items: Extract any tasks, follow-ups, or action items mentioned (preserve existing ones)
4. Important Details: List 3-5 critical pieces of information from the existing content
5. Structure Suggestions: How to better organize this existing content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags for organization and searchability
7. Enhanced Content: Improve the existing content structure and formatting while preserving ALL original meaning
   - Keep the same core information but make it clearer and better organized
   - Add missing context or details that would be helpful
   - Improve formatting and structure
   - For empty notes: Create comprehensive, well-structured content based on the title
   - IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Improve the existing title to be more descriptive and clear
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Focus on IMPROVING what exists rather than creating something new. The user wants their existing note to be better, not replaced.

Return ONLY valid JSON in this exact format:
{{
    "note_type": "string",
    "key_topics": ["topic1", "topic2"],
    "action_items": ["action1", "action2"],
    "important_details": ["detail1", "detail2"],
    "structure_suggestions": ["suggestion1", "suggestion2"],
    "smart_tags": ["tag1", "tag2", "tag3"],
    "enhanced_content": "improved existing content with better structure",
    "enhanced_title": "improved, descriptive title for the existing note",
    "confidence_score": 0.85
}}
"""
        }
    
    async def enhance_note_content(
        self, 
        content: str, 
        title: str = None,
        note_type: Optional[NoteType] = None
    ) -> EnhancedNote:
        """
        Enhance note content using specialized LLM analysis
        
        Args:
            content: Original note content
            title: Note title (optional)
            note_type: Pre-determined note type (optional)
            
        Returns:
            EnhancedNote with all processed information
        """
        try:
            self.logger.info(f"Enhancing note content: {title or 'Untitled'}")
            
            # Use comprehensive analysis prompt for single LLM call
            prompt = self.prompts["comprehensive_analysis"].format(
                content=content,
                title=title or "Untitled"
            )
            
            # Single LLM call that does everything
            response = await self._get_llm_response(prompt)
            
            # Parse the comprehensive response
            analysis = self._parse_llm_json_response(response)
            
            # Convert string note type to enum
            note_type_str = analysis.get("note_type", "unknown").lower()
            note_type_enum = getattr(NoteType, note_type_str.upper(), NoteType.UNKNOWN)
            
            # Create enhanced note object
            enhanced_note = EnhancedNote(
                original_content=content,
                enhanced_content=analysis.get("enhanced_content", content),
                enhanced_title=analysis.get("enhanced_title", title or "Untitled"),
                note_type=note_type_enum,
                suggested_tags=analysis.get("smart_tags", []),
                key_topics=analysis.get("key_topics", []),
                action_items=analysis.get("action_items", []),
                important_details=analysis.get("important_details", []),
                structure_suggestions=analysis.get("structure_suggestions", []),
                confidence_score=analysis.get("confidence_score", 0.0)
            )
            
            self.logger.info(f"Successfully enhanced note: {title or 'Untitled'}")
            return enhanced_note
            
        except Exception as e:
            self.logger.error(f"Error enhancing note content: {e}")
            # Return basic enhanced note on error
            return EnhancedNote(
                original_content=content,
                enhanced_content=content,
                enhanced_title=title or "Untitled",
                note_type=NoteType.UNKNOWN,
                suggested_tags=[],
                key_topics=[],
                action_items=[],
                important_details=[],
                structure_suggestions=[],
                confidence_score=0.0
            )
    
    async def enhance_existing_note_content(
        self, 
        content: str, 
        title: str = None,
        note_type: Optional[NoteType] = None
    ) -> EnhancedNote:
        """
        Enhance existing note content using specialized LLM analysis for existing notes
        
        Args:
            content: Original existing note content
            title: Note title (optional)
            note_type: Pre-determined note type (optional)
            
        Returns:
            EnhancedNote with all processed information
        """
        try:
            self.logger.info(f"Enhancing existing note content: {title or 'Untitled'}")
            
            # Use existing note enhancement prompt
            prompt = self.prompts["existing_note_enhancement"].format(
                content=content,
                title=title or "Untitled"
            )
            
            # Single LLM call that does everything
            response = await self._get_llm_response(prompt)
            
            # Parse the comprehensive response
            analysis = self._parse_llm_json_response(response)
            
            # Convert string note type to enum
            note_type_str = analysis.get("note_type", "unknown").lower()
            note_type_enum = getattr(NoteType, note_type_str.upper(), NoteType.UNKNOWN)
            
            # Create enhanced note object
            enhanced_note = EnhancedNote(
                original_content=content,
                enhanced_content=analysis.get("enhanced_content", content),
                enhanced_title=analysis.get("enhanced_title", title or "Untitled"),
                note_type=note_type_enum,
                suggested_tags=analysis.get("smart_tags", []),
                key_topics=analysis.get("key_topics", []),
                action_items=analysis.get("action_items", []),
                important_details=analysis.get("important_details", []),
                structure_suggestions=analysis.get("structure_suggestions", []),
                confidence_score=analysis.get("confidence_score", 0.0)
            )
            
            self.logger.info(f"Successfully enhanced existing note: {title or 'Untitled'}")
            return enhanced_note
            
        except Exception as e:
            self.logger.error(f"Error enhancing existing note content: {e}")
            # Return basic enhanced note on error
            return EnhancedNote(
                original_content=content,
                enhanced_content=content,
                enhanced_title=title or "Untitled",
                note_type=NoteType.UNKNOWN,
                suggested_tags=[],
                key_topics=[],
                action_items=[],
                important_details=[],
                structure_suggestions=[],
                confidence_score=0.0
            )
    
    def _parse_llm_json_response(self, response: str) -> dict:
        """Parse JSON response from LLM, handling code blocks and special characters"""
        try:
            # Handle cases where response might be wrapped in code blocks
            if "```json" in response:
                # Extract JSON from code block
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            # Clean up any special characters that might break JSON parsing
            json_str = json_str.replace('\u4fac', '')  # Remove problematic unicode characters
            
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"Error parsing LLM JSON response: {e}")
            # Return empty analysis structure as fallback
            return {
                "note_type": "unknown",
                "key_topics": [],
                "action_items": [],
                "important_details": [],
                "structure_suggestions": [],
                "smart_tags": [],
                "enhanced_content": "",
                "enhanced_title": "",
                "confidence_score": 0.0
            }
    
    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM with error handling"""
        try:
            # Use the LLM client to generate response
            response = self.llm_client.complete(prompt, functions={})
            
            # Extract content from response
            if isinstance(response, dict):
                return response.get("content", "")
            else:
                return str(response)
                
        except Exception as e:
            self.logger.error(f"LLM response error: {e}")
            raise
