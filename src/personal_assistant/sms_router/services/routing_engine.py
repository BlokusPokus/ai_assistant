"""
SMS Routing Engine - Core service for routing SMS messages.

This service orchestrates:
- User identification by phone number
- Message processing and spam detection
- Agent integration for response generation
- Response formatting and delivery
- Usage logging and analytics
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select

from ...database.session import AsyncSessionLocal
from ..models.sms_models import SMSUsageLog
from .agent_integration import AgentIntegrationService
from .message_processor import MessageProcessor
from .response_formatter import ResponseFormatter
from .user_identification import UserIdentificationService

logger = logging.getLogger(__name__)


class SMSRoutingEngine:
    """Main SMS routing engine that orchestrates the entire SMS processing pipeline."""

    def __init__(self):
        """Initialize the SMS routing engine."""
        self.user_identification = UserIdentificationService()
        self.message_processor = MessageProcessor()
        self.response_formatter = ResponseFormatter()
        self.agent_integration = AgentIntegrationService()

        # Performance tracking
        self.total_messages_processed = 0
        self.successful_routes = 0
        self.failed_routes = 0
        self.average_processing_time = 0.0

    async def route_sms(
        self, from_phone: str, message_body: str, message_sid: str
    ) -> Any:
        """
        Route an incoming SMS message through the complete pipeline.

        Args:
            from_phone: Sender's phone number
            message_body: SMS message content
            message_sid: Twilio message SID

        Returns:
            Formatted TwiML response
        """
        start_time = time.time()
        error_message = None

        try:
            logger.info(f"Processing SMS from {from_phone}: {message_body[:50]}...")

            # Step 1: Identify user
            user_info = await self.user_identification.identify_user_by_phone(
                from_phone
            )
            if not user_info:
                logger.warning(f"No user found for phone number: {from_phone}")
                response = self.response_formatter.format_unknown_user_response(
                    from_phone
                )
                await self._log_usage(
                    from_phone,
                    message_body,
                    "inbound",
                    False,
                    time.time() - start_time,
                    "User not found",
                )
                return response

            if not user_info.get("is_active", False):
                logger.warning(
                    f"Inactive user {user_info['id']} for phone: {from_phone}"
                )
                response = self.response_formatter.format_inactive_user_response(
                    user_info
                )
                await self._log_usage(
                    from_phone,
                    message_body,
                    "inbound",
                    False,
                    time.time() - start_time,
                    "Inactive user",
                )
                return response

            # Step 2: Process message
            processed_message = await self.message_processor.process_message(
                message_body, user_info
            )

            # Step 3: Check for spam
            if processed_message.get("is_spam", False):
                logger.warning(
                    f"Spam detected from {from_phone}: {message_body[:50]}..."
                )
                response = self.response_formatter.format_spam_response(user_info)

                # Log spam message and update statistics
                await self._log_usage(
                    from_phone,
                    message_body,
                    "inbound",
                    False,
                    time.time() - start_time,
                    "Spam detected",
                )

                # Update statistics for spam messages
                self.total_messages_processed += 1
                # Note: Spam messages are not counted as successful routes

                return response

            # Step 4: Process with agent
            agent_response = await self.agent_integration.process_with_agent(
                processed_message.get("cleaned_message", message_body), user_info
            )

            # Step 5: Format response
            response = self.response_formatter.format_response(
                agent_response, user_info
            )

            # Step 6: Log successful processing
            await self._log_usage(
                from_phone, message_body, "inbound", True, time.time() - start_time
            )

            # Update statistics
            self.total_messages_processed += 1
            self.successful_routes += 1

            logger.info(f"Successfully processed SMS for user {user_info['id']}")
            return response

        except Exception as e:
            error_message = str(e)
            logger.error(f"Error routing SMS from {from_phone}: {e}")

            # Update statistics
            self.total_messages_processed += 1
            self.failed_routes += 1

            # Return error response
            response = self.response_formatter.format_error_response(
                from_phone, error_message
            )

            # Log the error
            await self._log_usage(
                from_phone,
                message_body,
                "inbound",
                False,
                time.time() - start_time,
                error_message,
            )

            return response

        finally:
            # Update average processing time
            processing_time = time.time() - start_time
            if self.total_messages_processed > 0:
                self.average_processing_time = (
                    self.average_processing_time * (self.total_messages_processed - 1)
                    + processing_time
                ) / self.total_messages_processed

    async def send_sms(self, to_phone: str, message: str, user_id: int) -> bool:
        """
        Send an outbound SMS message.

        Args:
            to_phone: Recipient's phone number
            message: Message content
            user_id: Sender's user ID

        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()

        try:
            logger.info(f"Sending SMS to {to_phone} from user {user_id}")

            # TODO: Integrate with Twilio service for actual SMS sending
            # For now, just log the outbound message
            logger.info(f"Outbound SMS: {message[:50]}...")

            # Log the outbound message
            await self._log_usage(
                to_phone,
                message,
                "outbound",
                True,
                time.time() - start_time,
                user_id=user_id,
            )

            return True

        except Exception as e:
            logger.error(f"Error sending SMS to {to_phone}: {e}")
            await self._log_usage(
                to_phone,
                message,
                "outbound",
                False,
                time.time() - start_time,
                str(e),
                user_id,
            )
            return False

    async def _log_usage(
        self,
        phone_number: str,
        message_content: str,
        direction: str,
        success: bool,
        processing_time_ms: float,
        error_message: str = None,
        user_id: int = None,
    ) -> None:
        """Log SMS usage for analytics and monitoring."""
        try:
            async with AsyncSessionLocal() as session:
                # If no user_id provided, try to identify user
                if not user_id:
                    user_info = await self.user_identification.identify_user_by_phone(
                        phone_number
                    )
                    user_id = user_info["id"] if user_info else None

                usage_log = SMSUsageLog(
                    user_id=user_id,
                    phone_number=phone_number,
                    message_direction=direction,
                    message_length=len(message_content),
                    # Store content in column
                    message_content=message_content[:1000],
                    success=success,
                    # Convert to milliseconds
                    processing_time_ms=int(processing_time_ms * 1000),
                    error_message=error_message,
                    sms_metadata={
                        "direction": direction,
                        "timestamp": datetime.now().isoformat(),
                        "message_sid": None,
                    },
                )

                session.add(usage_log)
                await session.commit()

                logger.debug(f"Usage logged for {direction} SMS to/from {phone_number}")

        except Exception as e:
            logger.error(f"Error logging SMS usage: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the routing engine."""
        try:
            # Check database connectivity
            async with AsyncSessionLocal() as session:
                await session.execute(select(1))
                db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        # Check service dependencies
        services_status = {
            "user_identification": "healthy",
            "message_processor": "healthy",
            "response_formatter": "healthy",
            "agent_integration": "healthy",
        }

        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "services": services_status,
            "statistics": {
                "total_messages": self.total_messages_processed,
                "successful_routes": self.successful_routes,
                "failed_routes": self.failed_routes,
                "average_processing_time_ms": round(
                    self.average_processing_time * 1000, 2
                ),
            },
        }

    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics."""
        try:
            async with AsyncSessionLocal() as session:
                # Get recent usage statistics
                recent_stats = await session.execute(
                    select(
                        SMSUsageLog.message_direction,
                        SMSUsageLog.success,
                        SMSUsageLog.processing_time_ms,
                    )
                    .order_by(SMSUsageLog.created_at.desc())
                    .limit(100)
                )

                stats_data = recent_stats.fetchall()

                # Calculate statistics
                inbound_count = sum(1 for row in stats_data if row[0] == "inbound")
                outbound_count = sum(1 for row in stats_data if row[0] == "outbound")
                success_count = sum(1 for row in stats_data if row[1] is True)
                sum(1 for row in stats_data if row[1] is False)

                processing_times = [row[2] for row in stats_data if row[2] is not None]
                avg_processing_time = (
                    sum(processing_times) / len(processing_times)
                    if processing_times
                    else 0
                )

                return {
                    "timestamp": datetime.now().isoformat(),
                    "recent_activity": {
                        "total_messages": len(stats_data),
                        "inbound": inbound_count,
                        "outbound": outbound_count,
                        "success_rate": f"{(success_count / len(stats_data) * 100):.1f}%"
                        if stats_data
                        else "0%",
                    },
                    "performance": {
                        "average_processing_time_ms": round(avg_processing_time, 2),
                        "total_processed": self.total_messages_processed,
                        "successful_routes": self.successful_routes,
                        "failed_routes": self.failed_routes,
                    },
                }

        except Exception as e:
            logger.error(f"Error getting routing stats: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def get_user_routing_history(
        self, user_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get routing history for a specific user."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(SMSUsageLog)
                    .where(SMSUsageLog.user_id == user_id)
                    .order_by(SMSUsageLog.created_at.desc())
                    .limit(limit)
                )

                logs = result.scalars().all()

                return [
                    {
                        "id": log.id,
                        "phone_number": log.phone_number,
                        "direction": log.message_direction,
                        "message_length": log.message_length,
                        "success": log.success,
                        "processing_time_ms": log.processing_time_ms,
                        "created_at": log.created_at.isoformat()
                        if log.created_at
                        else None,
                        "error_message": log.error_message,
                    }
                    for log in logs
                ]

        except Exception as e:
            logger.error(f"Error getting routing history for user {user_id}: {e}")
            return []
