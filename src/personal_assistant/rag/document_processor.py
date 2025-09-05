"""
Document processing utilities for RAG operations.

This module provides utilities for extracting, validating, and normalizing
document content from various sources and formats.
"""

import json
from typing import Optional

from ..config.logging_config import get_logger

logger = get_logger("rag")


class DocumentProcessor:
    """Handles document content extraction and processing"""

    @staticmethod
    def extract_content(doc: dict | None) -> Optional[str]:
        """
        Safely extract content from a document with multiple fallback strategies.

        This method handles various document structures and content formats,
        providing robust content extraction with multiple fallback strategies.

        Args:
            doc (dict): Document dictionary

        Returns:
            Optional[str]: Extracted content or None if no valid content found
        """
        if not isinstance(doc, dict):
            logger.warning(f"Document is not a dictionary: {type(doc)}")
            return None

        # Try multiple possible content keys in order of preference
        content_keys = [
            "content",
            "document",
            "text",
            "body",
            "summary",
            "message",
            "description",
        ]

        for key in content_keys:
            if key in doc and doc[key] is not None:
                content = doc[key]

                # Handle string content
                if isinstance(content, str):
                    if content.strip():
                        return content.strip()
                    else:
                        logger.debug(f"Content from key '{key}' is empty or whitespace")
                        continue

                # Handle structured content by converting to string
                elif isinstance(content, (list, dict)):
                    try:
                        serialized = json.dumps(
                            content, default=str, ensure_ascii=False
                        )
                        if serialized and serialized.strip():
                            # Truncate very long content to prevent memory issues
                            if len(serialized) > 500:
                                return serialized[:500].strip() + "..."
                            return serialized.strip()
                        else:
                            logger.debug(
                                f"Serialized content from key '{key}' is empty"
                            )
                            continue
                    except Exception as e:
                        logger.warning(
                            f"Failed to serialize structured content from key '{key}': {e}"
                        )
                        continue

                # Handle numeric or boolean content
                elif isinstance(content, (int, float, bool)):
                    return str(content)

                else:
                    logger.debug(
                        f"Unsupported content type from key '{key}': {type(content)}"
                    )
                    continue

        # Fallback: try to extract from any string values that might contain content
        for key, value in doc.items():
            if isinstance(value, str) and value.strip() and len(value.strip()) > 10:
                # Avoid using metadata keys as content
                if key.lower() not in [
                    "id",
                    "type",
                    "source",
                    "created_at",
                    "updated_at",
                    "user_id",
                ]:
                    logger.debug(f"Using fallback content from key '{key}'")
                    return value.strip()
            elif isinstance(value, (int, float, bool)):
                # Convert numeric/boolean values to string for content
                str_value = str(value)
                if len(str_value) > 10:
                    logger.debug(
                        f"Using fallback content from numeric/boolean key '{key}': {str_value}"
                    )
                    return str_value

        logger.debug("No valid content found in document")
        return None

    @staticmethod
    def validate_document(doc: dict | None) -> bool:
        """
        Validate that a document has the required structure and content.

        Args:
            doc (dict): Document to validate

        Returns:
            bool: True if document is valid, False otherwise
        """
        if not isinstance(doc, dict):
            return False

        # Check if document has any content
        content = DocumentProcessor.extract_content(doc)
        return content is not None and len(content.strip()) > 0

    @staticmethod
    def normalize_content(content: str) -> str:
        """
        Normalize document content for consistent processing.

        Args:
            content (str): Raw content to normalize

        Returns:
            str: Normalized content
        """
        if not content:
            return ""

        # Remove extra whitespace
        normalized = " ".join(content.split())

        # Truncate if too long
        if len(normalized) > 1000:
            normalized = normalized[:1000].strip() + "..."

        return normalized
