# 🔐 Core Authentication Service - Implementation Guide

## **🎯 Overview**

This guide explains how to use the newly implemented Core Authentication Service for the Personal Assistant TDAH platform. The system provides JWT-based authentication with secure password management, rate limiting, and user isolation.

## **🏗️ Architecture Components**

### **1. Authentication Module (`src/personal_assistant/auth/`)**

- **`jwt_service.py`**: JWT token generation, validation, and refresh
- **`password_service.py`**: Secure password hashing and validation using bcrypt
- **`auth_utils.py`**: Utility functions for token extraction and user context management

### **2. Middleware (`src/apps/fastapi_app/middleware/`)**

- **`auth.py`**: JWT authentication middleware with user context injection
- **`rate_limiting.py`**: Rate limiting for authentication endpoints to prevent abuse

### **3. Authentication Routes (`src/apps/fastapi_app/routes/auth.py`)**

- **`POST /api/v1/auth/register`**: User registration
- **`POST /api/v1/auth/login`**: User authentication
- **`POST /api/v1/auth/refresh`**: Token refresh
- **`POST /api/v1/auth/logout`**: User logout
- **`GET /api/v1/auth/me`**: Get current user info

### **4. Enhanced Database Models**

- **`User`**: Extended with password, verification, and security fields
- **`AuthToken`**: Enhanced with token type, revocation, and usage tracking

## **🚀 Setup Instructions**

### **Step 1: Install Dependencies**

The required packages have been added to `requirements.txt`:

```bash
pip install -r requirements.txt
```

**New dependencies added:**

- `PyJWT>=2.8.0` - JWT token handling
- `bcrypt>=4.1.2` - Password hashing
- `passlib>=1.7.4` - Password utilities

### **Step 2: Environment Configuration**

Add these environment variables to your `.env` file:

```bash
# Authentication settings
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_SALT_ROUNDS=12

# Rate limiting settings
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW_MINUTES=15
RATE_LIMIT_TOKEN_REFRESH_PER_HOUR=10
RATE_LIMIT_REGISTRATION_PER_HOUR=3
```

**⚠️ Security Note**: In production, use a strong, randomly generated JWT secret key.

### **Step 3: Database Schema Update**

Run the database update script to add authentication fields:

```bash
cd scripts
python update_database_auth.py
```

This script will:

- Add authentication fields to existing `users` table
- Enhance `auth_tokens` table with additional fields
- Set appropriate default values
- Add necessary constraints

### **Step 4: Verify Installation**

Run the basic tests to ensure everything works:

```bash
cd tests
python test_auth_basic.py
```

## **🔧 Usage Examples**

### **1. User Registration**

```python
import requests

# Register a new user
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
})

if response.status_code == 201:
    user = response.json()
    print(f"User created: {user['email']}")
```

### **2. User Login**

```python
# Login to get tokens
response = requests.post("http://localhost:8000/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "SecurePass123!"
})

if response.status_code == 200:
    tokens = response.json()
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    # Store tokens for future requests
    headers = {"Authorization": f"Bearer {access_token}"}
```

### **3. Protected Endpoint Access**

```python
# Access protected endpoint
response = requests.get(
    "http://localhost:8000/api/v1/auth/me",
    headers=headers
)

if response.status_code == 200:
    user_info = response.json()
    print(f"Authenticated as: {user_info['full_name']}")
```

### **4. Token Refresh**

```python
# Refresh access token
response = requests.post("http://localhost:8000/api/v1/auth/refresh", json={
    "refresh_token": refresh_token
})

if response.status_code == 200:
    new_tokens = response.json()
    access_token = new_tokens['access_token']
```

### **5. User Logout**

```python
# Logout user
response = requests.post(
    "http://localhost:8000/api/v1/auth/logout",
    headers=headers
)

if response.status_code == 200:
    print("Successfully logged out")
```

## **🛡️ Security Features**

### **Password Security**

- **Minimum Requirements**: 8+ characters, uppercase, lowercase, digit, special character
- **Hashing**: bcrypt with 12 salt rounds (configurable)
- **Strength Scoring**: 0-100 scale with descriptive feedback

### **Token Security**

- **Access Tokens**: 15-minute expiration (configurable)
- **Refresh Tokens**: 7-day expiration (configurable)
- **Automatic Rotation**: Refresh tokens rotate on each use
- **Secure Storage**: HTTP-only cookies with strict settings

### **Rate Limiting**

- **Login Attempts**: Max 5 per 15 minutes per IP
- **Token Refresh**: Max 10 per hour per user
- **Registration**: Max 3 per hour per IP
- **Account Lockout**: 30-minute lockout after 5 failed attempts

### **Account Protection**

- **Account Status**: Active/inactive account management
- **Verification**: Email verification system (framework ready)
- **Password Reset**: Secure token-based password reset
- **Session Management**: Comprehensive token tracking

## **🔗 Integration with Existing System**

### **Twilio Webhook Compatibility**

The authentication middleware excludes the Twilio webhook endpoint (`/webhook/twilio`) to maintain compatibility with existing SMS functionality.

### **User Data Isolation**

All existing endpoints will automatically receive user context through the authentication middleware:

```python
# In your existing endpoints, access user context:
@app.get("/api/v1/events")
async def get_events(request: Request):
    user_id = request.state.user_id
    # Filter events by user_id for data isolation
    events = await get_user_events(user_id)
    return events
```

### **Database Session Integration**

The authentication system integrates with your existing database session management:

```python
from src.personal_assistant.database.session import AsyncSessionLocal

async def get_user_events(user_id: int):
    async with AsyncSessionLocal() as session:
        # Your existing database queries here
        pass
```

## **🧪 Testing**

### **Unit Tests**

```bash
# Run basic authentication tests
python tests/test_auth_basic.py

# Expected output:
# 🚀 Personal Assistant - Authentication System Tests
# ============================================================
# 🧪 Testing Password Service...
#   ✅ Rejected weak password
#   ✅ Hashed strong password: $2b$12$...
#   ✅ Password verification works
#   ✅ Wrong password correctly rejected
#   ✅ Password strength: 85/100 (Strong)
#
# 🧪 Testing JWT Service...
#   ✅ Created access token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
#   ✅ Created refresh token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
#   ✅ Token verification works
#   ✅ Token refresh works
#   ✅ Rejected expired token
#
# 🧪 Testing Auth Utils...
#   ✅ User context creation works
#   ✅ User context validation works for same user
#   ✅ User context validation correctly rejected different user
#
# 🧪 Testing Service Integration...
#   ✅ Complete authentication flow works
#
# 📊 Test Results: 4/4 tests passed
# 🎉 All tests passed! Authentication system is working correctly.
```

### **Integration Testing**

Test the complete authentication flow:

```bash
# Start the server
python src/apps/fastapi_app/main.py

# In another terminal, test the endpoints
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","full_name":"Test User"}'

curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
```

## **📊 Monitoring and Observability**

### **Request Headers**

The authentication middleware injects user context into request headers:

- `X-User-Id`: Current user ID
- `X-User-Email`: Current user email
- `X-User-Full-Name`: Current user full name
- `X-Authenticated`: Authentication status

### **Logging**

Authentication events are logged with appropriate detail levels:

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"User {user_id} logged in successfully")
logger.warning(f"Failed login attempt for email: {email}")
logger.error(f"Account locked for user: {user_id}")
```

## **⚠️ Common Issues and Solutions**

### **1. JWT_SECRET_KEY Not Set**

**Error**: `JWT_SECRET_KEY must be set in production environment`

**Solution**: Set the environment variable:

```bash
export JWT_SECRET_KEY="your-secret-key"
```

### **2. Database Connection Issues**

**Error**: Database connection failures during authentication

**Solution**: Verify database connection and run the update script:

```bash
python scripts/update_database_auth.py
```

### **3. Password Validation Failures**

**Error**: Password doesn't meet requirements

**Solution**: Ensure passwords meet all criteria:

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### **4. Token Expiration Issues**

**Error**: Tokens expiring too quickly

**Solution**: Adjust expiration times in environment:

```bash
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Increase from 15
REFRESH_TOKEN_EXPIRE_DAYS=14    # Increase from 7
```

## **🚀 Next Steps**

### **Immediate Actions**

1. ✅ **Set JWT_SECRET_KEY** in your environment
2. ✅ **Run database update script** to add authentication fields
3. ✅ **Test basic functionality** with the test script
4. ✅ **Verify Twilio webhook** still works

### **Future Enhancements**

1. **Email Verification**: Implement email verification system
2. **Password Reset**: Add password reset functionality
3. **MFA Support**: Add multi-factor authentication
4. **RBAC Integration**: Implement role-based access control
5. **Audit Logging**: Add comprehensive authentication audit trails

## **📚 Additional Resources**

- **FastAPI Security**: [https://fastapi.tiangolo.com/tutorial/security/](https://fastapi.tiangolo.com/tutorial/security/)
- **JWT Best Practices**: [https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- **OWASP Authentication**: [https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Implementation Status**: ✅ Complete  
**Last Updated**: December 2024  
**Next Review**: Before production deployment
