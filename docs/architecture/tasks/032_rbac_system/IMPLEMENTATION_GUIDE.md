# 🔐 RBAC System - Implementation Guide

## **🎯 Overview**

This guide provides step-by-step instructions for implementing the Role-Based Access Control (RBAC) system for the Personal Assistant TDAH platform.

## **🚀 Implementation Steps**

### **Step 1: Create RBAC Database Models**

Create `src/personal_assistant/database/models/rbac_models.py`:

```python
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Text, ARRAY, INET
from sqlalchemy.orm import relationship
from .base import Base

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("Permission", secondary="role_permissions")
    users = relationship("User", secondary="user_roles")
    parent_role = relationship("Role", remote_side=[id])
    child_roles = relationship("Role")

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    resource_type = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary="role_permissions")

class UserRole(Base):
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

### **Step 2: Update User Model**

Add role relationships to `src/personal_assistant/database/models/users.py`:

```python
# Add these relationships to the User class
user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
access_audit_logs = relationship("AccessAuditLog", back_populates="user", cascade="all, delete-orphan")

# Add these fields
default_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
role_assigned_at = Column(DateTime, nullable=True)
role_assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)
```

### **Step 3: Create Permission Service**

Create `src/personal_assistant/auth/permission_service.py`:

```python
from typing import List, Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from personal_assistant.database.models.rbac_models import Role, Permission, UserRole, AccessAuditLog

class PermissionService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self._permission_cache = {}

    async def check_permission(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[int] = None
    ) -> bool:
        """Check if user has permission for specific action on resource."""
        cache_key = f"{user_id}:{resource_type}:{action}"

        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]

        # Get user roles
        user_roles = await self.get_user_roles(user_id)

        # Check permissions for each role
        for role in user_roles:
            for permission in role.permissions:
                if (permission.resource_type == resource_type and
                    permission.action == action):
                    self._permission_cache[cache_key] = True
                    return True

        self._permission_cache[cache_key] = False
        return False

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a user with inheritance."""
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        result = await self.db.execute(stmt)
        user_roles = result.scalars().all()

        roles = []
        for user_role in user_roles:
            role = user_role.role
            roles.append(role)

            # Add inherited roles
            if role.parent_role_id:
                parent_role = await self._get_role_by_id(role.parent_role_id)
                if parent_role:
                    roles.append(parent_role)

        return roles

    async def has_role(self, user_id: int, role_name: str) -> bool:
        """Check if user has specific role."""
        user_roles = await self.get_user_roles(user_id)
        return any(role.name == role_name for role in user_roles)

    async def grant_role(self, user_id: int, role_name: str, granted_by: int) -> bool:
        """Grant role to user with audit trail."""
        try:
            role = await self._get_role_by_name(role_name)
            if not role:
                return False

            user_role = UserRole(
                user_id=user_id,
                role_id=role.id,
                granted_by=granted_by
            )

            self.db.add(user_role)
            await self.db.commit()

            # Clear cache for this user
            self._clear_user_cache(user_id)
            return True

        except Exception:
            await self.db.rollback()
            return False

    async def log_access_attempt(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[int],
        granted: bool,
        roles_checked: List[str],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Log access attempt for audit trail."""
        audit_log = AccessAuditLog(
            user_id=user_id,
            resource_type=resource_type,
            action=action,
            resource_id=resource_id,
            permission_granted=granted,
            roles_checked=roles_checked,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.db.add(audit_log)
        await self.db.commit()

    def _clear_user_cache(self, user_id: int):
        """Clear permission cache for specific user."""
        keys_to_remove = [k for k in self._permission_cache.keys() if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self._permission_cache[key]

    async def _get_role_by_id(self, role_id: int) -> Optional[Role]:
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_role_by_name(self, role_name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == role_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
```

### **Step 4: Create Permission Decorators**

Create `src/personal_assistant/auth/decorators.py`:

```python
from functools import wraps
from typing import Optional
from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .permission_service import PermissionService
from personal_assistant.database.models.users import User
from apps.fastapi_app.routes.auth import get_current_user

def require_permission(resource_type: str, action: str):
    """Decorator to require specific permission for endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )

            # Get current user
            current_user = get_current_user(request)

            # Check permission
            db = request.state.db if hasattr(request.state, 'db') else None
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not found"
                )

            permission_service = PermissionService(db)
            has_permission = await permission_service.check_permission(
                current_user["user_id"], resource_type, action
            )

            if not has_permission:
                # Log access attempt
                await permission_service.log_access_attempt(
                    user_id=current_user["user_id"],
                    resource_type=resource_type,
                    action=action,
                    resource_id=None,
                    granted=False,
                    roles_checked=[],
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

            # Log successful access
            await permission_service.log_access_attempt(
                user_id=current_user["user_id"],
                resource_type=resource_type,
                action=action,
                resource_id=None,
                granted=True,
                roles_checked=[],
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role_name: str):
    """Decorator to require specific role for endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Similar implementation to require_permission
            # but checks for specific role instead of permission
            pass
        return wrapper
    return decorator
```

### **Step 5: Create RBAC Routes**

Create `src/apps/fastapi_app/routes/rbac.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from personal_assistant.database.models.users import User
from personal_assistant.database.models.rbac_models import Role, Permission, UserRole
from personal_assistant.auth.permission_service import PermissionService
from apps.fastapi_app.routes.auth import get_current_user, get_db

router = APIRouter(prefix="/api/v1/rbac", tags=["RBAC"])

@router.post("/users/{user_id}/roles/{role_name}")
@require_role("administrator")
async def grant_role(
    user_id: int,
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Grant role to user (admin only)."""
    permission_service = PermissionService(db)

    success = await permission_service.grant_role(
        user_id=user_id,
        role_name=role_name,
        granted_by=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to grant role"
        )

    return {"message": f"Role {role_name} granted to user {user_id}"}

@router.get("/users/{user_id}/permissions")
@require_role("administrator")
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all permissions for a user (admin only)."""
    permission_service = PermissionService(db)
    user_roles = await permission_service.get_user_roles(user_id)

    permissions = set()
    for role in user_roles:
        for permission in role.permissions:
            permissions.add(f"{permission.resource_type}:{permission.action}")

    return {"user_id": user_id, "permissions": list(permissions)}
```

### **Step 6: Create Database Migration**

Create `src/personal_assistant/database/migrations/002_add_rbac_system.sql`:

```sql
-- Create RBAC tables
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_role_id INTEGER REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

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

CREATE TABLE access_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER NULL,
    action VARCHAR(50) NOT NULL,
    permission_granted BOOLEAN NOT NULL,
    roles_checked TEXT[],
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_permissions_resource_action ON permissions(resource_type, action);
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_access_audit_logs_user_id ON access_audit_logs(user_id);
CREATE INDEX idx_access_audit_logs_created_at ON access_audit_logs(created_at);

-- Insert initial roles
INSERT INTO roles (name, description) VALUES
('user', 'Standard user with basic permissions'),
('premium', 'Premium user with extended permissions'),
('administrator', 'System administrator with full access');

-- Insert initial permissions
INSERT INTO permissions (name, resource_type, action, description) VALUES
('user:read', 'user', 'read', 'Read user profile'),
('user:write', 'user', 'write', 'Write user profile'),
('memory:read', 'memory', 'read', 'Read user memories'),
('memory:write', 'memory', 'write', 'Write user memories'),
('system:read', 'system', 'read', 'Read system information'),
('system:write', 'system', 'write', 'Write system configuration');

-- Assign permissions to roles
INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4),  -- user role
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5),  -- premium role
(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6);  -- administrator role
```

### **Step 7: Update Main Application**

Update `src/apps/fastapi_app/main.py`:

```python
# Add RBAC router
from apps.fastapi_app.routes import rbac

# Include RBAC router
app.include_router(rbac.router)
```

### **Step 8: Update Models Init**

Update `src/personal_assistant/database/models/__init__.py`:

```python
# Add RBAC models
from .rbac_models import Role, Permission, UserRole, AccessAuditLog

__all__ = [
    # ... existing models ...
    "Role",
    "Permission",
    "UserRole",
    "AccessAuditLog"
]
```

## **🧪 Testing**

### **Unit Tests**

Create `tests/test_auth/test_permission_service.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from personal_assistant.auth.permission_service import PermissionService

@pytest.mark.asyncio
async def test_check_permission():
    # Test permission checking logic
    pass

@pytest.mark.asyncio
async def test_get_user_roles():
    # Test role retrieval with inheritance
    pass

@pytest.mark.asyncio
async def test_has_role():
    # Test role checking
    pass
```

### **Integration Tests**

Test the complete RBAC flow:

1. Create user with role
2. Test permission checking
3. Test role inheritance
4. Test audit logging

## **🚀 Next Steps**

After implementing the RBAC system:

1. **Test thoroughly** - ensure all permission checks work correctly
2. **Performance testing** - verify permission checks are fast
3. **Security testing** - ensure no permission bypasses are possible
4. **Documentation** - create user guides for role management
5. **Integration** - integrate with existing endpoints using decorators

## **🔍 Key Implementation Notes**

- **Start simple** - implement basic roles and permissions first
- **Test incrementally** - test each component as you build it
- **Performance matters** - use caching for frequently checked permissions
- **Security first** - never bypass permission checks
- **Log everything** - maintain complete audit trails for compliance
