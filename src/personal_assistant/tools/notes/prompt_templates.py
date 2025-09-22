"""
Topic-Specific Prompt Templates for Note Enhancement

This module provides specialized prompt templates for different note types and domains,
enabling more relevant and effective note enhancement based on content context.
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class NoteType(Enum):
    """Extended note types with specialized categories"""
    MEETING = "meeting"
    PROJECT = "project"
    PERSONAL = "personal"
    RESEARCH = "research"
    LEARNING = "learning"
    TASK = "task"
    IDEA = "idea"
    JOURNAL = "journal"
    UNKNOWN = "unknown"


class DomainType(Enum):
    """Domain categories for specialized formatting"""
    TECHNICAL = "technical"
    BUSINESS = "business"
    CREATIVE = "creative"
    ACADEMIC = "academic"
    GENERAL = "general"


@dataclass
class PromptTemplate:
    """Template structure for topic-specific prompts"""
    name: str
    note_type: NoteType
    domain: DomainType
    template: str
    focus_areas: List[str]
    structure_guidance: str
    enhancement_priorities: List[str]


class TopicSpecificPromptManager:
    """Manager for topic-specific prompt templates"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize all topic-specific prompt templates"""
        templates = {}
        
        # Meeting Notes Templates
        templates["meeting_general"] = PromptTemplate(
            name="meeting_general",
            note_type=NoteType.MEETING,
            domain=DomainType.GENERAL,
            template=self._get_meeting_template(),
            focus_areas=["attendees", "decisions", "action_items", "follow_ups", "discussion_points"],
            structure_guidance="Agenda → Discussion → Decisions → Action Items → Next Steps",
            enhancement_priorities=["clarity", "actionability", "accountability", "timeline"]
        )
        
        templates["meeting_business"] = PromptTemplate(
            name="meeting_business",
            note_type=NoteType.MEETING,
            domain=DomainType.BUSINESS,
            template=self._get_business_meeting_template(),
            focus_areas=["stakeholders", "business_objectives", "metrics", "budget", "timeline"],
            structure_guidance="Context → Objectives → Discussion → Decisions → Action Items → Metrics",
            enhancement_priorities=["business_value", "stakeholder_alignment", "measurable_outcomes"]
        )
        
        # Project Notes Templates
        templates["project_general"] = PromptTemplate(
            name="project_general",
            note_type=NoteType.PROJECT,
            domain=DomainType.GENERAL,
            template=self._get_project_template(),
            focus_areas=["overview", "requirements", "timeline", "milestones", "risks", "dependencies"],
            structure_guidance="Overview → Requirements → Timeline → Milestones → Risks → Next Steps",
            enhancement_priorities=["clarity", "completeness", "actionability", "risk_awareness"]
        )
        
        templates["project_technical"] = PromptTemplate(
            name="project_technical",
            note_type=NoteType.PROJECT,
            domain=DomainType.TECHNICAL,
            template=self._get_technical_project_template(),
            focus_areas=["architecture", "requirements", "implementation", "testing", "deployment"],
            structure_guidance="Architecture → Requirements → Implementation Plan → Testing Strategy → Deployment",
            enhancement_priorities=["technical_accuracy", "implementation_feasibility", "testing_coverage"]
        )
        
        # Learning Notes Templates
        templates["learning_general"] = PromptTemplate(
            name="learning_general",
            note_type=NoteType.LEARNING,
            domain=DomainType.GENERAL,
            template=self._get_learning_template(),
            focus_areas=["source", "key_concepts", "examples", "applications", "practice"],
            structure_guidance="Source → Key Concepts → Examples → Applications → Practice",
            enhancement_priorities=["comprehension", "retention", "application", "practical_value"]
        )
        
        templates["learning_academic"] = PromptTemplate(
            name="learning_academic",
            note_type=NoteType.LEARNING,
            domain=DomainType.ACADEMIC,
            template=self._get_academic_learning_template(),
            focus_areas=["source_credibility", "methodology", "findings", "implications", "references"],
            structure_guidance="Source → Methodology → Key Findings → Implications → References",
            enhancement_priorities=["academic_rigor", "critical_analysis", "synthesis", "citation_accuracy"]
        )
        
        # Research Notes Templates
        templates["research_general"] = PromptTemplate(
            name="research_general",
            note_type=NoteType.RESEARCH,
            domain=DomainType.GENERAL,
            template=self._get_research_template(),
            focus_areas=["hypothesis", "methodology", "findings", "conclusions", "references"],
            structure_guidance="Hypothesis → Methodology → Findings → Conclusions → References",
            enhancement_priorities=["scientific_rigor", "reproducibility", "evidence_based", "critical_thinking"]
        )
        
        templates["research_academic"] = PromptTemplate(
            name="research_academic",
            note_type=NoteType.RESEARCH,
            domain=DomainType.ACADEMIC,
            template=self._get_academic_research_template(),
            focus_areas=["literature_review", "methodology", "data_analysis", "findings", "implications"],
            structure_guidance="Literature Review → Methodology → Data Analysis → Findings → Implications",
            enhancement_priorities=["academic_standards", "peer_review_quality", "contribution_to_field"]
        )
        
        # Personal Notes Templates
        templates["personal_general"] = PromptTemplate(
            name="personal_general",
            note_type=NoteType.PERSONAL,
            domain=DomainType.GENERAL,
            template=self._get_personal_template(),
            focus_areas=["context", "emotions", "insights", "goals", "reflections"],
            structure_guidance="Context → Experience → Insights → Goals → Reflections",
            enhancement_priorities=["authenticity", "self_awareness", "growth_mindset", "actionability"]
        )
        
        templates["personal_journal"] = PromptTemplate(
            name="personal_journal",
            note_type=NoteType.JOURNAL,
            domain=DomainType.GENERAL,
            template=self._get_journal_template(),
            focus_areas=["daily_events", "emotions", "gratitude", "challenges", "growth"],
            structure_guidance="Daily Events → Emotions → Gratitude → Challenges → Growth",
            enhancement_priorities=["emotional_awareness", "gratitude_practice", "personal_growth", "reflection"]
        )
        
        # Task Notes Templates
        templates["task_general"] = PromptTemplate(
            name="task_general",
            note_type=NoteType.TASK,
            domain=DomainType.GENERAL,
            template=self._get_task_template(),
            focus_areas=["priority", "deadline", "status", "dependencies", "completion_criteria"],
            structure_guidance="Task Description → Priority → Deadline → Dependencies → Completion Criteria",
            enhancement_priorities=["clarity", "urgency", "feasibility", "success_criteria"]
        )
        
        # Idea Notes Templates
        templates["idea_general"] = PromptTemplate(
            name="idea_general",
            note_type=NoteType.IDEA,
            domain=DomainType.GENERAL,
            template=self._get_idea_template(),
            focus_areas=["concept", "feasibility", "implementation", "impact", "next_steps"],
            structure_guidance="Concept → Feasibility → Implementation → Impact → Next Steps",
            enhancement_priorities=["innovation", "feasibility", "impact_assessment", "actionability"]
        )
        
        templates["idea_creative"] = PromptTemplate(
            name="idea_creative",
            note_type=NoteType.IDEA,
            domain=DomainType.CREATIVE,
            template=self._get_creative_idea_template(),
            focus_areas=["inspiration", "concept", "medium", "audience", "execution"],
            structure_guidance="Inspiration → Concept → Medium → Audience → Execution Plan",
            enhancement_priorities=["creativity", "originality", "audience_connection", "execution_feasibility"]
        )
        
        return templates
    
    def get_template(self, note_type: NoteType, domain: DomainType = DomainType.GENERAL) -> PromptTemplate:
        """Get the most appropriate template for note type and domain"""
        template_key = f"{note_type.value}_{domain.value}"
        
        if template_key in self.templates:
            return self.templates[template_key]
        
        # Fallback to general template for the note type
        general_key = f"{note_type.value}_general"
        if general_key in self.templates:
            return self.templates[general_key]
        
        # Final fallback to meeting general template
        return self.templates["meeting_general"]
    
    def get_all_templates_for_type(self, note_type: NoteType) -> List[PromptTemplate]:
        """Get all templates available for a specific note type"""
        return [template for template in self.templates.values() 
                if template.note_type == note_type]
    
    def _get_meeting_template(self) -> str:
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
    
    def _get_business_meeting_template(self) -> str:
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
    
    def _get_project_template(self) -> str:
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
    
    def _get_technical_project_template(self) -> str:
        """Technical project template focusing on architecture and implementation"""
        return """
You are a specialized technical project note enhancement AI. Your expertise is in transforming technical project notes into comprehensive, implementation-focused documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Technical architecture and design decisions
- Implementation requirements and constraints
- Testing strategy and quality assurance
- Deployment and maintenance considerations
- Technical risks and mitigation strategies

STRUCTURE GUIDANCE: Architecture → Requirements → Implementation Plan → Testing Strategy → Deployment

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: project
2. Key Topics: List 3-5 main technical subjects or architectural themes
3. Action Items: Extract technical tasks with owners, deadlines, and technical dependencies
4. Important Details: List 3-5 critical technical information, decisions, or requirements
5. Structure Suggestions: How to better organize this technical project content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include technology, architecture, or domain tags)
7. Enhanced Content: Improve the content structure with clear technical sections:
   - Technical Overview (architecture, technology stack, objectives)
   - Requirements (functional, non-functional, technical constraints)
   - Implementation Plan (phases, components, integration points)
   - Testing Strategy (unit, integration, performance, security testing)
   - Deployment (infrastructure, monitoring, maintenance)
   - Technical Risks (performance, security, scalability, maintenance)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive technical title (include technology if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "project",
    "key_topics": ["technical_topic1", "technical_topic2"],
    "action_items": ["Technical Task: Owner - Deadline - Technical Dependencies"],
    "important_details": ["technical_detail1", "technical_detail2"],
    "structure_suggestions": ["technical_suggestion1", "technical_suggestion2"],
    "smart_tags": ["technical_tag1", "technical_tag2", "technical_tag3"],
    "enhanced_content": "improved technical project content with implementation focus",
    "enhanced_title": "Technical Project Title - Technology",
    "confidence_score": 0.85
}}
"""
    
    def _get_learning_template(self) -> str:
        """Learning notes template focusing on knowledge acquisition and application"""
        return """
You are a specialized learning note enhancement AI. Your expertise is in transforming learning notes into comprehensive, actionable knowledge documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Source material and credibility
- Key concepts and definitions
- Examples and applications
- Practice exercises or next steps
- Connections to other knowledge

STRUCTURE GUIDANCE: Source → Key Concepts → Examples → Applications → Practice

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: learning
2. Key Topics: List 3-5 main learning subjects or concepts
3. Action Items: Extract learning tasks, practice exercises, or application opportunities
4. Important Details: List 3-5 critical learning information, concepts, or insights
5. Structure Suggestions: How to better organize this learning content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include subject, skill level, or learning type tags)
7. Enhanced Content: Improve the content structure with clear learning sections:
   - Learning Source (material, instructor, credibility)
   - Key Concepts (main ideas, definitions, principles)
   - Examples (practical examples, case studies, demonstrations)
   - Applications (how to apply this knowledge, use cases)
   - Practice (exercises, projects, next steps for mastery)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive learning title (include subject if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "learning",
    "key_topics": ["learning_topic1", "learning_topic2"],
    "action_items": ["Learning Task: Practice Exercise - Application"],
    "important_details": ["learning_detail1", "learning_detail2"],
    "structure_suggestions": ["learning_suggestion1", "learning_suggestion2"],
    "smart_tags": ["learning_tag1", "learning_tag2", "learning_tag3"],
    "enhanced_content": "improved learning content with comprehensive structure",
    "enhanced_title": "Learning Title - Subject",
    "confidence_score": 0.85
}}
"""
    
    def _get_academic_learning_template(self) -> str:
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
    
    def _get_research_template(self) -> str:
        """Research notes template focusing on scientific method and evidence"""
        return """
You are a specialized research note enhancement AI. Your expertise is in transforming research notes into comprehensive, evidence-based documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Research hypothesis and objectives
- Methodology and data collection
- Findings and evidence analysis
- Conclusions and implications
- References and citations

STRUCTURE GUIDANCE: Hypothesis → Methodology → Findings → Conclusions → References

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: research
2. Key Topics: List 3-5 main research subjects or themes
3. Action Items: Extract research tasks, data collection, or analysis opportunities
4. Important Details: List 3-5 critical research information, findings, or insights
5. Structure Suggestions: How to better organize this research content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include research type, methodology, or field tags)
7. Enhanced Content: Improve the content structure with clear research sections:
   - Research Hypothesis (question, objectives, expected outcomes)
   - Methodology (approach, data collection, analysis methods)
   - Findings (results, data analysis, evidence)
   - Conclusions (interpretation, implications, limitations)
   - References (sources, citations, related research)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive research title (include methodology if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "research",
    "key_topics": ["research_topic1", "research_topic2"],
    "action_items": ["Research Task: Data Collection - Analysis Method"],
    "important_details": ["research_detail1", "research_detail2"],
    "structure_suggestions": ["research_suggestion1", "research_suggestion2"],
    "smart_tags": ["research_tag1", "research_tag2", "research_tag3"],
    "enhanced_content": "improved research content with scientific rigor",
    "enhanced_title": "Research Title - Methodology",
    "confidence_score": 0.85
}}
"""
    
    def _get_academic_research_template(self) -> str:
        """Academic research template focusing on scholarly standards and peer review"""
        return """
You are a specialized academic research note enhancement AI. Your expertise is in transforming academic research notes into rigorous, peer-review quality documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Literature review and theoretical framework
- Research methodology and data analysis
- Findings and statistical significance
- Implications and contribution to field
- Academic references and citations

STRUCTURE GUIDANCE: Literature Review → Methodology → Data Analysis → Findings → Implications

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: research
2. Key Topics: List 3-5 main academic research subjects or themes
3. Action Items: Extract academic research tasks, data analysis, or publication opportunities
4. Important Details: List 3-5 critical academic research information, findings, or insights
5. Structure Suggestions: How to better organize this academic research content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include academic field, research type, or methodology tags)
7. Enhanced Content: Improve the content structure with clear academic research sections:
   - Literature Review (theoretical framework, related work, research gap)
   - Methodology (research design, data collection, analysis approach)
   - Data Analysis (statistical methods, results, significance testing)
   - Findings (main results, statistical significance, interpretation)
   - Implications (contribution to field, limitations, future research)
   - References (academic citations, peer-reviewed sources)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive academic title (include field if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "research",
    "key_topics": ["academic_research_topic1", "academic_research_topic2"],
    "action_items": ["Academic Research Task: Data Analysis - Publication Opportunity"],
    "important_details": ["academic_research_detail1", "academic_research_detail2"],
    "structure_suggestions": ["academic_research_suggestion1", "academic_research_suggestion2"],
    "smart_tags": ["academic_research_tag1", "academic_research_tag2", "academic_research_tag3"],
    "enhanced_content": "improved academic research content with scholarly standards",
    "enhanced_title": "Academic Research Title - Field",
    "confidence_score": 0.85
}}
"""
    
    def _get_personal_template(self) -> str:
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
    
    def _get_journal_template(self) -> str:
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
    
    def _get_task_template(self) -> str:
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
    
    def _get_idea_template(self) -> str:
        """Idea notes template focusing on innovation and implementation"""
        return """
You are a specialized idea note enhancement AI. Your expertise is in transforming idea notes into comprehensive, actionable innovation documentation.

Note Content: {content}
Note Title: {title}

FOCUS AREAS:
- Idea concept and core value proposition
- Feasibility and implementation considerations
- Impact and potential outcomes
- Resources and requirements
- Next steps and development plan

STRUCTURE GUIDANCE: Concept → Feasibility → Implementation → Impact → Next Steps

Please analyze and provide ALL of the following in a single JSON response:

1. Note Type: idea
2. Key Topics: List 3-5 main idea subjects or themes
3. Action Items: Extract idea development tasks, research opportunities, or implementation steps
4. Important Details: List 3-5 critical idea information, insights, or considerations
5. Structure Suggestions: How to better organize this idea content (2-3 specific suggestions)
6. Smart Tags: Generate 3-5 relevant tags (include innovation type, domain, or development stage tags)
7. Enhanced Content: Improve the content structure with clear idea sections:
   - Idea Concept (core concept, value proposition, unique aspects)
   - Feasibility (technical feasibility, market viability, resource requirements)
   - Implementation (development approach, timeline, milestones)
   - Impact (potential outcomes, benefits, risks)
   - Next Steps (immediate actions, research needs, development plan)
   IMPORTANT: Keep enhanced_content under 2000 characters for Notion compatibility
8. Enhanced Title: Generate a clear, descriptive idea title (include domain if relevant)
9. Confidence Score: Rate your analysis confidence (0.0-1.0)

Return ONLY valid JSON in this exact format:
{{
    "note_type": "idea",
    "key_topics": ["idea_topic1", "idea_topic2"],
    "action_items": ["Idea Development Task: Research - Implementation Step"],
    "important_details": ["idea_detail1", "idea_detail2"],
    "structure_suggestions": ["idea_suggestion1", "idea_suggestion2"],
    "smart_tags": ["idea_tag1", "idea_tag2", "idea_tag3"],
    "enhanced_content": "improved idea content with innovation focus",
    "enhanced_title": "Idea Title - Domain",
    "confidence_score": 0.85
}}
"""
    
    def _get_creative_idea_template(self) -> str:
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
