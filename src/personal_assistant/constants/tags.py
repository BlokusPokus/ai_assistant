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

    # Organization & Management
    "organization",
    "management",
    "productivity",
    "automation",
    "efficiency",
    "optimization",

    # Communication Styles
    "communication",
    "concise",
    "detailed",
    "professional",
    "casual",
    "formal",
    "informal",

    # Frequency & Patterns
    "frequent",
    "occasional",
    "rare",
    "consistent",
    "variable",

    # Work Styles
    "technical",
    "creative",
    "analytical",
    "strategic",
    "tactical",
    "operational",

    # Quality & Effectiveness
    "effective",
    "ineffective",
    "streamlined",
    "simplified",
    "complex",
    "straightforward",

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
    "organization": ["organization", "management", "productivity", "automation", "efficiency", "optimization"],
    "communication_style": ["communication", "concise", "detailed", "professional", "casual", "formal", "informal"],
    "frequency": ["frequent", "occasional", "rare", "consistent", "variable"],
    "work_style": ["technical", "creative", "analytical", "strategic", "tactical", "operational"],
    "quality": ["effective", "ineffective", "streamlined", "simplified", "complex", "straightforward"],
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


def validate_tags(tags: list, enable_smart_fallback: bool = True) -> tuple[list, list]:
    """
    Validate that all tags are from the allowed LTM_TAGS list.
    Optionally provides smart fallback suggestions for invalid tags.

    Args:
        tags: List of tags to validate
        enable_smart_fallback: If True, suggest similar valid tags for invalid ones

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
            if enable_smart_fallback:
                # Try to find a similar valid tag
                similar_tag = _find_similar_tag(tag)
                if similar_tag:
                    valid_tags.append(similar_tag)
                    continue
            invalid_tags.append(tag)

    return valid_tags, invalid_tags


def _find_similar_tag(invalid_tag: str) -> str:
    """
    Find a similar valid tag for an invalid tag using fuzzy matching.

    Args:
        invalid_tag: The invalid tag to find a replacement for

    Returns:
        A similar valid tag or None if no good match found
    """
    invalid_lower = invalid_tag.lower()

    # Direct mappings for common cases
    tag_mappings = {
        'organize': 'organization',
        'organizing': 'organization',
        'organised': 'organization',
        'manage': 'management',
        'managing': 'management',
        'productive': 'productivity',
        'automate': 'automation',
        'automating': 'automation',
        'efficient': 'efficiency',
        'optimize': 'optimization',
        'optimizing': 'optimization',
        'communicate': 'communication',
        'communicating': 'communication',
        'brief': 'concise',
        'short': 'concise',
        'detailed': 'detailed',
        'thorough': 'detailed',
        'pro': 'professional',
        'business': 'professional',
        'relaxed': 'casual',
        'informal': 'casual',
        'formal': 'formal',
        'official': 'formal',
        'tech': 'technical',
        'technology': 'technical',
        'innovative': 'creative',
        'artistic': 'creative',
        'logical': 'analytical',
        'systematic': 'analytical',
        'planning': 'strategic',
        'tactics': 'tactical',
        'operations': 'operational',
        'working': 'operational',
        'successful': 'effective',
        'useful': 'effective',
        'streamline': 'streamlined',
        'simplify': 'simplified',
        'easy': 'simplified',
        'complicated': 'complex',
        'difficult': 'complex',
        'simple': 'straightforward',
        'clear': 'straightforward',
        'often': 'frequent',
        'regularly': 'frequent',
        'sometimes': 'occasional',
        'rarely': 'rare',
        'consistent': 'consistent',
        'steady': 'consistent',
        'changing': 'variable',
        'inconsistent': 'variable'
    }

    # Check direct mappings first
    if invalid_lower in tag_mappings:
        return tag_mappings[invalid_lower]

    # Check if the invalid tag is a substring of any valid tag
    for valid_tag in LTM_TAGS:
        if invalid_lower in valid_tag.lower() or valid_tag.lower() in invalid_lower:
            return valid_tag

    # Check for partial matches (at least 3 characters)
    if len(invalid_lower) >= 3:
        for valid_tag in LTM_TAGS:
            if len(valid_tag) >= 3:
                # Check if they share at least 3 consecutive characters
                for i in range(len(invalid_lower) - 2):
                    substring = invalid_lower[i:i+3]
                    if substring in valid_tag.lower():
                        return valid_tag

    return None


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
