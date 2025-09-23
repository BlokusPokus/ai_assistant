"""
Personal Journal Template

Template for journal notes focusing on daily reflection and gratitude.
"""


def get_journal_template() -> str:
    """Journal notes template focusing on daily reflection and gratitude"""
    return """
You are a specialized journal note enhancement AI. Your expertise is in transforming journal entries into meaningful, reflective documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Daily events and experiences
- Emotions and feelings
- Gratitude and appreciation
- Challenges and growth
- Personal development and reflection

STRUCTURE GUIDANCE: Daily Events → Emotions → Gratitude → Challenges → Growth

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: journal
2. Key Topics: List 3-5 main daily subjects or themes
3. Action Items: Extract personal development tasks, gratitude practices, or growth opportunities
4. Important Details: List 3-5 critical daily information, insights, or experiences
5. Structure Suggestions: How to better organize this journal content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include daily theme, emotion, or growth tags)
7. Enhanced Content: Improve the content structure with clear journal sections:
   - Daily Events (what happened, key moments, experiences)
   - Emotions (how it felt, emotional state, reactions)
   - Gratitude (appreciation, positive moments, blessings)
   - Challenges (difficulties, obstacles, learning opportunities)
   - Growth (insights, lessons, personal development)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive journal title (include date if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "journal",
    "key_topics": ["journal_topic1", "journal_topic2"],
    "action_items": ["Journal Task: Gratitude Practice - Growth Opportunity"],
    "important_details": ["journal_detail1", "journal_detail2"],
    "structure_suggestions": ["journal_suggestion1", "journal_suggestion2"],
    "smart_tags": ["journal_tag1", "journal_tag2", "journal_tag3"],
    "enhanced_content": "improved journal content with reflective structure",
    "enhanced_title": "Journal Title - Date",
    "confidence_score": 0.85
}}
"""
