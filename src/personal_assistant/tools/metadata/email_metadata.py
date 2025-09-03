"""
Email Tool Metadata

This module provides enhanced metadata for the email tool to improve AI understanding.
"""

from .ai_enhancements import AIEnhancementManager, EnhancementPriority, EnhancementType
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
            name="Move Emails Between Folders",
            description="Organize emails by moving them between different folders (Inbox, Archive, Junk, etc.)",
            example_request="Move my recent emails to the Archive folder",
            example_parameters={
                "message_id": "email_message_id",
                "destination_folder": "Archive",
            },
            expected_outcome="Email successfully moved to the specified folder",
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
            description="Check recently sent emails",
            user_request="What was my last email sent?",
            parameters={"count": 1, "batch_size": 10},
            expected_result="Shows the most recent email you sent with subject, recipients, and sent date",
            notes="Useful for tracking communication history and confirming what was sent",
        ),
        ToolExample(
            description="Search emails by criteria",
            user_request="Find emails with 'meeting' in the subject from last week",
            parameters={
                "query": "meeting",
                "count": 20,
                "date_from": "2024-01-15",
                "date_to": "2024-01-22",
            },
            expected_result="List of emails matching the search criteria with subject, sender, and date",
            notes="Powerful search across email content and metadata for finding specific information",
        ),
        ToolExample(
            description="Move email to Archive folder",
            user_request="Move my most recent email to the Archive folder",
            parameters={
                "message_id": "AQMkADAwATZiZmYAZC1iNzYwLWVhMzgtMDACLTAwCgBGAAAD...",
                "destination_folder": "Archive",
            },
            expected_result="Email successfully moved from Inbox to Archive with confirmation message",
            notes="Useful for organizing inbox by archiving read or processed emails",
        ),
        ToolExample(
            description="Move email to Junk folder",
            user_request="Move this spam email to the Junk folder",
            parameters={"message_id": "email_id_here", "destination_folder": "Junk"},
            expected_result="Email moved to Junk folder to help train spam filters",
            notes="Helps organize spam and unwanted emails while keeping inbox clean",
        ),
        ToolExample(
            description="Move email between custom folders",
            user_request="Move this project email to my Work Projects folder",
            parameters={
                "message_id": "email_id_here",
                "destination_folder": "Work Projects",
            },
            expected_result="Email moved to custom Work Projects folder for better organization",
            notes="Supports custom folder names for personalized email organization",
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
            "Use the email tool when users want to send messages, notifications, invitations, "
            "or any form of written communication. Also use it when users want to review "
            "emails they have previously sent, search existing emails, or organize emails by moving them between folders. "
            "Analyze the user's request to determine whether they want to send new emails, review sent emails, "
            "search existing emails, or organize their inbox. "
            "For sending: determine appropriate recipients, subject, and body content. "
            "For reviewing: determine how many sent emails to retrieve and any specific criteria. "
            "For searching: identify search terms, date ranges, and folder preferences. "
            "For organizing: identify which emails to move and to which destination folder."
        ),
        parameter_guidance={
            "to_recipients": "Comma-separated list of valid email addresses",
            "subject": "Clear, concise subject line that summarizes the email content",
            "body": "Professional, well-structured email body with appropriate greeting and closing",
            "is_html": "Set to true for formatted emails, false for plain text",
            "message_id": "Unique identifier of the email message to move",
            "destination_folder": "Target folder name (e.g., 'Archive', 'Junk', 'Deleted Items', or custom folder)",
        },
        common_mistakes=[
            "Sending to invalid email addresses",
            "Missing subject line",
            "Inappropriate tone for business communication",
            "Sending to wrong recipients",
            "Moving emails to wrong folders",
            "Using invalid folder names",
            "Moving emails without user confirmation",
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
                "parameters": "message_id, destination_folder",
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


def get_email_tool_metadata() -> dict:
    """Get the complete email tool metadata for AI consumption."""
    metadata = create_email_tool_metadata()
    return metadata.get_ai_guidance()


def get_email_tool_metadata_full() -> dict:
    """Get the complete email tool metadata including all details."""
    metadata = create_email_tool_metadata()
    return metadata.to_dict()
