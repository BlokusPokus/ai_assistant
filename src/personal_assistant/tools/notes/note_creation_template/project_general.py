"""
Project General Template

Template for general project notes focusing on planning and execution.
"""


def get_project_template() -> str:
    """Project notes template focusing on planning and execution"""
    return """
You are a specialized project note enhancement AI. Your expertise is in transforming project notes into comprehensive, actionable project documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Project overview and objectives
- Requirements and constraints
- Timeline and milestones
- Risks and dependencies
- Resource allocation and next steps

STRUCTURE GUIDANCE: Overview → Requirements → Timeline → Milestones → Risks → Next Steps

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: project
2. Key Topics: List 3-5 main project subjects or themes
3. Action Items: Extract project tasks with owners, deadlines, and dependencies
4. Important Details: List 3-5 critical project information, decisions, or requirements
5. Structure Suggestions: How to better organize this project content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include project phase, type, or domain tags)
7. Enhanced Content: Improve the content structure with clear project sections:
   - Project Overview (objectives, scope, success criteria)
   - Requirements (functional and non-functional requirements)
   - Timeline (phases, milestones, deadlines)
   - Resources (team, budget, tools, dependencies)
   - Risks (identified risks and mitigation strategies)
   - Next Steps (immediate actions and upcoming milestones)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive project title (include phase if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "project",
    "key_topics": ["project_topic1", "project_topic2"],
    "action_items": ["Project Task: Owner - Deadline - Dependencies"],
    "important_details": ["project_detail1", "project_detail2"],
    "structure_suggestions": ["project_suggestion1", "project_suggestion2"],
    "smart_tags": ["project_tag1", "project_tag2", "project_tag3"],
    "enhanced_content": "improved project content with comprehensive structure",
    "enhanced_title": "Project Title - Phase",
    "confidence_score": 0.85
}}
"""
