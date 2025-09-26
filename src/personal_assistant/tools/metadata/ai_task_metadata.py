"""
AI Task Scheduler Metadata

This module provides enhanced metadata for the AI task scheduler tools to improve AI understanding
and tool selection capabilities for reminder and task management.
"""

from .ai_enhancements import AIEnhancement, AIEnhancementManager, EnhancementPriority, EnhancementType
from .tool_metadata import (
    ToolCategory,
    ToolComplexity,
    ToolExample,
    ToolMetadata,
    ToolUseCase,
)


def create_ai_task_metadata() -> ToolMetadata:
    """Create comprehensive metadata for the AI task scheduler tools."""

    # Define use cases for the AI task scheduler
    use_cases = [
        ToolUseCase(
            name="Set One-Time Reminder",
            description="Create a single reminder for a specific time or event",
            example_request="Remind me to call the dentist tomorrow at 2pm",
            example_parameters={
                "title": "Call the dentist to schedule checkup",
                "description": "This is important for maintaining your oral health and staying on top of preventive care.",
                "task_type": "reminder",
                "schedule_type": "once",
                "next_run_at": "tomorrow at 2pm",
                "ai_context": "EXECUTION PLAN: 1) Check current time and calculate reminder timing 2) Send personalized SMS reminder with dentist contact info if available 3) Include motivation about preventive care benefits 4) Log reminder interaction for tracking 5) Follow up if no response after 24 hours. CONTEXT: User needs to schedule dental checkup for preventive care. Timing is flexible but should be during business hours.",
                "notification_channels": ["sms"],
                "user_id": 126,
            },
            expected_outcome="Reminder created and scheduled for the specified time",
            success_indicators=["reminder_created", "time_parsed", "scheduled_correctly"],
            failure_modes=["invalid_time_format", "parsing_error", "database_error"],
            prerequisites=["valid time string", "reminder text", "user_id"],
        ),
        ToolUseCase(
            name="Set Recurring Reminder",
            description="Create a recurring reminder that repeats at regular intervals",
            example_request="Remind me to take medication every day at 8am",
            example_parameters={
                "title": "Take morning medication",
                "description": "This daily habit keeps you healthy and on track with your treatment plan.",
                "task_type": "reminder",
                "schedule_type": "daily",
                "schedule_config": {"interval": "daily", "time": "08:00"},
                "next_run_at": "every day at 8am",
                "ai_context": "EXECUTION PLAN: 1) Check user's medication schedule and current time 2) Verify if medication was already taken today by checking recent activity logs 3) If not taken, send personalized reminder with medication name and dosage 4) If already taken, send confirmation message 5) Log the interaction for tracking compliance. CONTEXT: User has prescribed morning medication that must be taken consistently for health management. Timing is critical for effectiveness.",
                "notification_channels": ["sms"],
                "user_id": 126,
            },
            expected_outcome="Recurring reminder created with daily schedule",
            success_indicators=["recurring_reminder_created", "schedule_parsed", "recurrence_set"],
            failure_modes=["invalid_recurrence", "schedule_conflict", "parsing_error"],
            prerequisites=["recurrence pattern", "base time", "reminder text"],
        ),
        ToolUseCase(
            name="Set Work Reminder",
            description="Create reminders for work-related tasks and meetings",
            example_request="Remind me about the team standup meeting every weekday at 9am",
            example_parameters={
                "title": "Team standup meeting - prepare updates",
                "description": "This daily meeting keeps the team aligned and helps you stay on top of project progress.",
                "task_type": "reminder",
                "schedule_type": "daily",
                "schedule_config": {"interval": "daily", "time": "09:00", "weekdays_only": True},
                "next_run_at": "every weekday at 9am",
                "ai_context": "EXECUTION PLAN: 1) Check current time against meeting schedule 2) Send reminder 15 minutes before standup with preparation checklist 3) Include previous day's action items if available 4) Provide quick access to project status updates 5) Log meeting attendance for team tracking. CONTEXT: User participates in daily team standup meetings. Preparation includes reviewing yesterday's work and planning today's priorities.",
                "notification_channels": ["sms"],
                "user_id": 126,
            },
            expected_outcome="Work reminder created with weekday schedule",
            success_indicators=["work_reminder_created", "weekday_schedule_set", "work_context_applied"],
            failure_modes=["invalid_weekday_schedule", "work_context_missing", "scheduling_error"],
            prerequisites=["work_schedule", "meeting_details", "recurrence_pattern"],
        ),
        ToolUseCase(
            name="Set Health Reminder",
            description="Create reminders for health-related activities",
            example_request="Remind me to drink water every 2 hours during work",
            example_parameters={
                "title": "Drink water - stay hydrated",
                "description": "This regular habit keeps you energized and focused throughout your workday.",
                "task_type": "reminder",
                "schedule_type": "custom",
                "schedule_config": {"interval": "2_hours", "start_time": "09:00", "end_time": "17:00"},
                "next_run_at": "every 2 hours from 9am to 5pm",
                "ai_context": "EXECUTION PLAN: 1) Track water intake intervals during work hours (9am-5pm) 2) Send gentle reminder every 2 hours with hydration tips 3) Include water intake tracking if available 4) Adjust frequency based on user response patterns 5) Provide hydration benefits motivation. CONTEXT: User wants to maintain proper hydration during work hours for health and productivity. Regular gentle reminders are preferred.",
                "notification_channels": ["push"],
                "user_id": 126,
            },
            expected_outcome="Health reminder created with interval schedule",
            success_indicators=["health_reminder_created", "interval_set", "health_context_applied"],
            failure_modes=["invalid_interval", "health_context_missing", "scheduling_error"],
            prerequisites=["health_activity", "interval_timing", "health_goals"],
        ),
        ToolUseCase(
            name="Set Personal Reminder",
            description="Create reminders for personal tasks and activities",
            example_request="Remind me to buy groceries this weekend",
            example_parameters={
                "title": "Buy groceries - milk, bread, eggs",
                "description": "This weekend shopping trip ensures you have essentials for the week ahead.",
                "task_type": "reminder",
                "schedule_type": "once",
                "next_run_at": "this saturday at 10am",
                "ai_context": "EXECUTION PLAN: 1) Check weekend schedule and suggest optimal shopping time 2) Include grocery list if available or prompt user to create one 3) Send reminder with store hours and location info 4) Provide meal planning suggestions for the week 5) Follow up after shopping to track completion. CONTEXT: User has weekly grocery shopping routine for meal planning. Weekend timing works best for their schedule.",
                "notification_channels": ["sms"],
                "user_id": 126,
            },
            expected_outcome="Personal reminder created for weekend shopping",
            success_indicators=["personal_reminder_created", "weekend_timing_set", "shopping_list_included"],
            failure_modes=["invalid_weekend_time", "shopping_list_missing", "personal_context_error"],
            prerequisites=["personal_schedule", "shopping_list", "weekend_availability"],
        ),
        ToolUseCase(
            name="Set Complex Automated Task",
            description="Create AI-executed tasks that require analysis and decision-making",
            example_request="Analyze my emails and classify them",
            example_parameters={
                "title": "Email Inbox Management - Classify Emails",
                "description": "Analyze emails and classify them based on user preferences to help with inbox management.",
                "task_type": "automated_task",
                "schedule_type": "once",
                "next_run_at": "immediately",
                "ai_context": "EXECUTION PLAN: 1) Connect to user's email account (Outlook/Gmail) 2) Fetch last 10 emails 3) Analyze email content, sender reputation, and subject lines 4) Apply classification rules: Important (work, bills, appointments), Useless (spam, promotions) 5) Move emails to appropriate folders 6) Provide clear summary report. CONTEXT: User wants automated email triage with specific criteria - analyze last 10 emails, create Important and Useless folders, use sender reputation and keywords for classification.",
                "notification_channels": ["email"],
                "user_id": 126,
            },
            expected_outcome="AI task created for email analysis and classification with specific user preferences",
            success_indicators=["automated_task_created", "ai_context_set", "execution_scheduled", "user_preferences_applied"],
            failure_modes=["invalid_ai_context", "execution_error", "tool_access_denied", "insufficient_user_input"],
            prerequisites=["email_tool_access", "ai_execution_capability", "user_permission", "clarifying_questions_answered"],
        ),
        ToolUseCase(
            name="List Active Reminders",
            description="View all currently active reminders for the user",
            example_request="Show me all my active reminders",
            example_parameters={
                "status": "active",
                "user_id": 126,
            },
            expected_outcome="List of all active reminders with details",
            success_indicators=["reminders_listed", "details_shown", "count_displayed"],
            failure_modes=["no_reminders_found", "database_error", "permission_denied"],
            prerequisites=["user_id", "valid_status"],
        ),
        ToolUseCase(
            name="Update Existing Reminder",
            description="Modify an existing reminder's details",
            example_request="Change my dentist appointment reminder to 3pm instead of 2pm",
            example_parameters={
                "reminder_id": 123,
                "user_id": 126,
                "update_data": {
                    "title": "Call dentist - rescheduled",
                    "next_run_at": "tomorrow at 3pm",
                },
            },
            expected_outcome="Reminder updated with new details",
            success_indicators=["reminder_updated", "changes_applied", "confirmation_shown"],
            failure_modes=["reminder_not_found", "invalid_updates", "permission_denied"],
            prerequisites=["valid_reminder_id", "update_data", "user_permission"],
        ),
        ToolUseCase(
            name="Delete Reminder",
            description="Remove a reminder that is no longer needed",
            example_request="Delete my old dentist appointment reminder",
            example_parameters={
                "reminder_id": 123,
                "user_id": 126,
            },
            expected_outcome="Reminder deleted successfully",
            success_indicators=["reminder_deleted", "confirmation_shown", "list_updated"],
            failure_modes=["reminder_not_found", "permission_denied", "deletion_failed"],
            prerequisites=["valid_reminder_id", "user_permission"],
        ),
        ToolUseCase(
            name="Set Work Reminder",
            description="Create reminders for work-related tasks and meetings",
            example_request="Remind me about the team standup meeting every weekday at 9am",
            example_parameters={
                "text": "Team standup meeting - prepare updates",
                "time": "every weekday at 9am",
                "channel": "sms",
                "user_id": 126,
                "schedule_type": "recurring",
                "task_type": "work_reminder",
            },
            expected_outcome="Work reminder created with weekday schedule",
            success_indicators=["work_reminder_created", "weekday_schedule_set", "work_context_applied"],
            failure_modes=["invalid_weekday_schedule", "work_context_missing", "scheduling_error"],
            prerequisites=["work_schedule", "meeting_details", "recurrence_pattern"],
        ),
        ToolUseCase(
            name="Set Health Reminder",
            description="Create reminders for health-related activities",
            example_request="Remind me to drink water every 2 hours during work",
            example_parameters={
                "text": "Drink water - stay hydrated",
                "time": "every 2 hours from 9am to 5pm",
                "channel": "sms",
                "user_id": 126,
                "schedule_type": "recurring",
                "task_type": "health_reminder",
            },
            expected_outcome="Health reminder created with interval schedule",
            success_indicators=["health_reminder_created", "interval_set", "health_context_applied"],
            failure_modes=["invalid_interval", "health_context_missing", "scheduling_error"],
            prerequisites=["health_activity", "interval_timing", "health_goals"],
        ),
        ToolUseCase(
            name="Set Personal Reminder",
            description="Create reminders for personal tasks and activities",
            example_request="Remind me to buy groceries this weekend",
            example_parameters={
                "text": "Buy groceries - milk, bread, eggs",
                "time": "this saturday at 10am",
                "channel": "sms",
                "user_id": 126,
                "task_type": "personal_reminder",
            },
            expected_outcome="Personal reminder created for weekend shopping",
            success_indicators=["personal_reminder_created", "weekend_timing_set", "shopping_list_included"],
            failure_modes=["invalid_weekend_time", "shopping_list_missing", "personal_context_error"],
            prerequisites=["personal_schedule", "shopping_list", "weekend_availability"],
        ),
    ]

    # Define examples for better AI understanding
    examples = [
        ToolExample(
            description="Basic reminder for a specific time",
            user_request="Remind me to call mom at 7pm",
            parameters={
                "title": "Call mom",
                "description": "This is important for staying connected with family and showing you care.",
                "task_type": "reminder",
                "schedule_type": "once",
                "next_run_at": "7pm today",
                "ai_context": "EXECUTION PLAN: 1) Check optimal calling time based on user's schedule and timezone 2) Send personalized reminder with mom's contact info if available 3) Include conversation starters or recent family updates 4) Provide gentle motivation about family connection importance 5) Log call completion for relationship tracking. CONTEXT: User values family connections and wants to maintain regular contact with their mother. Timing should be convenient for both parties.",
                "notification_channels": ["sms"],
                "user_id": 126,
            },
            expected_result="✅ Reminder set: 'Call mom' for 2024-01-15 19:00 (ID: 123)",
        ),
        ToolExample(
            description="Reminder that repeats every day",
            user_request="Remind me to take vitamins every morning at 8am",
            parameters={
                "title": "Take daily vitamins",
                "description": "This daily habit supports your overall health and wellness goals.",
                "task_type": "reminder",
                "schedule_type": "daily",
                "schedule_config": {"interval": "daily", "time": "08:00"},
                "next_run_at": "every day at 8am",
                "ai_context": "EXECUTION PLAN: 1) Check user's vitamin schedule and current time 2) Verify if vitamins were already taken today by checking recent logs 3) If not taken, send reminder with vitamin types and benefits 4) If already taken, send confirmation and health tip 5) Track compliance for health monitoring. CONTEXT: User takes daily vitamins as part of health routine. Consistency is important for effectiveness and health benefits.",
                "notification_channels": ["sms"],
                "user_id": 126,
            },
            expected_result="✅ Recurring reminder set: 'Take daily vitamins' every day at 08:00 (ID: 124)",
        ),
        ToolExample(
            description="Work-related reminder that repeats weekly",
            user_request="Remind me about the weekly team meeting every Monday at 2pm",
            parameters={
                "title": "Weekly team meeting - prepare agenda",
                "description": "This weekly meeting keeps the team aligned and helps you stay on top of project progress.",
                "task_type": "reminder",
                "schedule_type": "weekly",
                "schedule_config": {"interval": "weekly", "day": "monday", "time": "14:00"},
                "next_run_at": "every monday at 2pm",
                "ai_context": "EXECUTION PLAN: 1) Check meeting schedule and send reminder 1 hour before 2) Include agenda items and preparation checklist 3) Provide access to previous meeting notes and action items 4) Include team member updates if available 5) Log meeting participation for project tracking. CONTEXT: User participates in weekly team meetings for project coordination. Preparation includes reviewing progress and preparing updates.",
                "notification_channels": ["sms"],
                "user_id": 126,
            },
            expected_result="✅ Weekly work reminder set: 'Weekly team meeting - prepare agenda' every Monday at 14:00 (ID: 125)",
        ),
        ToolExample(
            description="Complex AI-executed task with clarifying questions",
            user_request="Analyze my emails and classify them",
            parameters={
                "title": "Email Inbox Management - Classify Emails",
                "description": "Analyze emails and classify them based on user preferences to help with inbox management.",
                "task_type": "automated_task",
                "schedule_type": "once",
                "next_run_at": "immediately",
                "ai_context": "EXECUTION PLAN: 1) Connect to user's email account (Outlook/Gmail) 2) Fetch last 10 emails 3) Analyze email content, sender reputation, and subject lines 4) Apply classification rules: Important (work, bills, appointments), Useless (spam, promotions) 5) Move emails to appropriate folders 6) Provide clear summary report. CONTEXT: User wants automated email triage with specific criteria - analyze last 10 emails, create Important and Useless folders, use sender reputation and keywords for classification.",
                "notification_channels": ["email"],
                "user_id": 126,
            },
            expected_result="✅ AI task created: 'Email Inbox Management - Classify Emails' (ID: 126)\n\nConversation flow:\nUser: 'Analyze my emails and classify them'\nAI: 'I'd be happy to help you set up an automated email classification task! To create the best solution, I need to ask a few questions:\n1. How many emails should I analyze?\n2. What folders should I create for classification?\n3. What criteria should I use for classification?'\nUser: [provides answers]\nAI: [creates task with detailed ai_context based on answers]",
        ),
        ToolExample(
            description="View all active reminders",
            user_request="Show me all my reminders",
            parameters={
                "status": "active",
                "user_id": 126,
            },
            expected_result="📋 Active reminders (3 found):\n\n⏰ **Call mom** (ID: 123)\n   📅 Next run: 2024-01-15 19:00\n   📝 Status: active\n\n⏰ **Take daily vitamins** (ID: 124)\n   📅 Next run: 2024-01-16 08:00\n   📝 Status: active\n\n⏰ **Weekly team meeting** (ID: 125)\n   📅 Next run: 2024-01-22 14:00\n   📝 Status: active",
        ),
        ToolExample(
            description="Change the time of an existing reminder",
            user_request="Change my mom call reminder to 8pm instead of 7pm",
            parameters={
                "reminder_id": 123,
                "user_id": 126,
                "update_data": {
                    "next_run_at": "8pm today",
                },
            },
            expected_result="✅ Task 123 updated successfully. Updated fields: next_run_at",
        ),
        ToolExample(
            description="Remove a reminder that's no longer needed",
            user_request="Delete my old dentist appointment reminder",
            parameters={
                "reminder_id": 123,
                "user_id": 126,
            },
            expected_result="✅ Reminder 123 deleted successfully",
        ),
    ]

    # Create the metadata object
    metadata = ToolMetadata(
        tool_name="create_reminder",
        tool_version="2.0.0",
        description="SCHEDULED AUTOMATION: Create persistent tasks that run automatically on schedule. Use for recurring automation (e.g., 'create a daily task to filter my emails at 7am'). Tasks are stored in database and run via Celery workers. NOT for conversation-based multi-step operations. IMPORTANT: For complex tasks, ask clarifying questions BEFORE calling this tool to ensure proper configuration.",
        category=ToolCategory.PRODUCTIVITY,
        complexity=ToolComplexity.MODERATE,
        
        # Use cases and examples
        use_cases=use_cases,
        examples=examples,
        
        # Prerequisites
        prerequisites=[
            "Valid user ID",
            "Proper time format",
            "Reminder text",
            "Database access",
        ],
        
        # Related tools
        related_tools=["notification_service", "calendar_integration", "email_tool"],
        complementary_tools=["note_tool", "calendar_tool", "task_management"],
        conflicting_tools=[],
        
        # Performance
        execution_time="1-3 seconds",
        success_rate=0.95,
        rate_limits="10 requests per minute per user",
        retry_strategy="Exponential backoff with 3 retries",
        
        # AI guidance
        ai_instructions="""
        AI Task Scheduler Guidance:
        
        CONTENT CREATION BEST PRACTICES:
        1. Title (3-8 words): Start with action verb, be specific, use positive language
        2. Description: Explain the 'why', include timing context, add motivation
        3. AI Context: Include user intent, emotional context, execution guidance
        4. Task Type: Choose based on context (work, health, personal, automated)
        5. Schedule Type: Match timing needs (once, daily, weekly, monthly, custom)
        6. Notification Channels: Tailor content length to delivery method
        
        DATABASE SCHEMA ALIGNMENT:
        - Use 'title' for primary reminder content (scannable, action-focused)
        - Use 'description' for additional context and motivation
        - Use 'ai_context' for detailed AI execution guidance
        - Use 'task_type' to categorize based on content complexity
        - Use 'schedule_type' to match timing needs
        - Use 'notification_channels' to optimize content length
        
        CONTENT QUALITY CHECKLIST:
        - Title: Action verb, specific, concise, positive
        - Description: Explains why, includes timing, adds motivation
        - AI Context: User intent, emotional context, execution guidance
        - Task Type: Matches content complexity and execution method
        - Schedule Type: Appropriate for content type and user habits
        
        EXECUTION GUIDANCE:
        1. Always validate time strings before creating reminders
        2. Use appropriate task_type based on context (work, health, personal, automated)
        3. Suggest recurring patterns for regular activities
        4. Provide clear confirmation messages with reminder details
        5. Handle time zone considerations for the user
        6. Offer to update existing reminders instead of creating duplicates
        7. Ask for clarification if time format is ambiguous
        8. Keep responses concise but upbeat and encouraging
        
        CLARIFYING QUESTIONS FOR COMPLEX TASKS:
        When a user requests a complex automated task, ask clarifying questions BEFORE calling the create_reminder tool:
        
        1. For EMAIL CLASSIFICATION tasks, ask:
           - "How many emails should I analyze?" (e.g., 5, 10, all unread, last week's emails)
           - "What folders should I create for classification?" (e.g., Important, Interesting, Useless)
           - "What criteria should I use for classification?" (sender reputation, keywords, content analysis)
        
        2. For GROCERY SHOPPING tasks, ask:
           - "What specific items do you need?" (milk, bread, eggs, or general categories)
           - "Which store do you prefer?" (IGA, Metro, local grocery)
           - "What time works best for you?" (morning, afternoon, evening)
        
        3. For WORK MEETING reminders, ask:
           - "What preparation do you need to do?" (agenda review, materials, updates)
           - "How early should I remind you?" (15 min, 1 hour, day before)
           - "What information should I include?" (meeting link, agenda items, attendees)
        
        4. For HEALTH/MEDICATION reminders, ask:
           - "What medication(s) are you taking?" (specific names, dosages)
           - "What dosage information should I include?" (mg, frequency, timing)
           - "Should I track if you've already taken it?" (compliance tracking)
        
        5. For PERSONAL TASK reminders, ask:
           - "What specific items or categories?" (detailed breakdown)
           - "Which day/time works best?" (schedule preferences)
           - "Any special considerations?" (dietary restrictions, budget, location)
        
        6. For RECURRING TASKS, ask:
           - "How often should this run?" (daily, weekly, monthly)
           - "What time works best for you?" (morning, afternoon, evening)
           - "Should it run on weekends too?" (schedule exceptions)
        
        CRITICAL: Ask these questions in the conversation, get user answers, then use those answers to create a properly configured task with detailed ai_context.
        """,
        
        # Parameter guidance
        parameter_guidance={
            "title": "Primary reminder content - 3-8 words, action-focused, positive language",
            "description": "Additional context and motivation - explains why, includes timing",
            "task_type": "Categorize based on context: reminder, automated_task, periodic_task",
            "schedule_type": "Match timing needs: once, daily, weekly, monthly, custom",
            "schedule_config": "JSON config for complex scheduling (intervals, weekdays, etc.)",
            "next_run_at": "When to execute next - supports natural language",
            "ai_context": "Detailed AI execution guidance - user intent, emotional context",
            "notification_channels": "Array of channels: sms, email, push - tailor content length",
            "user_id": "Required for security and personalization",
        },
        
        # Common mistakes
        common_mistakes=[
            "Using vague titles like 'Reminder' or 'Don't forget'",
            "Not providing motivating descriptions",
            "Missing AI context for complex tasks",
            "Using invalid time formats",
            "Not specifying task_type for context",
            "Creating duplicates instead of updating existing reminders",
            "Forgetting to handle time zones",
            "Not providing clear confirmation messages",
            "Making content too verbose or too brief",
        ],
        
        # Best practices
        best_practices=[
            "Create scannable, action-focused titles",
            "Add motivating descriptions that explain the 'why'",
            "Provide rich AI context for complex tasks",
            "Always validate time input before processing",
            "Use descriptive reminder text with positive language",
            "Suggest appropriate task categories and notification channels",
            "Provide clear success/error messages",
            "Handle edge cases gracefully",
            "Offer helpful suggestions for time formats",
            "Keep responses concise but encouraging",
        ],
    )

    return metadata


def create_ai_task_ai_enhancements() -> AIEnhancementManager:
    """Create AI enhancements for the AI task scheduler tools."""
    
    manager = AIEnhancementManager()
    
    # Enhancement 1: Smart Time Parsing
    manager.register_enhancement(
        AIEnhancement(
            enhancement_id="smart_time_parsing",
            tool_name="create_reminder",
            enhancement_type=EnhancementType.PARAMETER_SUGGESTION,
            priority=EnhancementPriority.HIGH,
            title="Smart Time Parsing",
            description="Intelligent parsing of natural language time expressions",
            ai_instructions="""
            When processing time parameters, use these parsing strategies:
            1. Relative times: "in 2 hours", "tomorrow at 3pm", "next week"
            2. Absolute times: "2024-01-15 14:30", "January 15th at 2:30pm"
            3. Recurring patterns: "every day at 8am", "weekdays at 9am", "monthly on the 1st"
            4. Context-aware: "this evening", "next monday", "end of month"
            
            If time format is unclear, ask for clarification with examples.
            """,
            examples=[
                {
                    "input": "remind me in 2 hours",
                    "parsed_time": "2 hours from now",
                    "confidence": 0.9
                },
                {
                    "input": "every weekday at 9am",
                    "parsed_time": "Monday-Friday at 09:00",
                    "confidence": 0.95
                },
                {
                    "input": "next monday at 2pm",
                    "parsed_time": "Next Monday at 14:00",
                    "confidence": 0.9
                }
            ],
            trigger_conditions=["time parameter provided", "natural language time expression"],
            success_criteria=["time parsed correctly", "user confirmation", "reminder scheduled"],
            failure_handling=["ask for clarification", "provide time format examples", "suggest alternatives"]
        )
    )
    
    # Enhancement 2: Context-Aware Task Categorization
    manager.register_enhancement(
        AIEnhancement(
            enhancement_id="context_aware_categorization",
            tool_name="create_reminder",
            enhancement_type=EnhancementType.INTENT_RECOGNITION,
            priority=EnhancementPriority.MEDIUM,
            title="Context-Aware Task Categorization",
            description="Automatically categorize tasks based on content and context",
            ai_instructions="""
            Analyze reminder text and context to suggest appropriate task_type:
            
            Work-related keywords: meeting, deadline, project, team, work, office, client
            → task_type: "reminder" with work context
            
            Health-related keywords: medication, doctor, exercise, workout, health, medical
            → task_type: "reminder" with health context
            
            Personal keywords: family, personal, home, shopping, personal, private
            → task_type: "reminder" with personal context
            
            Complex analysis keywords: analyze, classify, review, evaluate, process
            → task_type: "automated_task"
            
            Default: "reminder"
            
            Always confirm the categorization with the user.
            """,
            examples=[
                {
                    "text": "Team standup meeting at 9am",
                    "suggested_type": "reminder",
                    "context": "work",
                    "confidence": 0.9
                },
                {
                    "text": "Take blood pressure medication",
                    "suggested_type": "reminder",
                    "context": "health",
                    "confidence": 0.95
                },
                {
                    "text": "Call mom for her birthday",
                    "suggested_type": "reminder",
                    "context": "personal",
                    "confidence": 0.8
                },
                {
                    "text": "Analyze last 5 emails and classify them",
                    "suggested_type": "automated_task",
                    "context": "analysis",
                    "confidence": 0.9
                }
            ],
            trigger_conditions=["reminder text provided", "task_type not specified"],
            success_criteria=["appropriate category suggested", "user confirmation", "context applied"],
            failure_handling=["ask user to specify", "provide category options", "use default"]
        )
    )
    
    # Enhancement 3: Content Quality Optimization
    manager.register_enhancement(
        AIEnhancement(
            enhancement_id="content_quality_optimization",
            tool_name="create_reminder",
            enhancement_type=EnhancementType.WORKFLOW_SUGGESTION,
            priority=EnhancementPriority.HIGH,
            title="Content Quality Optimization",
            description="Optimize reminder content for maximum effectiveness",
            ai_instructions="""
            Apply content quality guidelines to create effective reminders:
            
            TITLE OPTIMIZATION:
            - Start with action verb (Call, Review, Take, Follow up)
            - Be specific and clear (3-8 words)
            - Use positive language
            - Avoid vague terms like "Reminder" or "Don't forget"
            
            DESCRIPTION OPTIMIZATION:
            - Explain the 'why' behind the reminder
            - Include timing context
            - Add motivation and benefits
            - Provide background information
            - Keep encouraging and supportive tone
            
            AI CONTEXT OPTIMIZATION:
            - Include user intent and goals
            - Add emotional context and motivation
            - Provide execution guidance for AI
            - Include personal touches
            - Make it feel caring and supportive
            
            Always suggest improvements and ask for user confirmation.
            """,
            examples=[
                {
                    "original_title": "Reminder",
                    "optimized_title": "Call John about project proposal",
                    "improvement": "More specific and action-focused"
                },
                {
                    "original_description": "Don't forget",
                    "optimized_description": "This is important for getting the green light on your Q4 initiative",
                    "improvement": "Explains why and adds motivation"
                },
                {
                    "original_ai_context": "User wants reminder",
                    "optimized_ai_context": "User wants to be reminded to call John about the project proposal. This is important for their Q4 initiative and they have prepared well for this conversation. They need encouragement and confidence.",
                    "improvement": "Rich context with user intent and emotional support"
                }
            ],
            trigger_conditions=["reminder content provided", "content quality issues detected"],
            success_criteria=["content optimized", "user confirmation", "quality improved"],
            failure_handling=["proceed with original", "ask for manual input", "log optimization attempt"]
        )
    )
    
    # Enhancement 4: Recurring Pattern Detection
    manager.register_enhancement(
        AIEnhancement(
            enhancement_id="recurring_pattern_detection",
            tool_name="create_reminder",
            enhancement_type=EnhancementType.WORKFLOW_SUGGESTION,
            priority=EnhancementPriority.MEDIUM,
            title="Recurring Pattern Detection",
            description="Detect and suggest recurring patterns for regular activities",
            ai_instructions="""
            Look for recurring patterns in reminder requests:
            
            Daily patterns: "every day", "daily", "each day"
            Weekly patterns: "every monday", "weekdays", "weekends"
            Monthly patterns: "monthly", "first of month", "last day"
            Custom intervals: "every 2 hours", "every 3 days"
            
            Suggest appropriate schedule_type and provide examples.
            """,
            examples=[
                {
                    "request": "remind me to drink water every 2 hours",
                    "suggested_pattern": "recurring",
                    "schedule": "every 2 hours",
                    "confidence": 0.9
                },
                {
                    "request": "daily medication reminder at 8am",
                    "suggested_pattern": "recurring",
                    "schedule": "every day at 8am",
                    "confidence": 0.95
                }
            ],
            trigger_conditions=["recurring keywords detected", "regular activity mentioned"],
            success_criteria=["pattern detected", "recurring schedule suggested", "user confirmation"],
            failure_handling=["ask for clarification", "provide pattern examples", "suggest one-time reminder"]
        )
    )
    
    # Enhancement 5: Duplicate Prevention
    manager.register_enhancement(
        AIEnhancement(
            enhancement_id="duplicate_prevention",
            tool_name="create_reminder",
            enhancement_type=EnhancementType.ERROR_PREVENTION,
            priority=EnhancementPriority.HIGH,
            title="Duplicate Reminder Prevention",
            description="Prevent creation of duplicate reminders",
            ai_instructions="""
            Before creating a new reminder, check for existing similar reminders:
            
            1. Search existing reminders for similar text
            2. Check for overlapping time ranges
            3. Suggest updating existing reminder instead of creating new one
            4. Show existing reminders to user for confirmation
            
            If duplicates found, ask user if they want to:
            - Update existing reminder
            - Create new reminder anyway
            - Cancel the operation
            """,
            examples=[
                {
                    "new_reminder": "Call dentist tomorrow at 2pm",
                    "existing_reminder": "Call dentist tomorrow at 2:30pm",
                    "action": "suggest_update",
                    "reason": "similar time and text"
                }
            ],
            trigger_conditions=["new reminder request", "similar text detected"],
            success_criteria=["duplicates detected", "user choice provided", "conflict resolved"],
            failure_handling=["proceed with creation", "log potential duplicate", "notify user"]
        )
    )
    
    # Enhancement 6: Smart Notification Channel Selection
    manager.register_enhancement(
        AIEnhancement(
            enhancement_id="smart_notification_channel",
            tool_name="create_reminder",
            enhancement_type=EnhancementType.PARAMETER_SUGGESTION,
            priority=EnhancementPriority.LOW,
            title="Smart Notification Channel Selection",
            description="Suggest appropriate notification channels based on context",
            ai_instructions="""
            Suggest notification channels based on:
            
            Urgent/Important: SMS for immediate attention
            Work-related: Email or in-app for professional context
            Health/Medical: SMS for critical reminders
            Personal: User preference or SMS for convenience
            Recurring: Email for less intrusive notifications
            Complex tasks: Email for detailed information
            
            Consider user preferences and reminder importance.
            """,
            examples=[
                {
                    "reminder": "Important meeting in 30 minutes",
                    "suggested_channel": "sms",
                    "reason": "urgent and time-sensitive"
                },
                {
                    "reminder": "Weekly team report due",
                    "suggested_channel": "email",
                    "reason": "work-related and not urgent"
                },
                {
                    "reminder": "Analyze emails and classify them",
                    "suggested_channel": "email",
                    "reason": "complex task requiring detailed response"
                }
            ],
            trigger_conditions=["channel not specified", "context suggests urgency"],
            success_criteria=["appropriate channel suggested", "user confirmation", "context considered"],
            failure_handling=["use default channel", "ask user preference", "log suggestion"]
        )
    )
    
    return manager


def get_ai_task_metadata() -> ToolMetadata:
    """Get the AI task scheduler metadata."""
    return create_ai_task_metadata()


def get_ai_task_metadata_full() -> tuple[ToolMetadata, AIEnhancementManager]:
    """Get the complete AI task scheduler metadata with enhancements."""
    return create_ai_task_metadata(), create_ai_task_ai_enhancements()
