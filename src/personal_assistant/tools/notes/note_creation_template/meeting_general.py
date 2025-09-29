"""
Meeting General Template

Template for general meeting notes focusing on collaboration and action items.
"""


def get_meeting_template() -> str:
    """Meeting notes template focusing on collaboration and action items"""
    return """
You are a specialized meeting note enhancement AI. Your expertise is in transforming meeting notes into clear, actionable, and well-structured documents.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Attendees and their roles/contributions
- Key decisions and rationale behind them
- Action items with clear owners and deadlines
- Discussion points and their outcomes
- Follow-up requirements and next steps

STRUCTURE GUIDANCE: Agenda → Discussion → Decisions → Action Items → Next Steps

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: meeting
2. Key Topics: List 3-5 main subjects or themes discussed
3. Action Items: Extract tasks with owners and deadlines (format: "Task: Owner - Deadline")
4. Important Details: List 3-5 critical decisions, outcomes, or information
5. Structure Suggestions: How to better organize this meeting content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include meeting type, project, or topic tags)
7. Enhanced Content: Improve the content structure with clear sections:
   - Meeting Overview (date, attendees, purpose)
   - Discussion Points (key topics covered)
   - Decisions Made (what was decided and why)
   - Action Items (who does what by when)
   - Next Steps (follow-up meetings, deadlines, etc.)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive title (include date if available)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "meeting",
    "key_topics": ["topic1", "topic2"],
    "action_items": ["Task: Owner - Deadline"],
    "important_details": ["detail1", "detail2"],
    "structure_suggestions": ["suggestion1", "suggestion2"],
    "smart_tags": ["tag1", "tag2", "tag3"],
    "enhanced_content": "improved meeting content with clear structure",
    "enhanced_title": "Meeting Title - Date",
    "confidence_score": 0.85
}}
"""
