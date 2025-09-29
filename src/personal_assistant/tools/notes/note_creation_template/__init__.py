"""
Note Creation Template Package

This package contains individual template files for different note types and domains.
Each template is designed for specific note enhancement scenarios.
"""

from .meeting_general import get_meeting_template
from .meeting_business import get_business_meeting_template
from .project_general import get_project_template
from .project_technical import get_technical_project_template
from .learning_general import get_learning_template
from .learning_academic import get_academic_learning_template
from .research_general import get_research_template
from .research_academic import get_academic_research_template
from .personal_general import get_personal_template
from .personal_journal import get_journal_template
from .task_general import get_task_template
from .idea_general import get_idea_template
from .idea_creative import get_creative_idea_template

__all__ = [
    "get_meeting_template",
    "get_business_meeting_template", 
    "get_project_template",
    "get_technical_project_template",
    "get_learning_template",
    "get_academic_learning_template",
    "get_research_template",
    "get_academic_research_template",
    "get_personal_template",
    "get_journal_template",
    "get_task_template",
    "get_idea_template",
    "get_creative_idea_template",
]
