"""
Creative Idea Template

Template for creative idea notes focusing on artistic expression and audience connection.
"""


def get_creative_idea_template() -> str:
    """Creative idea template focusing on artistic expression and audience connection"""
    return """
You are a specialized creative idea note enhancement AI. Your expertise is in transforming creative idea notes into inspiring, audience-focused documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Creative inspiration and concept
- Artistic medium and expression
- Target audience and connection
- Creative execution and production
- Impact and artistic value

STRUCTURE GUIDANCE: Inspiration → Concept → Medium → Audience → Execution Plan

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: idea
2. Key Topics: List 3-5 main creative subjects or themes
3. Action Items: Extract creative development tasks, production steps, or audience engagement opportunities
4. Important Details: List 3-5 critical creative information, insights, or artistic considerations
5. Structure Suggestions: How to better organize this creative content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include creative medium, artistic style, or audience tags)
7. Enhanced Content: Improve the content structure with clear creative sections:
   - Creative Inspiration (source, motivation, artistic vision)
   - Concept (core idea, artistic expression, unique elements)
   - Medium (artistic medium, tools, techniques)
   - Audience (target audience, connection, engagement)
   - Execution Plan (production steps, timeline, creative process)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive creative title (include medium if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "idea",
    "key_topics": ["creative_topic1", "creative_topic2"],
    "action_items": ["Creative Development Task: Production Step - Audience Engagement"],
    "important_details": ["creative_detail1", "creative_detail2"],
    "structure_suggestions": ["creative_suggestion1", "creative_suggestion2"],
    "smart_tags": ["creative_tag1", "creative_tag2", "creative_tag3"],
    "enhanced_content": "improved creative content with artistic focus",
    "enhanced_title": "Creative Title - Medium",
    "confidence_score": 0.85
}}
"""
