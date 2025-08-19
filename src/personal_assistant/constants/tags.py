"""
LTM (Long-Term Memory) tag definitions for consistent categorization.

This module provides a centralized list of tags that the LLM must choose from
when categorizing LTM entries. This ensures consistency and prevents tag proliferation.
"""

# Core LTM Tags - These are the primary tags the LLM must choose from
LTM_TAGS = [
    # Communication & Information
    "email",
    "meeting",
    "conversation",
    "document",
    "note",

    # Actions & Operations
    "create",
    "delete",
    "update",
    "search",
    "schedule",
    "remind",

    # Importance & Priority
    "important",
    "urgent",
    "critical",
    "low_priority",

    # Context & Categories
    "work",
    "personal",
    "health",
    "finance",
    "travel",
    "shopping",
    "entertainment",
    "education",

    # User Behavior & Preferences
    "preference",
    "habit",
    "pattern",
    "routine",
    "dislike",
    "favorite",

    # Tool & System Usage
    "tool_execution",
    "user_request",
    "system_response",
    "error",
    "success",

    # Time & Frequency
    "daily",
    "weekly",
    "monthly",
    "one_time",
    "recurring",

    # General
    "general",
    "miscellaneous",
    "other",

    # Project Management
    "project",
    "task",
    "deadline",
    "milestone",

    # Health & Wellness
    "exercise",
    "diet",
    "medication",
    "wellness",

    # Social
    "friend",
    "family",
    "event",
    "birthday",

    # Shopping
    "wishlist",
    "purchase",
    "order",
    "delivery",

    # Learning
    "course",
    "lesson",
    "reading",
    "research",

    # Finance
    "budget",
    "expense",
    "income",
    "investment",

    # Travel
    "flight",
    "hotel",
    "reservation",
    "itinerary",

    # Reminders
    "follow_up",
    "due",
    "overdue"
]

# Tag Categories for better organization
TAG_CATEGORIES = {
    "communication": ["email", "meeting", "conversation", "document", "note"],
    "actions": ["create", "delete", "update", "search", "schedule", "remind"],
    "priority": ["important", "urgent", "critical", "low_priority"],
    "context": ["work", "personal", "health", "finance", "travel", "shopping", "entertainment", "education"],
    "behavior": ["preference", "habit", "pattern", "routine", "dislike", "favorite"],
    "system": ["tool_execution", "user_request", "system_response", "error", "success"],
    "time": ["daily", "weekly", "monthly", "one_time", "recurring"],
    "general": ["general", "miscellaneous", "other"],
    "project_management": ["project", "task", "deadline", "milestone"],
    "health": ["exercise", "diet", "medication", "wellness"],
    "social": ["friend", "family", "event", "birthday"],
    "shopping": ["wishlist", "purchase", "order", "delivery"],
    "learning": ["course", "lesson", "reading", "research"],
    "finance": ["budget", "expense", "income", "investment"],
    "travel": ["flight", "hotel", "reservation", "itinerary"],
    "reminders": ["follow_up", "due", "overdue"]
}

# Validation function to ensure tags are from the allowed list


def validate_tags(tags: list) -> tuple[list, list]:
    """
    Validate that all tags are from the allowed LTM_TAGS list.

    Args:
        tags: List of tags to validate

    Returns:
        Tuple of (valid_tags, invalid_tags)
    """
    if not tags:
        return [], []

    valid_tags = []
    invalid_tags = []

    for tag in tags:
        if tag in LTM_TAGS:
            valid_tags.append(tag)
        else:
            invalid_tags.append(tag)

    return valid_tags, invalid_tags


def get_tag_suggestions(content: str) -> list:
    """
    Get suggested tags based on content analysis.
    This is a simple keyword-based suggestion system.

    Args:
        content: The content to analyze for tag suggestions

    Returns:
        List of suggested tags
    """
    content_lower = content.lower()
    suggestions = []

    # Simple keyword matching
    if any(word in content_lower for word in ["email", "mail", "gmail"]):
        suggestions.append("email")
    if any(word in content_lower for word in ["meeting", "appointment", "call"]):
        suggestions.append("meeting")
    if any(word in content_lower for word in ["delete", "remove", "trash"]):
        suggestions.append("delete")
    if any(word in content_lower for word in ["important", "urgent", "critical"]):
        suggestions.append("important")
    if any(word in content_lower for word in ["work", "job", "office"]):
        suggestions.append("work")
    if any(word in content_lower for word in ["personal", "private", "family"]):
        suggestions.append("personal")
    if any(word in content_lower for word in ["preference", "like", "dislike", "favorite"]):
        suggestions.append("preference")
    if any(word in content_lower for word in ["project", "task", "milestone"]):
        suggestions.append("project")
    if any(word in content_lower for word in ["deadline", "due", "overdue"]):
        suggestions.append("deadline")
    if any(word in content_lower for word in ["exercise", "workout", "fitness"]):
        suggestions.append("exercise")
    if any(word in content_lower for word in ["diet", "nutrition", "food"]):
        suggestions.append("diet")
    if any(word in content_lower for word in ["medication", "medicine", "pill"]):
        suggestions.append("medication")
    if any(word in content_lower for word in ["wellness", "health"]):
        suggestions.append("wellness")
    if any(word in content_lower for word in ["friend", "family", "birthday"]):
        suggestions.append("friend")
    if any(word in content_lower for word in ["event", "party", "gathering"]):
        suggestions.append("event")
    if any(word in content_lower for word in ["wishlist", "purchase", "order", "delivery"]):
        suggestions.append("shopping")
    if any(word in content_lower for word in ["course", "lesson", "reading", "research"]):
        suggestions.append("learning")
    if any(word in content_lower for word in ["budget", "expense", "income", "investment"]):
        suggestions.append("finance")
    if any(word in content_lower for word in ["flight", "hotel", "reservation", "itinerary"]):
        suggestions.append("travel")
    if any(word in content_lower for word in ["follow up", "remind", "due", "overdue"]):
        suggestions.append("reminders")

    # Always add general if no specific tags found
    if not suggestions:
        suggestions.append("general")

    return suggestions
