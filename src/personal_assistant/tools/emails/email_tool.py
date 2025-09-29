from typing import Any, Dict, Optional, Union

import os
import time
import httpx
from dotenv import load_dotenv

from personal_assistant.config.logging_config import get_logger
from personal_assistant.tools.base import Tool

# Import email-specific error handling
from .email_error_handler import EmailErrorHandler
from .email_internal import (
    build_email_headers,
    build_email_message_data,
    build_email_params,
    build_search_parameters,
    clean_recipients_string,
    clean_html_content,
    execute_search_with_retry,
    format_email_list_response,
    format_email_response,
    format_move_email_response,
    format_success_response,
    get_oauth_access_token_with_retry,
    handle_email_not_found,
    parse_email_content_response,
    parse_emails_from_batch,
    process_email_batch,
    process_search_results,
    sanitize_search_parameters,
    sort_search_results,
    validate_email_parameters,
    validate_message_id,
    validate_search_parameters,
    validate_send_email_params,
)
# OAuth imports for user-specific authentication
from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.services.integration_service import OAuthIntegrationService
from personal_assistant.database.session import AsyncSessionLocal


class EmailTool:
    def __init__(self):
        # Load environment-specific config
        env = os.getenv("ENVIRONMENT", "development")
        config_file = f"config/{env}.env"
        load_dotenv(config_file)
        self.ms_graph_url = "https://graph.microsoft.com/v1.0"
        self.logger = get_logger("tools.emails")
        
        # Initialize OAuth services
        self.token_service = OAuthTokenService()
        self.integration_service = OAuthIntegrationService()
        
        # Create individual tools
        self._create_tools()

    async def _get_oauth_access_token(self, user_id: int) -> str:
        """Get a valid OAuth access token for the user's Microsoft integration."""
        try:
            async with AsyncSessionLocal() as db:
                # Get user's Microsoft integration
                integration = await self.integration_service.get_integration_by_user_and_provider(
                    db=db, user_id=user_id, provider="microsoft"
                )
                
                if not integration:
                    raise Exception("Microsoft integration not found. Please connect your Microsoft account first.")
                
                # Get valid access token
                token = await self.token_service.get_valid_token(db, integration.id, "access_token")
                
                # If no valid access token, try to refresh it
                if not token:
                    self.logger.info("Access token expired or not found, attempting to refresh...")
                    
                    # Use OAuth manager to get properly configured Microsoft provider
                    from personal_assistant.oauth.oauth_manager import OAuthManager
                    oauth_manager = OAuthManager()
                    provider = oauth_manager.get_provider("microsoft")
                    
                    # Attempt to refresh the access token
                    new_access_token = await self.token_service.refresh_access_token(
                        db, integration.id, provider
                    )
                    
                    if new_access_token:
                        self.logger.info("Successfully refreshed access token")
                        return new_access_token
                    else:
                        raise Exception("Could not refresh access token. Please reconnect your Microsoft account.")
                
                return token.access_token
                
        except Exception as e:
            self.logger.error(f"Failed to get OAuth access token: {e}")
            raise Exception(f"Authentication failed: {str(e)}")

    def _create_tools(self):
        """Create individual email tools."""
        self.read_emails_tool = Tool(
            name="read_emails",
            func=self.get_emails,
            description="Read recent emails from your inbox",
            parameters={
                "count": {
                    "type": "integer",
                    "description": "Number of emails to fetch (default: 10)",
                    "default": 10,
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Number of emails per batch (default: 10)",
                    "default": 10,
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
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
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
                },
            },
        )

        self.delete_email_tool = Tool(
            name="delete_email",
            func=self.delete_email,
            description="Delete an email by its ID",
            parameters={
                "email_id": {
                    "type": "string",
                    "description": "The ID of the email message to delete",
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
                }
            },
        )

        self.get_email_content_tool = Tool(
            name="get_email_content",
            func=self.get_email_content,
            description="Get the full content of a specific email by its ID",
            parameters={
                "email_id": {
                    "type": "string",
                    "description": "The ID of the email message to get content from",
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
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
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
                },
            },
        )

        self.search_emails_tool = Tool(
            name="search_emails",
            func=self.search_emails,
            description="Search emails by query, sender, date range, or other criteria. Uses Microsoft Graph $search parameter to search in subject, sender email, sender name, and email body content natively.",
            parameters={
                "search_terms": {
                    "type": "string",
                    "description": "What to search for (keywords, sender email, subject terms, body content - all searched natively by Microsoft Graph API). For date filtering, use 'received:last 24 hours' or 'received:2024-01-01' format.",
                },
                "query": {
                    "type": "string",
                    "description": "Alternative parameter name for search_terms. What to search for (keywords, sender email, subject terms, body content).",
                },
                "date_range": {
                    "type": "string",
                    "description": "Alternative parameter name for search_terms. Use 'received:last 24 hours' or 'received:2024-01-01' format for date filtering.",
                },
                "count": {
                    "type": "integer",
                    "description": "Maximum number of emails to return (default: 20)",
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date for search (YYYY-MM-DD format, optional). Also accepts 'date_from' parameter name.",
                },
                "end_date": {
                    "type": "string", 
                    "description": "End date for search (YYYY-MM-DD format, optional). Also accepts 'date_to' parameter name.",
                },
                "received_after": {
                    "type": "string",
                    "description": "Alternative parameter name for start_date. Search for emails received after this date (YYYY-MM-DD format or ISO datetime).",
                },
                "folder": {
                    "type": "string",
                    "description": "Folder to search in (inbox, sentitems, drafts, etc., default: inbox)",
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
                },
            },
        )

        self.move_email_tool = Tool(
            name="move_email",
            func=self.move_email,
            description="Move an email from one folder to another folder (e.g., from Inbox to Archive, or between custom folders)",
            parameters={
                "email_id": {
                    "type": "string",
                    "description": "The ID of the email message to move",
                },
                "destination_folder": {
                    "type": "string",
                    "description": "Destination folder name (e.g., 'Archive', 'Junk', 'Deleted Items', or custom folder name)",
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
                },
            },
        )

        self.find_all_email_folders_tool = Tool(
            name="find_all_email_folders",
            func=self.find_all_email_folders,
            description="Get a list of all available email folders (Inbox, Sent Items, Drafts, Archive, Junk, Deleted Items, and custom folders)",
            parameters={
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
                },
            },
        )

        self.create_email_folder_tool = Tool(
            name="create_email_folder",
            func=self.create_email_folder,
            description="Create a new custom email folder for organizing emails",
            parameters={
                "folder_name": {
                    "type": "string",
                    "description": "Name of the new folder to create (also called display_name in some contexts)",
                },
                "display_name": {
                    "type": "string",
                    "description": "Alternative parameter name for folder_name. Name of the new folder to create.",
                },
                "parent_folder_id": {
                    "type": "string",
                    "description": "ID of the parent folder (optional, defaults to root if not specified)",
                    "default": None,
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID for authentication (required for OAuth access)",
                },
            },
        )


    async def get_emails(self, user_id: int, count: int = 10, batch_size: int = 10, ) -> Union[str, dict]:
        """Read recent emails with improved error handling and OAuth token management"""
        try:
            # Validate and normalize parameters
            count, batch_size = validate_email_parameters(count, batch_size)


            # Get OAuth access token
            token = await self._get_oauth_access_token(user_id)
            headers = build_email_headers(token)
            all_emails = []

            # Process emails in batches
            async with httpx.AsyncClient() as client:
                for i in range(0, count, batch_size):
                    batch_num = i // batch_size + 1
                    current_batch_size = min(batch_size, count - i)
                    
                    self.logger.info(f"Processing batch {batch_num}, emails {i} to {i + current_batch_size}")
                    
                    batch_emails = await process_email_batch(
                        client, headers, batch_num, current_batch_size, i, 
                        self.ms_graph_url, self.logger
                    )
                    
                    parsed_emails = parse_emails_from_batch(batch_emails, self.logger)
                    all_emails.extend(parsed_emails)

            # Format and return response
            return format_email_response(all_emails, count, self.logger)

        except Exception as e:
            return EmailErrorHandler.handle_email_error_str(
                e, "get_emails", {"count": count, "batch_size": batch_size}
            )


    async def send_email(
        self, user_id: int, to_recipients: str = None, subject: str = None, body: str = None, is_html: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Send an email to one or more recipients"""
        try:
            # Validate parameters using internal functions
            validation_error = validate_send_email_params(to_recipients, subject, body, is_html)
            if validation_error:
                return validation_error


            # Get OAuth access token
            token = await self._get_oauth_access_token(user_id)
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
                    return format_success_response(
                        f"Email sent successfully to {to_recipients}",
                        {"recipients": to_recipients},
                    )
                else:
                    return EmailErrorHandler.handle_http_error(
                        response, "send_email",
                        {"to_recipients": to_recipients, "subject": subject, "body": body, "is_html": is_html}
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

    async def delete_email(self, user_id: int,email_id: str) -> Dict[str, Any]:
        """Delete an email by its ID"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_message_id(email_id)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg), "delete_email", {"email_id": email_id}
                )

            
            token = await self._get_oauth_access_token(user_id)
            headers = build_email_headers(token)

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.ms_graph_url}/me/messages/{email_id}", headers=headers
                )

                if response.status_code == 204:  # No content on successful deletion
                    return format_success_response(
                        f"Successfully deleted email with ID: {email_id}",
                        {"email_id": email_id},
                    )
                elif response.status_code == 404:
                    return handle_email_not_found(email_id)
                else:
                    return EmailErrorHandler.handle_http_error(
                        response, "delete_email", {"email_id": email_id}
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e, "delete_email", {"email_id": email_id}
            )

    async def get_email_content(self, user_id: int,email_id: str) -> Dict[str, Any]:
        """Get the full content of a specific email by its ID"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_message_id(email_id)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "get_email_content",
                    {"email_id": email_id},
                )

            
            token = await self._get_oauth_access_token(user_id)
            headers = build_email_headers(token)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/messages/{email_id}",
                    headers=headers,
                    params=build_email_params(
                        top=1,
                        select="id,subject,body,receivedDateTime,from,toRecipients",
                    ),
                )

                if response.status_code == 200:
                    mail = response.json()
                    raw_body = mail.get("body", {}).get("content", "")
                    clean_body = clean_html_content(raw_body)

                    # Use formatting function for clean user output
                    email_data = parse_email_content_response(mail, clean_body)
                    return format_success_response(
                        "Email content retrieved successfully", email_data
                    )
                elif response.status_code == 404:
                    return handle_email_not_found(email_id)
                else:
                    return EmailErrorHandler.handle_http_error(
                        response, "get_email_content", {"email_id": email_id}
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e, "get_email_content", {"email_id": email_id}
            )

    async def get_sent_emails(self, user_id: int,count: int = 10, batch_size: int = 10, ) -> str:
        """
        Read recent emails you have sent with improved error handling and token management
        """
        try:
            # Validate parameters using internal functions
            # Ensure count and batch_size are integers (handle float values from LLM)
            count = int(count) if count else 10
            batch_size = int(batch_size) if batch_size else 10

            count, batch_size = validate_email_parameters(count, batch_size)

            
            token = await self._get_oauth_access_token(user_id)
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
                        return EmailErrorHandler.handle_http_error(
                            response, "get_sent_emails", {"count": count, "batch_size": batch_size}
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
            return EmailErrorHandler.handle_email_error_str(
                e, "get_sent_emails", {"count": count, "batch_size": batch_size}
            )

    async def search_emails(
        self,
        user_id: int,
        search_terms: str = None,
        query: str = None,
        count: int = 20,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date_range: Optional[str] = None,
        received_after: Optional[str] = None,
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
        start_time = time.time()
        request_id = f"search_{int(start_time * 1000)}"
        
        try:
            # Enhanced parameter validation
            validation_result = validate_search_parameters(
                search_terms, query, count, date_from, date_to, 
                start_date, end_date, date_range, received_after, folder
            )
            if not validation_result["valid"]:
                return EmailErrorHandler.handle_validation_error(
                    validation_result["error"], "search_emails",
                    {"query": query, "count": count, "folder": folder}
                )

            # Sanitize and normalize parameters
            sanitized_params = sanitize_search_parameters(
                search_terms, query, count, date_from, date_to,
                start_date, end_date, date_range, received_after, folder
            )

            self.logger.info(
                f"[{request_id}] Starting email search with params: "
                f"query='{sanitized_params['query'][:50]}...', "
                f"count={sanitized_params['count']}, "
                f"folder='{sanitized_params['folder']}'"
            )

            # Get OAuth access token with retry logic
            token = await get_oauth_access_token_with_retry(self._get_oauth_access_token, user_id, request_id)
            headers = build_email_headers(token)
            
            # Build optimized search parameters
            search_params = build_search_parameters(sanitized_params)
            
            # Execute search with retry logic and rate limiting
            search_results = await execute_search_with_retry(
                self.ms_graph_url, headers, search_params, sanitized_params["count"], request_id
            )

            # Process and sort results efficiently
            processed_results = process_search_results(search_results, sanitized_params["query"])
            
            # Sort results by received date (newest first)
            sorted_results = sort_search_results(processed_results, request_id)

            execution_time = time.time() - start_time
            self.logger.info(
                f"[{request_id}] Search completed: found {len(sorted_results)} results "
                f"for query '{sanitized_params['query'][:50]}...' in folder '{sanitized_params['folder']}' "
                f"(execution time: {execution_time:.2f}s)"
            )

            # Return formatted results
            return format_email_list_response(sorted_results[:sanitized_params["count"]], sanitized_params["count"])

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"[{request_id}] Search failed after {execution_time:.2f}s: {str(e)}"
            )
            return EmailErrorHandler.handle_email_error_str(
                e, "search_emails", {"query": query, "count": count, "folder": folder}
            )

    async def move_email(self, email_id: str, destination_folder: str, user_id: int) -> str:
        """
        Move an email from one folder to another folder for organization and classification.
        
        Args:
            email_id: ID of the email to move
            destination_folder: Name of the destination folder
            user_id: User identifier for OAuth authentication
            
        Returns:
            Success message with move details or error message
        """
        try:
            # Build error context once
            error_context = {"email_id": email_id, "destination_folder": destination_folder}
            
            # Validate parameters
            if not email_id or not email_id.strip():
                return EmailErrorHandler.handle_validation_error(
                    "Email ID cannot be empty", "move_email", error_context
                )

            if not destination_folder or not destination_folder.strip():
                return EmailErrorHandler.handle_validation_error(
                    "Destination folder cannot be empty", "move_email", error_context
                )

            
            token = await self._get_oauth_access_token(user_id)
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
            destination_id = folder_mapping.get(dest_folder_lower, None)
            
            # If it's not a standard folder, we need to find the custom folder ID
            if destination_id is None:
                # Search for custom folder by display name
                async with httpx.AsyncClient() as client:
                    folders_response = await client.get(
                        f"{self.ms_graph_url}/me/mailFolders",
                        headers=headers,
                        params={
                            "$select": "id,displayName",
                            "$top": 100  # Get all folders, not just first 10
                        }
                    )
                    
                    if folders_response.status_code == 200:
                        folders_data = folders_response.json().get("value", [])
                        for folder in folders_data:
                            if folder.get("displayName", "").lower() == dest_folder_lower:
                                destination_id = folder.get("id")
                                break
                        
                        if destination_id is None:
                            return EmailErrorHandler.handle_folder_not_found_error(
                                destination_folder, "move_email", error_context
                            )
                    else:
                        return EmailErrorHandler.handle_http_error(
                            folders_response, "move_email", error_context
                        )

            # Build the move request payload
            move_data = {"destinationId": destination_id}

            # Helper function to avoid repeating parameters
            def create_response(success: bool, message: str) -> str:
                return format_move_email_response(success, message, email_id, destination_folder, "unknown")

            # Perform the move operation
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ms_graph_url}/me/messages/{email_id}/move",
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

                    success_message = f"Successfully moved email '{move_result.get('subject', 'Unknown subject')}' to '{destination_folder}'"
                    return create_response(True, success_message)
                    
                elif response.status_code == 404:
                    return create_response(False, f"Email with ID {email_id} not found")
                    
                elif response.status_code == 400:
                    error_data = response.json()
                    error_message = f"Move failed: {error_data.get('error', {}).get('message', 'Bad request')}"
                    return create_response(False, error_message)
                    
                else:
                    return create_response(False, f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            return EmailErrorHandler.handle_email_error_str(
                e, "move_email", error_context
            )

    async def find_all_email_folders(self, user_id: int) -> str:
        """
        Get a list of all available email folders including standard and custom folders.
        
        Returns both standard Microsoft folders (Inbox, Sent Items, Drafts, etc.) 
        and any custom folders the user has created.
        """
        try:
            
            token = await self._get_oauth_access_token(user_id)
            headers = build_email_headers(token)
            
            folders = []
            
            async with httpx.AsyncClient() as client:
                # Get all mail folders using $top parameter (more efficient than pagination)
                response = await client.get(
                    f"{self.ms_graph_url}/me/mailFolders",
                    headers=headers,
                    params={
                        "$select": "id,displayName,parentFolderId,totalItemCount,unreadItemCount",
                        "$orderby": "displayName",
                        "$top": 100  # Get up to 100 folders at once (should cover most cases)
                    }
                )
                
                if response.status_code != 200:
                    return EmailErrorHandler.handle_http_error(
                        response, "find_all_email_folders", {}
                    )
                
                folders_data = response.json().get("value", [])
                
                # Process and format folder information
                for folder in folders_data:
                    folder_info = {
                        "id": folder.get("id"),
                        "name": folder.get("displayName", "Unknown"),
                        "total_items": folder.get("totalItemCount", 0),
                        "unread_items": folder.get("unreadItemCount", 0),
                        "parent_folder_id": folder.get("parentFolderId")
                    }
                    folders.append(folder_info)
                
                # Sort folders: standard folders first, then custom folders alphabetically
                standard_folders = ["Inbox", "Sent Items", "Drafts", "Archive", "Junk Email", "Deleted Items"]
                
                def sort_key(folder):
                    name = folder["name"]
                    if name in standard_folders:
                        return (0, standard_folders.index(name))
                    else:
                        return (1, name.lower())
                
                folders.sort(key=sort_key)
                
                # Format response
                if not folders:
                    return "No email folders found."
                
                result = "Available Email Folders:\n\n"
                
                for folder in folders:
                    unread_info = f" ({folder['unread_items']} unread)" if folder['unread_items'] > 0 else ""
                    result += f"• {folder['name']}: {folder['total_items']} emails{unread_info}\n"
                
                self.logger.info(f"Found {len(folders)} email folders for user {user_id}")
                return result
                
        except Exception as e:
            return EmailErrorHandler.handle_email_error_str(
                e, "find_all_email_folders", {}
            )

    async def create_email_folder(self, folder_name: str, user_id: int, parent_folder_id: Optional[str] = None) -> str:
        """
        Create a new custom email folder for organizing emails.
        
        Args:
            folder_name: Name of the new folder to create
            parent_folder_id: ID of the parent folder (optional, defaults to root)
            user_id: User identifier for OAuth authentication
            
        Returns:
            Success message with folder details or error message
        """
        try:
            # Build error context once
            error_context = {"folder_name": folder_name, "parent_folder_id": parent_folder_id}
            
            # Validate and clean folder name
            if not folder_name or not folder_name.strip():
                return EmailErrorHandler.handle_validation_error(
                    "Folder name cannot be empty", "create_email_folder", error_context
                )
            
            folder_name = folder_name.strip()
            if len(folder_name) > 255:
                return EmailErrorHandler.handle_validation_error(
                    "Folder name cannot exceed 255 characters", "create_email_folder", error_context
                )
            
            token = await self._get_oauth_access_token(user_id)
            headers = build_email_headers(token, "application/json")
            
            # Build the folder creation payload
            folder_data = {"displayName": folder_name}
            if parent_folder_id:
                folder_data["parentFolderId"] = parent_folder_id
            
            async with httpx.AsyncClient() as client:
                # Create the folder
                response = await client.post(
                    f"{self.ms_graph_url}/me/mailFolders",
                    headers=headers,
                    json=folder_data
                )
                
                if response.status_code == 201:  # Created
                    folder_info = response.json()
                    folder_id = folder_info.get("id")
                    created_name = folder_info.get("displayName", folder_name)
                    
                    success_message = f"Successfully created email folder '{created_name}'"
                    if folder_id:
                        success_message += f" with ID: {folder_id}"
                    
                    self.logger.info(f"Created email folder '{created_name}' for user {user_id}")
                    return success_message
                    
                else:
                    return EmailErrorHandler.handle_http_error(
                        response, "create_email_folder", error_context
                    )
                    
        except Exception as e:
            return EmailErrorHandler.handle_email_error_str(
                e, "create_email_folder", error_context
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
                self.find_all_email_folders_tool,
                self.create_email_folder_tool,
            ]
        )
