from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

from ..base import Tool
from ..emails.ms_graph import get_access_token

# Import calendar-specific error handling
from .calendar_error_handler import CalendarErrorHandler
from .calendar_internal import (
    build_calendar_headers,
    build_calendar_view_params,
    build_event_data,
    format_event_details_response,
    format_success_response,
    get_datetime_range,
    get_environment_error_message,
    handle_event_not_found,
    parse_calendar_event,
    parse_event_details,
    parse_start_time_with_duration,
    validate_calendar_parameters,
    validate_duration,
    validate_environment_variables,
    validate_event_id,
    validate_location,
    validate_start_time,
    validate_subject,
)


class CalendarTool:
    def __init__(self):
        load_dotenv()
        self.ms_graph_url = "https://graph.microsoft.com/v1.0"
        self._access_token = None
        self.scopes = ["Calendars.Read", "Calendars.ReadWrite", "User.Read"]
        # Don't initialize token here - do it lazily when needed

        # Create individual tools
        self.view_calendar_events_tool = Tool(
            name="view_calendar_events",
            func=self.get_events,
            description="View upcoming calendar events",
            parameters={
                "count": {
                    "type": "integer",
                    "description": "Number of events to fetch",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look ahead",
                },
            },
        )

        self.create_calendar_event_tool = Tool(
            name="create_calendar_event",
            func=self.create_calendar_event,
            description="Create a new calendar event or reminder. Use 'subject' for the event title, 'start_time' for when it starts, and 'duration' for how long it lasts (in minutes).",
            parameters={
                "subject": {"type": "string", "description": "Event title/subject (use this parameter name, not 'title')"},
                "start_time": {
                    "type": "string",
                    "description": "Start time in YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM format (e.g., '2024-01-15 14:30' or '2024-01-15T14:30'). Use this parameter name, not 'time' or 'date'.",
                },
                "duration": {"type": "integer", "description": "Duration in minutes (use this parameter name, not 'end_time')"},
                "location": {"type": "string", "description": "Location of the event"},
                "attendees": {
                    "type": "string",
                    "description": "Comma-separated list of attendee email addresses (e.g., 'user@example.com,user2@example.com')",
                },
            },
        )

        self.delete_calendar_event_tool = Tool(
            name="delete_calendar_event",
            func=self.delete_calendar_event,
            description="Delete a specific calendar event by its ID. Use this to delete individual events. The response will clearly indicate which event was deleted by name/subject to help you track progress.",
            parameters={
                "event_id": {
                    "type": "string",
                    "description": "The ID of the specific event to delete (get this from view_calendar_events first)",
                }
            },
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter(
            [
                self.view_calendar_events_tool,
                self.create_calendar_event_tool,
                self.delete_calendar_event_tool,
            ]
        )

    def _initialize_token(self):
        """Initialize the access token using environment variables"""
        is_valid, application_id, client_secret = validate_environment_variables()

        if not is_valid:
            raise ValueError(get_environment_error_message())

        self._access_token = get_access_token(
            application_id, client_secret, self.scopes
        )

    async def get_events(self, count: int = 5, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming calendar events"""
        if not self._access_token:
            self._initialize_token()

        try:
            # Validate parameters using internal functions
            count, days = validate_calendar_parameters(count, days)

            headers = build_calendar_headers(self._access_token)

            # Get datetime range using internal function
            start_datetime, end_datetime = get_datetime_range(days)

            # Build query parameters using internal function
            params = build_calendar_view_params(start_datetime, end_datetime, count)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/calendarView",
                    headers=headers,
                    params=params,
                )

                if response.status_code != 200:
                    # Use calendar-specific error handling for HTTP errors
                    return [
                        CalendarErrorHandler.handle_calendar_error(
                            Exception(f"HTTP {response.status_code}: {response.text}"),
                            "view_calendar_events",
                            {"count": count, "days": days},
                        )
                    ]

                data = response.json()
                events = data.get("value", [])

                if not events:
                    return [{"message": f"No events found in the next {days} days."}]

                # Parse events using internal function
                parsed_events = [
                    parse_calendar_event(event) for event in events[:count]
                ]
                return parsed_events

        except Exception as e:
            # Use calendar-specific error handling for all exceptions
            return [
                CalendarErrorHandler.handle_calendar_error(
                    e, "view_calendar_events", {"count": count, "days": days}
                )
            ]

    async def create_calendar_event(
        self,
        subject: str,
        start_time: str,
        duration: int = 60,
        location: str = "",
        attendees: str = "",
    ) -> Dict[str, Any]:
        """Create a new calendar event"""
        if not self._access_token:
            self._initialize_token()

        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_subject(subject)
            if not is_valid:
                return CalendarErrorHandler.handle_calendar_error(
                    ValueError(error_msg),
                    "create_calendar_event",
                    {
                        "subject": subject,
                        "start_time": start_time,
                        "duration": duration,
                        "location": location,
                        "attendees": attendees,
                    },
                )

            is_valid, error_msg = validate_start_time(start_time)
            if not is_valid:
                return CalendarErrorHandler.handle_calendar_error(
                    ValueError(error_msg),
                    "create_calendar_event",
                    {
                        "subject": subject,
                        "start_time": start_time,
                        "duration": duration,
                        "location": location,
                        "attendees": attendees,
                    },
                )

            is_valid, error_msg = validate_duration(duration)
            if not is_valid:
                return CalendarErrorHandler.handle_calendar_error(
                    ValueError(error_msg),
                    "create_calendar_event",
                    {
                        "subject": subject,
                        "start_time": start_time,
                        "duration": duration,
                        "location": location,
                        "attendees": attendees,
                    },
                )

            is_valid, error_msg = validate_location(location)
            if not is_valid:
                return CalendarErrorHandler.handle_calendar_error(
                    ValueError(error_msg),
                    "create_calendar_event",
                    {
                        "subject": subject,
                        "start_time": start_time,
                        "duration": duration,
                        "location": location,
                        "attendees": attendees,
                    },
                )

            headers = build_calendar_headers(self._access_token, "application/json")

            # Parse start time and calculate end time using internal function
            start_dt, end_dt = parse_start_time_with_duration(start_time, duration)

            # Build event data using internal function
            event_data = build_event_data(subject, start_dt, end_dt, location)

            # Add attendees if provided
            if attendees:
                attendee_emails = [
                    email.strip() for email in attendees.split(",") if email.strip()
                ]
                if attendee_emails:
                    event_data["attendees"] = [
                        {"emailAddress": {"address": email}}
                        for email in attendee_emails
                    ]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ms_graph_url}/me/events", headers=headers, json=event_data
                )

                if response.status_code in [200, 201]:
                    attendee_info = ""
                    if attendees:
                        attendee_emails = [
                            email.strip()
                            for email in attendees.split(",")
                            if email.strip()
                        ]
                        if attendee_emails:
                            attendee_info = f" with {len(attendee_emails)} attendee(s): {', '.join(attendee_emails)}"

                    return format_success_response(
                        f"Successfully created event '{subject}' at {start_time}{attendee_info}",
                        response.json(),
                    )
                else:
                    # Use calendar-specific error handling for HTTP errors
                    return CalendarErrorHandler.handle_calendar_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "create_calendar_event",
                        {
                            "subject": subject,
                            "start_time": start_time,
                            "duration": duration,
                            "location": location,
                            "attendees": attendees,
                        },
                    )

        except ValueError as e:
            # Use calendar-specific error handling for validation errors
            return CalendarErrorHandler.handle_calendar_error(
                e,
                "create_calendar_event",
                {
                    "subject": subject,
                    "start_time": start_time,
                    "duration": duration,
                    "location": location,
                    "attendees": attendees,
                },
            )
        except Exception as e:
            # Use calendar-specific error handling for all other exceptions
            return CalendarErrorHandler.handle_calendar_error(
                e,
                "create_calendar_event",
                {
                    "subject": subject,
                    "start_time": start_time,
                    "duration": duration,
                    "location": location,
                    "attendees": attendees,
                },
            )

    async def get_event_details(self, event_id: str) -> str:
        """
        Get detailed information about a specific event.

        Args:
            event_id: ID of the event to retrieve

        Returns:
            Detailed event information
        """
        if not self._access_token:
            self._initialize_token()

        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_event_id(event_id)
            if not is_valid:
                error_response = CalendarErrorHandler.handle_calendar_error(
                    ValueError(error_msg), "get_event_details", {"event_id": event_id}
                )
                return error_response["llm_instructions"]  # type: ignore

            headers = build_calendar_headers(self._access_token)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/events/{event_id}", headers=headers
                )

                if response.status_code != 200:
                    error_response = CalendarErrorHandler.handle_calendar_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "get_event_details",
                        {"event_id": event_id},
                    )
                    return error_response["llm_instructions"]  # type: ignore

                event = response.json()

                # Parse event details using internal function
                event_details = parse_event_details(event)
                return format_event_details_response(event_details)

        except Exception as e:
            error_response = CalendarErrorHandler.handle_calendar_error(
                e, "get_event_details", {"event_id": event_id}
            )
            return error_response["llm_instructions"]  # type: ignore

    async def delete_calendar_event(self, event_id: str) -> Dict[str, Any]:
        """Delete a calendar event"""
        if not self._access_token:
            self._initialize_token()

        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_event_id(event_id)
            if not is_valid:
                return CalendarErrorHandler.handle_calendar_error(
                    ValueError(error_msg),
                    "delete_calendar_event",
                    {"event_id": event_id},
                )

            headers = build_calendar_headers(self._access_token)

            # First, get event details before deletion for better response
            event_details = None
            try:
                async with httpx.AsyncClient() as client:
                    get_response = await client.get(
                        f"{self.ms_graph_url}/me/events/{event_id}", headers=headers
                    )
                    if get_response.status_code == 200:
                        event_data = get_response.json()
                        event_details = {
                            "subject": event_data.get("subject", "Untitled Event"),
                            "start": event_data.get("start", {}).get("dateTime", "Unknown"),
                            "location": event_data.get("location", {}).get("displayName", "No location")
                        }
            except Exception:
                # If we can't get event details, continue with deletion anyway
                pass

            # Now delete the event
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.ms_graph_url}/me/events/{event_id}", headers=headers
                )

                if response.status_code == 204:  # No content on successful deletion
                    # Create a more informative success message
                    if event_details:
                        message = f"✅ Successfully deleted event: '{event_details['subject']}'"
                        message += f"\n📅 Start time: {event_details['start']}"
                        if event_details['location'] != "No location":
                            message += f"\n📍 Location: {event_details['location']}"
                        message += f"\n🆔 Event ID: {event_id[:20]}..."
                    else:
                        message = f"✅ Successfully deleted event with ID: {event_id[:20]}..."
                    
                    return format_success_response(message, {"deleted_event": event_details})
                elif response.status_code == 404:
                    return handle_event_not_found(event_id)
                else:
                    return CalendarErrorHandler.handle_calendar_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "delete_calendar_event",
                        {"event_id": event_id},
                    )

        except Exception as e:
            return CalendarErrorHandler.handle_calendar_error(
                e, "delete_calendar_event", {"event_id": event_id}
            )
