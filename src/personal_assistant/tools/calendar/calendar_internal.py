"""
Internal functions for Calendar Tool.

This module contains internal utility functions and helper methods
that are used by the main CalendarTool class.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_calendar_parameters(count: int, days: int) -> tuple[int, int]:
    """Validate and normalize calendar parameters"""
    try:
        count = int(count)
        days = int(days)

        if count < 1:
            count = 5
            logger.warning(f"Invalid count: {count}, defaulting to 5")

        if days < 1:
            days = 7
            logger.warning(f"Invalid days: {days}, defaulting to 7")

        return count, days
    except (ValueError, TypeError):
        logger.warning("Invalid parameter types, using defaults")
        return 5, 7


def validate_event_id(event_id: str) -> tuple[bool, str]:
    """Validate calendar event ID"""
    if not event_id or not event_id.strip():
        return False, "Error: Event ID is required"
    return True, ""


def validate_subject(subject: str) -> tuple[bool, str]:
    """Validate event subject"""
    if not subject or not subject.strip():
        return False, "Error: Subject is required"
    return True, ""


def validate_start_time(start_time: str) -> tuple[bool, str]:
    """Validate event start time format - accepts both YYYY-MM-DD HH:MM and ISO format"""
    if not start_time or not start_time.strip():
        return False, "Error: Start time is required"

    # Try the expected format first (YYYY-MM-DD HH:MM)
    try:
        datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        return True, ""
    except ValueError:
        pass
    
    # Try ISO format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM)
    try:
        datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        return True, ""
    except ValueError:
        pass
    
    try:
        datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        return True, ""
    except ValueError:
        pass
    
    return False, "Error: Start time must be in YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM format"


def validate_duration(duration: int) -> tuple[bool, str]:
    """Validate event duration"""
    try:
        duration = int(duration)
        if duration < 1:
            return False, "Error: Duration must be at least 1 minute"
        if duration > 1440:  # 24 hours in minutes
            return False, "Error: Duration cannot exceed 24 hours"
        return True, ""
    except (ValueError, TypeError):
        return False, "Error: Duration must be a valid integer"


def validate_location(location: str) -> tuple[bool, str]:
    """Validate event location (optional)"""
    if location and len(location.strip()) > 200:
        return False, "Error: Location description too long (max 200 characters)"
    return True, ""


def is_token_valid(access_token: str) -> bool:
    """Check if current token is valid"""
    return access_token is not None


def build_calendar_headers(
    token: str, content_type: Optional[str] = None
) -> Dict[str, str]:
    """Build HTTP headers for calendar operations"""
    headers = {"Authorization": f"Bearer {token}"}
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def build_calendar_view_params(
    start_datetime: str, end_datetime: str, count: int
) -> Dict[str, Any]:
    """Build query parameters for calendar view"""
    return {
        "startDateTime": start_datetime,
        "endDateTime": end_datetime,
        "$top": count,
        "$orderby": "start/dateTime asc",
        "$select": "subject,start,end,location,bodyPreview,organizer",
    }


def build_event_data(
    subject: str, start_dt: datetime, end_dt: datetime, location: str = ""
) -> Dict[str, Any]:
    """Build event data for creation"""
    event_data = {
        "subject": subject,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
    }

    if location:
        event_data["location"] = {"displayName": location}

    return event_data


def parse_calendar_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse calendar event from Microsoft Graph API response"""
    return {
        "id": event.get("id", ""),
        "subject": event.get("subject", "Untitled Event"),
        "start": event.get("start", {}).get("dateTime", ""),
        "end": event.get("end", {}).get("dateTime", ""),
        "location": event.get("location", {}).get("displayName", "No location"),
        "preview": event.get("bodyPreview", ""),
        "organizer": event.get("organizer", {})
        .get("emailAddress", {})
        .get("name", "Unknown"),
    }


def parse_event_details(event: Dict[str, Any]) -> str:
    """Parse and format detailed event information"""
    start = event.get("start", {}).get("dateTime", "Unknown")
    end = event.get("end", {}).get("dateTime", "Unknown")
    subject = event.get("subject", "Untitled Event")
    body = event.get("body", {}).get("content", "No description")
    location = event.get("location", {}).get("displayName", "No location")
    organizer = (
        event.get("organizer", {}).get("emailAddress", {}).get("name", "Unknown")
    )

    result = f"Event: {subject}\n"
    result += f"Start: {start}\n"
    result += f"End: {end}\n"
    result += f"Location: {location}\n"
    result += f"Organizer: {organizer}\n"
    result += f"Description: {body}"

    return result


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
    if response.status_code in [200, 201, 202, 204]:
        return format_success_response(success_message)
    else:
        return format_error_response(f"{error_prefix}: {response.text}")


def handle_event_not_found(event_id: str) -> Dict[str, Any]:
    """Handle case when event is not found"""
    return format_error_response(f"Event with ID {event_id} not found")


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


def get_datetime_range(days: int) -> tuple[str, str]:
    """Get start and end datetime strings for calendar view"""
    start_datetime = datetime.now().isoformat()
    end_datetime = (datetime.now() + timedelta(days=days)).isoformat()
    return start_datetime, end_datetime


def parse_start_time_with_duration(
    start_time: str, duration: int
) -> tuple[datetime, datetime]:
    """Parse start time and calculate end time with specified duration - accepts both formats"""
    # Try the expected format first (YYYY-MM-DD HH:MM)
    try:
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    except ValueError:
        # Try ISO format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM)
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
            except ValueError:
                raise ValueError(f"Invalid start time format: {start_time}. Expected YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM format")
    
    end_dt = start_dt + timedelta(minutes=duration)
    return start_dt, end_dt


def format_calendar_events_response(
    events: List[Dict[str, Any]], count: int, days: int
) -> str:
    """Format calendar events response for display"""
    if not events:
        return f"📅 No events found in the next {days} days."

    response = f"📅 Upcoming Calendar Events ({len(events)} of {count} requested):\n\n"

    for i, event in enumerate(events, 1):
        response += f"{i}. **{event['subject']}**\n"
        response += f"   🕐 Start: {event['start']}\n"
        response += f"   🕐 End: {event['end']}\n"
        response += f"   📍 Location: {event['location']}\n"
        response += f"   👤 Organizer: {event['organizer']}\n"
        response += f"   📝 Preview: {event['preview'][:100]}...\n\n"

    response += f"⏱️ Response Time: <3 seconds (target)"
    return response


def format_create_event_response(
    success: bool, message: str, subject: str, start_time: str
) -> str:
    """Format create event response for display"""
    if success:
        return f"✅ {message}\n📅 Event: {subject}\n🕐 Start: {start_time}\n⏱️ Response Time: <3 seconds (target)"
    else:
        return f"❌ {message}\n⏱️ Response Time: <3 seconds (target)"


def format_delete_event_response(success: bool, message: str, event_id: str) -> str:
    """Format delete event response for display"""
    if success:
        return f"✅ {message}\n🗑️ Deleted event ID: {event_id}\n⏱️ Response Time: <3 seconds (target)"
    else:
        return f"❌ {message}\n⏱️ Response Time: <3 seconds (target)"


def format_event_details_response(event_details: str) -> str:
    """Format event details response for display"""
    response = (
        f"📅 Event Details\n\n{event_details}\n\n⏱️ Response Time: <3 seconds (target)"
    )
    return response
