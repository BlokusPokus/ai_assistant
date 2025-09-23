"""
Topic-Specific Prompt Templates for Note Enhancement

This module provides specialized prompt templates for different note types and domains,
enabling more relevant and effective note enhancement based on content context.
"""

from typing import Dict, List
from enum import Enum
from dataclasses import dataclass

# Import individual template functions
from .note_creation_template import (
    get_meeting_template,
    get_business_meeting_template,
    get_project_template,
    get_technical_project_template,
    get_learning_template,
    get_academic_learning_template,
    get_research_template,
    get_academic_research_template,
    get_personal_template,
    get_journal_template,
    get_task_template,
    get_idea_template,
    get_creative_idea_template,
)


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
            template=get_meeting_template(),
            focus_areas=["attendees", "decisions", "action_items", "follow_ups", "discussion_points"],
            structure_guidance="Agenda → Discussion → Decisions → Action Items → Next Steps",
            enhancement_priorities=["clarity", "actionability", "accountability", "timeline"]
        )
        
        templates["meeting_business"] = PromptTemplate(
            name="meeting_business",
            note_type=NoteType.MEETING,
            domain=DomainType.BUSINESS,
            template=get_business_meeting_template(),
            focus_areas=["stakeholders", "business_objectives", "metrics", "budget", "timeline"],
            structure_guidance="Context → Objectives → Discussion → Decisions → Action Items → Metrics",
            enhancement_priorities=["business_value", "stakeholder_alignment", "measurable_outcomes"]
        )
        
        # Project Notes Templates
        templates["project_general"] = PromptTemplate(
            name="project_general",
            note_type=NoteType.PROJECT,
            domain=DomainType.GENERAL,
            template=get_project_template(),
            focus_areas=["overview", "requirements", "timeline", "milestones", "risks", "dependencies"],
            structure_guidance="Overview → Requirements → Timeline → Milestones → Risks → Next Steps",
            enhancement_priorities=["clarity", "completeness", "actionability", "risk_awareness"]
        )
        
        templates["project_technical"] = PromptTemplate(
            name="project_technical",
            note_type=NoteType.PROJECT,
            domain=DomainType.TECHNICAL,
            template=get_technical_project_template(),
            focus_areas=["architecture", "requirements", "implementation", "testing", "deployment"],
            structure_guidance="Architecture → Requirements → Implementation Plan → Testing Strategy → Deployment",
            enhancement_priorities=["technical_accuracy", "implementation_feasibility", "testing_coverage"]
        )
        
        # Learning Notes Templates
        templates["learning_general"] = PromptTemplate(
            name="learning_general",
            note_type=NoteType.LEARNING,
            domain=DomainType.GENERAL,
            template=get_learning_template(),
            focus_areas=["source", "key_concepts", "examples", "applications", "practice"],
            structure_guidance="Source → Key Concepts → Examples → Applications → Practice",
            enhancement_priorities=["comprehension", "retention", "application", "practical_value"]
        )
        
        templates["learning_academic"] = PromptTemplate(
            name="learning_academic",
            note_type=NoteType.LEARNING,
            domain=DomainType.ACADEMIC,
            template=get_academic_learning_template(),
            focus_areas=["source_credibility", "methodology", "findings", "implications", "references"],
            structure_guidance="Source → Methodology → Key Findings → Implications → References",
            enhancement_priorities=["academic_rigor", "critical_analysis", "synthesis", "citation_accuracy"]
        )
        
        # Research Notes Templates
        templates["research_general"] = PromptTemplate(
            name="research_general",
            note_type=NoteType.RESEARCH,
            domain=DomainType.GENERAL,
            template=get_research_template(),
            focus_areas=["hypothesis", "methodology", "findings", "conclusions", "references"],
            structure_guidance="Hypothesis → Methodology → Findings → Conclusions → References",
            enhancement_priorities=["scientific_rigor", "reproducibility", "evidence_based", "critical_thinking"]
        )
        
        templates["research_academic"] = PromptTemplate(
            name="research_academic",
            note_type=NoteType.RESEARCH,
            domain=DomainType.ACADEMIC,
            template=get_academic_research_template(),
            focus_areas=["literature_review", "methodology", "data_analysis", "findings", "implications"],
            structure_guidance="Literature Review → Methodology → Data Analysis → Findings → Implications",
            enhancement_priorities=["academic_standards", "peer_review_quality", "contribution_to_field"]
        )
        
        # Personal Notes Templates
        templates["personal_general"] = PromptTemplate(
            name="personal_general",
            note_type=NoteType.PERSONAL,
            domain=DomainType.GENERAL,
            template=get_personal_template(),
            focus_areas=["context", "emotions", "insights", "goals", "reflections"],
            structure_guidance="Context → Experience → Insights → Goals → Reflections",
            enhancement_priorities=["authenticity", "self_awareness", "growth_mindset", "actionability"]
        )
        
        templates["personal_journal"] = PromptTemplate(
            name="personal_journal",
            note_type=NoteType.JOURNAL,
            domain=DomainType.GENERAL,
            template=get_journal_template(),
            focus_areas=["daily_events", "emotions", "gratitude", "challenges", "growth"],
            structure_guidance="Daily Events → Emotions → Gratitude → Challenges → Growth",
            enhancement_priorities=["emotional_awareness", "gratitude_practice", "personal_growth", "reflection"]
        )
        
        # Task Notes Templates
        templates["task_general"] = PromptTemplate(
            name="task_general",
            note_type=NoteType.TASK,
            domain=DomainType.GENERAL,
            template=get_task_template(),
            focus_areas=["priority", "deadline", "status", "dependencies", "completion_criteria"],
            structure_guidance="Task Description → Priority → Deadline → Dependencies → Completion Criteria",
            enhancement_priorities=["clarity", "urgency", "feasibility", "success_criteria"]
        )
        
        # Idea Notes Templates
        templates["idea_general"] = PromptTemplate(
            name="idea_general",
            note_type=NoteType.IDEA,
            domain=DomainType.GENERAL,
            template=get_idea_template(),
            focus_areas=["concept", "feasibility", "implementation", "impact", "next_steps"],
            structure_guidance="Concept → Feasibility → Implementation → Impact → Next Steps",
            enhancement_priorities=["innovation", "feasibility", "impact_assessment", "actionability"]
        )
        
        templates["idea_creative"] = PromptTemplate(
            name="idea_creative",
            note_type=NoteType.IDEA,
            domain=DomainType.CREATIVE,
            template=get_creative_idea_template(),
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
    
