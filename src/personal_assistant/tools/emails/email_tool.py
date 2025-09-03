from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

from personal_assistant.config.logging_config import get_logger
from personal_assistant.tools.base import Tool
from personal_assistant.utils.text_cleaner import clean_html_content

# Import email-specific error handling
from .email_error_handler import EmailErrorHandler
from .email_internal import (
    build_email_headers,
    build_email_message_data,
    build_email_params,
    clean_recipients_string,
    format_delete_email_response,
    format_email_content_response,
    format_email_list_response,
    format_error_response,
    format_move_email_response,
    format_send_email_response,
    format_success_response,
    get_environment_error_message,
    get_token_expiration,
    handle_email_not_found,
    handle_http_response,
    is_token_valid,
    parse_email_content_response,
    parse_email_response,
    validate_body,
    validate_email_parameters,
    validate_environment_variables,
    validate_message_id,
    validate_recipients,
    validate_subject,
)
from .ms_graph import get_access_token


class EmailTool:
    def __init__(self):
        load_dotenv()
        self.ms_graph_url = "https://graph.microsoft.com/v1.0"
        self._access_token = None
        self._token_expires_at = None
        self.scopes = ["Mail.Read", "Mail.ReadWrite", "Mail.Send", "User.Read"]
        self.logger = get_logger("tools.emails")
        self._initialize_token()

        # Create individual tools
        self.read_emails_tool = Tool(
            name="read_emails",
            func=self.get_emails,
            description="Read recent emails from your inbox",
            parameters={
                "count": {
                    "type": "integer",
                    "description": "Number of emails to fetch",
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Number of emails per batch (default: 10)",
                },
            },
        )

        self.send_email_tool = Tool(
            name="send_email",
            func=self.send_email,
            description="Send an email to one or more recipients",
            parameters={
                "to_recipients": {
                    "type": "string",
                    "description": "Comma-separated list of email addresses to send to",
                },
                "subject": {
                    "type": "string",
                    "description": "Subject line of the email",
                },
                "body": {"type": "string", "description": "Body content of the email"},
                "is_html": {
                    "type": "boolean",
                    "description": "Whether the body is HTML format (default: false)",
                },
            },
        )

        self.delete_email_tool = Tool(
            name="delete_email",
            func=self.delete_email,
            description="Delete an email by its ID",
            parameters={
                "message_id": {
                    "type": "string",
                    "description": "The ID of the email message to delete",
                }
            },
        )

        self.get_email_content_tool = Tool(
            name="get_email_content",
            func=self.get_email_content,
            description="Get the full content of a specific email by its ID",
            parameters={
                "message_id": {
                    "type": "string",
                    "description": "The ID of the email message to get content from",
                }
            },
        )

        self.get_sent_emails_tool = Tool(
            name="get_sent_emails",
            func=self.get_sent_emails,
            description="Read recent emails you have sent",
            parameters={
                "count": {
                    "type": "integer",
                    "description": "Number of sent emails to fetch (default: 10)",
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Number of emails per batch (default: 10)",
                },
            },
        )

        self.search_emails_tool = Tool(
            name="search_emails",
            func=self.search_emails,
            description="Search emails by query, sender, date range, or other criteria. Uses Microsoft Graph $search parameter to search in subject, sender email, sender name, and email body content natively.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query (keywords, sender email, subject terms, body content - all searched natively by Microsoft Graph API)",
                },
                "count": {
                    "type": "integer",
                    "description": "Maximum number of emails to return (default: 20)",
                },
                "date_from": {
                    "type": "string",
                    "description": "Start date for search (YYYY-MM-DD format, optional)",
                },
                "date_to": {
                    "type": "string",
                    "description": "End date for search (YYYY-MM-DD format, optional)",
                },
                "folder": {
                    "type": "string",
                    "description": "Folder to search in (inbox, sentitems, drafts, etc., default: inbox)",
                },
            },
        )

        self.move_email_tool = Tool(
            name="move_email",
            func=self.move_email,
            description="Move an email from one folder to another folder (e.g., from Inbox to Archive, or between custom folders)",
            parameters={
                "message_id": {
                    "type": "string",
                    "description": "The ID of the email message to move",
                },
                "destination_folder": {
                    "type": "string",
                    "description": "Destination folder name (e.g., 'Archive', 'Junk', 'Deleted Items', or custom folder name)",
                },
            },
        )

    def _clean_html_content(self, html_content: str) -> str:
        """Extract clean text content from HTML, removing styling and formatting"""
        # Use the new text cleaning utility
        return clean_html_content(html_content)

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired"""
        return is_token_valid(self._access_token, self._token_expires_at)

    def _initialize_token(self):
        """Initialize the access token using environment variables"""
        is_valid, application_id, client_secret = validate_environment_variables()

        if not is_valid:
            raise ValueError(get_environment_error_message())

        self._access_token = get_access_token(
            application_id, client_secret, self.scopes
        )
        # Set expiration (assuming 1 hour from now)
        self._token_expires_at = get_token_expiration()

    def _get_valid_token(self) -> str:
        """Get a valid token, refreshing if necessary"""
        if self._is_token_valid():
            return self._access_token

        # Token expired or missing, get new one
        self._initialize_token()
        return self._access_token

    async def get_emails(self, count: int, batch_size: int = 10) -> str:
        """
        Read recent emails with improved error handling and token management
        """
        try:
            # Validate parameters using internal functions
            # Ensure count and batch_size are integers (handle float values from LLM)
            count = int(count) if count else 10
            batch_size = int(batch_size) if batch_size else 10

            count, batch_size = validate_email_parameters(count, batch_size)

            token = self._get_valid_token()
            headers = build_email_headers(token)
            emails = []

            # Reuse the pagination logic
            for i in range(0, count, batch_size):
                params = build_email_params(
                    top=min(batch_size, count - i),
                    select="id,subject,bodyPreview,receivedDateTime,from,isDraft",
                    skip=i,
                    orderby="receivedDateTime desc",
                )

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.ms_graph_url}/me/messages",
                        headers=headers,
                        params=params,
                    )

                    if response.status_code != 200:
                        return EmailErrorHandler.handle_email_error(
                            Exception(f"HTTP {response.status_code}: {response.text}"),
                            "get_emails",
                            {"count": count, "batch_size": batch_size},
                        )

                    for mail in response.json().get("value", []):
                        if not mail.get("isDraft"):
                            emails.append(parse_email_response(mail))

                    if len(emails) >= count:
                        break

            # Use formatting function for clean user output
            return format_email_list_response(emails[:count], count)

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e, "get_emails", {"count": count, "batch_size": batch_size}
            )

    async def send_email(
        self, to_recipients: str, subject: str, body: str, is_html: bool = False
    ) -> Dict[str, Any]:
        """Send an email to one or more recipients"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_recipients(to_recipients)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "send_email",
                    {
                        "to_recipients": to_recipients,
                        "subject": subject,
                        "body": body,
                        "is_html": is_html,
                    },
                )

            is_valid, error_msg = validate_subject(subject)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "send_email",
                    {
                        "to_recipients": to_recipients,
                        "subject": subject,
                        "body": body,
                        "is_html": is_html,
                    },
                )

            is_valid, error_msg = validate_body(body)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "send_email",
                    {
                        "to_recipients": to_recipients,
                        "subject": subject,
                        "body": body,
                        "is_html": is_html,
                    },
                )

            token = self._get_valid_token()
            headers = build_email_headers(token, "application/json")

            # Parse and clean recipients
            recipients = clean_recipients_string(to_recipients)

            # Build email message data
            email_data = build_email_message_data(subject, body, recipients, is_html)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ms_graph_url}/me/sendMail", headers=headers, json=email_data
                )

                if response.status_code == 202:  # Accepted
                    return format_send_email_response(
                        True,
                        f"Email sent successfully to {to_recipients}",
                        to_recipients,
                    )
                else:
                    return EmailErrorHandler.handle_email_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "send_email",
                        {
                            "to_recipients": to_recipients,
                            "subject": subject,
                            "body": body,
                            "is_html": is_html,
                        },
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e,
                "send_email",
                {
                    "to_recipients": to_recipients,
                    "subject": subject,
                    "body": body,
                    "is_html": is_html,
                },
            )

    async def delete_email(self, message_id: str) -> Dict[str, Any]:
        """Delete an email by its ID"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_message_id(message_id)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg), "delete_email", {"message_id": message_id}
                )

            token = self._get_valid_token()
            headers = build_email_headers(token)

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.ms_graph_url}/me/messages/{message_id}", headers=headers
                )

                if response.status_code == 204:  # No content on successful deletion
                    return format_delete_email_response(
                        True,
                        f"Successfully deleted email with ID: {message_id}",
                        message_id,
                    )
                elif response.status_code == 404:
                    return handle_email_not_found(message_id)
                else:
                    return EmailErrorHandler.handle_email_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "delete_email",
                        {"message_id": message_id},
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e, "delete_email", {"message_id": message_id}
            )

    async def get_email_content(self, message_id: str) -> Dict[str, Any]:
        """Get the full content of a specific email by its ID"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_message_id(message_id)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "get_email_content",
                    {"message_id": message_id},
                )

            token = self._get_valid_token()
            headers = build_email_headers(token)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/messages/{message_id}",
                    headers=headers,
                    params=build_email_params(
                        top=1,
                        select="id,subject,body,receivedDateTime,from,toRecipients",
                    ),
                )

                if response.status_code == 200:
                    mail = response.json()
                    raw_body = mail.get("body", {}).get("content", "")
                    clean_body = self._clean_html_content(raw_body)

                    # Use formatting function for clean user output
                    return format_email_content_response(
                        parse_email_content_response(mail, clean_body)
                    )
                elif response.status_code == 404:
                    return handle_email_not_found(message_id)
                else:
                    return EmailErrorHandler.handle_email_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "get_email_content",
                        {"message_id": message_id},
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e, "get_email_content", {"message_id": message_id}
            )

    async def get_sent_emails(self, count: int = 10, batch_size: int = 10) -> str:
        """
        Read recent emails you have sent with improved error handling and token management
        """
        try:
            # Validate parameters using internal functions
            # Ensure count and batch_size are integers (handle float values from LLM)
            count = int(count) if count else 10
            batch_size = int(batch_size) if batch_size else 10

            count, batch_size = validate_email_parameters(count, batch_size)

            token = self._get_valid_token()
            headers = build_email_headers(token)
            sent_emails = []

            # Use Microsoft Graph to get sent emails from the Sent Items folder
            for i in range(0, count, batch_size):
                params = build_email_params(
                    top=min(batch_size, count - i),
                    select="id,subject,bodyPreview,receivedDateTime,from,toRecipients,isDraft",
                    skip=i,
                    orderby="sentDateTime desc",  # Order by when they were sent
                )

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.ms_graph_url}/me/mailFolders/SentItems/messages",
                        headers=headers,
                        params=params,
                    )

                    if response.status_code != 200:
                        return EmailErrorHandler.handle_email_error(
                            Exception(f"HTTP {response.status_code}: {response.text}"),
                            "get_sent_emails",
                            {"count": count, "batch_size": batch_size},
                        )

                    batch_data = response.json()
                    batch_emails = batch_data.get("value", [])

                    for email in batch_emails:
                        # Format sent email data
                        email_info = {
                            "id": email.get("id"),
                            "subject": email.get("subject", "No Subject"),
                            "body_preview": email.get(
                                "bodyPreview", "No preview available"
                            ),
                            "sent_date": email.get("sentDateTime"),
                            "to_recipients": [
                                recipient.get("emailAddress", {}).get(
                                    "address", "Unknown"
                                )
                                for recipient in email.get("toRecipients", [])
                            ],
                            "is_draft": email.get("isDraft", False),
                        }
                        sent_emails.append(email_info)

            # Use formatting function for clean user output
            return format_email_list_response(sent_emails[:count], count)

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e, "get_sent_emails", {"count": count, "batch_size": batch_size}
            )

    async def search_emails(
        self,
        query: str,
        count: int = 20,
        date_from: str = None,
        date_to: str = None,
        folder: str = "inbox",
    ) -> str:
        """
        Search emails by query, sender, date range, or other criteria.

        Uses Microsoft Graph $search parameter for comprehensive search including:
        - Subject content
        - Sender email and name
        - Email body content (via native API search)

        Note: $search doesn't support $orderby, so results are sorted client-side by received date.
        Reference: https://learn.microsoft.com/en-us/graph/search-query-parameter?tabs=http
        """
        try:
            # Validate parameters
            if not query or not query.strip():
                return EmailErrorHandler.handle_email_error(
                    ValueError("Search query cannot be empty"),
                    "search_emails",
                    {"query": query, "count": count},
                )

            # Ensure count is an integer (handle float values from LLM)
            count = int(count) if count else 20

            if count <= 0 or count > 100:
                count = min(max(count, 1), 100)  # Clamp between 1 and 100

            token = self._get_valid_token()
            headers = build_email_headers(token)
            search_results = []

            # Build search filter
            search_filter = []

            # Use $search parameter for comprehensive email search (includes body content)
            # Microsoft Graph API supports $search in from, subject, and body automatically
            # Reference: https://learn.microsoft.com/en-us/graph/search-query-parameter?tabs=http
            search_params = {}
            if query:
                # Use $search instead of $filter for better body content search
                search_params["$search"] = f'"{query}"'
            else:
                # If no query, build filter for other criteria only
                search_filter = []

            # Add date range filter if provided
            if date_from:
                search_filter.append(f"receivedDateTime ge {date_from}T00:00:00Z")
            if date_to:
                search_filter.append(f"receivedDateTime le {date_to}T23:59:59Z")

            # Combine date filters with AND logic (since they're date constraints)
            filter_string = " and ".join(search_filter) if search_filter else None

            # Build final parameters
            final_params = {
                "$top": count,
                "$select": "id,subject,bodyPreview,receivedDateTime,from,toRecipients,isDraft,importance",
            }

            # Add search and filter parameters
            if search_params:
                final_params.update(search_params)
            if filter_string:
                final_params["$filter"] = filter_string

            # Get folder ID if not inbox
            if folder.lower() != "inbox":
                # For now, we'll search in inbox and filter by folder later
                # In a full implementation, you'd get the folder ID first
                pass

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/messages",
                    headers=headers,
                    params=final_params,
                )

                if response.status_code != 200:
                    return EmailErrorHandler.handle_email_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "search_emails",
                        {"query": query, "count": count, "folder": folder},
                    )

                emails = response.json().get("value", [])

                for email in emails:
                    # Format search result
                    email_info = {
                        "id": email.get("id"),
                        "subject": email.get("subject", "No Subject"),
                        "body_preview": email.get(
                            "bodyPreview", "No preview available"
                        ),
                        "received_date": email.get("receivedDateTime"),
                        "from_sender": email.get("from", {})
                        .get("emailAddress", {})
                        .get("address", "Unknown"),
                        "to_recipients": [
                            recipient.get("emailAddress", {}).get("address", "Unknown")
                            for recipient in email.get("toRecipients", [])
                        ],
                        "is_draft": email.get("isDraft", False),
                        "importance": email.get("importance", "normal"),
                        "folder": folder,
                    }
                    search_results.append(email_info)

                # Sort results by received date when using $search (since API doesn't support $orderby with $search)
                if query and search_results:
                    try:
                        from datetime import datetime

                        # Parse ISO datetime strings and sort by received date (newest first)
                        search_results.sort(
                            key=lambda x: datetime.fromisoformat(
                                x["received_date"].replace("Z", "+00:00")
                            )
                            if x["received_date"]
                            else datetime.min,
                            reverse=True,
                        )
                        self.logger.info(
                            f"Sorted {len(search_results)} search results by received date"
                        )
                    except Exception as sort_error:
                        self.logger.warning(
                            f"Failed to sort search results: {sort_error}"
                        )

            # Note: $search parameter automatically searches in from, subject, and body
            # Client-side filtering is no longer needed for basic search functionality
            # The Microsoft Graph API handles body content search natively via $search

            self.logger.info(
                f"Search completed: found {len(search_results)} results for query '{query}' in folder '{folder}'"
            )

            # Use formatting function for clean user output
            return format_email_list_response(search_results[:count], count)

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e, "search_emails", {"query": query, "count": count, "folder": folder}
            )

    async def move_email(self, message_id: str, destination_folder: str) -> str:
        """
        Move an email from one folder to another folder.

        Supports moving emails to standard folders like:
        - Archive
        - Junk
        - Deleted Items
        - Custom folders

        Reference: https://learn.microsoft.com/en-us/graph/api/message-move
        """
        try:
            # Validate parameters
            if not message_id or not message_id.strip():
                return EmailErrorHandler.handle_email_error(
                    ValueError("Message ID cannot be empty"),
                    "move_email",
                    {
                        "message_id": message_id,
                        "destination_folder": destination_folder,
                    },
                )

            if not destination_folder or not destination_folder.strip():
                return EmailErrorHandler.handle_email_error(
                    ValueError("Destination folder cannot be empty"),
                    "move_email",
                    {
                        "message_id": message_id,
                        "destination_folder": destination_folder,
                    },
                )

            token = self._get_valid_token()
            headers = build_email_headers(token, "application/json")

            # Map common folder names to their IDs
            folder_mapping = {
                "archive": "archive",
                "junk": "junk",
                "deleted items": "deleteditems",
                "deleted": "deleteditems",
                "trash": "deleteditems",
                "sent items": "sentitems",
                "sent": "sentitems",
                "drafts": "drafts",
                "inbox": "inbox",
            }

            # Normalize destination folder name
            dest_folder_lower = destination_folder.lower().strip()
            destination_id = folder_mapping.get(dest_folder_lower, dest_folder_lower)

            # Build the move request payload
            move_data = {"destinationId": destination_id}

            # First, try to get the current folder of the message to provide better feedback
            current_folder = "unknown"
            try:
                async with httpx.AsyncClient() as client:
                    # Get message details to see current folder
                    response = await client.get(
                        f"{self.ms_graph_url}/me/messages/{message_id}",
                        headers=headers,
                        params={"$select": "id,subject,parentFolderId"},
                    )

                    if response.status_code == 200:
                        message_data = response.json()
                        # Try to get folder name from parentFolderId
                        folder_response = await client.get(
                            f"{self.ms_graph_url}/me/mailFolders/{message_data.get('parentFolderId')}",
                            headers=headers,
                        )
                        if folder_response.status_code == 200:
                            folder_data = folder_response.json()
                            current_folder = folder_data.get("displayName", "unknown")
            except Exception as folder_error:
                self.logger.warning(
                    f"Could not determine current folder: {folder_error}"
                )

            # Perform the move operation
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ms_graph_url}/me/messages/{message_id}/move",
                    headers=headers,
                    json=move_data,
                )

                # Both 200 OK and 201 Created are success responses
                if response.status_code in [200, 201]:
                    try:
                        move_result = response.json()
                    except (ValueError, KeyError):
                        # If response is empty or not JSON, create a basic success response
                        move_result = {"subject": "Email moved successfully"}

                    success_message = f"Successfully moved email '{move_result.get('subject', 'Unknown subject')}' from '{current_folder}' to '{destination_folder}'"

                    return format_move_email_response(
                        True,
                        success_message,
                        message_id,
                        destination_folder,
                        current_folder,
                    )
                elif response.status_code == 404:
                    error_message = f"Email with ID {message_id} not found"
                    return format_move_email_response(
                        False,
                        error_message,
                        message_id,
                        destination_folder,
                        current_folder,
                    )
                elif response.status_code == 400:
                    error_data = response.json()
                    error_message = f"Move failed: {error_data.get('error', {}).get('message', 'Bad request')}"
                    return format_move_email_response(
                        False,
                        error_message,
                        message_id,
                        destination_folder,
                        current_folder,
                    )
                else:
                    error_message = f"HTTP {response.status_code}: {response.text}"
                    return format_move_email_response(
                        False,
                        error_message,
                        message_id,
                        destination_folder,
                        current_folder,
                    )

        except Exception as e:
            error_message = f"Move operation failed: {str(e)}"
            return format_move_email_response(
                False, error_message, message_id, destination_folder, "unknown"
            )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter(
            [
                self.read_emails_tool,
                self.send_email_tool,
                self.delete_email_tool,
                self.get_email_content_tool,
                self.get_sent_emails_tool,
                self.search_emails_tool,
                self.move_email_tool,
            ]
        )
