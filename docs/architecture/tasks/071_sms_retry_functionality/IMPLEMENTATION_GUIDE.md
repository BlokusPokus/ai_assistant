# Task 071: SMS Retry Functionality - Implementation Guide

## **📋 Implementation Overview**

This guide provides step-by-step instructions for implementing comprehensive SMS retry functionality to ensure reliable message delivery.

## **🏗️ Phase 1: Database Schema Enhancement**

### **1.1 Create Database Migration**

**File**: `src/personal_assistant/database/migrations/005_sms_retry_functionality.sql`

```sql
-- Migration: 005_sms_retry_functionality
-- Description: Add SMS retry functionality tables and columns
-- Dependencies: 004_create_sms_router_tables
-- Rollback: Available

-- Create SMS Retry Queue table
CREATE TABLE IF NOT EXISTS sms_retry_queue (
    id SERIAL PRIMARY KEY,
    original_message_id INTEGER REFERENCES sms_usage_logs(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP,
    retry_reason VARCHAR(100),
    error_code VARCHAR(50),
    error_message TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'retrying', 'failed', 'delivered')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    twilio_message_sid VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sms_retry_queue_status ON sms_retry_queue(status);
CREATE INDEX IF NOT EXISTS idx_sms_retry_queue_next_retry ON sms_retry_queue(next_retry_at);
CREATE INDEX IF NOT EXISTS idx_sms_retry_queue_user_id ON sms_retry_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_sms_retry_queue_original_message ON sms_retry_queue(original_message_id);

-- Update SMS Usage Logs table
ALTER TABLE sms_usage_logs
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS final_status VARCHAR(20) DEFAULT 'unknown',
ADD COLUMN IF NOT EXISTS delivery_confirmed_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS twilio_message_sid VARCHAR(50);

-- Create index for twilio_message_sid lookups
CREATE INDEX IF NOT EXISTS idx_sms_usage_logs_twilio_sid ON sms_usage_logs(twilio_message_sid);

-- Add constraint for final_status
ALTER TABLE sms_usage_logs
ADD CONSTRAINT chk_final_status CHECK (final_status IN ('unknown', 'sent', 'delivered', 'failed', 'undelivered'));
```

### **1.2 Create Database Model**

**File**: `src/personal_assistant/sms_router/models/sms_retry_models.py`

```python
"""
SMS Retry Functionality Database Models

This module defines the database models for SMS retry functionality.
"""

from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP
)
from sqlalchemy.orm import relationship

from ...database.models.base import Base


class SMSRetryQueue(Base):
    """Queue for SMS messages that need to be retried."""

    __tablename__ = "sms_retry_queue"

    id = Column(Integer, primary_key=True)
    original_message_id = Column(Integer, ForeignKey("sms_usage_logs.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message_content = Column(Text, nullable=False)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(TIMESTAMP)
    retry_reason = Column(String(100))
    error_code = Column(String(50))
    error_message = Column(Text)
    status = Column(String(20), default="pending")  # pending, retrying, failed, delivered
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivered_at = Column(DateTime)
    twilio_message_sid = Column(String(50))

    # Relationships
    original_message = relationship("SMSUsageLog", back_populates="retry_attempts")
    user = relationship("User", back_populates="sms_retry_queue")

    def __repr__(self):
        return f"<SMSRetryQueue(id={self.id}, status='{self.status}', retry_count={self.retry_count})>"
```

### **1.3 Update Existing Models**

**File**: `src/personal_assistant/sms_router/models/sms_models.py`

```python
# Add to existing SMSUsageLog class
class SMSUsageLog(Base):
    # ... existing fields ...

    # Add new fields for retry functionality
    retry_count = Column(Integer, default=0)
    final_status = Column(String(20), default="unknown")
    delivery_confirmed_at = Column(DateTime)
    twilio_message_sid = Column(String(50))

    # Add relationship to retry queue
    retry_attempts = relationship("SMSRetryQueue", back_populates="original_message")
```

## **🏗️ Phase 2: SMS Retry Service Implementation**

### **2.1 Create Error Classification System**

**File**: `src/personal_assistant/sms_router/services/error_classifier.py`

```python
"""
SMS Error Classification System

This module classifies SMS errors for appropriate retry strategies.
"""

from enum import Enum
from typing import Dict, Optional


class RetryStrategy(Enum):
    """Retry strategies for different error types."""
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    NO_RETRY = "no_retry"


class SMSErrorClassifier:
    """Classifies SMS errors for appropriate retry strategies."""

    # Twilio error codes that should be retried
    RETRYABLE_ERRORS: Dict[str, Dict[str, any]] = {
        '30001': {
            'description': 'Temporary network issue',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 3,
            'base_delay': 60
        },
        '30002': {
            'description': 'Temporary service unavailable',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 3,
            'base_delay': 120
        },
        '30003': {
            'description': 'Rate limit exceeded',
            'strategy': RetryStrategy.LINEAR_BACKOFF,
            'max_retries': 2,
            'base_delay': 300
        },
        '30004': {
            'description': 'Temporary carrier issue',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 2,
            'base_delay': 180
        },
        '30005': {
            'description': 'Temporary message queue full',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 3,
            'base_delay': 90
        }
    }

    # Twilio error codes that should NOT be retried
    NON_RETRYABLE_ERRORS: Dict[str, str] = {
        '21211': 'Invalid phone number format',
        '21214': 'Invalid message body',
        '21610': 'Message blocked by carrier',
        '21614': 'Message body contains invalid characters',
        '21617': 'Message body is too long',
        '30006': 'Invalid phone number',
        '30007': 'Phone number is not a mobile number',
        '30008': 'Phone number is not reachable'
    }

    @classmethod
    def is_retryable(cls, error_code: str) -> bool:
        """Check if an error code should be retried."""
        return error_code in cls.RETRYABLE_ERRORS

    @classmethod
    def get_retry_strategy(cls, error_code: str) -> Optional[Dict[str, any]]:
        """Get retry strategy for an error code."""
        return cls.RETRYABLE_ERRORS.get(error_code)

    @classmethod
    def get_error_description(cls, error_code: str) -> str:
        """Get human-readable description of error code."""
        if error_code in cls.RETRYABLE_ERRORS:
            return cls.RETRYABLE_ERRORS[error_code]['description']
        elif error_code in cls.NON_RETRYABLE_ERRORS:
            return cls.NON_RETRYABLE_ERRORS[error_code]
        else:
            return f"Unknown error code: {error_code}"

    @classmethod
    def calculate_retry_delay(cls, error_code: str, retry_count: int) -> int:
        """Calculate retry delay based on error code and retry count."""
        strategy_info = cls.get_retry_strategy(error_code)
        if not strategy_info:
            return 0

        base_delay = strategy_info['base_delay']
        strategy = strategy_info['strategy']

        if strategy == RetryStrategy.IMMEDIATE:
            return 0
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            return base_delay * (retry_count + 1)
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return base_delay * (2 ** retry_count)
        else:
            return 0
```

### **2.2 Create SMS Retry Service**

**File**: `src/personal_assistant/sms_router/services/retry_service.py`

```python
"""
SMS Retry Service

This module handles SMS retry logic and delivery confirmation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...communication.twilio_integration.twilio_client import TwilioService
from ...database.database import get_db_session
from ..models.sms_retry_models import SMSRetryQueue
from ..models.sms_models import SMSUsageLog
from .error_classifier import SMSErrorClassifier

logger = logging.getLogger(__name__)


class SMSRetryService:
    """Handles SMS retry logic and delivery confirmation."""

    def __init__(self):
        self.twilio_service = TwilioService()
        self.error_classifier = SMSErrorClassifier()
        self.max_batch_size = 50

    async def queue_for_retry(
        self,
        sms_log_id: int,
        error_code: str,
        error_message: str,
        user_id: int,
        phone_number: str,
        message_content: str
    ) -> bool:
        """
        Queue a failed SMS for retry.

        Args:
            sms_log_id: ID of the original SMS log entry
            error_code: Twilio error code
            error_message: Error message from Twilio
            user_id: User ID who sent the SMS
            phone_number: Recipient phone number
            message_content: SMS message content

        Returns:
            bool: True if queued for retry, False if not retryable
        """
        if not self.error_classifier.is_retryable(error_code):
            logger.info(f"SMS error {error_code} is not retryable: {error_message}")
            return False

        strategy_info = self.error_classifier.get_retry_strategy(error_code)
        if not strategy_info:
            return False

        try:
            async with get_db_session() as db:
                # Create retry queue entry
                retry_entry = SMSRetryQueue(
                    original_message_id=sms_log_id,
                    user_id=user_id,
                    phone_number=phone_number,
                    message_content=message_content,
                    retry_count=0,
                    max_retries=strategy_info['max_retries'],
                    retry_reason=self.error_classifier.get_error_description(error_code),
                    error_code=error_code,
                    error_message=error_message,
                    status='pending',
                    next_retry_at=datetime.utcnow() + timedelta(
                        seconds=self.error_classifier.calculate_retry_delay(error_code, 0)
                    )
                )

                db.add(retry_entry)
                await db.commit()

                logger.info(f"Queued SMS for retry: {retry_entry.id}, error: {error_code}")
                return True

        except Exception as e:
            logger.error(f"Failed to queue SMS for retry: {e}")
            return False

    async def process_retry_queue(self) -> dict:
        """
        Process pending retries from the queue.

        Returns:
            dict: Processing statistics
        """
        stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }

        try:
            async with get_db_session() as db:
                # Get pending retries that are due
                now = datetime.utcnow()
                query = select(SMSRetryQueue).where(
                    and_(
                        SMSRetryQueue.status == 'pending',
                        SMSRetryQueue.next_retry_at <= now,
                        SMSRetryQueue.retry_count < SMSRetryQueue.max_retries
                    )
                ).limit(self.max_batch_size)

                result = await db.execute(query)
                retry_entries = result.scalars().all()

                logger.info(f"Processing {len(retry_entries)} SMS retries")

                for retry_entry in retry_entries:
                    try:
                        await self._process_single_retry(db, retry_entry)
                        stats['processed'] += 1

                        # Update status based on result
                        if retry_entry.status == 'delivered':
                            stats['successful'] += 1
                        elif retry_entry.status == 'failed':
                            stats['failed'] += 1
                        else:
                            stats['skipped'] += 1

                    except Exception as e:
                        logger.error(f"Error processing retry {retry_entry.id}: {e}")
                        stats['failed'] += 1

                await db.commit()

        except Exception as e:
            logger.error(f"Error processing retry queue: {e}")

        logger.info(f"Retry queue processing completed: {stats}")
        return stats

    async def _process_single_retry(self, db: AsyncSession, retry_entry: SMSRetryQueue):
        """Process a single retry entry."""
        try:
            # Update status to retrying
            retry_entry.status = 'retrying'
            retry_entry.retry_count += 1
            retry_entry.updated_at = datetime.utcnow()

            # Attempt to send SMS
            message_sid = await self.twilio_service.send_sms(
                retry_entry.phone_number,
                retry_entry.message_content
            )

            # Update retry entry with success
            retry_entry.twilio_message_sid = message_sid
            retry_entry.status = 'delivered'
            retry_entry.delivered_at = datetime.utcnow()

            # Update original SMS log
            if retry_entry.original_message_id:
                original_log = await db.get(SMSUsageLog, retry_entry.original_message_id)
                if original_log:
                    original_log.final_status = 'delivered'
                    original_log.twilio_message_sid = message_sid
                    original_log.delivery_confirmed_at = datetime.utcnow()

            logger.info(f"SMS retry successful: {retry_entry.id}, SID: {message_sid}")

        except Exception as e:
            # Handle retry failure
            retry_entry.error_message = str(e)
            retry_entry.updated_at = datetime.utcnow()

            if retry_entry.retry_count >= retry_entry.max_retries:
                # Max retries reached
                retry_entry.status = 'failed'
                logger.warning(f"SMS retry failed after {retry_entry.max_retries} attempts: {retry_entry.id}")
            else:
                # Schedule next retry
                delay = self.error_classifier.calculate_retry_delay(
                    retry_entry.error_code,
                    retry_entry.retry_count
                )
                retry_entry.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                retry_entry.status = 'pending'
                logger.info(f"SMS retry scheduled for {retry_entry.next_retry_at}: {retry_entry.id}")

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
            async with get_db_session() as db:
                # Find retry entry by message SID
                query = select(SMSRetryQueue).where(
                    SMSRetryQueue.twilio_message_sid == message_sid
                )
                result = await db.execute(query)
                retry_entry = result.scalar_one_or_none()

                if retry_entry:
                    # Update retry entry status
                    if status in ['delivered', 'sent']:
                        retry_entry.status = 'delivered'
                        retry_entry.delivered_at = datetime.utcnow()
                    elif status in ['failed', 'undelivered']:
                        retry_entry.status = 'failed'

                    retry_entry.updated_at = datetime.utcnow()

                    # Update original SMS log
                    if retry_entry.original_message_id:
                        original_log = await db.get(SMSUsageLog, retry_entry.original_message_id)
                        if original_log:
                            original_log.final_status = status
                            original_log.delivery_confirmed_at = datetime.utcnow()

                    await db.commit()
                    logger.info(f"Updated delivery status for retry {retry_entry.id}: {status}")
                    return True

                # Also check original SMS logs
                query = select(SMSUsageLog).where(
                    SMSUsageLog.twilio_message_sid == message_sid
                )
                result = await db.execute(query)
                sms_log = result.scalar_one_or_none()

                if sms_log:
                    sms_log.final_status = status
                    sms_log.delivery_confirmed_at = datetime.utcnow()
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

            async with get_db_session() as db:
                # Delete old retry records
                query = select(SMSRetryQueue).where(
                    SMSRetryQueue.created_at < cutoff_date
                )
                result = await db.execute(query)
                old_retries = result.scalars().all()

                count = len(old_retries)
                for retry_entry in old_retries:
                    await db.delete(retry_entry)

                await db.commit()

                logger.info(f"Cleaned up {count} old retry records")
                return count

        except Exception as e:
            logger.error(f"Error cleaning up old retries: {e}")
            return 0
```

## **🏗️ Phase 3: Celery Task Integration**

### **3.1 Create SMS Retry Tasks**

**File**: `src/personal_assistant/workers/tasks/sms_tasks.py`

```python
"""
SMS Retry Background Tasks

This module handles SMS retry-related background tasks.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from ..celery_app import app
from ...sms_router.services.retry_service import SMSRetryService

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def process_sms_retry_queue(self) -> Dict[str, Any]:
    """
    Process SMS retry queue every 2 minutes.

    This task:
    1. Processes pending retries that are due
    2. Attempts to resend failed SMS messages
    3. Updates retry status and schedules next attempts
    4. Logs processing statistics
    """
    task_id = self.request.id
    logger.info(f"Starting SMS retry queue processing task {task_id}")

    try:
        retry_service = SMSRetryService()
        stats = await retry_service.process_retry_queue()

        result = {
            "task_id": task_id,
            "status": "success",
            "processed": stats['processed'],
            "successful": stats['successful'],
            "failed": stats['failed'],
            "skipped": stats['skipped'],
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"SMS retry queue processing completed: {result}")
        return result

    except Exception as e:
        logger.error(f"SMS retry queue processing failed: {e}")
        raise self.retry(countdown=300, max_retries=3)


@app.task(bind=True, max_retries=5, default_retry_delay=60)
def retry_failed_sms(self, retry_queue_id: int) -> Dict[str, Any]:
    """
    Retry a specific failed SMS.

    Args:
        retry_queue_id: ID of the retry queue entry to process

    Returns:
        Dict with retry result
    """
    task_id = self.request.id
    logger.info(f"Starting individual SMS retry task {task_id} for retry {retry_queue_id}")

    try:
        retry_service = SMSRetryService()

        # Get the specific retry entry
        async with retry_service.get_db_session() as db:
            from ...sms_router.models.sms_retry_models import SMSRetryQueue
            retry_entry = await db.get(SMSRetryQueue, retry_queue_id)

            if not retry_entry:
                raise ValueError(f"Retry entry {retry_queue_id} not found")

            # Process the retry
            await retry_service._process_single_retry(db, retry_entry)
            await db.commit()

            result = {
                "task_id": task_id,
                "status": "success",
                "retry_id": retry_queue_id,
                "retry_status": retry_entry.status,
                "retry_count": retry_entry.retry_count,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Individual SMS retry completed: {result}")
            return result

    except Exception as e:
        logger.error(f"Individual SMS retry failed: {e}")
        raise self.retry(countdown=60, max_retries=5)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_retries(self) -> Dict[str, Any]:
    """
    Clean up old retry records.

    This task:
    1. Removes retry records older than 7 days
    2. Logs cleanup statistics
    3. Helps maintain database performance
    """
    task_id = self.request.id
    logger.info(f"Starting SMS retry cleanup task {task_id}")

    try:
        retry_service = SMSRetryService()
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
def sms_retry_health_check(self) -> Dict[str, Any]:
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
        retry_service = SMSRetryService()

        # Get retry statistics
        async with retry_service.get_db_session() as db:
            from sqlalchemy import func, select
            from ...sms_router.models.sms_retry_models import SMSRetryQueue

            # Count retries by status
            query = select(
                SMSRetryQueue.status,
                func.count(SMSRetryQueue.id).label('count')
            ).group_by(SMSRetryQueue.status)

            result = await db.execute(query)
            status_counts = {row.status: row.count for row in result}

            # Calculate success rate
            total_retries = sum(status_counts.values())
            successful_retries = status_counts.get('delivered', 0)
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
```

### **3.2 Update Celery Beat Schedule**

**File**: `src/personal_assistant/workers/celery_app.py`

```python
# Add to existing beat_schedule
beat_schedule={
    # ... existing tasks ...

    # SMS retry tasks (high priority)
    "sms-retry-processor": {
        "task": "personal_assistant.workers.tasks.sms_tasks.process_sms_retry_queue",
        "schedule": crontab(minute="*/2"),
        "options": {"priority": 8},
    },
    "sms-retry-cleanup": {
        "task": "personal_assistant.workers.tasks.sms_tasks.cleanup_old_retries",
        "schedule": crontab(hour=3, minute=0),
        "options": {"priority": 5},
    },
    "sms-retry-health-check": {
        "task": "personal_assistant.workers.tasks.sms_tasks.sms_retry_health_check",
        "schedule": crontab(minute="*/15"),
        "options": {"priority": 7},
    },
}
```

## **🏗️ Phase 4: Service Integration**

### **4.1 Update Twilio Service**

**File**: `src/personal_assistant/communication/twilio_integration/twilio_client.py`

```python
# Add to existing TwilioService class
class TwilioService:
    def __init__(self, agent_core: Optional[AgentCore] = None):
        # ... existing init code ...
        self.retry_service = None  # Will be initialized when needed

    async def send_sms_with_retry(
        self,
        to: str,
        message: str,
        user_id: int,
        sms_log_id: Optional[int] = None
    ) -> str:
        """
        Send SMS with automatic retry functionality.

        Args:
            to: Recipient phone number
            message: SMS message content
            user_id: User ID sending the SMS
            sms_log_id: Optional SMS log ID for retry tracking

        Returns:
            str: Message SID if successful

        Raises:
            TwilioRestException: If SMS fails and is not retryable
        """
        try:
            # Attempt to send SMS
            message_obj = self.client.messages.create(
                body=message, from_=self.from_number, to=to
            )

            logger.info(f"Message sent successfully. SID: {message_obj.sid}")
            return message_obj.sid

        except TwilioRestException as e:
            logger.error(f"Twilio error: {e.code} - {e.msg}")

            # Initialize retry service if needed
            if not self.retry_service:
                from ...sms_router.services.retry_service import SMSRetryService
                self.retry_service = SMSRetryService()

            # Queue for retry if error is retryable
            if self.retry_service.error_classifier.is_retryable(e.code):
                await self.retry_service.queue_for_retry(
                    sms_log_id=sms_log_id or 0,
                    error_code=e.code,
                    error_message=e.msg,
                    user_id=user_id,
                    phone_number=to,
                    message_content=message
                )
                logger.info(f"SMS queued for retry due to error {e.code}")

            # Re-raise the exception
            raise
```

### **4.2 Update SMS Router Engine**

**File**: `src/personal_assistant/sms_router/services/routing_engine.py`

```python
# Update existing send_sms method
async def send_sms(self, to_phone: str, message: str, user_id: int) -> bool:
    """
    Send an outbound SMS message with retry functionality.

    Args:
        to_phone: Recipient's phone number
        message: Message content
        user_id: Sender's user ID

    Returns:
        True if successful or queued for retry, False otherwise
    """
    start_time = time.time()
    sms_log_id = None

    try:
        logger.info(f"Sending SMS to {to_phone} from user {user_id}")

        # Log the attempt
        sms_log = await self._log_usage(
            to_phone,
            message,
            "outbound",
            True,
            time.time() - start_time,
            user_id=user_id,
        )
        sms_log_id = sms_log.id

        # Send via Twilio with retry support
        twilio_service = TwilioService()
        message_sid = await twilio_service.send_sms_with_retry(
            to_phone, message, user_id, sms_log_id
        )

        # Update log with success
        sms_log.twilio_message_sid = message_sid
        sms_log.final_status = 'sent'

        logger.info(f"SMS sent successfully: {message_sid}")
        return True

    except Exception as e:
        logger.error(f"Error sending SMS to {to_phone}: {e}")

        # Log the failure
        await self._log_usage(
            to_phone,
            message,
            "outbound",
            False,
            time.time() - start_time,
            str(e),
            user_id,
        )

        # Check if this was a retryable error (already queued by TwilioService)
        if hasattr(e, 'code'):
            from .error_classifier import SMSErrorClassifier
            classifier = SMSErrorClassifier()
            if classifier.is_retryable(e.code):
                logger.info(f"SMS queued for retry due to error {e.code}")
                return True  # Consider it successful since it's queued for retry

        return False
```

### **4.3 Create Webhook Handler**

**File**: `src/apps/fastapi_app/routes/sms_router/webhooks.py`

```python
# Add to existing webhooks.py
@router.post("/delivery-status")
async def twilio_delivery_status_webhook(
    request: Request,
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    retry_service: SMSRetryService = Depends(get_retry_service)
):
    """
    Handle Twilio delivery status webhooks.

    This endpoint receives delivery confirmations from Twilio and updates
    the retry queue status accordingly.
    """
    try:
        logger.info(f"Received delivery status webhook: {MessageSid} - {MessageStatus}")

        # Handle delivery confirmation
        success = await retry_service.handle_delivery_confirmation(MessageSid, MessageStatus)

        if success:
            return {"status": "success", "message": "Delivery status updated"}
        else:
            return {"status": "warning", "message": "No matching SMS record found"}

    except Exception as e:
        logger.error(f"Error processing delivery status webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_retry_service() -> SMSRetryService:
    """Dependency to get SMS retry service."""
    return SMSRetryService()
```

## **🧪 Testing Strategy**

### **Unit Tests**

**File**: `tests/unit/test_sms_retry_service.py`

```python
"""
Unit tests for SMS retry service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.personal_assistant.sms_router.services.retry_service import SMSRetryService
from src.personal_assistant.sms_router.services.error_classifier import SMSErrorClassifier


class TestSMSErrorClassifier:
    """Test SMS error classification."""

    def test_retryable_error_detection(self):
        """Test detection of retryable errors."""
        assert SMSErrorClassifier.is_retryable('30001') == True
        assert SMSErrorClassifier.is_retryable('30002') == True
        assert SMSErrorClassifier.is_retryable('21211') == False
        assert SMSErrorClassifier.is_retryable('unknown') == False

    def test_retry_delay_calculation(self):
        """Test retry delay calculation."""
        # Exponential backoff
        delay1 = SMSErrorClassifier.calculate_retry_delay('30001', 0)
        delay2 = SMSErrorClassifier.calculate_retry_delay('30001', 1)
        delay3 = SMSErrorClassifier.calculate_retry_delay('30001', 2)

        assert delay1 == 60  # base_delay
        assert delay2 == 120  # base_delay * 2^1
        assert delay3 == 240  # base_delay * 2^2


class TestSMSRetryService:
    """Test SMS retry service."""

    @pytest.fixture
    def retry_service(self):
        """Create retry service instance."""
        return SMSRetryService()

    @pytest.mark.asyncio
    async def test_queue_for_retry_retryable_error(self, retry_service):
        """Test queuing retryable errors."""
        with patch.object(retry_service, 'get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session

            result = await retry_service.queue_for_retry(
                sms_log_id=1,
                error_code='30001',
                error_message='Temporary network issue',
                user_id=1,
                phone_number='+1234567890',
                message_content='Test message'
            )

            assert result == True
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_for_retry_non_retryable_error(self, retry_service):
        """Test handling non-retryable errors."""
        result = await retry_service.queue_for_retry(
            sms_log_id=1,
            error_code='21211',
            error_message='Invalid phone number',
            user_id=1,
            phone_number='+1234567890',
            message_content='Test message'
        )

        assert result == False

    @pytest.mark.asyncio
    async def test_process_retry_queue(self, retry_service):
        """Test processing retry queue."""
        with patch.object(retry_service, 'get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session

            # Mock retry entries
            mock_retry = MagicMock()
            mock_retry.id = 1
            mock_retry.status = 'pending'
            mock_retry.retry_count = 0
            mock_retry.max_retries = 3

            mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_retry]

            stats = await retry_service.process_retry_queue()

            assert 'processed' in stats
            assert 'successful' in stats
            assert 'failed' in stats
            assert 'skipped' in stats
```

### **Integration Tests**

**File**: `tests/integration/test_sms_retry_integration.py`

```python
"""
Integration tests for SMS retry functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.personal_assistant.workers.tasks.sms_tasks import process_sms_retry_queue


class TestSMSRetryIntegration:
    """Test SMS retry integration."""

    @pytest.mark.asyncio
    async def test_process_sms_retry_queue_task(self):
        """Test SMS retry queue processing task."""
        with patch('src.personal_assistant.workers.tasks.sms_tasks.SMSRetryService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            mock_service.process_retry_queue.return_value = {
                'processed': 5,
                'successful': 4,
                'failed': 1,
                'skipped': 0
            }

            # Create mock task
            mock_task = AsyncMock()
            mock_task.request.id = 'test-task-id'

            result = await process_sms_retry_queue(mock_task)

            assert result['status'] == 'success'
            assert result['processed'] == 5
            assert result['successful'] == 4
            assert result['failed'] == 1
```

## **📊 Monitoring & Analytics**

### **Metrics to Track**

1. **Retry Success Rate**: Percentage of retries that succeed
2. **Average Retry Count**: How many retries per message on average
3. **Retry Queue Size**: Number of pending retries
4. **Processing Time**: Time to process retry queue
5. **Error Distribution**: Most common retry reasons

### **Alerting Rules**

1. **High Retry Rate**: Alert if retry success rate < 80%
2. **Queue Backlog**: Alert if retry queue size > 100
3. **Processing Delays**: Alert if queue processing takes > 5 minutes
4. **Critical Errors**: Alert on non-retryable error spikes

This implementation guide provides comprehensive instructions for building a robust SMS retry system that ensures reliable message delivery while maintaining system performance and cost efficiency.
