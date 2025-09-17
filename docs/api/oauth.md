# 🔗 OAuth Integration API Documentation

## 🎯 **Overview**

The OAuth Integration API provides endpoints for connecting with external services like Google, Microsoft, Notion, and YouTube. It handles the complete OAuth 2.0 flow including authorization, token management, and integration status monitoring.

## 📍 **Base Path**

All OAuth endpoints are prefixed with `/api/v1/oauth`

## 🔑 **Endpoints**

### **Provider Management**

---

### **GET /providers**

Get list of supported OAuth providers with their available scopes.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
[
  {
    "name": "google",
    "display_name": "Google",
    "description": "Google services including Calendar, Drive, and Gmail",
    "scopes": [
      {
        "name": "calendar",
        "description": "Access to Google Calendar",
        "required": false
      },
      {
        "name": "drive",
        "description": "Access to Google Drive",
        "required": false
      },
      {
        "name": "gmail",
        "description": "Access to Gmail",
        "required": false
      }
    ]
  },
  {
    "name": "microsoft",
    "display_name": "Microsoft",
    "description": "Microsoft 365 services including Outlook and OneDrive",
    "scopes": [
      {
        "name": "calendar",
        "description": "Access to Outlook Calendar",
        "required": false
      },
      {
        "name": "mail",
        "description": "Access to Outlook Mail",
        "required": false
      },
      {
        "name": "onedrive",
        "description": "Access to OneDrive",
        "required": false
      }
    ]
  },
  {
    "name": "notion",
    "display_name": "Notion",
    "description": "Notion workspace and pages",
    "scopes": [
      {
        "name": "read",
        "description": "Read Notion pages",
        "required": true
      },
      {
        "name": "write",
        "description": "Write to Notion pages",
        "required": false
      }
    ]
  },
  {
    "name": "youtube",
    "display_name": "YouTube",
    "description": "YouTube videos and channels",
    "scopes": [
      {
        "name": "readonly",
        "description": "Read YouTube data",
        "required": true
      },
      {
        "name": "manage",
        "description": "Manage YouTube content",
        "required": false
      }
    ]
  }
]
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to get providers

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/providers" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **OAuth Flow Management**

---

### **POST /initiate**

Initiate an OAuth flow for a user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "provider": "google",
  "scopes": ["calendar", "drive"],
  "redirect_uri": "https://yourapp.com/oauth/callback"
}
```

**Request Schema:**

- `provider` (string, required): OAuth provider name (google, microsoft, notion, youtube)
- `scopes` (array, required): List of requested scopes
- `redirect_uri` (string, optional): Custom redirect URI

**Response (200 OK):**

```json
{
  "authorization_url": "https://accounts.google.com/oauth/authorize?client_id=...&redirect_uri=...&scope=...&state=...",
  "state_token": "oauth_state_abc123def456",
  "provider": "google",
  "scopes": ["calendar", "drive"]
}
```

**Response Schema:**

- `authorization_url` (string): URL to redirect user for authorization
- `state_token` (string): State token for security validation
- `provider` (string): OAuth provider name
- `scopes` (array): Requested scopes

**Error Responses:**

- `400 Bad Request`: Unsupported provider or invalid scopes
- `401 Unauthorized`: Authentication required
- `503 Service Unavailable`: OAuth service temporarily unavailable
- `500 Internal Server Error`: Failed to initiate OAuth flow

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/oauth/initiate" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "scopes": ["calendar", "drive"],
    "redirect_uri": "https://yourapp.com/oauth/callback"
  }'
```

**OAuth Flow Process:**

1. **Initiate**: Call this endpoint to get authorization URL
2. **Redirect**: Redirect user to the authorization URL
3. **Authorize**: User authorizes the application on provider's site
4. **Callback**: Provider redirects to callback URL with authorization code
5. **Complete**: Use `/callback` endpoint to complete the flow

---

### **GET /callback**

Handle OAuth callback and complete the flow.

**Query Parameters:**

- `state` (string, required): OAuth state parameter
- `code` (string, required): OAuth authorization code
- `provider` (string, optional): OAuth provider name

**Response (200 OK):**

```json
{
  "message": "OAuth integration completed successfully",
  "integration_id": 123,
  "provider": "google",
  "status": "active"
}
```

**Response Schema:**

- `message` (string): Success message
- `integration_id` (integer): ID of the created integration
- `provider` (string): OAuth provider name
- `status` (string): Integration status

**Error Responses:**

- `400 Bad Request`: Invalid state token or authorization code
- `500 Internal Server Error`: Failed to complete OAuth flow

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/callback?state=oauth_state_abc123def456&code=authorization_code_xyz789&provider=google"
```

**Note:** This endpoint is typically called by the OAuth provider, not directly by your application.

---

### **Integration Management**

---

### **GET /integrations**

Get OAuth integrations for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Query Parameters:**

- `provider` (string, optional): Filter by provider name
- `active_only` (boolean, optional): Return only active integrations (default: true)

**Response (200 OK):**

```json
[
  {
    "id": 123,
    "provider": "google",
    "status": "active",
    "is_active": true,
    "scopes": ["calendar", "drive"],
    "created_at": "2024-01-01T00:00:00Z",
    "last_sync_at": "2024-01-01T12:00:00Z",
    "metadata": {
      "user_email": "user@gmail.com",
      "account_type": "personal"
    }
  },
  {
    "id": 124,
    "provider": "microsoft",
    "status": "active",
    "is_active": true,
    "scopes": ["calendar", "mail"],
    "created_at": "2024-01-01T01:00:00Z",
    "last_sync_at": "2024-01-01T13:00:00Z",
    "metadata": {
      "user_email": "user@outlook.com",
      "account_type": "business"
    }
  }
]
```

**Response Schema:**

- `id` (integer): Integration ID
- `provider` (string): OAuth provider name
- `status` (string): Integration status (active, inactive, expired, revoked)
- `is_active` (boolean): Whether integration is active
- `scopes` (array): Granted scopes
- `created_at` (string): Creation timestamp
- `last_sync_at` (string, nullable): Last synchronization timestamp
- `metadata` (object, nullable): Additional provider-specific data

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to get integrations

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/integrations?provider=google&active_only=true" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /integrations/{integration_id}/refresh**

Refresh tokens for an OAuth integration.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Path Parameters:**

- `integration_id` (integer, required): Integration ID

**Response (200 OK):**

```json
{
  "message": "Tokens refreshed successfully"
}
```

**Error Responses:**

- `400 Bad Request`: Failed to refresh tokens
- `401 Unauthorized`: Authentication required
- `503 Service Unavailable`: OAuth service temporarily unavailable
- `500 Internal Server Error`: Failed to refresh tokens

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/oauth/integrations/123/refresh" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Token Refresh Process:**

1. **Automatic**: Tokens are automatically refreshed when they expire
2. **Manual**: Use this endpoint to manually refresh tokens
3. **Validation**: System validates refresh token with provider
4. **Update**: New tokens are stored securely

---

### **DELETE /integrations/{integration_id}**

Revoke an OAuth integration.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Path Parameters:**

- `integration_id` (integer, required): Integration ID

**Query Parameters:**

- `reason` (string, optional): Reason for revocation

**Response (200 OK):**

```json
{
  "message": "Integration revoked successfully"
}
```

**Error Responses:**

- `400 Bad Request`: Failed to revoke integration
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to revoke integration

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/oauth/integrations/123?reason=user_request" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Revocation Process:**

1. **Revoke**: Tokens are revoked with the OAuth provider
2. **Deactivate**: Integration is marked as inactive
3. **Cleanup**: Associated data is cleaned up
4. **Logging**: Revocation is logged for audit purposes

---

### **POST /integrations/sync**

Sync all OAuth integrations for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "message": "Integration sync completed",
  "results": [
    {
      "integration_id": 123,
      "provider": "google",
      "status": "success",
      "synced_at": "2024-01-01T14:00:00Z"
    },
    {
      "integration_id": 124,
      "provider": "microsoft",
      "status": "success",
      "synced_at": "2024-01-01T14:00:00Z"
    }
  ]
}
```

**Response Schema:**

- `message` (string): Success message
- `results` (array): Sync results for each integration
  - `integration_id` (integer): Integration ID
  - `provider` (string): Provider name
  - `status` (string): Sync status (success, failed, skipped)
  - `synced_at` (string): Sync timestamp

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to sync integrations

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/oauth/integrations/sync" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Sync Process:**

1. **Validate**: Check if tokens are still valid
2. **Refresh**: Refresh expired tokens if possible
3. **Sync**: Synchronize data with provider
4. **Update**: Update last sync timestamp
5. **Report**: Return sync results

---

### **GET /status**

Get OAuth status summary for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "integrations": {
    "total": 4,
    "active": 3,
    "expired": 1,
    "revoked": 0,
    "by_provider": {
      "google": {
        "total": 1,
        "active": 1,
        "last_sync": "2024-01-01T12:00:00Z"
      },
      "microsoft": {
        "total": 1,
        "active": 1,
        "last_sync": "2024-01-01T13:00:00Z"
      },
      "notion": {
        "total": 1,
        "active": 0,
        "last_sync": null
      },
      "youtube": {
        "total": 1,
        "active": 1,
        "last_sync": "2024-01-01T11:00:00Z"
      }
    }
  },
  "consents": {
    "total_consents": 4,
    "active_consents": 3,
    "expired_consents": 1,
    "consent_summary": {
      "google": {
        "granted_scopes": ["calendar", "drive"],
        "consent_date": "2024-01-01T00:00:00Z",
        "expires_at": "2024-01-01T00:00:00Z"
      },
      "microsoft": {
        "granted_scopes": ["calendar", "mail"],
        "consent_date": "2024-01-01T01:00:00Z",
        "expires_at": "2024-01-01T01:00:00Z"
      }
    }
  }
}
```

**Response Schema:**

- `integrations` (object): Integration status summary
  - `total` (integer): Total number of integrations
  - `active` (integer): Number of active integrations
  - `expired` (integer): Number of expired integrations
  - `revoked` (integer): Number of revoked integrations
  - `by_provider` (object): Status by provider
- `consents` (object): Consent status summary
  - `total_consents` (integer): Total number of consents
  - `active_consents` (integer): Number of active consents
  - `expired_consents` (integer): Number of expired consents
  - `consent_summary` (object): Consent details by provider

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to get OAuth status

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🔒 **Security Features**

### **OAuth 2.0 Compliance**

- **Authorization Code Flow**: Standard OAuth 2.0 authorization code flow
- **State Parameter**: CSRF protection using state tokens
- **PKCE Support**: Proof Key for Code Exchange for additional security
- **Token Storage**: Secure storage of access and refresh tokens

### **Token Management**

- **Automatic Refresh**: Tokens are automatically refreshed before expiry
- **Secure Storage**: Tokens are encrypted and stored securely
- **Revocation**: Tokens can be revoked and invalidated
- **Expiry Handling**: Graceful handling of expired tokens

### **Provider Security**

- **Credential Validation**: OAuth credentials are validated before use
- **Scope Validation**: Requested scopes are validated against provider capabilities
- **Error Handling**: Graceful handling of provider errors and outages

### **User Privacy**

- **Consent Tracking**: User consent is tracked and managed
- **Data Isolation**: User data is isolated between integrations
- **Audit Logging**: All OAuth operations are logged for audit purposes

## 🔄 **OAuth Flow Examples**

### **Google Calendar Integration**

1. **Get Providers**: Check available Google scopes
2. **Initiate Flow**: Request calendar access
3. **User Authorization**: User authorizes on Google's site
4. **Complete Integration**: Integration is created and activated
5. **Sync Data**: Calendar data is synchronized

### **Microsoft Outlook Integration**

1. **Get Providers**: Check available Microsoft scopes
2. **Initiate Flow**: Request mail and calendar access
3. **User Authorization**: User authorizes on Microsoft's site
4. **Complete Integration**: Integration is created and activated
5. **Sync Data**: Mail and calendar data is synchronized

### **Notion Workspace Integration**

1. **Get Providers**: Check available Notion scopes
2. **Initiate Flow**: Request workspace access
3. **User Authorization**: User authorizes on Notion's site
4. **Complete Integration**: Integration is created and activated
5. **Sync Data**: Workspace data is synchronized

## 📱 **Supported Providers**

### **Google**

- **Services**: Calendar, Drive, Gmail, Contacts
- **Scopes**: calendar, drive, gmail, contacts
- **Authentication**: OAuth 2.0 with PKCE

### **Microsoft**

- **Services**: Outlook, OneDrive, Teams
- **Scopes**: calendar, mail, onedrive, teams
- **Authentication**: OAuth 2.0 with PKCE

### **Notion**

- **Services**: Workspace, Pages, Databases
- **Scopes**: read, write, insert
- **Authentication**: OAuth 2.0

### **YouTube**

- **Services**: Videos, Channels, Playlists
- **Scopes**: readonly, manage
- **Authentication**: OAuth 2.0

## 🚨 **Error Handling**

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status": "error",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Common Error Codes**

- `OAUTH_PROVIDER_ERROR`: Provider-specific error
- `OAUTH_CREDENTIALS_MISSING`: OAuth credentials not configured
- `OAUTH_TOKEN_EXPIRED`: Access token has expired
- `OAUTH_TOKEN_INVALID`: Invalid or revoked token
- `OAUTH_SCOPE_INVALID`: Invalid or unsupported scope
- `OAUTH_STATE_INVALID`: Invalid state parameter

## 🧪 **Testing**

Use the provided examples with curl or any HTTP client. The API also provides interactive documentation at `/docs` (Swagger UI) for testing endpoints directly in the browser.

### **Testing OAuth Flow**

1. **Development**: Use test OAuth applications for development
2. **Staging**: Use staging OAuth applications for testing
3. **Production**: Use production OAuth applications for live deployment

### **Provider Testing**

- **Google**: Use Google Cloud Console for OAuth app configuration
- **Microsoft**: Use Azure Portal for OAuth app configuration
- **Notion**: Use Notion Developer Portal for OAuth app configuration
- **YouTube**: Use Google Cloud Console for YouTube API access

---

**This OAuth API provides comprehensive integration with external services, enabling secure data synchronization and enhanced functionality for the Personal Assistant system.**
