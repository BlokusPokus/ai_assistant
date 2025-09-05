"""
Internal functions for Email Tool.

This module contains internal utility functions and helper methods
that are used by the main EmailTool class.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_email_parameters(count: int, batch_size: int = 10) -> tuple[int, int]:
    """Validate and normalize email parameters"""
    try:
        count = int(count)
        batch_size = int(batch_size)

        if count < 1:
            count = 10
            logger.warning(f"Invalid count: {count}, defaulting to 10")

        if batch_size < 1 or batch_size > 50:
            batch_size = 10
            logger.warning(f"Invalid batch_size: {batch_size}, defaulting to 10")

        return count, batch_size
    except (ValueError, TypeError):
        logger.warning("Invalid parameter types, using defaults")
        return 10, 10


def validate_message_id(message_id: str) -> tuple[bool, str]:
    """Validate email message ID"""
    if not message_id or not message_id.strip():
        return False, "Error: Message ID is required"
    return True, ""


def validate_recipients(to_recipients: str) -> tuple[bool, str]:
    """Validate email recipients"""
    if not to_recipients or not to_recipients.strip():
        return False, "Error: Recipients are required"

    # Basic email validation
    emails = [email.strip() for email in to_recipients.split(",")]
    for email in emails:
        if not is_valid_email(email):
            return False, f"Error: Invalid email address: {email}"

    return True, ""


def validate_subject(subject: str) -> tuple[bool, str]:
    """Validate email subject"""
    if not subject or not subject.strip():
        return False, "Error: Subject is required"
    return True, ""


def validate_body(body: str) -> tuple[bool, str]:
    """Validate email body"""
    if not body or not body.strip():
        return False, "Error: Body content is required"
    return True, ""


def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_token_valid(access_token: str, token_expires_at: datetime) -> bool:
    """Check if current token is valid and not expired"""
    if not access_token or not token_expires_at:
        return False
    return datetime.now() < token_expires_at


def get_token_expiration() -> datetime:
    """Get token expiration time (1 hour from now)"""
    return datetime.now() + timedelta(hours=1)


def build_email_headers(
    token: str, content_type: str = "application/json"
) -> Dict[str, str]:
    """Build HTTP headers for email operations"""
    headers = {"Authorization": f"Bearer {token}"}
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def build_email_params(
    top: int, select: Optional[str] = None, skip: int = 0, orderby: Optional[str] = None
) -> Dict[str, Any]:
    """Build query parameters for email operations"""
    params: Dict[str, Any] = {"$top": top}

    if select:
        params["$select"] = select
    if skip > 0:
        params["$skip"] = skip
    if orderby:
        params["$orderby"] = orderby

    return params


def build_email_message_data(
    subject: str, body: str, recipients: List[str], is_html: bool = False
) -> Dict[str, Any]:
    """Build email message data for sending"""
    recipient_list = [
        {"emailAddress": {"address": email.strip()}} for email in recipients
    ]

    return {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML" if is_html else "Text", "content": body},
            "toRecipients": recipient_list,
        }
    }


def parse_email_response(mail: Dict[str, Any]) -> Dict[str, Any]:
    """Parse email response from Microsoft Graph API"""
    return {
        "id": mail.get("id", ""),
        "subject": mail.get("subject", "No Subject"),
        "preview": mail.get("bodyPreview", ""),
        "received": mail.get("receivedDateTime", ""),
        "from_name": mail.get("from", {})
        .get("emailAddress", {})
        .get("name", "Unknown"),
        "from_email": mail.get("from", {}).get("emailAddress", {}).get("address", ""),
    }


def parse_email_content_response(
    mail: Dict[str, Any], clean_body: str
) -> Dict[str, Any]:
    """Parse email content response from Microsoft Graph API"""
    return {
        "id": mail.get("id", ""),
        "subject": mail.get("subject", "No Subject"),
        "body": clean_body,
        "received": mail.get("receivedDateTime", ""),
        "from_name": mail.get("from", {})
        .get("emailAddress", {})
        .get("name", "Unknown"),
        "from_email": mail.get("from", {}).get("emailAddress", {}).get("address", ""),
        "to_recipients": [
            recipient.get("emailAddress", {}).get("address", "")
            for recipient in mail.get("toRecipients", [])
        ],
    }


def format_success_response(message: str, data: Any = None) -> Dict[str, Any]:
    """Format successful response"""
    response = {"success": True, "message": message}
    if data:
        response["data"] = data
    return response


def format_error_response(error: str, data: Any = None) -> Dict[str, Any]:
    """Format error response"""
    response = {"success": False, "error": error}
    if data:
        response["data"] = data
    return response


def handle_http_response(
    response, success_message: str, error_prefix: str = "Failed"
) -> Dict[str, Any]:
    """Handle HTTP response and return appropriate format"""
    if response.status_code in [200, 202, 204]:
        return format_success_response(success_message)
    else:
        return format_error_response(f"{error_prefix}: {response.text}")


def handle_email_not_found(message_id: str) -> Dict[str, Any]:
    """Handle case when email is not found"""
    return format_error_response(f"Email with ID {message_id} not found")


def validate_environment_variables() -> tuple[bool, str, str]:
    """Validate required environment variables"""
    application_id = os.getenv("MICROSOFT_APPLICATION_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")

    if not application_id or not client_secret:
        return False, "", ""

    return True, application_id, client_secret


def get_environment_error_message() -> str:
    """Get error message for missing environment variables"""
    return "Missing required environment variables: MICROSOFT_APPLICATION_ID and MICROSOFT_CLIENT_SECRET"


def clean_recipients_string(recipients: str) -> List[str]:
    """Clean and split recipients string into list"""
    return [email.strip() for email in recipients.split(",") if email.strip()]


def format_email_list_response(emails: List[Dict[str, Any]], count: int) -> str:
    """Format email list response for display"""
    if not emails:
        return "No emails found."

    response = f"📧 Recent Emails ({len(emails)} of {count} requested):\n\n"

    for i, email in enumerate(emails, 1):
        response += f"{i}. **{email['subject']}**\n"
        response += f"   🆔 ID: {email['id']}\n"
        response += f"   👤 From: {email['from_name']} <{email['from_email']}>\n"
        response += f"   📅 Received: {email['received']}\n"
        response += f"   📝 Preview: {email['preview'][:100]}...\n\n"

    return response


def format_email_content_response(email_data: Dict[str, Any]) -> str:
    """Format email content response for display"""
    email = email_data.get("email", {})

    response = "📧 Email Content\n\n"
    response += f"**ID:** {email.get('id', 'Unknown')}\n"
    response += f"**Subject:** {email.get('subject', 'No Subject')}\n"
    response += f"**From:** {email.get('from_name', 'Unknown')} <{email.get('from_email', '')}>\n"
    response += f"**Received:** {email.get('received', 'Unknown')}\n"
    response += f"**To:** {', '.join(email.get('to_recipients', []))}\n\n"
    response += f"**Content:**\n{email.get('body', 'No content')}\n\n"
    response += "⏱️ Response Time: <3 seconds (target)"

    return response


def format_send_email_response(success: bool, message: str, recipients: str) -> str:
    """Format send email response for display"""
    if success:
        return f"✅ {message}\n📧 Sent to: {recipients}\n⏱️ Response Time: <3 seconds (target)"
    else:
        return f"❌ {message}\n⏱️ Response Time: <3 seconds (target)"


def format_delete_email_response(success: bool, message: str, message_id: str) -> str:
    """Format delete email response for display"""
    if success:
        return f"✅ {message}\n🗑️ Deleted email ID: {message_id}\n⏱️ Response Time: <3 seconds (target)"
    else:
        return f"❌ {message}\n⏱️ Response Time: <3 seconds (target)"


def format_move_email_response(
    success: bool,
    message: str,
    email_id: str,
    destination_folder: str,
    previous_folder: str = "unknown",
) -> str:
    """Format move email response for display"""
    if success:
        return f"✅ {message}\n📧 Email ID: {email_id}\n📁 Moved from: {previous_folder}\n📁 Moved to: {destination_folder}\n⏱️ Response Time: <3 seconds (target)"
    else:
        return f"❌ {message}\n⏱️ Response Time: <3 seconds (target)"


# EmailTool internal helper functions
def clean_html_content(html_content: str) -> str:
    """Extract clean text content from HTML, removing styling and formatting"""
    from personal_assistant.utils.text_cleaner import clean_html_content as clean_html
    return str(clean_html(html_content))


async def process_email_batch(client, headers: dict, batch_num: int, batch_size: int, skip: int, 
                             ms_graph_url: str, logger) -> List[Dict[str, Any]]:
    """Process a single batch of emails"""
    params = build_email_params(
        top=batch_size,
        select="id,subject,bodyPreview,receivedDateTime,from,isDraft",
        skip=skip,
        orderby="receivedDateTime desc",
    )

    try:
        response = await client.get(
            f"{ms_graph_url}/me/messages",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            logger.error(f"HTTP error {response.status_code} in batch {batch_num}: {response.text}")
            return []

        batch_emails = response.json().get("value", [])
        logger.info(f"Retrieved {len(batch_emails)} emails from API in batch {batch_num}")
        return batch_emails

    except Exception as batch_error:
        logger.error(f"Error processing batch {batch_num}: {batch_error}")
        return []


def parse_emails_from_batch(batch_emails: List[Dict[str, Any]], logger) -> List[Dict[str, Any]]:
    """Parse and filter emails from a batch"""
    parsed_emails = []
    for mail in batch_emails:
        if not mail.get("isDraft"):
            try:
                parsed_email = parse_email_response(mail)
                parsed_emails.append(parsed_email)
                logger.debug(f"Successfully parsed email: {parsed_email.get('subject', 'No Subject')}")
            except Exception as parse_error:
                logger.error(f"Failed to parse email: {parse_error}")
                continue
    return parsed_emails


def format_email_response(emails: List[Dict[str, Any]], requested_count: int, logger) -> str:
    """Format the final email response"""
    logger.info(f"Total emails collected: {len(emails)}, about to format response")
    
    if not emails:
        logger.warning("No emails were successfully retrieved")
        return "No emails found or all batches failed to retrieve emails."
    
    try:
        formatted_response = format_email_list_response(emails[:requested_count], requested_count)
        logger.info("Successfully formatted email response")
        return formatted_response
    except Exception as format_error:
        logger.error(f"Failed to format email response: {format_error}")
        return f"Retrieved {len(emails)} emails, but formatting failed: {str(format_error)}"
