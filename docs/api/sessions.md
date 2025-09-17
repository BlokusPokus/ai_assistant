# Sessions API

The Sessions API provides comprehensive session management capabilities for users, including viewing active sessions, invalidating sessions, extending session duration, and monitoring session statistics.

## Base URL

```
/api/v1/sessions
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Permission Requirements

- **Read operations**: Require `user:read` permission
- **Write operations**: Require `user:write` permission
- **Session management**: Requires authenticated user

## Rate Limiting

- **Read operations**: 100 requests per minute
- **Write operations**: 50 requests per minute
- **Session invalidation**: 10 requests per minute

## Session Management Endpoints

### Get User Sessions

Get all active sessions for the current user with device information and security details.

**Endpoint**: `GET /`

**Response**:

```json
[
  {
    "session_id": "sess_abc123def456",
    "device_info": {
      "browser": "Chrome",
      "os": "Windows",
      "device": "Desktop",
      "platform": "Windows 10"
    },
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "created_at": "2024-01-15T09:00:00Z",
    "last_accessed": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-15T21:00:00Z",
    "is_active": true,
    "session_type": "web"
  },
  {
    "session_id": "sess_xyz789uvw012",
    "device_info": {
      "browser": "Safari",
      "os": "iOS",
      "device": "Mobile",
      "platform": "iOS 17.0"
    },
    "ip_address": "192.168.1.101",
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "created_at": "2024-01-15T08:30:00Z",
    "last_accessed": "2024-01-15T10:25:00Z",
    "expires_at": "2024-01-15T20:30:00Z",
    "is_active": true,
    "session_type": "mobile"
  }
]
```

**Required Permissions**: `user:read`

**Status Codes**:

- `200 OK`: Sessions retrieved successfully
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Server error

### Get Session Statistics

Get comprehensive statistics about the current user's sessions.

**Endpoint**: `GET /stats`

**Response**:

```json
{
  "total_sessions": 3,
  "active_sessions": 2,
  "can_create_new": true,
  "oldest_session": "2024-01-15T08:30:00Z",
  "newest_session": "2024-01-15T09:00:00Z",
  "sessions_remaining": 2
}
```

**Authentication**: Required (no specific permissions needed)

**Status Codes**:

- `200 OK`: Statistics retrieved successfully
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server error

### Invalidate Specific Session

Invalidate a specific session by session ID.

**Endpoint**: `DELETE /{session_id}`

**Path Parameters**:

- `session_id` (string): ID of the session to invalidate

**Response**:

```json
{
  "message": "Session invalidated successfully"
}
```

**Required Permissions**: `user:write`

**Status Codes**:

- `200 OK`: Session invalidated successfully
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Session not found or doesn't belong to user
- `500 Internal Server Error`: Server error

**Security Note**: This action logs a security event for audit purposes.

### Invalidate All Sessions

Invalidate all sessions for the current user, with option to exclude the current session.

**Endpoint**: `POST /invalidate-all`

**Request Body**:

```json
{
  "exclude_current": true
}
```

**Request Parameters**:

- `exclude_current` (boolean, optional): Whether to exclude the current session from invalidation. Default: `true`

**Response**:

```json
{
  "message": "Invalidated 2 sessions successfully",
  "invalidated_count": 2
}
```

**Authentication**: Required (no specific permissions needed)

**Status Codes**:

- `200 OK`: Sessions invalidated successfully
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server error

**Security Note**: This action logs a security event with "warning" severity for audit purposes.

### Extend Session

Extend the expiration time of a specific session.

**Endpoint**: `POST /extend/{session_id}`

**Path Parameters**:

- `session_id` (string): ID of the session to extend

**Query Parameters**:

- `hours` (integer, optional): Number of hours to extend the session. If not provided, uses default extension time.

**Response**:

```json
{
  "message": "Session extended successfully"
}
```

**Authentication**: Required (no specific permissions needed)

**Status Codes**:

- `200 OK`: Session extended successfully
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Session not found or doesn't belong to user
- `500 Internal Server Error`: Server error

**Security Note**: This action logs a security event for audit purposes.

## Health Check Endpoint

### Session Service Health Check

Check the health status of the session management service.

**Endpoint**: `GET /health`

**Response**:

```json
{
  "status": "healthy",
  "service": "session_management",
  "redis": "connected"
}
```

**Authentication**: Not required

**Status Codes**:

- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

## Session Information

### Session Types

The system supports different types of sessions:

- **web**: Standard web browser sessions
- **mobile**: Mobile app sessions
- **api**: API client sessions
- **admin**: Administrative sessions

### Device Information

Session device information includes:

- **browser**: Browser name (Chrome, Firefox, Safari, etc.)
- **os**: Operating system (Windows, macOS, Linux, iOS, Android)
- **device**: Device type (Desktop, Mobile, Tablet)
- **platform**: Specific platform version

### Session Security

All session management operations are logged as security events:

- **session_invalidated**: Manual session invalidation
- **all_sessions_invalidated**: Bulk session invalidation
- **session_extended**: Session extension

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized

```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "detail": "Session not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to get sessions: Redis connection error"
}
```

### 503 Service Unavailable

```json
{
  "detail": "Session service unavailable"
}
```

## Usage Examples

### Get All User Sessions

```bash
curl -X GET "https://api.personalassistant.com/api/v1/sessions/" \
  -H "Authorization: Bearer <jwt_token>"
```

### Get Session Statistics

```bash
curl -X GET "https://api.personalassistant.com/api/v1/sessions/stats" \
  -H "Authorization: Bearer <jwt_token>"
```

### Invalidate Specific Session

```bash
curl -X DELETE "https://api.personalassistant.com/api/v1/sessions/sess_abc123def456" \
  -H "Authorization: Bearer <jwt_token>"
```

### Invalidate All Sessions

```bash
curl -X POST "https://api.personalassistant.com/api/v1/sessions/invalidate-all" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "exclude_current": true
  }'
```

### Extend Session

```bash
curl -X POST "https://api.personalassistant.com/api/v1/sessions/extend/sess_abc123def456?hours=2" \
  -H "Authorization: Bearer <jwt_token>"
```

### Check Service Health

```bash
curl -X GET "https://api.personalassistant.com/api/v1/sessions/health"
```

## Session Limits and Policies

### Maximum Sessions per User

- **Standard users**: 5 concurrent sessions
- **Premium users**: 10 concurrent sessions
- **Admin users**: 15 concurrent sessions

### Session Duration

- **Default session**: 12 hours
- **Extended session**: Up to 24 hours
- **Admin session**: 8 hours (security policy)

### Session Inactivity

- **Auto-logout**: 2 hours of inactivity
- **Warning**: 30 minutes before auto-logout
- **Extension**: Can be extended up to 3 times per day

## Security Features

### Session Tracking

- **IP Address**: Tracked for security monitoring
- **User Agent**: Logged for device identification
- **Device Fingerprinting**: Basic device information collection
- **Geolocation**: Optional location tracking (with consent)

### Security Events

All session operations generate security events:

- **Event Types**: session_invalidated, all_sessions_invalidated, session_extended
- **Severity Levels**: info, warning, critical
- **Retention**: 7 years (compliance requirement)

### Session Validation

- **Ownership Verification**: Users can only manage their own sessions
- **Permission Checks**: All operations require appropriate permissions
- **Audit Logging**: All actions are logged for security auditing

## Best Practices

### Session Management

1. **Regular Cleanup**: Periodically review and invalidate unused sessions
2. **Device Security**: Invalidate sessions from lost or compromised devices
3. **Session Monitoring**: Monitor session statistics for unusual activity
4. **Extension Limits**: Use session extensions sparingly for security

### Security Considerations

1. **Logout**: Always logout from shared or public devices
2. **Session Monitoring**: Regularly check active sessions for unauthorized access
3. **Device Trust**: Only extend sessions on trusted devices
4. **Bulk Invalidation**: Use "invalidate all" when account security is compromised

## Integration Notes

### Frontend Integration

- **Session List**: Display active sessions in user settings
- **Device Management**: Show device information for each session
- **Security Alerts**: Notify users of suspicious session activity
- **Auto-refresh**: Refresh session list periodically

### Mobile App Integration

- **Session Types**: Distinguish between web and mobile sessions
- **Push Notifications**: Alert users of new sessions on other devices
- **Biometric Sessions**: Support biometric authentication for session extension
- **Offline Handling**: Handle session expiration gracefully

## Data Retention

- **Active Sessions**: Retained until expiration or invalidation
- **Session Logs**: Retained for 30 days
- **Security Events**: Retained for 7 years (compliance requirement)
- **Device Information**: Retained for 1 year after session expiration
