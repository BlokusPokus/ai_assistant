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


# Production-ready helper methods for search_emails
def validate_search_parameters(
    search_terms: str, query: str, count: int, date_from: str, 
    date_to: str, start_date: str, end_date: str, date_range: str, 
    received_after: str, folder: str
) -> Dict[str, Any]:
    """Validate search parameters with comprehensive checks."""
    # Check if any query is provided
    actual_query = search_terms or query or date_range
    if not actual_query or not str(actual_query).strip():
        return {"valid": False, "error": "Search query cannot be empty"}

    # Validate count parameter
    try:
        count = int(count) if count else 20
        if count <= 0 or count > 100:
            return {"valid": False, "error": "Count must be between 1 and 100"}
    except (ValueError, TypeError):
        return {"valid": False, "error": "Count must be a valid integer"}

    # Validate folder parameter
    if folder and not isinstance(folder, str):
        return {"valid": False, "error": "Folder must be a valid string"}

    # Validate date parameters
    date_params = [date_from, date_to, start_date, end_date, received_after]
    for date_param in date_params:
        if date_param and not is_valid_date_format(date_param):
            return {"valid": False, "error": f"Invalid date format: {date_param}"}

    return {"valid": True, "error": None}


def sanitize_search_parameters(
    search_terms: str, query: str, count: int, date_from: str,
    date_to: str, start_date: str, end_date: str, date_range: str,
    received_after: str, folder: str
) -> Dict[str, Any]:
    """Sanitize and normalize search parameters."""
    
    # Determine actual query (prioritize search_terms)
    actual_query = search_terms or query or date_range
    sanitized_query = sanitize_search_query(str(actual_query).strip())
    
    # Normalize count
    normalized_count = min(max(count if count else 20, 1), 100)
    
    # Normalize folder
    normalized_folder = str(folder).strip().lower() if folder else "inbox"
    
    # Determine date parameters
    actual_start_date = start_date or date_from or received_after
    actual_end_date = end_date or date_to
    
    return {
        "query": sanitized_query,
        "count": normalized_count,
        "folder": normalized_folder,
        "start_date": actual_start_date,
        "end_date": actual_end_date
    }


def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent injection attacks."""
    import re
    
    if not query:
        return ""
    
    # Remove potentially dangerous characters
    # Keep alphanumeric, spaces, basic punctuation, and common email characters
    sanitized = re.sub(r'[^\w\s@.-]', '', query)
    
    # Limit length to prevent abuse
    sanitized = sanitized[:200]
    
    # Remove multiple consecutive spaces
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized


def is_valid_date_format(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    import re
    from datetime import datetime
    
    if not date_str:
        return True
    
    try:
        # Check if it matches YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            # Try to parse it to ensure it's a valid date
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
    except (ValueError, AttributeError):
        pass
    
    return False


def build_search_parameters(sanitized_params: Dict[str, Any]) -> Dict[str, Any]:
    """Build optimized search parameters for Microsoft Graph API."""
    search_params = {
        "$top": sanitized_params["count"],
        "$select": "id,subject,bodyPreview,receivedDateTime,from,toRecipients,isDraft,importance",
    }

    # Add search query
    if sanitized_params["query"]:
        search_params["$search"] = f'"{sanitized_params["query"]}"'

    # Add date filters
    date_filters = []
    if sanitized_params["start_date"]:
        date_filters.append(f"receivedDateTime ge {sanitized_params['start_date']}T00:00:00Z")
    if sanitized_params["end_date"]:
        date_filters.append(f"receivedDateTime le {sanitized_params['end_date']}T23:59:59Z")
    
    if date_filters:
        search_params["$filter"] = " and ".join(date_filters)

    return search_params


async def get_oauth_access_token_with_retry(get_token_func, user_id: int, request_id: str) -> str:
    """Get OAuth access token with retry logic."""
    import asyncio
    
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            token = await get_token_func(user_id)
            if token:
                return token
        except Exception as e:
            logger.warning(
                f"[{request_id}] Token retrieval attempt {attempt + 1} failed: {str(e)}"
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                raise e
    
    raise Exception("Failed to obtain OAuth access token after retries")


async def execute_search_with_retry(
    ms_graph_url: str, headers: Dict[str, str], search_params: Dict[str, Any], 
    count: int, request_id: str
) -> List[Dict[str, Any]]:
    """Execute search with retry logic and rate limiting."""
    import asyncio
    import httpx
    from .email_error_handler import EmailErrorHandler
    
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{ms_graph_url}/me/messages",
                    headers=headers,
                    params=search_params,
                )

                if response.status_code == 200:
                    emails = response.json().get("value", [])
                    logger.info(
                        f"[{request_id}] Retrieved {len(emails)} emails from API"
                    )
                    return emails
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", retry_delay))
                    logger.warning(
                        f"[{request_id}] Rate limited, waiting {retry_after}s before retry"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_after)
                        continue
                else:
                    return EmailErrorHandler.handle_http_error(
                        response, "search_emails", 
                        {"query": search_params.get("$search", ""), "count": count}
                    )

        except httpx.TimeoutException:
            logger.warning(
                f"[{request_id}] Request timeout on attempt {attempt + 1}"
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                raise Exception("Request timeout after retries")
        except Exception as e:
            logger.error(f"[{request_id}] Search request failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                raise e

    return []


def process_search_results(
    emails: List[Dict[str, Any]], query: str
) -> List[Dict[str, Any]]:
    """Process and format search results efficiently."""
    processed_results = []
    
    for email in emails:
        try:
            email_info = {
                "id": email.get("id"),
                "subject": email.get("subject", "No Subject"),
                "preview": email.get("bodyPreview", "No preview available"),
                "received": email.get("receivedDateTime"),
                "from_name": email.get("from", {})
                .get("emailAddress", {})
                .get("name", "Unknown"),
                "from_email": email.get("from", {})
                .get("emailAddress", {})
                .get("address", "Unknown"),
                "to_recipients": [
                    recipient.get("emailAddress", {}).get("address", "Unknown")
                    for recipient in email.get("toRecipients", [])
                ],
                "is_draft": email.get("isDraft", False),
                "importance": email.get("importance", "normal"),
            }
            processed_results.append(email_info)
        except Exception as e:
            logger.warning(f"Failed to process email: {str(e)}")
            continue
    
    return processed_results


def sort_search_results(
    results: List[Dict[str, Any]], request_id: str
) -> List[Dict[str, Any]]:
    """Sort search results by received date (newest first)."""
    from datetime import datetime
    
    if not results:
        return results
    
    try:
        def sort_key(email):
            received = email.get("received")
            if received:
                try:
                    return datetime.fromisoformat(received.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    return datetime.min
            return datetime.min
        
        sorted_results = sorted(results, key=sort_key, reverse=True)
        logger.info(
            f"[{request_id}] Sorted {len(sorted_results)} search results by received date"
        )
        return sorted_results
        
    except Exception as sort_error:
        logger.warning(f"[{request_id}] Failed to sort search results: {sort_error}")
        return results


def validate_send_email_params(to_recipients: str, subject: str, body: str, is_html: bool):
    """Validate send email parameters and return error response if invalid."""
    from .email_error_handler import EmailErrorHandler
    
    params = {
        "to_recipients": to_recipients,
        "subject": subject,
        "body": body,
        "is_html": is_html,
    }
    
    # Validate recipients
    is_valid, error_msg = validate_recipients(to_recipients)
    if not is_valid:
        return EmailErrorHandler.handle_email_error(ValueError(error_msg), "send_email", params)
    
    # Validate subject
    is_valid, error_msg = validate_subject(subject)
    if not is_valid:
        return EmailErrorHandler.handle_email_error(ValueError(error_msg), "send_email", params)
    
    # Validate body
    is_valid, error_msg = validate_body(body)
    if not is_valid:
        return EmailErrorHandler.handle_email_error(ValueError(error_msg), "send_email", params)
    
    return None  # No validation errors
