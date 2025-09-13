"""
SMS Retry Background Tasks

This module handles SMS retry-related background tasks.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from ..celery_app import app
from ...sms_router.services.simple_retry_service import SimpleSMSRetryService

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
async def process_sms_retries(self) -> Dict[str, Any]:
    """
    Process SMS retries every 2 minutes.

    This task:
    1. Processes pending retries that are due
    2. Attempts to resend failed SMS messages
    3. Updates retry status and schedules next attempts
    4. Logs processing statistics
    """
    task_id = self.request.id
    logger.info(f"Starting SMS retry processing task {task_id}")

    try:
        retry_service = SimpleSMSRetryService()
        stats = await retry_service.process_retry_queue()

        result = {
            "task_id": task_id,
            "status": "success",
            "processed": stats['processed'],
            "successful": stats['successful'],
            "failed": stats['failed'],
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"SMS retry processing completed: {result}")
        return result

    except Exception as e:
        logger.error(f"SMS retry processing failed: {e}")
        raise self.retry(countdown=300, max_retries=3)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
async def cleanup_old_retries(self) -> Dict[str, Any]:
    """
    Clean up old retry records.

    This task:
    1. Removes retry scheduling from records older than 7 days
    2. Logs cleanup statistics
    3. Helps maintain database performance
    """
    task_id = self.request.id
    logger.info(f"Starting SMS retry cleanup task {task_id}")

    try:
        retry_service = SimpleSMSRetryService()
        cleaned_count = await retry_service.cleanup_old_retries(days_old=7)

        result = {
            "task_id": task_id,
            "status": "success",
            "cleaned_records": cleaned_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"SMS retry cleanup completed: {result}")
        return result

    except Exception as e:
        logger.error(f"SMS retry cleanup failed: {e}")
        raise self.retry(countdown=300, max_retries=3)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
async def sms_retry_health_check(self) -> Dict[str, Any]:
    """
    Health check for SMS retry system.

    This task:
    1. Checks retry queue status
    2. Monitors retry success rates
    3. Alerts on high failure rates
    """
    task_id = self.request.id
    logger.info(f"Starting SMS retry health check task {task_id}")

    try:
        retry_service = SimpleSMSRetryService()

        # Get retry statistics
        from ...database.session import _get_session_factory
        session_factory = _get_session_factory()
        async with session_factory() as db:
            from sqlalchemy import func, select
            from ...sms_router.models.sms_models import SMSUsageLog

            # Count retries by status
            query = select(
                SMSUsageLog.final_status,
                func.count(SMSUsageLog.id).label('count')
            ).where(
                SMSUsageLog.retry_count > 0
            ).group_by(SMSUsageLog.final_status)

            result = await db.execute(query)
            status_counts = {row.final_status: row.count for row in result}

            # Calculate success rate
            total_retries = sum(status_counts.values())
            successful_retries = status_counts.get('sent', 0) + status_counts.get('delivered', 0)
            success_rate = (successful_retries / total_retries * 100) if total_retries > 0 else 0

            health_status = "healthy"
            if success_rate < 80:
                health_status = "warning"
            if success_rate < 60:
                health_status = "critical"

            result = {
                "task_id": task_id,
                "status": "success",
                "health_status": health_status,
                "success_rate": success_rate,
                "status_counts": status_counts,
                "total_retries": total_retries,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"SMS retry health check completed: {result}")
            return result

    except Exception as e:
        logger.error(f"SMS retry health check failed: {e}")
        raise self.retry(countdown=300, max_retries=3)
