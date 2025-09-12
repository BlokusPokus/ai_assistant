# Implementation Plan: Interactive SMS Onboarding Flow

## 🏗 **Architecture Overview**

### **Core Components**

1. **OnboardingConversationManager**

   - Manages conversation state and flow progression
   - Handles user input parsing and validation
   - Coordinates with other services

2. **OnboardingResponseFormatter**

   - Generates contextual messages for each step
   - Handles message formatting and length optimization
   - Manages fallback responses

3. **SignupLinkGenerator**

   - Generates personalized signup links with phone number
   - Handles link formatting and validation

4. **OnboardingSessionStorage**
   - Stores temporary conversation state
   - Handles session cleanup and expiration
   - Provides quick lookups by phone number

## 📁 **File Structure**

```
src/personal_assistant/sms_router/
├── services/
│   ├── onboarding/
│   │   ├── __init__.py
│   │   ├── conversation_manager.py
│   │   ├── response_formatter.py
│   │   ├── signup_link_generator.py
│   │   └── session_storage.py
│   └── response_formatter.py (updated)
├── models/
│   └── onboarding_models.py
└── middleware/
    └── onboarding_middleware.py
```

## 🔄 **Implementation Steps**

### **Step 1: Database Schema**

```sql
-- Migration: 006_interactive_sms_onboarding
-- Description: Add SMS onboarding session tracking

CREATE TABLE sms_onboarding_sessions (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    current_step VARCHAR(50) NOT NULL,
    collected_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
);

-- Indexes for performance
CREATE INDEX idx_sms_onboarding_phone ON sms_onboarding_sessions(phone_number);
CREATE INDEX idx_sms_onboarding_expires ON sms_onboarding_sessions(expires_at);

-- Cleanup old sessions (run periodically)
CREATE OR REPLACE FUNCTION cleanup_expired_onboarding_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sms_onboarding_sessions
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
```

### **Step 2: Core Models**

```python
# src/personal_assistant/sms_router/models/onboarding_models.py

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OnboardingStep(Enum):
    WELCOME = "welcome"
    FEATURE_OVERVIEW = "feature_overview"
    QUICK_START = "quick_start"
    LEARN_MORE = "learn_more"
    SIGNUP_LINK = "signup_link"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"

class OnboardingSession(Base):
    __tablename__ = 'sms_onboarding_sessions'

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), nullable=False)
    current_step = Column(String(50), nullable=False)
    collected_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
```

### **Step 3: Conversation Manager**

```python
# src/personal_assistant/sms_router/services/onboarding/conversation_manager.py

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.onboarding_models import OnboardingStep, OnboardingSession
from .session_storage import OnboardingSessionStorage
from .response_formatter import OnboardingResponseFormatter
from .signup_link_generator import SignupLinkGenerator

logger = logging.getLogger(__name__)

class OnboardingConversationManager:
    """Manages the interactive onboarding conversation flow."""

    def __init__(self):
        self.session_storage = OnboardingSessionStorage()
        self.response_formatter = OnboardingResponseFormatter()
        self.signup_generator = SignupLinkGenerator()

    async def handle_unregistered_user(self, phone_number: str, message: str) -> str:
        """Handle message from unregistered user."""
        try:
            # Get or create session
            session = await self.session_storage.get_or_create_session(phone_number)

            # Process message based on current step
            response = await self._process_message(session, message)

            # Update session
            await self.session_storage.update_session(session)

            return response

        except Exception as e:
            logger.error(f"Error handling onboarding conversation: {e}")
            return self.response_formatter.get_fallback_response()

    async def _process_message(self, session: OnboardingSession, message: str) -> str:
        """Process message based on current step."""
        message_clean = message.strip().upper()

        if session.current_step == OnboardingStep.WELCOME.value:
            return await self._handle_welcome_response(session, message_clean)
        elif session.current_step == OnboardingStep.FEATURE_OVERVIEW.value:
            return await self._handle_feature_response(session, message_clean)
        elif session.current_step == OnboardingStep.SIGNUP_LINK.value:
            return await self._handle_signup_link(session, message)
        else:
            return self.response_formatter.get_fallback_response()

    async def _handle_welcome_response(self, session: OnboardingSession, message: str) -> str:
        """Handle response to welcome message."""
        if message in ['A', 'SEE WHAT I CAN DO']:
            session.current_step = OnboardingStep.FEATURE_OVERVIEW.value
            return self.response_formatter.get_feature_overview()
        elif message in ['B', 'GET STARTED NOW', 'GET STARTED']:
            session.current_step = OnboardingStep.SIGNUP_LINK.value
            return self.response_formatter.get_signup_link_message(session.phone_number)
        elif message in ['C', 'LEARN MORE']:
            session.current_step = OnboardingStep.LEARN_MORE.value
            return self.response_formatter.get_learn_more()
        else:
            return self.response_formatter.get_welcome_message()

    async def _handle_feature_response(self, session: OnboardingSession, message: str) -> str:
        """Handle response to feature overview."""
        if message in ['YES', 'Y', 'GET STARTED', 'START']:
            session.current_step = OnboardingStep.SIGNUP_LINK.value
            return self.response_formatter.get_signup_link_message(session.phone_number)
        else:
            return self.response_formatter.get_feature_overview()

    async def _handle_signup_link(self, session: OnboardingSession, message: str) -> str:
        """Handle signup link generation."""
        # Generate personalized signup link
        signup_link = self.signup_generator.generate_signup_link(session.phone_number)

        # Store signup link in session
        session.collected_data['signup_link'] = signup_link

        session.current_step = OnboardingStep.CONFIRMATION.value
        return self.response_formatter.get_confirmation_message(signup_link)
```

### **Step 4: Response Formatter**

```python
# src/personal_assistant/sms_router/services/onboarding/response_formatter.py

from typing import Dict, Any

class OnboardingResponseFormatter:
    """Formats responses for the onboarding conversation flow."""

    def get_welcome_message(self) -> str:
        """Get the initial welcome message."""
        return (
            "Hi! I'm your AI assistant. I can help with tasks, reminders, and more. "
            "Would you like to:\n"
            "A) See what I can do\n"
            "B) Get started now\n"
            "C) Learn more"
        )

    def get_feature_overview(self) -> str:
        """Get the feature overview message."""
        return (
            "I can help you with:\n"
            "📝 Create and manage tasks\n"
            "📅 Set reminders and events\n"
            "📧 Manage emails\n"
            "📊 Track your productivity\n"
            "And much more!\n\n"
            "Ready to get started? Reply 'YES' to create your account."
        )

    def get_signup_link_message(self, phone_number: str) -> str:
        """Get the signup link message."""
        signup_link = f"https://yourwebsite.com/signup?phone={phone_number}"
        return (
            "Great! Let's get you set up quickly.\n\n"
            f"Here's your signup link:\n{signup_link}\n\n"
            "Complete signup there, then text me back!"
        )

    def get_confirmation_message(self, signup_link: str) -> str:
        """Get the confirmation message."""
        return (
            "Perfect! I've shared your signup link.\n\n"
            "Once you complete signup, text me back and I'll help you "
            "get started with your first task!"
        )

    def get_fallback_response(self) -> str:
        """Get fallback response for unexpected inputs."""
        return (
            "I'm not sure what you mean. Let's start over!\n\n"
            "Would you like to:\n"
            "A) See what I can do\n"
            "B) Get started now\n"
            "C) Learn more"
        )
```

### **Step 5: Integration with SMS Router**

```python
# Update src/personal_assistant/sms_router/services/response_formatter.py

from .onboarding.conversation_manager import OnboardingConversationManager

class ResponseFormatter:
    def __init__(self):
        self.max_sms_length: int = 1600
        self.max_concatenated_length: int = 3200
        self.onboarding_manager = OnboardingConversationManager()

    def format_unknown_user_response(self, phone_number: str) -> MessagingResponse:
        """Format response for unknown phone numbers with interactive onboarding."""
        response = MessagingResponse()

        # Get interactive onboarding message
        onboarding_message = await self.onboarding_manager.handle_unregistered_user(
            phone_number, "start"
        )

        response.message(onboarding_message)
        return response
```

## 🧪 **Testing Strategy**

### **Unit Tests**

- Test each conversation step
- Test input parsing and validation
- Test email validation
- Test session management

### **Integration Tests**

- Test complete onboarding flow
- Test database operations
- Test email sending
- Test SMS response formatting

### **End-to-End Tests**

- Test with real phone numbers
- Test with various user inputs
- Test error scenarios
- Test session expiration

## 📊 **Monitoring & Analytics**

### **Key Metrics**

- Onboarding completion rate
- Step-by-step conversion rates
- Time spent in each step
- Drop-off points
- Email collection success rate

### **Logging**

- Conversation flow tracking
- User input logging
- Error tracking
- Performance metrics

## 🚀 **Deployment Plan**

### **Phase 1: Core Implementation**

1. Database migration
2. Core conversation manager
3. Basic response formatter
4. Integration with SMS router

### **Phase 2: Email Integration**

1. Email collection service
2. Signup link generation
3. Email sending integration
4. Confirmation handling

### **Phase 3: Testing & Optimization**

1. Comprehensive testing
2. Performance optimization
3. Error handling improvements
4. Analytics integration

### **Phase 4: Monitoring & Iteration**

1. Real-time monitoring
2. A/B testing framework
3. Continuous optimization
4. User feedback integration
