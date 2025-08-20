# 🔐 Task 032: Role-Based Access Control (RBAC) System

## **📋 Task Overview**

**Task ID**: 032  
**Task Name**: Role-Based Access Control (RBAC) System  
**Status**: 🔴 Not Started  
**Effort**: 5 days  
**Dependencies**: Tasks 030 (Core Authentication) & 031 (MFA & Session Management) ✅ Complete  
**Priority**: HIGH - Critical for multi-user architecture

## **🎯 Objectives**

Implement a comprehensive Role-Based Access Control (RBAC) system that provides:

1. **Three-tier role system**: User, Premium, Administrator with permission inheritance
2. **Granular resource permissions**: Read, Write, Delete, Admin access per resource type
3. **FastAPI integration**: Decorators and middleware for seamless permission checking
4. **Audit logging**: Complete trail of all access decisions for compliance
5. **Performance optimization**: Fast permission checks (<50ms) with caching support

## **🏗️ Architecture Context**

### **Current State (Tasks 030 & 031 Complete)**

The platform currently has:

- ✅ JWT-based authentication with MFA
- ✅ Redis-based session management
- ✅ Basic user isolation (users can only access their own data)
- ✅ Security event logging
- ✅ Rate limiting and abuse prevention

### **Target State (After Task 032)**

The platform will have:

- 🔐 **Enterprise-grade authorization** with role-based access control
- 👥 **Multi-user architecture foundation** ready for implementation
- 📊 **Compliance-ready audit trails** for GDPR, SOC 2, and ISO 27001
- 🚀 **Scalable permission system** for future feature expansion

### **Integration Points**

- **Authentication Flow**: Extends existing JWT validation with permission checking
- **Middleware Layer**: Integrates with existing AuthMiddleware
- **Database Models**: Extends User model with role relationships
- **API Endpoints**: Protects endpoints with permission decorators

## **🔐 RBAC Design**

### **Role Hierarchy**

```
Administrator (admin)
├── All system permissions
├── User management
├── System monitoring
└── Configuration management

Premium User (premium)
├── Inherits: User permissions
├── Advanced features access
├── Extended integrations
└── Analytics and reporting

Standard User (user)
├── Basic feature access
├── Own data management
├── Limited integrations
└── Basic reporting
```

### **Permission Matrix**

| Resource Type       | User | Premium | Administrator |
| ------------------- | ---- | ------- | ------------- |
| **Own Profile**     | R/W  | R/W     | R/W (all)     |
| **Own Memories**    | R/W  | R/W     | R/W (all)     |
| **Own Tasks**       | R/W  | R/W     | R/W (all)     |
| **System Metrics**  | None | R       | R/W           |
| **User Management** | None | None    | R/W           |
| **System Config**   | None | None    | R/W           |

**Legend**: R = Read, W = Write, None = No Access

### **Resource Types**

1. **User Resources**: Profile, settings, preferences
2. **Data Resources**: Memories, tasks, notes, events
3. **System Resources**: Metrics, logs, configuration
4. **Integration Resources**: API keys, webhooks, external services

## **📊 Database Schema**

### **New Tables**

#### **1. roles**

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_role_id INTEGER REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **2. permissions**

```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **3. role_permissions**

```sql
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);
```

#### **4. user_roles**

```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    UNIQUE(user_id, role_id)
);
```

#### **5. access_audit_logs**

```sql
CREATE TABLE access_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER NULL,
    action VARCHAR(50) NOT NULL,
    permission_granted BOOLEAN NOT NULL,
    roles_checked TEXT[], -- Array of role names checked
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Updated Tables**

#### **users**

```sql
-- Add role-related fields
ALTER TABLE users ADD COLUMN default_role_id INTEGER REFERENCES roles(id);
ALTER TABLE users ADD COLUMN role_assigned_at TIMESTAMP;
ALTER TABLE users ADD COLUMN role_assigned_by INTEGER REFERENCES users(id);
```

## **🔧 Implementation Components**

### **1. RBAC Models (`src/personal_assistant/database/models/rbac_models.py`)**

```python
class Role(Base):
    """User roles with hierarchical permissions."""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)

    # Relationships
    permissions = relationship("Permission", secondary="role_permissions")
    users = relationship("User", secondary="user_roles")
    parent_role = relationship("Role", remote_side=[id])
    child_roles = relationship("Role")

class Permission(Base):
    """Granular permissions for resources."""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    resource_type = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text)

    # Relationships
    roles = relationship("Role", secondary="role_permissions")

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

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role")
    granted_by_user = relationship("User", foreign_keys=[granted_by])

class AccessAuditLog(Base):
    """Audit trail for all access decisions."""
    __tablename__ = 'access_audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    action = Column(String(50), nullable=False)
    permission_granted = Column(Boolean, nullable=False)
    roles_checked = Column(ARRAY(String))
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
```

### **2. Permission Service (`src/personal_assistant/auth/permission_service.py`)**

```python
class PermissionService:
    """Core service for permission checking and access control."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self._permission_cache = {}  # Simple in-memory cache

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

    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permissions for a user including inheritance."""

    async def log_access_attempt(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[int],
        granted: bool,
        roles_checked: List[str]
    ) -> None:
        """Log access attempt for audit trail."""
```

### **3. FastAPI Permission Decorators (`src/personal_assistant/auth/decorators.py`)**

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

def require_ownership(resource_type: str, action: str):
    """Decorator to require ownership of resource for endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user and resource from request
            # Check ownership and permission
            # Log access decision
            # Return 403 if access denied
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### **4. RBAC Management Routes (`src/apps/fastapi_app/routes/rbac.py`)**

```python
@router.post("/roles", response_model=RoleResponse)
@require_role("administrator")
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new role (admin only)."""

@router.post("/users/{user_id}/roles/{role_name}")
@require_role("administrator")
async def grant_role(
    user_id: int,
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Grant role to user (admin only)."""

@router.delete("/users/{user_id}/roles/{role_name}")
@require_role("administrator")
async def revoke_role(
    user_id: int,
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke role from user (admin only)."""

@router.get("/users/{user_id}/permissions")
@require_role("administrator")
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all permissions for a user (admin only)."""

@router.get("/audit-logs")
@require_role("administrator")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get access audit logs (admin only)."""
```

## **🚀 Implementation Phases**

### **Phase 1: Database Schema (Days 1-2)**

1. **Create RBAC Models**: Implement all RBAC-related database models
2. **Database Migration**: Create migration script for new tables
3. **Seed Data**: Populate initial roles and permissions
4. **Testing**: Verify database schema and relationships

### **Phase 2: Core Services (Days 3-4)**

1. **Permission Service**: Implement core permission checking logic
2. **Role Management**: Implement role assignment and inheritance
3. **Audit Logging**: Implement comprehensive access logging
4. **Caching**: Add permission caching for performance

### **Phase 3: FastAPI Integration (Days 5-6)**

1. **Permission Decorators**: Implement easy-to-use permission decorators
2. **RBAC Routes**: Create role and permission management endpoints
3. **Middleware Integration**: Integrate with existing authentication
4. **Testing & Documentation**: Comprehensive testing and documentation

## **🧪 Testing Strategy**

### **Unit Tests**

- **Permission Service**: Test permission checking logic
- **Role Management**: Test role assignment and inheritance
- **Model Validation**: Test database model constraints

### **Integration Tests**

- **API Endpoints**: Test permission-protected endpoints
- **Database Operations**: Test RBAC database operations
- **Middleware Integration**: Test permission checking in requests

### **Security Tests**

- **Permission Bypass**: Test attempts to bypass permission checks
- **Role Escalation**: Test attempts to gain unauthorized roles
- **Audit Logging**: Verify all access attempts are logged

### **Performance Tests**

- **Permission Checks**: Ensure checks complete in <50ms
- **Concurrent Users**: Test with 100+ concurrent users
- **Cache Performance**: Test permission caching effectiveness

## **📊 Success Metrics**

### **Security Metrics**

- ✅ 100% of resource accesses go through permission checks
- ✅ 0 successful unauthorized access attempts
- ✅ Complete audit trail for all access decisions

### **Performance Metrics**

- ✅ Permission checks <50ms response time
- ✅ <5% performance degradation overall
- ✅ Support for 100+ concurrent users

### **Compliance Metrics**

- ✅ 100% of access decisions logged
- ✅ Role assignments tracked with audit trail
- ✅ Permission changes logged with justification

## **🔗 Dependencies & Integration**

### **Internal Dependencies**

- **Task 030**: Core Authentication Service ✅ Complete
- **Task 031**: MFA & Session Management ✅ Complete
- **Database Models**: Existing User and MFA models
- **Authentication Middleware**: Existing JWT validation

### **External Dependencies**

- **PostgreSQL**: Database for RBAC tables
- **SQLAlchemy**: ORM for database operations
- **FastAPI**: Web framework for API endpoints
- **Pydantic**: Data validation for request/response models

## **🚨 Risk Mitigation**

### **High-Risk Areas**

1. **Performance Impact**: Permission checks could slow down the system

   - **Mitigation**: Implement caching, optimize database queries, use async operations

2. **Permission Complexity**: Complex permission rules could lead to security gaps

   - **Mitigation**: Start simple, test thoroughly, implement comprehensive logging

3. **Database Migration**: Schema changes could affect existing data
   - **Mitigation**: Test migrations thoroughly, implement rollback procedures

### **Security Considerations**

1. **Permission Bypass**: Ensure no endpoints can bypass permission checks
2. **Role Escalation**: Prevent users from granting themselves elevated roles
3. **Audit Trail**: Ensure all access decisions are logged for compliance

## **📚 Documentation Requirements**

### **Technical Documentation**

- **API Reference**: Complete RBAC API documentation
- **Database Schema**: RBAC table structures and relationships
- **Integration Guide**: How to use permission decorators
- **Performance Guide**: Optimization and caching strategies

### **User Documentation**

- **Role Management**: How administrators manage user roles
- **Permission System**: Understanding the permission matrix
- **Audit Logs**: How to review access logs for compliance

## **🎯 Next Steps After Completion**

Once Task 032 is complete, the platform will be ready for:

1. **Phase 2.2**: Infrastructure & Database optimization
2. **Phase 2.3**: API & Backend services with permission integration
3. **Phase 2.5**: Multi-user architecture with SMS Router Service
4. **Enterprise Deployment**: Production deployment with compliance requirements

## **📞 Support & Resources**

### **When You Need Help**

1. **Check the logs** for error messages and stack traces
2. **Review existing code** for patterns and examples
3. **Test incrementally** - don't try to build everything at once
4. **Document issues** and solutions for future reference

### **Useful Resources**

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **RBAC Best Practices**: https://owasp.org/www-project-proactive-controls/

---

**Remember**: You're building the authorization foundation that will control access to users' personal data and enable secure multi-user deployment. Take the time to get it right - access control is critical for security and compliance.

**Good luck with the implementation!** 🚀
