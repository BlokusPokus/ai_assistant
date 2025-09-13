# Task 071: SMS Retry Functionality - Onboarding

## **📋 Context**

You are given the following context:

- **Task**: Implement SMS retry functionality to ensure reliable message delivery
- **Goal**: Create a comprehensive retry system that automatically handles failed SMS transmissions
- **Dependencies**: SMS Router Service (Task 045) ✅ COMPLETED, Background Task System (Task 037) ✅ COMPLETED

## **🔍 Current SMS Infrastructure Analysis**

### **1. Existing SMS Services ✅ READY**

**Primary SMS Service**:

```python
# src/personal_assistant/communication/twilio_integration/twilio_client.py
class TwilioService:
    async def send_sms(self, to: str, message: str) -> str:
        """Sends SMS via Twilio - currently no retry logic"""
        try:
            message = self.client.messages.create(
                body=message, from_=self.from_number, to=to
            )
            return message.sid
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e.code} - {e.msg}")
            raise  # Currently just raises exception
```

**SMS Router Engine**:

```python
# src/personal_assistant/sms_router/services/routing_engine.py
class SMSRoutingEngine:
    async def send_sms(self, to_phone: str, message: str, user_id: int) -> bool:
        """Currently just logs outbound messages - TODO: Integrate with Twilio"""
        # TODO: Integrate with Twilio service for actual SMS sending
        # For now, just log the outbound message
        logger.info(f"Outbound SMS: {message[:50]}...")
        return True  # Always returns True currently
```

**Notification Service**:

```python
# src/personal_assistant/tools/ai_scheduler/notifications/service.py
class NotificationService:
    async def send_sms_notification(self, to_number: str, message: str, task_title: Optional[str] = None):
        """Sends SMS via Twilio with basic error handling"""
        try:
            message_obj = self.twilio_client.messages.create(
                body=formatted_message,
                from_=self.from_number,
                to=to_number
            )
            return {'success': True, 'message_sid': message_obj.sid}
        except TwilioException as e:
            self.logger.error(f"SMS notification failed: {e}")
            return {'success': False, 'error': str(e)}
```

### **2. Database Models ✅ READY**

**SMS Usage Logging**:

```python
# src/personal_assistant/sms_router/models/sms_models.py
class SMSUsageLog(Base):
    __tablename__ = 'sms_usage_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message_direction = Column(String(10), nullable=False)  # 'inbound' or 'outbound'
    message_content = Column(Text)
    success = Column(Boolean, default=True)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    sms_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Current Limitations**:

- No retry tracking
- No delivery confirmation
- No error classification
- Success/failure logging only

### **3. Background Task System ✅ COMPLETED**

**Celery Infrastructure**:

```python
# src/personal_assistant/workers/celery_app.py
app = Celery('personal_assistant')

# Existing retry decorator
@app.task(bind=True, max_retries=3, default_retry_delay=300)
def some_task(self):
    try:
        # Task logic
        pass
    except Exception as e:
        raise self.retry(countdown=300, max_retries=3)
```

**Available Task Types**:

- AI tasks (high priority)
- Email tasks (medium priority)
- File tasks (low priority)
- Sync tasks (medium-high priority)

## **🎯 What Needs to Be Built**

### **1. Database Schema Enhancement**

**New Table: `sms_retry_queue`**

```sql
CREATE TABLE sms_retry_queue (
    id SERIAL PRIMARY KEY,
    original_message_id INTEGER REFERENCES sms_usage_logs(id),
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP,
    retry_reason VARCHAR(100),
    error_code VARCHAR(50),
    error_message TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, retrying, failed, delivered
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    twilio_message_sid VARCHAR(50)
);
```

**Enhanced SMS Usage Logs**:

```sql
ALTER TABLE sms_usage_logs
ADD COLUMN retry_count INTEGER DEFAULT 0,
ADD COLUMN final_status VARCHAR(20) DEFAULT 'unknown',
ADD COLUMN delivery_confirmed_at TIMESTAMP;
```

### **2. SMS Retry Service**

**Core Retry Service**:

```python
# src/personal_assistant/sms_router/services/retry_service.py
class SMSRetryService:
    """Handles SMS retry logic and delivery confirmation."""

    async def queue_for_retry(self, sms_log_id: int, error_code: str, error_message: str):
        """Queue a failed SMS for retry based on error type."""

    async def process_retry_queue(self):
        """Process pending retries from the queue."""

    async def retry_sms(self, retry_record: SMSRetryQueue):
        """Attempt to retry a specific SMS."""

    async def handle_delivery_confirmation(self, message_sid: str, status: str):
        """Handle Twilio delivery status webhooks."""

    def _calculate_retry_delay(self, retry_count: int, error_code: str) -> int:
        """Calculate intelligent retry delay with exponential backoff."""

    def _is_retryable_error(self, error_code: str) -> bool:
        """Determine if an error should be retried."""
```

**Error Classification**:

```python
class SMSErrorClassifier:
    """Classifies SMS errors for appropriate retry strategies."""

    RETRYABLE_ERRORS = {
        '30001': 'Temporary network issue - retry with backoff',
        '30002': 'Temporary service unavailable - retry with backoff',
        '30003': 'Rate limit exceeded - retry with longer delay',
        '30004': 'Temporary carrier issue - retry with backoff'
    }

    NON_RETRYABLE_ERRORS = {
        '21211': 'Invalid phone number - do not retry',
        '21214': 'Invalid message body - do not retry',
        '21610': 'Message blocked by carrier - do not retry'
    }
```

### **3. Celery Task Integration**

**SMS Retry Tasks**:

```python
# src/personal_assistant/workers/tasks/sms_tasks.py
@app.task(bind=True, max_retries=3, default_retry_delay=300)
def process_sms_retry_queue(self):
    """Process SMS retry queue every 2 minutes."""

@app.task(bind=True, max_retries=5, default_retry_delay=60)
def retry_failed_sms(self, retry_queue_id: int):
    """Retry a specific failed SMS."""

@app.task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_retries(self):
    """Clean up old retry records after 7 days."""
```

**Updated Beat Schedule**:

```python
# Add to celery_app.py beat_schedule
"sms-retry-processor": {
    "task": "personal_assistant.workers.tasks.sms_tasks.process_sms_retry_queue",
    "schedule": crontab(minute="*/2"),
    "options": {"priority": 8},
},
```

### **4. Service Integration**

**Enhanced Twilio Service**:

```python
# Update src/personal_assistant/communication/twilio_integration/twilio_client.py
class TwilioService:
    def __init__(self, agent_core: Optional[AgentCore] = None):
        # ... existing init ...
        self.retry_service = SMSRetryService()  # Add retry service

    async def send_sms(self, to: str, message: str) -> str:
        """Enhanced with retry logic."""
        try:
            message = self.client.messages.create(
                body=message, from_=self.from_number, to=to
            )
            return message.sid
        except TwilioRestException as e:
            # Queue for retry if error is retryable
            if self.retry_service._is_retryable_error(e.code):
                await self.retry_service.queue_for_retry(
                    sms_log_id=None,  # Will be set by caller
                    error_code=e.code,
                    error_message=e.msg
                )
            raise
```

**Enhanced SMS Router**:

```python
# Update src/personal_assistant/sms_router/services/routing_engine.py
class SMSRoutingEngine:
    async def send_sms(self, to_phone: str, message: str, user_id: int) -> bool:
        """Enhanced with actual Twilio integration and retry logic."""
        start_time = time.time()

        try:
            # Log the attempt
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
            retry_service = SMSRetryService()
            await retry_service.queue_for_retry(
                sms_log.id, getattr(e, 'code', 'unknown'), str(e)
            )

            return False
```

### **5. Webhook Integration**

**Delivery Status Webhook**:

```python
# src/apps/fastapi_app/routes/sms_router/webhooks.py
@router.post("/delivery-status")
async def twilio_delivery_status_webhook(
    request: Request,
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    retry_service: SMSRetryService = Depends()
):
    """Handle Twilio delivery status webhooks."""
    try:
        await retry_service.handle_delivery_confirmation(MessageSid, MessageStatus)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing delivery status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## **🔧 Implementation Strategy**

### **Phase 1: Database Foundation (Day 1)**

1. Create database migration for retry queue table
2. Update SMS usage logs schema
3. Create necessary indexes
4. Test database changes

### **Phase 2: Core Retry Service (Day 2)**

1. Implement `SMSRetryService` class
2. Create error classification system
3. Implement retry delay calculation
4. Add delivery confirmation handling
5. Unit tests for retry service

### **Phase 3: Celery Integration (Day 3)**

1. Create SMS retry tasks
2. Update Celery beat schedule
3. Implement retry queue processing
4. Add cleanup tasks
5. Integration tests

### **Phase 4: Service Integration (Day 4)**

1. Update existing SMS services
2. Implement webhook handlers
3. Add monitoring and analytics
4. End-to-end testing
5. Performance optimization

## **📊 Success Criteria**

### **Functional Requirements**

- [ ] Failed SMS messages are automatically queued for retry
- [ ] Retry attempts use intelligent delay calculation
- [ ] Non-retryable errors are not queued for retry
- [ ] Delivery confirmation updates retry status
- [ ] Old retry records are cleaned up automatically

### **Performance Requirements**

- [ ] Retry queue processing completes within 2 minutes
- [ ] Individual retry attempts complete within 30 seconds
- [ ] Database queries perform within 100ms
- [ ] System handles 100+ retries per minute

### **Reliability Requirements**

- [ ] SMS delivery success rate >99%
- [ ] Retry success rate >80%
- [ ] Average retry attempts per message <1.5
- [ ] Zero data loss during retry processing

## **🚨 Key Considerations**

### **Cost Management**

- Monitor retry costs to avoid excessive charges
- Implement circuit breaker for high error rates
- Use intelligent retry delays to avoid rate limiting

### **Performance Impact**

- Retry processing should not impact normal SMS flow
- Use background tasks to avoid blocking operations
- Implement proper database indexing for performance

### **Data Consistency**

- Ensure retry status is always accurate
- Handle concurrent retry attempts properly
- Maintain audit trail of all retry attempts

## **📚 Resources & References**

### **Twilio Documentation**

- [Twilio Error Codes](https://www.twilio.com/docs/api/errors)
- [Twilio Webhooks](https://www.twilio.com/docs/messaging/webhooks)
- [Twilio Rate Limits](https://www.twilio.com/docs/messaging/limits)

### **Existing Code References**

- `src/personal_assistant/workers/utils/error_handling.py` - Retry decorators
- `src/personal_assistant/workers/tasks/email_tasks.py` - Task patterns
- `src/personal_assistant/sms_router/services/routing_engine.py` - SMS routing

### **Database References**

- `src/personal_assistant/database/migrations/004_create_sms_router_tables.sql`
- `src/personal_assistant/sms_router/models/sms_models.py`

This onboarding provides comprehensive context for implementing SMS retry functionality. The existing infrastructure is well-prepared, and the implementation can build upon the solid foundation of SMS routing and background task systems.
