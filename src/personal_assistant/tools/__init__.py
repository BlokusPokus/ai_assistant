"""
Collection of tools available to the agent.
"""
from ..config.logging_config import get_logger
from .base import Tool, ToolRegistry
from .calendar.calendar_tool import CalendarTool
from .emails.email_tool import EmailTool
from .internet.internet_tool import InternetTool
from .ltm.ltm_tool import LTMTool
from .notion_pages.notion_pages_tool import NotionPagesTool
from .notes.enhanced_notes_tool import EnhancedNotesTool
from .grocery.grocery_deals_tool import GroceryDealsTool

# Configure module logger
# from .planning.llm_planner import LLMPlannerTool  # Temporarily disabled - module not found
from .reminders.reminder_tool import ReminderTool
from .todos.todo_tool import create_todo_tools
from .youtube.youtube_tool import YouTubeTool
from .ai_tasks.ai_task_tool import AgentWorkflowTool

logger = get_logger("tools")


def create_tool_registry() -> ToolRegistry:
    """Creates and configures a ToolRegistry with all available tools."""
    registry = ToolRegistry()

    # Register email tools
    email_tool = EmailTool()
    for tool in email_tool:
        tool.set_category("Email")
        registry.register(tool)

    # Register calendar tools
    calendar_tool = CalendarTool()
    for tool in calendar_tool:
        tool.set_category("Calendar")
        registry.register(tool)

    # Register Notion note tools
    # notion_notes_tool = NotionNotesTool()
    # for tool in notion_notes_tool:
    #     tool.set_category("Notes")
    #     registry.register(tool)

    # Register Notion pages tools (new page-based note system)
    # notion_pages_tool = NotionPagesTool()
    # for tool in notion_pages_tool:
    #     tool.set_category("NotionPages")
    #     registry.register(tool)

    # Register enhanced notes tools (AI-powered note management)
    enhanced_notes_tool = EnhancedNotesTool()
    for tool in enhanced_notes_tool:
        tool.set_category("EnhancedNotes")
        registry.register(tool)

    # Register reminder tools
    reminder_tool = ReminderTool()
    for tool in reminder_tool:
        tool.set_category("Reminders")
        registry.register(tool)

    # Register LTM tools
    ltm_tool = LTMTool()
    for tool in ltm_tool:
        tool.set_category("LTM")
        registry.register(tool)

    # Register internet tools
    internet_tool = InternetTool()
    for tool in internet_tool:
        tool.set_category("Internet")
        registry.register(tool)

    # Register YouTube tools
    youtube_tool = YouTubeTool()
    for tool in youtube_tool:
        tool.set_category("YouTube")
        registry.register(tool)

    # Register research tools
    # research_tool = ResearchTool()
    # for tool in research_tool:
    #     tool.set_category("Research")
    #     registry.register(tool)

    # planner_tool = LLMPlannerTool()  # Temporarily disabled - module not found
    # for tool in planner_tool:
    #     tool.set_category("Planner")
    #     registry.register(tool)

    # Register todo tools
    todo_tools = create_todo_tools()
    for tool in todo_tools:
        registry.register(tool)

    # Register grocery deals tools
    grocery_deals_tool = GroceryDealsTool()
    for tool in grocery_deals_tool:
        tool.set_category("GroceryDeals")
        registry.register(tool)

    # Register AI agent workflow management tools
    agent_workflow_tool = AgentWorkflowTool()
    for tool in agent_workflow_tool:
        tool.set_category("AgentWorkflow")
        registry.register(tool)

    return registry


# Export all implemented tools
__all__ = [
    "Tool",
    "ToolRegistry",
    "CalendarTool",
    "EmailTool",
    "NotionPagesTool",
    "EnhancedNotesTool",
    "ReminderTool",
    "InternetTool",
    "YouTubeTool",
    "GroceryDealsTool",
    "create_todo_tools",
    # 'ResearchTool',
    "create_tool_registry",
    "logger",
]
