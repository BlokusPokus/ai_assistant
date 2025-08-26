"""
SMS Router Service for Personal Assistant.

This service enables multi-user SMS functionality using a single Twilio number.
It routes incoming SMS messages to the correct user agent based on phone number identification,
maintaining strict user isolation and supporting 10,000+ users efficiently.
"""

from .config import settings

# Import services only when needed to avoid circular dependencies
__all__ = [
    "settings"
]

__version__ = "1.0.0"
__all__ = [
    "settings",
    "SMSRoutingEngine", 
    "UserIdentificationService",
    "AgentIntegrationService"
]
