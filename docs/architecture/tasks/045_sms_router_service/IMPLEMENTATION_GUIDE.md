# Task 045: SMS Router Service - Implementation Guide

## 📋 **Implementation Overview**

This guide provides detailed technical implementation instructions for **Task 2.5.1.1: Create SMS Router Service**. The service will be integrated into the existing FastAPI app to enable multi-user SMS functionality using a single Twilio number with user identification by phone number.

## 🏗️ **Architecture Decisions**

### **Service Architecture**

- **Integrated FastAPI Service**: Add to existing FastAPI app on port 8000
- **Route Prefix**: Use `/sms-router` prefix for new SMS routing endpoints
- **Database Integration**: Direct connection to existing PostgreSQL database
- **Agent Core Integration**: Reuse existing Agent Core system with user context

### **Database Schema Approach**

- **Hybrid Model**: Use existing `users.phone_number` field + new routing tables
- **Separate Tables**: Create dedicated tables for SMS routing functionality
- **Performance Optimization**: Indexed phone number lookups
- **Audit Trail**: Comprehensive logging for compliance and debugging

### **User Identification Strategy**

- **Phone Number Mapping**: Direct lookup from `users.phone_number` + new mapping tables
- **Caching Layer**: Redis-based caching for frequent lookups
- **Fallback Handling**: Graceful degradation for unknown numbers

## 🔧 **Implementation Steps**

### **Step 1: Service Structure Setup**

#### **1.1 Create SMS Router Service Structure**

```bash
mkdir -p src/apps/fastapi_app/routes/sms_router
mkdir -p src/personal_assistant/sms_router/{models,services,middleware}
mkdir -p tests/test_sms_router
```

#### **1.2 Create Route Module**

```python
# src/apps/fastapi_app/routes/sms_router/__init__.py
from fastapi import APIRouter
from .webhooks import router as webhook_router

router = APIRouter(prefix="/sms-router", tags=["sms-router"])

# Include webhook routes
router.include_router(webhook_router, prefix="/webhook")
```

#### **1.3 Configuration Management**

```python
# src/personal_assistant/sms_router/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class SMSServiceSettings(BaseSettings):
    # Service Configuration
    LOG_LEVEL: str = "info"

    # Database Configuration
    DATABASE_URL: str

    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str

    # Redis Configuration (for caching)
    REDIS_URL: Optional[str] = None

    # Security Configuration
    WEBHOOK_SECRET: Optional[str] = None
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        env_prefix = "SMS_ROUTER_"

settings = SMSServiceSettings()
```

### **Step 2: Database Models**

#### **2.1 SMS Routing Models**

```python
# src/personal_assistant/sms_router/models/sms_models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from ...database.models.base import Base

class SMSRouterConfig(Base):
    """Configuration for SMS routing behavior."""
    __tablename__ = 'sms_router_configs'

    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SMSUsageLog(Base):
    """Log of SMS usage for analytics and billing."""
    __tablename__ = 'sms_usage_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message_direction = Column(String(10), nullable=False)  # 'inbound' or 'outbound'
    message_length = Column(Integer, nullable=False)
    twilio_message_sid = Column(String(50), unique=True)
    processing_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sms_usage_logs")

class UserPhoneMapping(Base):
    """Additional phone number mappings for users (extends users.phone_number)."""
    __tablename__ = 'user_phone_mappings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String(20), nullable=False)
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(50))  # 'sms', 'manual', 'oauth'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="phone_mappings")
```

#### **2.2 Update User Model Relationships**

```python
# Add to existing User model in src/personal_assistant/database/models/users.py
class User(Base):
    # ... existing fields ...

    # Add new relationships for SMS routing
    phone_mappings = relationship(
        "UserPhoneMapping", back_populates="user", cascade="all, delete-orphan"
    )
    sms_usage_logs = relationship(
        "SMSUsageLog", back_populates="user", cascade="all, delete-orphan"
    )
```

#### **2.3 Database Migration**

```python
# src/personal_assistant/sms_router/migrations/001_create_sms_router_tables.py
"""Create SMS Router Service tables.

Revision ID: 001_sms_router
Revises: 003_add_phone_number_to_users
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_sms_router'
down_revision = '003_add_phone_number_to_users'
depends_on = None

def upgrade():
    # Create sms_router_configs table
    op.create_table('sms_router_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_key', sa.String(length=100), nullable=False),
        sa.Column('config_value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_key')
    )

    # Create sms_usage_logs table
    op.create_table('sms_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('message_direction', sa.String(length=10), nullable=False),
        sa.Column('message_length', sa.Integer(), nullable=False),
        sa.Column('twilio_message_sid', sa.String(length=50), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('twilio_message_sid')
    )

    # Create user_phone_mappings table
    op.create_table('user_phone_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('verification_method', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('idx_sms_usage_logs_user_id', 'sms_usage_logs', ['user_id'])
    op.create_index('idx_sms_usage_logs_phone_number', 'sms_usage_logs', ['phone_number'])
    op.create_index('idx_sms_usage_logs_created_at', 'sms_usage_logs', ['created_at'])
    op.create_index('idx_user_phone_mappings_user_id', 'user_phone_mappings', ['user_id'])
    op.create_index('idx_user_phone_mappings_phone_number', 'user_phone_mappings', ['phone_number'])

def downgrade():
    op.drop_index('idx_user_phone_mappings_phone_number', 'user_phone_mappings')
    op.drop_index('idx_user_phone_mappings_user_id', 'user_phone_mappings')
    op.drop_index('idx_sms_usage_logs_created_at', 'sms_usage_logs')
    op.drop_index('idx_sms_usage_logs_phone_number', 'sms_usage_logs')
    op.drop_index('idx_sms_usage_logs_user_id', 'sms_usage_logs')
    op.drop_table('user_phone_mappings')
    op.drop_table('sms_usage_logs')
    op.drop_table('sms_router_configs')
```

### **Step 3: Core Services**

#### **3.1 User Identification Service**

```python
# src/personal_assistant/sms_router/services/user_identification.py
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re

from ...database.models.users import User
from ...database.models.sms_models import UserPhoneMapping
from ...database.session import AsyncSessionLocal
from .phone_validator import PhoneValidator
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class UserIdentificationService:
    """Service for identifying users by phone number."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.phone_validator = PhoneValidator()
        self.cache_manager = cache_manager or CacheManager()

    async def identify_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Identify user by phone number.

        Args:
            phone_number: Raw phone number from SMS

        Returns:
            User information dict or None if not found
        """
        try:
            # Normalize phone number
            normalized_phone = self.phone_validator.normalize_phone_number(phone_number)
            if not normalized_phone:
                logger.warning(f"Invalid phone number format: {phone_number}")
                return None

            # Check cache first
            cache_key = f"user_phone:{normalized_phone}"
            cached_user = await self.cache_manager.get(cache_key)
            if cached_user:
                logger.info(f"User found in cache for phone: {normalized_phone}")
                return cached_user

            # Database lookup - check both users.phone_number and user_phone_mappings
            user = await self._lookup_user_in_database(normalized_phone)
            if user:
                # Cache the result
                await self.cache_manager.set(cache_key, user, ttl=3600)  # 1 hour
                logger.info(f"User identified: {user['id']} for phone: {normalized_phone}")
                return user

            logger.warning(f"No user found for phone number: {normalized_phone}")
            return None

        except Exception as e:
            logger.error(f"Error identifying user by phone {phone_number}: {e}")
            return None

    async def _lookup_user_in_database(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Look up user in database by phone number."""
        async with AsyncSessionLocal() as session:
            try:
                # First check users.phone_number (primary)
                result = await session.execute(
                    select(User.id, User.email, User.full_name, User.is_active)
                    .where(User.phone_number == phone_number)
                )
                user = result.first()

                if user:
                    return {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_active': user.is_active,
                        'phone_number': phone_number,
                        'source': 'primary'
                    }

                # Then check user_phone_mappings (additional numbers)
                result = await session.execute(
                    select(User.id, User.email, User.full_name, User.is_active, UserPhoneMapping.phone_number)
                    .join(UserPhoneMapping, User.id == UserPhoneMapping.user_id)
                    .where(UserPhoneMapping.phone_number == phone_number)
                )
                user = result.first()

                if user:
                    return {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_active': user.is_active,
                        'phone_number': phone_number,
                        'source': 'mapping'
                    }

                return None

            except Exception as e:
                logger.error(f"Database error looking up user by phone: {e}")
                return None
```

### **Step 4: SMS Routing Engine**

#### **4.1 Main Routing Engine**

```python
# src/personal_assistant/sms_router/services/routing_engine.py
import logging
import time
from typing import Dict, Any, Optional
from twilio.twiml.messaging_response import MessagingResponse

from .user_identification import UserIdentificationService
from .message_processor import MessageProcessor
from .response_formatter import ResponseFormatter
from .agent_integration import AgentIntegrationService

logger = logging.getLogger(__name__)

class SMSRoutingEngine:
    """Main SMS routing engine for multi-user support."""

    def __init__(self):
        self.user_identification = UserIdentificationService()
        self.message_processor = MessageProcessor()
        self.response_formatter = ResponseFormatter()
        self.agent_integration = AgentIntegrationService()

    async def route_sms(self, from_number: str, message_body: str) -> MessagingResponse:
        """
        Route incoming SMS to appropriate user agent.

        Args:
            from_number: Sender's phone number
            message_body: SMS message content

        Returns:
            TwiML response for Twilio
        """
        start_time = time.time()

        try:
            # Step 1: Identify user
            user_info = await self.user_identification.identify_user_by_phone(from_number)
            if not user_info:
                return self._handle_unknown_user(from_number)

            # Step 2: Validate user status
            if not user_info.get('is_active', False):
                return self._handle_inactive_user(from_number)

            # Step 3: Process message
            processed_message = await self.message_processor.process_message(
                message_body, user_info
            )

            # Step 4: Route to agent
            agent_response = await self.agent_integration.process_with_agent(
                processed_message, user_info
            )

            # Step 5: Format response
            response = self.response_formatter.format_response(agent_response, user_info)

            # Step 6: Log usage
            processing_time = int((time.time() - start_time) * 1000)
            await self._log_sms_usage(user_info, from_number, 'inbound',
                                    len(message_body), processing_time, True)

            logger.info(f"SMS routed successfully for user {user_info['id']} in {processing_time}ms")
            return response

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f"Error routing SMS from {from_number}: {e}")

            # Log error usage
            if 'user_info' in locals():
                await self._log_sms_usage(user_info, from_number, 'inbound',
                                        len(message_body), processing_time, False, str(e))

            return self._handle_error_response()
```

### **Step 5: FastAPI Integration**

#### **5.1 Update Main App**

```python
# src/apps/fastapi_app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from personal_assistant.config.settings import settings

from apps.fastapi_app.middleware.auth import AuthMiddleware
from apps.fastapi_app.middleware.rate_limiting import RateLimitingMiddleware
from apps.fastapi_app.routes import twilio, auth, mfa, sessions, rbac, users, oauth, sms_router
from personal_assistant.config.monitoring import monitoring_router

# ... existing code ...

# Include routers
app.include_router(twilio.router)
app.include_router(auth.router)
app.include_router(mfa.router)
app.include_router(sessions.router)
app.include_router(rbac.router)
app.include_router(users.router)
app.include_router(oauth.router)

# Add new SMS Router routes
app.include_router(sms_router.router)

# ... rest of existing code ...
```

#### **5.2 Webhook Routes**

```python
# src/apps/fastapi_app/routes/sms_router/webhooks.py
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

from personal_assistant.sms_router.services.routing_engine import SMSRoutingEngine
from personal_assistant.sms_router.middleware.webhook_validation import validate_twilio_webhook

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
            logger.warning(f"Invalid webhook request from {request.client.host}")
            raise HTTPException(status_code=400, detail="Invalid webhook")

        logger.info(f"Processing SMS from {From}: {Body[:50]}...")

        # Route the SMS
        response = await routing_engine.route_sms(From, Body)

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
```

### **Step 6: Agent Core Integration**

#### **6.1 Agent Integration Service**

```python
# src/personal_assistant/sms_router/services/agent_integration.py
import logging
from typing import Dict, Any
from ...core import AgentCore
from ...tools import create_tool_registry
from ...llm.gemini import GeminiLLM
from ...config.settings import settings

logger = logging.getLogger(__name__)

class AgentIntegrationService:
    """Service for integrating with existing Agent Core."""

    def __init__(self):
        # Reuse existing Agent Core setup
        self.tool_registry = create_tool_registry()
        self.llm = GeminiLLM(api_key=settings.GOOGLE_API_KEY, model="gemini-2.0-flash")
        self.agent_core = AgentCore(tools=self.tool_registry, llm=self.llm)

    async def process_with_agent(self, message: str, user_info: Dict[str, Any]) -> str:
        """
        Process message with Agent Core using user context.

        Args:
            message: SMS message content
            user_info: User information including ID

        Returns:
            Agent response string
        """
        try:
            user_id = user_info['id']
            logger.info(f"Processing message for user {user_id}: {message[:50]}...")

            # Call existing Agent Core with user context
            result = await self.agent_core.run(message, user_id)

            logger.info(f"Agent response for user {user_id}: {result[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error processing message with Agent Core: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."
```

## 🚀 **Deployment Instructions**

### **1. Environment Setup**

```bash
# Add to existing .env file
SMS_ROUTER_LOG_LEVEL=info
SMS_ROUTER_WEBHOOK_SECRET=your_webhook_secret
SMS_ROUTER_RATE_LIMIT_PER_MINUTE=60
```

### **2. Database Migration**

```bash
# Run database migrations
cd src/personal_assistant/sms_router
alembic upgrade head
```

### **3. Service Integration**

```bash
# The service is now integrated into the main FastAPI app
# No separate service startup needed
# Just restart the main application
```

### **4. Twilio Configuration**

1. Log into Twilio Console
2. Navigate to Phone Numbers > Manage > Active numbers
3. Select your phone number
4. Set webhook URL to: `https://yourdomain.com/sms-router/webhook/sms`
5. Set HTTP method to POST
6. Save configuration

## 🔍 **Key Benefits of This Approach**

### **Integration Benefits**

- ✅ **No Port Conflicts**: Uses existing port 8000
- ✅ **Shared Infrastructure**: Reuses authentication, middleware, database
- ✅ **Easier Testing**: Single application to test
- ✅ **Simplified Deployment**: One service to manage

### **Database Benefits**

- ✅ **Scalability**: Multiple phone numbers per user
- ✅ **Analytics**: Comprehensive SMS usage tracking
- ✅ **Audit Trail**: Full compliance and debugging support
- ✅ **Performance**: Optimized indexes and queries

### **Architecture Benefits**

- ✅ **Reuse Existing**: Leverages current Agent Core and Twilio setup
- ✅ **User Isolation**: Maintains strict data separation
- ✅ **Future Ready**: Can migrate to separate service later if needed
- ✅ **Cost Optimized**: Single Twilio number for all users

## 📝 **Scope Notes**

**This implementation guide focuses ONLY on Task 2.5.1.1: Create SMS Router Service infrastructure.**

**Future tasks will handle:**

- Task 2.5.1.2: User Phone Number Management
- Task 2.5.1.3: Additional database schema enhancements
- Task 2.5.1.4: Twilio webhook configuration updates
- Task 2.5.1.5: Enhanced TwilioService features
- Task 2.5.1.6: SMS usage analytics and reporting

This updated implementation approach provides a practical and maintainable solution that integrates seamlessly with your existing infrastructure while delivering the multi-user SMS functionality foundation you need.
