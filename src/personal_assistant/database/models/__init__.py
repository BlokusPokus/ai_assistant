# Database models
# SMS Router models - import after User to avoid circular imports
from personal_assistant.sms_router.models import (
    SMSRouterConfig,
    SMSUsageLog,
    UserPhoneMapping,
)

from .ai_tasks import AITask
from .auth_tokens import AuthToken
from .base import Base
from .conversation_message import ConversationMessage

# New Conversation Schema models
from .conversation_state import ConversationState
from .event_creation_logs import EventCreationLog
from .event_processing_log import EventProcessingLog
from .events import Event
from .expense_category import ExpenseCategory
from .expenses import Expense
from .grocery_analysis import GroceryAnalysis
from .grocery_deals import GroceryDeal
from .grocery_items import GroceryItem
from .ltm_context import LTMContext
from .ltm_memory import LTMMemory
from .ltm_memory_access import LTMMemoryAccess
from .ltm_memory_relationship import LTMMemoryRelationship
from .ltm_memory_tag import LTMMemoryTag
from .memory_context_item import MemoryContextItem

# New MFA and Session Management models
from .mfa_models import MFAConfiguration, SecurityEvent, UserSession
from .note_sync_log import NoteSyncLog
from .notes import Note

# RBAC models
from .rbac_models import AccessAuditLog, Permission, Role, RolePermission, UserRole
from .recurrence_patterns import RecurrencePattern
from .reminders import Reminder
from .task_results import TaskResult
from .tasks import Task
from .user_settings import UserSetting
from .users import User

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
    "LTMContext",
    "LTMMemoryRelationship",
    "LTMMemoryAccess",
    "LTMMemoryTag",
    "EventProcessingLog",
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
    # New Conversation Schema models
    "ConversationState",
    "ConversationMessage",
    "MemoryContextItem",
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
