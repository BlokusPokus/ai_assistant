# Database models
from .base import Base
from .users import User
from .auth_tokens import AuthToken
from .ltm_memory import LTMMemory
from .memory_chunk import MemoryChunk
from .memory_metadata import MemoryMetadata
from .event_processing_log import EventProcessingLog
from .agent_logs import AgentLog
from .ai_tasks import AITask
from .task_results import TaskResult
from .grocery_items import GroceryItem
from .grocery_analysis import GroceryAnalysis
from .grocery_deals import GroceryDeal
from .expenses import Expense
from .expense_category import ExpenseCategory
from .notes import Note
from .note_sync_log import NoteSyncLog
from .events import Event
from .event_creation_logs import EventCreationLog
from .tasks import Task
from .reminders import Reminder
from .recurrence_patterns import RecurrencePattern
from .user_settings import UserSetting

# New MFA and Session Management models
from .mfa_models import MFAConfiguration, UserSession, SecurityEvent

# RBAC models
from .rbac_models import Role, Permission, RolePermission, UserRole, AccessAuditLog

# SMS Router models - import after User to avoid circular imports
from personal_assistant.sms_router.models import SMSRouterConfig, SMSUsageLog, UserPhoneMapping

# OAuth models - imported separately when needed to avoid circular imports
# from personal_assistant.oauth.models import (
#     OAuthIntegration,
#     OAuthToken,
#     OAuthScope,
#     OAuthConsent,
#     OAuthAuditLog,
#     OAuthState
# )

__all__ = [
    "Base",
    "User",
    "AuthToken",
    "LTMMemory",
    "MemoryChunk",
    "MemoryMetadata",
    "EventProcessingLog",
    "AgentLog",
    "AITask",
    "TaskResult",
    "GroceryItem",
    "GroceryAnalysis",
    "GroceryDeal",
    "Expense",
    "ExpenseCategory",
    "Note",
    "NoteSyncLog",
    "Event",
    "EventCreationLog",
    "Task",
    "Reminder",
    "RecurrencePattern",
    "UserSetting",
    "MFAConfiguration",
    "UserSession",
    "SecurityEvent",
    # RBAC models
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "AccessAuditLog",
    # SMS Router models
    "SMSRouterConfig",
    "SMSUsageLog",
    "UserPhoneMapping",
    # OAuth models - imported separately when needed to avoid circular imports
    # "OAuthIntegration",
    # "OAuthToken",
    # "OAuthScope",
    # "OAuthConsent",
    # "OAuthAuditLog",
    # "OAuthState"
]
