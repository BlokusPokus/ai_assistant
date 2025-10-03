"""
Todo Tool Metadata

This module provides enhanced metadata for the enhanced todo tool with missed counter
and auto-segmentation features to improve AI understanding and tool selection.
"""

from .ai_enhancements import AIEnhancementManager, EnhancementPriority
from .tool_metadata import (
    ToolCategory,
    ToolComplexity,
    ToolExample,
    ToolMetadata,
    ToolUseCase,
)


def create_todo_tool_metadata() -> ToolMetadata:
    """Create comprehensive metadata for the enhanced todo tool."""

    # Define use cases for the todo tool
    use_cases = [
        ToolUseCase(
            name="Create Personal Task",
            description="Create a personal todo item with basic information",
            example_request="Create a todo to buy groceries this weekend",
            example_parameters={
                "title": "Buy groceries",
                "description": "Get milk, bread, eggs, and vegetables for the week",
                "due_date": "2024-12-22T18:00:00",
                "priority": "medium",
                "category": "personal"
            },
            expected_outcome="Personal todo created with appropriate priority and category",
            success_indicators=["todo_created", "due_date_set", "category_assigned"],
            failure_modes=["invalid_date", "missing_title", "database_error"],
            prerequisites=["user_authenticated", "task_description", "due_date_optional"],
        ),
        ToolUseCase(
            name="Create Work Task",
            description="Create a work-related todo with high priority and specific category",
            example_request="Create a todo to finish the quarterly report by Friday",
            example_parameters={
                "title": "Complete Q4 quarterly report",
                "description": "Compile sales data, analyze trends, and create executive summary",
                "due_date": "2024-12-20T17:00:00",
                "priority": "high",
                "category": "work"
            },
            expected_outcome="High-priority work todo with clear deadline and detailed description",
            success_indicators=["todo_created", "high_priority_set", "work_category", "deadline_clear"],
            failure_modes=["missing_deadline", "insufficient_details", "priority_mismatch"],
            prerequisites=["work_context", "deadline_known", "task_scope_defined"],
        ),
        ToolUseCase(
            name="Create Complex Project Task",
            description="Create a complex task that may need segmentation after missed attempts",
            example_request="Create a todo to redesign the company website",
            example_parameters={
                "title": "Redesign company website",
                "description": "Complete overhaul of website including new design, content updates, and mobile optimization",
                "due_date": "2024-12-30T17:00:00",
                "priority": "high",
                "category": "project"
            },
            expected_outcome="Complex project todo that can be segmented if missed multiple times",
            success_indicators=["todo_created", "complex_task_identified", "segmentation_ready"],
            failure_modes=["task_too_simple", "missing_scope", "unclear_requirements"],
            prerequisites=["project_scope", "complex_requirements", "long_timeline"],
        ),
        ToolUseCase(
            name="Track Overdue Tasks",
            description="Monitor and manage tasks that have passed their due dates",
            example_request="Show me all my overdue tasks",
            example_parameters={
                "user_id": 1
            },
            expected_outcome="List of overdue todos with missed count and segmentation recommendations",
            success_indicators=["overdue_listed", "missed_count_updated", "insights_provided"],
            failure_modes=["no_overdue_tasks", "database_error", "user_not_found"],
            prerequisites=["existing_todos", "due_dates_set", "user_authenticated"],
        ),
        ToolUseCase(
            name="Get Productivity Analytics",
            description="Analyze user's task completion patterns and get behavioral insights",
            example_request="Show me my productivity analytics and insights",
            example_parameters={
                "user_id": 1
            },
            expected_outcome="Comprehensive analytics including completion rates, missed patterns, and personalized insights",
            success_indicators=["analytics_generated", "insights_provided", "patterns_identified"],
            failure_modes=["insufficient_data", "analysis_error", "user_not_found"],
            prerequisites=["todo_history", "completion_data", "user_authenticated"],
        ),
        ToolUseCase(
            name="Trigger Task Segmentation",
            description="Manually break down a complex task into manageable subtasks",
            example_request="Break down my website redesign task into smaller pieces",
            example_parameters={
                "todo_id": 5,
                "user_id": 1
            },
            expected_outcome="Complex task segmented into 3-5 manageable subtasks with individual due dates",
            success_indicators=["segmentation_triggered", "subtasks_created", "due_dates_distributed"],
            failure_modes=["task_not_eligible", "segmentation_failed", "llm_error"],
            prerequisites=["complex_task", "segmentation_threshold_met", "llm_available"],
        ),
        ToolUseCase(
            name="Complete Task",
            description="Mark a todo as completed and update completion patterns",
            example_request="Mark my grocery shopping task as done",
            example_parameters={
                "todo_id": 3,
                "user_id": 1
            },
            expected_outcome="Todo marked as completed with completion timestamp and pattern updates",
            success_indicators=["todo_completed", "completion_timestamp_set", "patterns_updated"],
            failure_modes=["todo_not_found", "already_completed", "access_denied"],
            prerequisites=["todo_exists", "user_owns_todo", "todo_not_completed"],
        ),
        ToolUseCase(
            name="Update Task Details",
            description="Modify existing todo properties like title, description, or due date",
            example_request="Update my report task to include the new requirements",
            example_parameters={
                "todo_id": 2,
                "title": "Complete Q4 quarterly report with new requirements",
                "description": "Compile sales data, analyze trends, create executive summary, and include market analysis",
                "due_date": "2024-12-21T17:00:00"
            },
            expected_outcome="Todo updated with new information and updated timestamp",
            success_indicators=["todo_updated", "changes_saved", "timestamp_updated"],
            failure_modes=["todo_not_found", "invalid_data", "access_denied"],
            prerequisites=["todo_exists", "user_owns_todo", "valid_update_data"],
        ),
        ToolUseCase(
            name="Filter Tasks by Category",
            description="Get todos filtered by specific category or status",
            example_request="Show me all my work tasks that are still pending",
            example_parameters={
                "category": "work",
                "status": "pending"
            },
            expected_outcome="Filtered list of todos matching the specified criteria",
            success_indicators=["filtered_results", "criteria_applied", "count_provided"],
            failure_modes=["no_matching_tasks", "invalid_filters", "database_error"],
            prerequisites=["existing_todos", "valid_filter_criteria", "user_authenticated"],
        ),
        ToolUseCase(
            name="Get Task Statistics",
            description="Retrieve comprehensive statistics about user's task management",
            example_request="Give me a summary of my task completion statistics",
            example_parameters={
                "user_id": 1
            },
            expected_outcome="Detailed statistics including completion rates, missed patterns, and productivity trends",
            success_indicators=["stats_generated", "completion_rate_calculated", "insights_provided"],
            failure_modes=["insufficient_data", "calculation_error", "user_not_found"],
            prerequisites=["todo_history", "completion_data", "user_authenticated"],
        ),
    ]

    # Define examples for the todo tool
    examples = [
        ToolExample(
            description="Create a simple personal task",
            user_request="I need to remember to call my mom tomorrow",
            parameters={
                "title": "Call mom",
                "description": "Check in and catch up",
                "due_date": "2024-12-20T19:00:00",
                "priority": "medium",
                "category": "personal"
            },
            expected_result="Todo created successfully with medium priority and personal category",
            notes="Simple personal task with clear deadline"
        ),
        ToolExample(
            description="Create a high-priority work task",
            user_request="I have an urgent deadline for the client presentation next week",
            parameters={
                "title": "Prepare client presentation",
                "description": "Create slides, gather data, and rehearse presentation for Q4 review",
                "due_date": "2024-12-23T14:00:00",
                "priority": "high",
                "category": "work"
            },
            expected_result="High-priority work todo created with clear deadline and detailed description",
            notes="Urgent work task requiring immediate attention"
        ),
        ToolExample(
            description="Get overdue tasks with missed counter",
            user_request="Show me what tasks I've been missing",
            parameters={},
            expected_result="List of overdue todos with missed counts and segmentation recommendations",
            notes="Helps identify tasks that need attention or segmentation"
        ),
        ToolExample(
            description="Trigger segmentation for complex task",
            user_request="Break down my website project into smaller tasks",
            parameters={
                "todo_id": 10,
                "user_id": 1
            },
            expected_result="Complex task segmented into 4-5 manageable subtasks with distributed due dates",
            notes="Uses LLM to intelligently break down overwhelming tasks"
        ),
        ToolExample(
            description="Get productivity insights",
            user_request="How am I doing with my task completion?",
            parameters={},
            expected_result="Comprehensive analytics showing completion rates, optimal work times, and personalized insights",
            notes="Provides behavioral analysis to improve productivity"
        ),
        ToolExample(
            description="Filter tasks by category and status",
            user_request="Show me all my pending work tasks",
            parameters={
                "category": "work",
                "status": "pending"
            },
            expected_result="Filtered list of pending work tasks with count and details",
            notes="Helps focus on specific types of tasks"
        ),
        ToolExample(
            description="Update task with new information",
            user_request="Update my report task to include the new requirements from the meeting",
            parameters={
                "todo_id": 5,
                "title": "Complete Q4 report with new requirements",
                "description": "Include market analysis and competitor data as discussed in today's meeting",
                "due_date": "2024-12-22T17:00:00"
            },
            expected_result="Todo updated successfully with new requirements and extended deadline",
            notes="Shows how to modify existing tasks with new information"
        ),
        ToolExample(
            description="Complete a task and track patterns",
            user_request="Mark my grocery shopping as done",
            parameters={
                "todo_id": 3,
                "user_id": 1
            },
            expected_result="Task marked as completed with timestamp and completion patterns updated",
            notes="Demonstrates task completion and pattern tracking"
        ),
    ]

    # Create the metadata object
    metadata = ToolMetadata(
        tool_name="todo_tool",
        tool_version="1.0.0",
        description="PERSONAL TASK TRACKING: Track tasks that YOU need to complete. AI helps organize and segment complex tasks, but YOU do the work. Use for: 'I need to remember to...', 'Track my progress on...', 'Break down this task...'. NOT for: AI automation, calendar events, or simple reminders.",
        category=ToolCategory.PRODUCTIVITY,
        complexity=ToolComplexity.COMPLEX,
        use_cases=use_cases,
        examples=examples,
        prerequisites=[
            "User authentication and authorization",
            "Database connection and schema",
            "LLM access for segmentation (optional)",
            "Automatic user_id injection (handled by system)"
        ],
        related_tools=[
            "calendar_tool",
            "reminder_tool",
            "note_tool",
            "email_tool"
        ],
        complementary_tools=[
            "calendar_tool",
            "reminder_tool",
            "note_tool",
            "ai_planner_tool"
        ],
        conflicting_tools=[],
        execution_time="1-3 seconds",
        success_rate=0.95,
        rate_limits="100 requests per minute per user",
        retry_strategy="Exponential backoff with 3 retries for database operations",
        ai_instructions="""
        TOOL DIFFERENTIATION - Use this tool ONLY for personal task tracking:
        
        ✅ USE TODO TOOL FOR:
        - "I need to remember to buy groceries"
        - "Track my progress on the project"
        - "Break down this complex task"
        - "I have to complete this by Friday"
        - Personal productivity management
        
        ❌ DO NOT USE TODO TOOL FOR:
        - "Make a list of good emails" → Use AI Task Tool
        - "Schedule a meeting with John" → Use Calendar Tool  
        - "Remind me to call mom at 3pm" → Use Reminder Tool
        - "Analyze my productivity patterns" → Use AI Task Tool
        
        KEY PRINCIPLES:
        1. AUTOMATIC USER_ID: User ID is automatically injected - never ask for it
        2. INTELLIGENT DATE PARSING: Accepts various date formats (YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS)
        3. MISSED COUNTER: Always check if tasks are overdue and increment missed_count
        4. SEGMENTATION: Complex tasks should be segmented after 3 missed attempts
        5. BEHAVIORAL PATTERNS: Use analytics to provide personalized insights
        6. PRIORITY GUIDANCE: Help users set appropriate priorities based on deadlines
        7. CATEGORY ORGANIZATION: Suggest meaningful categories for better organization
        8. DUE DATE VALIDATION: Ensure due dates are realistic and achievable
        9. COMPLETION TRACKING: Always update completion patterns for analytics
        10. USER CONTEXT: Consider user's productivity patterns when making recommendations
        
        FORMATTING RULES:
        - NEVER use markdown formatting (* **text**, # headers, etc.) in todo lists
        - Use plain text bullet points (•) or dashes (-) for lists
        - For SMS responses: Keep todo lists concise and mobile-friendly
        - Use simple formatting that works in all contexts
        
        When creating todos:
        - Ask for clear, actionable titles
        - Accept flexible date formats (system handles parsing)
        - Recommend appropriate priorities
        - Suggest helpful categories
        - Warn about complex tasks that might need segmentation
        
        When managing todos:
        - Check for overdue tasks regularly
        - Suggest segmentation for repeatedly missed complex tasks
        - Provide insights based on completion patterns
        - Help users understand their productivity patterns
        """,
        parameter_guidance={
            "user_id": "Always required. Must be a valid authenticated user ID.",
            "title": "Required for creation. Should be clear, actionable, and specific.",
            "description": "Optional but recommended. Provides context and details for the task.",
            "due_date": "Optional but recommended. Use ISO format. Consider user's schedule and realistic completion time.",
            "priority": "Optional, defaults to 'medium'. Use 'high' for urgent tasks, 'low' for flexible tasks.",
            "category": "Optional but helpful for organization. Common categories: work, personal, health, learning, project.",
            "status": "Optional for updates. Valid values: pending, in_progress, completed, cancelled.",
            "todo_id": "Required for updates/deletes. Must belong to the specified user.",
            "include_subtasks": "Optional for get_todos. Set to false to exclude segmented subtasks.",
            "threshold": "Optional for missed counter. Defaults to 3 missed attempts before segmentation."
        },
        common_mistakes=[
            "Creating todos without due dates for time-sensitive tasks",
            "Setting unrealistic due dates that lead to missed tasks",
            "Not using categories for organization",
            "Ignoring overdue tasks instead of addressing them",
            "Not leveraging segmentation for complex tasks",
            "Forgetting to update task status when completed",
            "Not using analytics to improve productivity patterns"
        ],
        best_practices=[
            "Always set realistic due dates with buffer time",
            "Use clear, actionable task titles",
            "Organize tasks with meaningful categories",
            "Regularly review and update task priorities",
            "Use segmentation for complex or overwhelming tasks",
            "Monitor completion patterns and adjust approach",
            "Set up regular reviews of overdue tasks",
            "Leverage behavioral analytics for productivity insights",
            "Break down large projects into manageable tasks",
            "Use the missed counter to identify problematic tasks"
        ]
    )

    return metadata


def create_todo_ai_enhancements() -> AIEnhancementManager:
    """Create AI enhancements for the todo tool."""
    
    enhancement_manager = AIEnhancementManager()
    
    # Parameter suggestion enhancement for task creation
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="todo_tool",
        parameter_name="due_date",
        suggestion_logic="Consider user's typical work hours, add buffer time for complex tasks, check for conflicts with existing tasks, and suggest realistic deadlines based on task complexity",
        examples=[
            {
                "user_input": "I need to finish the report",
                "suggestion": "When would you like to complete this? Consider adding 2-3 hours buffer for review time.",
                "reasoning": "Reports often need review time, so buffer should be added"
            },
            {
                "user_input": "Buy groceries",
                "suggestion": "Would you like to set this for this evening or weekend?",
                "reasoning": "Personal tasks are often flexible in timing"
            }
        ],
        priority=EnhancementPriority.HIGH
    )
    
    # Parameter suggestion enhancement for priority setting
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="todo_tool",
        parameter_name="priority",
        suggestion_logic="High for urgent tasks with tight deadlines, Medium for important tasks with reasonable timelines, Low for flexible tasks that can be done when convenient",
        examples=[
            {
                "user_input": "Client presentation due tomorrow",
                "suggestion": "This should be HIGH priority due to the tight deadline",
                "reasoning": "Tight deadlines require immediate attention"
            },
            {
                "user_input": "Organize my desk",
                "suggestion": "This could be LOW priority since it's not time-sensitive",
                "reasoning": "Organizational tasks are typically flexible"
            }
        ],
        priority=EnhancementPriority.MEDIUM
    )
    
    # Conversational guidance enhancement
    enhancement_manager.create_conversational_guidance_enhancement(
        tool_name="todo_tool",
        description="Provide conversational guidance for todo management",
        ai_instructions="Always ask for due dates when creating tasks, suggest breaking down complex tasks into smaller pieces, recommend appropriate categories for better organization, check for overdue tasks regularly and offer help, provide insights based on completion patterns, suggest segmentation for repeatedly missed tasks",
        examples=[
            {
                "scenario": "User creates a vague task",
                "guidance": "Could you provide more details about this task? A clear description helps with planning and execution.",
                "outcome": "User provides more specific details"
            },
            {
                "scenario": "User has many overdue tasks",
                "guidance": "I notice you have several overdue tasks. Would you like me to help prioritize them or break down the complex ones?",
                "outcome": "User gets help with task management"
            }
        ],
        priority=EnhancementPriority.HIGH
    )
    
    # Workflow suggestion enhancement for todo + calendar
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["todo_tool", "calendar_tool"],
        workflow_description="Create task and schedule time to work on it",
        workflow_steps=[
            {
                "step": 1,
                "tool": "todo_tool",
                "action": "Create task with details and due date",
                "parameters": "title, description, due_date, priority, category"
            },
            {
                "step": 2,
                "tool": "calendar_tool",
                "action": "Block time in calendar for task work",
                "parameters": "start_time, end_time, task_title, location"
            }
        ],
        examples=[
            {
                "user_request": "I need to work on the quarterly report",
                "workflow": "todo_tool -> calendar_tool",
                "reasoning": "User needs both task creation and time blocking for complex work"
            },
            {
                "user_request": "Prepare for the client meeting next week",
                "workflow": "todo_tool -> calendar_tool",
                "reasoning": "Meeting prep requires task tracking and dedicated time"
            }
        ],
        priority=EnhancementPriority.MEDIUM
    )
    
    return enhancement_manager


# Create the metadata instance
todo_metadata = create_todo_tool_metadata()
todo_ai_enhancements = create_todo_ai_enhancements()

# Export for use in other modules
__all__ = [
    "todo_metadata",
    "todo_ai_enhancements",
    "create_todo_tool_metadata",
    "create_todo_ai_enhancements"
]
