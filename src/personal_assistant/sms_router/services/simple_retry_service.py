"""
Simplified SMS Retry Service

This module provides a simplified SMS retry service using existing infrastructure.
It leverages the SMSUsageLog table and Celery's built-in retry mechanisms.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...communication.twilio_integration.twilio_client import TwilioService
from ...database.session import _get_session_factory
from ..models.sms_models import SMSUsageLog
from .error_classifier import SMSErrorClassifier

logger = logging.getLogger(__name__)


class SimpleSMSRetryService:
    """Simplified SMS retry service using existing infrastructure."""

    def __init__(self):
        self.twilio_service = TwilioService()
        self.error_classifier = SMSErrorClassifier()
        self.max_batch_size = 50

    async def queue_for_retry(
        self, 
        sms_log_id: int, 
        error_code: str, 
        error_message: str
    ) -> bool:
        """
        Queue a failed SMS for retry using existing SMSUsageLog record.
        
        Args:
            sms_log_id: ID of the SMS log entry to retry
            error_code: Twilio error code
            error_message: Error message from Twilio
            
        Returns:
            bool: True if queued for retry, False if not retryable
        """
        if not self.error_classifier.is_retryable(error_code):
            logger.info(f"SMS error {error_code} is not retryable: {error_message}")
            return False

        retry_config = self.error_classifier.get_retry_strategy(error_code)
        if not retry_config:
            return False

        try:
            session_factory = _get_session_factory()
            async with session_factory() as db:
                sms_log = await db.get(SMSUsageLog, sms_log_id)
                if not sms_log:
                    logger.error(f"SMS log {sms_log_id} not found")
                    return False

                # Update existing record for retry
                sms_log.retry_count = 1
                sms_log.max_retries = retry_config['max_retries']
                sms_log.next_retry_at = datetime.utcnow() + timedelta(
                    seconds=self.error_classifier.calculate_retry_delay(error_code, 0)
                )
                sms_log.sms_metadata = sms_log.sms_metadata or {}
                sms_log.sms_metadata.update({
                    'retry_reason': error_code,
                    'retry_error': error_message,
                    'retry_strategy': 'exponential_backoff'
                })

                await db.commit()
                logger.info(f"Queued SMS {sms_log_id} for retry due to error {error_code}")
                return True

        except Exception as e:
            logger.error(f"Failed to queue SMS {sms_log_id} for retry: {e}")
            return False

    async def process_retry_queue(self) -> Dict[str, int]:
        """
        Process failed SMS records that are ready for retry.
        
        Returns:
            dict: Processing statistics
        """
        stats = {'processed': 0, 'successful': 0, 'failed': 0}

        try:
            session_factory = _get_session_factory()
            async with session_factory() as db:
                # Get failed SMS records ready for retry
                now = datetime.utcnow()
                query = select(SMSUsageLog).where(
                    and_(
                        SMSUsageLog.success == False,
                        SMSUsageLog.retry_count < SMSUsageLog.max_retries,
                        SMSUsageLog.next_retry_at <= now
                    )
                ).limit(self.max_batch_size)

                result = await db.execute(query)
                failed_sms = result.scalars().all()

                logger.info(f"Processing {len(failed_sms)} SMS retries")

                for sms_log in failed_sms:
                    try:
                        # Attempt to resend
                        message_sid = await self.twilio_service.send_sms(
                            sms_log.phone_number, 
                            sms_log.message_content
                        )

                        # Update on success
                        sms_log.success = True
                        sms_log.twilio_message_sid = message_sid
                        sms_log.final_status = 'sent'
                        sms_log.next_retry_at = None
                        stats['successful'] += 1
                        logger.info(f"SMS retry successful: {sms_log.id}, SID: {message_sid}")

                    except Exception as e:
                        # Handle retry failure
                        sms_log.retry_count += 1
                        sms_log.error_message = str(e)

                        if sms_log.retry_count >= sms_log.max_retries:
                            sms_log.final_status = 'failed'
                            sms_log.next_retry_at = None
                            logger.warning(f"SMS retry failed after {sms_log.max_retries} attempts: {sms_log.id}")
                        else:
                            # Schedule next retry with exponential backoff
                            delay = 60 * (2 ** (sms_log.retry_count - 1))
                            sms_log.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                            logger.info(f"SMS retry scheduled for {sms_log.next_retry_at}: {sms_log.id}")

                        stats['failed'] += 1

                    stats['processed'] += 1

                await db.commit()

        except Exception as e:
            logger.error(f"Error processing retry queue: {e}")

        logger.info(f"Retry queue processing completed: {stats}")
        return stats

    async def handle_delivery_confirmation(self, message_sid: str, status: str) -> bool:
        """
        Handle Twilio delivery status webhooks.
        
        Args:
            message_sid: Twilio message SID
            status: Delivery status from Twilio
            
        Returns:
            bool: True if status was updated successfully
        """
        try:
            session_factory = _get_session_factory()
            async with session_factory() as db:
                # Find SMS log by message SID
                query = select(SMSUsageLog).where(
                    SMSUsageLog.twilio_message_sid == message_sid
                )
                result = await db.execute(query)
                sms_log = result.scalar_one_or_none()

                if sms_log:
                    sms_log.final_status = status
                    await db.commit()
                    logger.info(f"Updated delivery status for SMS log {sms_log.id}: {status}")
                    return True

                logger.warning(f"No SMS record found for message SID: {message_sid}")
                return False

        except Exception as e:
            logger.error(f"Error handling delivery confirmation: {e}")
            return False

    async def cleanup_old_retries(self, days_old: int = 7) -> int:
        """
        Clean up old retry records.
        
        Args:
            days_old: Number of days after which to clean up records
            
        Returns:
            int: Number of records cleaned up
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            session_factory = _get_session_factory()
            async with session_factory() as db:
                # Update old retry records to remove retry scheduling
                query = select(SMSUsageLog).where(
                    and_(
                        SMSUsageLog.created_at < cutoff_date,
                        SMSUsageLog.next_retry_at.isnot(None)
                    )
                )
                result = await db.execute(query)
                old_retries = result.scalars().all()

                count = len(old_retries)
                for sms_log in old_retries:
                    sms_log.next_retry_at = None
                    if sms_log.final_status == 'unknown':
                        sms_log.final_status = 'failed'

                await db.commit()

                logger.info(f"Cleaned up {count} old retry records")
                return count

        except Exception as e:
            logger.error(f"Error cleaning up old retries: {e}")
            return 0
