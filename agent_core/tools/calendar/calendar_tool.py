import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from agent_core.tools.base import Tool
import httpx
from agent_core.tools.emails.ms_graph import get_access_token
from dotenv import load_dotenv

# Placeholder for an actual calendar client


class CalendarClient:
    async def get_events(self, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: int = 5) -> List[dict]:
        """Get calendar events within a date range"""
        # Implementation would connect to a calendar service
        start = start_date or datetime.now()
        end = end_date or (start + timedelta(days=7))

        # Mock data for demonstration
        return [
            {
                "id": f"event_{i}",
                "title": f"Meeting {i}",
                "start": start + timedelta(days=i, hours=i),
                "end": start + timedelta(days=i, hours=i+1),
                "location": "Conference Room" if i % 2 == 0 else "Virtual",
                "description": f"Discussion about project {i}"
            } for i in range(limit)
        ]

    async def create_event(self, title: str, start_time: datetime,
                           end_time: datetime, description: str = "",
                           location: str = "") -> dict:
        """Create a new calendar event"""
        # Implementation would connect to a calendar service
        return {
            "status": "created",
            "id": f"event_{hash(title) % 10000}",
            "title": title,
            "start": start_time,
            "end": end_time,
            "location": location,
            "description": description
        }

    async def get_event_details(self, event_id: str) -> dict:
        """Get detailed information about a specific event"""
        # Implementation would connect to a calendar service
        # Mock data for demonstration
        return {
            "id": event_id,
            "title": f"Meeting about {event_id}",
            "start": datetime.now() + timedelta(days=1),
            "end": datetime.now() + timedelta(days=1, hours=1),
            "location": "Conference Room A",
            "description": "Detailed discussion about project progress",
            "attendees": ["john@example.com", "jane@example.com"]
        }


class CalendarTool(Tool):
    def __init__(self, name: str = "calendar"):
        super().__init__(
            name=name,
            func=self.handle_calendar_action,  # Use a handler function
            description="Tool for viewing and creating calendar events",
            parameters={
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'view' to see events, 'create' to add new event",
                    "enum": ["view", "create"]
                },
                "count": {
                    "type": "integer",
                    "description": "Number of events to fetch (for view action)"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look ahead (for view action)"
                },
                "subject": {
                    "type": "string",
                    "description": "Title of the event (for create action)"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in YYYY-MM-DD HH:MM format (for create action)"
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration in minutes (for create action)"
                },
                "location": {
                    "type": "string",
                    "description": "Location of the event (for create action)"
                }
            }
        )
        load_dotenv()
        self.ms_graph_url = "https://graph.microsoft.com/v1.0"
        self._access_token = None
        self.scopes = ["Calendars.Read", "Calendars.ReadWrite", "User.Read"]
        self._initialize_token()

    def _initialize_token(self):
        application_id = os.getenv("MICROSOFT_APPLICATION_ID")
        client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")

        if not application_id or not client_secret:
            raise ValueError(
                "Missing required environment variables: "
                "MICROSOFT_APPLICATION_ID and MICROSOFT_CLIENT_SECRET"
            )

        self._access_token = get_access_token(
            application_id,
            client_secret,
            self.scopes
        )

    async def handle_calendar_action(self, action: str, **kwargs) -> List[Dict[str, Any]]:
        """Handle different calendar actions"""
        if action == "view":
            return await self.get_events(
                count=kwargs.get('count', 5),
                days=kwargs.get('days', 7)
            )
        elif action == "create":
            result = await self.create_event(
                subject=kwargs.get('subject'),
                start_time=kwargs.get('start_time'),
                duration=kwargs.get('duration', 60),
                location=kwargs.get('location', '')
            )
            return [result]  # Wrap in list to match return type
        else:
            return [{"error": f"Unknown action: {action}"}]

    async def get_events(self, count: int = 5, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming calendar events"""
        if not self._access_token:
            self._initialize_token()

        try:
            headers = {"Authorization": f"Bearer {self._access_token}"}

            start_datetime = datetime.now().isoformat()
            end_datetime = (datetime.now() + timedelta(days=days)).isoformat()

            params = {
                'startDateTime': start_datetime,
                'endDateTime': end_datetime,
                '$top': count,
                '$orderby': 'start/dateTime asc',
                '$select': 'subject,start,end,location,bodyPreview,organizer'
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/calendarView",
                    headers=headers,
                    params=params
                )

                if response.status_code != 200:
                    return [{"error": f"Failed to get calendar events: {response.text}"}]

                data = response.json()
                events = data.get('value', [])

                if not events:
                    return [{"message": f"No events found in the next {days} days."}]

                return [{
                    'subject': event.get('subject', 'Untitled Event'),
                    'start': event.get('start', {}).get('dateTime', ''),
                    'end': event.get('end', {}).get('dateTime', ''),
                    'location': event.get('location', {}).get('displayName', 'No location'),
                    'preview': event.get('bodyPreview', ''),
                    'organizer': event.get('organizer', {}).get('emailAddress', {}).get('name', 'Unknown')
                } for event in events[:count]]

        except Exception as e:
            return [{"error": f"Error retrieving calendar events: {str(e)}"}]

    async def create_event(self, subject: str, start_time: str,
                           duration: int = 60, location: str = "") -> Dict[str, Any]:
        """Create a new calendar event"""
        if not self._access_token:
            self._initialize_token()

        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }

            # Parse start time
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=duration)

            event_data = {
                "subject": subject,
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "UTC"
                }
            }

            if location:
                event_data["location"] = {"displayName": location}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ms_graph_url}/me/events",
                    headers=headers,
                    json=event_data
                )

                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "message": f"Successfully created event '{subject}' at {start_time}",
                        "event": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create event: {response.text}"
                    }

        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid date format. Please use YYYY-MM-DD HH:MM format: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating calendar event: {str(e)}"
            }

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
            headers = {"Authorization": f"Bearer {self._access_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/events/{event_id}",
                    headers=headers
                )

                if response.status_code != 200:
                    return f"Failed to get event details: {response.text}"

                event = response.json()

                # Format the result
                start = event.get('start', {}).get('dateTime', 'Unknown')
                end = event.get('end', {}).get('dateTime', 'Unknown')
                subject = event.get('subject', 'Untitled Event')
                body = event.get('body', {}).get('content', 'No description')
                location = event.get('location', {}).get(
                    'displayName', 'No location')
                organizer = event.get('organizer', {}).get(
                    'emailAddress', {}).get('name', 'Unknown')

                result = f"Event: {subject}\n"
                result += f"Start: {start}\n"
                result += f"End: {end}\n"
                result += f"Location: {location}\n"
                result += f"Organizer: {organizer}\n"
                result += f"Description: {body}"

                return result

        except Exception as e:
            return f"Error retrieving event details: {str(e)}"
