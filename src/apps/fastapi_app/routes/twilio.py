from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.auth.decorators import require_permission
from personal_assistant.communication.twilio_integration.twilio_client import (
    TwilioService,
)
from personal_assistant.config.settings import settings
from personal_assistant.core import AgentCore
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.llm.gemini import GeminiLLM
from personal_assistant.tools import create_tool_registry

router = APIRouter(prefix="/twilio", tags=["twilio"])

# Database dependency


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


# Authentication dependency


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    if not hasattr(request.state, "authenticated") or not request.state.authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = request.state.user_id
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# Dependency to get TwilioService instance


async def get_twilio_service():
    tool_registry = create_tool_registry()
    agent_core = AgentCore(
        tools=tool_registry,
        llm=GeminiLLM(api_key=settings.GOOGLE_API_KEY, model="gemini-2.0-flash"),
    )
    return TwilioService(agent_core)


class SMSRequest(BaseModel):
    to: str
    message: str


@router.post("/sms", response_class=PlainTextResponse)
async def twilio_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    twilio_service: TwilioService = Depends(get_twilio_service),
):
    """
    Webhook endpoint for receiving SMS messages from Twilio.
    Returns TwiML response.
    """
    try:
        response = await twilio_service.handle_sms_webhook(Body, From)
        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send", response_model=dict)
@require_permission("system", "send_sms")
async def send_sms(
    request_obj: Request,
    request: SMSRequest,
    current_user: User = Depends(get_current_user),
    twilio_service: TwilioService = Depends(get_twilio_service),
):
    """
    Endpoint to send SMS messages through Twilio.
    """
    try:
        message_sid = await twilio_service.send_sms(request.to, request.message)
        return {"status": "success", "message_sid": message_sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
