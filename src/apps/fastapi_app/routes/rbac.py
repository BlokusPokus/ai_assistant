"""
RBAC Management Routes for Role-Based Access Control.

This module provides endpoints for managing roles, permissions,
and viewing audit logs. All endpoints require appropriate permissions.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.routes.auth import get_current_user, get_db
from personal_assistant.auth.decorators import require_admin, require_rbac_permission
from personal_assistant.auth.permission_service import PermissionService
from personal_assistant.database.models.rbac_models import (
    AccessAuditLog,
    Permission,
    Role,
    UserRole,
)
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal

# Create router
router = APIRouter(prefix="/api/v1/rbac", tags=["RBAC Management"])

# Pydantic models for request/response


class RoleCreate(BaseModel):
    """Request model for creating a new role."""

    name: str
    description: Optional[str] = None
    parent_role_id: Optional[int] = None


class RoleUpdate(BaseModel):
    """Request model for updating a role."""

    description: Optional[str] = None
    parent_role_id: Optional[int] = None


class RoleResponse(BaseModel):
    """Response model for role information."""

    id: int
    name: str
    description: Optional[str]
    parent_role_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class PermissionResponse(BaseModel):
    """Response model for permission information."""

    id: int
    name: str
    resource_type: str
    action: str
    description: Optional[str]
    created_at: datetime


class UserRoleGrant(BaseModel):
    """Request model for granting a role to a user."""

    role_name: str
    is_primary: bool = False
    expires_at: Optional[datetime] = None


class UserRoleResponse(BaseModel):
    """Response model for user role information."""

    id: int
    user_id: int
    role_name: str
    is_primary: bool
    granted_by: Optional[int]
    granted_at: datetime
    expires_at: Optional[datetime]


class UserPermissionsResponse(BaseModel):
    """Response model for user permissions."""

    user_id: int
    roles: List[str]
    permissions: List[str]


class AuditLogResponse(BaseModel):
    """Response model for audit log entries."""

    id: int
    user_id: int
    resource_type: str
    resource_id: Optional[int]
    action: str
    permission_granted: bool
    roles_checked: List[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


class RoleListResponse(BaseModel):
    """Response model for list of roles."""

    roles: List[RoleResponse]
    total: int


class PermissionListResponse(BaseModel):
    """Response model for list of permissions."""

    permissions: List[PermissionResponse]
    total: int


class AuditLogListResponse(BaseModel):
    """Response model for list of audit logs."""

    logs: List[AuditLogResponse]
    total: int


# Dependency to get database session
async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


# Role Management Endpoints


@router.post("/roles", response_model=RoleResponse)
@require_admin()
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new role (administrator only).

    Args:
        role_data: Role creation data
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Created role information

    Raises:
        HTTPException: If role creation fails or role already exists
    """
    try:
        # Check if role already exists
        existing_role = await db.execute(
            select(Role).where(Role.name == role_data.name)
        )
        if existing_role.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_data.name}' already exists",
            )

        # Create new role
        new_role = Role(
            name=role_data.name,
            description=role_data.description,
            parent_role_id=role_data.parent_role_id,
        )

        db.add(new_role)
        await db.commit()
        await db.refresh(new_role)

        return RoleResponse(
            id=new_role.id,
            name=new_role.name,
            description=new_role.description,
            parent_role_id=new_role.parent_role_id,
            created_at=new_role.created_at,
            updated_at=new_role.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}",
        )


@router.get("/roles", response_model=RoleListResponse)
@require_rbac_permission("read")
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    List all roles with pagination.

    Args:
        skip: Number of roles to skip
        limit: Maximum number of roles to return
        db: Database session

    Returns:
        List of roles with total count
    """
    try:
        # Get total count
        count_stmt = select(Role)
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Get roles with pagination
        roles_stmt = select(Role).offset(skip).limit(limit)
        roles_result = await db.execute(roles_stmt)
        roles = roles_result.scalars().all()

        role_responses = [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                parent_role_id=role.parent_role_id,
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
            for role in roles
        ]

        return RoleListResponse(roles=role_responses, total=total)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list roles: {str(e)}",
        )


@router.get("/roles/{role_id}", response_model=RoleResponse)
@require_rbac_permission("read")
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get role by ID.

    Args:
        role_id: ID of the role to retrieve
        db: Database session

    Returns:
        Role information

    Raises:
        HTTPException: If role not found
    """
    try:
        role = await db.execute(select(Role).where(Role.id == role_id))
        role_obj = role.scalar_one_or_none()

        if not role_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found",
            )

        return RoleResponse(
            id=role_obj.id,
            name=role_obj.name,
            description=role_obj.description,
            parent_role_id=role_obj.parent_role_id,
            created_at=role_obj.created_at,
            updated_at=role_obj.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get role: {str(e)}",
        )


@router.put("/roles/{role_id}", response_model=RoleResponse)
@require_admin()
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update role information (administrator only).

    Args:
        role_id: ID of the role to update
        role_data: Role update data
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Updated role information

    Raises:
        HTTPException: If role not found or update fails
    """
    try:
        role = await db.execute(select(Role).where(Role.id == role_id))
        role_obj = role.scalar_one_or_none()

        if not role_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found",
            )

        # Update role fields
        if role_data.description is not None:
            role_obj.description = role_data.description
        if role_data.parent_role_id is not None:
            role_obj.parent_role_id = role_data.parent_role_id

        await db.commit()
        await db.refresh(role_obj)

        return RoleResponse(
            id=role_obj.id,
            name=role_obj.name,
            description=role_obj.description,
            parent_role_id=role_obj.parent_role_id,
            created_at=role_obj.created_at,
            updated_at=role_obj.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}",
        )


# User Role Management Endpoints


@router.post("/users/{user_id}/roles", response_model=UserRoleResponse)
@require_admin()
async def grant_role(
    user_id: int,
    role_data: UserRoleGrant,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Grant role to user (administrator only).

    Args:
        user_id: ID of the user receiving the role
        role_data: Role grant data
        current_user: Currently authenticated user
        db: Database session

    Returns:
        User role information

    Raises:
        HTTPException: If role granting fails
    """
    try:
        permission_service = PermissionService(db)

        success = await permission_service.grant_role(
            user_id=user_id,
            role_name=role_data.role_name,
            granted_by=current_user.id,
            is_primary=role_data.is_primary,
            expires_at=role_data.expires_at,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to grant role '{role_data.role_name}' to user {user_id}",
            )

        # Get the created user role
        user_role = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id
                == (
                    await db.execute(
                        select(Role.id).where(Role.name == role_data.role_name)
                    )
                ).scalar_one(),
            )
        )
        user_role_obj = user_role.scalar_one_or_none()

        if not user_role_obj:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role granted but user role not found",
            )

        return UserRoleResponse(
            id=user_role_obj.id,
            user_id=user_role_obj.user_id,
            role_name=role_data.role_name,
            is_primary=user_role_obj.is_primary,
            granted_by=user_role_obj.granted_by,
            granted_at=user_role_obj.granted_at,
            expires_at=user_role_obj.expires_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to grant role: {str(e)}",
        )


@router.delete("/users/{user_id}/roles/{role_name}")
@require_admin()
async def revoke_role(
    user_id: int,
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke role from user (administrator only).

    Args:
        user_id: ID of the user losing the role
        role_name: Name of the role to revoke
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If role revocation fails
    """
    try:
        permission_service = PermissionService(db)

        success = await permission_service.revoke_role(
            user_id=user_id, role_name=role_name, revoked_by=current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to revoke role '{role_name}' from user {user_id}",
            )

        return {"message": f"Role '{role_name}' revoked from user {user_id}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke role: {str(e)}",
        )


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
@require_rbac_permission("read")
async def get_user_permissions(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all permissions for a user including inherited roles.

    Args:
        user_id: ID of the user
        db: Database session

    Returns:
        User permissions and roles

    Raises:
        HTTPException: If user not found
    """
    try:
        permission_service = PermissionService(db)

        # Get user roles
        user_roles = await permission_service.get_user_roles(user_id)
        role_names = [role.name for role in user_roles]

        # Get user permissions
        permissions = await permission_service.get_user_permissions(user_id)

        return UserPermissionsResponse(
            user_id=user_id, roles=role_names, permissions=list(permissions)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user permissions: {str(e)}",
        )


# Permission Management Endpoints


@router.get("/permissions", response_model=PermissionListResponse)
@require_rbac_permission("read")
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    List all permissions with optional filtering.

    Args:
        skip: Number of permissions to skip
        limit: Maximum number of permissions to return
        resource_type: Filter by resource type
        action: Filter by action
        db: Database session

    Returns:
        List of permissions with total count
    """
    try:
        # Build query with filters
        conditions = []
        if resource_type:
            conditions.append(Permission.resource_type == resource_type)
        if action:
            conditions.append(Permission.action == action)

        # Get total count
        count_stmt = select(Permission).where(conditions[0] if conditions else True)
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Get permissions with pagination
        permissions_stmt = (
            select(Permission)
            .where(conditions[0] if conditions else True)
            .offset(skip)
            .limit(limit)
        )
        permissions_result = await db.execute(permissions_stmt)
        permissions = permissions_result.scalars().all()

        permission_responses = [
            PermissionResponse(
                id=perm.id,
                name=perm.name,
                resource_type=perm.resource_type,
                action=perm.action,
                description=perm.description,
                created_at=perm.created_at,
            )
            for perm in permissions
        ]

        return PermissionListResponse(permissions=permission_responses, total=total)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list permissions: {str(e)}",
        )


# Audit Log Endpoints


@router.get("/audit-logs", response_model=AuditLogListResponse)
@require_admin()
async def get_audit_logs(
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    granted: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit logs with filtering options (administrator only).

    Args:
        user_id: Filter by specific user
        resource_type: Filter by resource type
        action: Filter by action
        granted: Filter by permission result
        start_date: Filter by start date
        end_date: Filter by end date
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        db: Database session

    Returns:
        List of audit logs with total count
    """
    try:
        permission_service = PermissionService(db)

        # Get audit logs
        logs = await permission_service.get_audit_logs(
            user_id=user_id,
            resource_type=resource_type,
            action=action,
            granted=granted,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=skip,
        )

        # Convert to response models
        log_responses = [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                action=log.action,
                permission_granted=log.permission_granted,
                roles_checked=log.roles_checked or [],
                ip_address=str(log.ip_address) if log.ip_address else None,
                user_agent=log.user_agent,
                created_at=log.created_at,
            )
            for log in logs
        ]

        # Get total count (this is approximate due to filtering)
        total = len(logs) if len(logs) < limit else limit + skip

        return AuditLogListResponse(logs=log_responses, total=total)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}",
        )


# Health Check Endpoint


@router.get("/health")
async def rbac_health_check():
    """
    Health check endpoint for RBAC system.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "RBAC Management",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }
