"""
Notion content extractor for RAG indexing.
Extracts and normalizes content from Notion notes for vector embedding.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..tools.notion_pages.notion_pages_tool import NotionPagesTool

logger = logging.getLogger(__name__)


class NotionContentExtractor:
    """
    Extract and normalize content from Notion notes for RAG indexing.
    """

    def __init__(self):
        """Initialize the content extractor."""
        self.notion_tool = NotionPagesTool()
        logger.info("NotionContentExtractor initialized")

    async def extract_note_content(
        self, note_id: str, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Extract full note content with metadata.

        Args:
            note_id: Notion note ID
            user_id: User ID for the note

        Returns:
            Dictionary containing structured note data or None if extraction fails
        """
        try:
            logger.debug(f"Extracting content for note {note_id} (user: {user_id})")

            # Get note using existing NotionNotesTool
            note_content = await self.notion_tool.get_note(note_id)

            if not note_content:
                logger.warning(f"No content returned for note {note_id}")
                return None

            # Parse and structure content
            structured_content = self._parse_note_content(note_content)

            if not structured_content:
                logger.warning(f"Failed to parse content for note {note_id}")
                return None

            # Add metadata
            structured_content.update(
                {
                    "id": note_id,
                    "user_id": user_id,
                    "source": "notion",
                    "extracted_at": datetime.utcnow().isoformat(),
                }
            )

            logger.info(f"Successfully extracted content for note {note_id}")
            return structured_content

        except Exception as e:
            logger.error(f"Error extracting note content for {note_id}: {e}")
            return None

    def _parse_note_content(self, note_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse note content into structured format.

        Args:
            note_content: Raw note content from Notion

        Returns:
            Structured content dictionary or None if parsing fails
        """
        try:
            if not note_content or not note_content.strip():
                return None

            # Split content into lines for analysis
            lines = [line.strip() for line in note_content.split("\n") if line.strip()]

            if not lines:
                return None

            # Extract title (first non-empty line)
            title = lines[0] if lines else "Untitled Note"

            # Extract main content (all lines after title)
            content_lines = lines[1:] if len(lines) > 1 else []
            main_content = "\n".join(content_lines)

            # Initialize structured content
            structured: dict[str, Any] = {
                "title": title,
                "text": note_content,  # Keep full text for embedding
                "summary": "",
                "tags": [],
                "category": "",
                "importance": "",
                "status": "",
                "created_at": None,
                "updated_at": None,
            }

            # Try to extract metadata from content structure
            self._extract_metadata_from_content(lines, structured)

            # Generate summary if not present
            if not structured["summary"] and main_content:
                structured["summary"] = self._generate_summary(main_content)

            return structured

        except Exception as e:
            logger.error(f"Error parsing note content: {e}")
            return None

    def _extract_metadata_from_content(
        self, lines: List[str], structured: Dict[str, Any]
    ):
        """
        Extract metadata from content structure.

        Args:
            lines: List of content lines
            structured: Structured content dictionary to update
        """
        try:
            for line in lines:
                line_lower = line.lower()

                # Extract tags (lines starting with #)
                if line.startswith("#"):
                    tag = line.strip("#").strip()
                    if tag and tag not in structured["tags"]:
                        structured["tags"].append(tag)

                # Extract importance indicators
                if any(
                    word in line_lower for word in ["important", "urgent", "critical"]
                ):
                    if "critical" in line_lower or "urgent" in line_lower:
                        structured["importance"] = "High"
                    elif "important" in line_lower:
                        structured["importance"] = "Medium"

                # Extract status indicators
                if any(
                    word in line_lower
                    for word in ["draft", "in progress", "complete", "done", "archived"]
                ):
                    if "draft" in line_lower:
                        structured["status"] = "Draft"
                    elif "in progress" in line_lower or "working" in line_lower:
                        structured["status"] = "In Progress"
                    elif "complete" in line_lower or "done" in line_lower:
                        structured["status"] = "Complete"
                    elif "archived" in line_lower:
                        structured["status"] = "Archived"

                # Extract category indicators
                if any(
                    word in line_lower
                    for word in ["work", "personal", "learning", "planning", "research"]
                ):
                    if "work" in line_lower:
                        structured["category"] = "Work"
                    elif "personal" in line_lower:
                        structured["category"] = "Personal"
                    elif "learning" in line_lower or "study" in line_lower:
                        structured["category"] = "Learning"
                    elif "planning" in line_lower or "plan" in line_lower:
                        structured["category"] = "Planning"
                    elif "research" in line_lower:
                        structured["category"] = "Research"

                # Extract dates (simple pattern matching)
                if self._looks_like_date(line):
                    if not structured["created_at"]:
                        structured["created_at"] = line
                    else:
                        structured["updated_at"] = line

        except Exception as e:
            logger.warning(f"Error extracting metadata from content: {e}")

    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """
        Generate a summary of the content.

        Args:
            content: Content to summarize
            max_length: Maximum summary length

        Returns:
            Generated summary
        """
        try:
            if not content:
                return ""

            # Simple summary: take first few sentences
            sentences = content.split(".")
            summary = ""

            for sentence in sentences:
                if len(summary + sentence) < max_length:
                    summary += sentence + "."
                else:
                    break

            # Clean up summary
            summary = summary.strip()
            if len(summary) > max_length:
                summary = summary[: max_length - 3] + "..."

            return summary

        except Exception as e:
            logger.warning(f"Error generating summary: {e}")
            return ""

    def _looks_like_date(self, text: str) -> bool:
        """
        Check if text looks like a date.

        Args:
            text: Text to check

        Returns:
            True if text appears to be a date
        """
        # Simple date pattern matching
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{1,2}/\d{1,2}/\d{2,4}",  # M/D/YY or M/D/YYYY
        ]

        import re

        for pattern in date_patterns:
            if re.search(pattern, text):
                return True

        # Check for month names
        months = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]

        text_lower = text.lower()
        if any(month in text_lower for month in months):
            return True

        return False

    async def extract_multiple_notes(
        self, note_ids: List[str], user_id: int
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract content from multiple notes.

        Args:
            note_ids: List of note IDs to extract
            user_id: User ID for the notes

        Returns:
            Dictionary mapping note IDs to structured content
        """
        results = {}

        for note_id in note_ids:
            content = await self.extract_note_content(note_id, user_id)
            if content:
                results[note_id] = content

        logger.info(
            f"Extracted content from {len(results)} out of {len(note_ids)} notes"
        )
        return results

    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about content extraction.

        Returns:
            Dictionary with extraction statistics
        """
        return {
            "extractor_type": "NotionContentExtractor",
            "notion_tool_available": self.notion_tool is not None,
        }
