"""
Webhook routes for SMS Router Service.
"""

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

from personal_assistant.sms_router.middleware.webhook_validation import validate_twilio_webhook
from personal_assistant.sms_router.services.routing_engine import SMSRoutingEngine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sms")
async def twilio_sms_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    MessageSid: str = Form(...),
    routing_engine: SMSRoutingEngine = Depends()
):
    """
    Handle incoming SMS webhook from Twilio.

    Args:
        Body: SMS message content
        From: Sender's phone number
        To: Recipient's phone number (our Twilio number)
        MessageSid: Twilio message SID
        routing_engine: SMS routing engine instance
    """
    try:
        # Validate webhook (optional security measure)
        if not validate_twilio_webhook(request):
            logger.warning(
                f"Invalid webhook request from {request.client.host}")
            raise HTTPException(status_code=400, detail="Invalid webhook")

        logger.info(f"Processing SMS from {From}: {Body[:50]}...")

        # Route the SMS through the routing engine
        response = await routing_engine.route_sms(From, Body, MessageSid)

        # Return TwiML response
        return Response(
            content=str(response),
            media_type="application/xml"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def webhook_health_check(
    routing_engine: SMSRoutingEngine = Depends()
):
    """Health check endpoint for SMS Router webhook service."""
    try:
        health_status = await routing_engine.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/stats")
async def webhook_stats(
    routing_engine: SMSRoutingEngine = Depends()
):
    """Get routing engine statistics."""
    try:
        stats = await routing_engine.get_routing_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
