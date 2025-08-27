"""
Permission decorators for FastAPI endpoints.

This module provides decorators for protecting endpoints with
role-based access control (RBAC).
"""

import logging
from functools import wraps
from typing import Optional, Callable, Any, Dict
from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .permission_service import PermissionService
from personal_assistant.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


def require_permission(resource_type: str, action: str):
    """
    Decorator to require specific permission for endpoint.

    Args:
        resource_type: Type of resource (e.g., 'user', 'memory')
        action: Action being performed (e.g., 'read', 'write')

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in args
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

            # Check if user is authenticated
            if not hasattr(request.state, 'authenticated') or not request.state.authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_id = request.state.user_id

            # Get database session
            db = None
            for arg in args:
                if isinstance(arg, AsyncSession):
                    db = arg
                    break

            if not db:
                # If no session found in args, create a temporary one
                db = AsyncSessionLocal()
                should_close = True
            else:
                should_close = False

            try:
                permission_service = PermissionService(db)

                # Check permission
                has_permission = await permission_service.check_permission(
                    user_id=user_id,
                    resource_type=resource_type,
                    action=action
                )

                # Log access attempt
                await permission_service.log_access_attempt(
                    user_id=user_id,
                    resource_type=resource_type,
                    action=action,
                    granted=has_permission,
                    roles_checked=await permission_service.get_user_roles(user_id),
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )

                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required: {resource_type}:{action}"
                    )
            finally:
                # Only close if we created the session
                if should_close:
                    await db.close()

            # User has permission, proceed with the endpoint
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(role_name: str):
    """
    Decorator to require specific role for endpoint.

    Args:
        role_name: Name of required role

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in args
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

            # Check if user is authenticated
            if not hasattr(request.state, 'authenticated') or not request.state.authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_id = request.state.user_id

            # Get database session and check role
            db = None
            for arg in args:
                if isinstance(arg, AsyncSession):
                    db = arg
                    break

            if not db:
                # If no session found in args, create a temporary one
                db = AsyncSessionLocal()
                should_close = True
            else:
                should_close = False

            try:
                permission_service = PermissionService(db)

                # Check role
                has_role = await permission_service.has_role(
                    user_id=user_id,
                    role_name=role_name
                )

                # Log access attempt
                await permission_service.log_access_attempt(
                    user_id=user_id,
                    resource_type="role",
                    action="check",
                    granted=has_role,
                    roles_checked=[role_name],
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )

                if not has_role:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role required: {role_name}"
                    )
            finally:
                # Only close if we created the session
                if should_close:
                    await db.close()

            # User has role, proceed with the endpoint
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_ownership(resource_type: str, action: str, resource_id_param: str = "id"):
    """
    Decorator to require ownership of resource for endpoint.

    Args:
        resource_type: Type of resource (e.g., 'user', 'memory')
        action: Action being performed (e.g., 'read', 'write')
        resource_id_param: Name of the parameter containing the resource ID

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in args
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

            # Check if user is authenticated
            if not hasattr(request.state, 'authenticated') or not request.state.authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_id = request.state.user_id

            # Get resource ID from kwargs
            resource_id = kwargs.get(resource_id_param)
            if not resource_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Resource ID parameter '{resource_id_param}' not found"
                )

            # Get database session and check ownership
            db = AsyncSessionLocal()
            try:
                permission_service = PermissionService(db)

                # Check permission and ownership
                has_permission = await permission_service.check_permission(
                    user_id=user_id,
                    resource_type=resource_type,
                    action=action,
                    resource_id=resource_id
                )

                # Log access attempt
                await permission_service.log_access_attempt(
                    user_id=user_id,
                    resource_type=resource_type,
                    action=action,
                    resource_id=resource_id,
                    granted=has_permission,
                    roles_checked=await permission_service.get_user_roles(user_id),
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )

                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions or ownership: {resource_type}:{action}"
                    )
            finally:
                await db.close()

            # User has permission and ownership, proceed with endpoint
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_any_role(*role_names: str):
    """
    Decorator to require any of the specified roles for endpoint.

    Args:
        *role_names: Names of the roles (any one is sufficient)

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in args
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

            # Check if user is authenticated
            if not hasattr(request.state, 'authenticated') or not request.state.authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_id = request.state.user_id

            # Get database session and check roles
            db = AsyncSessionLocal()
            try:
                permission_service = PermissionService(db)
                has_any_role = False
                roles_checked = []

                for role_name in role_names:
                    has_role = await permission_service.has_role(user_id, role_name)
                    roles_checked.append(role_name)
                    if has_role:
                        has_any_role = True
                        break

                # Log access attempt
                await permission_service.log_access_attempt(
                    user_id=user_id,
                    resource_type="role",
                    action="check",
                    granted=has_any_role,
                    roles_checked=roles_checked,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )

                if not has_any_role:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"One of these roles required: {', '.join(role_names)}"
                    )
            finally:
                await db.close()

            # User has required role, proceed with endpoint
            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Convenience decorators for common permission patterns
def require_user_permission(action: str):
    """Require permission on user resources."""
    return require_permission('user', action)


def require_memory_permission(action: str):
    """Require permission on memory resources."""
    return require_permission('memory', action)


def require_task_permission(action: str):
    """Require permission on task resources."""
    return require_permission('task', action)


def require_note_permission(action: str):
    """Require permission on note resources."""
    return require_permission('note', action)


def require_event_permission(action: str):
    """Require permission on event resources."""
    return require_permission('event', action)


def require_system_permission(action: str):
    """Require permission on system resources."""
    return require_permission('system', action)


def require_rbac_permission(action: str):
    """Require permission on RBAC resources."""
    return require_permission('rbac', action)


# Convenience decorators for common role patterns
def require_admin():
    """Require administrator role."""
    return require_role('administrator')


def require_premium():
    """Require premium or administrator role."""
    return require_any_role('premium', 'administrator')


def require_authenticated():
    """Require any authenticated user (no specific role)."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in args
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

            # Check if user is authenticated
            if not hasattr(request.state, 'authenticated') or not request.state.authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # User is authenticated, proceed
            return await func(*args, **kwargs)

        return wrapper
    return decorator
