"""
Authentication and Authorization Module.

This module provides comprehensive authentication and authorization
services including JWT tokens, MFA, sessions, and RBAC.
"""

from .jwt_service import jwt_service
from .password_service import password_service
from .mfa_service import MFAService
from .sms_mfa import SMSMFAService
from .session_service import SessionService
from .auth_utils import AuthUtils
from .permission_service import PermissionService
from .decorators import (
    require_permission,
    require_role,
    require_ownership,
    require_any_role,
    require_user_permission,
    require_memory_permission,
    require_task_permission,
    require_note_permission,
    require_event_permission,
    require_system_permission,
    require_rbac_permission,
    require_admin,
    require_premium,
    require_authenticated
)

__all__ = [
    "jwt_service",
    "password_service",
    "MFAService",
    "SMSMFAService",
    "SessionService",
    "AuthUtils",
    "PermissionService",
    "require_permission",
    "require_role",
    "require_ownership",
    "require_any_role",
    "require_user_permission",
    "require_memory_permission",
    "require_task_permission",
    "require_note_permission",
    "require_event_permission",
    "require_system_permission",
    "require_rbac_permission",
    "require_admin",
    "require_premium",
    "require_authenticated"
]
