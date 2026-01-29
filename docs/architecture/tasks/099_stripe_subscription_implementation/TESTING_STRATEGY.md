# Task 099: Stripe Subscription Implementation - Testing & Quality Assurance

## 📋 **Testing Strategy Overview**

This document outlines the comprehensive testing strategy for the Stripe subscription implementation, ensuring reliability, security, and compliance with existing system standards.

## 🧪 **Testing Phases**

### **Phase 1: Unit Testing**

#### **Backend Unit Tests**

```python
# File: tests/unit/test_stripe_service.py

import pytest
from unittest.mock import Mock, patch, AsyncMock
from personal_assistant.services.stripe_service import StripeService
from personal_assistant.database.models.users import User

class TestStripeService:
    """Test cases for StripeService."""

    @pytest.fixture
    def stripe_service(self):
        """Create StripeService instance for testing."""
        return StripeService()

    @pytest.fixture
    def mock_user(self):
        """Create mock user for testing."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.phone_number = "+1234567890"
        return user

    @patch('stripe.Customer.create')
    async def test_create_customer_success(self, mock_create, stripe_service, mock_user):
        """Test successful customer creation."""
        mock_create.return_value = {"id": "cus_test123"}

        customer_id = await stripe_service.create_customer(mock_user)

        assert customer_id == "cus_test123"
        mock_create.assert_called_once_with(
            email=mock_user.email,
            name=mock_user.full_name,
            metadata={
                "user_id": str(mock_user.id),
                "phone_number": mock_user.phone_number,
            }
        )

    @patch('stripe.Customer.create')
    async def test_create_customer_stripe_error(self, mock_create, stripe_service, mock_user):
        """Test customer creation with Stripe error."""
        mock_create.side_effect = stripe.error.StripeError("Stripe error")

        with pytest.raises(stripe.error.StripeError):
            await stripe_service.create_customer(mock_user)

    @patch('stripe.Subscription.create')
    async def test_create_subscription_success(self, mock_create, stripe_service):
        """Test successful subscription creation."""
        mock_subscription = {
            "id": "sub_test123",
            "status": "trialing",
            "current_period_start": 1640995200,
            "current_period_end": 1643673600,
        }
        mock_create.return_value = mock_subscription

        result = await stripe_service.create_subscription(
            customer_id="cus_test123",
            price_id="price_test123",
            trial_period_days=14
        )

        assert result == mock_subscription
        mock_create.assert_called_once()

    @patch('stripe.Subscription.modify')
    async def test_cancel_subscription_success(self, mock_modify, stripe_service):
        """Test successful subscription cancellation."""
        mock_subscription = {
            "id": "sub_test123",
            "cancel_at_period_end": True,
        }
        mock_modify.return_value = mock_subscription

        result = await stripe_service.cancel_subscription(
            subscription_id="sub_test123",
            cancel_at_period_end=True
        )

        assert result == mock_subscription
        mock_modify.assert_called_once_with(
            "sub_test123",
            cancel_at_period_end=True
        )
```

#### **Database Model Tests**

```python
# File: tests/unit/test_subscription_models.py

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from personal_assistant.database.models.subscriptions import Subscription, BillingHistory, PaymentMethod
from personal_assistant.database.models.users import User

class TestSubscriptionModels:
    """Test cases for subscription models."""

    @pytest.mark.asyncio
    async def test_subscription_creation(self, db_session: AsyncSession):
        """Test subscription model creation."""
        # Create user
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create subscription
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier="premium",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)

        assert subscription.id is not None
        assert subscription.user_id == user.id
        assert subscription.tier == "premium"
        assert subscription.status == "active"

    @pytest.mark.asyncio
    async def test_billing_history_creation(self, db_session: AsyncSession):
        """Test billing history model creation."""
        # Create user
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create billing history
        billing = BillingHistory(
            user_id=user.id,
            stripe_invoice_id="in_test123",
            amount=900,  # $9.00 in cents
            currency="usd",
            status="paid",
            paid_at=datetime.utcnow()
        )
        db_session.add(billing)
        await db_session.commit()
        await db_session.refresh(billing)

        assert billing.id is not None
        assert billing.user_id == user.id
        assert billing.amount == 900
        assert billing.status == "paid"
```

### **Phase 2: Integration Testing**

#### **API Integration Tests**

```python
# File: tests/integration/test_subscription_api.py

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.main import app
from personal_assistant.database.models.users import User
from personal_assistant.database.models.subscriptions import Subscription

class TestSubscriptionAPI:
    """Integration tests for subscription API endpoints."""

    @pytest.mark.asyncio
    async def test_create_subscription_success(
        self,
        client: AsyncClient,
        authenticated_user: User,
        db_session: AsyncSession
    ):
        """Test successful subscription creation."""
        subscription_data = {
            "tier": "premium",
            "status": "trialing",
            "price_id": "price_test123",
            "trial_period_days": 14
        }

        with patch('personal_assistant.services.stripe_service.StripeService.create_subscription') as mock_create:
            mock_create.return_value = {
                "id": "sub_test123",
                "status": "trialing",
                "current_period_start": 1640995200,
                "current_period_end": 1643673600,
            }

            response = await client.post(
                "/api/v1/subscriptions/",
                json=subscription_data,
                headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["tier"] == "premium"
            assert data["status"] == "trialing"

    @pytest.mark.asyncio
    async def test_get_subscription_success(
        self,
        client: AsyncClient,
        authenticated_user: User,
        db_session: AsyncSession
    ):
        """Test successful subscription retrieval."""
        # Create subscription
        subscription = Subscription(
            user_id=authenticated_user.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier="premium",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        await db_session.commit()

        response = await client.get(
            "/api/v1/subscriptions/me",
            headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "premium"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_update_subscription_success(
        self,
        client: AsyncClient,
        authenticated_user: User,
        db_session: AsyncSession
    ):
        """Test successful subscription update."""
        # Create subscription
        subscription = Subscription(
            user_id=authenticated_user.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier="premium",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        await db_session.commit()

        update_data = {
            "tier": "pro",
            "cancel_at_period_end": False
        }

        with patch('personal_assistant.services.stripe_service.StripeService.update_subscription') as mock_update:
            mock_update.return_value = {
                "id": "sub_test123",
                "status": "active",
                "current_period_start": 1640995200,
                "current_period_end": 1643673600,
            }

            response = await client.put(
                "/api/v1/subscriptions/me",
                json=update_data,
                headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["tier"] == "pro"
```

#### **Webhook Integration Tests**

```python
# File: tests/integration/test_stripe_webhooks.py

import pytest
import json
from unittest.mock import patch
from httpx import AsyncClient

class TestStripeWebhooks:
    """Integration tests for Stripe webhook processing."""

    @pytest.mark.asyncio
    async def test_subscription_created_webhook(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test subscription created webhook processing."""
        # Create user with Stripe customer ID
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            stripe_customer_id="cus_test123"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Mock webhook event
        webhook_event = {
            "id": "evt_test123",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "trialing",
                    "current_period_start": 1640995200,
                    "current_period_end": 1643673600,
                    "items": {
                        "data": [{
                            "price": {"id": "price_premium"}
                        }]
                    }
                }
            }
        }

        # Create webhook signature
        payload = json.dumps(webhook_event).encode()
        signature = "t=1640995200,v1=test_signature"

        with patch('personal_assistant.services.stripe_service.StripeService.construct_webhook_event') as mock_construct:
            mock_construct.return_value = webhook_event

            response = await client.post(
                "/api/v1/webhooks/stripe",
                content=payload,
                headers={"stripe-signature": signature}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_payment_succeeded_webhook(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test payment succeeded webhook processing."""
        # Create user and subscription
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            stripe_customer_id="cus_test123"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier="premium",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)

        # Mock webhook event
        webhook_event = {
            "id": "evt_test123",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "subscription": "sub_test123",
                    "amount_paid": 900,
                    "currency": "usd",
                    "status": "paid",
                    "status_transitions": {
                        "paid_at": 1640995200
                    },
                    "due_date": 1640995200
                }
            }
        }

        payload = json.dumps(webhook_event).encode()
        signature = "t=1640995200,v1=test_signature"

        with patch('personal_assistant.services.stripe_service.StripeService.construct_webhook_event') as mock_construct:
            mock_construct.return_value = webhook_event

            response = await client.post(
                "/api/v1/webhooks/stripe",
                content=payload,
                headers={"stripe-signature": signature}
            )

            assert response.status_code == 200

            # Verify billing history was created
            billing_history = await db_session.execute(
                select(BillingHistory).where(
                    BillingHistory.stripe_invoice_id == "in_test123"
                )
            )
            billing_record = billing_history.scalar_one_or_none()
            assert billing_record is not None
            assert billing_record.amount == 900
            assert billing_record.status == "paid"
```

### **Phase 3: End-to-End Testing**

#### **Complete Subscription Flow Tests**

```python
# File: tests/e2e/test_subscription_flow.py

import pytest
from httpx import AsyncClient
from unittest.mock import patch, Mock

class TestSubscriptionE2E:
    """End-to-end tests for complete subscription flow."""

    @pytest.mark.asyncio
    async def test_complete_subscription_flow(
        self,
        client: AsyncClient,
        authenticated_user: User,
        db_session: AsyncSession
    ):
        """Test complete subscription flow from creation to payment."""

        # Step 1: Create subscription
        subscription_data = {
            "tier": "premium",
            "status": "trialing",
            "price_id": "price_premium",
            "trial_period_days": 14
        }

        with patch('personal_assistant.services.stripe_service.StripeService.create_subscription') as mock_create:
            mock_create.return_value = {
                "id": "sub_test123",
                "status": "trialing",
                "current_period_start": 1640995200,
                "current_period_end": 1643673600,
            }

            response = await client.post(
                "/api/v1/subscriptions/",
                json=subscription_data,
                headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
            )

            assert response.status_code == 200
            subscription_id = response.json()["id"]

        # Step 2: Verify subscription exists
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "premium"
        assert data["status"] == "trialing"

        # Step 3: Simulate payment success webhook
        webhook_event = {
            "id": "evt_test123",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "subscription": "sub_test123",
                    "amount_paid": 900,
                    "currency": "usd",
                    "status": "paid",
                    "status_transitions": {
                        "paid_at": 1640995200
                    }
                }
            }
        }

        with patch('personal_assistant.services.stripe_service.StripeService.construct_webhook_event') as mock_construct:
            mock_construct.return_value = webhook_event

            response = await client.post(
                "/api/v1/webhooks/stripe",
                content=json.dumps(webhook_event).encode(),
                headers={"stripe-signature": "t=1640995200,v1=test_signature"}
            )

            assert response.status_code == 200

        # Step 4: Verify billing history
        response = await client.get(
            "/api/v1/subscriptions/me/history",
            headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
        )

        assert response.status_code == 200
        billing_history = response.json()
        assert len(billing_history) == 1
        assert billing_history[0]["amount"] == 900
        assert billing_history[0]["status"] == "paid"

        # Step 5: Test subscription cancellation
        with patch('personal_assistant.services.stripe_service.StripeService.cancel_subscription') as mock_cancel:
            mock_cancel.return_value = {
                "id": "sub_test123",
                "cancel_at_period_end": True,
                "status": "active"
            }

            response = await client.put(
                "/api/v1/subscriptions/me",
                json={"cancel_at_period_end": True},
                headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["cancel_at_period_end"] == True
```

### **Phase 4: Security Testing**

#### **Security Test Cases**

```python
# File: tests/security/test_subscription_security.py

import pytest
from httpx import AsyncClient

class TestSubscriptionSecurity:
    """Security tests for subscription endpoints."""

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test that subscription endpoints require authentication."""
        response = await client.get("/api/v1/subscriptions/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_webhook_signature_validation(self, client: AsyncClient):
        """Test webhook signature validation."""
        payload = b'{"test": "data"}'

        # Test without signature
        response = await client.post("/api/v1/webhooks/stripe", content=payload)
        assert response.status_code == 400

        # Test with invalid signature
        response = await client.post(
            "/api/v1/webhooks/stripe",
            content=payload,
            headers={"stripe-signature": "invalid_signature"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_user_isolation(self, client: AsyncClient, db_session: AsyncSession):
        """Test that users can only access their own subscriptions."""
        # Create two users
        user1 = User(email="user1@example.com", hashed_password="password1")
        user2 = User(email="user2@example.com", hashed_password="password2")
        db_session.add_all([user1, user2])
        await db_session.commit()

        # Create subscription for user1
        subscription = Subscription(
            user_id=user1.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier="premium",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        await db_session.commit()

        # Try to access user1's subscription as user2
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers={"Authorization": f"Bearer {user2.access_token}"}
        )

        assert response.status_code == 404  # Should not find user2's subscription
```

## 📊 **Performance Testing**

### **Load Testing**

```python
# File: tests/performance/test_subscription_performance.py

import pytest
import asyncio
from httpx import AsyncClient

class TestSubscriptionPerformance:
    """Performance tests for subscription endpoints."""

    @pytest.mark.asyncio
    async def test_concurrent_subscription_creation(self, client: AsyncClient):
        """Test concurrent subscription creation performance."""
        async def create_subscription(user_token):
            subscription_data = {
                "tier": "premium",
                "status": "trialing",
                "price_id": "price_premium",
                "trial_period_days": 14
            }

            with patch('personal_assistant.services.stripe_service.StripeService.create_subscription'):
                response = await client.post(
                    "/api/v1/subscriptions/",
                    json=subscription_data,
                    headers={"Authorization": f"Bearer {user_token}"}
                )
                return response.status_code

        # Create 10 concurrent requests
        tasks = [create_subscription(f"token_{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All requests should succeed
        assert all(status == 200 for status in results)

    @pytest.mark.asyncio
    async def test_webhook_processing_performance(self, client: AsyncClient):
        """Test webhook processing performance."""
        webhook_event = {
            "id": "evt_test123",
            "type": "customer.subscription.created",
            "data": {"object": {"id": "sub_test123"}}
        }

        payload = json.dumps(webhook_event).encode()
        signature = "t=1640995200,v1=test_signature"

        with patch('personal_assistant.services.stripe_service.StripeService.construct_webhook_event'):
            start_time = time.time()

            response = await client.post(
                "/api/v1/webhooks/stripe",
                content=payload,
                headers={"stripe-signature": signature}
            )

            end_time = time.time()
            processing_time = end_time - start_time

            assert response.status_code == 200
            assert processing_time < 1.0  # Should process within 1 second
```

## 🔍 **Test Coverage Requirements**

### **Code Coverage Targets**

- **Unit Tests**: 95%+ coverage for subscription models and services
- **Integration Tests**: 90%+ coverage for API endpoints
- **E2E Tests**: 100% coverage for critical user flows
- **Security Tests**: 100% coverage for security-critical paths

### **Test Data Management**

```python
# File: tests/fixtures/subscription_fixtures.py

import pytest
from datetime import datetime, timedelta
from personal_assistant.database.models.users import User
from personal_assistant.database.models.subscriptions import Subscription, BillingHistory

@pytest.fixture
async def subscription_user(db_session: AsyncSession):
    """Create a user with subscription for testing."""
    user = User(
        email="subscription@example.com",
        full_name="Subscription User",
        hashed_password="hashed_password",
        stripe_customer_id="cus_test123"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    subscription = Subscription(
        user_id=user.id,
        stripe_subscription_id="sub_test123",
        stripe_customer_id="cus_test123",
        tier="premium",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30)
    )
    db_session.add(subscription)
    await db_session.commit()

    return user, subscription

@pytest.fixture
async def billing_history(db_session: AsyncSession, subscription_user):
    """Create billing history for testing."""
    user, subscription = subscription_user

    billing = BillingHistory(
        user_id=user.id,
        subscription_id=subscription.id,
        stripe_invoice_id="in_test123",
        amount=900,
        currency="usd",
        status="paid",
        paid_at=datetime.utcnow()
    )
    db_session.add(billing)
    await db_session.commit()

    return billing
```

## 🚀 **CI/CD Integration**

### **Test Pipeline Configuration**

```yaml
# File: .github/workflows/subscription-tests.yml

name: Subscription Tests

on:
  push:
    paths:
      - "src/personal_assistant/services/stripe_service.py"
      - "src/apps/fastapi_app/routes/subscriptions.py"
      - "tests/unit/test_subscription_*.py"
      - "tests/integration/test_subscription_*.py"

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-mock
      - name: Run unit tests
        run: pytest tests/unit/test_subscription_*.py -v --cov=src/personal_assistant/services/stripe_service.py

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run integration tests
        run: pytest tests/integration/test_subscription_*.py -v
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          STRIPE_SECRET_KEY: sk_test_fake_key
          STRIPE_WEBHOOK_SECRET: whsec_fake_secret

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run security tests
        run: pytest tests/security/test_subscription_security.py -v
```

This comprehensive testing strategy ensures the Stripe subscription implementation is robust, secure, and reliable while maintaining the high standards of the existing Personal Assistant TDAH system.
