# Authentication Examples

This example demonstrates the complete user authentication flow, including registration, login, token management, and logout.

## Overview

The authentication flow involves:

1. User registration with email verification
2. User login with credentials
3. Token refresh when needed
4. Secure logout

## Prerequisites

- API endpoint accessible
- Valid email address for testing
- SMTP configured for email verification

## Step 1: User Registration

### Register a new user

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
  }'
```

**Expected Response:**

```json
{
  "message": "User registered successfully. Please check your email for verification.",
  "user_id": 123,
  "email": "john.doe@example.com",
  "verification_required": true
}
```

### JavaScript Implementation

```javascript
async function registerUser(userData) {
  const response = await fetch(
    "https://api.personalassistant.com/api/v1/auth/register",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: userData.email,
        password: userData.password,
        first_name: userData.firstName,
        last_name: userData.lastName,
        phone_number: userData.phoneNumber,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}

// Usage
const userData = {
  email: "john.doe@example.com",
  password: "SecurePassword123!",
  firstName: "John",
  lastName: "Doe",
  phoneNumber: "+1234567890",
};

try {
  const result = await registerUser(userData);
  console.log("Registration successful:", result);
} catch (error) {
  console.error("Registration failed:", error.message);
}
```

### Python Implementation

```python
import requests

def register_user(user_data):
    response = requests.post(
        'https://api.personalassistant.com/api/v1/auth/register',
        json={
            'email': user_data['email'],
            'password': user_data['password'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'phone_number': user_data['phone_number']
        }
    )

    if not response.ok:
        error = response.json()
        raise Exception(error['detail'])

    return response.json()

# Usage
user_data = {
    'email': 'john.doe@example.com',
    'password': 'SecurePassword123!',
    'first_name': 'John',
    'last_name': 'Doe',
    'phone_number': '+1234567890'
}

try:
    result = register_user(user_data)
    print('Registration successful:', result)
except Exception as e:
    print('Registration failed:', str(e))
```

## Step 2: Email Verification

### Verify email address

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "verification_token_from_email"
  }'
```

**Expected Response:**

```json
{
  "message": "Email verified successfully",
  "user_id": 123,
  "email_verified": true
}
```

### Resend verification email

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/resend-verification" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com"
  }'
```

## Step 3: User Login

### Login with credentials

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true,
    "phone_verified": false,
    "mfa_enabled": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### JavaScript Implementation with Token Storage

```javascript
class AuthService {
  constructor() {
    this.baseURL = "https://api.personalassistant.com/api/v1/auth";
    this.tokens = this.loadTokens();
  }

  loadTokens() {
    const accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");
    return { accessToken, refreshToken };
  }

  saveTokens(accessToken, refreshToken) {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    this.tokens = { accessToken, refreshToken };
  }

  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    this.tokens = { accessToken: null, refreshToken: null };
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const data = await response.json();
    this.saveTokens(data.access_token, data.refresh_token);
    return data;
  }

  async refreshToken() {
    if (!this.tokens.refreshToken) {
      throw new Error("No refresh token available");
    }

    const response = await fetch(`${this.baseURL}/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.tokens.refreshToken}`,
      },
    });

    if (!response.ok) {
      this.clearTokens();
      throw new Error("Token refresh failed");
    }

    const data = await response.json();
    this.saveTokens(data.access_token, data.refresh_token);
    return data;
  }

  async logout() {
    if (this.tokens.accessToken) {
      try {
        await fetch(`${this.baseURL}/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.tokens.accessToken}`,
          },
        });
      } catch (error) {
        console.warn("Logout request failed:", error);
      }
    }
    this.clearTokens();
  }

  getAuthHeaders() {
    return {
      Authorization: `Bearer ${this.tokens.accessToken}`,
      "Content-Type": "application/json",
    };
  }
}

// Usage
const authService = new AuthService();

// Login
try {
  const loginResult = await authService.login(
    "john.doe@example.com",
    "SecurePassword123!"
  );
  console.log("Login successful:", loginResult);
} catch (error) {
  console.error("Login failed:", error.message);
}
```

## Step 4: Token Management

### Refresh access token

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <refresh_token>"
```

**Expected Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Get current user info

```bash
curl -X GET "https://api.personalassistant.com/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "id": 123,
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "email_verified": true,
  "phone_verified": false,
  "mfa_enabled": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Step 5: Password Management

### Request password reset

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com"
  }'
```

**Expected Response:**

```json
{
  "message": "Password reset email sent successfully"
}
```

### Reset password

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset_token_from_email",
    "new_password": "NewSecurePassword123!"
  }'
```

**Expected Response:**

```json
{
  "message": "Password reset successfully"
}
```

## Step 6: Logout

### Logout user

```bash
curl -X POST "https://api.personalassistant.com/api/v1/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "message": "Logged out successfully"
}
```

## Complete Authentication Flow Example

### JavaScript Complete Implementation

```javascript
class CompleteAuthFlow {
  constructor() {
    this.baseURL = "https://api.personalassistant.com/api/v1/auth";
    this.tokens = this.loadTokens();
  }

  loadTokens() {
    return {
      accessToken: localStorage.getItem("access_token"),
      refreshToken: localStorage.getItem("refresh_token"),
    };
  }

  saveTokens(accessToken, refreshToken) {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    this.tokens = { accessToken, refreshToken };
  }

  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    this.tokens = { accessToken: null, refreshToken: null };
  }

  async makeAuthenticatedRequest(url, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.tokens.accessToken) {
      headers["Authorization"] = `Bearer ${this.tokens.accessToken}`;
    }

    let response = await fetch(url, {
      ...options,
      headers,
    });

    // If token expired, try to refresh
    if (response.status === 401 && this.tokens.refreshToken) {
      try {
        await this.refreshToken();
        headers["Authorization"] = `Bearer ${this.tokens.accessToken}`;
        response = await fetch(url, {
          ...options,
          headers,
        });
      } catch (error) {
        this.clearTokens();
        throw new Error("Authentication failed");
      }
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Request failed");
    }

    return response;
  }

  async register(userData) {
    const response = await fetch(`${this.baseURL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async verifyEmail(token) {
    const response = await fetch(`${this.baseURL}/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const data = await response.json();
    this.saveTokens(data.access_token, data.refresh_token);
    return data;
  }

  async refreshToken() {
    if (!this.tokens.refreshToken) {
      throw new Error("No refresh token available");
    }

    const response = await fetch(`${this.baseURL}/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.tokens.refreshToken}`,
      },
    });

    if (!response.ok) {
      this.clearTokens();
      throw new Error("Token refresh failed");
    }

    const data = await response.json();
    this.saveTokens(data.access_token, data.refresh_token);
    return data;
  }

  async getCurrentUser() {
    const response = await this.makeAuthenticatedRequest(`${this.baseURL}/me`);
    return await response.json();
  }

  async logout() {
    if (this.tokens.accessToken) {
      try {
        await this.makeAuthenticatedRequest(`${this.baseURL}/logout`, {
          method: "POST",
        });
      } catch (error) {
        console.warn("Logout request failed:", error);
      }
    }
    this.clearTokens();
  }

  async forgotPassword(email) {
    const response = await fetch(`${this.baseURL}/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async resetPassword(token, newPassword) {
    const response = await fetch(`${this.baseURL}/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, new_password: newPassword }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  isAuthenticated() {
    return !!this.tokens.accessToken;
  }
}

// Usage Example
async function demonstrateAuthFlow() {
  const auth = new CompleteAuthFlow();

  try {
    // 1. Register user
    console.log("1. Registering user...");
    const registration = await auth.register({
      email: "john.doe@example.com",
      password: "SecurePassword123!",
      first_name: "John",
      last_name: "Doe",
      phone_number: "+1234567890",
    });
    console.log("Registration successful:", registration);

    // 2. Verify email (in real app, user would click link in email)
    console.log("2. Verifying email...");
    const verification = await auth.verifyEmail(
      "verification_token_from_email"
    );
    console.log("Email verified:", verification);

    // 3. Login
    console.log("3. Logging in...");
    const login = await auth.login(
      "john.doe@example.com",
      "SecurePassword123!"
    );
    console.log("Login successful:", login);

    // 4. Get current user
    console.log("4. Getting current user...");
    const user = await auth.getCurrentUser();
    console.log("Current user:", user);

    // 5. Make authenticated requests
    console.log("5. Making authenticated requests...");
    // Example: Get user sessions
    const sessionsResponse = await auth.makeAuthenticatedRequest(
      "https://api.personalassistant.com/api/v1/sessions/"
    );
    const sessions = await sessionsResponse.json();
    console.log("User sessions:", sessions);

    // 6. Logout
    console.log("6. Logging out...");
    await auth.logout();
    console.log("Logged out successfully");
  } catch (error) {
    console.error("Authentication flow failed:", error.message);
  }
}

// Run the demonstration
demonstrateAuthFlow();
```

## Error Handling

### Common Authentication Errors

```javascript
function handleAuthError(error, response) {
  switch (response.status) {
    case 400:
      console.error("Bad Request:", error.detail);
      break;
    case 401:
      console.error("Unauthorized:", error.detail);
      // Redirect to login
      break;
    case 403:
      console.error("Forbidden:", error.detail);
      break;
    case 409:
      console.error("Conflict:", error.detail);
      // User already exists
      break;
    case 422:
      console.error("Validation Error:", error.detail);
      break;
    case 429:
      console.error("Rate Limited:", error.detail);
      break;
    case 500:
      console.error("Server Error:", error.detail);
      break;
    default:
      console.error("Unknown Error:", error.detail);
  }
}
```

## Best Practices

### Security Considerations

1. **Store tokens securely**: Use secure storage mechanisms
2. **Implement token refresh**: Handle token expiration gracefully
3. **Validate input**: Sanitize all user inputs
4. **Use HTTPS**: Always use secure connections
5. **Handle errors**: Implement proper error handling

### Performance Optimization

1. **Cache tokens**: Store tokens in memory and localStorage
2. **Implement retry logic**: Handle network failures gracefully
3. **Use connection pooling**: Reuse HTTP connections
4. **Implement backoff**: Handle rate limiting appropriately

### User Experience

1. **Show loading states**: Provide feedback during operations
2. **Handle offline mode**: Gracefully handle network issues
3. **Implement auto-login**: Remember user sessions
4. **Provide clear error messages**: Help users understand issues
