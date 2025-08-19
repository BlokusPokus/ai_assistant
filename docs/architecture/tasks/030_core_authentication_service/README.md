# 🚀 Task 030: Core Authentication Service Implementation

## **📋 Task Overview**

**Task ID**: 030  
**Task Name**: Core Authentication Service Implementation  
**Phase**: 2.1 - Authentication System  
**Priority**: 🔴 CRITICAL PATH  
**Status**: 🔴 Not Started  
**Estimated Effort**: 5 days  
**Dependencies**: None

## **🎯 Objective**

Implement the foundational authentication system for the Personal Assistant TDAH platform, enabling secure multi-user access through JWT tokens, authentication middleware, and proper user management. This is a critical prerequisite for Phase 2.5 (Multi-User Architecture) and the SMS Router Service.

## **🏗️ Architecture Context**

Based on the MAE (Multi-Agent Environment) and MAS (Multi-Agent System) architecture:

- **Current State**: Single-user MVP with basic FastAPI structure
- **Target State**: Multi-user enterprise system with JWT authentication
- **Integration Points**: FastAPI backend, PostgreSQL database, Redis cache
- **Security Requirements**: MFA support, RBAC foundation, secure session management

## **📊 Current Codebase Analysis**

### **✅ What Exists**

- Basic FastAPI application structure (`src/apps/fastapi_app/`)
- PostgreSQL database with basic user models (`src/personal_assistant/database/models/`) \*models might not be up to date, look at @MAS for the right datatables
- Configuration system (`src/personal_assistant/config/settings.py`)
- Basic database session management
- Twilio integration for SMS

### **❌ What's Missing**

- JWT token generation and validation
- Authentication middleware
- User authentication endpoints (login/register)
- Password hashing and security
- Session management
- Authentication configuration in settings

## **🎯 Deliverables**

### **1. JWT Token Management Service**

- **File**: `src/personal_assistant/auth/jwt_service.py`
- **Features**:
  - JWT token generation with configurable expiration
  - Token validation and refresh mechanism
  - Secure secret management via environment variables
  - Token blacklisting support

### **2. Authentication Middleware**

- **File**: `src/apps/fastapi_app/middleware/auth.py`
- **Features**:
  - JWT token validation
  - User context injection into requests
  - Unauthorized request handling (401 responses)
  - Rate limiting integration

### **3. User Authentication Endpoints**

- **File**: `src/apps/fastapi_app/routes/auth.py`
- **Features**:
  - User registration with validation
  - User login with JWT token generation
  - Password reset functionality
  - Logout with token invalidation

### **4. Enhanced User Models**

- **File**: `src/personal_assistant/database/models/users.py`
- **Features**:
  - Password hashing with bcrypt
  - Email verification fields
  - Account status management
  - Last login tracking

### **5. Authentication Configuration**

- **File**: `src/personal_assistant/config/settings.py`
- **Features**:
  - JWT secret configuration
  - Token expiration settings
  - MFA configuration flags
  - Security policy settings

## **🔧 Technical Implementation Details**

### **JWT Service Architecture**

```python
class JWTAuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256")
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str
    def create_refresh_token(self, data: dict) -> str
    def verify_token(self, token: str) -> Optional[dict]
    def refresh_access_token(self, refresh_token: str) -> Optional[str]
```

### **Authentication Middleware**

```python
class AuthMiddleware:
    def __init__(self, jwt_service: JWTAuthService)
    async def __call__(self, request: Request, call_next)
    def extract_token(self, request: Request) -> Optional[str]
    def validate_user_context(self, user_data: dict) -> bool
```

### **Database Schema Updates**

```sql
-- Enhanced users table
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL;
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN account_status VARCHAR(20) DEFAULT 'active';
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN locked_until TIMESTAMP;

-- Enhanced auth_tokens table
ALTER TABLE auth_tokens ADD COLUMN token_type VARCHAR(20) NOT NULL;
ALTER TABLE auth_tokens ADD COLUMN is_revoked BOOLEAN DEFAULT FALSE;
ALTER TABLE auth_tokens ADD COLUMN ip_address VARCHAR(45);
ALTER TABLE auth_tokens ADD COLUMN user_agent TEXT;
```

## **🔐 Security Requirements**

### **Password Security**

- **Hashing**: bcrypt with salt rounds ≥ 12
- **Validation**: Minimum 8 characters, complexity requirements
- **Storage**: Never store plain text passwords

### **Token Security**

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: Access tokens (15 min), Refresh tokens (7 days)
- **Storage**: Secure HTTP-only cookies or Authorization header
- **Rotation**: Automatic refresh token rotation

### **Rate Limiting**

- **Login attempts**: Max 5 per 15 minutes per IP
- **Token refresh**: Max 10 per hour per user
- **Registration**: Max 3 per hour per IP

## **🧪 Testing Requirements**

### **Unit Tests (90% Coverage)**

- JWT service token generation/validation
- Password hashing and verification
- Authentication middleware logic
- User authentication flows

### **Integration Tests**

- End-to-end authentication flows
- Database integration
- Middleware integration with FastAPI
- Error handling scenarios

### **Security Tests**

- Token tampering resistance
- Password brute force protection
- Session hijacking prevention
- SQL injection protection

## **📁 File Structure**

```
src/
├── personal_assistant/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt_service.py
│   │   ├── password_service.py
│   │   └── auth_utils.py
│   └── config/
│       └── settings.py (enhanced)
├── apps/
│   └── fastapi_app/
│       ├── middleware/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── rate_limiting.py
│       ├── routes/
│       │   ├── auth.py
│       │   └── users.py
│       └── dependencies/
│           └── auth_deps.py
└── tests/
    ├── test_auth/
    │   ├── test_jwt_service.py
    │   ├── test_auth_middleware.py
    │   └── test_auth_endpoints.py
    └── conftest.py
```

## **🚀 Implementation Steps**

### **Phase 1: Core JWT Service (Day 1-2)**

1. Create JWT service with token generation/validation
2. Implement password hashing service
3. Add authentication configuration to settings
4. Write unit tests for JWT service

### **Phase 2: Authentication Middleware (Day 3)**

1. Implement authentication middleware
2. Integrate with FastAPI dependency injection
3. Add user context injection
4. Test middleware integration

### **Phase 3: Authentication Endpoints (Day 4)**

1. Create user registration endpoint
2. Implement login/logout endpoints
3. Add password reset functionality
4. Integrate with existing user models

### **Phase 4: Testing & Integration (Day 5)**

1. Complete unit test coverage
2. Integration testing with FastAPI
3. Security testing and validation
4. Documentation and code review

## **🔗 Dependencies & Integration**

### **External Dependencies**

- `PyJWT` for JWT token handling
- `bcrypt` for password hashing
- `python-multipart` for form data handling
- `redis` for token blacklisting (optional)

### **Internal Dependencies**

- Existing database models and session management
- FastAPI application structure
- Configuration system
- Logging infrastructure

### **Future Integration Points**

- MFA service (Phase 2.1.3)
- RBAC system (Phase 2.1.2)
- SMS Router Service (Phase 2.5.3)
- User management API (Phase 2.3.1)

## **📊 Success Metrics**

### **Functional Requirements**

- ✅ JWT tokens generated and validated correctly
- ✅ Authentication middleware blocks unauthorized requests
- ✅ User registration and login work end-to-end
- ✅ Password security meets industry standards
- ✅ Rate limiting prevents abuse

### **Performance Requirements**

- Token validation: < 10ms response time
- Login endpoint: < 100ms response time
- Middleware overhead: < 5ms per request
- Database queries: Optimized with proper indexing

### **Security Requirements**

- Zero critical security vulnerabilities
- Passes OWASP security guidelines
- Secure password storage and transmission
- Protection against common attack vectors

## **⚠️ Risk Mitigation**

### **Technical Risks**

- **JWT Secret Management**: Use environment variables, never hardcode
- **Password Security**: Implement proper hashing with bcrypt
- **Token Expiration**: Implement automatic cleanup of expired tokens
- **Database Security**: Use parameterized queries, validate all inputs

### **Integration Risks**

- **FastAPI Compatibility**: Test with current FastAPI version
- **Database Migration**: Backup existing data before schema changes
- **Backward Compatibility**: Maintain existing API endpoints during transition
- **Performance Impact**: Monitor middleware performance overhead

## **📚 Resources & References**

### **Documentation**

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

### **Code Examples**

- FastAPI authentication examples
- JWT implementation patterns
- Password hashing best practices
- Middleware implementation patterns

## **🎯 Next Steps After Completion**

1. **Phase 2.1.2**: Implement RBAC system
2. **Phase 2.1.3**: Add MFA support
3. **Phase 2.2**: Infrastructure and database optimization
4. **Phase 2.5.3**: SMS Router Service implementation

## **📝 Notes**

- This task is on the critical path for multi-user functionality
- Authentication system must be production-ready and secure
- Consider future MFA and RBAC requirements during design
- Maintain compatibility with existing Twilio SMS integration
- Follow security best practices and industry standards

---

**Created**: December 2024  
**Last Updated**: December 2024  
**Assigned To**: [Developer Name]  
**Reviewer**: [Reviewer Name]
