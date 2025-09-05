"""
Permission Service for Role-Based Access Control (RBAC).

This service handles permission checking, role management,
and audit logging for the RBAC system.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from personal_assistant.database.models.rbac_models import (
    AccessAuditLog,
    Role,
    UserRole,
)

logger = logging.getLogger(__name__)


class PermissionService:
    """Core service for permission checking and access control."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self._permission_cache: dict[str, bool] = {}  # Simple in-memory cache
        self._role_cache: dict[str, list[Any]] = {}  # Cache for user roles
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._cache_timestamps: dict[
            str, datetime
        ] = {}  # Track when cache entries were created

    async def check_permission(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if user has permission for specific action on resource.

        Args:
            user_id: ID of the user requesting access
            resource_type: Type of resource (e.g., 'user', 'memory', 'task')
            action: Action being performed (e.g., 'read', 'write', 'delete')
            resource_id: Optional specific resource ID for ownership checks
            context: Optional additional context for permission evaluation

        Returns:
            True if permission granted, False otherwise
        """
        cache_key = f"{user_id}:{resource_type}:{action}"

        # Check cache first
        if self._is_cache_valid(cache_key):
            return bool(self._permission_cache[cache_key])

        try:
            # Get user roles with permissions
            user_roles = await self.get_user_roles(user_id)

            # Check if user has any roles
            if not user_roles:
                self._cache_permission(cache_key, False)
                return False

            # Check permissions for each role
            for role in user_roles:
                for permission in role.permissions:
                    if (
                        permission.resource_type == resource_type
                        and permission.action == action
                    ):
                        # Additional ownership check for user resources
                        if resource_type == "user" and resource_id:
                            if not await self._check_ownership(
                                user_id, resource_id, context
                            ):
                                continue

                        # Permission granted
                        self._cache_permission(cache_key, True)
                        return True

            # No permission found
            self._cache_permission(cache_key, False)
            return False

        except Exception as e:
            logger.error(f"Error checking permission for user {user_id}: {e}")
            return False

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """
        Get all roles for a user with inheritance.

        Args:
            user_id: ID of the user

        Returns:
            List of Role objects including inherited roles
        """
        cache_key = f"roles:{user_id}"

        # Check cache first
        if self._is_cache_valid(cache_key):
            return list(self._role_cache[cache_key])

        try:
            # Get user's direct roles
            stmt = select(UserRole).where(UserRole.user_id == user_id)
            result = await self.db.execute(stmt)
            user_roles = result.scalars().all()

            roles = []
            for user_role in user_roles:
                # Get the role with permissions loaded
                role_stmt = (
                    select(Role)
                    .options(selectinload(Role.permissions))
                    .where(Role.id == user_role.role_id)
                )
                role_result = await self.db.execute(role_stmt)
                role = role_result.scalar_one_or_none()

                if role:
                    roles.append(role)

                    # Add inherited roles (parent roles)
                    if role.parent_role_id:
                        parent_roles = await self._get_inherited_roles(
                            role.parent_role_id
                        )
                        roles.extend(parent_roles)

            # Cache the results
            self._cache_roles(cache_key, roles)
            return roles

        except Exception as e:
            logger.error(f"Error getting roles for user {user_id}: {e}")
            return []

    async def has_role(self, user_id: int, role_name: str) -> bool:
        """
        Check if user has specific role.

        Args:
            user_id: ID of the user
            role_name: Name of the role to check

        Returns:
            True if user has the role, False otherwise
        """
        user_roles = await self.get_user_roles(user_id)
        return any(role.name == role_name for role in user_roles)

    async def grant_role(
        self,
        user_id: int,
        role_name: str,
        granted_by: int,
        is_primary: bool = False,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """
        Grant role to user with audit trail.

        Args:
            user_id: ID of the user receiving the role
            role_name: Name of the role to grant
            granted_by: ID of the user granting the role
            is_primary: Whether this is the user's primary role
            expires_at: Optional expiration date for the role

        Returns:
            True if role granted successfully, False otherwise
        """
        try:
            # Get the role
            role = await self._get_role_by_name(role_name)
            if not role:
                logger.error(f"Role '{role_name}' not found")
                return False

            # Check if user already has this role
            existing_role = await self._get_user_role(user_id, role.id)
            if existing_role:
                logger.warning(f"User {user_id} already has role '{role_name}'")
                return False

            # Create user role
            user_role = UserRole(
                user_id=user_id,
                role_id=role.id,
                is_primary=is_primary,
                granted_by=granted_by,
                expires_at=expires_at,
            )

            self.db.add(user_role)
            await self.db.commit()

            # Clear cache for this user
            self._clear_user_cache(user_id)

            logger.info(
                f"Role '{role_name}' granted to user {user_id} by user {granted_by}"
            )
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error granting role '{role_name}' to user {user_id}: {e}")
            return False

    async def revoke_role(self, user_id: int, role_name: str, revoked_by: int) -> bool:
        """
        Revoke role from user with audit trail.

        Args:
            user_id: ID of the user losing the role
            role_name: Name of the role to revoke
            revoked_by: ID of the user revoking the role

        Returns:
            True if role revoked successfully, False otherwise
        """
        try:
            # Get the role
            role = await self._get_role_by_name(role_name)
            if not role:
                logger.error(f"Role '{role_name}' not found")
                return False

            # Get the user role
            user_role = await self._get_user_role(user_id, role.id)
            if not user_role:
                logger.warning(f"User {user_id} does not have role '{role_name}'")
                return False

            # Delete the user role
            await self.db.delete(user_role)
            await self.db.commit()

            # Clear cache for this user
            self._clear_user_cache(user_id)

            logger.info(
                f"Role '{role_name}' revoked from user {user_id} by user {revoked_by}"
            )
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error revoking role '{role_name}' from user {user_id}: {e}")
            return False

    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """
        Get all permissions for a user including inheritance.

        Args:
            user_id: ID of the user

        Returns:
            Set of permission strings in format "resource_type:action"
        """
        user_roles = await self.get_user_roles(user_id)

        permissions = set()
        for role in user_roles:
            for permission in role.permissions:
                permissions.add(f"{permission.resource_type}:{permission.action}")

        return permissions

    async def log_access_attempt(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[int],
        granted: bool,
        roles_checked: List[str],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log access attempt for audit trail.

        Args:
            user_id: ID of the user attempting access
            resource_type: Type of resource being accessed
            action: Action being performed
            resource_id: Optional specific resource ID
            granted: Whether permission was granted
            roles_checked: List of role names that were checked
            ip_address: IP address of the request
            user_agent: User agent string
            context: Optional additional context
        """
        try:
            audit_log = AccessAuditLog(
                user_id=user_id,
                resource_type=resource_type,
                action=action,
                resource_id=resource_id,
                permission_granted=granted,
                roles_checked=roles_checked,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            self.db.add(audit_log)
            await self.db.commit()

            # Log to application logs as well
            log_level = logging.INFO if granted else logging.WARNING
            logger.log(
                log_level,
                f"Access attempt: user={user_id}, resource={resource_type}:{resource_id}, "
                f"action={action}, granted={granted}, roles={roles_checked}",
            )

        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")
            # Don't fail the main operation if logging fails

    async def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        granted: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AccessAuditLog]:
        """
        Get audit logs with filtering options.

        Args:
            user_id: Filter by specific user
            resource_type: Filter by resource type
            action: Filter by action
            granted: Filter by permission result
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of AccessAuditLog objects
        """
        try:
            # Build query
            conditions = []

            if user_id:
                conditions.append(AccessAuditLog.user_id == user_id)
            if resource_type:
                conditions.append(AccessAuditLog.resource_type == resource_type)
            if action:
                conditions.append(AccessAuditLog.action == action)
            if granted is not None:
                conditions.append(AccessAuditLog.permission_granted == granted)
            if start_date:
                conditions.append(AccessAuditLog.created_at >= start_date)
            if end_date:
                conditions.append(AccessAuditLog.created_at <= end_date)

            if conditions:
                stmt = (
                    select(AccessAuditLog)
                    .where(and_(*conditions))
                    .order_by(AccessAuditLog.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
            else:
                stmt = (
                    select(AccessAuditLog)
                    .order_by(AccessAuditLog.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )

            result = await self.db.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []

    # Private helper methods

    async def _get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID."""
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get role by name."""
        stmt = select(Role).where(Role.name == role_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_user_role(self, user_id: int, role_id: int) -> Optional[UserRole]:
        """Get specific user role."""
        stmt = select(UserRole).where(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_inherited_roles(self, parent_role_id: int) -> List[Role]:
        """Get all inherited roles recursively."""
        roles = []
        try:
            parent_role = await self._get_role_by_id(parent_role_id)
            if parent_role:
                roles.append(parent_role)
                # Recursively get parent's parent roles
                if parent_role.parent_role_id:
                    grandparent_roles = await self._get_inherited_roles(
                        parent_role.parent_role_id
                    )
                    roles.extend(grandparent_roles)
        except Exception as e:
            logger.error(f"Error getting inherited roles: {e}")

        return roles

    async def _check_ownership(
        self, user_id: int, resource_id: int, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if user owns the resource.

        Args:
            user_id: ID of the user
            resource_id: ID of the resource
            context: Optional context for ownership checking

        Returns:
            True if user owns the resource, False otherwise
        """
        # For user resources, check if user is accessing their own data
        if context and context.get("resource_type") == "user":
            return user_id == resource_id

        # Default: allow access (this can be extended for other resource types)
        return True

    def _cache_permission(self, key: str, value: bool) -> None:
        """Cache permission check result."""
        self._permission_cache[key] = value
        self._cache_timestamps[key] = datetime.utcnow()

    def _cache_roles(self, key: str, value: List[Role]) -> None:
        """Cache user roles."""
        self._role_cache[key] = value
        self._cache_timestamps[key] = datetime.utcnow()

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        if key not in self._cache_timestamps:
            return False

        age = datetime.utcnow() - self._cache_timestamps[key]
        return float(age.total_seconds()) < self._cache_ttl

    def _clear_user_cache(self, user_id: int) -> None:
        """Clear cache for specific user."""
        keys_to_remove = [
            k for k in self._permission_cache.keys() if k.startswith(f"{user_id}:")
        ]
        for key in keys_to_remove:
            del self._permission_cache[key]
            if key in self._cache_timestamps:
                del self._cache_timestamps[key]

        # Clear role cache
        role_cache_key = f"roles:{user_id}"
        if role_cache_key in self._role_cache:
            del self._role_cache[role_cache_key]
        if role_cache_key in self._cache_timestamps:
            del self._cache_timestamps[role_cache_key]

    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._permission_cache.clear()
        self._role_cache.clear()
        self._cache_timestamps.clear()
        logger.info("Permission service cache cleared")
