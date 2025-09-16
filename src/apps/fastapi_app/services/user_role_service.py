"""
User Role Service for RBAC integration.

This service handles fetching user roles, permissions, and creating
enhanced user responses with role information.
"""

import logging
from typing import List, Optional, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from personal_assistant.auth.permission_service import PermissionService
from personal_assistant.database.models.rbac_models import Role, UserRole
from personal_assistant.database.models.users import User

logger = logging.getLogger(__name__)


class UserRoleService:
    """Service for managing user roles and permissions."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.permission_service = PermissionService(db_session)

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """
        Get all roles for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of Role objects
        """
        try:
            # Get user roles with permissions loaded
            result = await self.db.execute(
                select(Role)
                .join(UserRole, Role.id == UserRole.role_id)
                .where(UserRole.user_id == user_id)
                .options(selectinload(Role.permissions))
            )
            roles = result.scalars().all()
            
            logger.debug(f"Found {len(roles)} roles for user {user_id}")
            return roles
            
        except Exception as e:
            logger.error(f"Error fetching roles for user {user_id}: {e}")
            return []

    async def get_user_permissions(self, user_id: int) -> List[dict]:
        """
        Get all permissions for a user across all their roles.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of permission dictionaries
        """
        try:
            roles = await self.get_user_roles(user_id)
            permissions_set: Set[dict] = set()
            
            for role in roles:
                for permission in role.permissions:
                    # Convert to dict and use as set key to avoid duplicates
                    perm_dict = {
                        'id': permission.id,
                        'name': permission.name,
                        'resource_type': permission.resource_type,
                        'action': permission.action,
                        'description': permission.description,
                        'created_at': permission.created_at
                    }
                    permissions_set.add(tuple(perm_dict.items()))
            
            # Convert back to list of dicts
            permissions = [dict(perm_tuple) for perm_tuple in permissions_set]
            
            logger.debug(f"Found {len(permissions)} unique permissions for user {user_id}")
            return permissions
            
        except Exception as e:
            logger.error(f"Error fetching permissions for user {user_id}: {e}")
            return []

    async def get_primary_role(self, user_id: int) -> Optional[Role]:
        """
        Get the primary role for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Primary Role object or None
        """
        try:
            result = await self.db.execute(
                select(Role)
                .join(UserRole, Role.id == UserRole.role_id)
                .where(
                    UserRole.user_id == user_id,
                    UserRole.is_primary == True
                )
                .options(selectinload(Role.permissions))
            )
            primary_role = result.scalar_one_or_none()
            
            if primary_role:
                logger.debug(f"Primary role for user {user_id}: {primary_role.name}")
            else:
                logger.debug(f"No primary role found for user {user_id}")
                
            return primary_role
            
        except Exception as e:
            logger.error(f"Error fetching primary role for user {user_id}: {e}")
            return None

    async def check_user_permission(self, user_id: int, resource_type: str, action: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: The user ID
            resource_type: The resource type (e.g., 'user', 'system')
            action: The action (e.g., 'read', 'write', 'admin')
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            return await self.permission_service.check_permission(
                user_id=user_id,
                resource_type=resource_type,
                action=action
            )
        except Exception as e:
            logger.error(f"Error checking permission for user {user_id}: {e}")
            return False

    async def get_user_role_names(self, user_id: int) -> List[str]:
        """
        Get list of role names for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of role names
        """
        try:
            roles = await self.get_user_roles(user_id)
            return [role.name for role in roles]
        except Exception as e:
            logger.error(f"Error fetching role names for user {user_id}: {e}")
            return []

    async def is_user_admin(self, user_id: int) -> bool:
        """
        Check if user has administrator role.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if user is admin, False otherwise
        """
        try:
            role_names = await self.get_user_role_names(user_id)
            return 'administrator' in role_names
        except Exception as e:
            logger.error(f"Error checking admin status for user {user_id}: {e}")
            return False

    async def is_user_premium(self, user_id: int) -> bool:
        """
        Check if user has premium role.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if user is premium, False otherwise
        """
        try:
            role_names = await self.get_user_role_names(user_id)
            return 'premium' in role_names or 'administrator' in role_names
        except Exception as e:
            logger.error(f"Error checking premium status for user {user_id}: {e}")
            return False
