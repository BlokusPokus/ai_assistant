# Task 067: Notion OAuth Frontend Integration

## 🎯 **Overview**

This task integrates the user-specific Notion system with the frontend OAuth infrastructure by implementing JWT token-based user identification, ensuring OAuth callback routes exist, and updating tool parameters to work seamlessly with the frontend authentication system.

## 📋 **Current State Analysis**

### **✅ What's Already Implemented**

1. **Complete OAuth System**: Full OAuth 2.0 implementation with Notion provider
2. **JWT Authentication**: JWT token generation, validation, and refresh system
3. **User-Specific Notion Tools**: Complete user-specific Notion implementation (Task 066)
4. **Frontend OAuth Flow**: Complete OAuth integration in React frontend
5. **OAuth Callback Routes**: Backend OAuth callback endpoints exist
6. **Session Management**: Redis-based session handling with user context

### **❌ What's Missing for Frontend Integration**

1. **JWT Token Integration**: Notion tools still expect `session_id` parameter instead of using JWT tokens
2. **User ID Extraction**: No mechanism to extract user ID from JWT tokens in Notion tools
3. **Tool Parameter Updates**: Notion tools require `session_id` parameter that frontend doesn't provide
4. **Frontend-Backend Bridge**: Missing integration between frontend JWT auth and backend Notion tools

## 🚀 **Proposed Solution**

### **Core Feature: JWT-Based User Identification for Notion Tools**

Transform the user-specific Notion system to work seamlessly with the frontend OAuth by:

1. **JWT Token Integration**: Extract user ID from JWT tokens instead of requiring `session_id`
2. **Tool Parameter Simplification**: Remove `session_id` requirement from Notion tools
3. **Frontend Compatibility**: Ensure tools work with frontend OAuth flow
4. **Error Handling**: Proper error handling for authentication failures

## 🏗️ **Architecture Context**

Based on the MAE (Multi-Agent Environment) and MAS (Multi-Agent System) architecture:

- **Current State**: User-specific Notion tools with session-based authentication
- **Target State**: JWT-based authentication compatible with frontend OAuth
- **Integration Points**: Frontend OAuth → JWT tokens → Notion tools → User-specific workspaces
- **Security Requirements**: JWT validation, user isolation, OAuth token management

## 📊 **Technical Requirements**

### **1. JWT Token Integration**

- **File**: `src/personal_assistant/tools/notion_pages/jwt_integration.py`
- **Purpose**: Extract user ID from JWT tokens for Notion operations
- **Features**:
  - JWT token validation and decoding
  - User ID extraction from token payload
  - Integration with existing JWT service
  - Error handling for invalid/expired tokens

### **2. Tool Parameter Updates**

- **Files**:
  - `src/personal_assistant/tools/notion_pages/notion_pages_tool_user_specific.py`
  - `src/personal_assistant/tools/notion_pages/notion_internal_user_specific.py`
- **Purpose**: Remove `session_id` parameter requirement
- **Features**:
  - Extract user ID from JWT token in request headers
  - Update tool parameters to remove `session_id`
  - Maintain backward compatibility where possible

### **3. OAuth Callback Route Verification**

- **File**: `src/apps/fastapi_app/routes/oauth.py`
- **Purpose**: Ensure OAuth callback routes work with frontend
- **Features**:
  - Verify `/oauth/callback/notion` route exists
  - Test OAuth flow integration
  - Ensure proper error handling

### **4. Frontend Integration Testing**

- **Purpose**: Verify complete OAuth flow works end-to-end
- **Features**:
  - Test Notion OAuth connection from frontend
  - Verify user-specific workspace creation
  - Test Notion tool operations through frontend

## 🎯 **Deliverables**

### **Phase 1: JWT Integration Service** (2 days)

1. **JWT Integration Service**

   - Create `jwt_integration.py` for user ID extraction
   - Integrate with existing `JWTService`
   - Add proper error handling and validation

2. **Unit Tests**
   - Test JWT token extraction
   - Test error handling scenarios
   - Test integration with existing services

### **Phase 2: Tool Parameter Updates** (2 days)

1. **Update Notion Tools**

   - Remove `session_id` parameter from all tools
   - Implement JWT-based user identification
   - Update tool descriptions and parameters

2. **Update Internal Functions**

   - Modify `notion_internal_user_specific.py`
   - Update user identification logic
   - Maintain existing functionality

3. **Integration Tests**
   - Test tool operations with JWT tokens
   - Verify user isolation still works
   - Test error handling

### **Phase 3: OAuth Route Verification** (1 day)

1. **Route Verification**

   - Verify OAuth callback routes exist
   - Test OAuth flow integration
   - Ensure proper error handling

2. **End-to-End Testing**
   - Test complete OAuth flow
   - Verify frontend-backend integration
   - Test user-specific workspace creation

## 📋 **Implementation Checklist**

### **Phase 1: JWT Integration Service** ⏳

#### **1.1 JWT Integration Service** ⏳

- [ ] **Create JWT Integration Service**

  - [ ] Create `src/personal_assistant/tools/notion_pages/jwt_integration.py`
  - [ ] Implement `extract_user_id_from_jwt()` function
  - [ ] Integrate with existing `JWTService`
  - [ ] Add proper error handling

- [ ] **Unit Tests**
  - [ ] Test JWT token extraction
  - [ ] Test invalid token handling
  - [ ] Test expired token handling
  - [ ] Test missing token handling

#### **1.2 Integration with Existing Services** ⏳

- [ ] **JWT Service Integration**
  - [ ] Import and use existing `JWTService`
  - [ ] Use existing token validation logic
  - [ ] Maintain consistency with auth system

### **Phase 2: Tool Parameter Updates** ⏳

#### **2.1 Update Notion Tools** ⏳

- [ ] **Remove session_id Parameter**

  - [ ] Update `notion_pages_tool_user_specific.py`
  - [ ] Remove `session_id` from all tool parameters
  - [ ] Update tool descriptions

- [ ] **Implement JWT-Based User ID Extraction**
  - [ ] Add JWT token extraction from request headers
  - [ ] Integrate with JWT integration service
  - [ ] Update user identification logic

#### **2.2 Update Internal Functions** ⏳

- [ ] **Update notion_internal_user_specific.py**

  - [ ] Remove `session_id` parameter from functions
  - [ ] Implement JWT-based user identification
  - [ ] Update function signatures

- [ ] **Update Client Factory and Workspace Manager**
  - [ ] Remove `session_id` parameters
  - [ ] Use JWT-based user identification
  - [ ] Maintain existing functionality

#### **2.3 Integration Tests** ⏳

- [ ] **Tool Operation Tests**

  - [ ] Test create_note_page with JWT token
  - [ ] Test read_note_page with JWT token
  - [ ] Test update_note_page with JWT token
  - [ ] Test delete_note_page with JWT token
  - [ ] Test search_note_pages with JWT token

- [ ] **User Isolation Tests**
  - [ ] Verify user isolation still works
  - [ ] Test multiple users with different tokens
  - [ ] Verify workspace separation

### **Phase 3: OAuth Route Verification** ⏳

#### **3.1 Route Verification** ⏳

- [ ] **OAuth Callback Route Check**

  - [ ] Verify `/oauth/callback/notion` route exists
  - [ ] Test route functionality
  - [ ] Verify error handling

- [ ] **OAuth Flow Integration**
  - [ ] Test complete OAuth flow
  - [ ] Verify token generation
  - [ ] Test integration with Notion tools

#### **3.2 End-to-End Testing** ⏳

- [ ] **Frontend Integration Tests**

  - [ ] Test Notion OAuth connection from frontend
  - [ ] Verify user-specific workspace creation
  - [ ] Test Notion tool operations through frontend

- [ ] **Error Handling Tests**
  - [ ] Test invalid OAuth tokens
  - [ ] Test expired tokens
  - [ ] Test missing authentication

## 🔧 **Technical Implementation Details**

### **JWT Integration Service**

```python
# src/personal_assistant/tools/notion_pages/jwt_integration.py
from fastapi import Request, HTTPException
from personal_assistant.auth.jwt_service import jwt_service
from personal_assistant.auth.auth_utils import AuthUtils

class NotionJWTIntegration:
    """JWT integration for Notion tools"""

    @staticmethod
    async def get_user_id_from_request(request: Request) -> int:
        """Extract user ID from JWT token in request headers"""
        token = AuthUtils.extract_token_from_header(request)
        if not token:
            raise HTTPException(status_code=401, detail="Authentication required")

        try:
            payload = jwt_service.verify_access_token(token)
            user_id = AuthUtils.get_user_id_from_token(payload)
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            return user_id
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail="Token validation failed")
```

### **Updated Tool Parameters**

```python
# Before (with session_id)
"session_id": {
    "type": "string",
    "description": "User session ID for authentication (required)",
}

# After (JWT-based)
# No session_id parameter needed - extracted from JWT token
```

### **Updated Function Signatures**

```python
# Before
async def create_note_page(
    self,
    title: str,
    content: Optional[str] = None,
    session_id: str = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:

# After
async def create_note_page(
    self,
    title: str,
    content: Optional[str] = None,
    request: Request = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
```

## 🧪 **Testing Strategy**

### **Unit Tests**

1. **JWT Integration Tests**

   - Test token extraction from headers
   - Test user ID extraction from payload
   - Test error handling scenarios

2. **Tool Parameter Tests**
   - Test tools without session_id parameter
   - Test JWT-based user identification
   - Test error handling for invalid tokens

### **Integration Tests**

1. **OAuth Flow Tests**

   - Test complete OAuth flow
   - Test token generation and validation
   - Test integration with Notion tools

2. **Frontend Integration Tests**
   - Test frontend OAuth connection
   - Test user-specific workspace creation
   - Test tool operations through frontend

### **End-to-End Tests**

1. **Complete User Journey**
   - User connects Notion via frontend
   - User creates notes through frontend
   - User accesses their private workspace

## 📈 **Success Criteria**

### **Functional Requirements**

- [ ] Notion tools work with JWT tokens instead of session_id
- [ ] OAuth callback routes function properly
- [ ] Frontend can connect to Notion and use tools
- [ ] User isolation is maintained
- [ ] Error handling works correctly

### **Technical Requirements**

- [ ] JWT integration service implemented
- [ ] Tool parameters updated
- [ ] OAuth routes verified
- [ ] Comprehensive test coverage
- [ ] Documentation updated

### **Performance Requirements**

- [ ] JWT token validation is fast
- [ ] No performance degradation
- [ ] Proper error handling doesn't impact performance

## 🚨 **Risks and Mitigation**

### **Risk 1: JWT Token Validation Performance**

- **Mitigation**: Use existing JWT service, implement caching if needed

### **Risk 2: Breaking Existing Functionality**

- **Mitigation**: Comprehensive testing, gradual rollout

### **Risk 3: Frontend Integration Issues**

- **Mitigation**: Test with frontend team, verify OAuth flow

## 📚 **Dependencies**

- **Task 066**: User-Specific Notion Pages Implementation (completed)
- **Task 030**: Core Authentication Service (completed)
- **Task 043**: OAuth Manager Service (completed)
- **Frontend OAuth Implementation** (completed)

## 🎯 **Timeline**

- **Phase 1**: 2 days (JWT Integration Service)
- **Phase 2**: 2 days (Tool Parameter Updates)
- **Phase 3**: 1 day (OAuth Route Verification)
- **Total**: 5 days

## 📝 **Notes**

- This task builds on the completed user-specific Notion implementation
- Focus on maintaining existing functionality while adding JWT support
- Ensure proper error handling and user feedback
- Test thoroughly with frontend integration
