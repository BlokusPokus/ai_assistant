# Task 066 Onboarding: User-Specific Notion Pages Implementation

## 🎯 **Task Context**

You are implementing user-specific Notion page management to enable true multi-user support. Currently, all users share the same hardcoded `settings.NOTION_ROOT_PAGE_ID`, which creates security and isolation issues. This task will create a "Personal Assistant" page in each user's Notion workspace, ensuring complete user isolation while maintaining all existing functionality.

## 🧠 **Ultrathink Analysis**

### **Current Architecture Understanding**

1. **OAuth System**: Users already have individual Notion workspaces through OAuth
2. **Token Management**: Each user has their own Notion access tokens
3. **Workspace Isolation**: OAuth provides natural user separation
4. **Hardcoded Dependencies**: Current system uses `settings.NOTION_ROOT_PAGE_ID`

### **Key Insight**

The OAuth system already provides user isolation at the Notion workspace level. We don't need to change the database schema - we just need to make the Notion tools user-aware instead of using hardcoded settings.

### **Implementation Strategy**

1. **User Context Injection**: Pass user information to all Notion operations
2. **Dynamic Root Page**: Create user-specific "Personal Assistant" pages
3. **OAuth Integration**: Use user-specific tokens from existing OAuth system
4. **Graceful Fallbacks**: Handle edge cases without breaking functionality

## 🔍 **Codebase Exploration**

### **Critical Files to Understand**

#### **1. OAuth System**

```bash
src/personal_assistant/oauth/
├── providers/notion.py          # Notion OAuth provider
├── services/token_service.py    # Token management
└── models/oauth_connection.py   # OAuth connection models
```

#### **2. Notion Tools**

```bash
src/personal_assistant/tools/
├── notes/enhanced_notes_tool.py    # Main notes tool
├── notes/llm_notes_enhancer.py     # LLM enhancement
└── notion_pages/notion_internal.py # Notion API utilities
```

#### **3. Current Settings**

```bash
src/personal_assistant/config/settings.py  # Hardcoded NOTION_ROOT_PAGE_ID
```

### **Key Dependencies**

1. **OAuth Token Service**: How to retrieve user-specific Notion tokens
2. **User Context**: How to identify current user in tool operations
3. **Notion API Client**: How to create user-specific Notion clients
4. **Error Handling**: How to handle OAuth and Notion API errors

## 🎯 **Implementation Phases**

### **Phase 1: User Context Foundation**

#### **1.1 User Context Service**

```python
# src/personal_assistant/oauth/services/user_context_service.py
class UserContextService:
    """Service for managing user context in Notion operations"""

    async def get_current_user(self) -> Optional[User]:
        """Get current user from request context"""

    async def get_user_notion_token(self, user_id: str) -> Optional[str]:
        """Get user's Notion access token"""

    async def validate_user_workspace(self, user_id: str) -> bool:
        """Validate user has access to their Notion workspace"""
```

#### **1.2 Notion Client Factory**

```python
# src/personal_assistant/tools/notion_pages/client_factory.py
class NotionClientFactory:
    """Factory for creating user-specific Notion clients"""

    def create_user_client(self, access_token: str) -> Client:
        """Create Notion client with user's access token"""

    async def get_user_client(self, user_id: str) -> Client:
        """Get or create Notion client for user"""
```

### **Phase 2: Workspace Management**

#### **2.1 Notion Workspace Manager**

```python
# src/personal_assistant/tools/notion_pages/workspace_manager.py
class NotionWorkspaceManager:
    """Manages user-specific Notion workspaces"""

    async def ensure_user_root_page(self, client: Client, user_id: str) -> str:
        """Ensure user has Personal Assistant page in their workspace"""

    async def create_user_root_page(self, client: Client, user_id: str) -> str:
        """Create Personal Assistant page in user's workspace"""

    async def find_user_root_page(self, client: Client, user_id: str) -> Optional[str]:
        """Find existing Personal Assistant page"""
```

#### **2.2 Dynamic Root Page System**

```python
# Update src/personal_assistant/tools/notion_pages/notion_internal.py
async def ensure_main_page_exists(
    client: Client,
    user_id: str,  # NEW: User context
    main_page_id: Optional[str] = None
) -> str:
    """Ensure user has main page, create if needed"""

    # Replace hardcoded settings.NOTION_ROOT_PAGE_ID
    # with user-specific page creation
```

### **Phase 3: Tool Integration**

#### **3.1 Enhanced Notes Tool Updates**

```python
# Update src/personal_assistant/tools/notes/enhanced_notes_tool.py
class EnhancedNotesTool:
    def __init__(self):
        self.user_context_service = UserContextService()  # NEW
        self.workspace_manager = NotionWorkspaceManager()  # NEW

    async def create_enhanced_note(self, content: str, **kwargs):
        # Get user context
        user_id = await self.user_context_service.get_current_user()

        # Get user-specific Notion client
        client = await self.client_factory.get_user_client(user_id)

        # Ensure user has root page
        main_page_id = await self.workspace_manager.ensure_user_root_page(client, user_id)

        # Continue with existing logic...
```

#### **3.2 Notion Pages Tool Updates**

```python
# Update src/personal_assistant/tools/notion_pages/notion_pages_tool.py
class NotionPagesTool:
    def __init__(self):
        self.user_context_service = UserContextService()  # NEW
        self.workspace_manager = NotionWorkspaceManager()  # NEW

    async def create_note_page(self, title: str, content: str, **kwargs):
        # Similar user context integration
```

## 🔧 **Technical Implementation Details**

### **1. User Context Injection**

#### **Method 1: Request Context (Recommended)**

```python
# In FastAPI routes or tool execution
async def get_current_user() -> Optional[User]:
    """Get current user from request context"""
    # Implementation depends on your auth system
    return request.state.user
```

#### **Method 2: Session-Based**

```python
# Using existing session management
async def get_current_user() -> Optional[User]:
    """Get current user from session"""
    session_id = get_session_id()
    return await session_service.get_user(session_id)
```

### **2. OAuth Token Retrieval**

```python
async def get_user_notion_token(user_id: str) -> Optional[str]:
    """Get user's Notion access token from OAuth system"""
    oauth_connection = await oauth_service.get_connection(
        user_id=user_id,
        provider="notion"
    )
    return oauth_connection.access_token if oauth_connection else None
```

### **3. User-Specific Page Creation**

```python
async def create_user_root_page(client: Client, user_id: str) -> str:
    """Create Personal Assistant page in user's workspace"""

    # Get user's workspace root (first page in workspace)
    workspace_pages = client.search(
        query="",
        filter={"property": "object", "value": "page"}
    )

    if not workspace_pages.get("results"):
        raise Exception("User workspace not accessible")

    workspace_root = workspace_pages["results"][0]

    # Create Personal Assistant page
    personal_assistant_page = client.pages.create(
        parent={"type": "page_id", "page_id": workspace_root["id"]},
        properties={
            "title": [{"type": "text", "text": {"content": "Personal Assistant"}}]
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Welcome to your personal assistant notes!"}
                    }]
                }
            }
        ]
    )

    return personal_assistant_page["id"]
```

## 🚨 **Critical Considerations**

### **1. Error Handling**

#### **OAuth Token Issues**

```python
try:
    access_token = await get_user_notion_token(user_id)
    if not access_token:
        raise NotionNotConnectedError("User must connect Notion account")
except OAuthError as e:
    raise NotionConnectionError(f"OAuth error: {e}")
```

#### **Workspace Access Issues**

```python
try:
    client = create_user_client(access_token)
    # Test workspace access
    client.search(query="", filter={"property": "object", "value": "page"})
except NotionAPIError as e:
    if e.status_code == 401:
        raise NotionTokenExpiredError("Notion token expired, please reconnect")
    elif e.status_code == 403:
        raise NotionAccessDeniedError("Insufficient Notion permissions")
```

### **2. Security Considerations**

#### **User Isolation Validation**

```python
def validate_user_isolation(user_id: str, page_id: str) -> bool:
    """Ensure page belongs to user's workspace"""
    # Implementation to verify page ownership
    pass
```

#### **Token Security**

```python
def sanitize_logs(data: dict) -> dict:
    """Remove sensitive tokens from logs"""
    sanitized = data.copy()
    if "access_token" in sanitized:
        sanitized["access_token"] = "***REDACTED***"
    return sanitized
```

### **3. Performance Considerations**

#### **Client Caching**

```python
class NotionClientCache:
    """Cache Notion clients to avoid recreation"""

    def __init__(self):
        self._clients = {}

    async def get_client(self, user_id: str) -> Client:
        if user_id not in self._clients:
            self._clients[user_id] = await self._create_client(user_id)
        return self._clients[user_id]
```

## 🧪 **Testing Strategy**

### **1. Unit Tests**

```python
# Test user context service
async def test_get_current_user():
    user = await user_context_service.get_current_user()
    assert user is not None
    assert user.id is not None

# Test Notion client factory
async def test_create_user_client():
    client = client_factory.create_user_client("test_token")
    assert isinstance(client, Client)

# Test workspace manager
async def test_ensure_user_root_page():
    page_id = await workspace_manager.ensure_user_root_page(client, "user123")
    assert page_id is not None
```

### **2. Integration Tests**

```python
# Test complete user workflow
async def test_user_note_creation():
    # Simulate user context
    with user_context("user123"):
        result = await enhanced_notes_tool.create_enhanced_note(
            content="Test note content"
        )
        assert "successfully created" in result

# Test multi-user isolation
async def test_user_isolation():
    # Create notes for two different users
    # Verify they can't see each other's notes
    pass
```

### **3. Security Tests**

```python
# Test user isolation
async def test_user_cannot_access_other_workspace():
    # Attempt to access another user's workspace
    # Should fail with appropriate error
    pass

# Test token security
async def test_tokens_not_exposed_in_logs():
    # Verify sensitive tokens are not logged
    pass
```

## 📋 **Implementation Checklist**

### **Phase 1: Foundation**

- [ ] Create `UserContextService` class
- [ ] Implement user identification logic
- [ ] Create `NotionClientFactory` class
- [ ] Implement user-specific client creation
- [ ] Add client caching mechanism
- [ ] Write unit tests for foundation classes

### **Phase 2: Workspace Management**

- [ ] Create `NotionWorkspaceManager` class
- [ ] Implement user root page creation
- [ ] Add page validation logic
- [ ] Implement fallback mechanisms
- [ ] Update `ensure_main_page_exists` function
- [ ] Write integration tests

### **Phase 3: Tool Integration**

- [ ] Update `EnhancedNotesTool` for user context
- [ ] Update `NotionPagesTool` for user context
- [ ] Update `notion_internal.py` functions
- [ ] Add user context injection to all tools
- [ ] Implement error handling
- [ ] Write comprehensive tests

### **Phase 4: Testing & Validation**

- [ ] Test multi-user scenarios
- [ ] Validate user isolation
- [ ] Test error handling
- [ ] Performance testing
- [ ] Security validation
- [ ] Documentation updates

## 🔄 **Migration Strategy**

### **1. Backward Compatibility**

- Keep existing hardcoded approach as fallback
- Gradually migrate tools to user-aware approach
- Add feature flags for new functionality

### **2. User Experience**

- Provide clear error messages for OAuth issues
- Guide users through Notion connection process
- Implement graceful degradation

### **3. Rollout Plan**

- Deploy with feature flags disabled
- Enable for test users first
- Gradual rollout to all users
- Monitor for issues and rollback if needed

## 📚 **Key Resources**

### **Code References**

- `src/personal_assistant/oauth/providers/notion.py` - OAuth integration
- `src/personal_assistant/tools/notes/enhanced_notes_tool.py` - Main tool to update
- `src/personal_assistant/tools/notion_pages/notion_internal.py` - Core functions
- `src/personal_assistant/config/settings.py` - Current hardcoded settings

### **Documentation**

- [Notion API Documentation](https://developers.notion.com/reference)
- [OAuth 2.0 Best Practices](https://tools.ietf.org/html/rfc6749)
- [FastAPI Request Context](https://fastapi.tiangolo.com/advanced/request-state/)

### **Related Tasks**

- Task 044: OAuth Settings Management
- Task 064: Enhanced Notes Tool with LLM
- Task 030: Core Authentication Service

## 🎯 **Success Criteria**

1. **User Isolation**: Each user has their own Notion workspace
2. **OAuth Integration**: User-specific tokens used for all operations
3. **Dynamic Pages**: No hardcoded root page IDs
4. **Error Handling**: Graceful handling of OAuth and Notion errors
5. **Performance**: No significant performance degradation
6. **Security**: Complete user data isolation
7. **Backward Compatibility**: Existing functionality preserved

## 🚀 **Ready to Start**

You now have a comprehensive understanding of:

- The current architecture and its limitations
- The OAuth system and how to integrate with it
- The specific files and functions that need modification
- The implementation strategy and phases
- The testing and security considerations

**Next Step**: Begin with Phase 1 - creating the `UserContextService` and `NotionClientFactory` classes.
