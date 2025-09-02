"""
RBAC (Role-Based Access Control) API models.

This module provides Pydantic models for RBAC API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class RoleResponse(BaseModel):
    """Response model for role information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    parent_role_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class RoleCreateRequest(BaseModel):
    """Request model for creating a new role."""
    name: str = Field(..., min_length=1, max_length=50,
                      description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    parent_role_id: Optional[int] = Field(None, description="Parent role ID")


class RoleUpdateRequest(BaseModel):
    """Request model for updating a role."""
    name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    parent_role_id: Optional[int] = Field(None, description="Parent role ID")


class PermissionResponse(BaseModel):
    """Response model for permission information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    resource_type: str
    action: str
    description: Optional[str]
    created_at: datetime


class PermissionCreateRequest(BaseModel):
    """Request model for creating a new permission."""
    name: str = Field(..., min_length=1, max_length=100,
                      description="Permission name")
    resource_type: str = Field(..., min_length=1,
                               max_length=50, description="Resource type")
    action: str = Field(..., min_length=1, max_length=50, description="Action")
    description: Optional[str] = Field(
        None, description="Permission description")


class RolePermissionResponse(BaseModel):
    """Response model for role-permission relationship."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    permission_id: int
    created_at: datetime


class RolePermissionCreateRequest(BaseModel):
    """Request model for assigning permission to role."""
    role_id: int = Field(..., description="Role ID")
    permission_id: int = Field(..., description="Permission ID")


class UserRoleResponse(BaseModel):
    """Response model for user-role relationship."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role_id: int
    is_primary: bool
    granted_by: Optional[int]
    granted_at: datetime
    expires_at: Optional[datetime]


class UserRoleCreateRequest(BaseModel):
    """Request model for assigning role to user."""
    user_id: int = Field(..., description="User ID")
    role_id: int = Field(..., description="Role ID")
    is_primary: bool = Field(
        default=False, description="Whether this is the primary role")
    expires_at: Optional[datetime] = Field(
        None, description="Role expiration date")


class AccessAuditLogResponse(BaseModel):
    """Response model for access audit log information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    resource_type: str
    resource_id: Optional[int]
    action: str
    permission_granted: bool
    roles_checked: Optional[List[str]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


class AccessAuditLogCreateRequest(BaseModel):
    """Request model for creating access audit log entry."""
    user_id: Optional[int] = Field(None, description="User ID")
    resource_type: str = Field(..., min_length=1,
                               max_length=50, description="Resource type")
    resource_id: Optional[int] = Field(None, description="Resource ID")
    action: str = Field(..., min_length=1, max_length=50,
                        description="Action performed")
    permission_granted: bool = Field(...,
                                     description="Whether permission was granted")
    roles_checked: Optional[List[str]] = Field(
        None, description="Roles that were checked")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")


class RoleListResponse(BaseModel):
    """Response model for role list."""
    roles: List[RoleResponse]
    total: int
    skip: int
    limit: int


class PermissionListResponse(BaseModel):
    """Response model for permission list."""
    permissions: List[PermissionResponse]
    total: int
    skip: int
    limit: int


class UserRoleListResponse(BaseModel):
    """Response model for user role list."""
    user_roles: List[UserRoleResponse]
    total: int
    skip: int
    limit: int


class AccessAuditLogListResponse(BaseModel):
    """Response model for access audit log list."""
    audit_logs: List[AccessAuditLogResponse]
    total: int
    skip: int
    limit: int


class RoleSearchRequest(BaseModel):
    """Request model for searching roles."""
    name: Optional[str] = Field(None, description="Filter by role name")
    parent_role_id: Optional[int] = Field(
        None, description="Filter by parent role ID")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100,
                       description="Maximum number of records to return")


class PermissionSearchRequest(BaseModel):
    """Request model for searching permissions."""
    name: Optional[str] = Field(None, description="Filter by permission name")
    resource_type: Optional[str] = Field(
        None, description="Filter by resource type")
    action: Optional[str] = Field(None, description="Filter by action")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100,
                       description="Maximum number of records to return")


class AccessAuditLogSearchRequest(BaseModel):
    """Request model for searching access audit logs."""
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    resource_type: Optional[str] = Field(
        None, description="Filter by resource type")
    action: Optional[str] = Field(None, description="Filter by action")
    permission_granted: Optional[bool] = Field(
        None, description="Filter by permission granted")
    created_after: Optional[datetime] = Field(
        None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(
        None, description="Filter by creation date")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100,
                       description="Maximum number of records to return")
