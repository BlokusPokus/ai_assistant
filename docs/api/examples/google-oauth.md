# Google OAuth Integration Examples

This example demonstrates the complete Google OAuth integration flow, including authorization, token exchange, and API usage.

## Overview

The Google OAuth flow involves:

1. Getting supported OAuth providers
2. Initiating OAuth flow with Google
3. Handling OAuth callback
4. Managing Google integrations
5. Using Google services through the integration

## Prerequisites

- Valid authentication token
- Google OAuth credentials configured
- Access to OAuth API endpoints

## Step 1: Get Supported Providers

### Check available OAuth providers

```bash
curl -X GET "https://api.personalassistant.com/api/v1/oauth/providers" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "providers": [
    {
      "name": "google",
      "display_name": "Google",
      "description": "Access Google services like Gmail, Calendar, Drive, and YouTube",
      "scopes": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/youtube.readonly"
      ],
      "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
      "token_url": "https://oauth2.googleapis.com/token",
      "enabled": true
    },
    {
      "name": "microsoft",
      "display_name": "Microsoft",
      "description": "Access Microsoft services like Outlook, OneDrive, and Teams",
      "scopes": [
        "https://graph.microsoft.com/User.Read",
        "https://graph.microsoft.com/Mail.Read",
        "https://graph.microsoft.com/Calendars.Read"
      ],
      "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
      "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
      "enabled": true
    }
  ]
}
```

## Step 2: Initiate Google OAuth Flow

### Start Google OAuth authorization

```bash
curl -X POST "https://api.personalassistant.com/api/v1/oauth/initiate" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "scopes": [
      "https://www.googleapis.com/auth/gmail.readonly",
      "https://www.googleapis.com/auth/calendar.readonly"
    ],
    "redirect_uri": "https://yourapp.com/oauth/callback"
  }'
```

**Expected Response:**

```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=your_client_id&redirect_uri=https%3A%2F%2Fyourapp.com%2Foauth%2Fcallback&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.readonly&state=oauth_state_abc123",
  "state": "oauth_state_abc123",
  "provider": "google",
  "expires_in": 600
}
```

### JavaScript Implementation

```javascript
class GoogleOAuthService {
  constructor(accessToken) {
    this.baseURL = "https://api.personalassistant.com/api/v1/oauth";
    this.accessToken = accessToken;
  }

  async getProviders() {
    const response = await fetch(`${this.baseURL}/providers`, {
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async initiateOAuth(provider, scopes, redirectUri) {
    const response = await fetch(`${this.baseURL}/initiate`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        provider,
        scopes,
        redirect_uri: redirectUri,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async handleCallback(code, state) {
    const response = await fetch(`${this.baseURL}/callback`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        state,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async getIntegrations() {
    const response = await fetch(`${this.baseURL}/integrations`, {
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async refreshToken(integrationId) {
    const response = await fetch(
      `${this.baseURL}/integrations/${integrationId}/refresh`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async revokeIntegration(integrationId) {
    const response = await fetch(
      `${this.baseURL}/integrations/${integrationId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }
}

// Usage example
async function demonstrateGoogleOAuth() {
  const oauthService = new GoogleOAuthService("your_access_token");

  try {
    // 1. Get available providers
    console.log("1. Getting OAuth providers...");
    const providers = await oauthService.getProviders();
    console.log(
      "Available providers:",
      providers.providers.map((p) => p.name)
    );

    // 2. Initiate Google OAuth
    console.log("2. Initiating Google OAuth...");
    const oauthInit = await oauthService.initiateOAuth(
      "google",
      [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.readonly",
      ],
      "https://yourapp.com/oauth/callback"
    );
    console.log("Authorization URL:", oauthInit.authorization_url);

    // 3. Redirect user to authorization URL
    // In a real app, you would redirect the user to oauthInit.authorization_url
    // After user authorizes, they'll be redirected back with a code

    // 4. Handle callback (simulated)
    console.log("3. Handling OAuth callback...");
    const callbackResult = await oauthService.handleCallback(
      "authorization_code_from_google",
      oauthInit.state
    );
    console.log("OAuth callback successful:", callbackResult);

    // 5. Get user integrations
    console.log("4. Getting user integrations...");
    const integrations = await oauthService.getIntegrations();
    console.log("User integrations:", integrations);
  } catch (error) {
    console.error("OAuth flow failed:", error.message);
  }
}
```

## Step 3: Handle OAuth Callback

### Process OAuth callback

```bash
curl -X POST "https://api.personalassistant.com/api/v1/oauth/callback" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "authorization_code_from_google",
    "state": "oauth_state_abc123"
  }'
```

**Expected Response:**

```json
{
  "integration_id": "int_xyz789",
  "provider": "google",
  "status": "active",
  "scopes": [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly"
  ],
  "user_info": {
    "id": "google_user_123",
    "email": "user@gmail.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/..."
  },
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-15T11:30:00Z"
}
```

## Step 4: Manage Google Integrations

### Get user integrations

```bash
curl -X GET "https://api.personalassistant.com/api/v1/oauth/integrations" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "integrations": [
    {
      "id": "int_xyz789",
      "provider": "google",
      "status": "active",
      "scopes": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.readonly"
      ],
      "user_info": {
        "id": "google_user_123",
        "email": "user@gmail.com",
        "name": "John Doe",
        "picture": "https://lh3.googleusercontent.com/..."
      },
      "created_at": "2024-01-15T10:30:00Z",
      "expires_at": "2024-01-15T11:30:00Z",
      "last_sync": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

### Refresh Google token

```bash
curl -X POST "https://api.personalassistant.com/api/v1/oauth/integrations/int_xyz789/refresh" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "message": "Token refreshed successfully",
  "integration_id": "int_xyz789",
  "expires_at": "2024-01-15T12:30:00Z"
}
```

### Revoke Google integration

```bash
curl -X DELETE "https://api.personalassistant.com/api/v1/oauth/integrations/int_xyz789" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "message": "Integration revoked successfully",
  "integration_id": "int_xyz789"
}
```

## Complete Google OAuth Integration Example

### HTML/JavaScript Implementation

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Google OAuth Integration</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
      }
      .container {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      }
      .integration-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background: #f9f9f9;
      }
      .integration-card.active {
        border-color: #4caf50;
        background: #f0f8f0;
      }
      .integration-card.expired {
        border-color: #f44336;
        background: #fff0f0;
      }
      .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        margin: 5px;
        text-decoration: none;
        display: inline-block;
      }
      .btn-primary {
        background-color: #007bff;
        color: white;
      }
      .btn-success {
        background-color: #28a745;
        color: white;
      }
      .btn-danger {
        background-color: #dc3545;
        color: white;
      }
      .btn:hover {
        opacity: 0.8;
      }
      .status {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
      }
      .status.active {
        background-color: #d4edda;
        color: #155724;
      }
      .status.expired {
        background-color: #f8d7da;
        color: #721c24;
      }
      .user-info {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
      }
      .user-info img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
      }
      .scopes {
        margin-top: 10px;
      }
      .scope-tag {
        display: inline-block;
        background-color: #e9ecef;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin: 2px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Google OAuth Integration</h1>

      <div id="providers"></div>

      <div id="integrations">
        <h3>Your Google Integrations</h3>
        <div id="integrationsList"></div>
      </div>

      <div id="oauthStatus"></div>
    </div>

    <script>
      class GoogleOAuthApp {
        constructor() {
          this.accessToken = localStorage.getItem("access_token");
          this.oauthService = new GoogleOAuthService(this.accessToken);
          this.init();
        }

        async init() {
          if (!this.accessToken) {
            document.getElementById("oauthStatus").innerHTML =
              '<p style="color: red;">Please login first</p>';
            return;
          }

          await this.loadProviders();
          await this.loadIntegrations();
        }

        async loadProviders() {
          try {
            const providers = await this.oauthService.getProviders();
            this.displayProviders(providers.providers);
          } catch (error) {
            console.error("Failed to load providers:", error);
          }
        }

        displayProviders(providers) {
          const container = document.getElementById("providers");
          container.innerHTML = "<h3>Available OAuth Providers</h3>";

          providers.forEach((provider) => {
            const div = document.createElement("div");
            div.className = "integration-card";
            div.innerHTML = `
                        <h4>${provider.display_name}</h4>
                        <p>${provider.description}</p>
                        <div class="scopes">
                            <strong>Scopes:</strong>
                            ${provider.scopes
                              .map(
                                (scope) =>
                                  `<span class="scope-tag">${scope}</span>`
                              )
                              .join("")}
                        </div>
                        <button class="btn btn-primary" onclick="app.connectProvider('${
                          provider.name
                        }')">
                            Connect ${provider.display_name}
                        </button>
                    `;
            container.appendChild(div);
          });
        }

        async loadIntegrations() {
          try {
            const integrations = await this.oauthService.getIntegrations();
            this.displayIntegrations(integrations.integrations);
          } catch (error) {
            console.error("Failed to load integrations:", error);
          }
        }

        displayIntegrations(integrations) {
          const container = document.getElementById("integrationsList");
          container.innerHTML = "";

          if (integrations.length === 0) {
            container.innerHTML =
              "<p>No integrations found. Connect a provider to get started.</p>";
            return;
          }

          integrations.forEach((integration) => {
            const div = document.createElement("div");
            div.className = `integration-card ${integration.status}`;

            const isExpired = new Date(integration.expires_at) < new Date();
            const statusClass = isExpired ? "expired" : "active";

            div.innerHTML = `
                        <div class="user-info">
                            <img src="${
                              integration.user_info.picture
                            }" alt="Profile">
                            <div>
                                <strong>${
                                  integration.user_info.name
                                }</strong><br>
                                <small>${integration.user_info.email}</small>
                            </div>
                        </div>
                        <div class="status ${statusClass}">
                            ${integration.status.toUpperCase()}
                        </div>
                        <div class="scopes">
                            <strong>Scopes:</strong>
                            ${integration.scopes
                              .map(
                                (scope) =>
                                  `<span class="scope-tag">${scope}</span>`
                              )
                              .join("")}
                        </div>
                        <div>
                            <small>Connected: ${new Date(
                              integration.created_at
                            ).toLocaleString()}</small><br>
                            <small>Expires: ${new Date(
                              integration.expires_at
                            ).toLocaleString()}</small>
                        </div>
                        <div>
                            <button class="btn btn-success" onclick="app.refreshIntegration('${
                              integration.id
                            }')">
                                Refresh Token
                            </button>
                            <button class="btn btn-danger" onclick="app.revokeIntegration('${
                              integration.id
                            }')">
                                Revoke Access
                            </button>
                        </div>
                    `;
            container.appendChild(div);
          });
        }

        async connectProvider(providerName) {
          try {
            const oauthInit = await this.oauthService.initiateOAuth(
              providerName,
              [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/calendar.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
              ],
              window.location.origin + "/oauth/callback"
            );

            // Store state for verification
            localStorage.setItem("oauth_state", oauthInit.state);

            // Redirect to authorization URL
            window.location.href = oauthInit.authorization_url;
          } catch (error) {
            console.error("Failed to initiate OAuth:", error);
            alert("Failed to initiate OAuth: " + error.message);
          }
        }

        async refreshIntegration(integrationId) {
          try {
            const result = await this.oauthService.refreshToken(integrationId);
            alert("Token refreshed successfully");
            await this.loadIntegrations();
          } catch (error) {
            console.error("Failed to refresh token:", error);
            alert("Failed to refresh token: " + error.message);
          }
        }

        async revokeIntegration(integrationId) {
          if (!confirm("Are you sure you want to revoke this integration?")) {
            return;
          }

          try {
            const result = await this.oauthService.revokeIntegration(
              integrationId
            );
            alert("Integration revoked successfully");
            await this.loadIntegrations();
          } catch (error) {
            console.error("Failed to revoke integration:", error);
            alert("Failed to revoke integration: " + error.message);
          }
        }

        async handleCallback(code, state) {
          try {
            const storedState = localStorage.getItem("oauth_state");
            if (state !== storedState) {
              throw new Error("Invalid state parameter");
            }

            const result = await this.oauthService.handleCallback(code, state);
            alert("OAuth integration successful!");

            // Clear stored state
            localStorage.removeItem("oauth_state");

            // Reload integrations
            await this.loadIntegrations();
          } catch (error) {
            console.error("OAuth callback failed:", error);
            alert("OAuth callback failed: " + error.message);
          }
        }
      }

      // Initialize the app
      const app = new GoogleOAuthApp();

      // Handle OAuth callback if we're on the callback page
      if (window.location.pathname === "/oauth/callback") {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get("code");
        const state = urlParams.get("state");

        if (code && state) {
          app.handleCallback(code, state);
        }
      }
    </script>
  </body>
</html>
```

## Python Implementation

```python
import requests
import json
from typing import List, Dict, Optional

class GoogleOAuthService:
    def __init__(self, access_token: str):
        self.base_url = 'https://api.personalassistant.com/api/v1/oauth'
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_providers(self) -> Dict:
        """Get available OAuth providers."""
        response = requests.get(
            f'{self.base_url}/providers',
            headers=self.headers
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def initiate_oauth(self, provider: str, scopes: List[str], redirect_uri: str) -> Dict:
        """Initiate OAuth flow with a provider."""
        data = {
            'provider': provider,
            'scopes': scopes,
            'redirect_uri': redirect_uri
        }

        response = requests.post(
            f'{self.base_url}/initiate',
            headers=self.headers,
            json=data
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def handle_callback(self, code: str, state: str) -> Dict:
        """Handle OAuth callback."""
        data = {
            'code': code,
            'state': state
        }

        response = requests.post(
            f'{self.base_url}/callback',
            headers=self.headers,
            json=data
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def get_integrations(self) -> Dict:
        """Get user's OAuth integrations."""
        response = requests.get(
            f'{self.base_url}/integrations',
            headers=self.headers
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def refresh_token(self, integration_id: str) -> Dict:
        """Refresh OAuth token."""
        response = requests.post(
            f'{self.base_url}/integrations/{integration_id}/refresh',
            headers=self.headers
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def revoke_integration(self, integration_id: str) -> Dict:
        """Revoke OAuth integration."""
        response = requests.delete(
            f'{self.base_url}/integrations/{integration_id}',
            headers=self.headers
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

# Usage example
def demonstrate_google_oauth():
    oauth_service = GoogleOAuthService('your_access_token')

    try:
        # 1. Get available providers
        print("Getting OAuth providers...")
        providers = oauth_service.get_providers()
        print(f"Available providers: {[p['name'] for p in providers['providers']]}")

        # 2. Initiate Google OAuth
        print("Initiating Google OAuth...")
        oauth_init = oauth_service.initiate_oauth(
            'google',
            [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/calendar.readonly'
            ],
            'https://yourapp.com/oauth/callback'
        )
        print(f"Authorization URL: {oauth_init['authorization_url']}")

        # 3. Handle callback (simulated)
        print("Handling OAuth callback...")
        callback_result = oauth_service.handle_callback(
            'authorization_code_from_google',
            oauth_init['state']
        )
        print(f"Integration created: {callback_result['integration_id']}")

        # 4. Get integrations
        print("Getting user integrations...")
        integrations = oauth_service.get_integrations()
        print(f"Total integrations: {integrations['total']}")

        # 5. Refresh token
        if integrations['integrations']:
            integration_id = integrations['integrations'][0]['id']
            print(f"Refreshing token for integration {integration_id}...")
            refresh_result = oauth_service.refresh_token(integration_id)
            print("Token refreshed successfully")

    except Exception as e:
        print(f"OAuth flow failed: {e}")

if __name__ == "__main__":
    demonstrate_google_oauth()
```

## Error Handling

### Common OAuth Errors

```javascript
function handleOAuthError(error, response) {
  switch (response.status) {
    case 400:
      console.error("Bad Request:", error.detail);
      // Invalid provider or scopes
      break;
    case 401:
      console.error("Unauthorized:", error.detail);
      // Token expired or invalid
      break;
    case 403:
      console.error("Forbidden:", error.detail);
      // Insufficient permissions
      break;
    case 404:
      console.error("Not Found:", error.detail);
      // Provider not found
      break;
    case 409:
      console.error("Conflict:", error.detail);
      // Integration already exists
      break;
    case 500:
      console.error("Server Error:", error.detail);
      // Internal server error
      break;
    default:
      console.error("Unknown Error:", error.detail);
  }
}
```

## Best Practices

### Security Considerations

1. **Validate state parameter**: Always verify the state parameter in callbacks
2. **Store tokens securely**: Use secure storage for OAuth tokens
3. **Handle token expiration**: Implement automatic token refresh
4. **Validate scopes**: Only request necessary scopes

### User Experience

1. **Clear permissions**: Explain what permissions you're requesting
2. **Handle errors gracefully**: Show user-friendly error messages
3. **Provide status updates**: Show integration status clearly
4. **Allow easy revocation**: Make it easy to disconnect services

### Performance Optimization

1. **Cache provider info**: Store provider information locally
2. **Implement retry logic**: Handle network failures gracefully
3. **Use WebSocket**: For real-time integration updates
4. **Optimize token refresh**: Implement smart token refresh strategies
