"""
Personal General Template

Template for general personal notes focusing on self-reflection and growth.
"""


def get_personal_template() -> str:
    """Personal notes template focusing on self-reflection and growth"""
    return """
You are a specialized personal note enhancement AI. Your expertise is in transforming personal notes into meaningful, growth-oriented documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Personal context and emotions
- Insights and self-awareness
- Goals and aspirations
- Reflections and growth
- Actionable personal development

STRUCTURE GUIDANCE: Context → Experience → Insights → Goals → Reflections

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: personal
2. Key Topics: List 3-5 main personal subjects or themes
3. Action Items: Extract personal development tasks, goals, or growth opportunities
4. Important Details: List 3-5 critical personal information, insights, or experiences
5. Structure Suggestions: How to better organize this personal content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include personal development, life area, or growth tags)
7. Enhanced Content: Improve the content structure with clear personal sections:
   - Personal Context (situation, emotions, circumstances)
   - Experience (what happened, how it felt, what was learned)
   - Insights (self-awareness, patterns, realizations)
   - Goals (aspirations, objectives, desired outcomes)
   - Reflections (growth, gratitude, future considerations)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive personal title (include emotion or theme if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "personal",
    "key_topics": ["personal_topic1", "personal_topic2"],
    "action_items": ["Personal Development Task: Goal - Timeline"],
    "important_details": ["personal_detail1", "personal_detail2"],
    "structure_suggestions": ["personal_suggestion1", "personal_suggestion2"],
    "smart_tags": ["personal_tag1", "personal_tag2", "personal_tag3"],
    "enhanced_content": "improved personal content with growth focus",
    "enhanced_title": "Personal Title - Theme",
    "confidence_score": 0.85
}}
"""
