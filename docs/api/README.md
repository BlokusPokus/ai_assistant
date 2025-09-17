# 📚 Personal Assistant API Documentation

## 🎯 **Overview**

The Personal Assistant API is a comprehensive REST API built with FastAPI that provides authentication, user management, OAuth integration, SMS routing, analytics, and AI assistant functionality. This API serves as the backend for the Personal Assistant TDAH system.

## 🔗 **Base Information**

- **Base URL**: `http://localhost:8000/api/v1`
- **API Version**: v1
- **Content Type**: `application/json`
- **Authentication**: JWT Bearer tokens
- **Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## 🔐 **Authentication**

The API uses JWT (JSON Web Token) authentication with the following features:

- **Access Tokens**: Short-lived tokens (15 minutes) for API access
- **Refresh Tokens**: Long-lived tokens (7 days) for token renewal
- **Multi-Factor Authentication**: TOTP and SMS-based MFA support
- **Role-Based Access Control**: Granular permissions system

### **Authentication Flow**

1. **Register/Login**: Obtain access and refresh tokens
2. **API Requests**: Include `Authorization: Bearer <access_token>` header
3. **Token Refresh**: Use refresh token to get new access token
4. **MFA**: Additional verification step for sensitive operations

### **Example Authentication Header**

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📊 **Rate Limiting**

- **Default Limit**: 100 requests per minute per user
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information included in response headers
- **Exceeded**: Returns `429 Too Many Requests` with retry-after header

## 📝 **Common Response Formats**

### **Success Response**

```json
{
  "data": { ... },
  "message": "Operation completed successfully",
  "status": "success"
}
```

### **Error Response**

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status": "error",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Paginated Response**

```json
{
  "data": [ ... ],
  "total": 100,
  "skip": 0,
  "limit": 20,
  "has_next": true,
  "has_prev": false
}
```

## 🚨 **Error Codes**

| Code  | Status                | Description                        |
| ----- | --------------------- | ---------------------------------- |
| `400` | Bad Request           | Invalid request data or parameters |
| `401` | Unauthorized          | Authentication required or invalid |
| `403` | Forbidden             | Insufficient permissions           |
| `404` | Not Found             | Resource not found                 |
| `409` | Conflict              | Resource already exists            |
| `422` | Unprocessable Entity  | Validation error                   |
| `429` | Too Many Requests     | Rate limit exceeded                |
| `500` | Internal Server Error | Server error                       |

## 🔧 **API Endpoints Overview**

### **Authentication Endpoints** (`/api/v1/auth`)

- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /refresh` - Token refresh
- `POST /forgot-password` - Password reset request
- `POST /reset-password` - Password reset confirmation
- `GET /me` - Current user information

### **User Management Endpoints** (`/api/v1/users`)

- `GET /me` - Current user profile
- `PUT /me` - Update current user profile
- `GET /me/preferences` - User preferences
- `PUT /me/preferences` - Update user preferences
- `GET /me/settings` - User settings
- `PUT /me/settings` - Update user settings
- `GET /me/phone-numbers` - User phone numbers
- `POST /me/phone-numbers` - Add phone number
- `PUT /me/phone-numbers/{id}` - Update phone number
- `DELETE /me/phone-numbers/{id}` - Delete phone number

### **MFA Endpoints** (`/api/v1/mfa`)

- `POST /setup/totp` - Setup TOTP MFA
- `POST /verify/totp` - Verify TOTP token
- `POST /setup/sms` - Setup SMS MFA
- `POST /verify/sms` - Verify SMS code
- `POST /verify/backup` - Verify backup code
- `GET /status` - MFA status
- `POST /disable` - Disable MFA
- `POST /regenerate-backup-codes` - Regenerate backup codes

### **OAuth Integration Endpoints** (`/api/v1/oauth`)

- `GET /providers` - Available OAuth providers
- `POST /initiate` - OAuth flow initiation
- `GET /callback` - OAuth callback handling
- `GET /integrations` - Integration management
- `POST /integrations/{id}/refresh` - Token refresh
- `DELETE /integrations/{id}` - Revoke integration
- `GET /status` - Integration status summary

### **SMS Router Endpoints** (`/api/v1/sms-router`)

- `POST /webhook/sms` - Twilio SMS webhook
- `GET /webhook/health` - Health check
- `GET /config` - SMS routing configuration
- `PUT /config` - Update SMS routing configuration

### **Analytics Endpoints** (`/api/v1/analytics`)

- `GET /sms` - SMS usage analytics
- `GET /costs` - Cost tracking and analysis
- `GET /performance` - Performance metrics
- `GET /admin` - Admin analytics dashboard
- `GET /reports` - Usage reports
- `POST /export` - Export analytics data

### **RBAC Endpoints** (`/api/v1/rbac`)

- `GET /roles` - List roles
- `POST /roles` - Create role
- `PUT /roles/{id}` - Update role
- `DELETE /roles/{id}` - Delete role
- `GET /permissions` - List permissions
- `POST /permissions` - Create permission
- `PUT /permissions/{id}` - Update permission
- `DELETE /permissions/{id}` - Delete permission
- `GET /users/{id}/roles` - Get user roles
- `POST /users/{id}/roles` - Assign role to user
- `DELETE /users/{id}/roles/{role_id}` - Remove role from user
- `GET /audit` - Access audit logs

### **Session Management Endpoints** (`/api/v1/sessions`)

- `GET /` - List user sessions
- `DELETE /{id}` - Terminate session
- `DELETE /all` - Terminate all sessions
- `GET /stats` - Session statistics

### **Chat Endpoints** (`/api/v1/chat`)

- `POST /messages` - Send message to agent
- `GET /conversations` - Get conversation history

## 🛡️ **Security Features**

- **JWT Authentication**: Secure token-based authentication
- **Multi-Factor Authentication**: TOTP and SMS support
- **Role-Based Access Control**: Granular permission system
- **Rate Limiting**: Protection against abuse
- **CORS**: Cross-origin resource sharing configuration
- **Security Headers**: Comprehensive security headers
- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## 📋 **Request/Response Examples**

### **User Registration**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "phone_number": "+1234567890"
}
```

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### **User Login**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "mfa_required": false,
  "mfa_setup_required": false
}
```

### **Get Current User Profile**

```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "phone_number": "+1234567890",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "last_login": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## 🔄 **Webhooks**

### **SMS Webhook**

The SMS router accepts webhooks from Twilio for incoming SMS messages:

```http
POST /api/v1/sms-router/webhook/sms
Content-Type: application/x-www-form-urlencoded

From=%2B1234567890&Body=Hello%20world&MessageSid=SM1234567890
```

## 📚 **Additional Resources**

- **Swagger UI**: `/docs` - Interactive API documentation
- **ReDoc**: `/redoc` - Alternative API documentation
- **OpenAPI Schema**: `/openapi.json` - Machine-readable API schema
- **Health Check**: `/health` - Service health status
- **Metrics**: `/metrics` - Prometheus metrics endpoint

## 🚀 **Getting Started**

1. **Register**: Create a new user account
2. **Login**: Authenticate and get tokens
3. **Setup MFA**: Configure multi-factor authentication (optional)
4. **Make Requests**: Use the access token for API calls
5. **Refresh Tokens**: Use refresh token when access token expires

## 📞 **Support**

For API support and questions:

- **Documentation**: Check individual endpoint documentation
- **Issues**: Report issues through the project repository
- **Health Check**: Use `/health` endpoint to verify service status

---

**This API provides comprehensive functionality for the Personal Assistant TDAH system, enabling secure user management, OAuth integration, SMS routing, and AI assistant capabilities.**
