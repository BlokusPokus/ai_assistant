from typing import Dict, Any, List, Optional
from personal_assistant.tools.base import Tool
import httpx
from .ms_graph import get_access_token
from .email_internal import (
    validate_email_parameters,
    validate_message_id,
    validate_recipients,
    validate_subject,
    validate_body,
    is_token_valid,
    get_token_expiration,
    build_email_headers,
    build_email_params,
    build_email_message_data,
    parse_email_response,
    parse_email_content_response,
    format_success_response,
    format_error_response,
    handle_http_response,
    handle_email_not_found,
    validate_environment_variables,
    get_environment_error_message,
    clean_recipients_string,
    format_email_list_response,
    format_email_content_response,
    format_send_email_response,
    format_delete_email_response
)
from dotenv import load_dotenv
from personal_assistant.utils.text_cleaner import clean_html_content

# Import email-specific error handling
from .email_error_handler import EmailErrorHandler


class EmailTool:
    def __init__(self):
        load_dotenv()
        self.ms_graph_url = "https://graph.microsoft.com/v1.0"
        self._access_token = None
        self._token_expires_at = None
        self.scopes = ["Mail.Read", "Mail.ReadWrite", "Mail.Send", "User.Read"]
        self._initialize_token()

        # Create individual tools
        self.read_emails_tool = Tool(
            name="read_emails",
            func=self.read_recent_emails,
            description="Read recent emails from your inbox",
            parameters={
                "count": {
                    "type": "integer",
                    "description": "Number of emails to fetch",
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Number of emails per batch (default: 10)",
                }
            }
        )

        self.send_email_tool = Tool(
            name="send_email",
            func=self.send_email,
            description="Send an email to one or more recipients",
            parameters={
                "to_recipients": {
                    "type": "string",
                    "description": "Comma-separated list of email addresses to send to"
                },
                "subject": {
                    "type": "string",
                    "description": "Subject line of the email"
                },
                "body": {
                    "type": "string",
                    "description": "Body content of the email"
                },
                "is_html": {
                    "type": "boolean",
                    "description": "Whether the body is HTML format (default: false)"
                }
            }
        )

        self.delete_email_tool = Tool(
            name="delete_email",
            func=self.delete_email,
            description="Delete an email by its ID",
            parameters={
                "message_id": {
                    "type": "string",
                    "description": "The ID of the email message to delete"
                }
            }
        )

        self.get_email_content_tool = Tool(
            name="get_email_content",
            func=self.get_email_content,
            description="Get the full content of a specific email by its ID",
            parameters={
                "message_id": {
                    "type": "string",
                    "description": "The ID of the email message to get content from"
                }
            }
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
            application_id,
            client_secret,
            self.scopes
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

    async def read_recent_emails(self, count: int, batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Read recent emails with improved error handling and token management
        """
        try:
            # Validate parameters using internal functions
            count, batch_size = validate_email_parameters(count, batch_size)

            token = self._get_valid_token()
            headers = build_email_headers(token)
            emails = []

            # Reuse the pagination logic
            for i in range(0, count, batch_size):
                params = build_email_params(
                    top=min(batch_size, count - i),
                    select='id,subject,bodyPreview,receivedDateTime,from,isDraft',
                    skip=i,
                    orderby='receivedDateTime desc'
                )

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.ms_graph_url}/me/messages",
                        headers=headers,
                        params=params
                    )

                    if response.status_code != 200:
                        return [EmailErrorHandler.handle_email_error(
                            Exception(
                                f"HTTP {response.status_code}: {response.text}"),
                            "read_recent_emails",
                            {"count": count, "batch_size": batch_size}
                        )]

                    for mail in response.json().get('value', []):
                        if not mail.get('isDraft'):
                            emails.append(parse_email_response(mail))

                    if len(emails) >= count:
                        break

            return emails[:count]

        except Exception as e:
            return [EmailErrorHandler.handle_email_error(e, "read_recent_emails", {"count": count, "batch_size": batch_size})]

    async def send_email(self, to_recipients: str, subject: str, body: str, is_html: bool = False) -> Dict[str, Any]:
        """Send an email to one or more recipients"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_recipients(to_recipients)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "send_email",
                    {"to_recipients": to_recipients, "subject": subject,
                        "body": body, "is_html": is_html}
                )

            is_valid, error_msg = validate_subject(subject)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "send_email",
                    {"to_recipients": to_recipients, "subject": subject,
                        "body": body, "is_html": is_html}
                )

            is_valid, error_msg = validate_body(body)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "send_email",
                    {"to_recipients": to_recipients, "subject": subject,
                        "body": body, "is_html": is_html}
                )

            token = self._get_valid_token()
            headers = build_email_headers(token, "application/json")

            # Parse and clean recipients
            recipients = clean_recipients_string(to_recipients)

            # Build email message data
            email_data = build_email_message_data(
                subject, body, recipients, is_html)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ms_graph_url}/me/sendMail",
                    headers=headers,
                    json=email_data
                )

                if response.status_code == 202:  # Accepted
                    return format_success_response(f"Email sent successfully to {to_recipients}")
                else:
                    return EmailErrorHandler.handle_email_error(
                        Exception(
                            f"HTTP {response.status_code}: {response.text}"),
                        "send_email",
                        {"to_recipients": to_recipients, "subject": subject,
                            "body": body, "is_html": is_html}
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(
                e,
                "send_email",
                {"to_recipients": to_recipients, "subject": subject,
                    "body": body, "is_html": is_html}
            )

    async def delete_email(self, message_id: str) -> Dict[str, Any]:
        """Delete an email by its ID"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_message_id(message_id)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "delete_email",
                    {"message_id": message_id}
                )

            token = self._get_valid_token()
            headers = build_email_headers(token)

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.ms_graph_url}/me/messages/{message_id}",
                    headers=headers
                )

                if response.status_code == 204:  # No content on successful deletion
                    return format_success_response(f"Successfully deleted email with ID: {message_id}")
                elif response.status_code == 404:
                    return handle_email_not_found(message_id)
                else:
                    return EmailErrorHandler.handle_email_error(
                        Exception(
                            f"HTTP {response.status_code}: {response.text}"),
                        "delete_email",
                        {"message_id": message_id}
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(e, "delete_email", {"message_id": message_id})

    async def get_email_content(self, message_id: str) -> Dict[str, Any]:
        """Get the full content of a specific email by its ID"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_message_id(message_id)
            if not is_valid:
                return EmailErrorHandler.handle_email_error(
                    ValueError(error_msg),
                    "get_email_content",
                    {"message_id": message_id}
                )

            token = self._get_valid_token()
            headers = build_email_headers(token)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/messages/{message_id}",
                    headers=headers,
                    params=build_email_params(
                        top=1,
                        select='id,subject,body,receivedDateTime,from,toRecipients'
                    )
                )

                if response.status_code == 200:
                    mail = response.json()
                    raw_body = mail.get('body', {}).get('content', '')
                    clean_body = self._clean_html_content(raw_body)

                    email_data = {
                        "success": True,
                        "email": parse_email_content_response(mail, clean_body)
                    }
                    return email_data
                elif response.status_code == 404:
                    return handle_email_not_found(message_id)
                else:
                    return EmailErrorHandler.handle_email_error(
                        Exception(
                            f"HTTP {response.status_code}: {response.text}"),
                        "get_email_content",
                        {"message_id": message_id}
                    )

        except Exception as e:
            return EmailErrorHandler.handle_email_error(e, "get_email_content", {"message_id": message_id})

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([self.read_emails_tool, self.send_email_tool, self.delete_email_tool, self.get_email_content_tool])
