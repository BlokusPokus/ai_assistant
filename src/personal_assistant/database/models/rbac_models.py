from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from .base import Base


class Role(Base):
    """User roles with hierarchical permissions."""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("Permission", secondary="role_permissions")
    # Note: users relationship removed to avoid SQLAlchemy join condition issues
    parent_role = relationship("Role", remote_side=[id])
    child_roles = relationship("Role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(Base):
    """Granular permissions for resources."""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    resource_type = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary="role_permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource_type='{self.resource_type}', action='{self.action}')>"


class RolePermission(Base):
    """Many-to-many relationship between roles and permissions."""
    __tablename__ = 'role_permissions'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey(
        'roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey(
        'permissions.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


class UserRole(Base):
    """User-role associations with audit trail."""
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey(
        'roles.id', ondelete='CASCADE'), nullable=False)
    is_primary = Column(Boolean, default=False)
    granted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[
                        user_id], back_populates="user_roles")
    role = relationship("Role")
    # Note: granted_by relationship removed to avoid circular reference issues

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, is_primary={self.is_primary})>"


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

    def __repr__(self):
        return f"<AccessAuditLog(user_id={self.user_id}, resource_type='{self.resource_type}', action='{self.action}', granted={self.permission_granted})>"
