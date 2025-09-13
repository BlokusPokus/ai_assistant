# Task 071: SMS Retry Functionality Implementation

## **📋 Task Overview**

**Task ID**: 071  
**Task Name**: SMS Retry Functionality Implementation  
**Phase**: 2.4 - Reliability & Monitoring  
**Module**: 2.4.1 - Message Delivery Reliability  
**Status**: 🚀 **READY TO START**  
**Target Start Date**: January 2025  
**Effort Estimate**: 1 day (simplified approach)  
**Dependencies**: Task 045 (SMS Router Service) ✅ **COMPLETED**, Task 037 (Background Task System) ✅ **COMPLETED**

> **💡 SIMPLIFIED APPROACH**: After analysis, we can implement SMS retry functionality using the existing `SMSUsageLog` table and Celery's built-in retry mechanisms. This reduces implementation time from 3-4 days to ~4 hours. See `SIMPLIFIED_APPROACH.md` for details.

## **🎯 Task Objectives**

### **Primary Goal**

Implement comprehensive SMS retry functionality to ensure reliable message delivery and improve user experience by automatically handling failed SMS transmissions.

### **Key Objectives**

1. **Reliable Delivery**: Ensure SMS messages are delivered even when initial attempts fail
2. **Intelligent Retry Logic**: Implement smart retry strategies based on error types
3. **User Experience**: Minimize user impact from SMS delivery failures
4. **Monitoring & Analytics**: Track retry patterns and success rates
5. **Cost Optimization**: Avoid unnecessary retries that could increase costs

## **🔍 Current State Analysis**

### **Existing SMS Infrastructure ✅ READY**

**SMS Services Available**:

- `TwilioService` (`src/personal_assistant/communication/twilio_integration/twilio_client.py`)
- `SMSRoutingEngine` (`src/personal_assistant/sms_router/services/routing_engine.py`)
- `NotificationService` (`src/personal_assistant/tools/ai_scheduler/notifications/service.py`)

**Database Models Ready**:

- `SMSUsageLog` - Tracks SMS usage and success/failure
- `SMSRouterConfig` - Configuration management
- `UserPhoneMapping` - Phone number management

**Background Task System ✅ COMPLETED**:

- Celery workers with retry capabilities
- Task scheduling and monitoring
- Error handling infrastructure

### **Current Limitations ❌ NEEDS IMPROVEMENT**

1. **No Retry Logic**: SMS failures are logged but not retried
2. **No Delivery Confirmation**: No tracking of actual delivery status
3. **No Error Classification**: All errors treated the same way
4. **No Exponential Backoff**: No intelligent retry timing
5. **No Circuit Breaker**: No protection against cascading failures

## **🏗️ Implementation Plan**

### **Phase 1: Database Schema Enhancement (Day 1)**

#### **1.1 Create SMS Retry Tracking Table**

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

-- Indexes for performance
CREATE INDEX idx_sms_retry_queue_status ON sms_retry_queue(status);
CREATE INDEX idx_sms_retry_queue_next_retry ON sms_retry_queue(next_retry_at);
CREATE INDEX idx_sms_retry_queue_user_id ON sms_retry_queue(user_id);
```

#### **1.2 Update SMS Usage Logs**

```sql
ALTER TABLE sms_usage_logs
ADD COLUMN retry_count INTEGER DEFAULT 0,
ADD COLUMN final_status VARCHAR(20) DEFAULT 'unknown',
ADD COLUMN delivery_confirmed_at TIMESTAMP;
```

### **Phase 2: Retry Service Implementation (Day 2)**

#### **2.1 Create SMS Retry Service**

```python
# src/personal_assistant/sms_router/services/retry_service.py
class SMSRetryService:
    """Handles SMS retry logic and delivery confirmation."""

    def __init__(self):
        self.twilio_service = TwilioService()
        self.db_session = get_db_session()

    async def queue_for_retry(self, sms_log_id: int, error_code: str, error_message: str):
        """Queue a failed SMS for retry."""

    async def process_retry_queue(self):
        """Process pending retries."""

    async def handle_delivery_confirmation(self, message_sid: str, status: str):
        """Handle Twilio delivery status webhooks."""

    def _calculate_retry_delay(self, retry_count: int, error_code: str) -> int:
        """Calculate intelligent retry delay."""
```

#### **2.2 Error Classification System**

```python
class SMSErrorClassifier:
    """Classifies SMS errors for appropriate retry strategies."""

    RETRYABLE_ERRORS = {
        '30001': 'Temporary network issue',
        '30002': 'Temporary service unavailable',
        '30003': 'Rate limit exceeded',
        '30004': 'Temporary carrier issue'
    }

    NON_RETRYABLE_ERRORS = {
        '21211': 'Invalid phone number',
        '21214': 'Invalid message body',
        '21610': 'Message blocked by carrier'
    }
```

### **Phase 3: Celery Task Integration (Day 3)**

#### **3.1 Create SMS Retry Tasks**

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
    """Clean up old retry records."""
```

#### **3.2 Update Celery Beat Schedule**

```python
# Add to celery_app.py beat_schedule
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
```

### **Phase 4: Integration & Testing (Day 4)**

#### **4.1 Update Existing SMS Services**

- Modify `TwilioService.send_sms()` to use retry service
- Update `SMSRoutingEngine.send_sms()` to queue retries
- Enhance `NotificationService` with retry capabilities

#### **4.2 Webhook Integration**

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
```

#### **4.3 Monitoring & Analytics**

- Add retry metrics to existing analytics
- Create retry success rate dashboards
- Implement alerting for high retry rates

## **📊 Success Metrics**

### **Reliability Metrics**

- SMS delivery success rate: Target >99%
- Retry success rate: Target >80%
- Average retry attempts per message: Target <1.5

### **Performance Metrics**

- Retry processing time: Target <30 seconds
- Queue processing latency: Target <2 minutes
- Database query performance: Target <100ms

### **Cost Metrics**

- Retry cost per message: Monitor and optimize
- Unnecessary retry reduction: Target 20% reduction

## **🔧 Technical Requirements**

### **Dependencies**

- Twilio API access with webhook support
- Redis for retry queue management
- PostgreSQL for retry tracking
- Celery workers for background processing

### **Configuration**

```python
# SMS Retry Configuration
SMS_RETRY_CONFIG = {
    'max_retries': 3,
    'base_delay': 60,  # seconds
    'max_delay': 3600,  # 1 hour
    'retry_multiplier': 2,
    'cleanup_after_days': 7,
    'batch_size': 50
}
```

## **🚨 Risk Mitigation**

### **Potential Risks**

1. **Cost Increase**: Excessive retries could increase Twilio costs
2. **Performance Impact**: Retry processing could slow down system
3. **Data Consistency**: Retry tracking could get out of sync

### **Mitigation Strategies**

1. **Smart Retry Logic**: Only retry recoverable errors
2. **Rate Limiting**: Implement retry rate limits
3. **Monitoring**: Real-time monitoring of retry patterns
4. **Circuit Breaker**: Stop retries if error rate is too high

## **📋 Implementation Checklist**

### **Phase 1: Database Schema**

- [ ] Create `sms_retry_queue` table
- [ ] Update `sms_usage_logs` table
- [ ] Create necessary indexes
- [ ] Run database migration

### **Phase 2: Retry Service**

- [ ] Implement `SMSRetryService` class
- [ ] Create error classification system
- [ ] Implement retry delay calculation
- [ ] Add delivery confirmation handling

### **Phase 3: Celery Integration**

- [ ] Create SMS retry tasks
- [ ] Update Celery beat schedule
- [ ] Implement retry queue processing
- [ ] Add cleanup tasks

### **Phase 4: Integration**

- [ ] Update existing SMS services
- [ ] Implement webhook handlers
- [ ] Add monitoring and analytics
- [ ] Create comprehensive tests

### **Testing & Validation**

- [ ] Unit tests for retry service
- [ ] Integration tests for Celery tasks
- [ ] End-to-end SMS retry flow testing
- [ ] Performance testing under load
- [ ] Cost analysis and optimization

## **📚 Documentation Requirements**

- [ ] API documentation for retry service
- [ ] Configuration guide for retry settings
- [ ] Monitoring and alerting setup guide
- [ ] Troubleshooting guide for retry issues
- [ ] Cost optimization recommendations

## **🎯 Expected Outcomes**

1. **Improved Reliability**: SMS delivery success rate >99%
2. **Better User Experience**: Automatic handling of delivery failures
3. **Cost Optimization**: Intelligent retry logic reduces unnecessary costs
4. **Operational Visibility**: Clear monitoring of SMS delivery patterns
5. **Scalable Foundation**: Retry system that can handle increased SMS volume

This task will significantly improve the reliability of SMS delivery in the personal assistant system, ensuring users receive their messages even when initial delivery attempts fail.
