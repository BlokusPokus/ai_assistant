"""
Authentication and Authorization Module.

This module provides comprehensive authentication and authorization
services including JWT tokens, MFA, sessions, and RBAC.
"""

from .auth_utils import AuthUtils
from .decorators import (
    require_admin,
    require_any_role,
    require_authenticated,
    require_event_permission,
    require_memory_permission,
    require_note_permission,
    require_ownership,
    require_permission,
    require_premium,
    require_rbac_permission,
    require_role,
    require_system_permission,
    require_task_permission,
    require_user_permission,
)
from .jwt_service import jwt_service
from .mfa_service import MFAService
from .password_service import password_service
from .permission_service import PermissionService
from .session_service import SessionService
from .sms_mfa import SMSMFAService

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
    "require_authenticated",
]
