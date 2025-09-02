"""
FastAPI application models package.

This package contains Pydantic models for API requests and responses.
"""

from .users import (
    UserResponse,
    UserPublicResponse,
    UserUpdateRequest,
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
    UserListResponse,
    UserCreateRequest,
    UserDeleteRequest
)

from .phone_management import (
    PhoneNumberBase,
    PhoneNumberCreate,
    PhoneNumberUpdate,
    PhoneNumberResponse,
    PhoneNumberListResponse,
    PhoneNumberVerificationRequest,
    PhoneNumberVerificationCode,
    PhoneNumberVerificationResponse,
    PhoneNumberDeleteResponse
)

from .ltm_memory import (
    LTMMemoryResponse,
    LTMMemoryCreateRequest,
    LTMMemoryUpdateRequest,
    LTMMemoryListResponse,
    LTMMemorySearchRequest,
    LTMContextResponse,
    LTMMemoryTagResponse,
    LTMMemoryAccessResponse
)

from .conversation import (
    ConversationStateResponse,
    ConversationStateCreateRequest,
    ConversationStateUpdateRequest,
    ConversationMessageResponse,
    ConversationMessageCreateRequest,
    MemoryContextItemResponse,
    MemoryContextItemCreateRequest,
    ConversationListResponse,
    ConversationSearchRequest
)

from .rbac import (
    RoleResponse,
    RoleCreateRequest,
    RoleUpdateRequest,
    PermissionResponse,
    PermissionCreateRequest,
    RolePermissionResponse,
    RolePermissionCreateRequest,
    UserRoleResponse,
    UserRoleCreateRequest,
    AccessAuditLogResponse,
    AccessAuditLogCreateRequest,
    RoleListResponse,
    PermissionListResponse,
    UserRoleListResponse,
    AccessAuditLogListResponse,
    RoleSearchRequest,
    PermissionSearchRequest,
    AccessAuditLogSearchRequest
)

from .mfa import (
    MFAConfigurationResponse,
    MFAConfigurationCreateRequest,
    MFAConfigurationUpdateRequest,
    UserSessionResponse,
    UserSessionCreateRequest,
    SecurityEventResponse,
    SecurityEventCreateRequest,
    SecurityEventUpdateRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    UserSessionListResponse,
    SecurityEventListResponse,
    UserSessionSearchRequest,
    SecurityEventSearchRequest
)

__all__ = [
    # User models
    "UserResponse",
    "UserPublicResponse",
    "UserUpdateRequest",
    "UserPreferencesResponse",
    "UserPreferencesUpdateRequest",
    "UserListResponse",
    "UserCreateRequest",
    "UserDeleteRequest",

    # Phone management models
    "PhoneNumberBase",
    "PhoneNumberCreate",
    "PhoneNumberUpdate",
    "PhoneNumberResponse",
    "PhoneNumberListResponse",
    "PhoneNumberVerificationRequest",
    "PhoneNumberVerificationCode",
    "PhoneNumberVerificationResponse",
    "PhoneNumberDeleteResponse",

    # LTM Memory models
    "LTMMemoryResponse",
    "LTMMemoryCreateRequest",
    "LTMMemoryUpdateRequest",
    "LTMMemoryListResponse",
    "LTMMemorySearchRequest",
    "LTMContextResponse",
    "LTMMemoryTagResponse",
    "LTMMemoryAccessResponse",

    # Conversation models
    "ConversationStateResponse",
    "ConversationStateCreateRequest",
    "ConversationStateUpdateRequest",
    "ConversationMessageResponse",
    "ConversationMessageCreateRequest",
    "MemoryContextItemResponse",
    "MemoryContextItemCreateRequest",
    "ConversationListResponse",
    "ConversationSearchRequest",

    # RBAC models
    "RoleResponse",
    "RoleCreateRequest",
    "RoleUpdateRequest",
    "PermissionResponse",
    "PermissionCreateRequest",
    "RolePermissionResponse",
    "RolePermissionCreateRequest",
    "UserRoleResponse",
    "UserRoleCreateRequest",
    "AccessAuditLogResponse",
    "AccessAuditLogCreateRequest",
    "RoleListResponse",
    "PermissionListResponse",
    "UserRoleListResponse",
    "AccessAuditLogListResponse",
    "RoleSearchRequest",
    "PermissionSearchRequest",
    "AccessAuditLogSearchRequest",

    # MFA models
    "MFAConfigurationResponse",
    "MFAConfigurationCreateRequest",
    "MFAConfigurationUpdateRequest",
    "UserSessionResponse",
    "UserSessionCreateRequest",
    "SecurityEventResponse",
    "SecurityEventCreateRequest",
    "SecurityEventUpdateRequest",
    "MFASetupResponse",
    "MFAVerifyRequest",
    "MFAVerifyResponse",
    "UserSessionListResponse",
    "SecurityEventListResponse",
    "UserSessionSearchRequest",
    "SecurityEventSearchRequest"
]
