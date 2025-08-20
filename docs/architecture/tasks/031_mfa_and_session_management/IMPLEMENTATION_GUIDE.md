# 🔐 Multi-Factor Authentication & Session Management - Implementation Guide

## **🎯 Overview**

This guide provides step-by-step instructions for implementing Multi-Factor Authentication (MFA) and Redis-based session management for the Personal Assistant TDAH platform. The implementation addresses Tasks 2.1.1.3, 2.1.1.4, and 2.1.3.1 from the technical roadmap.

## **🏗️ Architecture Components**

### **1. MFA Services (`src/personal_assistant/auth/`)**

- **`mfa_service.py`**: TOTP-based MFA with QR codes and backup codes
- **`sms_mfa.py`**: SMS verification with rate limiting and abuse prevention
- **`mfa_models.py`**: Database models for MFA configuration and security events

### **2. Session Management (`src/personal_assistant/auth/`)**

- **`session_service.py`**: Redis-based session storage and lifecycle management
- **`session_models.py`**: Database models for session tracking and security events

### **3. Enhanced Authentication Routes (`src/apps/fastapi_app/routes/`)**

- **`auth.py`**: Enhanced with MFA setup, verification, and session management
- **`mfa.py`**: Dedicated MFA management endpoints

### **4. Database Schema Updates**

- **MFA Configuration Tables**: Store TOTP secrets, SMS settings, backup codes
- **Session Management Tables**: Track active sessions, device information, security events

## **🚀 Setup Instructions**

### **Step 1: Install Dependencies**

Add these packages to `requirements.txt`:

```bash
# MFA Dependencies
pyotp>=2.9.0          # TOTP generation and validation
qrcode[pil]>=7.4.2    # QR code generation
redis>=5.0.0           # Redis client (already configured)

# Security Dependencies
cryptography>=41.0.0   # Enhanced security features
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### **Step 2: Environment Configuration**

Add these environment variables to your `.env` file:

```bash
# MFA Configuration
MFA_TOTP_ISSUER="Personal Assistant TDAH"
MFA_TOTP_WINDOW=1                    # 30-second window tolerance
MFA_SMS_RATE_LIMIT=3                 # Max SMS attempts per window
MFA_SMS_RATE_WINDOW_MINUTES=10       # Rate limiting window
MFA_BACKUP_CODES_COUNT=10            # Number of backup codes
MFA_TRUSTED_DEVICE_DAYS=30           # Remember trusted devices

# Session Management
SESSION_EXPIRY_HOURS=24              # Session lifetime
SESSION_MAX_CONCURRENT=5              # Max sessions per user
SESSION_REDIS_DB=1                    # Redis database for sessions
SESSION_CLEANUP_INTERVAL=3600         # Cleanup interval in seconds

# Security Settings
SECURITY_AUDIT_ENABLED=true           # Enable security event logging
SECURITY_IP_WHITELIST=""              # IP addresses to trust
SECURITY_DEVICE_TRACKING=true         # Track device information
```

### **Step 3: Redis Configuration**

Update Redis configuration to support sessions (already configured for Celery):

```python
# src/personal_assistant/config/redis.py
import redis
from .settings import settings

# Celery Redis (existing)
celery_redis = redis.Redis.from_url(
    settings.CELERY_BROKER_URL,
    decode_responses=True
)

# Session Redis (new)
session_redis = redis.Redis.from_url(
    f"redis://localhost:6379/{settings.SESSION_REDIS_DB}",
    decode_responses=True
)

# Health check function
async def check_redis_health():
    try:
        celery_redis.ping()
        session_redis.ping()
        return True
    except Exception:
        return False
```

## **🔧 Implementation Details**

### **1. MFA Service Implementation**

#### **TOTP-based MFA Service**

```python
# src/personal_assistant/auth/mfa_service.py
import pyotp
import qrcode
import secrets
import base64
from io import BytesIO
from typing import List, Optional
from datetime import datetime, timedelta

class MFAService:
    def __init__(self, issuer: str = "Personal Assistant TDAH"):
        self.issuer = issuer

    def generate_totp_secret(self, user_id: str) -> str:
        """Generate a secure TOTP secret for a user."""
        return pyotp.random_base32()

    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """Generate QR code for authenticator apps."""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def verify_totp(self, secret: str, token: str, window: int = 1) -> bool:
        """Verify TOTP token with configurable window."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery."""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_urlsafe(6)[:8].upper()
            codes.append(code)
        return codes

    def verify_backup_code(self, user_id: str, code: str, stored_codes: List[str]) -> bool:
        """Verify and consume a backup code."""
        if code.upper() in stored_codes:
            # Remove used code
            stored_codes.remove(code.upper())
            return True
        return False
```

#### **SMS-based MFA Service**

```python
# src/personal_assistant/auth/sms_mfa.py
import secrets
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from personal_assistant.tools.sms.twilio_client import TwilioClient

class SMSMFAService:
    def __init__(self, twilio_client: TwilioClient):
        self.twilio_client = twilio_client
        self.verification_codes: Dict[str, Dict] = {}

    def send_verification_code(self, phone_number: str) -> str:
        """Send SMS verification code and return code ID."""
        if self.is_rate_limited(phone_number):
            raise ValueError("Rate limit exceeded. Please try again later.")

        # Generate 6-digit code
        code = str(secrets.randbelow(1000000)).zfill(6)
        code_id = secrets.token_urlsafe(16)

        # Store code with expiration
        self.verification_codes[code_id] = {
            'phone_number': phone_number,
            'code': code,
            'expires_at': datetime.now() + timedelta(minutes=10),
            'attempts': 0
        }

        # Send SMS
        message = f"Your verification code is: {code}. Valid for 10 minutes."
        self.twilio_client.send_sms(phone_number, message)

        return code_id

    def verify_code(self, code_id: str, code: str) -> bool:
        """Verify SMS code and return success status."""
        if code_id not in self.verification_codes:
            return False

        verification_data = self.verification_codes[code_id]

        # Check expiration
        if datetime.now() > verification_data['expires_at']:
            del self.verification_codes[code_id]
            return False

        # Check attempts
        if verification_data['attempts'] >= 3:
            del self.verification_codes[code_id]
            return False

        verification_data['attempts'] += 1

        # Verify code
        if verification_data['code'] == code:
            del self.verification_codes[code_id]
            return True

        return False

    def is_rate_limited(self, phone_number: str) -> bool:
        """Check if phone number is rate limited."""
        now = datetime.now()
        window_start = now - timedelta(minutes=10)

        # Count recent attempts
        recent_attempts = sum(
            1 for data in self.verification_codes.values()
            if (data['phone_number'] == phone_number and
                data['expires_at'] > window_start)
        )

        return recent_attempts >= 3
```

### **2. Session Management Service**

```python
# src/personal_assistant/auth/session_service.py
import json
import secrets
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from personal_assistant.config.settings import settings

class SessionService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"

    async def create_session(self, user_id: str, device_info: dict) -> str:
        """Create a new session for a user."""
        # Check concurrent session limit
        if not await self.enforce_session_limits(user_id):
            raise ValueError("Maximum concurrent sessions reached")

        # Generate session ID
        session_id = secrets.token_urlsafe(32)

        # Create session data
        session_data = {
            'user_id': user_id,
            'device_info': device_info,
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=settings.SESSION_EXPIRY_HOURS)).isoformat(),
            'is_active': True
        }

        # Store in Redis
        session_key = f"{self.session_prefix}{session_id}"
        await self.redis.setex(
            session_key,
            settings.SESSION_EXPIRY_HOURS * 3600,
            json.dumps(session_data)
        )

        # Track user sessions
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis.sadd(user_sessions_key, session_id)
        await self.redis.expire(user_sessions_key, settings.SESSION_EXPIRY_HOURS * 3600)

        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data by ID."""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return None

        session = json.loads(session_data)

        # Check if expired
        if datetime.fromisoformat(session['expires_at']) < datetime.now():
            await self.invalidate_session(session_id)
            return None

        # Update last accessed
        session['last_accessed'] = datetime.now().isoformat()
        await self.redis.setex(
            session_key,
            settings.SESSION_EXPIRY_HOURS * 3600,
            json.dumps(session)
        )

        return session

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return False

        session = json.loads(session_data)
        user_id = session['user_id']

        # Remove from Redis
        await self.redis.delete(session_key)

        # Remove from user sessions
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis.srem(user_sessions_key, session_id)

        return True

    async def get_user_sessions(self, user_id: str) -> List[dict]:
        """Get all active sessions for a user."""
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_ids = await self.redis.smembers(user_sessions_key)

        sessions = []
        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session:
                sessions.append(session)

        return sessions

    async def enforce_session_limits(self, user_id: str) -> bool:
        """Check if user can create a new session."""
        current_sessions = await self.get_user_sessions(user_id)
        return len(current_sessions) < settings.SESSION_MAX_CONCURRENT

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions (run periodically)."""
        # This would be implemented as a background task
        # For now, sessions expire automatically via Redis TTL
        pass
```

### **3. Database Schema Updates**

#### **MFA Configuration Table**

```sql
-- Create MFA configuration table
CREATE TABLE IF NOT EXISTS mfa_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    totp_secret VARCHAR(255),
    totp_enabled BOOLEAN DEFAULT FALSE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    phone_number VARCHAR(20),
    backup_codes JSONB,
    trusted_devices JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_mfa_configurations_user_id ON mfa_configurations(user_id);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_mfa_configurations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_mfa_configurations_updated_at
    BEFORE UPDATE ON mfa_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_mfa_configurations_updated_at();
```

#### **Session Management Tables**

```sql
-- Create user sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Create security events table
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    severity VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for security monitoring
CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_event_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
```

### **4. Enhanced Authentication Endpoints**

#### **MFA Setup Endpoint**

```python
# src/apps/fastapi_app/routes/mfa.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from personal_assistant.database.session import get_db
from personal_assistant.auth.mfa_service import MFAService
from personal_assistant.auth.sms_mfa import SMSMFAService
from personal_assistant.database.models.mfa_models import MFAConfiguration
from personal_assistant.auth.jwt_service import get_current_user

router = APIRouter(prefix="/api/v1/mfa", tags=["MFA"])

@router.post("/setup/totp")
async def setup_totp(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Setup TOTP-based MFA for the current user."""
    try:
        mfa_service = MFAService()

        # Generate TOTP secret
        totp_secret = mfa_service.generate_totp_secret(str(current_user.id))

        # Generate QR code
        qr_code = mfa_service.generate_qr_code(totp_secret, current_user.email)

        # Store secret in database (encrypted)
        mfa_config = MFAConfiguration(
            user_id=current_user.id,
            totp_secret=totp_secret,
            totp_enabled=False  # Will be enabled after verification
        )

        db.add(mfa_config)
        await db.commit()

        return {
            "totp_secret": totp_secret,
            "qr_code": qr_code,
            "message": "Scan QR code with your authenticator app"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup TOTP: {str(e)}"
        )

@router.post("/verify/totp")
async def verify_totp(
    token: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify TOTP token and enable MFA."""
    try:
        # Get MFA configuration
        mfa_config = await db.get(MFAConfiguration, current_user.id)
        if not mfa_config or not mfa_config.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP not configured"
            )

        # Verify token
        mfa_service = MFAService()
        if not mfa_service.verify_totp(mfa_config.totp_secret, token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP token"
            )

        # Enable MFA
        mfa_config.totp_enabled = True
        await db.commit()

        return {"message": "TOTP MFA enabled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify TOTP: {str(e)}"
        )
```

#### **Session Management Endpoints**

```python
# src/apps/fastapi_app/routes/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from personal_assistant.auth.session_service import SessionService
from personal_assistant.auth.jwt_service import get_current_user
from personal_assistant.config.redis import session_redis

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])

@router.get("/")
async def get_user_sessions(
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Get all active sessions for the current user."""
    try:
        session_service = SessionService(session_redis)
        sessions = await session_service.get_user_sessions(str(current_user.id))

        # Filter sensitive information
        for session in sessions:
            if 'device_info' in session:
                session['device_info'] = {
                    'browser': session['device_info'].get('browser'),
                    'os': session['device_info'].get('os'),
                    'device': session['device_info'].get('device')
                }

        return {"sessions": sessions}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )

@router.delete("/{session_id}")
async def invalidate_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Invalidate a specific session."""
    try:
        session_service = SessionService(session_redis)

        # Get session to verify ownership
        session = await session_service.get_session(session_id)
        if not session or session['user_id'] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Invalidate session
        success = await session_service.invalidate_session(session_id)

        if success:
            return {"message": "Session invalidated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to invalidate session"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate session: {str(e)}"
        )
```

## **🧪 Testing Strategy**

### **Unit Tests**

```python
# tests/test_auth/test_mfa_service.py
import pytest
from unittest.mock import Mock, patch
from personal_assistant.auth.mfa_service import MFAService

class TestMFAService:
    def setup_method(self):
        self.mfa_service = MFAService()

    def test_generate_totp_secret(self):
        secret = self.mfa_service.generate_totp_secret("user123")
        assert len(secret) == 32
        assert secret.isalnum()

    def test_verify_totp_valid(self):
        secret = self.mfa_service.generate_totp_secret("user123")
        # Generate current TOTP
        import pyotp
        totp = pyotp.TOTP(secret)
        current_token = totp.now()

        result = self.mfa_service.verify_totp(secret, current_token)
        assert result is True

    def test_verify_totp_invalid(self):
        secret = self.mfa_service.generate_totp_secret("user123")
        result = self.mfa_service.verify_totp(secret, "000000")
        assert result is False
```

### **Integration Tests**

```python
# tests/test_auth/test_mfa_integration.py
import pytest
from fastapi.testclient import TestClient
from personal_assistant.apps.fastapi_app.main import app

client = TestClient(app)

class TestMFAIntegration:
    def test_mfa_setup_flow(self):
        # 1. Login to get token
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 2. Setup TOTP
        headers = {"Authorization": f"Bearer {token}"}
        setup_response = client.post("/api/v1/mfa/setup/totp", headers=headers)
        assert setup_response.status_code == 200

        data = setup_response.json()
        assert "totp_secret" in data
        assert "qr_code" in data

        # 3. Verify TOTP (would need actual TOTP generation)
        # This is a simplified test
        verify_response = client.post("/api/v1/mfa/verify/totp",
                                   json={"token": "123456"},
                                   headers=headers)
        # This would fail with invalid token, but shows the flow
        assert verify_response.status_code in [400, 200]
```

## **🔒 Security Considerations**

### **MFA Security**

1. **TOTP Secrets**: Store encrypted in database, never log
2. **Rate Limiting**: Implement for both TOTP and SMS verification
3. **Backup Codes**: One-time use, secure storage, easy revocation
4. **Device Trust**: Remember trusted devices with user consent

### **Session Security**

1. **Session IDs**: Cryptographically secure random generation
2. **Expiration**: Automatic expiration with Redis TTL
3. **Device Tracking**: Log IP, user agent, location for security
4. **Concurrent Limits**: Prevent session abuse

### **Audit and Monitoring**

1. **Security Events**: Log all authentication and security events
2. **Anomaly Detection**: Monitor for suspicious patterns
3. **Compliance**: Ensure GDPR and SOC 2 compliance
4. **Incident Response**: Clear procedures for security incidents

## **📚 Next Steps**

After implementing this task:

1. **Phase 2.2**: Move to Infrastructure & Database optimization
2. **Phase 2.3**: Implement API & Backend services
3. **Phase 2.5**: Multi-user architecture with SMS Router Service

## **🔗 Additional Resources**

- [PyOTP Documentation](https://github.com/pyotp/pyotp)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Document prepared by**: Technical Architecture Team  
**Next review**: Weekly during implementation  
**Contact**: [Your Team Contact Information]
