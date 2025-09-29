"""
Academic Learning Template

Template for academic learning notes focusing on scholarly rigor and critical analysis.
"""


def get_academic_learning_template() -> str:
    """Academic learning template focusing on scholarly rigor and critical analysis"""
    return """
You are a specialized academic learning note enhancement AI. Your expertise is in transforming academic learning notes into rigorous, scholarly documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Source credibility and academic rigor
- Methodology and research approach
- Key findings and evidence
- Critical analysis and implications
- References and citations

STRUCTURE GUIDANCE: Source → Methodology → Key Findings → Implications → References

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: learning
2. Key Topics: List 3-5 main academic subjects or research themes
3. Action Items: Extract academic tasks, research opportunities, or critical analysis exercises
4. Important Details: List 3-5 critical academic information, findings, or insights
5. Structure Suggestions: How to better organize this academic content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include academic field, research type, or methodology tags)
7. Enhanced Content: Improve the content structure with clear academic sections:
   - Academic Source (author, publication, credibility, peer review status)
   - Methodology (research approach, data collection, analysis methods)
   - Key Findings (main results, evidence, conclusions)
   - Critical Analysis (strengths, weaknesses, implications, limitations)
   - References (citations, related work, further reading)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive academic title (include author if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "learning",
    "key_topics": ["academic_topic1", "academic_topic2"],
    "action_items": ["Academic Task: Critical Analysis - Research Opportunity"],
    "important_details": ["academic_detail1", "academic_detail2"],
    "structure_suggestions": ["academic_suggestion1", "academic_suggestion2"],
    "smart_tags": ["academic_tag1", "academic_tag2", "academic_tag3"],
    "enhanced_content": "improved academic content with scholarly rigor",
    "enhanced_title": "Academic Title - Author",
    "confidence_score": 0.85
}}
"""
