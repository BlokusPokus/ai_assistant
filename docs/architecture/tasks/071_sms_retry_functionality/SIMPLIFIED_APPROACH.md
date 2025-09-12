# Task 071: SMS Retry Functionality - Simplified Approach

## **🎯 Simplified Strategy**

Instead of creating a new database table, we can leverage the existing `SMSUsageLog` table and Celery's built-in retry mechanisms to implement SMS retry functionality with minimal changes.

## **🔍 What We Already Have**

### **Existing SMSUsageLog Table**

```sql
CREATE TABLE sms_usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    message_direction VARCHAR(10) NOT NULL,
    message_length INTEGER NOT NULL,
    message_content TEXT,
    success BOOLEAN DEFAULT TRUE,
    processing_time_ms INTEGER,
    error_message TEXT,
    sms_metadata JSONB,  -- We can store retry info here!
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Existing Celery Retry Infrastructure**

```python
@app.task(bind=True, max_retries=3, default_retry_delay=300)
def some_task(self):
    try:
        # Task logic
        pass
    except Exception as e:
        raise self.retry(countdown=300, max_retries=3)
```

## **💡 Simplified Implementation**

### **Phase 1: Minimal Database Changes (30 minutes)**

Just add a few fields to the existing table:

```sql
-- Migration: 005_sms_retry_simplified
ALTER TABLE sms_usage_logs
ADD COLUMN retry_count INTEGER DEFAULT 0,
ADD COLUMN max_retries INTEGER DEFAULT 3,
ADD COLUMN next_retry_at TIMESTAMP,
ADD COLUMN twilio_message_sid VARCHAR(50),
ADD COLUMN final_status VARCHAR(20) DEFAULT 'unknown';

-- Add index for retry processing
CREATE INDEX idx_sms_usage_logs_retry ON sms_usage_logs(success, next_retry_at)
WHERE success = false AND next_retry_at IS NOT NULL;
```

### **Phase 2: Simple Retry Service (2 hours)**

```python
# src/personal_assistant/sms_router/services/simple_retry_service.py
class SimpleSMSRetryService:
    """Simplified SMS retry service using existing infrastructure."""

    RETRYABLE_ERRORS = {
        '30001': {'max_retries': 3, 'base_delay': 60},
        '30002': {'max_retries': 3, 'base_delay': 120},
        '30003': {'max_retries': 2, 'base_delay': 300},
        '30004': {'max_retries': 2, 'base_delay': 180}
    }

    NON_RETRYABLE_ERRORS = {'21211', '21214', '21610', '30006', '30007', '30008'}

    async def queue_for_retry(self, sms_log_id: int, error_code: str, error_message: str):
        """Queue a failed SMS for retry using existing SMSUsageLog record."""
        if error_code in self.NON_RETRYABLE_ERRORS:
            return False

        retry_config = self.RETRYABLE_ERRORS.get(error_code, {'max_retries': 2, 'base_delay': 120})

        async with get_db_session() as db:
            sms_log = await db.get(SMSUsageLog, sms_log_id)
            if not sms_log:
                return False

            # Update existing record for retry
            sms_log.retry_count = 1
            sms_log.max_retries = retry_config['max_retries']
            sms_log.next_retry_at = datetime.utcnow() + timedelta(seconds=retry_config['base_delay'])
            sms_log.sms_metadata = sms_log.sms_metadata or {}
            sms_log.sms_metadata.update({
                'retry_reason': error_code,
                'retry_error': error_message,
                'retry_strategy': 'exponential_backoff'
            })

            await db.commit()
            return True

    async def process_retry_queue(self):
        """Process failed SMS records that are ready for retry."""
        stats = {'processed': 0, 'successful': 0, 'failed': 0}

        async with get_db_session() as db:
            # Get failed SMS records ready for retry
            now = datetime.utcnow()
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.success == False,
                    SMSUsageLog.retry_count < SMSUsageLog.max_retries,
                    SMSUsageLog.next_retry_at <= now
                )
            ).limit(50)

            result = await db.execute(query)
            failed_sms = result.scalars().all()

            for sms_log in failed_sms:
                try:
                    # Attempt to resend
                    twilio_service = TwilioService()
                    message_sid = await twilio_service.send_sms(sms_log.phone_number, sms_log.message_content)

                    # Update on success
                    sms_log.success = True
                    sms_log.twilio_message_sid = message_sid
                    sms_log.final_status = 'sent'
                    sms_log.next_retry_at = None
                    stats['successful'] += 1

                except Exception as e:
                    # Handle retry failure
                    sms_log.retry_count += 1
                    sms_log.error_message = str(e)

                    if sms_log.retry_count >= sms_log.max_retries:
                        sms_log.final_status = 'failed'
                        sms_log.next_retry_at = None
                        stats['failed'] += 1
                    else:
                        # Schedule next retry with exponential backoff
                        delay = 60 * (2 ** (sms_log.retry_count - 1))
                        sms_log.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                        stats['failed'] += 1

                stats['processed'] += 1

            await db.commit()
            return stats
```

### **Phase 3: Simple Celery Task (1 hour)**

```python
# src/personal_assistant/workers/tasks/sms_tasks.py
@app.task(bind=True, max_retries=3, default_retry_delay=300)
def process_sms_retries(self):
    """Process SMS retries every 2 minutes."""
    try:
        retry_service = SimpleSMSRetryService()
        stats = await retry_service.process_retry_queue()

        logger.info(f"SMS retry processing: {stats}")
        return stats

    except Exception as e:
        logger.error(f"SMS retry processing failed: {e}")
        raise self.retry(countdown=300, max_retries=3)

# Add to celery_app.py beat_schedule
"sms-retry-processor": {
    "task": "personal_assistant.workers.tasks.sms_tasks.process_sms_retries",
    "schedule": crontab(minute="*/2"),
    "options": {"priority": 8},
},
```

### **Phase 4: Update Existing Services (1 hour)**

```python
# Update TwilioService.send_sms() to queue retries
async def send_sms(self, to: str, message: str) -> str:
    try:
        message_obj = self.client.messages.create(
            body=message, from_=self.from_number, to=to
        )
        return message_obj.sid

    except TwilioRestException as e:
        # Queue for retry if retryable
        retry_service = SimpleSMSRetryService()
        if e.code in retry_service.RETRYABLE_ERRORS:
            # We need the SMS log ID, so this would be called from SMSRoutingEngine
            logger.info(f"SMS queued for retry due to error {e.code}")

        raise  # Re-raise for caller to handle

# Update SMSRoutingEngine.send_sms() to integrate retry
async def send_sms(self, to_phone: str, message: str, user_id: int) -> bool:
    start_time = time.time()

    try:
        # Log the attempt first
        sms_log = await self._log_usage(
            to_phone, message, "outbound", True,
            time.time() - start_time, user_id=user_id
        )

        # Send via Twilio
        twilio_service = TwilioService()
        message_sid = await twilio_service.send_sms(to_phone, message)

        # Update log with success
        sms_log.twilio_message_sid = message_sid
        sms_log.final_status = 'sent'

        return True

    except Exception as e:
        # Log the failure
        sms_log = await self._log_usage(
            to_phone, message, "outbound", False,
            time.time() - start_time, str(e), user_id
        )

        # Queue for retry if appropriate
        retry_service = SimpleSMSRetryService()
        if hasattr(e, 'code') and e.code in retry_service.RETRYABLE_ERRORS:
            await retry_service.queue_for_retry(sms_log.id, e.code, str(e))
            return True  # Consider it successful since it's queued for retry

        return False
```

## **📊 Benefits of Simplified Approach**

### **Minimal Changes**

- ✅ No new database table
- ✅ Leverages existing SMSUsageLog infrastructure
- ✅ Uses existing Celery retry mechanisms
- ✅ Minimal code changes required

### **Same Functionality**

- ✅ Automatic retry of failed SMS
- ✅ Intelligent retry delays
- ✅ Error classification
- ✅ Retry limits and cleanup
- ✅ Monitoring and analytics

### **Faster Implementation**

- ⏱️ **Total time: ~4 hours** (vs 3-4 days)
- 🚀 **Deployable in 1 day**
- 🧪 **Easier to test**
- 🔧 **Easier to maintain**

## **🔧 Implementation Steps**

1. **Add retry fields to SMSUsageLog** (30 min)
2. **Create SimpleSMSRetryService** (2 hours)
3. **Add Celery task for retry processing** (1 hour)
4. **Update existing SMS services** (1 hour)
5. **Test and deploy** (30 min)

## **📈 Monitoring**

Use existing SMS analytics with new retry fields:

```python
# Retry success rate
SELECT
    COUNT(*) as total_retries,
    SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as successful_retries,
    (SUM(CASE WHEN success = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
FROM sms_usage_logs
WHERE retry_count > 0;

# Retry patterns
SELECT
    retry_count,
    COUNT(*) as count,
    AVG(processing_time_ms) as avg_processing_time
FROM sms_usage_logs
WHERE retry_count > 0
GROUP BY retry_count;
```

## **🎯 Success Criteria**

- SMS delivery success rate >99%
- Retry success rate >80%
- Average retry attempts <1.5
- Implementation time <1 day
- Zero new database tables
- Minimal code changes

This simplified approach achieves the same goals with significantly less complexity and faster implementation time!
