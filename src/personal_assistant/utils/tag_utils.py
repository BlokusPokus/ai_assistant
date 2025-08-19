"""
Tag management utilities for LTM (Long-Term Memory) system.

This module provides utility functions for working with tags, including
validation, normalization, and tag-based queries.
"""

from typing import List, Dict, Set, Optional
from ..constants.tags import LTM_TAGS, validate_tags, get_tag_suggestions


def normalize_tag(tag: str) -> str:
    """
    Normalize a tag string for consistent storage and comparison.

    Args:
        tag: Raw tag string

    Returns:
        Normalized tag string
    """
    if not tag:
        return ""

    # Convert to lowercase and remove extra whitespace
    normalized = tag.lower().strip()

    # Replace spaces with underscores for consistency
    normalized = normalized.replace(" ", "_")

    # Remove special characters except underscores and hyphens
    import re
    normalized = re.sub(r'[^a-z0-9_-]', '', normalized)

    return normalized


def normalize_tags(tags: List[str]) -> List[str]:
    """
    Normalize a list of tags.

    Args:
        tags: List of raw tag strings

    Returns:
        List of normalized tag strings
    """
    if not tags:
        return []

    normalized = [normalize_tag(tag) for tag in tags]
    # Remove empty tags and duplicates while preserving order
    seen = set()
    result = []
    for tag in normalized:
        if tag and tag not in seen:
            result.append(tag)
            seen.add(tag)

    return result


def get_related_tags(tag: str, max_related: int = 5) -> List[str]:
    """
    Get tags that are semantically related to the given tag.

    Args:
        tag: The tag to find related tags for
        max_related: Maximum number of related tags to return

    Returns:
        List of related tags
    """
    from ..constants.tags import TAG_CATEGORIES

    normalized_tag = normalize_tag(tag)

    # Find which category the tag belongs to
    for category, category_tags in TAG_CATEGORIES.items():
        if normalized_tag in category_tags:
            # Return other tags from the same category
            related = [t for t in category_tags if t != normalized_tag]
            return related[:max_related]

    # If no category found, return some general tags
    return ["general", "miscellaneous"][:max_related]


def build_tag_query(tags: List[str], operator: str = "OR") -> Dict:
    """
    Build a database query filter for tags.

    Args:
        tags: List of tags to search for
        operator: "AND" or "OR" to determine how tags should be combined

    Returns:
        Dictionary with query parameters
    """
    if not tags:
        return {}

    normalized_tags = normalize_tags(tags)
    valid_tags, invalid_tags = validate_tags(normalized_tags)

    if not valid_tags:
        return {}

    return {
        "tags": valid_tags,
        "operator": operator.upper(),
        "invalid_tags": invalid_tags
    }


def suggest_tags_for_content(content: str, max_suggestions: int = 5) -> List[str]:
    """
    Suggest tags for content based on analysis.

    Args:
        content: The content to analyze
        max_suggestions: Maximum number of tag suggestions

    Returns:
        List of suggested tags
    """
    if not content:
        return ["general"]

    # Get basic suggestions
    suggestions = get_tag_suggestions(content)

    # Add content-based suggestions
    content_lower = content.lower()

    # Check for time-related content
    if any(word in content_lower for word in ["daily", "every day", "each day"]):
        suggestions.append("daily")
    elif any(word in content_lower for word in ["weekly", "every week"]):
        suggestions.append("weekly")
    elif any(word in content_lower for word in ["monthly", "every month"]):
        suggestions.append("monthly")

    # Check for action-related content
    if any(word in content_lower for word in ["create", "make", "add"]):
        suggestions.append("create")
    elif any(word in content_lower for word in ["delete", "remove", "trash"]):
        suggestions.append("delete")
    elif any(word in content_lower for word in ["update", "change", "modify"]):
        suggestions.append("update")

    # Check for priority indicators
    if any(word in content_lower for word in ["urgent", "asap", "immediately"]):
        suggestions.append("urgent")
    elif any(word in content_lower for word in ["critical", "essential", "vital"]):
        suggestions.append("critical")

    # Remove duplicates and limit results
    unique_suggestions = list(dict.fromkeys(suggestions))  # Preserve order
    return unique_suggestions[:max_suggestions]


def validate_and_suggest_tags(tags: List[str], content: str = "") -> Dict:
    """
    Validate tags and provide suggestions if needed.

    Args:
        tags: List of tags to validate
        content: Optional content for generating suggestions

    Returns:
        Dictionary with validation results and suggestions
    """
    if not tags:
        suggestions = suggest_tags_for_content(
            content) if content else ["general"]
        return {
            "valid_tags": [],
            "invalid_tags": [],
            "suggestions": suggestions,
            "needs_suggestions": True
        }

    normalized_tags = normalize_tags(tags)
    valid_tags, invalid_tags = validate_tags(normalized_tags)

    result = {
        "valid_tags": valid_tags,
        "invalid_tags": invalid_tags,
        "suggestions": [],
        "needs_suggestions": False
    }

    # If we have invalid tags, provide suggestions
    if invalid_tags and content:
        result["suggestions"] = suggest_tags_for_content(content)
        result["needs_suggestions"] = True

    return result


def get_tag_statistics(user_id: str) -> Dict:
    """
    Get statistics about tag usage for a user.

    Args:
        user_id: User ID to get statistics for

    Returns:
        Dictionary with tag usage statistics
    """
    # This would typically query the database
    # For now, return a placeholder structure
    return {
        "total_memories": 0,
        "tag_counts": {},
        "most_used_tags": [],
        "recent_tags": []
    }
