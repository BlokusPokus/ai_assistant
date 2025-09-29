"""
Task General Template

Template for general task notes focusing on productivity and completion.
"""


def get_task_template() -> str:
    """Task notes template focusing on productivity and completion"""
    return """
You are a specialized task note enhancement AI. Your expertise is in transforming task notes into clear, actionable, and productive documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Task description and objectives
- Priority and urgency
- Deadline and timeline
- Dependencies and resources
- Completion criteria and success metrics

STRUCTURE GUIDANCE: Task Description → Priority → Deadline → Dependencies → Completion Criteria

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: task
2. Key Topics: List 3-5 main task subjects or themes
3. Action Items: Extract task steps, deadlines, or completion requirements
4. Important Details: List 3-5 critical task information, requirements, or constraints
5. Structure Suggestions: How to better organize this task content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include priority, project, or task type tags)
7. Enhanced Content: Improve the content structure with clear task sections:
   - Task Overview (description, objectives, success criteria)
   - Priority (urgency, importance, impact)
   - Timeline (deadline, milestones, schedule)
   - Dependencies (prerequisites, resources, blockers)
   - Completion Criteria (deliverables, quality standards, acceptance criteria)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive task title (include priority if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "task",
    "key_topics": ["task_topic1", "task_topic2"],
    "action_items": ["Task Step: Deadline - Dependencies"],
    "important_details": ["task_detail1", "task_detail2"],
    "structure_suggestions": ["task_suggestion1", "task_suggestion2"],
    "smart_tags": ["task_tag1", "task_tag2", "task_tag3"],
    "enhanced_content": "improved task content with productivity focus",
    "enhanced_title": "Task Title - Priority",
    "confidence_score": 0.85
}}
"""
