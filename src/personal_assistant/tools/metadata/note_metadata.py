"""
Note Tool Metadata

This module provides enhanced metadata for the note tool to improve AI understanding.
"""

from .tool_metadata import (
    ToolMetadata, ToolUseCase, ToolExample, ToolCategory, ToolComplexity
)
from .ai_enhancements import (
    AIEnhancementManager, EnhancementType, EnhancementPriority
)


def create_note_tool_metadata() -> ToolMetadata:
    """Create comprehensive metadata for the note tool."""

    # Define use cases for the note tool
    use_cases = [
        ToolUseCase(
            name="Create Meeting Prep Notes",
            description="Create structured notes for meeting preparation and planning",
            example_request="Prepare notes for the team meeting about Q1 goals",
            example_parameters={
                "title": "Q1 Team Meeting Prep",
                "content": "Meeting Date: [Date]\nAgenda:\n- Q1 Goals Review\n- Progress Updates\n- Action Items Discussion\n\nKey Points to Cover:\n- Current status of Q1 objectives\n- Challenges and blockers\n- Resource needs\n\nQuestions to Ask:\n- [Question 1]\n- [Question 2]",
                "tags": ["meeting", "prep", "Q1", "goals"],
                "notebook": "Work Meetings"
            },
            expected_outcome="Structured meeting preparation notes with agenda and key discussion points",
            success_indicators=["note_created",
                                "content_structured", "tags_applied"],
            failure_modes=["content_too_long",
                           "invalid_format", "storage_error"],
            prerequisites=["meeting context",
                           "agenda items", "key discussion points"]
        ),
        ToolUseCase(
            name="Create Project Notes",
            description="Document project progress, ideas, and technical details",
            example_request="Create a note about the new feature implementation plan",
            example_parameters={
                "title": "Feature Implementation Plan",
                "content": "Feature: User Authentication\nRequirements:\n- OAuth 2.0 integration\n- MFA support\n- Session management\n\nImplementation Steps:\n1. Set up OAuth providers\n2. Implement MFA\n3. Add session handling",
                "tags": ["project", "feature", "authentication", "technical"],
                "notebook": "Project Notes"
            },
            expected_outcome="Comprehensive project documentation with implementation details",
            success_indicators=["note_created",
                                "content_detailed", "structure_clear"],
            failure_modes=["content_disorganized",
                           "missing_details", "format_issues"],
            prerequisites=["project requirements",
                           "technical specifications", "implementation plan"]
        ),
        ToolUseCase(
            name="Create Personal Notes",
            description="Capture personal thoughts, reminders, and ideas",
            example_request="Write a note about my weekend plans",
            example_parameters={
                "title": "Weekend Plans",
                "content": "Saturday:\n- Grocery shopping\n- Gym workout\n- Dinner with friends\n\nSunday:\n- Laundry\n- Meal prep\n- Reading time",
                "tags": ["personal", "weekend", "plans"],
                "notebook": "Personal"
            },
            expected_outcome="Personal note with weekend activities and schedule",
            success_indicators=["note_created",
                                "content_personal", "schedule_clear"],
            failure_modes=["content_private",
                           "format_issues", "storage_error"],
            prerequisites=["personal information",
                           "schedule details", "activities"]
        ),
        ToolUseCase(
            name="Create Research Notes",
            description="Document research findings, sources, and insights",
            example_request="Take notes on the AI research paper I just read",
            example_parameters={
                "title": "AI Research Paper Notes",
                "content": "Paper: 'Advances in Large Language Models'\nAuthors: [Author Names]\nPublication: [Journal/Conference]\n\nKey Findings:\n- Improved performance on reasoning tasks\n- Better few-shot learning capabilities\n- Enhanced safety measures\n\nMy Insights:\n- Potential applications in our project\n- Areas for further investigation",
                "tags": ["research", "AI", "LLM", "academic"],
                "notebook": "Research"
            },
            expected_outcome="Comprehensive research notes with findings and personal insights",
            success_indicators=["note_created",
                                "research_documented", "insights_added"],
            failure_modes=["missing_sources",
                           "incomplete_findings", "format_issues"],
            prerequisites=["research material",
                           "key findings", "personal insights"]
        ),
        ToolUseCase(
            name="Create Detailed Explanations",
            description="Create comprehensive notes with multiple paragraphs explaining complex topics using markdown formatting",
            example_request="Give me a brief overview of philosophy with key concepts and thinkers",
            example_parameters={
                "title": "Philosophy Overview and Key Concepts",
                "content": "# Philosophy Overview and Key Concepts\n\nPhilosophy is the **systematic study** of fundamental questions about existence, knowledge, values, reason, mind, and language. It seeks to understand the nature of reality and human experience through critical analysis and logical reasoning.\n\n## Key Branches\n\n- **Metaphysics**: Study of reality and existence\n- **Epistemology**: Study of knowledge and belief\n- **Ethics**: Study of morality and values\n- **Logic**: Study of valid reasoning\n- **Aesthetics**: Study of beauty and art\n\n## Major Thinkers\n\n- **Socrates**: Emphasized questioning and self-examination\n- **Plato**: Founded the Academy and wrote philosophical dialogues\n- **Aristotle**: Developed systematic approaches to logic and ethics\n- **Descartes**: Famous for *'Cogito, ergo sum'* and mind-body dualism\n- **Kant**: Developed deontological ethics and transcendental idealism\n\n## Contemporary Relevance\n\nPhilosophy continues to inform modern debates in science, politics, and ethics. It provides frameworks for critical thinking and helps us navigate complex moral and intellectual challenges in today's world.",
                "tags": ["philosophy", "education", "overview", "concepts", "thinkers"],
                "notebook": "Learning"
            },
            expected_outcome="Comprehensive explanation with multiple paragraphs covering key concepts and details, properly formatted in markdown",
            success_indicators=["note_created",
                                "content_detailed", "paragraphs_structured", "concepts_explained", "markdown_formatted"],
            failure_modes=["content_too_brief",
                           "poor_paragraph_structure", "missing_key_concepts", "poor_markdown_formatting"],
            prerequisites=["topic knowledge",
                           "key concepts to explain", "audience understanding", "markdown formatting knowledge"]
        ),

        ToolUseCase(
            name="Search and Retrieve Notes",
            description="Find existing notes by content, tags, or metadata",
            example_request="Find all my notes about the authentication project",
            example_parameters={
                "query": "authentication",
                "tags": "project,authentication",
                "category": "Project Notes"
            },
            expected_outcome="List of relevant notes matching search criteria",
            success_indicators=["notes_found",
                                "search_relevant", "results_organized"],
            failure_modes=["no_results",
                           "search_failed", "irrelevant_results"],
            prerequisites=["search criteria",
                           "note database", "search permissions"]
        ),
        ToolUseCase(
            name="Update and Edit Notes",
            description="Modify existing notes with new information, corrections, or subtle additions without overwriting entire content",
            example_request="Update my project notes with the latest progress",
            example_parameters={
                "page_id": "page_123",
                "content": "Progress Update - [Date]:\n- OAuth integration completed\n- MFA implementation in progress\n- Session management next week",
                "append_content": True,
                "tags": "progress,update",
                "category": "Project Notes"
            },
            expected_outcome="Note updated with latest information and new tags, preserving existing content",
            success_indicators=["note_updated",
                                "content_added", "tags_updated", "existing_content_preserved"],
            failure_modes=["note_not_found",
                           "update_failed", "permission_denied", "content_overwritten"],
            prerequisites=["existing note",
                           "update content", "edit permissions", "update strategy (append vs replace)"]
        ),
        ToolUseCase(
            name="Organize Notes",
            description="Categorize, tag, and organize notes for better retrieval",
            example_request="Organize my notes by adding proper tags and moving them to the right categories",
            example_parameters={
                "page_id": "page_456",
                "tags": "organized,categorized",
                "category": "Work Projects"
            },
            expected_outcome="Note properly organized with tags and category placement",
            success_indicators=["note_organized",
                                "tags_applied", "category_updated"],
            failure_modes=["organization_failed",
                           "invalid_tags", "category_not_found"],
            prerequisites=["existing note",
                           "organization criteria", "category structure"]
        )
    ]

    # Define concrete examples
    examples = [
        ToolExample(
            description="Create a simple meeting note",
            user_request="Take notes during our team meeting about the new project",
            parameters={
                "title": "Team Meeting - New Project Discussion",
                "content": "Meeting Date: [Current Date]\nAttendees: Team members\n\nDiscussion Points:\n- New project requirements\n- Timeline: 3 months\n- Budget: $50K\n\nAction Items:\n- [ ] Create project plan\n- [ ] Assign team roles\n- [ ] Set up project repository",
                "tags": ["meeting", "project", "planning"],
                "notebook": "Work Meetings"
            },
            expected_result="Structured meeting notes created with discussion points and action items",
            notes="Simple but effective meeting documentation"
        ),
        ToolExample(
            description="Create a technical implementation note",
            user_request="Write down my plan for implementing the new authentication system",
            parameters={
                "title": "Authentication System Implementation",
                "content": "System: User Authentication & Authorization\n\nArchitecture:\n- OAuth 2.0 for external providers\n- JWT tokens for sessions\n- Role-based access control\n\nImplementation Steps:\n1. Set up OAuth providers (Google, Microsoft)\n2. Implement JWT token generation\n3. Add RBAC middleware\n4. Create user management API\n5. Add audit logging\n\nDependencies:\n- Python 3.9+\n- FastAPI framework\n- PostgreSQL database\n\nTimeline: 2 weeks",
                "tags": ["technical", "authentication", "implementation", "planning"],
                "notebook": "Technical Notes"
            },
            expected_result="Detailed technical implementation plan with architecture and timeline",
            notes="Comprehensive technical documentation for development team"
        ),
        ToolExample(
            description="Create a personal reminder note",
            user_request="Write a note to remind me about my dentist appointment next week",
            parameters={
                "title": "Dentist Appointment Reminder",
                "content": "Appointment: Dental Checkup\nDate: [Next Week Date]\nTime: 2:00 PM\nLocation: Dr. Smith's Office - 123 Main St\n\nPreparation:\n- Bring insurance card\n- Arrive 15 minutes early\n- No food 2 hours before\n\nFollow-up:\n- Schedule next appointment\n- Get cleaning recommendations",
                "tags": ["personal", "health", "appointment", "reminder"],
                "notebook": "Personal"
            },
            expected_result="Personal reminder note with appointment details and preparation steps",
            notes="Personal health appointment tracking"
        ),
        ToolExample(
            description="Create a learning note",
            user_request="Take notes on the Python async programming tutorial I watched",
            parameters={
                "title": "Python Async Programming Tutorial",
                "content": "Source: YouTube Tutorial by [Creator]\nDuration: 45 minutes\n\nKey Concepts:\n- async/await syntax\n- Event loops\n- Coroutines\n- asyncio library\n\nCode Examples:\n```python\nasync def fetch_data():\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as response:\n            return await response.json()\n```\n\nPractice Exercises:\n- [ ] Build async web scraper\n- [ ] Create async API client\n- [ ] Implement async database operations\n\nResources:\n- Official Python docs\n- asyncio examples\n- Real Python tutorials",
                "tags": ["learning", "python", "async", "programming", "tutorial"],
                "notebook": "Learning"
            },
            expected_result="Comprehensive learning notes with concepts, examples, and practice exercises",
            notes="Structured learning documentation for skill development"
        ),
        ToolExample(
            description="Search for specific notes",
            user_request="Find all my notes about machine learning projects",
            parameters={
                "query": "machine learning",
                "tags": "ML,AI,project",
                "category": "Projects"
            },
            expected_result="List of machine learning related notes with titles and content previews",
            notes="Efficient note retrieval using search criteria and category filtering"
        ),
        ToolExample(
            description="Update existing note with new information",
            user_request="Add the latest progress to my project implementation note",
            parameters={
                "page_id": "page_789",
                "content": "Progress Update - [Current Date]:\n\nCompleted:\n- [x] OAuth provider setup\n- [x] JWT token implementation\n- [x] Basic RBAC middleware\n\nIn Progress:\n- [ ] User management API\n- [ ] Audit logging system\n\nNext Week:\n- [ ] API testing\n- [ ] Documentation updates\n- [ ] Security review",
                "tags": "progress,update",
                "category": "Project Notes"
            },
            expected_result="Note updated with latest progress and new completion status",
            notes="Iterative note updates to track project progress"
        ),
        ToolExample(
            description="Organize notes with better structure",
            user_request="Reorganize my work notes by adding proper tags and moving them to the right categories",
            parameters={
                "page_id": "page_101",
                "tags": "organized,categorized,work",
                "category": "Work Projects"
            },
            expected_result="Note properly organized with consistent tags and category placement",
            notes="Systematic note organization for better retrieval"
        )
    ]

    # Create the metadata
    metadata = ToolMetadata(
        tool_name="note_tool",
        tool_version="1.0.0",
        description="Create, organize, and manage notes for various purposes including meetings, projects, personal tasks, and research",
        category=ToolCategory.PRODUCTIVITY,
        complexity=ToolComplexity.MODERATE,
        use_cases=use_cases,
        examples=examples,
        prerequisites=[
            "Note content and context",
            "Appropriate title and description",
            "Relevant tags for categorization",
            "Category organization structure"
        ],
        related_tools=["calendar_tool", "reminder_tool", "notion_tool"],
        complementary_tools=["calendar_tool", "email_tool", "project_tool"],
        conflicting_tools=[],
        execution_time="1-3 seconds",
        success_rate=0.98,
        rate_limits="1000 notes per day",
        retry_strategy="Retry failed operations with exponential backoff",
        ai_instructions=(
            "Use the note tool when users want to create, organize, or retrieve notes for any purpose. "
            "This includes meeting notes, project documentation, personal reminders, research findings, "
            "task lists, and any other information they want to capture and organize. "
            "Analyze the user's request to determine the type of note they want to create: "
            "meeting notes, project notes, personal notes, research notes, task notes, etc. "
            "Help structure the content appropriately for the note type. "
            "Suggest relevant tags and categories for better organization. "
            "For existing notes, help with searching, updating, and organizing them. "
            "Always ask for clarification if the note type or content is unclear."
        ),
        parameter_guidance={
            "title": "Clear, descriptive title that summarizes the note content",
            "content": "Well-structured content with appropriate formatting and organization",
            "tags": "Comma-separated tags for easy categorization and retrieval",
            "category": "Appropriate category for organizing related notes",
            "page_id": "Unique identifier of the page to update or organize",
            "query": "Search query to find relevant notes",
            "append_content": "Whether to add new content or replace existing content"
        },
        common_mistakes=[
            "Creating notes without clear titles",
            "Missing relevant tags for categorization",
            "Poor content structure and organization",
            "Not using appropriate categories",
            "Creating duplicate notes",
            "Missing context or important details",
            "Inconsistent formatting across notes"
        ],
        best_practices=[
            "Always include a clear, descriptive title",
            "Use consistent formatting and structure",
            "Apply relevant tags for easy retrieval",
            "Organize notes in appropriate categories",
            "Include context and important details",
            "Use bullet points and lists for clarity",
            "Regularly review and organize existing notes",
            "Update notes with progress and new information"
        ]
    )

    return metadata


def create_note_ai_enhancements(enhancement_manager: AIEnhancementManager):
    """Create AI enhancements for the note tool."""

    # Parameter suggestion enhancement for note titles
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="note_tool",
        parameter_name="title",
        suggestion_logic=(
            "Analyze the user's request to create a clear, descriptive title. "
            "Extract the main topic, purpose, or context of the note. "
            "Use action words and be specific about the note's content."
        ),
        examples=[
            {
                "user_request": "Take notes during our team meeting about the new project",
                "suggested_value": "Team Meeting - New Project Discussion",
                "reasoning": "Clear meeting context with project focus"
            },
            {
                "user_request": "Write down my plan for implementing the authentication system",
                "suggested_value": "Authentication System Implementation Plan",
                "reasoning": "Specific technical implementation with clear purpose"
            },
            {
                "user_request": "Create a note about my weekend plans",
                "suggested_value": "Weekend Plans and Activities",
                "reasoning": "Personal planning with time context"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Parameter suggestion enhancement for note content
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="note_tool",
        parameter_name="content",
        suggestion_logic=(
            "Analyze the user's request to structure the note content appropriately. "
            "Consider the note type (meeting, project, personal, research) and "
            "suggest appropriate formatting and organization. "
            "Include relevant sections and structure for the specific note type."
        ),
        examples=[
            {
                "user_request": "Take meeting notes about Q1 goals",
                "suggested_value": "Meeting Date: [Date]\nAttendees: [List]\n\nDiscussion Points:\n- Q1 Goals Review\n- Progress Updates\n- Challenges Identified\n\nAction Items:\n- [ ] [Action 1]\n- [ ] [Action 2]\n\nNext Steps:\n- [Next meeting date]\n- [Follow-up items]",
                "reasoning": "Structured meeting format with key sections for meetings"
            },
            {
                "user_request": "Document my project implementation plan",
                "suggested_value": "Project: [Project Name]\n\nOverview:\n[Brief description]\n\nRequirements:\n- [Requirement 1]\n- [Requirement 2]\n\nImplementation Steps:\n1. [Step 1]\n2. [Step 2]\n\nTimeline:\n- [Timeline details]\n\nDependencies:\n- [Dependency 1]\n- [Dependency 2]",
                "reasoning": "Project planning format with logical structure"
            },
            {
                "user_request": "Write a note about my learning progress",
                "suggested_value": "Topic: [Learning Topic]\n\nWhat I Learned:\n- [Key concept 1]\n- [Key concept 2]\n\nResources Used:\n- [Resource 1]\n- [Resource 2]\n\nPractice Exercises:\n- [ ] [Exercise 1]\n- [ ] [Exercise 2]\n\nNext Steps:\n- [Next learning goal]",
                "reasoning": "Learning progress format with structured learning tracking"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Parameter suggestion enhancement for tags
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="note_tool",
        parameter_name="tags",
        suggestion_logic=(
            "Analyze the user's request and note content to suggest relevant tags. "
            "Consider the note type, topic, context, and purpose. "
            "Suggest tags that will help with categorization and retrieval. "
            "Use consistent tag naming conventions."
        ),
        examples=[
            {
                "user_request": "Take notes during our team meeting about the new project",
                "suggested_value": ["meeting", "team", "project", "planning"],
                "reasoning": "Meeting context, team involvement, project focus, planning purpose"
            },
            {
                "user_request": "Document my authentication system implementation",
                "suggested_value": ["technical", "authentication", "implementation", "planning", "security"],
                "reasoning": "Technical nature, authentication topic, implementation phase, planning context, security relevance"
            },
            {
                "user_request": "Write a note about my weekend plans",
                "suggested_value": ["personal", "weekend", "plans", "schedule"],
                "reasoning": "Personal nature, weekend timeframe, planning purpose, schedule context"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Intent recognition enhancement
    enhancement_manager.create_intent_recognition_enhancement(
        tool_name="note_tool",
        intent_patterns=[
            "take notes", "write a note", "create a note", "document", "record",
            "note down", "write down", "keep track", "log", "journal",
            "meeting notes", "project notes", "research notes", "learning notes",
            "task notes", "personal notes", "reminder", "to-do", "checklist",
            "search notes", "find notes", "organize notes", "update note",
            "edit note", "add to note", "categorize", "tag", "organize"
        ],
        recognition_logic=(
            "Look for note-related verbs and phrases in the user's request. "
            "Consider context clues like note purpose, content type, or organization needs. "
            "Recognize both direct note creation requests and indirect note-related activities. "
            "For organization: look for terms like 'organize', 'categorize', 'tag', 'search'."
        ),
        examples=[
            {
                "user_request": "I need to take notes during our team meeting",
                "detected_intent": "note_creation",
                "confidence": "high",
                "reasoning": "Direct mention of 'take notes' with clear meeting context"
            },
            {
                "user_request": "Can you help me document this project plan?",
                "detected_intent": "note_creation",
                "confidence": "high",
                "reasoning": "Use of 'document' with project planning context"
            },
            {
                "user_request": "I want to keep track of my learning progress",
                "detected_intent": "note_creation",
                "confidence": "high",
                "reasoning": "Clear tracking intent for learning progress"
            },
            {
                "user_request": "Find all my notes about machine learning",
                "detected_intent": "note_search",
                "confidence": "high",
                "reasoning": "Direct mention of 'find notes' with specific topic"
            },
            {
                "user_request": "Organize my notes by adding better tags",
                "detected_intent": "note_organization",
                "confidence": "high",
                "reasoning": "Mentions 'organize' and 'tags' indicating organization intent"
            }
        ],
        priority=EnhancementPriority.CRITICAL
    )

    # Note type recognition enhancement
    enhancement_manager.create_intent_recognition_enhancement(
        tool_name="note_tool",
        intent_patterns=[
            "meeting", "team", "project", "technical", "implementation",
            "personal", "weekend", "plans", "schedule", "reminder",
            "learning", "tutorial", "research", "study", "education",
            "tasks", "to-do", "checklist", "action items", "progress",
            "ideas", "brainstorming", "creative", "inspiration"
        ],
        recognition_logic=(
            "Analyze the user's request to identify the specific type of note they want to create. "
            "Look for context clues about the note's purpose, content, or intended use. "
            "Recognize common note types: meeting notes, project notes, personal notes, "
            "learning notes, task notes, research notes, etc."
        ),
        examples=[
            {
                "user_request": "Take notes during our team meeting about Q1 goals",
                "detected_type": "meeting_notes",
                "confidence": "high",
                "reasoning": "Mentions 'team meeting' and 'Q1 goals' indicating meeting context"
            },
            {
                "user_request": "Document my authentication system implementation plan",
                "detected_type": "project_notes",
                "confidence": "high",
                "reasoning": "Technical implementation with project planning context"
            },
            {
                "user_request": "Write a note about my weekend plans",
                "detected_type": "personal_notes",
                "confidence": "high",
                "reasoning": "Personal weekend planning indicating personal note type"
            },
            {
                "user_request": "Take notes on the Python tutorial I watched",
                "detected_type": "learning_notes",
                "confidence": "high",
                "reasoning": "Tutorial learning context indicating learning note type"
            },
            {
                "user_request": "Create a checklist of my tasks for this week",
                "detected_type": "task_notes",
                "confidence": "high",
                "reasoning": "Checklist and tasks indicating task note type"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Content structure enhancement
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="note_tool",
        parameter_name="content",
        suggestion_logic=(
            "Based on the detected note type, suggest appropriate content structure. "
            "Meeting notes: include date, attendees, discussion points, action items. "
            "Project notes: include overview, requirements, implementation steps, timeline. "
            "Personal notes: include context, details, reminders, follow-up. "
            "Learning notes: include source, key concepts, examples, practice exercises. "
            "Task notes: include priorities, completion status, deadlines, dependencies."
        ),
        examples=[
            {
                "note_type": "meeting_notes",
                "suggested_structure": "Meeting Date: [Date]\nAttendees: [List]\n\nAgenda:\n- [Topic 1]\n- [Topic 2]\n\nDiscussion Points:\n- [Point 1]\n- [Point 2]\n\nAction Items:\n- [ ] [Action 1] - [Assignee] - [Deadline]\n- [ ] [Action 2] - [Assignee] - [Deadline]\n\nNext Meeting:\n- [Date] - [Topics to discuss]",
                "reasoning": "Standard meeting format with all essential meeting elements"
            },
            {
                "note_type": "project_notes",
                "suggested_structure": "Project: [Project Name]\n\nOverview:\n[Brief description and objectives]\n\nRequirements:\n- [Requirement 1]\n- [Requirement 2]\n\nImplementation Plan:\n1. [Phase 1] - [Timeline]\n2. [Phase 2] - [Timeline]\n\nDependencies:\n- [Dependency 1]\n- [Dependency 2]\n\nRisks & Mitigation:\n- [Risk 1]: [Mitigation strategy]\n- [Risk 2]: [Mitigation strategy]",
                "reasoning": "Comprehensive project planning structure with risk management"
            },
            {
                "note_type": "learning_notes",
                "suggested_structure": "Topic: [Learning Topic]\n\nSource: [Resource/Instructor]\n\nKey Concepts:\n- [Concept 1]: [Explanation]\n- [Concept 2]: [Explanation]\n\nExamples:\n[Code examples or practical examples]\n\nPractice Exercises:\n- [ ] [Exercise 1]\n- [ ] [Exercise 2]\n\nQuestions & Clarifications:\n- [Question 1]\n- [Question 2]\n\nNext Steps:\n- [Next learning goal]\n- [Resources to explore]",
                "reasoning": "Structured learning format with practical application focus"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Category suggestion enhancement
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="note_tool",
        parameter_name="category",
        suggestion_logic=(
            "Analyze the note type and content to suggest appropriate category placement. "
            "Work-related notes: Work, Projects, Meetings, Technical. "
            "Personal notes: Personal, Health, Finance, Travel. "
            "Learning notes: Learning, Education, Skills, Research. "
            "Task notes: Tasks, To-Do, Action Items, Planning. "
            "Suggest standard category names or custom ones based on context."
        ),
        examples=[
            {
                "note_type": "meeting_notes",
                "suggested_category": "Work Meetings",
                "reasoning": "Meeting notes belong in dedicated meetings category"
            },
            {
                "note_type": "project_notes",
                "suggested_category": "Work Projects",
                "reasoning": "Project documentation belongs in projects category"
            },
            {
                "note_type": "personal_notes",
                "suggested_category": "Personal",
                "reasoning": "Personal notes belong in personal category"
            },
            {
                "note_type": "learning_notes",
                "suggested_category": "Learning",
                "reasoning": "Learning notes belong in dedicated learning category"
            },
            {
                "note_type": "task_notes",
                "suggested_category": "Tasks & Planning",
                "reasoning": "Task notes belong in tasks and planning category"
            }
        ],
        priority=EnhancementPriority.MEDIUM
    )

    # Workflow suggestion enhancement for note + calendar
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["note_tool", "calendar_tool"],
        workflow_description="Create meeting notes and schedule follow-up calendar events",
        workflow_steps=[
            {
                "step": 1,
                "tool": "note_tool",
                "action": "Create meeting notes with action items and follow-up tasks",
                "parameters": "title, content, tags, notebook"
            },
            {
                "step": 2,
                "tool": "calendar_tool",
                "action": "Schedule follow-up meetings or deadline reminders",
                "parameters": "event_title, start_time, end_time, attendees"
            }
        ],
        examples=[
            {
                "user_request": "Take meeting notes and schedule our next team sync",
                "workflow": "note_tool -> calendar_tool",
                "reasoning": "User wants both meeting documentation and follow-up scheduling"
            },
            {
                "user_request": "Document our project plan and set milestone reminders",
                "workflow": "note_tool -> calendar_tool",
                "reasoning": "Project planning requires both documentation and timeline reminders"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Workflow suggestion enhancement for note + reminder
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["note_tool", "reminder_tool"],
        workflow_description="Create task notes and set up reminder notifications",
        workflow_steps=[
            {
                "step": 1,
                "tool": "note_tool",
                "action": "Create task notes with deadlines and priorities",
                "parameters": "title, content, tags, category"
            },
            {
                "step": 2,
                "tool": "reminder_tool",
                "action": "Set up reminder notifications for task deadlines",
                "parameters": "reminder_text, due_date, priority, notification_type"
            }
        ],
        examples=[
            {
                "user_request": "Create a task list and remind me about deadlines",
                "workflow": "note_tool -> reminder_tool",
                "reasoning": "Task management requires both documentation and deadline reminders"
            },
            {
                "user_request": "Write down my goals and set progress check reminders",
                "workflow": "note_tool -> reminder_tool",
                "reasoning": "Goal tracking requires both documentation and progress reminders"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Note organization enhancement
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["note_tool"],
        workflow_description="Search existing notes and organize them with better structure",
        workflow_steps=[
            {
                "step": 1,
                "tool": "note_tool",
                "action": "Search for existing notes that need organization",
                "parameters": "query, tags, category"
            },
            {
                "step": 2,
                "tool": "note_tool",
                "action": "Update and organize notes with better tags and structure",
                "parameters": "page_id, content, tags, category"
            }
        ],
        examples=[
            {
                "user_request": "Find and organize my project notes with better tags",
                "workflow": "search_notes -> organize_notes",
                "reasoning": "Note organization requires first finding then updating existing notes"
            },
            {
                "user_request": "Clean up my meeting notes and categorize them properly",
                "workflow": "search_notes -> organize_notes",
                "reasoning": "Note cleanup requires finding then reorganizing existing notes"
            }
        ],
        priority=EnhancementPriority.MEDIUM
    )


def get_note_tool_metadata() -> dict:
    """Get the complete note tool metadata for AI consumption."""
    metadata = create_note_tool_metadata()
    return metadata.get_ai_guidance()


def get_note_tool_metadata_full() -> dict:
    """Get the complete note tool metadata including all details."""
    metadata = create_note_tool_metadata()
    return metadata.to_dict()
