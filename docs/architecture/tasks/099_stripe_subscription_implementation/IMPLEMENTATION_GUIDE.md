# Task 099: Stripe Subscription Implementation - Detailed Implementation Guide

## 📋 **Implementation Overview**

This document provides detailed implementation guidance for integrating Stripe subscriptions into the Personal Assistant TDAH system, following the existing architecture patterns and maintaining security and compliance standards.

## 🏗️ **Phase 1: Foundation & Database Implementation**

### **Task 1.1: Database Schema Design**

#### **Database Migration Script**

```sql
-- File: migrations/010_add_subscription_system.sql

-- Add subscription fields to users table
ALTER TABLE users ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'trial';
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'free_trial';
ALTER TABLE users ADD COLUMN trial_ends_at TIMESTAMP;
ALTER TABLE users ADD COLUMN subscription_ends_at TIMESTAMP;
ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255) UNIQUE;

-- Create subscriptions table
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255) NOT NULL,
    tier VARCHAR(50) NOT NULL CHECK (tier IN ('free_trial', 'premium', 'pro')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid', 'trialing')),
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create billing history table
CREATE TABLE billing_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE CASCADE,
    stripe_invoice_id VARCHAR(255) UNIQUE NOT NULL,
    amount INTEGER NOT NULL, -- Amount in cents
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50) NOT NULL CHECK (status IN ('paid', 'open', 'void', 'uncollectible')),
    paid_at TIMESTAMP,
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create payment methods table
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_payment_method_id VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL, -- card, bank_account, etc.
    is_default BOOLEAN DEFAULT FALSE,
    last_four VARCHAR(4),
    brand VARCHAR(50), -- visa, mastercard, etc.
    exp_month INTEGER,
    exp_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_billing_history_user_id ON billing_history(user_id);
CREATE INDEX idx_billing_history_subscription_id ON billing_history(subscription_id);
CREATE INDEX idx_payment_methods_user_id ON payment_methods(user_id);
CREATE INDEX idx_users_stripe_customer_id ON users(stripe_customer_id);

-- Add audit logging for subscription events
CREATE TABLE subscription_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscription_audit_user_id ON subscription_audit_log(user_id);
CREATE INDEX idx_subscription_audit_event_type ON subscription_audit_log(event_type);
```

#### **SQLAlchemy Models**

```python
# File: src/personal_assistant/database/models/subscriptions.py

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_customer_id = Column(String(255), nullable=False)
    tier = Column(String(50), nullable=False)  # free_trial, premium, pro
    status = Column(String(50), nullable=False)  # active, canceled, past_due, unpaid, trialing
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")
    billing_history = relationship("BillingHistory", back_populates="subscription", cascade="all, delete-orphan")

class BillingHistory(Base):
    __tablename__ = "billing_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True)
    stripe_invoice_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), default="usd")
    status = Column(String(50), nullable=False)  # paid, open, void, uncollectible
    paid_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="billing_history")
    subscription = relationship("Subscription", back_populates="billing_history")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_payment_method_id = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=False)  # card, bank_account, etc.
    is_default = Column(Boolean, default=False)
    last_four = Column(String(4), nullable=True)
    brand = Column(String(50), nullable=True)  # visa, mastercard, etc.
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payment_methods")

class SubscriptionAuditLog(Base):
    __tablename__ = "subscription_audit_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription_audit_logs")
    subscription = relationship("Subscription", back_populates="audit_logs")
```

#### **Update User Model**

```python
# File: src/personal_assistant/database/models/users.py (additions)

# Add to existing User class
class User(Base):
    # ... existing fields ...

    # Subscription fields
    subscription_status = Column(String(50), default="trial")
    subscription_tier = Column(String(50), default="free_trial")
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)

    # ... existing relationships ...

    # Subscription relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    billing_history = relationship("BillingHistory", back_populates="user", cascade="all, delete-orphan")
    payment_methods = relationship("PaymentMethod", back_populates="user", cascade="all, delete-orphan")
    subscription_audit_logs = relationship("SubscriptionAuditLog", back_populates="user", cascade="all, delete-orphan")
```

### **Task 1.2: Stripe Configuration & Setup**

#### **Stripe Service Implementation**

```python
# File: src/personal_assistant/services/stripe_service.py

import stripe
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from personal_assistant.config.settings import settings
from personal_assistant.database.models.subscriptions import Subscription, BillingHistory, PaymentMethod
from personal_assistant.database.models.users import User

logger = logging.getLogger(__name__)

class StripeService:
    """Service for handling Stripe operations."""

    def __init__(self):
        """Initialize Stripe service."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        # Configure Stripe settings
        stripe.api_version = "2023-10-16"  # Use stable API version

        logger.info("Stripe service initialized")

    async def create_customer(self, user: User) -> str:
        """Create a Stripe customer for a user."""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    "user_id": str(user.id),
                    "phone_number": user.phone_number or "",
                }
            )

            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            return customer.id

        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_period_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a Stripe subscription."""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"],
            }

            if trial_period_days:
                subscription_data["trial_period_days"] = trial_period_days

            subscription = stripe.Subscription.create(**subscription_data)

            logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Error creating subscription: {e}")
            raise

    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get a Stripe subscription."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription {subscription_id}: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True
    ) -> Dict[str, Any]:
        """Cancel a Stripe subscription."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=cancel_at_period_end
            )

            logger.info(f"Cancelled subscription {subscription_id}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling subscription {subscription_id}: {e}")
            raise

    async def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str
    ) -> Dict[str, Any]:
        """Update a Stripe subscription to a new price."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0]["id"],
                    "price": new_price_id,
                }],
                proration_behavior="create_prorations",
            )

            updated_subscription = stripe.Subscription.retrieve(subscription_id)

            logger.info(f"Updated subscription {subscription_id} to price {new_price_id}")
            return updated_subscription

        except stripe.error.StripeError as e:
            logger.error(f"Error updating subscription {subscription_id}: {e}")
            raise

    async def get_customer_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get payment methods for a customer."""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            return payment_methods.data
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving payment methods for customer {customer_id}: {e}")
            raise

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a payment intent for one-time payments."""
        try:
            intent_data = {
                "amount": amount,
                "currency": currency,
                "automatic_payment_methods": {"enabled": True},
            }

            if customer_id:
                intent_data["customer"] = customer_id

            intent = stripe.PaymentIntent.create(**intent_data)

            logger.info(f"Created payment intent {intent.id}")
            return intent

        except stripe.error.StripeError as e:
            logger.error(f"Error creating payment intent: {e}")
            raise

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Construct and verify webhook event."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise
```

#### **Configuration Settings**

```python
# File: src/personal_assistant/config/settings.py (additions)

# Stripe Configuration
STRIPE_SECRET_KEY: str = Field(..., env="STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET: str = Field(..., env="STRIPE_WEBHOOK_SECRET")

# Subscription Configuration
STRIPE_PREMIUM_PRICE_ID: str = Field(..., env="STRIPE_PREMIUM_PRICE_ID")
STRIPE_PRO_PRICE_ID: str = Field(..., env="STRIPE_PRO_PRICE_ID")
TRIAL_PERIOD_DAYS: int = Field(default=14, env="TRIAL_PERIOD_DAYS")
```

### **Task 1.3: Core Subscription Models**

#### **Pydantic Models**

```python
# File: src/apps/fastapi_app/models/subscriptions.py

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class SubscriptionBase(BaseModel):
    tier: str = Field(..., description="Subscription tier")
    status: str = Field(..., description="Subscription status")

class SubscriptionCreate(SubscriptionBase):
    price_id: str = Field(..., description="Stripe price ID")
    trial_period_days: Optional[int] = Field(None, description="Trial period in days")

class SubscriptionUpdate(BaseModel):
    tier: Optional[str] = Field(None, description="New subscription tier")
    cancel_at_period_end: Optional[bool] = Field(None, description="Cancel at period end")

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    stripe_subscription_id: str
    stripe_customer_id: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    canceled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BillingHistoryResponse(BaseModel):
    id: int
    stripe_invoice_id: str
    amount: int
    currency: str
    status: str
    paid_at: Optional[datetime]
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentMethodResponse(BaseModel):
    id: int
    stripe_payment_method_id: str
    type: str
    is_default: bool
    last_four: Optional[str]
    brand: Optional[str]
    exp_month: Optional[int]
    exp_year: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionStatsResponse(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    monthly_revenue: float
    churn_rate: float
```

## 🚀 **Phase 2: Backend API Implementation**

### **Task 2.1: Subscription API Endpoints**

#### **Subscription Routes**

```python
# File: src/apps/fastapi_app/routes/subscriptions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from personal_assistant.database.session import get_db
from personal_assistant.middleware.auth import AuthMiddleware
from personal_assistant.services.stripe_service import StripeService
from personal_assistant.database.models.users import User
from personal_assistant.database.models.subscriptions import Subscription, BillingHistory
from apps.fastapi_app.models.subscriptions import (
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    BillingHistoryResponse, SubscriptionStatsResponse
)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthMiddleware.get_current_user),
    stripe_service: StripeService = Depends()
):
    """Create a new subscription for the current user."""
    try:
        # Check if user already has an active subscription
        existing_subscription = await db.execute(
            select(Subscription).where(
                Subscription.user_id == current_user.id,
                Subscription.status.in_(["active", "trialing"])
            )
        )
        if existing_subscription.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription"
            )

        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer_id = await stripe_service.create_customer(current_user)
            current_user.stripe_customer_id = customer_id
            await db.commit()
        else:
            customer_id = current_user.stripe_customer_id

        # Create Stripe subscription
        stripe_subscription = await stripe_service.create_subscription(
            customer_id=customer_id,
            price_id=subscription_data.price_id,
            trial_period_days=subscription_data.trial_period_days
        )

        # Create local subscription record
        subscription = Subscription(
            user_id=current_user.id,
            stripe_subscription_id=stripe_subscription["id"],
            stripe_customer_id=customer_id,
            tier=subscription_data.tier,
            status=stripe_subscription["status"],
            current_period_start=datetime.fromtimestamp(
                stripe_subscription["current_period_start"]
            ),
            current_period_end=datetime.fromtimestamp(
                stripe_subscription["current_period_end"]
            ),
            cancel_at_period_end=stripe_subscription.get("cancel_at_period_end", False)
        )

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        # Update user subscription status
        current_user.subscription_status = stripe_subscription["status"]
        current_user.subscription_tier = subscription_data.tier
        if stripe_subscription.get("trial_end"):
            current_user.trial_ends_at = datetime.fromtimestamp(
                stripe_subscription["trial_end"]
            )
        current_user.subscription_ends_at = subscription.current_period_end
        await db.commit()

        return subscription

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )

@router.get("/me", response_model=SubscriptionResponse)
async def get_current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthMiddleware.get_current_user)
):
    """Get the current user's subscription."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    return subscription

@router.put("/me", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_update: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthMiddleware.get_current_user),
    stripe_service: StripeService = Depends()
):
    """Update the current user's subscription."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    try:
        # Handle tier changes
        if subscription_update.tier and subscription_update.tier != subscription.tier:
            # Map tier to price ID
            price_mapping = {
                "premium": settings.STRIPE_PREMIUM_PRICE_ID,
                "pro": settings.STRIPE_PRO_PRICE_ID
            }

            if subscription_update.tier not in price_mapping:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid subscription tier"
                )

            # Update Stripe subscription
            stripe_subscription = await stripe_service.update_subscription(
                subscription.stripe_subscription_id,
                price_mapping[subscription_update.tier]
            )

            # Update local subscription
            subscription.tier = subscription_update.tier
            subscription.status = stripe_subscription["status"]
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription["current_period_start"]
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription["current_period_end"]
            )

        # Handle cancellation
        if subscription_update.cancel_at_period_end is not None:
            stripe_subscription = await stripe_service.cancel_subscription(
                subscription.stripe_subscription_id,
                subscription_update.cancel_at_period_end
            )

            subscription.cancel_at_period_end = subscription_update.cancel_at_period_end
            if subscription_update.cancel_at_period_end:
                subscription.canceled_at = datetime.utcnow()

        await db.commit()
        await db.refresh(subscription)

        return subscription

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )

@router.get("/me/history", response_model=List[BillingHistoryResponse])
async def get_billing_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthMiddleware.get_current_user)
):
    """Get the current user's billing history."""
    result = await db.execute(
        select(BillingHistory)
        .where(BillingHistory.user_id == current_user.id)
        .order_by(BillingHistory.created_at.desc())
    )
    billing_history = result.scalars().all()

    return billing_history
```

### **Task 2.2: Stripe Webhook Processing**

#### **Webhook Routes**

```python
# File: src/apps/fastapi_app/routes/webhooks.py

from fastapi import APIRouter, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from personal_assistant.database.session import get_db
from personal_assistant.services.stripe_service import StripeService
from personal_assistant.database.models.subscriptions import Subscription, BillingHistory, SubscriptionAuditLog
from personal_assistant.database.models.users import User

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_service: StripeService = Depends()
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )

    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )

    # Process the event
    try:
        await process_stripe_event(event, db)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing webhook event {event['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

async def process_stripe_event(event: dict, db: AsyncSession):
    """Process Stripe webhook events."""
    event_type = event["type"]

    # Log the event
    logger.info(f"Processing Stripe event: {event_type}")

    if event_type == "customer.subscription.created":
        await handle_subscription_created(event, db)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(event, db)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(event, db)
    elif event_type == "invoice.payment_succeeded":
        await handle_payment_succeeded(event, db)
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(event, db)
    elif event_type == "customer.subscription.trial_will_end":
        await handle_trial_will_end(event, db)
    else:
        logger.info(f"Unhandled event type: {event_type}")

async def handle_subscription_created(event: dict, db: AsyncSession):
    """Handle subscription created event."""
    subscription_data = event["data"]["object"]

    # Find user by Stripe customer ID
    result = await db.execute(
        select(User).where(User.stripe_customer_id == subscription_data["customer"])
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.error(f"User not found for customer {subscription_data['customer']}")
        return

    # Create or update subscription record
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_data["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=subscription_data["id"],
            stripe_customer_id=subscription_data["customer"],
            tier=determine_tier_from_price(subscription_data["items"]["data"][0]["price"]["id"]),
            status=subscription_data["status"],
            current_period_start=datetime.fromtimestamp(subscription_data["current_period_start"]),
            current_period_end=datetime.fromtimestamp(subscription_data["current_period_end"]),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False)
        )
        db.add(subscription)

    # Update user subscription status
    user.subscription_status = subscription_data["status"]
    user.subscription_tier = subscription.tier
    user.subscription_ends_at = subscription.current_period_end

    # Log the event
    audit_log = SubscriptionAuditLog(
        user_id=user.id,
        subscription_id=subscription.id,
        event_type="subscription_created",
        event_data=subscription_data
    )
    db.add(audit_log)

    await db.commit()
    logger.info(f"Subscription created for user {user.id}")

async def handle_subscription_updated(event: dict, db: AsyncSession):
    """Handle subscription updated event."""
    subscription_data = event["data"]["object"]

    # Find subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_data["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.error(f"Subscription not found: {subscription_data['id']}")
        return

    # Update subscription
    subscription.status = subscription_data["status"]
    subscription.current_period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
    subscription.current_period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
    subscription.cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)

    if subscription_data.get("canceled_at"):
        subscription.canceled_at = datetime.fromtimestamp(subscription_data["canceled_at"])

    # Update user
    user = subscription.user
    user.subscription_status = subscription_data["status"]
    user.subscription_ends_at = subscription.current_period_end

    # Log the event
    audit_log = SubscriptionAuditLog(
        user_id=user.id,
        subscription_id=subscription.id,
        event_type="subscription_updated",
        event_data=subscription_data
    )
    db.add(audit_log)

    await db.commit()
    logger.info(f"Subscription updated for user {user.id}")

async def handle_payment_succeeded(event: dict, db: AsyncSession):
    """Handle successful payment event."""
    invoice_data = event["data"]["object"]

    # Find subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == invoice_data["subscription"]
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.error(f"Subscription not found for invoice: {invoice_data['id']}")
        return

    # Create billing history record
    billing_record = BillingHistory(
        user_id=subscription.user_id,
        subscription_id=subscription.id,
        stripe_invoice_id=invoice_data["id"],
        amount=invoice_data["amount_paid"],
        currency=invoice_data["currency"],
        status="paid",
        paid_at=datetime.fromtimestamp(invoice_data["status_transitions"]["paid_at"]),
        due_date=datetime.fromtimestamp(invoice_data["due_date"]) if invoice_data.get("due_date") else None
    )
    db.add(billing_record)

    # Log the event
    audit_log = SubscriptionAuditLog(
        user_id=subscription.user_id,
        subscription_id=subscription.id,
        event_type="payment_succeeded",
        event_data=invoice_data
    )
    db.add(audit_log)

    await db.commit()
    logger.info(f"Payment succeeded for user {subscription.user_id}")

def determine_tier_from_price(price_id: str) -> str:
    """Determine subscription tier from Stripe price ID."""
    if price_id == settings.STRIPE_PREMIUM_PRICE_ID:
        return "premium"
    elif price_id == settings.STRIPE_PRO_PRICE_ID:
        return "pro"
    else:
        return "free_trial"
```

This implementation provides a comprehensive foundation for the Stripe subscription system, following the existing architecture patterns and maintaining security and compliance standards. The next phases would involve frontend implementation and admin functionality.
