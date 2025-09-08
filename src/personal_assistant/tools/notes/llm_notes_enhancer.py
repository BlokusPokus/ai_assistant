"""
LLM Notes Enhancer - Core LLM service for note enhancement and analysis.

This module provides specialized LLM capabilities for:
- Content analysis and enhancement
- Automatic tag generation
- Note type detection
- Content structuring
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
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
8. Confidence Score: Rate your analysis confidence (0.0-1.0)

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
    "confidence_score": 0.85
}}
""",
            
            "note_type_classification": """
Classify the following note content into one of these types:
- meeting: Meeting notes, discussions, decisions
- project: Project planning, documentation, progress
- personal: Personal thoughts, plans, memories
- research: Research findings, analysis, sources
- learning: Educational content, tutorials, study notes
- task: Task lists, to-dos, reminders
- idea: Brainstorming, creative ideas, concepts
- journal: Daily logs, reflections, experiences

Content: {content}
Title: {title}

Return only the classification type (lowercase).
""",
            
            "tag_generation": """
You are a tag generation AI. Based on the note content and analysis, generate 3-5 relevant tags.

Content: {content}
Title: {title}
Note Type: {note_type}
Key Topics: {key_topics}

Consider:
- Main topics and themes
- Note type and purpose
- Key people or projects mentioned
- Time sensitivity or priority
- Category or domain

Generate tags that will help with organization and searchability. Return as a JSON array:
["tag1", "tag2", "tag3"]
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
            
            analysis = json.loads(json_str)
            
            # Map string response to enum
            type_mapping = {
                "meeting": NoteType.MEETING,
                "project": NoteType.PROJECT,
                "personal": NoteType.PERSONAL,
                "research": NoteType.RESEARCH,
                "learning": NoteType.LEARNING,
                "task": NoteType.TASK,
                "idea": NoteType.IDEA,
                "journal": NoteType.JOURNAL
            }
            
            note_type_enum = type_mapping.get(analysis.get("note_type", "unknown"), NoteType.UNKNOWN)
            
            # Create enhanced note object
            enhanced_note = EnhancedNote(
                original_content=content,
                enhanced_content=analysis.get("enhanced_content", content),
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
                note_type=NoteType.UNKNOWN,
                suggested_tags=[],
                key_topics=[],
                action_items=[],
                important_details=[],
                structure_suggestions=[],
                confidence_score=0.0
            )
    
    async def detect_note_type(self, content: str, title: str = None) -> NoteType:
        """Detect the type of note based on content analysis"""
        try:
            prompt = self.prompts["note_type_classification"].format(
                content=content,
                title=title or "Untitled"
            )
            
            response = await self._get_llm_response(prompt)
            note_type_str = response.strip().lower()
            
            # Map string response to enum
            type_mapping = {
                "meeting": NoteType.MEETING,
                "project": NoteType.PROJECT,
                "personal": NoteType.PERSONAL,
                "research": NoteType.RESEARCH,
                "learning": NoteType.LEARNING,
                "task": NoteType.TASK,
                "idea": NoteType.IDEA,
                "journal": NoteType.JOURNAL
            }
            
            return type_mapping.get(note_type_str, NoteType.UNKNOWN)
            
        except Exception as e:
            self.logger.error(f"Error detecting note type: {e}")
            return NoteType.UNKNOWN
    
    async def generate_smart_tags(
        self, 
        content: str, 
        title: str = None,
        note_type: NoteType = None,
        key_topics: List[str] = None
    ) -> List[str]:
        """Generate intelligent tags based on content analysis"""
        try:
            prompt = self.prompts["tag_generation"].format(
                content=content,
                title=title or "Untitled",
                note_type=note_type.value if note_type else "unknown",
                key_topics=", ".join(key_topics) if key_topics else "none"
            )
            
            response = await self._get_llm_response(prompt)
            tags = json.loads(response)
            
            # Validate and clean tags
            if isinstance(tags, list):
                return [tag.strip().lower() for tag in tags if tag.strip()]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error generating tags: {e}")
            return []
    
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
