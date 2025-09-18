"""
Email Tool Metadata

This module provides enhanced metadata for the email tool to improve AI understanding.
"""

from .ai_enhancements import AIEnhancementManager, EnhancementPriority
from .tool_metadata import (
    ToolCategory,
    ToolComplexity,
    ToolExample,
    ToolMetadata,
    ToolUseCase,
)


def create_email_tool_metadata() -> ToolMetadata:
    """Create comprehensive metadata for the email tool."""

    # Define use cases for the email tool
    use_cases = [
        ToolUseCase(
            name="Send Meeting Invitation",
            description="Send email invitations for meetings and events",
            example_request="Send a meeting invitation to the development team",
            example_parameters={
                "to_recipients": "dev-team@company.com",
                "subject": "Weekly Development Team Meeting",
                "body": "Please join us for our weekly development team meeting on Friday at 2 PM.",
            },
            expected_outcome="Email sent successfully with meeting details",
            success_indicators=["email_sent", "message_id", "recipients_received"],
            failure_modes=["invalid_email", "rate_limited", "service_unavailable"],
            prerequisites=[
                "valid email addresses",
                "meeting details",
                "sender permissions",
            ],
        ),
        ToolUseCase(
            name="Send Status Update",
            description="Send status updates and progress reports",
            example_request="Send a status update to stakeholders about the project",
            example_parameters={
                "to_recipients": "stakeholders@company.com",
                "subject": "Project Status Update - Q1 2024",
                "body": "Here's our quarterly project status update...",
            },
            expected_outcome="Status update email sent to all stakeholders",
            success_indicators=["email_sent", "message_id", "stakeholders_notified"],
            failure_modes=[
                "invalid_recipients",
                "content_too_long",
                "attachment_issues",
            ],
            prerequisites=["stakeholder list", "status content", "project information"],
        ),
        ToolUseCase(
            name="Send Notification",
            description="Send automated notifications and alerts",
            example_request="Send a notification to users about system maintenance",
            example_parameters={
                "to_recipients": "users@company.com",
                "subject": "System Maintenance Notification",
                "body": "Scheduled maintenance will occur on Sunday from 2-4 AM.",
            },
            expected_outcome="Maintenance notification sent to all users",
            success_indicators=["email_sent", "message_id", "users_notified"],
            failure_modes=["bulk_send_failed", "rate_limited", "content_rejected"],
            prerequisites=["user list", "maintenance details", "notification content"],
        ),
        ToolUseCase(
            name="Read Sent Emails",
            description="Access and review emails you have previously sent",
            example_request="Show me the last 5 emails I sent",
            example_parameters={"count": 5, "batch_size": 10},
            expected_outcome="List of recently sent emails with details",
            success_indicators=[
                "emails_retrieved",
                "sent_date",
                "recipients",
                "subject",
            ],
            failure_modes=["access_denied", "no_sent_emails", "api_error"],
            prerequisites=["Microsoft Graph API access", "Sent Items folder access"],
        ),
        ToolUseCase(
            name="Search Emails",
            description="Find specific emails by query, sender, date range, or other criteria",
            example_request="Find emails from John about the project",
            example_parameters={
                "query": "project",
                "count": 20,
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "folder": "inbox",
            },
            expected_outcome="List of emails matching the search criteria",
            success_indicators=["emails_found", "search_results", "filtered_data"],
            failure_modes=["search_failed", "no_results", "invalid_query"],
            prerequisites=[
                "Microsoft Graph API access",
                "Search permissions",
                "Valid search criteria",
            ],
        ),
        ToolUseCase(
            name="Email Classification and Organization",
            description="Automatically categorize and organize emails into appropriate folders based on content, sender, or subject for better inbox management",
            example_request="Classify emails from the last 24 hours into 'Interesting reading', 'important emails', or 'useless emails' folders",
            example_parameters={
                "email_id": "email_message_id",
                "destination_folder": "Important emails",
            },
            expected_outcome="Emails successfully classified and moved to appropriate folders for better organization",
            success_indicators=[
                "email_moved",
                "folder_change_confirmed",
                "success_message",
            ],
            failure_modes=["email_not_found", "invalid_folder", "permission_denied"],
            prerequisites=[
                "Microsoft Graph API access",
                "Valid message ID",
                "Valid destination folder",
            ],
        ),
        ToolUseCase(
            name="List Available Email Folders for Classification",
            description="Get a comprehensive list of all available email folders including standard and custom classification folders. Essential for email organization and classification tasks.",
            example_request="Show me all my email folders so I can classify emails",
            example_parameters={},
            expected_outcome="List of all email folders with names, email counts, and unread counts, including custom classification folders like 'Important emails', 'Interesting reading', 'Useless emails'",
            success_indicators=[
                "folders_retrieved",
                "folder_names",
                "email_counts",
                "unread_counts",
            ],
            failure_modes=["access_denied", "api_error", "no_folders_found"],
            prerequisites=[
                "Microsoft Graph API access",
                "Mail folder read permissions",
            ],
        ),
        ToolUseCase(
            name="Create Custom Email Folders for Classification",
            description="Create new custom email folders for email classification, organization, and management. Essential for setting up classification categories.",
            example_request="Create classification folders like 'Important emails', 'Interesting reading', 'Useless emails'",
            example_parameters={
                "folder_name": "Important emails",
                "parent_folder_id": None,
            },
            expected_outcome="New custom classification folder created successfully with confirmation message",
            success_indicators=[
                "folder_created",
                "folder_id_returned",
                "success_confirmation",
            ],
            failure_modes=["folder_already_exists", "invalid_name", "permission_denied"],
            prerequisites=[
                "Microsoft Graph API access",
                "Mail folder creation permissions",
                "Valid folder name",
            ],
        ),
    ]

    # Define concrete examples
    examples = [
        ToolExample(
            description="Send a simple email to one recipient",
            user_request="Send an email to john@example.com saying 'Hello, how are you?'",
            parameters={
                "to_recipients": "john@example.com",
                "subject": "Hello",
                "body": "Hello, how are you?",
            },
            expected_result="Email sent successfully to john@example.com",
            notes="Simple one-to-one communication",
        ),
        ToolExample(
            description="Send a meeting invitation with multiple recipients",
            user_request="Invite the marketing team to a brainstorming session on Friday at 3 PM",
            parameters={
                "to_recipients": "marketing@company.com, team-lead@company.com",
                "subject": "Marketing Brainstorming Session - Friday 3 PM",
                "body": "Please join us for a brainstorming session to discuss Q2 marketing strategies. Meeting will be held in Conference Room A.",
            },
            expected_result="Meeting invitation sent to marketing team",
            notes="Team communication with specific meeting details",
        ),
        ToolExample(
            description="Send a professional business email",
            user_request="Send a follow-up email to a client about our proposal",
            parameters={
                "to_recipients": "client@business.com",
                "subject": "Follow-up: Project Proposal Discussion",
                "body": "Thank you for taking the time to discuss our project proposal yesterday. I wanted to follow up on the key points we discussed...",
            },
            expected_result="Professional follow-up email sent to client",
            notes="Business communication with formal tone",
        ),
        ToolExample(
            description="Read recent emails from inbox",
            user_request="Show me my recent emails",
            parameters={"count": 10, "batch_size": 10},
            expected_result="List of recent emails from your inbox with subject, sender, date, and preview. Each email includes an ID that can be used for other operations.",
            notes="This is for RECEIVED emails in your inbox. Use get_sent_emails for emails you sent. Email IDs from this response can be used with move_email, delete_email, or get_email_content.",
        ),
        ToolExample(
            description="Search emails by criteria",
            user_request="Find emails with 'meeting' in the subject from last week",
            parameters={
                "search_terms": "meeting",
                "count": 20,
                "date_from": "2024-01-15",
                "date_to": "2024-01-22",
            },
            expected_result="List of emails matching the search criteria with subject, sender, and date",
            notes="Powerful search across email content and metadata for finding specific information. Use 'search_terms' for what you're looking for.",
        ),
        ToolExample(
            description="Search emails by date range",
            user_request="Show me emails from the last 24 hours",
            parameters={
                "search_terms": "received:last 24 hours",
                "count": 20,
            },
            expected_result="List of emails received in the last 24 hours",
            notes="Use 'received:last 24 hours' or 'received:2024-01-01' format in search_terms for date filtering",
        ),
        ToolExample(
            description="Move email to Archive folder",
            user_request="Move my most recent email to the Archive folder",
            parameters={
                "email_id": "AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...",
                "destination_folder": "Archive",
            },
            expected_result="Email successfully moved from Inbox to Archive with confirmation message",
            notes="Useful for organizing inbox by archiving read or processed emails. IMPORTANT: Get email_id from read_emails response first!",
        ),
        ToolExample(
            description="Move email to Junk folder",
            user_request="Move this spam email to the Junk folder",
            parameters={"email_id": "email_id_here", "destination_folder": "Junk"},
            expected_result="Email moved to Junk folder to help train spam filters",
            notes="Helps organize spam and unwanted emails while keeping inbox clean",
        ),
        ToolExample(
            description="Move email between custom folders",
            user_request="Move this project email to my Work Projects folder",
            parameters={
                "email_id": "email_id_here",
                "destination_folder": "Work Projects",
            },
            expected_result="Email moved to custom Work Projects folder for better organization",
            notes="Supports custom folder names for personalized email organization",
        ),
        ToolExample(
            description="List all available email folders",
            user_request="Show me all my email folders",
            parameters={},
            expected_result="Available Email Folders:\n\n• Inbox: 45 emails (3 unread)\n• Sent Items: 120 emails\n• Drafts: 5 emails\n• Archive: 250 emails\n• Junk Email: 12 emails\n• Work Projects: 15 emails (1 unread)",
            notes="Useful for understanding email organization and choosing destination folders for moving emails",
        ),
        ToolExample(
            description="Create a new custom email folder",
            user_request="Create a folder called 'Client Communications' for organizing client emails",
            parameters={
                "folder_name": "Client Communications",
                "parent_folder_id": None,
            },
            expected_result="Successfully created email folder 'Client Communications' with ID: AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...",
            notes="Creates custom folders for better email organization. Folder names must be unique and cannot exceed 255 characters. Use 'folder_name' parameter (not 'display_name')",
        ),
        ToolExample(
            description="Move email to custom folder using display name",
            user_request="Move my most recent email to the 'Interesting reading' folder",
            parameters={
                "email_id": "AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD2SNuFV7IpUmItF3Ul9QufQcAUe2G-IRLgU2lgd5aWSivTAAAAgEMAAAAUe2G-IRLgU2lgd5aWSivTAAJNlKHBgAAAA==",
                "destination_folder": "Interesting reading",
            },
            expected_result="✅ Successfully moved email 'Build your own Deep Agent – New Academy Course' from 'Boîte de réception' to 'Interesting reading'",
            notes="The move_email function automatically resolves custom folder names to their folder IDs. Use the exact folder display name as shown in find_all_email_folders.",
        ),
        ToolExample(
            description="Categorize email by subject and move to appropriate folder",
            user_request="Organize my emails from the last 24 hours into appropriate folders",
            parameters={
                "email_id": "ABC123",
                "destination_folder": "Interesting reading",
            },
            expected_result="✅ Successfully moved email 'Weekly Tech Newsletter' from 'Inbox' to 'Interesting reading'",
            notes="Make categorization decisions based on email subject/title. Only read full content if subject is unclear or ambiguous.",
        ),
        ToolExample(
            description="Classify newsletter email into reading folder",
            user_request="Move newsletter emails to the 'Interesting reading' folder",
            parameters={
                "email_id": "XYZ789",
                "destination_folder": "Interesting reading",
            },
            expected_result="✅ Successfully moved email 'Build your own Deep Agent – New Academy Course' from 'Inbox' to 'Interesting reading'",
            notes="Newsletter and educational content should be moved to 'Interesting reading' folder for later review.",
        ),
        ToolExample(
            description="Classify invoice email as important",
            user_request="Move invoice emails to the 'Important emails' folder",
            parameters={
                "email_id": "INV456",
                "destination_folder": "Important emails",
            },
            expected_result="✅ Successfully moved email 'Invoice #12345 - Payment Due' from 'Inbox' to 'Important emails'",
            notes="Financial documents, invoices, and billing emails should be moved to 'Important emails' folder.",
        ),
        ToolExample(
            description="Classify promotional email as useless",
            user_request="Move promotional emails to the 'Useless emails' folder",
            parameters={
                "email_id": "SPAM123",
                "destination_folder": "Useless emails",
            },
            expected_result="✅ Successfully moved email 'Win $1000 Now!' from 'Inbox' to 'Useless emails'",
            notes="Spam, promotional offers, and marketing emails should be moved to 'Useless emails' folder.",
        ),
        ToolExample(
            description="Delete an email permanently",
            user_request="Delete this spam email permanently",
            parameters={
                "email_id": "AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...",
            },
            expected_result="Email deleted successfully",
            notes="Permanently removes the email from your account. This action cannot be undone. Get email_id from read_emails or search_emails first.",
        ),
        ToolExample(
            description="Read full content of a specific email",
            user_request="Show me the full content of this email",
            parameters={
                "email_id": "AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...",
            },
            expected_result="Full email content including subject, sender, recipients, date, and complete body text",
            notes="Retrieves the complete email content including HTML body. Get email_id from read_emails or search_emails first.",
        ),
        ToolExample(
            description="Check recently sent emails",
            user_request="Show me my last 5 sent emails",
            parameters={
                "count": 5,
                "batch_size": 10,
            },
            expected_result="List of your most recent sent emails with recipients, subject, and sent date",
            notes="Useful for tracking what you've sent and confirming email delivery. Different from read_emails which shows received emails.",
        ),
        ToolExample(
            description="Search emails by sender",
            user_request="Find all emails from john@example.com",
            parameters={
                "search_terms": "from:john@example.com",
                "count": 20,
            },
            expected_result="List of all emails from john@example.com with subject, date, and preview",
            notes="Use 'from:email@domain.com' format in search_terms to search by sender. Case-insensitive search.",
        ),
        ToolExample(
            description="Search emails by subject keywords",
            user_request="Find emails about 'project proposal'",
            parameters={
                "search_terms": "project proposal",
                "count": 15,
            },
            expected_result="List of emails containing 'project proposal' in subject or body",
            notes="Searches across subject lines and email body content for the specified keywords in search_terms.",
        ),
        ToolExample(
            description="Complete email management workflow",
            user_request="Help me organize my emails: find emails from last week, create a 'Last Week' folder, and move them there",
            parameters={
                "step1": "search_emails with search_terms 'received:last 7 days'",
                "step2": "create_email_folder with folder_name 'Last Week'", 
                "step3": "move_email for each email found",
            },
            expected_result="Emails from last week organized into a new 'Last Week' folder",
            notes="This shows how multiple email tools work together: search → create folder → move emails. Always get email_id from search results before moving.",
        ),
    ]

    # Create the metadata
    metadata = ToolMetadata(
        tool_name="email_tool",
        tool_version="1.0.0",
        description="Send and manage emails via Microsoft Graph integration",
        category=ToolCategory.COMMUNICATION,
        complexity=ToolComplexity.MODERATE,
        use_cases=use_cases,
        examples=examples,
        prerequisites=[
            "Microsoft Graph API access",
            "Valid sender email address",
            "Recipient email addresses",
            "Email content (subject and body)",
        ],
        related_tools=["calendar_tool", "reminder_tool"],
        complementary_tools=["calendar_tool", "notion_tool"],
        conflicting_tools=[],
        execution_time="2-5 seconds",
        success_rate=0.95,
        rate_limits="100 emails per hour",
        retry_strategy="Retry failed sends with exponential backoff",
        ai_instructions=(
            "Use the email tool for sending emails, reading sent emails, searching emails, organizing emails, listing folders, or creating folders. "
            "CRITICAL: Always use the exact parameter names from the tool schema: 'to_recipients' (not 'to'), 'subject', 'body', 'is_html'. "
            "For sending: use 'to_recipients' as comma-separated string, 'subject' as string, 'body' as string. "
            "For reading: use 'count' and 'batch_size' parameters. "
            "For searching: use 'query', 'count', 'date_from', 'date_to', 'folder' parameters. "
            "For organizing: use 'email_id' and 'destination_folder' parameters. "
            "For listing folders: use find_all_email_folders with no parameters to see all available folders. "
            "For creating folders: use 'folder_name' parameter (required) and 'parent_folder_id' parameter (optional). "
            "📧 EMAIL CATEGORIZATION: When organizing emails, prioritize decisions based on SUBJECT/TITLE first. Only read full content if subject is unclear or ambiguous. "
            "PROCESS ALL EMAILS: When filtering emails, you must categorize and move ALL emails found in the search results, not just a few. "
            "HANDLE AMBIGUITY: If email classification is unclear, ask for clarification: 'Should I classify emails about [topic] into [folder1] or [folder2]?' "
            "CONFIRMATION QUESTIONS: When multiple folders match criteria, ask: 'Which folder should I use for [email type]?' "
            "CRITICAL WORKFLOW: When asked to move/delete/reply to 'most recent email': "
            "1. Call read_emails ONCE to get the email list with IDs (🆔 ID: xyz) "
            "2. Extract the email_id from the response "
            "3. Use that email_id directly in move_email/delete_email/get_email_content "
            "4. DO NOT call read_emails again - you already have the email_id!"
            "\n\nFOLDER WORKFLOW: When user asks about folders or wants to move emails: "
            "1. Use find_all_email_folders to show available folders "
            "2. Let user choose the destination folder from the list "
            "3. Use the exact folder name in move_email destination_folder parameter"
            "\n\nFOLDER CREATION WORKFLOW: When user wants to create a new folder: "
            "1. Use create_email_folder with the desired folder_name "
            "2. Confirm the folder was created successfully "
            "3. Optionally use find_all_email_folders to show the updated folder list"
            "\n\nEMAIL ID EXTRACTION: When extracting email IDs from search_emails or read_emails responses: "
            "1. Look for the pattern '🆔 ID: [email_id]' in the formatted response "
            "2. Extract ONLY the email_id part (the long alphanumeric string) "
            "3. Do NOT include '🆔 ID:' prefix when using the ID in move_email/delete_email "
            "4. Example: If response shows '🆔 ID: AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...', use 'AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...'"
            "\n\nCUSTOM FOLDER HANDLING: The move_email function now automatically handles custom folders: "
            "1. Standard folders (Archive, Junk, Deleted Items) work with their display names "
            "2. Custom folders (like 'Interesting reading', 'important emails') are automatically resolved to their folder IDs "
            "3. If a custom folder doesn't exist, you'll get a clear error message "
            "4. No need to manually look up folder IDs - just use the folder display name"
            "\n\nTASK COMPLETION: ALWAYS check conversation history first! "
            "If you already moved/deleted/sent an email, provide FinalAnswer immediately. "
            "Look for '✅ Successfully moved email' or similar success messages. "
            "NEVER repeat completed actions!"
        ),
        parameter_guidance={
            "to_recipients": "CRITICAL: Use 'to_recipients' (not 'to') - Comma-separated list of valid email addresses",
            "subject": "Clear, concise subject line that summarizes the email content",
            "body": "Professional, well-structured email body with appropriate greeting and closing",
            "is_html": "Set to true for formatted emails, false for plain text",
            "email_id": "Unique identifier of the email message to move",
            "destination_folder": "Target folder name (e.g., 'Archive', 'Junk', 'Deleted Items', or custom folder)",
            "find_all_email_folders": "No parameters required - returns list of all available folders with email counts",
            "folder_name": "Name of the new folder to create (required, max 255 characters, must be unique)",
            "parent_folder_id": "ID of the parent folder (optional, defaults to root if not specified)",
        },
        common_mistakes=[
            "Using 'to' instead of 'to_recipients' parameter name",
            "Sending to invalid email addresses",
            "Missing subject line",
            "Inappropriate tone for business communication",
            "Sending to wrong recipients",
            "Moving emails to wrong folders",
            "Using invalid folder names",
            "Moving emails without user confirmation",
            "Calling read_emails multiple times when you already have the email_id",
            "Not extracting email_id from read_emails response before using move_email/delete_email",
            "Stopping email processing after moving only a few emails instead of all found emails",
            "Not asking for clarification when email classification is ambiguous",
            "Not using available folders from find_all_email_folders for classification decisions",
            "Reading full email content when subject line is sufficient for classification",
            "Not using find_all_email_folders before moving emails to unknown folders",
            "Guessing folder names instead of checking available folders first",
            "Creating folders with duplicate names",
            "Using folder names that are too long (over 255 characters)",
            "Creating folders without checking if they already exist",
            "Including '🆔 ID:' prefix when extracting email IDs from formatted responses",
            "Using malformed email IDs that include formatting characters",
            "Assuming custom folder names won't work with move_email function",
            "Not understanding that move_email automatically resolves custom folder names to IDs",
        ],
        best_practices=[
            "Always include a clear subject line",
            "Use professional tone and language",
            "Proofread content before sending",
            "Verify recipient email addresses",
            "Include appropriate greeting and closing",
            "Confirm folder destination before moving emails",
            "Use standard folder names (Archive, Junk, Deleted Items)",
            "Verify email ID before moving to prevent errors",
            "Extract email_id from read_emails response and reuse it for move_email/delete_email",
            "Call read_emails only once when you need the email_id for subsequent operations",
            "Use find_all_email_folders to show available folders before moving emails",
            "Let users choose from actual folder names rather than guessing",
            "Show folder statistics (email counts, unread counts) to help users decide",
            "Check existing folders before creating new ones to avoid duplicates",
            "Use descriptive folder names that clearly indicate their purpose",
            "For email classification: prioritize subject/title analysis over content reading",
            "Process ALL emails found in search results, not just a few",
            "Ask for clarification when email classification is ambiguous",
            "Use consistent classification rules: newsletters→'Interesting reading', invoices→'Important emails', spam→'Useless emails'",
            "Count progress when processing multiple emails: 'Processed 5/20 emails'",
            "Only declare task complete when ALL emails have been processed",
            "Confirm folder creation with user before proceeding",
            "Show updated folder list after creating new folders",
            "Extract clean email IDs without formatting prefixes (🆔 ID:)",
            "Trust that move_email handles custom folder name resolution automatically",
            "Use exact folder display names as they appear in find_all_email_folders",
            "Handle both standard and custom folders with the same move_email workflow",
        ],
    )

    return metadata


def create_email_ai_enhancements(enhancement_manager: AIEnhancementManager):
    """Create AI enhancements for the email tool."""

    # Parameter suggestion enhancement for recipients
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="email_tool",
        parameter_name="to_recipients",
        suggestion_logic=(
            "Analyze the user's request to identify who should receive the email. "
            "Look for names, roles, teams, or departments mentioned. "
            "Suggest appropriate email addresses based on context."
        ),
        examples=[
            {
                "user_request": "Send an email to the development team",
                "suggested_value": "dev-team@company.com",
                "reasoning": "User mentioned 'development team', suggesting team email alias",
            },
            {
                "user_request": "Email John and Sarah about the project",
                "suggested_value": "john@company.com, sarah@company.com",
                "reasoning": "User mentioned specific names, suggesting individual email addresses",
            },
            {
                "user_request": "Notify stakeholders about the update",
                "suggested_value": "stakeholders@company.com",
                "reasoning": "User mentioned 'stakeholders', suggesting stakeholder distribution list",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )

    # Parameter suggestion enhancement for subject
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="email_tool",
        parameter_name="subject",
        suggestion_logic=(
            "Analyze the user's request to create a clear, professional subject line. "
            "Extract key topics, actions, or time-sensitive information. "
            "Use action verbs and be specific about the email's purpose."
        ),
        examples=[
            {
                "user_request": "Send a meeting invitation for Friday's team sync",
                "suggested_value": "Team Sync Meeting - Friday [Date]",
                "reasoning": "Clear meeting purpose with date for urgency",
            },
            {
                "user_request": "Follow up on the proposal we discussed yesterday",
                "suggested_value": "Follow-up: Project Proposal Discussion",
                "reasoning": "Professional follow-up with clear context",
            },
            {
                "user_request": "Send a reminder about the deadline next week",
                "suggested_value": "Reminder: Project Deadline - [Date]",
                "reasoning": "Urgent reminder with specific deadline",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )

    # Intent recognition enhancement
    enhancement_manager.create_intent_recognition_enhancement(
        tool_name="email_tool",
        intent_patterns=[
            "send email",
            "send an email",
            "email to",
            "send message",
            "notify",
            "invite",
            "follow up",
            "remind",
            "update",
            "contact",
            "reach out",
            "get in touch",
            "send invitation",
            "move email",
            "move to",
            "archive",
            "junk",
            "organize emails",
            "clean inbox",
            "sort emails",
            "file email",
            "put in folder",
            "show folders",
            "list folders",
            "what folders",
            "available folders",
            "email folders",
            "my folders",
            "folder list",
            "see folders",
            "create folder",
            "make folder",
            "new folder",
            "add folder",
            "set up folder",
            "organize with folder",
        ],
        recognition_logic=(
            "Look for email-related verbs and phrases in the user's request. "
            "Consider context clues like recipient mentions, communication purpose, "
            "or urgency indicators. Recognize both direct and indirect email requests. "
            "For organization: look for folder-related terms like 'archive', 'junk', 'move', 'organize'."
        ),
        examples=[
            {
                "user_request": "I need to send an email to the team about the meeting",
                "detected_intent": "email_sending",
                "confidence": "high",
                "reasoning": "Direct mention of 'send an email' with clear purpose",
            },
            {
                "user_request": "Can you notify everyone about the system update?",
                "detected_intent": "email_notification",
                "confidence": "high",
                "reasoning": "Use of 'notify' with 'everyone' suggests broadcast email",
            },
            {
                "user_request": "I want to follow up with the client about our proposal",
                "detected_intent": "email_followup",
                "confidence": "high",
                "reasoning": "Clear follow-up intent with specific recipient and context",
            },
            {
                "user_request": "Move this email to the Archive folder",
                "detected_intent": "email_organization",
                "confidence": "high",
                "reasoning": "Direct mention of 'move' with specific destination folder",
            },
            {
                "user_request": "Clean up my inbox by archiving old emails",
                "detected_intent": "email_organization",
                "confidence": "high",
                "reasoning": "Mentions 'clean up' and 'archiving' indicating organization intent",
            },
            {
                "user_request": "Show me all my email folders",
                "detected_intent": "email_folder_listing",
                "confidence": "high",
                "reasoning": "Direct request to 'show' and 'email folders' indicating folder listing intent",
            },
            {
                "user_request": "What folders do I have for organizing emails?",
                "detected_intent": "email_folder_listing",
                "confidence": "high",
                "reasoning": "Asks 'what folders' and mentions 'organizing emails' indicating folder discovery intent",
            },
            {
                "user_request": "Create a new folder called 'Work Projects' for my work emails",
                "detected_intent": "email_folder_creation",
                "confidence": "high",
                "reasoning": "Direct request to 'create' a 'new folder' with specific name indicating folder creation intent",
            },
            {
                "user_request": "I need to set up a folder for client communications",
                "detected_intent": "email_folder_creation",
                "confidence": "high",
                "reasoning": "Mentions 'set up a folder' indicating folder creation intent with specific purpose",
            },
        ],
        priority=EnhancementPriority.CRITICAL,
    )

    # Parameter suggestion enhancement for destination folder
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="email_tool",
        parameter_name="destination_folder",
        suggestion_logic=(
            "Analyze the user's request to identify the appropriate destination folder. "
            "Look for folder-related terms like 'archive', 'junk', 'delete', 'organize'. "
            "Suggest standard folder names based on the user's intent."
        ),
        examples=[
            {
                "user_request": "Move this email to the archive",
                "suggested_value": "Archive",
                "reasoning": "User mentioned 'archive', suggesting Archive folder",
            },
            {
                "user_request": "Put this spam email in junk",
                "suggested_value": "Junk",
                "reasoning": "User mentioned 'spam' and 'junk', suggesting Junk folder",
            },
            {
                "user_request": "Delete this old email",
                "suggested_value": "Deleted Items",
                "reasoning": "User mentioned 'delete', suggesting Deleted Items folder",
            },
            {
                "user_request": "Organize this email in my Work folder",
                "suggested_value": "Work",
                "reasoning": "User mentioned specific custom folder 'Work'",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )

    # Parameter suggestion enhancement for email ID extraction
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="email_tool",
        parameter_name="email_id",
        suggestion_logic=(
            "When extracting email IDs from search_emails or read_emails responses, "
            "look for the pattern '🆔 ID: [email_id]' and extract ONLY the email_id part. "
            "Do not include the '🆔 ID:' prefix or any formatting characters. "
            "The email_id should be a long alphanumeric string starting with 'AQMk'."
        ),
        examples=[
            {
                "user_request": "Move the email about 'Deep Agent' to Interesting reading",
                "suggested_value": "AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD2SNuFV7IpUmItF3Ul9QufQcAUe2G-IRLgU2lgd5aWSivTAAAAgEMAAAAUe2G-IRLgU2lgd5aWSivTAAJNlKHBgAAAA==",
                "reasoning": "Extract the clean email ID from the formatted response, removing the '🆔 ID:' prefix",
            },
            {
                "user_request": "Delete the most recent email",
                "suggested_value": "AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...",
                "reasoning": "Use the raw email ID without any formatting characters or prefixes",
            },
        ],
        priority=EnhancementPriority.CRITICAL,
    )

    # ERROR LEARNING enhancement - Learn from previous failures
    enhancement_manager.create_error_learning_enhancement(
        tool_name="email_tool",
        description=(
            "CRITICAL: After any email tool execution, ALWAYS verify success and learn from errors. "
            "If the tool returns an error or exception, analyze the failure reason and adapt. "
            "Never assume an email was sent successfully without confirmation. "
            "Use the tool's return value to validate actual success."
        ),
        ai_instructions=(
            "1. ALWAYS check the tool's return value for success/failure\n"
            "2. If failure occurs, analyze the error message and retry with corrections\n"
            "3. If success is claimed, verify by checking the return value\n"
            "4. Never say 'email was sent' without tool confirmation\n"
            "5. Learn from each attempt and improve subsequent tries\n"
            "6. NEVER search the web for email addresses unless explicitly requested\n"
            "7. ALWAYS ask the user for email addresses they haven't provided\n"
            "8. Use conversation to gather missing information before acting"
        ),
        examples=[
            {
                "scenario": "Tool returns error: 'Recipient not found'",
                "action": "Ask user for correct email address - don't guess or search",
                "learning": "Always verify recipient email with user before sending",
            },
            {
                "scenario": "Tool returns success but with warnings",
                "action": "Acknowledge warnings and confirm actual delivery",
                "learning": "Success with warnings may indicate partial delivery issues",
            },
            {
                "scenario": "User says 'Send email to Camille' without email address",
                "action": "Ask: 'What email address should I use for Camille?'",
                "learning": "Never assume or search for email addresses - ask the user",
            },
        ],
    )

    # VALIDATION enhancement - Verify email was actually sent
    enhancement_manager.create_validation_enhancement(
        tool_name="email_tool",
        description=(
            "CRITICAL: After sending an email, validate that it was actually delivered. "
            "Check the tool's return value for delivery confirmation. "
            "If the tool doesn't provide delivery status, ask the user to confirm receipt. "
            "Never assume delivery without verification."
        ),
        ai_instructions=(
            "1. Check tool return value for delivery confirmation\n"
            "2. If no delivery status, ask user to confirm receipt\n"
            "3. Verify recipient email address is correct\n"
            "4. Confirm the right person received the email\n"
            "5. Provide delivery status to user"
        ),
        examples=[
            {
                "scenario": "Tool returns 'Email sent successfully'",
                "action": "Confirm delivery and ask user to verify receipt",
                "validation": "Ask recipient to confirm they received the email",
            },
            {
                "scenario": "Tool returns error or exception",
                "action": "Analyze error, retry with corrections, or ask for help",
                "validation": "Never claim success without tool confirmation",
            },
        ],
    )

    # CONVERSATIONAL GUIDANCE enhancement - Better user interaction
    enhancement_manager.create_conversational_guidance_enhancement(
        tool_name="email_tool",
        description=(
            "CRITICAL: Engage in helpful conversation to gather missing information before sending emails. "
            "Ask clarifying questions, suggest alternatives, and validate information with the user. "
            "Never assume or search for information - always ask the user directly."
        ),
        ai_instructions=(
            "1. ALWAYS ask the user for missing email addresses - never guess or search\n"
            "2. Use conversation to gather complete information before acting\n"
            "3. Ask clarifying questions: 'What email should I use for [Name]?'\n"
            "4. Suggest alternatives: 'Should I use their work email or personal email?'\n"
            "5. Validate information: 'Just to confirm, you want me to email [email] to [recipient]?'\n"
            "6. Be conversational and helpful, not robotic\n"
            "7. If you have access to email history, suggest recent contacts as options\n"
            "8. Ask for confirmation before sending to avoid mistakes"
        ),
        examples=[
            {
                "scenario": "User says 'Send email to Camille'",
                "conversation": "What email address should I use for Camille? Do you have their work email or personal email?",
                "outcome": "User provides email address, then proceed with sending",
            },
            {
                "scenario": "User says 'Email the team about the meeting'",
                "conversation": "Which team members should I include? Do you have a team distribution list, or should I email individuals?",
                "outcome": "User clarifies team composition, then proceed with sending",
            },
            {
                "scenario": "User says 'Send follow-up to client'",
                "conversation": "Which client are you referring to? I can see recent emails to [list recent clients]. Should I use the same email address?",
                "outcome": "User confirms client and email, then proceed with sending",
            },
        ],
    )

    # SMART VALIDATION enhancement - Use email history intelligently
    enhancement_manager.create_validation_enhancement(
        tool_name="email_tool",
        description=(
            "SMART: When user requests to email someone, check if you have access to email history "
            "and suggest recent contacts as options. Help the user choose the right email address "
            "from their recent communications."
        ),
        ai_instructions=(
            "1. If you have access to email history, suggest recent contacts as options\n"
            "2. Say: 'I can see recent emails to [list recent recipients]. Should I use [email]?'\n"
            "3. Help user choose from their existing contacts rather than guessing\n"
            "4. Ask: 'Is this the same [Name] you emailed last week about [topic]?'\n"
            "5. Use context clues to suggest the right person\n"
            "6. Always confirm with user before proceeding\n"
            "7. If no history available, ask user directly for email address"
        ),
        examples=[
            {
                "scenario": "User says 'Email John about the project'",
                "smart_suggestion": "I can see you recently emailed john@company.com about the Q1 review. Should I use that same email address for John?",
                "outcome": "User confirms, then proceed with sending",
            },
            {
                "scenario": "User says 'Send update to the team'",
                "smart_suggestion": "I can see your recent team emails went to team@company.com and dev-team@company.com. Which team should I include?",
                "outcome": "User clarifies team scope, then proceed with sending",
            },
        ],
    )

    # EMAIL CONFIRMATION enhancement - Ask for confirmation before sending
    enhancement_manager.create_validation_enhancement(
        tool_name="email_tool",
        description=(
            "CRITICAL: Before sending ANY email, always ask the user for confirmation with the complete email details. "
            "This prevents mistakes and ensures the user approves the email content before it's sent."
        ),
        ai_instructions=(
            "1. ALWAYS ask for confirmation before sending any email\n"
            "2. Show complete email details: recipient, subject, and body\n"
            '3. Say: \'Just to confirm, you want me to send an email to [email] with subject "[subject]" and body "[body]" - is that correct?\'\n'
            "4. Wait for user confirmation before proceeding\n"
            "5. If user says no or wants changes, ask for corrections\n"
            "6. Only send email after explicit user approval\n"
            "7. Never send email without confirmation"
        ),
        examples=[
            {
                "scenario": "User says 'Send email to John about meeting'",
                "confirmation": "Just to confirm, you want me to send an email to john@company.com with subject 'Meeting Discussion' and body 'Hi John, let's discuss the upcoming meeting. Is that correct?'",
                "outcome": "User confirms, then email is sent",
            },
            {
                "scenario": "User provides email details",
                "confirmation": "Just to confirm, you want me to send an email to camillecouture10@gmail.com with subject 'Testing email functionality' and body 'This email is to test the email functionality.' - is that correct?",
                "outcome": "User confirms, then email is sent",
            },
        ],
    )

    # Workflow suggestion enhancement for email + calendar
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["email_tool", "calendar_tool"],
        workflow_description="Send meeting invitation and create calendar event",
        workflow_steps=[
            {
                "step": 1,
                "tool": "calendar_tool",
                "action": "Create calendar event with meeting details",
                "parameters": "event_title, start_time, end_time, attendees",
            },
            {
                "step": 2,
                "tool": "email_tool",
                "action": "Send meeting invitation email",
                "parameters": "recipients, subject, body with calendar event details",
            },
        ],
        examples=[
            {
                "user_request": "Schedule a team meeting for Friday and send invites",
                "workflow": "calendar_tool -> email_tool",
                "reasoning": "User wants both scheduling and invitation, requiring two tools",
            },
            {
                "user_request": "Set up a client call and notify them via email",
                "workflow": "calendar_tool -> email_tool",
                "reasoning": "Meeting setup requires calendar creation and email notification",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )

    # Workflow suggestion enhancement for email organization
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["email_tool"],
        workflow_description="Read emails and organize them by moving to appropriate folders",
        workflow_steps=[
            {
                "step": 1,
                "tool": "email_tool",
                "action": "Read recent emails to identify which ones to organize",
                "parameters": "count, batch_size",
            },
            {
                "step": 2,
                "tool": "email_tool",
                "action": "Move selected emails to appropriate folders",
                "parameters": "email_id, destination_folder",
            },
        ],
        examples=[
            {
                "user_request": "Move my most recent emails to the Archive folder",
                "workflow": "read_emails -> move_email",
                "reasoning": "User wants to organize recent emails, requiring first reading then moving",
            },
            {
                "user_request": "Clean up my inbox by archiving old emails",
                "workflow": "read_emails -> move_email",
                "reasoning": "Inbox cleanup requires reading emails first, then organizing them",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )

    # Workflow suggestion enhancement for folder listing + email organization
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["email_tool"],
        workflow_description="List available folders and organize emails by moving to appropriate folders",
        workflow_steps=[
            {
                "step": 1,
                "tool": "email_tool",
                "action": "List all available email folders",
                "parameters": "find_all_email_folders (no parameters)",
            },
            {
                "step": 2,
                "tool": "email_tool",
                "action": "Read recent emails to identify which ones to organize",
                "parameters": "count, batch_size",
            },
            {
                "step": 3,
                "tool": "email_tool",
                "action": "Move selected emails to appropriate folders",
                "parameters": "email_id, destination_folder",
            },
        ],
        examples=[
            {
                "user_request": "Show me my folders and help me organize my emails",
                "workflow": "find_all_email_folders -> read_emails -> move_email",
                "reasoning": "User wants to organize emails, requiring first showing folders, then reading emails, then moving them",
            },
            {
                "user_request": "What folders can I move emails to?",
                "workflow": "find_all_email_folders",
                "reasoning": "User specifically asks about available folders, requiring only folder listing",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )

    # Workflow suggestion enhancement for folder creation + organization
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["email_tool"],
        workflow_description="Create new folder and organize emails by moving them to the new folder",
        workflow_steps=[
            {
                "step": 1,
                "tool": "email_tool",
                "action": "Create a new custom email folder",
                "parameters": "folder_name (required), parent_folder_id (optional)",
            },
            {
                "step": 2,
                "tool": "email_tool",
                "action": "List all folders to confirm creation",
                "parameters": "find_all_email_folders (no parameters)",
            },
            {
                "step": 3,
                "tool": "email_tool",
                "action": "Move emails to the new folder",
                "parameters": "email_id, destination_folder",
            },
        ],
        examples=[
            {
                "user_request": "Create a 'Client Communications' folder and move my client emails there",
                "workflow": "create_email_folder -> find_all_email_folders -> move_email",
                "reasoning": "User wants to create a new folder and organize emails, requiring creation, verification, then moving",
            },
            {
                "user_request": "Set up a folder for work projects",
                "workflow": "create_email_folder -> find_all_email_folders",
                "reasoning": "User wants to create a new folder, requiring creation and verification",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )

    # Workflow suggestion enhancement for automated email filtering
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["email_tool"],
        workflow_description="Automated email filtering: search recent emails and categorize them into custom folders using subject-based decisions",
        workflow_steps=[
            {
                "step": 1,
                "tool": "email_tool",
                "action": "Search for emails from the specified time period",
                "parameters": "search_terms='last 24 hours', count=20",
            },
            {
                "step": 2,
                "tool": "email_tool",
                "action": "List available folders to confirm target folders exist",
                "parameters": "find_all_email_folders (no parameters)",
            },
            {
                "step": 3,
                "tool": "email_tool",
                "action": "Categorize emails by SUBJECT/TITLE and move to appropriate folders",
                "parameters": "email_id (extracted from search results), destination_folder (decided by subject analysis)",
                "notes": "Make categorization decisions based on email subject/title. Only use get_email_content if subject is unclear."
            },
        ],
        examples=[
            {
                "user_request": "Filter emails from the last 24 hours into 'Interesting reading', 'important emails', or 'useless emails' folders",
                "workflow": "search_emails -> find_all_email_folders -> move_email (multiple times)",
                "reasoning": "Automated email filtering requires searching recent emails, checking folders, then moving ALL emails based on SUBJECT analysis. Examples: 'Newsletter: Tech Updates' → 'Interesting reading', 'Invoice #12345' → 'important emails', 'Win $1000 Now!' → 'useless emails'. Must process every email found, not just a few.",
            },
            {
                "user_request": "Sort my recent emails into appropriate folders",
                "workflow": "search_emails -> find_all_email_folders -> move_email",
                "reasoning": "Email sorting requires first finding emails, then organizing them into folders based on subject/title analysis",
            },
        ],
        priority=EnhancementPriority.HIGH,
    )


def get_email_tool_metadata() -> dict:
    """Get the complete email tool metadata for AI consumption."""
    metadata = create_email_tool_metadata()
    return metadata.get_ai_guidance()


def get_email_tool_metadata_full() -> dict:
    """Get the complete email tool metadata including all details."""
    metadata = create_email_tool_metadata()
    return metadata.to_dict()
