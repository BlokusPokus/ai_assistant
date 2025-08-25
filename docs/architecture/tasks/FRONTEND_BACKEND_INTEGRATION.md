# 🔗 Frontend-Backend Integration Guide

## 📋 **Document Overview**

**Purpose**: Comprehensive guide for frontend-backend integration, ensuring consistent API structure and data flow  
**Audience**: Frontend and Backend Developers  
**Last Updated**: December 2024  
**Status**: ✅ **ACTIVE AND TESTED**

This document serves as the single source of truth for all API contracts, data structures, and integration patterns between the React frontend and FastAPI backend.

---

## 🏗️ **System Architecture Overview**

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   React Frontend │ ◄──────────────► │  FastAPI Backend │
│   (Port 3000)   │                  │   (Port 8000)   │
└─────────────────┘                  └─────────────────┘
         │                                     │
         │                                     │
         ▼                                     ▼
┌─────────────────┐                  ┌─────────────────┐
│   Vite Dev      │                  │  PostgreSQL     │
│   Proxy         │                  │  Database       │
└─────────────────┘                  └─────────────────┘
```

### **Key Integration Points**

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Communication**: REST API with JWT authentication
- **Proxy**: Vite dev server proxies `/api/*` to backend

---

## 🔐 **Authentication Flow & API Contracts**

### **1. User Registration**

#### **Frontend Request**

```typescript
// POST /api/v1/auth/register
interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

// Frontend call
const response = await authService.register({
  email: "user@example.com",
  password: "Password123!",
  full_name: "John Doe",
});
```

#### **Backend Response**

```python
# Response Model: UserResponse
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: str

# Backend returns
{
    "id": 127,
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-08-22T16:37:30.698819"
}
```

#### **Frontend Handling**

```typescript
// After successful registration
const handleRegistrationSuccess = () => {
  setRegistrationSuccess(true);
  // Auto-switch to login after 2 seconds
  setTimeout(() => {
    setAuthMode("login");
    setRegistrationSuccess(false);
  }, 2000);
};
```

### **2. User Login**

#### **Frontend Request**

```typescript
// POST /api/v1/auth/login
interface LoginRequest {
  email: string;
  password: string;
}

// Frontend call
const response = await authService.login({
  email: "user@example.com",
  password: "Password123!",
});
```

#### **Backend Response**

```python
# Response Model: AuthResponse
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    mfa_required: bool = False
    mfa_setup_required: bool = False

# Backend returns
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
        "id": 127,
        "email": "user@example.com",
        "full_name": "John Doe",
        "created_at": "2025-08-22T16:37:30.698819"
    },
    "mfa_required": false,
    "mfa_setup_required": false
}
```

#### **Frontend Token Storage**

```typescript
// Auth service stores tokens
storeAuthData(authData: AuthResponse): void {
  localStorage.setItem('access_token', authData.access_token);
  localStorage.setItem('refresh_token', authData.refresh_token);
  localStorage.setItem('user', JSON.stringify(authData.user));
}

// Auth store updates state
set({
  user: authData.user,
  isAuthenticated: true,
  isLoading: false,
  mfaRequired: authData.mfa_required,
  mfaSetupRequired: authData.mfa_setup_required,
  error: null,
});
```

### **3. JWT Token Structure**

#### **Access Token Payload**

```json
{
  "sub": "user@example.com",
  "user_id": 127,
  "email": "user@example.com",
  "full_name": "John Doe",
  "type": "access",
  "exp": 1755881602
}
```

#### **Refresh Token Payload**

```json
{
  "sub": "user@example.com",
  "user_id": 127,
  "email": "user@example.com",
  "full_name": "John Doe",
  "type": "refresh",
  "exp": 1756485502
}
```

### **4. Protected API Calls**

#### **Frontend API Client Setup**

```typescript
// src/services/api.ts
const api: AxiosInstance = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor adds JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor handles 401 errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
```

#### **Backend Authentication Middleware**

```python
# src/apps/fastapi_app/middleware/auth.py
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: Optional[list] = None):
        self.exclude_paths = exclude_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/webhook/twilio",
            "/twilio/sms",
        ]

    async def dispatch(self, request: Request, call_next):
        if self._should_exclude_path(request.url.path):
            return await call_next(request)

        token = self._extract_token(request)
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        try:
            # Validate token and get user context
            payload = jwt_service.verify_access_token(token)
            user_id = AuthUtils.get_user_id_from_token(payload)
            email = AuthUtils.get_user_email_from_token(payload)
            full_name = payload.get("full_name")

            # Inject user context into request state
            request.state.user_id = user_id
            request.state.user_email = email
            request.state.user_full_name = full_name
            request.state.authenticated = True

            return await call_next(request)
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication failed"},
                headers={"WWW-Authenticate": "Bearer"}
            )
```

---

## 📡 **API Endpoints & Data Contracts**

### **Authentication Endpoints**

| Endpoint                       | Method | Frontend Call                  | Backend Response    | Status         |
| ------------------------------ | ------ | ------------------------------ | ------------------- | -------------- |
| `/api/v1/auth/register`        | POST   | `authService.register()`       | `UserResponse`      | ✅ **Working** |
| `/api/v1/auth/login`           | POST   | `authService.login()`          | `AuthResponse`      | ✅ **Working** |
| `/api/v1/auth/logout`          | POST   | `authService.logout()`         | `{message: string}` | ✅ **Working** |
| `/api/v1/auth/refresh`         | POST   | `authService.refreshToken()`   | `TokenResponse`     | ✅ **Working** |
| `/api/v1/auth/forgot-password` | POST   | `authService.forgotPassword()` | `{message: string}` | ✅ **Working** |
| `/api/v1/auth/reset-password`  | POST   | `authService.resetPassword()`  | `{message: string}` | ✅ **Working** |

### **User Management Endpoints**

| Endpoint                       | Method | Frontend Call                     | Backend Response          | Status         |
| ------------------------------ | ------ | --------------------------------- | ------------------------- | -------------- |
| `/api/v1/users/me`             | GET    | `authService.getCurrentUser()`    | `UserResponse`            | ✅ **Working** |
| `/api/v1/users/me`             | PUT    | `authService.updateProfile()`     | `UserResponse`            | 🔄 **Ready**   |
| `/api/v1/users/me/preferences` | GET    | `userService.getPreferences()`    | `UserPreferencesResponse` | 🔄 **Ready**   |
| `/api/v1/users/me/preferences` | PUT    | `userService.updatePreferences()` | `UserPreferencesResponse` | ✅ **Working** |

### **MFA Endpoints**

| Endpoint             | Method | Frontend Call            | Backend Response     | Status         |
| -------------------- | ------ | ------------------------ | -------------------- | -------------- |
| `/api/v1/mfa/setup`  | POST   | `mfaService.setupMFA()`  | `MFASetupResponse`   | ✅ **Working** |
| `/api/v1/mfa/verify` | POST   | `mfaService.verifyMFA()` | `{success: boolean}` | ✅ **Working** |

### **OAuth Endpoints**

| Endpoint                                  | Method | Frontend Call                      | Backend Response             | Status         |
| ----------------------------------------- | ------ | ---------------------------------- | ---------------------------- | -------------- |
| `/api/v1/oauth/providers`                 | GET    | `oauthService.getProviders()`      | `OAuthProviderInfo[]`        | ✅ **Working** |
| `/api/v1/oauth/initiate`                  | POST   | `oauthService.initiateFlow()`      | `OAuthInitiateResponse`      | ✅ **Working** |
| `/api/v1/oauth/callback`                  | GET    | OAuth provider redirect            | `{message, integration_id}`  | ✅ **Working** |
| `/api/v1/oauth/integrations`              | GET    | `oauthService.getIntegrations()`   | `OAuthIntegrationResponse[]` | ✅ **Working** |
| `/api/v1/oauth/integrations/{id}/refresh` | POST   | `oauthService.refreshTokens()`     | `{message: string}`          | ✅ **Working** |
| `/api/v1/oauth/integrations/{id}`         | DELETE | `oauthService.revokeIntegration()` | `{message: string}`          | ✅ **Working** |
| `/api/v1/oauth/integrations/sync`         | POST   | `oauthService.syncIntegrations()`  | `{message, results}`         | ✅ **Working** |
| `/api/v1/oauth/status`                    | GET    | `oauthService.getStatus()`         | `{integrations, consents}`   | ✅ **Working** |

---

## 🔐 **OAuth Data Contracts**

### **1. OAuth Provider Information**

#### **Frontend Request**

```typescript
// GET /api/v1/oauth/providers
// No request body needed - just authentication header
```

#### **Backend Response**

```python
# Response Model: OAuthProviderInfo[]
class OAuthProviderInfo(BaseModel):
    name: str                    # "google", "microsoft", "notion", "youtube"
    display_name: str            # "Google", "Microsoft", "Notion", "YouTube"
    description: str             # Provider description
    scopes: List[dict]          # Available scopes for this provider

# Backend returns
[
    {
        "name": "google",
        "display_name": "Google",
        "description": "Google services including Calendar, Drive, and Gmail",
        "scopes": [
            {"name": "calendar.readonly", "description": "Read calendar events"},
            {"name": "drive.readonly", "description": "Read Google Drive files"}
        ]
    },
    {
        "name": "microsoft",
        "display_name": "Microsoft",
        "description": "Microsoft 365 services including Outlook and OneDrive",
        "scopes": [
            {"name": "Calendars.Read", "description": "Read calendar events"},
            {"name": "Files.Read", "description": "Read OneDrive files"}
        ]
    }
]
```

### **2. OAuth Flow Initiation**

#### **Frontend Request**

```typescript
// POST /api/v1/oauth/initiate
interface OAuthInitiateRequest {
  provider: string;           # "google", "microsoft", "notion", "youtube"
  scopes: string[];           # ["calendar.readonly", "drive.readonly"]
  redirect_uri?: string;      # Optional custom redirect URI
}

# Frontend call
const response = await oauthService.initiateFlow({
  provider: "google",
  scopes: ["calendar.readonly", "drive.readonly"]
});
```

#### **Backend Response**

```python
# Response Model: OAuthInitiateResponse
class OAuthInitiateResponse(BaseModel):
    authorization_url: str     # OAuth provider authorization URL
    state_token: str          # CSRF protection token
    provider: str             # Provider name
    scopes: List[str]         # Requested scopes

# Backend returns
{
    "authorization_url": "https://accounts.google.com/oauth/authorize?...",
    "state_token": "abc123def456",
    "provider": "google",
    "scopes": ["calendar.readonly", "drive.readonly"]
}
```

### **3. OAuth Integration Management**

#### **Frontend Request (Get Integrations)**

```typescript
# GET /api/v1/oauth/integrations?provider=google&active_only=true
const integrations = await oauthService.getIntegrations({
  provider: "google",
  active_only: true
});
```

#### **Backend Response**

```python
# Response Model: OAuthIntegrationResponse[]
class OAuthIntegrationResponse(BaseModel):
    id: int                   # Integration ID
    provider: str             # Provider name
    status: str               # "active", "expired", "revoked"
    is_active: bool           # Active status
    scopes: List[str]         # Granted scopes
    created_at: str           # ISO timestamp
    last_sync_at: Optional[str] # Last sync timestamp
    metadata: Optional[dict]  # Provider-specific metadata

# Backend returns
[
    {
        "id": 1,
        "provider": "google",
        "status": "active",
        "is_active": true,
        "scopes": ["calendar.readonly", "drive.readonly"],
        "created_at": "2025-01-15T10:30:00Z",
        "last_sync_at": "2025-01-15T14:45:00Z",
        "metadata": {"user_email": "user@gmail.com"}
    }
]
```

### **4. OAuth Status Summary**

#### **Frontend Request**

```typescript
# GET /api/v1/oauth/status
const status = await oauthService.getStatus();
```

#### **Backend Response**

```python
# Response includes integration and consent summaries
{
    "integrations": {
        "google": {"count": 1, "active": 1, "expired": 0},
        "microsoft": {"count": 0, "active": 0, "expired": 0},
        "notion": {"count": 1, "active": 1, "expired": 0},
        "youtube": {"count": 0, "active": 0, "expired": 0}
    },
    "consents": {
        "total_consents": 2,
        "active_consents": 2,
        "expired_consents": 0
    }
}
```

---

## 🔄 **Data Flow Patterns**

### **1. Authentication Flow**

```
User Input → Frontend Validation → API Call → Backend Processing → Response → State Update → UI Update
```

#### **Detailed Flow Example (Login)**

1. **User Input**: User enters email/password
2. **Frontend Validation**: React Hook Form validates input
3. **API Call**: `authService.login(credentials)` called
4. **Backend Processing**: FastAPI validates credentials, generates JWT
5. **Response**: `AuthResponse` with tokens and user data
6. **State Update**: Zustand store updates `isAuthenticated: true`
7. **UI Update**: Redirect to dashboard, show user info

### **2. Protected Route Flow**

```
Route Access → Auth Check → Token Validation → User Context → Protected Content
```

#### **Detailed Flow Example (Dashboard)**

1. **Route Access**: User navigates to `/dashboard`
2. **Auth Check**: `ProtectedRoute` checks `isAuthenticated`
3. **Token Validation**: Backend validates JWT in `/users/me` call
4. **User Context**: User data loaded and stored in state
5. **Protected Content**: Dashboard renders with user information

### **3. Error Handling Flow**

```
Error Occurs → Backend Response → Frontend Interceptor → State Update → UI Feedback
```

### **4. OAuth Flow**

```
User Initiates → Frontend OAuth Request → Backend OAuth Service → Provider Redirect → User Authorization → Callback → Integration Creation → UI Update
```

#### **Detailed Flow Example (Google OAuth)**

1. **User Initiates**: User clicks "Connect Google" button
2. **Frontend OAuth Request**: `oauthService.initiateFlow({provider: "google", scopes: ["calendar.readonly"]})`
3. **Backend OAuth Service**: Creates state token, generates authorization URL
4. **Provider Redirect**: User redirected to Google OAuth page
5. **User Authorization**: User grants permissions on Google
6. **Callback**: Google redirects back to `/api/v1/oauth/callback`
7. **Integration Creation**: Backend creates OAuth integration record
8. **UI Update**: Frontend shows connected status, enables calendar features

#### **Detailed Flow Example (401 Unauthorized)**

1. **Error Occurs**: JWT token expired or invalid
2. **Backend Response**: Returns 401 status
3. **Frontend Interceptor**: Axios interceptor catches 401
4. **State Update**: Clears auth tokens and user data
5. **UI Feedback**: Redirects to login page

---

## 🛠️ **Development & Testing**

### **Frontend Development Commands**

```bash
# Start development server
cd src/apps/frontend
npm run dev

# Run tests
npm run test:run

# Build for production
npm run build
```

### **Backend Development Commands**

```bash
# Activate virtual environment
source venv_personal_assistant/bin/activate

# Start FastAPI server
cd src
uvicorn apps.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000

# Run database tests
python -c "import asyncio; from personal_assistant.database.session import AsyncSessionLocal; ..."
```

### **Integration Testing**

```bash
# Test registration
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "Password123!", "full_name": "Test User"}'

# Test login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "Password123!"}'

# Test protected endpoint
curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔧 **Configuration & Environment**

### **Frontend Environment Variables**

```typescript
// src/apps/frontend/.env
VITE_API_BASE_URL=/api/v1
VITE_APP_NAME="Personal Assistant TDAH"
VITE_APP_VERSION=1.0.0
```

### **Backend Environment Variables**

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/personal_assistant
JWT_SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
DEBUG=true
```

### **Vite Proxy Configuration**

```typescript
// src/apps/frontend/vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      // Don't rewrite the path - keep /api prefix for backend
    },
  },
},
```

---

## 🚨 **Common Issues & Solutions**

### **1. CORS Errors**

**Problem**: Frontend can't call backend due to CORS
**Solution**: Backend CORS middleware configured correctly

```python
# Backend CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **2. JWT Token Issues**

**Problem**: "Invalid token: missing user information"
**Solution**: JWT tokens now include complete user data

```python
# Backend JWT creation
access_token = jwt_service.create_access_token(
    data={
        "sub": user.email,
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }
)
```

### **3. API Endpoint Mismatch**

**Problem**: Frontend calls `/v1/auth/login` but backend expects `/api/v1/auth/login`
**Solution**: Vite proxy configuration fixed to maintain `/api` prefix

### **4. Permission Denied Errors**

**Problem**: `@require_permission("user", "read")` fails for new users
**Solution**: Temporarily removed permission requirements for basic endpoints
**Future**: Implement default role assignment during user registration

---

## 📊 **Performance & Monitoring**

### **Frontend Performance Metrics**

- **Bundle Size**: < 2MB gzipped
- **Initial Load**: < 3 seconds
- **Time to Interactive**: < 5 seconds
- **Lighthouse Score**: > 90

### **Backend Performance Metrics**

- **API Response Time**: < 200ms P95
- **Database Query Time**: < 100ms P95
- **JWT Validation**: < 50ms
- **Concurrent Users**: Support for 100+ users

### **Monitoring Endpoints**

```bash
# Health check
GET /health

# Metrics (when implemented)
GET /metrics

# API documentation
GET /docs
GET /redoc
```

---

## 🔮 **Future Enhancements**

### **Immediate (Phase 2.5)**

- [ ] **Enhanced Dashboard**: User profile management, settings
- [ ] **SMS Router Service**: Individual Twilio numbers per user
- [ ] **MFA Implementation**: TOTP and SMS verification

### **Short Term (Phase 2.6-2.7)**

- [ ] **Real-time Updates**: WebSocket integration
- [ ] **File Upload**: Document and image management
- [ ] **Advanced RBAC**: Resource-level permissions

### **Long Term (Phase 2.8+)**

- [ ] **PWA Features**: Offline support, push notifications
- [ ] **Social Auth**: OAuth integration
- [ ] **Multi-language**: Internationalization support

---

## 📚 **Additional Resources**

### **Frontend Documentation**

- **React 18**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/
- **Vite**: https://vitejs.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **Zustand**: https://github.com/pmndrs/zustand

### **Backend Documentation**

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Redis**: https://redis.io/documentation

### **Integration Resources**

- **JWT**: https://jwt.io/
- **REST API**: https://restfulapi.net/
- **HTTP Status Codes**: https://httpstatuses.com/

---

## 📞 **Support & Contact**

### **Development Team**

- **Frontend Lead**: [Your Name]
- **Backend Lead**: [Your Name]
- **DevOps Lead**: [Your Name]

### **Issue Reporting**

- **Frontend Issues**: GitHub Issues (Frontend Repository)
- **Backend Issues**: GitHub Issues (Backend Repository)
- **Integration Issues**: GitHub Issues (Main Repository)

### **Documentation Updates**

This document should be updated whenever:

- New API endpoints are added
- Data structures change
- Integration patterns are modified
- New authentication flows are implemented

**Last Updated**: December 2024  
**Next Review**: January 2025  
**Version**: 1.0
