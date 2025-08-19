from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import PlainTextResponse
from typing import Optional
from pydantic import BaseModel
from personal_assistant.config.settings import settings
from personal_assistant.llm.gemini import GeminiLLM
from personal_assistant.tools import create_tool_registry
from personal_assistant.communication.twilio_integration.twilio_client import TwilioService
from personal_assistant.core import AgentCore
from fastapi.responses import Response
router = APIRouter(prefix="/twilio", tags=["twilio"])

# Dependency to get TwilioService instance


async def get_twilio_service():
    tool_registry = create_tool_registry()
    agent_core = AgentCore(tools=tool_registry,
                           llm=GeminiLLM(api_key=settings.GOOGLE_API_KEY, model="gemini-2.0-flash"))
    return TwilioService(agent_core)


class SMSRequest(BaseModel):
    to: str
    message: str


@router.post("/sms", response_class=PlainTextResponse)
async def twilio_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    twilio_service: TwilioService = Depends(get_twilio_service)
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
async def send_sms(
    request: SMSRequest,
    twilio_service: TwilioService = Depends(get_twilio_service)
):
    """
    Endpoint to send SMS messages through Twilio.
    """
    try:
        message_sid = await twilio_service.send_sms(request.to, request.message)
        return {"status": "success", "message_sid": message_sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
