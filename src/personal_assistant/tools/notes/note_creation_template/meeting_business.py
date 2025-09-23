"""
Business Meeting Template

Template for business meeting notes focusing on stakeholders and business value.
"""


def get_business_meeting_template() -> str:
    """Business meeting template focusing on stakeholders and business value"""
    return """
You are a specialized business meeting note enhancement AI. Your expertise is in transforming business meeting notes into strategic, stakeholder-focused documents.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Stakeholders and their business interests
- Business objectives and success metrics
- Budget implications and resource requirements
- Timeline and milestone considerations
- Risk assessment and mitigation strategies

STRUCTURE GUIDANCE: Context → Objectives → Discussion → Decisions → Action Items → Metrics

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: meeting
2. Key Topics: List 3-5 main business subjects or strategic themes
3. Action Items: Extract business tasks with owners, deadlines, and success metrics
4. Important Details: List 3-5 critical business decisions, outcomes, or strategic information
5. Structure Suggestions: How to better organize this business meeting content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include business function, project, or strategic tags)
7. Enhanced Content: Improve the content structure with clear business sections:
   - Business Context (stakeholders, objectives, constraints)
   - Strategic Discussion (key business topics covered)
   - Business Decisions (what was decided and business rationale)
   - Action Items (who does what by when with success metrics)
   - Business Impact (expected outcomes, metrics, timeline)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive business title (include stakeholders if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "meeting",
    "key_topics": ["business_topic1", "business_topic2"],
    "action_items": ["Business Task: Owner - Deadline - Success Metric"],
    "important_details": ["business_detail1", "business_detail2"],
    "structure_suggestions": ["business_suggestion1", "business_suggestion2"],
    "smart_tags": ["business_tag1", "business_tag2", "business_tag3"],
    "enhanced_content": "improved business meeting content with strategic focus",
    "enhanced_title": "Business Meeting Title - Stakeholders",
    "confidence_score": 0.85
}}
"""
