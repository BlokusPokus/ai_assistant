"""
Simple Note Templates for Type-Specific Enhancement

This module provides specialized prompt templates for each note type,
enabling targeted enhancement based on the specific requirements of each category.
"""

from .note_types import NoteType


class NoteTemplates:
    """Simple template system for note type-specific enhancement"""
    
    @staticmethod
    def get_template(note_type: NoteType, content: str, title: str) -> str:
        """Get the appropriate template for the note type"""
        
        templates = {
            NoteType.MEETING: NoteTemplates._meeting_template,
            NoteType.LEARNING: NoteTemplates._learning_template,
            NoteType.PROJECT: NoteTemplates._project_template,
            NoteType.PERSONAL: NoteTemplates._personal_template,
            NoteType.RESEARCH: NoteTemplates._research_template,
            NoteType.TASK: NoteTemplates._task_template,
            NoteType.IDEA: NoteTemplates._idea_template,
            NoteType.JOURNAL: NoteTemplates._journal_template,
        }
        
        template_func = templates.get(note_type, NoteTemplates._general_template)
        return template_func(content, title)
    
    @staticmethod
    def _meeting_template(content: str, title: str) -> str:
        """Template for meeting notes - focuses on decisions, action items, and follow-ups"""
        return f"""You are an expert meeting note specialist. Your job is to enhance meeting notes to be clear, actionable, and well-organized.

MEETING NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these MEETING-SPECIFIC elements:
- Extract key decisions made
- Identify action items with owners and deadlines
- Highlight important discussion points
- Organize attendees and their contributions
- Note follow-up requirements

Please provide a JSON response with:
{{
    "key_topics": ["topic1", "topic2"],
    "action_items": ["action1 with owner and deadline", "action2 with owner and deadline"],
    "important_details": ["decision1", "decision2", "key discussion point"],
    "structure_suggestions": ["Add attendees section", "Create action items table", "Include next meeting date"],
    "smart_tags": ["#Meeting", "#Decisions", "#ActionItems", "#FollowUp"],
    "enhanced_content": "Well-structured meeting notes with clear sections for decisions, action items, and key discussions",
    "enhanced_title": "Clear, descriptive meeting title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _learning_template(content: str, title: str) -> str:
        """Template for learning notes - focuses on concepts, understanding, and study plans"""
        return f"""You are an expert learning and education specialist. Your job is to enhance study notes to be clear, comprehensive, and actionable for learning.

LEARNING NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these LEARNING-SPECIFIC elements:
- Break down complex concepts into digestible parts
- Create clear learning objectives and goals
- Suggest practical applications and examples
- Identify key takeaways and insights
- Recommend further study resources

Please provide a JSON response with:
{{
    "key_topics": ["concept1", "concept2"],
    "action_items": ["practice exercise1", "review concept2", "find additional resources"],
    "important_details": ["key insight1", "key insight2", "practical application"],
    "structure_suggestions": ["Add learning objectives section", "Create examples section", "Include practice exercises"],
    "smart_tags": ["#Learning", "#Study", "#Concepts", "#Education"],
    "enhanced_content": "Well-structured learning notes with clear concepts, examples, and study guidance",
    "enhanced_title": "Clear, descriptive learning title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _project_template(content: str, title: str) -> str:
        """Template for project notes - focuses on planning, milestones, and execution"""
        return f"""You are an expert project management specialist. Your job is to enhance project notes to be strategic, organized, and actionable.

PROJECT NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these PROJECT-SPECIFIC elements:
- Define clear project objectives and scope
- Identify key milestones and deliverables
- Highlight risks, dependencies, and blockers
- Organize timeline and resource requirements
- Create actionable next steps

Please provide a JSON response with:
{{
    "key_topics": ["objective1", "milestone1", "deliverable1"],
    "action_items": ["complete task1 by date", "review milestone2", "address risk3"],
    "important_details": ["project scope", "key milestone", "critical dependency"],
    "structure_suggestions": ["Add project timeline", "Create risk register", "Include resource allocation"],
    "smart_tags": ["#Project", "#Planning", "#Milestones", "#Management"],
    "enhanced_content": "Well-structured project notes with clear objectives, timeline, and action items",
    "enhanced_title": "Clear, descriptive project title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _personal_template(content: str, title: str) -> str:
        """Template for personal notes - focuses on reflection, goals, and personal growth"""
        return f"""You are an expert personal development specialist. Your job is to enhance personal notes to be meaningful, reflective, and growth-oriented.

PERSONAL NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these PERSONAL-SPECIFIC elements:
- Encourage self-reflection and insight
- Identify personal goals and aspirations
- Highlight meaningful experiences and learnings
- Suggest actionable steps for personal growth
- Maintain authentic voice and perspective

Please provide a JSON response with:
{{
    "key_topics": ["personal insight1", "goal1", "experience1"],
    "action_items": ["personal action1", "reflection exercise", "goal setting activity"],
    "important_details": ["meaningful insight", "personal learning", "growth opportunity"],
    "structure_suggestions": ["Add reflection section", "Create goals section", "Include gratitude section"],
    "smart_tags": ["#Personal", "#Reflection", "#Growth", "#Goals"],
    "enhanced_content": "Well-structured personal notes with clear insights, goals, and growth opportunities",
    "enhanced_title": "Clear, descriptive personal title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _research_template(content: str, title: str) -> str:
        """Template for research notes - focuses on methodology, findings, and analysis"""
        return f"""You are an expert research specialist. Your job is to enhance research notes to be thorough, analytical, and evidence-based.

RESEARCH NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these RESEARCH-SPECIFIC elements:
- Organize research methodology and approach
- Highlight key findings and evidence
- Identify gaps and areas for further investigation
- Suggest analytical frameworks and tools
- Create clear research questions and hypotheses

Please provide a JSON response with:
{{
    "key_topics": ["research question1", "methodology1", "finding1"],
    "action_items": ["conduct additional research", "analyze data", "review literature"],
    "important_details": ["key finding", "research gap", "methodological insight"],
    "structure_suggestions": ["Add methodology section", "Create findings summary", "Include references"],
    "smart_tags": ["#Research", "#Analysis", "#Findings", "#Methodology"],
    "enhanced_content": "Well-structured research notes with clear methodology, findings, and analysis",
    "enhanced_title": "Clear, descriptive research title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _task_template(content: str, title: str) -> str:
        """Template for task notes - focuses on organization, priorities, and execution"""
        return f"""You are an expert task management specialist. Your job is to enhance task notes to be organized, prioritized, and actionable.

TASK NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these TASK-SPECIFIC elements:
- Organize tasks by priority and urgency
- Define clear completion criteria
- Identify dependencies and blockers
- Suggest time estimates and deadlines
- Create actionable next steps

Please provide a JSON response with:
{{
    "key_topics": ["high priority task1", "urgent task2", "blocked task3"],
    "action_items": ["complete task1 by deadline", "resolve blocker2", "start task3"],
    "important_details": ["critical deadline", "dependency", "completion criteria"],
    "structure_suggestions": ["Add priority matrix", "Create deadline tracker", "Include blocker resolution"],
    "smart_tags": ["#Tasks", "#Priorities", "#Deadlines", "#Productivity"],
    "enhanced_content": "Well-structured task notes with clear priorities, deadlines, and action items",
    "enhanced_title": "Clear, descriptive task title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _idea_template(content: str, title: str) -> str:
        """Template for idea notes - focuses on creativity, innovation, and exploration"""
        return f"""You are an expert innovation and creativity specialist. Your job is to enhance idea notes to be creative, exploratory, and innovative.

IDEA NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these IDEA-SPECIFIC elements:
- Encourage creative thinking and exploration
- Identify potential applications and use cases
- Suggest ways to develop and refine ideas
- Highlight innovative aspects and opportunities
- Create actionable steps for idea development

Please provide a JSON response with:
{{
    "key_topics": ["innovative concept1", "creative application2", "exploration area3"],
    "action_items": ["prototype idea1", "research application2", "test concept3"],
    "important_details": ["innovative insight", "creative opportunity", "development potential"],
    "structure_suggestions": ["Add brainstorming section", "Create development roadmap", "Include feasibility analysis"],
    "smart_tags": ["#Ideas", "#Innovation", "#Creativity", "#Exploration"],
    "enhanced_content": "Well-structured idea notes with clear concepts, applications, and development paths",
    "enhanced_title": "Clear, descriptive idea title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _journal_template(content: str, title: str) -> str:
        """Template for journal notes - focuses on reflection, emotions, and personal growth"""
        return f"""You are an expert journaling and reflection specialist. Your job is to enhance journal entries to be meaningful, reflective, and emotionally aware.

JOURNAL NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Focus on these JOURNAL-SPECIFIC elements:
- Encourage deep reflection and emotional awareness
- Identify patterns and insights from experiences
- Highlight personal growth and learning moments
- Suggest reflective questions and prompts
- Maintain authentic emotional expression

Please provide a JSON response with:
{{
    "key_topics": ["emotional insight1", "personal growth2", "life pattern3"],
    "action_items": ["daily reflection practice", "gratitude exercise", "personal goal review"],
    "important_details": ["emotional insight", "growth moment", "life lesson"],
    "structure_suggestions": ["Add gratitude section", "Create reflection prompts", "Include mood tracking"],
    "smart_tags": ["#Journal", "#Reflection", "#Emotions", "#Growth"],
    "enhanced_content": "Well-structured journal entry with clear insights, emotions, and growth opportunities",
    "enhanced_title": "Clear, descriptive journal title",
    "confidence_score": 0.95
}}"""

    @staticmethod
    def _general_template(content: str, title: str) -> str:
        """Fallback template for unknown note types"""
        return f"""You are an expert note-taking assistant. Your job is to enhance any type of note to be clear, organized, and useful.

GENERAL NOTE ENHANCEMENT:
Title: {title}
Content: {content}

Please provide a JSON response with:
{{
    "key_topics": ["topic1", "topic2"],
    "action_items": ["action1", "action2"],
    "important_details": ["detail1", "detail2"],
    "structure_suggestions": ["suggestion1", "suggestion2"],
    "smart_tags": ["#General", "#Notes", "#Organization"],
    "enhanced_content": "Well-structured content with clear organization and formatting",
    "enhanced_title": "Clear, descriptive title",
    "confidence_score": 0.85
}}"""
