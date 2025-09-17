# 👤 User Management API Documentation

## 🎯 **Overview**

The User Management API provides comprehensive endpoints for user profile management, preferences, settings, phone number management, and administrative user operations. All endpoints require authentication and appropriate permissions.

## 📍 **Base Path**

All user management endpoints are prefixed with `/api/v1/users`

## 🔑 **Endpoints**

### **Current User Endpoints**

These endpoints allow users to manage their own profile and data.

---

### **GET /me**

Get current user profile information.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

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

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to retrieve user profile

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **GET /me/roles**

Get current user profile with role and permission information.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

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
  "updated_at": "2024-01-01T12:00:00Z",
  "roles": [
    {
      "id": 1,
      "name": "user",
      "description": "Standard user role",
      "parent_role_id": null,
      "permissions": [
        {
          "id": 1,
          "name": "user:read",
          "resource_type": "user",
          "action": "read",
          "description": "Read user data",
          "created_at": "2024-01-01T00:00:00Z"
        }
      ],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "permissions": [
    {
      "id": 1,
      "name": "user:read",
      "resource_type": "user",
      "action": "read",
      "description": "Read user data",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "primary_role": {
    "id": 1,
    "name": "user",
    "description": "Standard user role",
    "parent_role_id": null,
    "permissions": [...],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to retrieve user profile with roles

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/roles" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **PUT /me**

Update current user profile.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "full_name": "John Smith",
  "phone_number": "+1987654321"
}
```

**Request Schema:**

- `full_name` (string, optional): User's full name
- `phone_number` (string, optional): Phone number (10-15 digits, can start with +)

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "phone_number": "+1987654321",
  "full_name": "John Smith",
  "is_active": true,
  "is_verified": true,
  "last_login": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: No valid data provided for update
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to update user profile

**Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "phone_number": "+1987654321"
  }'
```

---

### **GET /me/preferences**

Get current user preferences and settings.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "user_id": 1,
  "preferences": {
    "theme": "light",
    "language": "en",
    "notifications": true,
    "timezone": "UTC"
  },
  "settings": {
    "privacy_level": "standard",
    "data_sharing": false,
    "auto_save": true,
    "session_timeout": 3600
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to retrieve user preferences

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/preferences" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **PUT /me/preferences**

Update current user preferences and settings.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "preferences": {
    "theme": "dark",
    "language": "es",
    "notifications": false,
    "timezone": "America/New_York"
  },
  "settings": {
    "privacy_level": "high",
    "data_sharing": true,
    "auto_save": false,
    "session_timeout": 7200
  }
}
```

**Request Schema:**

- `preferences` (object, optional): User preferences
- `settings` (object, optional): User settings

**Response (200 OK):**

```json
{
  "user_id": 1,
  "preferences": {
    "theme": "dark",
    "language": "es",
    "notifications": false,
    "timezone": "America/New_York"
  },
  "settings": {
    "privacy_level": "high",
    "data_sharing": true,
    "auto_save": false,
    "session_timeout": 7200
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid data provided
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to update preferences

**Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/me/preferences" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "theme": "dark",
      "language": "es",
      "notifications": false,
      "timezone": "America/New_York"
    },
    "settings": {
      "privacy_level": "high",
      "data_sharing": true,
      "auto_save": false,
      "session_timeout": 7200
    }
  }'
```

---

### **GET /me/settings**

Get current user settings only.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "user_id": 1,
  "preferences": {},
  "settings": {
    "privacy_level": "standard",
    "data_sharing": false,
    "auto_save": true,
    "session_timeout": 3600
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to retrieve user settings

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/settings" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **PUT /me/settings**

Update current user settings only.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "settings": {
    "privacy_level": "high",
    "data_sharing": true,
    "auto_save": false,
    "session_timeout": 7200
  }
}
```

**Response (200 OK):**

```json
{
  "user_id": 1,
  "preferences": {},
  "settings": {
    "privacy_level": "high",
    "data_sharing": true,
    "auto_save": false,
    "session_timeout": 7200
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid data provided
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to update settings

**Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/me/settings" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "privacy_level": "high",
      "data_sharing": true,
      "auto_save": false,
      "session_timeout": 7200
    }
  }'
```

## 📱 **Phone Number Management**

### **GET /me/phone-numbers**

Get current user's phone numbers.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "phone_numbers": [
    {
      "id": 1,
      "user_id": 1,
      "phone_number": "+1234567890",
      "is_primary": true,
      "is_verified": true,
      "verification_method": "sms",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total_count": 1,
  "primary_phone_id": 1
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/phone-numbers" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /me/phone-numbers**

Add a new phone number for current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "phone_number": "+1987654321",
  "is_primary": false
}
```

**Request Schema:**

- `phone_number` (string, required): Phone number (10-15 digits, can start with +)
- `is_primary` (boolean, optional): Whether this is the primary phone number

**Response (201 Created):**

```json
{
  "id": 2,
  "user_id": 1,
  "phone_number": "+1987654321",
  "is_primary": false,
  "is_verified": false,
  "verification_method": "sms",
  "created_at": "2024-01-01T13:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Phone number already exists or invalid
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to add phone number

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/me/phone-numbers" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1987654321",
    "is_primary": false
  }'
```

---

### **PUT /me/phone-numbers/{phone_id}**

Update user's phone number.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Path Parameters:**

- `phone_id` (integer, required): Phone number ID

**Request Body:**

```json
{
  "phone_number": "+1987654321",
  "is_primary": true
}
```

**Response (200 OK):**

```json
{
  "id": 2,
  "user_id": 1,
  "phone_number": "+1987654321",
  "is_primary": true,
  "is_verified": false,
  "verification_method": "sms",
  "created_at": "2024-01-01T13:00:00Z",
  "updated_at": "2024-01-01T14:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: No valid data provided for update
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Phone number not found
- `500 Internal Server Error`: Failed to update phone number

**Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/me/phone-numbers/2" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1987654321",
    "is_primary": true
  }'
```

---

### **DELETE /me/phone-numbers/{phone_id}**

Delete user's phone number.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Path Parameters:**

- `phone_id` (integer, required): Phone number ID

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Phone number deleted successfully",
  "deleted_phone_number": "+1987654321",
  "remaining_phone_count": 1
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `404 Not Found`: Phone number not found
- `500 Internal Server Error`: Failed to delete phone number

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/me/phone-numbers/2" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /me/phone-numbers/{phone_id}/set-primary**

Set a phone number as primary for current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Path Parameters:**

- `phone_id` (integer, required): Phone number ID

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Primary phone number updated successfully",
  "phone_id": 2
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `404 Not Found`: Phone number not found
- `500 Internal Server Error`: Failed to set primary phone number

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/me/phone-numbers/2/set-primary" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /me/phone-numbers/verify**

Request verification code for a phone number.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "phone_number": "+1987654321"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Verification code sent successfully",
  "phone_number": "+1987654321",
  "verification_status": "pending",
  "expires_at": "2024-01-01T13:10:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `404 Not Found`: Phone number not found in user profile
- `500 Internal Server Error`: Failed to send verification code

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/me/phone-numbers/verify" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1987654321"
  }'
```

---

### **POST /me/phone-numbers/verify-code**

Verify phone number with verification code.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "phone_number": "+1987654321",
  "verification_code": "123456"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Phone number verified successfully",
  "phone_number": "+1987654321",
  "verification_status": "verified",
  "expires_at": null
}
```

**Error Responses:**

- `400 Bad Request`: Invalid verification code
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Phone number not found in user profile
- `500 Internal Server Error`: Failed to verify phone number

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/me/phone-numbers/verify-code" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1987654321",
    "verification_code": "123456"
  }'
```

## 👨‍💼 **Admin Endpoints**

These endpoints require admin permissions and allow management of all users.

---

### **GET /**

List all users (admin only).

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:read`

**Query Parameters:**

- `skip` (integer, optional): Number of users to skip (default: 0)
- `limit` (integer, optional): Maximum number of users to return (default: 100, max: 1000)

**Response (200 OK):**

```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "is_verified": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to retrieve users list

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **GET /{user_id}**

Get user by ID (admin only).

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:read`

**Path Parameters:**

- `user_id` (integer, required): User ID

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found
- `500 Internal Server Error`: Internal server error

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **PUT /{user_id}**

Update user by ID (admin only).

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:write`

**Path Parameters:**

- `user_id` (integer, required): User ID

**Request Body:**

```json
{
  "full_name": "John Smith",
  "is_active": false
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Smith",
  "is_active": false,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T14:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: No valid data provided for update
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found
- `500 Internal Server Error`: Internal server error

**Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "is_active": false
  }'
```

---

### **DELETE /{user_id}**

Deactivate user account (admin only).

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:delete`

**Path Parameters:**

- `user_id` (integer, required): User ID

**Request Body:**

```json
{
  "deactivate_reason": "Account violation"
}
```

**Response (200 OK):**

```json
{
  "message": "User deactivated successfully",
  "user_id": 1,
  "deactivated_at": "2024-01-01T14:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Cannot deactivate your own account
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found
- `500 Internal Server Error`: Internal server error

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "deactivate_reason": "Account violation"
  }'
```

---

### **POST /**

Create a new user (admin only).

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:write`

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "full_name": "Jane Doe",
  "password": "SecurePassword123!",
  "is_active": true,
  "is_verified": false
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "email": "newuser@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T14:00:00Z",
  "updated_at": "2024-01-01T14:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: User with this email already exists
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Internal server error

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "full_name": "Jane Doe",
    "password": "SecurePassword123!",
    "is_active": true,
    "is_verified": false
  }'
```

---

### **GET /{user_id}/stats**

Get user statistics (admin only).

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:read`

**Path Parameters:**

- `user_id` (integer, required): User ID

**Response (200 OK):**

```json
{
  "user_id": 1,
  "stats": {
    "total_sessions": 5,
    "last_login": "2024-01-01T12:00:00Z",
    "total_phone_numbers": 2,
    "verified_phone_numbers": 1,
    "mfa_enabled": true,
    "total_oauth_integrations": 3
  },
  "retrieved_at": "2024-01-01T14:00:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found
- `500 Internal Server Error`: Internal server error

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/1/stats" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🔒 **Security Features**

### **Permission Requirements**

- **Current User Endpoints**: Require `user:read` or `user:write` permissions
- **Admin Endpoints**: Require admin-level permissions (`user:read`, `user:write`, `user:delete`)

### **Data Validation**

- **Phone Numbers**: Validated format and uniqueness
- **Preferences/Settings**: JSON validation with schema enforcement
- **User Data**: Email format validation and password strength requirements

### **Access Control**

- Users can only access their own data
- Admins can access all user data
- Self-deactivation prevention for admin accounts

## 📝 **Default Values**

### **Default Preferences**

```json
{
  "theme": "light",
  "language": "en",
  "notifications": true,
  "timezone": "UTC"
}
```

### **Default Settings**

```json
{
  "privacy_level": "standard",
  "data_sharing": false,
  "auto_save": true,
  "session_timeout": 3600
}
```

## 🧪 **Testing**

Use the provided examples with curl or any HTTP client. The API also provides interactive documentation at `/docs` (Swagger UI) for testing endpoints directly in the browser.

---

**This user management API provides comprehensive user profile management, preferences, settings, phone number management, and administrative operations with proper security and access control.**
