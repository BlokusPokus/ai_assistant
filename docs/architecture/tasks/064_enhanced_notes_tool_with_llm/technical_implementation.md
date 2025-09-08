# Technical Implementation: Enhanced Notes Tool with Specialized LLM

## 🏗️ **Architecture Overview**

### **System Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    Enhanced Notes Tool                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ LLM Notes       │  │ Content         │  │ Semantic     │ │
│  │ Enhancer        │  │ Processor       │  │ Search       │ │
│  │                 │  │                 │  │ Engine       │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Note Type       │  │ Content         │  │ Tag          │ │
│  │ Classifier      │  │ Structurer      │  │ Generator    │ │
│  │                 │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Notion API      │  │ Caching         │  │ Error        │ │
│  │ Client          │  │ System          │  │ Handler      │ │
│  │                 │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 **Core Implementation**

### **1. LLM Notes Enhancer**

```python
# src/personal_assistant/tools/notes/llm_notes_enhancer.py

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
            "content_analysis": """
You are a specialized note analysis AI. Analyze the following note content and provide a structured response.

Note Content: {content}
Note Title: {title}

Please analyze and provide:
1. Note Type: Choose from meeting, project, personal, research, learning, task, idea, journal, or unknown
2. Key Topics: List 3-5 main subjects or themes
3. Action Items: Extract any tasks, follow-ups, or action items mentioned
4. Important Details: List 3-5 critical pieces of information
5. Suggested Structure: How to better organize this content
6. Confidence Score: Rate your analysis confidence (0.0-1.0)

Format your response as JSON:
{{
    "note_type": "string",
    "key_topics": ["topic1", "topic2"],
    "action_items": ["action1", "action2"],
    "important_details": ["detail1", "detail2"],
    "structure_suggestions": ["suggestion1", "suggestion2"],
    "confidence_score": 0.85
}}
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
""",

            "content_enhancement": """
You are a note enhancement AI. Improve the following note content while preserving the original meaning and intent.

Note Type: {note_type}
Original Content: {content}
Structure Suggestions: {structure_suggestions}

Enhance the content by:
1. Adding proper structure and formatting
2. Highlighting key information
3. Organizing information logically
4. Improving readability
5. Adding relevant context

Return the enhanced content as plain text, maintaining the original meaning.
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

            # Step 1: Analyze content if type not provided
            if note_type is None:
                note_type = await self.detect_note_type(content, title)

            # Step 2: Get detailed content analysis
            analysis = await self._analyze_content(content, title)

            # Step 3: Generate smart tags
            tags = await self.generate_smart_tags(content, title, note_type, analysis.get('key_topics', []))

            # Step 4: Enhance content structure
            enhanced_content = await self._enhance_content_structure(
                content, note_type, analysis.get('structure_suggestions', [])
            )

            # Create enhanced note object
            enhanced_note = EnhancedNote(
                original_content=content,
                enhanced_content=enhanced_content,
                note_type=note_type,
                suggested_tags=tags,
                key_topics=analysis.get('key_topics', []),
                action_items=analysis.get('action_items', []),
                important_details=analysis.get('important_details', []),
                structure_suggestions=analysis.get('structure_suggestions', []),
                confidence_score=analysis.get('confidence_score', 0.0)
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

            # Parse JSON response
            import json
            tags = json.loads(response)

            # Validate and clean tags
            if isinstance(tags, list):
                return [tag.strip().lower() for tag in tags if tag.strip()]
            else:
                return []

        except Exception as e:
            self.logger.error(f"Error generating tags: {e}")
            return []

    async def _analyze_content(self, content: str, title: str = None) -> Dict:
        """Analyze content using LLM for detailed insights"""
        try:
            prompt = self.prompts["content_analysis"].format(
                content=content,
                title=title or "Untitled"
            )

            response = await self._get_llm_response(prompt)

            # Parse JSON response
            import json
            analysis = json.loads(response)

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing content: {e}")
            return {
                "key_topics": [],
                "action_items": [],
                "important_details": [],
                "structure_suggestions": [],
                "confidence_score": 0.0
            }

    async def _enhance_content_structure(
        self,
        content: str,
        note_type: NoteType,
        structure_suggestions: List[str]
    ) -> str:
        """Enhance content structure based on note type and suggestions"""
        try:
            prompt = self.prompts["content_enhancement"].format(
                note_type=note_type.value,
                content=content,
                structure_suggestions=", ".join(structure_suggestions) if structure_suggestions else "none"
            )

            enhanced_content = await self._get_llm_response(prompt)
            return enhanced_content

        except Exception as e:
            self.logger.error(f"Error enhancing content structure: {e}")
            return content  # Return original content on error

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
```

### **2. Enhanced Notes Tool**

```python
# src/personal_assistant/tools/notes/enhanced_notes_tool.py

import logging
from typing import Optional, Union, List, Dict, Any
from datetime import datetime

from .llm_notes_enhancer import LLMNotesEnhancer, NoteType, EnhancedNote
from .semantic_search import SemanticSearchEngine
from .content_processor import ContentProcessor
from ..base import Tool
from ...llm.llm_client import get_llm_client
from ...config.logging_config import get_logger

logger = get_logger("enhanced_notes_tool")


class EnhancedNotesTool:
    """Enhanced notes tool with specialized LLM integration"""

    def __init__(self):
        self.logger = logger

        # Initialize components
        self.llm_enhancer = LLMNotesEnhancer(get_llm_client())
        self.semantic_search = SemanticSearchEngine()
        self.content_processor = ContentProcessor()

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
            description="Create a new note with AI-powered content enhancement, automatic tagging, and intelligent structuring",
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
                    "description": "Type of note: meeting, project, personal, research, learning, task, idea, journal (optional)"
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
            description="Search notes using semantic understanding and intelligent filtering",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query - can be natural language (required)"
                },
                "note_type": {
                    "type": "string",
                    "description": "Filter by note type (optional)"
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
            description="Enhance an existing note with AI-powered improvements",
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
            description="Get AI-powered insights and suggestions for a note",
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

            main_page_id = await ensure_main_page_exists(self.notion_client)
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

            # Index for semantic search
            if enhance_content and 'enhanced_note' in locals():
                await self.semantic_search.index_note(
                    note_page["id"],
                    final_content,
                    final_title,
                    final_tags,
                    final_note_type
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

            # Use semantic search engine
            results = await self.semantic_search.search(
                query=query,
                note_type=note_type,
                tags=tags.split(",") if tags else None,
                limit=limit
            )

            if not results:
                return f"No notes found matching query: {query}"

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append(
                    f"• {result['title']} (ID: {result['page_id']})\n"
                    f"  Type: {result['note_type']} | "
                    f"Relevance: {result['relevance_score']:.2f}\n"
                    f"  Tags: {', '.join(result['tags'])}\n"
                    f"  Preview: {result['preview'][:100]}..."
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
```

### **3. Semantic Search Engine**

```python
# src/personal_assistant/tools/notes/semantic_search.py

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json

from ...llm.llm_client import get_llm_client
from ...config.logging_config import get_logger

logger = get_logger("semantic_search")


@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    page_id: str
    title: str
    content: str
    note_type: str
    tags: List[str]
    relevance_score: float
    preview: str


class SemanticSearchEngine:
    """Semantic search engine for notes using LLM understanding"""

    def __init__(self):
        self.logger = logger
        self.llm_client = get_llm_client()
        self.search_index = {}  # In-memory index (replace with proper storage)

        # Initialize search prompts
        self._init_search_prompts()

    def _init_search_prompts(self):
        """Initialize search-specific prompts"""
        self.prompts = {
            "semantic_search": """
You are a semantic search AI for notes. Find notes that are semantically related to the query, even if they don't contain exact keywords.

Query: {query}
Available Notes: {notes_data}

For each note, calculate a relevance score (0.0-1.0) based on:
1. Semantic similarity to the query
2. Note type relevance
3. Tag relevance
4. Content relevance

Return results as JSON array sorted by relevance score (highest first):
[
    {{
        "page_id": "page_id",
        "relevance_score": 0.85,
        "reasoning": "Brief explanation of why this note is relevant"
    }}
]
""",

            "query_expansion": """
You are a query expansion AI. Expand the search query to include related terms and concepts.

Original Query: {query}
Note Type Filter: {note_type}

Generate expanded search terms that would help find relevant notes:
1. Synonyms and related terms
2. Broader concepts
3. Specific examples
4. Related topics

Return as JSON array:
["term1", "term2", "term3"]
"""
        }

    async def index_note(
        self,
        page_id: str,
        content: str,
        title: str,
        tags: List[str],
        note_type: str
    ):
        """Index a note for semantic search"""
        try:
            self.search_index[page_id] = {
                "title": title,
                "content": content,
                "tags": tags,
                "note_type": note_type,
                "indexed_at": "now"  # Replace with actual timestamp
            }
            self.logger.info(f"Indexed note: {page_id}")
        except Exception as e:
            self.logger.error(f"Error indexing note {page_id}: {e}")

    async def search(
        self,
        query: str,
        note_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Perform semantic search across indexed notes"""
        try:
            self.logger.info(f"Performing semantic search: {query}")

            # Filter notes by type and tags
            filtered_notes = self._filter_notes(note_type, tags)

            if not filtered_notes:
                return []

            # Expand query for better results
            expanded_terms = await self._expand_query(query, note_type)

            # Perform semantic search
            search_results = await self._perform_semantic_search(query, filtered_notes, expanded_terms)

            # Format results
            formatted_results = []
            for result in search_results[:limit]:
                note_data = self.search_index[result["page_id"]]
                formatted_results.append({
                    "page_id": result["page_id"],
                    "title": note_data["title"],
                    "note_type": note_data["note_type"],
                    "tags": note_data["tags"],
                    "relevance_score": result["relevance_score"],
                    "preview": note_data["content"][:200] + "...",
                    "reasoning": result.get("reasoning", "")
                })

            return formatted_results

        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []

    def _filter_notes(
        self,
        note_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """Filter notes by type and tags"""
        filtered = {}

        for page_id, note_data in self.search_index.items():
            # Filter by note type
            if note_type and note_data["note_type"] != note_type:
                continue

            # Filter by tags
            if tags:
                note_tags = [tag.lower() for tag in note_data["tags"]]
                if not any(tag.lower() in note_tags for tag in tags):
                    continue

            filtered[page_id] = note_data

        return filtered

    async def _expand_query(self, query: str, note_type: Optional[str] = None) -> List[str]:
        """Expand search query with related terms"""
        try:
            prompt = self.prompts["query_expansion"].format(
                query=query,
                note_type=note_type or "any"
            )

            response = await self._get_llm_response(prompt)
            expanded_terms = json.loads(response)

            return expanded_terms if isinstance(expanded_terms, list) else []

        except Exception as e:
            self.logger.error(f"Error expanding query: {e}")
            return [query]  # Fallback to original query

    async def _perform_semantic_search(
        self,
        query: str,
        notes: Dict[str, Dict],
        expanded_terms: List[str]
    ) -> List[Dict[str, Any]]:
        """Perform the actual semantic search using LLM"""
        try:
            # Prepare notes data for LLM
            notes_data = []
            for page_id, note_data in notes.items():
                notes_data.append({
                    "page_id": page_id,
                    "title": note_data["title"],
                    "content": note_data["content"][:500],  # Truncate for LLM
                    "tags": note_data["tags"],
                    "note_type": note_data["note_type"]
                })

            prompt = self.prompts["semantic_search"].format(
                query=query,
                notes_data=json.dumps(notes_data, indent=2)
            )

            response = await self._get_llm_response(prompt)
            results = json.loads(response)

            return results if isinstance(results, list) else []

        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []

    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM"""
        try:
            response = self.llm_client.complete(prompt, functions={})

            if isinstance(response, dict):
                return response.get("content", "")
            else:
                return str(response)

        except Exception as e:
            self.logger.error(f"LLM response error: {e}")
            raise
```

## 🔧 **Integration Points**

### **1. Tool Registry Integration**

```python
# src/personal_assistant/tools/__init__.py

# Add to create_tool_registry function
def create_tool_registry() -> ToolRegistry:
    """Creates and configures a ToolRegistry with all available tools."""
    registry = ToolRegistry()

    # ... existing tools ...

    # Register enhanced notes tools
    from .notes.enhanced_notes_tool import EnhancedNotesTool
    enhanced_notes_tool = EnhancedNotesTool()
    for tool in enhanced_notes_tool:
        tool.set_category("EnhancedNotes")
        registry.register(tool)

    return registry
```

### **2. LLM Client Integration**

```python
# src/personal_assistant/llm/llm_client.py

# Add helper function for notes tool
def get_llm_client() -> LLMClient:
    """Get configured LLM client for notes enhancement"""
    from .gemini import GeminiLLM
    return GeminiLLM()
```

## 🧪 **Testing Strategy**

### **1. Unit Tests**

```python
# tests/unit/test_notes/test_llm_notes_enhancer.py

import pytest
from unittest.mock import Mock, AsyncMock
from src.personal_assistant.tools.notes.llm_notes_enhancer import LLMNotesEnhancer, NoteType

@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.complete = AsyncMock()
    return client

@pytest.fixture
def enhancer(mock_llm_client):
    return LLMNotesEnhancer(mock_llm_client)

@pytest.mark.asyncio
async def test_detect_note_type_meeting(enhancer, mock_llm_client):
    """Test meeting note type detection"""
    mock_llm_client.complete.return_value = {"content": "meeting"}

    result = await enhancer.detect_note_type(
        "Team meeting about Q1 goals. Discussed progress and next steps.",
        "Q1 Team Meeting"
    )

    assert result == NoteType.MEETING

@pytest.mark.asyncio
async def test_generate_smart_tags(enhancer, mock_llm_client):
    """Test smart tag generation"""
    mock_llm_client.complete.return_value = {
        "content": '["meeting", "Q1", "goals", "team", "planning"]'
    }

    result = await enhancer.generate_smart_tags(
        "Team meeting about Q1 goals",
        "Q1 Team Meeting",
        NoteType.MEETING,
        ["goals", "planning"]
    )

    assert result == ["meeting", "Q1", "goals", "team", "planning"]
```

### **2. Integration Tests**

```python
# tests/integration/test_enhanced_notes_tool.py

import pytest
from src.personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool

@pytest.mark.asyncio
async def test_create_enhanced_note():
    """Test creating an enhanced note"""
    tool = EnhancedNotesTool()

    result = await tool.create_enhanced_note(
        content="Team meeting about Q1 goals. Discussed progress and next steps.",
        title="Q1 Team Meeting",
        enhance_content=True,
        auto_tags=True
    )

    assert "Successfully created enhanced note" in result
    assert "Enhancement Summary" in result
```

## 📊 **Performance Considerations**

### **1. Caching Strategy**

- Cache LLM responses for similar content
- Cache note type classifications
- Cache tag generation results

### **2. Async Processing**

- All LLM calls are async
- Parallel processing where possible
- Non-blocking note creation

### **3. Error Handling**

- Graceful fallbacks for LLM failures
- Retry logic for transient errors
- User-friendly error messages

---

**Technical Implementation Complete**: Ready for development and testing  
**Last Updated**: December 2024  
**Next Review**: After Phase 1 implementation
