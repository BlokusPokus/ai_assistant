# Task 044: OAuth Settings & Management - API Endpoints Reference

## 📋 **Overview**

This document provides a comprehensive reference for all OAuth API endpoints required for Task 044 implementation. It serves as a single source of truth to prevent integration mistakes between frontend and backend.

## 🔐 **Authentication Requirements**

**All endpoints require authentication via JWT token in the Authorization header:**

```typescript
// Frontend API call example
const headers = {
  Authorization: `Bearer ${jwtToken}`,
  "Content-Type": "application/json",
};
```

## 📡 **Backend Endpoints (Already Implemented)**

### **1. OAuth Provider Endpoints**

#### **GET `/api/v1/oauth/providers`**

**Purpose**: Get list of supported OAuth providers with their available scopes

**Request**: No body required (authentication header only)

**Response**:

```typescript
interface OAuthProviderInfo {
  name: string; // "google", "microsoft", "notion", "youtube"
  display_name: string; // "Google", "Microsoft", "Notion", "YouTube"
  description: string; // Provider description
  scopes: Array<{
    name: string; // "calendar.readonly", "drive.readonly"
    description: string; // "Read calendar events"
  }>;
}

// Response: OAuthProviderInfo[]
```

**Frontend Usage**:

```typescript
const getProviders = async () => {
  const response = await api.get("/oauth/providers");
  return response.data;
};
```

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

#### **POST `/api/v1/oauth/initiate`**

**Purpose**: Initiate an OAuth flow for a user

**Request**:

```typescript
interface OAuthInitiateRequest {
  provider: string; // "google", "microsoft", "notion", "youtube"
  scopes: string[]; // ["calendar.readonly", "drive.readonly"]
  redirect_uri?: string; // Optional custom redirect URI
}
```

**Response**:

```typescript
interface OAuthInitiateResponse {
  authorization_url: string; // OAuth provider authorization URL
  state_token: string; // CSRF protection token
  provider: string; // Provider name
  scopes: string[]; // Requested scopes
}
```

**Frontend Usage**:

```typescript
const initiateOAuth = async (request: OAuthInitiateRequest) => {
  const response = await api.post("/oauth/initiate", request);
  return response.data;
};
```

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

#### **GET `/api/v1/oauth/callback`**

**Purpose**: Handle OAuth callback and complete the flow

**Request**: Query parameters from OAuth provider redirect

**Response**:

```typescript
interface OAuthCallbackResponse {
  message: string; // Success/error message
  integration_id?: number; // ID of created integration
  error?: string; // Error details if failed
}
```

**Frontend Usage**: This endpoint is called by OAuth provider redirects, not directly by frontend

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

### **2. OAuth Integration Management Endpoints**

#### **GET `/api/v1/oauth/integrations`**

**Purpose**: Get OAuth integrations for the current user

**Request Parameters** (optional):

```typescript
interface GetIntegrationsParams {
  provider?: string; // Filter by provider
  active_only?: boolean; // Show only active integrations
}
```

**Response**:

```typescript
interface OAuthIntegrationResponse {
  id: number; // Integration ID
  provider: string; // Provider name
  status: string; // "active", "expired", "revoked"
  is_active: boolean; // Active status
  scopes: string[]; // Granted scopes
  created_at: string; // ISO timestamp
  last_sync_at?: string; // Last sync timestamp
  metadata?: Record<string, any>; // Provider-specific metadata
}

// Response: OAuthIntegrationResponse[]
```

**Frontend Usage**:

```typescript
const getIntegrations = async (params?: GetIntegrationsParams) => {
  const response = await api.get("/oauth/integrations", { params });
  return response.data;
};

// Examples:
const allIntegrations = await getIntegrations();
const googleIntegrations = await getIntegrations({ provider: "google" });
const activeOnly = await getIntegrations({ active_only: true });
```

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

#### **POST `/api/v1/oauth/integrations/{integration_id}/refresh`**

**Purpose**: Refresh tokens for an OAuth integration

**Request**: No body required

**Response**:

```typescript
interface RefreshTokensResponse {
  message: string; // Success/error message
  refreshed_at: string; // ISO timestamp of refresh
  expires_at?: string; // New expiration timestamp
}
```

**Frontend Usage**:

```typescript
const refreshTokens = async (integrationId: number) => {
  const response = await api.post(
    `/oauth/integrations/${integrationId}/refresh`
  );
  return response.data;
};
```

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

#### **DELETE `/api/v1/oauth/integrations/{integration_id}`**

**Purpose**: Revoke an OAuth integration

**Request**:

```typescript
interface RevokeIntegrationRequest {
  reason?: string; // Optional reason for revocation
}
```

**Response**:

```typescript
interface RevokeIntegrationResponse {
  message: string; // Success/error message
  revoked_at: string; // ISO timestamp of revocation
}
```

**Frontend Usage**:

```typescript
const revokeIntegration = async (integrationId: number, reason?: string) => {
  const response = await api.delete(`/oauth/integrations/${integrationId}`, {
    data: { reason },
  });
  return response.data;
};
```

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

#### **POST `/api/v1/oauth/integrations/sync`**

**Purpose**: Sync all OAuth integrations for the current user

**Request**: No body required

**Response**:

```typescript
interface SyncIntegrationsResponse {
  message: string; // Success/error message
  results: {
    total: number; // Total integrations processed
    successful: number; // Successfully synced
    failed: number; // Failed to sync
    errors?: Array<{
      integration_id: number;
      error: string;
    }>;
  };
}
```

**Frontend Usage**:

```typescript
const syncIntegrations = async () => {
  const response = await api.post("/oauth/integrations/sync");
  return response.data;
};
```

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

### **3. OAuth Status & Analytics Endpoints**

#### **GET `/api/v1/oauth/status`**

**Purpose**: Get OAuth status summary for the current user

**Request**: No body required

**Response**:

```typescript
interface OAuthStatusResponse {
  integrations: {
    total: number; // Total integrations
    active: number; // Active integrations
    expired: number; // Expired integrations
    revoked: number; // Revoked integrations
    providers: Record<
      string,
      {
        count: number; // Total for this provider
        active: number; // Active for this provider
        expired: number; // Expired for this provider
      }
    >;
  };
  consents: {
    total_consents: number; // Total consent records
    active_consents: number; // Active consent records
    expired_consents: number; // Expired consent records
  };
  last_sync?: string; // Last sync timestamp
}
```

**Frontend Usage**:

```typescript
const getOAuthStatus = async () => {
  const response = await api.get("/oauth/status");
  return response.data;
};
```

**Status**: ✅ **IMPLEMENTED** (Task 043)

---

## 🚀 **Frontend Service Implementation**

### **OAuth Settings Service Class**

```typescript
// services/oauthSettingsService.ts
import { api } from "../../services/api";

export class OAuthSettingsService {
  // Provider Management
  async getProviders() {
    const response = await api.get("/oauth/providers");
    return response.data;
  }

  async initiateOAuth(request: OAuthInitiateRequest) {
    const response = await api.post("/oauth/initiate", request);
    return response.data;
  }

  // Integration Management
  async getIntegrations(params?: GetIntegrationsParams) {
    const response = await api.get("/oauth/integrations", { params });
    return response.data;
  }

  async refreshTokens(integrationId: number) {
    const response = await api.post(
      `/oauth/integrations/${integrationId}/refresh`
    );
    return response.data;
  }

  async revokeIntegration(integrationId: number, reason?: string) {
    const response = await api.delete(`/oauth/integrations/${integrationId}`, {
      data: { reason },
    });
    return response.data;
  }

  async syncIntegrations() {
    const response = await api.post("/oauth/integrations/sync");
    return response.data;
  }

  // Status & Analytics
  async getStatus() {
    const response = await api.get("/oauth/status");
    return response.data;
  }

  // Enhanced Analytics (using existing status endpoint)
  async getAnalytics(timeRange: string = "7d") {
    const status = await this.getStatus();

    // Transform status data into analytics format
    return {
      integrations: {
        total: status.integrations.total || 0,
        active: status.integrations.active || 0,
        expired: status.integrations.expired || 0,
        revoked: status.integrations.revoked || 0,
      },
      providers: status.integrations.providers || {},
      usage: {
        total_requests: 0, // Would come from analytics endpoint
        successful_requests: 0,
        failed_requests: 0,
        average_response_time: 0,
      },
      trends: {
        daily: [], // Would come from analytics endpoint
        weekly: [],
      },
    };
  }

  // Settings Management (mock for now)
  async getSettings(): Promise<OAuthSettings> {
    return {
      autoRefreshTokens: true,
      refreshThreshold: 30,
      notifications: {
        tokenExpiry: true,
        syncFailures: true,
        securityAlerts: true,
      },
      security: {
        requireReauthForRevoke: true,
        auditLogRetention: 90,
      },
    };
  }

  async updateSettings(settings: Partial<OAuthSettings>): Promise<void> {
    // For now, just log the settings update
    // In the future, this could save to a dedicated settings endpoint
    console.log("Updating OAuth settings:", settings);
  }

  // Audit Logs (mock for now)
  async getAuditLogs(filters: AuditFilters = {}): Promise<OAuthAuditLog[]> {
    // For now, return mock audit data
    // In the future, this would come from an audit endpoint
    return [
      {
        id: 1,
        timestamp: new Date().toISOString(),
        user_id: 1,
        action: "integration_created",
        provider: "google",
        integration_id: 1,
        details: { scopes: ["calendar.readonly"] },
        ip_address: "192.168.1.1",
        user_agent: "Mozilla/5.0...",
      },
      // Add more mock audit entries...
    ];
  }

  // Data Export
  async exportData(
    format: "csv" | "json",
    filters?: AuditFilters
  ): Promise<string> {
    const data = await this.getAuditLogs(filters);

    if (format === "json") {
      return JSON.stringify(data, null, 2);
    } else {
      // Simple CSV conversion
      const headers = ["ID", "Timestamp", "Action", "Provider", "Details"];
      const rows = data.map((log) => [
        log.id,
        log.timestamp,
        log.action,
        log.provider,
        JSON.stringify(log.details),
      ]);

      return [headers, ...rows]
        .map((row) => row.map((cell) => `"${cell}"`).join(","))
        .join("\n");
    }
  }
}

export const oauthSettingsService = new OAuthSettingsService();
```

## 🔄 **API Integration Patterns**

### **1. Error Handling Pattern**

```typescript
const handleApiCall = async (apiFunction: () => Promise<any>) => {
  try {
    setLoading(true);
    setError(null);
    const result = await apiFunction();
    setData(result);
    return result;
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error occurred";
    setError(errorMessage);
    throw error;
  } finally {
    setLoading(false);
  }
};

// Usage
const loadIntegrations = () =>
  handleApiCall(() => oauthSettingsService.getIntegrations());
```

### **2. Optimistic Updates Pattern**

```typescript
const handleRevokeIntegration = async (
  integrationId: number,
  reason?: string
) => {
  // Optimistically remove from UI
  const previousIntegrations = [...integrations];
  setIntegrations((prev) => prev.filter((i) => i.id !== integrationId));

  try {
    await oauthSettingsService.revokeIntegration(integrationId, reason);
    // Success - no need to update UI again
  } catch (error) {
    // Revert on failure
    setIntegrations(previousIntegrations);
    setError("Failed to revoke integration");
  }
};
```

### **3. Batch Operations Pattern**

```typescript
const handleBulkRefresh = async (integrationIds: number[]) => {
  const results = await Promise.allSettled(
    integrationIds.map((id) => oauthSettingsService.refreshTokens(id))
  );

  const successful = results.filter((r) => r.status === "fulfilled").length;
  const failed = results.filter((r) => r.status === "rejected").length;

  if (failed > 0) {
    setError(`${failed} integrations failed to refresh`);
  }

  // Reload integrations to get updated status
  await loadIntegrations();
};
```

## 📊 **Data Flow Diagrams**

### **Integration Management Flow**

```
User Action → Frontend Component → Service Method → API Endpoint → Backend → Response → State Update → UI Update
```

**Example: Refresh Integration**

1. User clicks "Refresh" button
2. `IntegrationsTab` calls `refreshIntegration(integrationId)`
3. `oauthSettingsService.refreshTokens(integrationId)` called
4. API request to `POST /oauth/integrations/{id}/refresh`
5. Backend processes refresh and returns response
6. Frontend updates local state
7. UI reflects new token status

### **Analytics Data Flow**

```
Tab Change → loadAnalytics() → getAnalytics() → getStatus() → API Call → Transform Data → Display
```

**Example: Analytics Tab**

1. User switches to Analytics tab
2. `AnalyticsTab` calls `loadAnalytics()`
3. Store calls `oauthSettingsService.getAnalytics()`
4. Service calls `getStatus()` endpoint
5. Backend returns status data
6. Service transforms status into analytics format
7. Store updates analytics state
8. UI displays metrics and charts

## 🚨 **Common Integration Mistakes to Avoid**

### **1. Authentication Headers**

❌ **Wrong**: Missing Authorization header

```typescript
const response = await api.get("/oauth/integrations"); // Missing auth
```

✅ **Correct**: Include Authorization header

```typescript
const response = await api.get("/oauth/integrations", {
  headers: { Authorization: `Bearer ${token}` },
});
```

### **2. API Endpoint Paths**

❌ **Wrong**: Incorrect endpoint path

```typescript
const response = await api.get("/api/oauth/integrations"); // Wrong path
```

✅ **Correct**: Use correct endpoint path

```typescript
const response = await api.get("/oauth/integrations"); // Correct path
```

### **3. Request Body Format**

❌ **Wrong**: Sending data in wrong format

```typescript
const response = await api.delete(`/oauth/integrations/${id}`, {
  body: { reason: "test" }, // Wrong - should be 'data'
});
```

✅ **Correct**: Use correct request format

```typescript
const response = await api.delete(`/oauth/integrations/${id}`, {
  data: { reason: "test" }, // Correct
});
```

### **4. Error Handling**

❌ **Wrong**: No error handling

```typescript
const integrations = await oauthSettingsService.getIntegrations(); // No error handling
```

✅ **Correct**: Proper error handling

```typescript
try {
  const integrations = await oauthSettingsService.getIntegrations();
  setIntegrations(integrations);
} catch (error) {
  setError("Failed to load integrations");
  console.error("API Error:", error);
}
```

## 📋 **API Testing Checklist**

### **Endpoint Availability**

- [ ] `/api/v1/oauth/providers` - Returns provider list
- [ ] `/api/v1/oauth/integrations` - Returns user integrations
- [ ] `/api/v1/oauth/integrations/{id}/refresh` - Refreshes tokens
- [ ] `/api/v1/oauth/integrations/{id}` - Revokes integration
- [ ] `/api/v1/oauth/integrations/sync` - Syncs all integrations
- [ ] `/api/v1/oauth/status` - Returns status summary

### **Authentication Testing**

- [ ] All endpoints require valid JWT token
- [ ] Invalid/expired tokens return 401
- [ ] Missing Authorization header returns 401

### **Response Format Testing**

- [ ] All endpoints return consistent JSON structure
- [ ] Error responses include proper error messages
- [ ] Success responses include required data fields

### **Error Scenarios Testing**

- [ ] Invalid integration ID returns 404
- [ ] Unauthorized access returns 403
- [ ] Server errors return 500
- [ ] Network errors are handled gracefully

## 🔮 **Future API Enhancements**

### **Potential New Endpoints**

- **`GET /api/v1/oauth/analytics`** - Detailed usage analytics
- **`GET /api/v1/oauth/audit-logs`** - OAuth activity audit logs
- **`POST /api/v1/oauth/settings`** - Save OAuth preferences
- **`GET /api/v1/oauth/settings`** - Retrieve OAuth preferences
- **`POST /api/v1/oauth/bulk-operations`** - Bulk refresh/revoke operations

### **Enhanced Response Models**

- **Real-time Updates**: WebSocket integration for live status
- **Pagination Support**: Handle large numbers of integrations
- **Advanced Filtering**: Date ranges, provider-specific filters
- **Export Formats**: CSV, JSON, PDF export options

---

## 📚 **Quick Reference**

### **Essential Endpoints**

| Endpoint                           | Method | Purpose               | Status         |
| ---------------------------------- | ------ | --------------------- | -------------- |
| `/oauth/providers`                 | GET    | List providers        | ✅ Implemented |
| `/oauth/integrations`              | GET    | List integrations     | ✅ Implemented |
| `/oauth/integrations/{id}/refresh` | POST   | Refresh tokens        | ✅ Implemented |
| `/oauth/integrations/{id}`         | DELETE | Revoke integration    | ✅ Implemented |
| `/oauth/integrations/sync`         | POST   | Sync all integrations | ✅ Implemented |
| `/oauth/status`                    | GET    | Get status summary    | ✅ Implemented |

### **Frontend Service Methods**

| Method                          | API Endpoint                            | Purpose                    |
| ------------------------------- | --------------------------------------- | -------------------------- |
| `getProviders()`                | `GET /oauth/providers`                  | Get OAuth providers        |
| `getIntegrations()`             | `GET /oauth/integrations`               | Get user integrations      |
| `refreshTokens(id)`             | `POST /oauth/integrations/{id}/refresh` | Refresh integration tokens |
| `revokeIntegration(id, reason)` | `DELETE /oauth/integrations/{id}`       | Revoke integration         |
| `syncIntegrations()`            | `POST /oauth/integrations/sync`         | Sync all integrations      |
| `getStatus()`                   | `GET /oauth/status`                     | Get OAuth status           |

---

**This document serves as the single source of truth for all OAuth API integration in Task 044. Always refer to this reference when implementing frontend-backend integration to prevent mistakes.**
