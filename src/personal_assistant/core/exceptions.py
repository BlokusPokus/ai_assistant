"""Custom exceptions for the agent core system."""

from typing import Optional


class AgentCoreError(Exception):
    """Base exception for agent core errors."""


class ConversationError(AgentCoreError):
    """Exception raised when conversation management fails."""

    def __init__(
        self, message: str, user_id: int, conversation_id: Optional[str] = None
    ):
        self.message = message
        self.user_id = user_id
        self.conversation_id = conversation_id
        super().__init__(self.message)


class AgentExecutionError(AgentCoreError):
    """Exception raised when agent execution fails."""

    def __init__(self, message: str, user_id: int, operation: Optional[str] = None):
        self.message = message
        self.user_id = user_id
        self.operation = operation
        super().__init__(self.message)


class ValidationError(AgentCoreError):
    """Exception raised when input validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[str] = None
    ):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class AgentMemoryError(AgentCoreError):
    """Exception raised when agent memory operations fail."""

    def __init__(self, message: str, operation: str, user_id: int):
        self.message = message
        self.operation = operation
        self.user_id = user_id
        super().__init__(self.message)


class ToolExecutionError(AgentCoreError):
    """Exception raised when tool execution fails."""

    def __init__(
        self, message: str, tool_name: str, user_id: int, args: Optional[dict] = None
    ):
        self.message = message
        self.tool_name = tool_name
        self.user_id = user_id
        self.args = args or {}
        super().__init__(self.message)


class LLMError(AgentCoreError):
    """Exception raised when LLM operations fail."""

    def __init__(
        self, message: str, model: Optional[str] = None, operation: Optional[str] = None
    ):
        self.message = message
        self.model = model
        self.operation = operation
        super().__init__(self.message)


class ContextError(AgentCoreError):
    """Exception raised when context management fails."""

    def __init__(self, message: str, context_type: str, user_id: int):
        self.message = message
        self.context_type = context_type
        self.user_id = user_id
        super().__init__(self.message)
