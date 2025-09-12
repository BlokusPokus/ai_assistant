# Onboarding Guide: User-Specific Email with Outlook Implementation

## 🎯 **Task Overview**

You are implementing user-specific email functionality with Microsoft Outlook integration. This task builds upon the existing OAuth infrastructure and follows the same pattern as the recently completed user-specific Notion pages implementation.

## 📋 **Context & Background**

### **What You're Building**

A comprehensive email management system that provides:

- **User-Specific Email Access**: Each user gets their own private email access
- **OAuth Integration**: Uses existing Microsoft OAuth provider for secure authentication
- **Email Operations**: Send, read, manage emails through the personal assistant
- **Complete User Isolation**: No data leakage between users

### **Why This Matters**

- **Multi-User Support**: Enables true multi-user personal assistant functionality
- **Security**: Each user's emails are completely isolated and secure
- **Scalability**: Architecture supports unlimited users
- **User Experience**: Seamless email management through the assistant

## 🏗️ **Architecture Overview**

### **Current System Design**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Current Email System                         │
├─────────────────────────────────────────────────────────────────┤
│  User Request → Email Tool → Microsoft Graph API (Single User) │
│       ↓              ↓                    ↓                    │
│  Email Operations → API Calls → Microsoft Graph (Hardcoded)    │
└─────────────────────────────────────────────────────────────────┘
```

### **Target System Design (User-Specific Implementation)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    User-Specific Email System                   │
├─────────────────────────────────────────────────────────────────┤
│  User Request → SessionService → OAuthTokenService → Microsoft  │
│       ↓              ↓              ↓              ↓           │
│  Tool Execution → EmailWorkspaceMgr → Email Operations → Graph  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 **Implementation Pattern**

### **Follow the Notion Pages Pattern**

This implementation follows the exact same pattern as the user-specific Notion pages:

1. **User Context Service** ✅ (Already Available)
2. **Client Factory** ⚠️ (Needs Implementation)
3. **Workspace Manager** ⚠️ (Needs Implementation)
4. **Tool Integration** ⚠️ (Needs Implementation)

### **Key Components to Implement**

#### **1. EmailClientFactory** (Similar to NotionClientFactory)

```python
# File: src/personal_assistant/tools/emails/email_client_factory.py
class EmailClientFactory:
    """Factory for creating user-specific Microsoft Graph email clients"""

    async def get_user_client(self, db: AsyncSession, user_id: int, session_id: str) -> GraphServiceClient:
        """Get or create Microsoft Graph client for a specific user"""
        # 1. Get user's Microsoft OAuth integration
        # 2. Get valid access token
        # 3. Create GraphServiceClient
        # 4. Cache client for performance
```

#### **2. EmailWorkspaceManager** (Similar to NotionWorkspaceManager)

```python
# File: src/personal_assistant/tools/emails/email_workspace_manager.py
class EmailWorkspaceManager:
    """Manages user-specific email operations and validation"""

    async def validate_user_email_access(self, client: GraphServiceClient, user_id: int) -> bool:
        """Validate user has access to their email"""

    async def get_user_folders(self, client: GraphServiceClient, user_id: int) -> List[Folder]:
        """Get user's email folders"""
```

#### **3. Updated Email Tool** (Similar to UserSpecificNotionPagesTool)

```python
# File: src/personal_assistant/tools/emails/email_tool_user_specific.py
class UserSpecificEmailTool:
    """User-specific email tool for managing emails with OAuth integration"""

    async def send_email(self, to: str, subject: str, body: str, session_id: str) -> Dict:
        """Send email using user's Microsoft account"""

    async def read_emails(self, folder: str, session_id: str) -> Dict:
        """Read emails from user's Microsoft account"""
```

## 📚 **Key Files to Study**

### **1. Notion Implementation (Reference Pattern)**

- `src/personal_assistant/tools/notion_pages/client_factory.py` - Client factory pattern
- `src/personal_assistant/tools/notion_pages/workspace_manager.py` - Workspace management
- `src/personal_assistant/tools/notion_pages/notion_pages_tool_user_specific.py` - Tool integration

### **2. OAuth Infrastructure (Already Available)**

- `src/personal_assistant/oauth/providers/microsoft.py` - Microsoft OAuth provider
- `src/personal_assistant/oauth/services/token_service.py` - Token management
- `src/personal_assistant/oauth/services/integration_service.py` - Integration management

### **3. Existing Email Tool (To Update)**

- `src/personal_assistant/tools/emails/email_tool.py` - Current email tool
- `src/personal_assistant/tools/emails/ms_graph.py` - Microsoft Graph integration

## 🚀 **Implementation Steps**

### **Step 1: Create EmailClientFactory**

1. **Study NotionClientFactory** (`src/personal_assistant/tools/notion_pages/client_factory.py`)
2. **Create EmailClientFactory** following the same pattern
3. **Use Microsoft Graph SDK** instead of Notion client
4. **Integrate with existing OAuth services**

### **Step 2: Create EmailWorkspaceManager**

1. **Study NotionWorkspaceManager** (`src/personal_assistant/tools/notion_pages/workspace_manager.py`)
2. **Create EmailWorkspaceManager** for email-specific operations
3. **Implement email validation and folder management**
4. **Add error handling and fallbacks**

### **Step 3: Update Email Tool**

1. **Study UserSpecificNotionPagesTool** (`src/personal_assistant/tools/notion_pages/notion_pages_tool_user_specific.py`)
2. **Create UserSpecificEmailTool** following the same pattern
3. **Update all email operations for user context**
4. **Add user isolation validation**

### **Step 4: Integration and Testing**

1. **Update tool registry** to use new user-specific email tool
2. **Test with multiple users**
3. **Validate email isolation**
4. **Test error scenarios**

## 🔍 **Key Implementation Details**

### **1. OAuth Integration Pattern**

```python
# Get user from session (existing)
user_id = await session_service.get_current_user_id(session_id)

# Get user's Microsoft integration (existing)
integration = await integration_service.get_integration_by_user_and_provider(
    db, user_id, "microsoft"
)

# Get valid access token (existing)
token = await token_service.get_valid_token(db, integration.id)

# Create Microsoft Graph client (new)
client = GraphServiceClient(credentials=token)
```

### **2. User Context Injection Pattern**

```python
async def send_email(self, to: str, subject: str, body: str, session_id: str) -> Dict:
    """Send email using user's Microsoft account"""
    try:
        # Get user ID from session
        user_id = await self._get_user_id_from_session(session_id, db)
        if not user_id:
            return {"error": "Invalid session or user not found"}

        # Get user-specific Microsoft Graph client
        client = await self.client_factory.get_user_client(db, user_id, session_id)

        # Send email using user's account
        # ... email sending logic

    except MicrosoftNotConnectedError:
        return {"error": "User must connect Microsoft account first"}
```

### **3. Error Handling Pattern**

```python
# Custom exceptions (similar to Notion)
class MicrosoftNotConnectedError(Exception):
    """Raised when user hasn't connected Microsoft account"""
    pass

class MicrosoftTokenExpiredError(Exception):
    """Raised when Microsoft token is expired and can't be refreshed"""
    pass

class MicrosoftEmailError(Exception):
    """Raised when email operation fails"""
    pass
```

## 🧪 **Testing Strategy**

### **1. Unit Tests**

- Test EmailClientFactory
- Test EmailWorkspaceManager
- Test user context integration
- Test error handling scenarios

### **2. Integration Tests**

- Test complete email workflow
- Test multi-user scenarios
- Test OAuth integration
- Test email isolation

### **3. Security Tests**

- Test user data isolation
- Test token security
- Test email access validation
- Test error information leakage

## 📁 **File Structure to Create**

```
src/personal_assistant/tools/emails/
├── email_client_factory.py           # New: Client factory
├── email_workspace_manager.py        # New: Workspace management
├── email_tool_user_specific.py       # New: User-specific tool
├── email_internal_user_specific.py   # New: User-specific operations
└── email_error_handler.py            # Update: Add user context

tests/unit/test_emails/
├── test_email_client_factory.py      # New: Factory tests
├── test_email_workspace_manager.py   # New: Manager tests
└── test_email_tool_user_specific.py  # New: Tool tests
```

## 🔒 **Security Considerations**

### **1. Token Security**

- Never log access tokens
- Use secure token storage
- Implement token rotation
- Validate token permissions

### **2. User Isolation**

- Validate user context in all operations
- Ensure no cross-user data access
- Implement strict permission checks
- Add audit logging

### **3. Error Handling**

- Sanitize error messages
- Don't expose sensitive information
- Log security events
- Implement graceful degradation

## 🚧 **Common Pitfalls to Avoid**

### **1. OAuth Integration**

- Don't hardcode tokens
- Use existing OAuth services
- Handle token refresh properly
- Validate user permissions

### **2. User Context**

- Always validate user context
- Don't assume user identity
- Handle missing context gracefully
- Add proper error messages

### **3. Error Handling**

- Don't expose sensitive data
- Handle all error scenarios
- Add user-friendly messages
- Implement proper logging

## 📖 **Resources and References**

### **1. Microsoft Graph API**

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Python SDK Documentation](https://docs.microsoft.com/en-us/graph/sdks/python)
- [Email API Reference](https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview)

### **2. OAuth Integration**

- [Microsoft OAuth Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Graph API Authentication](https://docs.microsoft.com/en-us/graph/auth/)

### **3. Implementation Examples**

- `src/personal_assistant/tools/notion_pages/` - Notion implementation pattern
- `src/personal_assistant/oauth/` - OAuth infrastructure
- `src/personal_assistant/tools/emails/` - Current email implementation

## ✅ **Success Criteria**

### **Functional Requirements**

- [ ] Each user has their own email access
- [ ] Complete user data isolation
- [ ] OAuth integration working
- [ ] All existing functionality preserved
- [ ] Send emails using user's account
- [ ] Read emails from user's account
- [ ] Manage email folders

### **Non-Functional Requirements**

- [ ] Performance within acceptable limits
- [ ] Security requirements met
- [ ] Error handling comprehensive
- [ ] User experience maintained
- [ ] Documentation complete

### **Quality Requirements**

- [ ] 90%+ test coverage
- [ ] All tests passing
- [ ] Code review completed
- [ ] Security review completed
- [ ] Performance review completed

## 🎯 **Getting Started**

1. **Read this onboarding guide completely**
2. **Study the Notion implementation pattern**
3. **Examine the existing OAuth infrastructure**
4. **Review the current email tool implementation**
5. **Start with EmailClientFactory implementation**
6. **Follow the step-by-step implementation plan**
7. **Test thoroughly at each step**

Remember: This implementation follows the exact same pattern as the user-specific Notion pages, so use that as your primary reference!

