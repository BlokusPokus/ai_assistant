"""
Outlook Calendar integration using Microsoft Graph API.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from msal import ConfidentialClientApplication
from msgraph.core import GraphClient
from tenacity import retry, stop_after_attempt, wait_exponential
from ..base import Tool

# Configuration and Models


@dataclass
class OutlookConfig:
    CLIENT_ID: str
    CLIENT_SECRET: str
    TENANT_ID: str
    SCOPES: list[str] = field(default_factory=lambda: [
        'https://graph.microsoft.com/Calendars.ReadWrite'
    ])


@dataclass
class CalendarEvent:
    subject: str
    start: datetime
    end: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    is_reminder_set: bool = False
    reminder_minutes_before: Optional[int] = None
    id: Optional[str] = None

# Service Implementation


class OutlookCalendarService:
    def __init__(self, config: OutlookConfig):
        self.config = config
        self.app = ConfidentialClientApplication(
            client_id=config.CLIENT_ID,
            client_credential=config.CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/{config.TENANT_ID}"
        )
        self.client = None
        self._token = None

    async def _get_token(self) -> str:
        if not self._token:
            result = await self.app.acquire_token_for_client(
                scopes=self.config.SCOPES
            )
            self._token = result['access_token']
        return self._token

    async def _get_client(self) -> GraphClient:
        if not self.client:
            token = await self._get_token()
            self.client = GraphClient(token)
        return self.client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create a new calendar event"""
        client = await self._get_client()
        # TODO: Implement Microsoft Graph API call
        return event

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent:
        """Update an existing calendar event"""
        client = await self._get_client()
        # TODO: Implement Microsoft Graph API call
        return event

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        client = await self._get_client()
        # TODO: Implement Microsoft Graph API call
        return True

    async def check_availability(self, start: datetime, end: datetime) -> List[dict]:
        """Check availability for a time period"""
        client = await self._get_client()
        # TODO: Implement Microsoft Graph API call
        return []

# Tool Interface


def create_calendar_service(client_id: str, client_secret: str, tenant_id: str) -> OutlookCalendarService:
    """Helper to create calendar service instance"""
    config = OutlookConfig(
        CLIENT_ID=client_id,
        CLIENT_SECRET=client_secret,
        TENANT_ID=tenant_id
    )
    return OutlookCalendarService(config)

# Tool definitions for LLM


async def create_event(service: OutlookCalendarService,
                       subject: str,
                       start_time: str,
                       end_time: str,
                       description: Optional[str] = None,
                       reminder_minutes: Optional[int] = None) -> str:
    """Create a calendar event"""
    event = CalendarEvent(
        subject=subject,
        start=datetime.fromisoformat(start_time),
        end=datetime.fromisoformat(end_time),
        description=description,
        is_reminder_set=reminder_minutes is not None,
        reminder_minutes_before=reminder_minutes
    )

    created_event = await service.create_event(event)
    return f"Created event '{created_event.subject}' from {created_event.start} to {created_event.end}"

CalendarCreateTool = Tool(
    name="create_event",
    func=create_event,
    description="Create a new calendar event",
    parameters={
        "subject": {
            "type": "string",
            "description": "Subject/title of the event"
        },
        "start_time": {
            "type": "string",
            "description": "Start time in ISO format (YYYY-MM-DDTHH:MM:SS)"
        },
        "end_time": {
            "type": "string",
            "description": "End time in ISO format (YYYY-MM-DDTHH:MM:SS)"
        },
        "description": {
            "type": "string",
            "description": "Optional event description",
            "optional": True
        },
        "reminder_minutes": {
            "type": "integer",
            "description": "Optional minutes before event for reminder",
            "optional": True
        }
    }
)
