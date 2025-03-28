from typing import Dict, Any, List
from agent_core.tools.base import Tool
import httpx
import os
from .ms_graph import get_access_token
from dotenv import load_dotenv


class EmailTool(Tool):
    def __init__(self, name: str = "email"):
        super().__init__(
            name=name,
            func=self.read_recent_emails,  # Default function
            description="Tool for reading and sending emails",
            parameters={
                "count": {
                    "type": "integer",
                    "description": "Number of emails to fetch",
                    "default": 5
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Number of emails per batch",
                    "default": 2
                }
            }
        )
        load_dotenv()  # Ensure environment variables are loaded
        self.ms_graph_url = "https://graph.microsoft.com/v1.0"
        self._access_token = None
        # Reuse the comprehensive scope list from ms_graph.py
        self.scopes = [
            "Mail.Read",
            "Mail.ReadWrite",
            "Mail.Send",
            "User.Read"
        ]

        # Initialize token right away using the existing refresh token
        self._initialize_token()

    def _initialize_token(self):
        """Initialize the access token using environment variables"""
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

    async def read_recent_emails(self, count: int = 5, batch_size: int = 2) -> List[Dict[str, Any]]:
        """
        Read recent emails using the pagination logic from emails.py
        """
        if not self._access_token:
            self._initialize_token()

        headers = {"Authorization": f"Bearer {self._access_token}"}
        emails = []

        # Reuse the pagination logic from emails.py
        for i in range(0, count, batch_size):
            params = {
                '$top': min(batch_size, count - i),
                '$select': '*',
                '$skip': i,
                '$orderby': 'receivedDateTime desc'
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ms_graph_url}/me/messages",
                    headers=headers,
                    params=params
                )

                if response.status_code != 200:
                    raise Exception(f"Failed to get messages: {response.text}")

                for mail in response.json().get('value', []):
                    if not mail.get('isDraft'):
                        # Reuse the email structure from emails.py
                        emails.append({
                            'subject': mail['subject'],
                            'preview': mail['bodyPreview'],
                            'received': mail['receivedDateTime'],
                            'from_name': mail['from']['emailAddress']['name'],
                            'from_email': mail['from']['emailAddress']['address']
                        })

                if len(emails) >= count:
                    break

        return emails[:count]
