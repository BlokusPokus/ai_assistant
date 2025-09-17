# 🔐 Authentication API Documentation

## 🎯 **Overview**

The Authentication API provides endpoints for user registration, login, logout, token management, and password reset functionality. All endpoints use JWT (JSON Web Token) authentication with access and refresh tokens.

## 📍 **Base Path**

All authentication endpoints are prefixed with `/api/v1/auth`

## 🔑 **Endpoints**

### **POST /register**

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "phone_number": "+1234567890"
}
```

**Request Schema:**

- `email` (string, required): Valid email address
- `password` (string, required): Password (min 8 chars, must contain uppercase, lowercase, number, special char)
- `full_name` (string, required): User's full name
- `phone_number` (string, required): Phone number (10-15 digits, can start with +)

**Response (201 Created):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Email already registered, invalid data
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Registration failed

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe",
    "phone_number": "+1234567890"
  }'
```

---

### **POST /login**

Authenticate user and return JWT tokens.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Request Schema:**

- `email` (string, required): User's email address
- `password` (string, required): User's password

**Response (200 OK):**

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

**Response Schema:**

- `access_token` (string): JWT access token (15 minutes)
- `refresh_token` (string): JWT refresh token (7 days)
- `token_type` (string): Always "bearer"
- `expires_in` (integer): Access token expiry in seconds
- `user` (object): User information
- `mfa_required` (boolean): Whether MFA is required
- `mfa_setup_required` (boolean): Whether MFA setup is required

**Error Responses:**

- `401 Unauthorized`: Invalid email or password, account locked
- `400 Bad Request`: Account deactivated
- `500 Internal Server Error`: Login failed

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

---

### **POST /logout**

Logout user and invalidate tokens.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "message": "Successfully logged out"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Logout failed

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /refresh**

Refresh access token using refresh token.

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Request Schema:**

- `refresh_token` (string, required): Valid refresh token

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid refresh token
- `500 Internal Server Error`: Token refresh failed

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

### **POST /forgot-password**

Request a password reset for a user.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Request Schema:**

- `email` (string, required): User's email address

**Response (200 OK):**

```json
{
  "message": "If the email exists, a password reset link has been sent",
  "reset_token": "abc123def456...",
  "expires_at": "2024-01-02T00:00:00Z"
}
```

**Note:** In production, the reset token should be sent via email, not returned in the response.

**Error Responses:**

- `500 Internal Server Error`: Failed to process password reset request

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

---

### **POST /reset-password**

Reset password using reset token.

**Request Body:**

```json
{
  "token": "abc123def456...",
  "new_password": "NewSecurePassword123!"
}
```

**Request Schema:**

- `token` (string, required): Password reset token
- `new_password` (string, required): New password (same validation as registration)

**Response (200 OK):**

```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid or expired reset token
- `422 Unprocessable Entity`: Password validation errors
- `500 Internal Server Error`: Failed to reset password

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456...",
    "new_password": "NewSecurePassword123!"
  }'
```

---

### **GET /me**

Get current user information.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to retrieve user information

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /verify-email**

Verify user email using verification token.

**Request Body:**

```json
{
  "token": "abc123def456..."
}
```

**Request Schema:**

- `token` (string, required): Email verification token

**Response (200 OK):**

```json
{
  "message": "Email verified successfully"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid verification token
- `500 Internal Server Error`: Failed to verify email

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456..."
  }'
```

---

### **POST /resend-verification**

Resend email verification token.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Request Schema:**

- `email` (string, required): User's email address

**Response (200 OK):**

```json
{
  "message": "If the email exists, a verification link has been sent",
  "verification_token": "abc123def456..."
}
```

**Note:** In production, the verification token should be sent via email, not returned in the response.

**Error Responses:**

- `500 Internal Server Error`: Failed to resend verification

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/resend-verification" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

## 🔒 **Security Features**

### **Password Requirements**

- Minimum 8 characters
- Must contain uppercase letter
- Must contain lowercase letter
- Must contain number
- Must contain special character

### **Account Lockout**

- Account locked after 5 failed login attempts
- Lockout duration: 30 minutes
- Failed attempts reset on successful login

### **Token Security**

- Access tokens: 15 minutes expiry
- Refresh tokens: 7 days expiry
- Tokens stored securely in database
- Tokens invalidated on logout

### **Rate Limiting**

- 100 requests per minute per user
- Additional protection against brute force attacks

## 🔄 **Authentication Flow**

1. **Registration**: User creates account with email/password
2. **Login**: User authenticates and receives tokens
3. **API Access**: Include access token in Authorization header
4. **Token Refresh**: Use refresh token to get new access token
5. **Logout**: Invalidate all tokens

## 📝 **Error Handling**

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status": "error",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🧪 **Testing**

Use the provided examples with curl or any HTTP client. The API also provides interactive documentation at `/docs` (Swagger UI) for testing endpoints directly in the browser.

---

**This authentication API provides secure user management with JWT tokens, password reset functionality, and comprehensive security features.**
