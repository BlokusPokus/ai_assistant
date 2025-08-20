# 🚀 Task 032 Onboarding: Role-Based Access Control (RBAC) System

## **📋 Task Context**

**AI models are geniuses who start from scratch on every task.** - Noam Brown

Welcome to Task 032! This document will onboard you to the current state of the Personal Assistant TDAH platform and prepare you to implement a comprehensive Role-Based Access Control (RBAC) system that will enable multi-user architecture and enterprise-grade security.

## **🎯 What You're Building**

You're implementing the missing authorization and access control components that will complete the enterprise-grade security system:

- **RBAC Schema Design**: Database models for roles, permissions, and resource access control
- **Permission Service**: Service layer for checking user permissions and enforcing access control
- **FastAPI Integration**: Decorators and middleware for seamless permission checking
- **Audit Logging**: Complete audit trail for all permission checks and access decisions

This addresses **Tasks 2.1.2.1 and 2.1.2.2** from the technical roadmap.

## **🏗️ Current Architecture State**

### **✅ What's Already Built (Tasks 030 & 031 Complete)**

The authentication and MFA system is already implemented and functional:

- **JWT Token Management**: `src/personal_assistant/auth/jwt_service.py` ✅
- **Authentication Middleware**: `src/apps/fastapi_app/middleware/auth.py` ✅
- **User Management**: `src/apps/fastapi_app/routes/auth.py` ✅
- **MFA System**: TOTP + SMS + Backup codes ✅
- **Session Management**: Redis-based session storage ✅
- **Database Models**: User, MFA, Session, and Security models ✅

### **🔍 Current Access Control State**

**Current Access Control is Basic:**

- Users can only access their own data (user isolation)
- No role-based permissions
- No granular resource access control
- No permission inheritance
- No audit logging for access decisions

**What You'll Implement:**

- **Three-tier role system**: User, Premium, Administrator
- **Granular permissions**: Read, Write, Delete, Admin per resource
- **Role inheritance**: Premium inherits User permissions
- **Resource-level control**: Fine-grained access to different data types
- **Audit logging**: Complete trail of all access decisions

## **🔐 RBAC Architecture Context**

Based on the architecture documentation, this platform must meet enterprise security standards:

### **Compliance Requirements**

- **GDPR**: Data access control, user consent, right to be forgotten
- **SOC 2**: Access controls, audit trails, permission management
- **ISO 27001**: Authorization controls, access management

### **Security Principles**

- **Principle of Least Privilege**: Users get minimum required access
- **Separation of Duties**: Different roles for different functions
- **Audit Everything**: Complete access decision logging
- **Role-Based Security**: Access based on job function, not individual

## **📊 Current Codebase Analysis**

### **Authentication Flow (Existing)**

```
User Login → MFA Verification → JWT Token Generation → Session Creation → User Context Injection
```

### **Target Authorization Flow (What You'll Build)**

```
Request → JWT Validation → User Context → Role Lookup → Permission Check → Access Decision → Audit Log
```

### **Key Files to Understand**

- `src/personal_assistant/auth/jwt_service.py` - JWT token handling
- `src/apps/fastapi_app/middleware/auth.py` - Authentication middleware
- `src/personal_assistant/database/models/users.py` - User model
- `src/personal_assistant/config/settings.py` - Configuration management

## **🎯 Implementation Strategy**

### **Phase 1: RBAC Database Schema (Days 1-2)**

1. **Role Models**: Design and implement role and permission tables
2. **User-Role Association**: Link users to roles with inheritance support
3. **Permission Matrix**: Define granular permissions per resource type
4. **Database Migration**: Create and test migration scripts

### **Phase 2: Permission Service (Days 3-4)**

1. **Permission Service**: Core logic for checking user permissions
2. **Role Inheritance**: Implement role hierarchy and permission inheritance
3. **Resource Access Control**: Check permissions for specific resources
4. **Audit Logging**: Log all permission checks and access decisions

### **Phase 3: FastAPI Integration (Days 5-6)**

1. **Permission Decorators**: Easy-to-use decorators for endpoint protection
2. **Middleware Integration**: Integrate with existing authentication middleware
3. **Testing**: Comprehensive testing of permission system
4. **Documentation**: User guides and technical documentation

## **🔧 Technical Implementation Details**

### **RBAC Database Schema**

```sql
-- Roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,  -- 'user', 'premium', 'administrator'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- 'user:read', 'user:write', 'admin:all'
    resource_type VARCHAR(50) NOT NULL, -- 'user', 'memory', 'task', 'system'
    action VARCHAR(50) NOT NULL,        -- 'read', 'write', 'delete', 'admin'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Role permissions (many-to-many)
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- User roles (many-to-many with inheritance)
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,  -- Primary role for inheritance
    granted_by INTEGER REFERENCES users(id),  -- Who granted this role
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,  -- Role expiration
    UNIQUE(user_id, role_id)
);
```

### **RBAC Models Architecture**

```python
class Role(Base):
    """User roles with hierarchical permissions."""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    permissions = relationship("Permission", secondary="role_permissions")
    users = relationship("User", secondary="user_roles")

class Permission(Base):
    """Granular permissions for resources."""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    resource_type = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text)

class UserRole(Base):
    """User-role associations with audit trail."""
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    is_primary = Column(Boolean, default=False)
    granted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
```

### **Permission Service Architecture**

```python
class PermissionService:
    """Core service for permission checking and access control."""

    async def check_permission(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[int] = None
    ) -> bool:
        """Check if user has permission for specific action on resource."""

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a user with inheritance."""

    async def has_role(self, user_id: int, role_name: str) -> bool:
        """Check if user has specific role."""

    async def grant_role(self, user_id: int, role_name: str, granted_by: int) -> bool:
        """Grant role to user with audit trail."""

    async def revoke_role(self, user_id: int, role_name: str, revoked_by: int) -> bool:
        """Revoke role from user with audit trail."""
```

### **FastAPI Permission Decorators**

```python
def require_permission(resource_type: str, action: str):
    """Decorator to require specific permission for endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request
            # Check permission using PermissionService
            # Log access decision
            # Return 403 if access denied
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role_name: str):
    """Decorator to require specific role for endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request
            # Check role using PermissionService
            # Log access decision
            # Return 403 if access denied
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## **🚀 Getting Started Steps**

### **Step 1: Environment Setup**

1. **Verify Database**: Ensure PostgreSQL is running and accessible
2. **Review Existing Models**: Understand current User and MFA models
3. **Environment Variables**: Configure RBAC settings

### **Step 2: Code Exploration**

1. **Study Existing Auth**: Understand how JWT and middleware work
2. **Review Database Schema**: See existing table structures
3. **Authentication Flow**: Understand current user context injection

### **Step 3: Implementation Planning**

1. **RBAC Schema Design**: Plan database structure and relationships
2. **Permission Matrix**: Define what each role can access
3. **Integration Points**: Identify where to hook into existing auth flow

## **🔍 Key Questions to Answer**

Before starting implementation, ensure you understand:

1. **Role Hierarchy**: How do roles inherit permissions? What's the inheritance chain?
2. **Resource Types**: What resources need permission control? (users, memories, tasks, etc.)
3. **Permission Granularity**: How fine-grained should permissions be? (read, write, delete, admin)
4. **Audit Requirements**: What information needs to be logged for compliance?
5. **Performance**: How do we ensure permission checks don't slow down the system?

## **📚 Essential Documentation**

### **Architecture Documents**

- `docs/architecture/3_MAE_security.md` - Security requirements and RBAC specifications
- `docs/architecture/4_MAS_application_model.md` - Application architecture and user profiles
- `docs/architecture/6_MAS_deployment.md` - Deployment and infrastructure

### **Technical Roadmap**

- `docs/architecture/TECHNICAL_BREAKDOWN_ROADMAP.md` - Overall project roadmap
- `docs/architecture/tasks/031_mfa_and_session_management/` - Previous task implementation

### **Code References**

- `src/personal_assistant/auth/` - Existing authentication services
- `src/apps/fastapi_app/middleware/auth.py` - Current authentication middleware
- `src/personal_assistant/database/models/` - Database models

## **🚨 Critical Success Factors**

### **Security First**

- **Never bypass permission checks** - every resource access must be validated
- **Implement proper role inheritance** to avoid permission gaps
- **Log all access decisions** for audit and compliance
- **Validate all inputs** and handle edge cases

### **Performance & Scalability**

- **Permission checks should be fast** (<50ms)
- **Support concurrent users** without degradation
- **Efficient database queries** with proper indexing
- **Cache frequently used permissions** to reduce database load

### **User Experience**

- **Clear error messages** when access is denied
- **Intuitive role management** for administrators
- **Seamless integration** with existing authentication
- **Comprehensive audit trails** for compliance

## **🔗 Integration Points**

### **Authentication Flow Integration**

- **JWT Validation**: Extract user context for permission checking
- **Middleware**: Integrate permission checking with auth middleware
- **User Context**: Use existing user context injection
- **Session Management**: Leverage existing session system

### **Existing System Integration**

- **User Models**: Extend with role relationships
- **Auth Middleware**: Add permission checking layer
- **Configuration**: Add RBAC settings
- **Logging**: Integrate with existing logging system

## **📊 Success Metrics**

### **Security Metrics**

- 100% of resource accesses go through permission checks
- 0 unauthorized access attempts successful
- Complete audit trail for all access decisions

### **Performance Metrics**

- Permission checks <50ms response time
- <5% performance degradation overall
- Support for 100+ concurrent users

### **Compliance Metrics**

- 100% of access decisions logged
- Role assignments tracked with audit trail
- Permission changes logged with justification

## **🎯 Next Steps After This Task**

Once Task 032 is complete, the platform will have:

1. **Enterprise-grade authorization** with role-based access control
2. **Multi-user architecture foundation** ready for implementation
3. **Compliance-ready audit trails** for GDPR, SOC 2, and ISO 27001
4. **Scalable permission system** for future feature expansion

The next logical tasks will be:

- **Phase 2.2**: Infrastructure & Database optimization
- **Phase 2.3**: API & Backend services with permission integration
- **Phase 2.5**: Multi-user architecture with SMS Router Service

## **🔧 Development Environment Setup**

### **Required Tools**

- Python 3.9+ with virtual environment
- PostgreSQL database (already configured)
- FastAPI development server
- Database migration tools

### **Testing Strategy**

- **Unit Tests**: Test individual RBAC services
- **Integration Tests**: Test complete permission flows
- **Security Tests**: Test permission bypass attempts
- **Performance Tests**: Test under load and concurrent users

### **Debugging Tips**

- **Database**: Use pgAdmin or psql to inspect RBAC tables
- **FastAPI Docs**: Use `/docs` endpoint for API testing
- **Logging**: Check logs for permission checks and access decisions
- **Middleware**: Test permission checking in isolation

## **📞 Getting Help**

### **When You're Stuck**

1. **Check the logs** for error messages and stack traces
2. **Review existing code** for patterns and examples
3. **Test incrementally** - don't try to build everything at once
4. **Document issues** and solutions for future reference

### **Resources**

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **RBAC Best Practices**: https://owasp.org/www-project-proactive-controls/

---

**Remember**: You're building the authorization foundation that will control access to users' personal data and enable secure multi-user deployment. Take the time to get it right - access control is critical for security and compliance.

**Good luck with the implementation!** 🚀

---

**Document prepared by**: Technical Architecture Team  
**Last updated**: [Current Date]  
**Next review**: Daily during implementation  
**Contact**: [Your Team Contact Information]
