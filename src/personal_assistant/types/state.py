"""
LangGraph state definitions and related types.

📁 types/state.py
Defines the LangGraph agent state, including memory, tool calls, loop counters, etc.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional, Tuple

from ..config.logging_config import get_logger
from .messages import ToolCall

logger = get_logger("types")

# Import constants from settings
try:
    from ..config.settings import (
        DEFAULT_CONTEXT_WINDOW_SIZE,
        DEFAULT_MAX_CONVERSATION_HISTORY_SIZE,
        DEFAULT_MAX_HISTORY_SIZE,
        DEFAULT_MAX_MEMORY_CONTEXT_SIZE,
    )
except ImportError:
    # Fallback constants if settings import fails
    DEFAULT_MAX_MEMORY_CONTEXT_SIZE = 20
    DEFAULT_MAX_CONVERSATION_HISTORY_SIZE = 20
    DEFAULT_MAX_HISTORY_SIZE = 20
    DEFAULT_CONTEXT_WINDOW_SIZE = 10


@dataclass
class StateConfig:
    """Configuration for state management limits"""

    max_memory_context_size: int = DEFAULT_MAX_MEMORY_CONTEXT_SIZE
    max_conversation_history_size: int = DEFAULT_MAX_CONVERSATION_HISTORY_SIZE
    max_history_size: int = DEFAULT_MAX_HISTORY_SIZE
    context_window_size: int = DEFAULT_CONTEXT_WINDOW_SIZE
    enable_smart_pruning: bool = True


@dataclass
class AgentState:
    user_input: str
    memory_context: List[dict] = field(default_factory=list)
    history: List[Tuple[Any, Any]] = field(default_factory=list)
    step_count: int = 0
    focus: List[str] = field(default_factory=list)
    conversation_history: list = field(default_factory=list)
    last_tool_result: Any = None
    config: StateConfig = field(default_factory=StateConfig)

    # Lazy evaluation flags
    _memory_context_needs_pruning: bool = False
    _conversation_history_needs_pruning: bool = False
    _history_needs_pruning: bool = False

    def __post_init__(self):
        """Initialize state and extract focus areas from user input if provided"""
        # Automatically extract focus areas from user input if provided
        if self.user_input and not self.focus:
            self._update_focus_areas(self.user_input)

    def _apply_size_limits(self):
        """Apply size limits to all arrays only when needed (lazy evaluation)"""
        if (
            self._memory_context_needs_pruning
            and len(self.memory_context) > self.config.max_memory_context_size
        ):
            self._prune_memory_context()
            self._memory_context_needs_pruning = False

        if (
            self._conversation_history_needs_pruning
            and len(self.conversation_history)
            > self.config.max_conversation_history_size
        ):
            self._prune_conversation_history()
            self._conversation_history_needs_pruning = False

        if (
            self._history_needs_pruning
            and len(self.history) > self.config.max_history_size
        ):
            self._prune_history()
            self._history_needs_pruning = False

    def _prune_memory_context(self):
        """Prune memory_context to size limit with smart pruning if enabled"""
        if self.config.enable_smart_pruning:
            self._smart_prune_memory_context()
        else:
            self._simple_prune_memory_context()

    def _simple_prune_memory_context(self):
        """Simple FIFO pruning of memory_context"""
        excess = len(self.memory_context) - self.config.max_memory_context_size
        if excess > 0:
            self.memory_context = self.memory_context[excess:]
            logger.debug(f"Pruned {excess} items from memory_context")

    def _smart_prune_memory_context(self):
        """Smart pruning based on relevance and recency"""
        if len(self.memory_context) <= self.config.max_memory_context_size:
            return

        # Score items by relevance and recency
        scored_items = self._score_memory_context_items()

        # Keep top items by score
        self.memory_context = [
            item
            for _, item in sorted(scored_items, reverse=True)[
                : self.config.max_memory_context_size
            ]
        ]
        logger.debug(f"Smart pruned memory_context to {len(self.memory_context)} items")

    def _score_memory_context_items(self) -> List[Tuple[float, dict]]:
        """Score memory context items by relevance and recency"""
        scored_items = []

        for i, item in enumerate(self.memory_context):
            score = self._calculate_context_score(item, i)
            scored_items.append((score, item))

        return scored_items

    def _calculate_context_score(self, item: dict, position: int) -> float:
        """Calculate relevance score for a context item"""
        # Base score from position (recency)
        recency_score = 1.0 / (position + 1)

        # Relevance score based on content type
        relevance_score = self._calculate_relevance_score(item)

        # Combine scores (weighted average)
        return 0.7 * recency_score + 0.3 * relevance_score

    def _calculate_relevance_score(self, item: dict) -> float:
        """Calculate relevance score based on content type and content"""
        content_type = item.get("role", "unknown")

        # Higher scores for more relevant content types
        type_scores = {
            "user": 1.0,  # User input is most relevant
            "assistant": 0.8,  # Assistant responses are relevant
            "tool": 0.6,  # Tool results are moderately relevant
            "memory": 0.7,  # Memory items are relevant
            "system": 0.5,  # System messages are less relevant
            "rag": 0.6,  # RAG documents are moderately relevant
            "ltm": 0.7,  # Long-term memory is relevant
        }

        base_score = type_scores.get(content_type, 0.5)

        # Additional scoring based on content
        content = item.get("content", "")
        if self.user_input and self.user_input.lower() in content.lower():
            base_score += 0.2  # Bonus for content matching current input

        return min(base_score, 1.0)  # Cap at 1.0

    def _prune_conversation_history(self):
        """Prune conversation_history to size limit with simple summarization"""
        self._simple_prune_conversation_history()

    def _simple_prune_conversation_history(self):
        """Simple FIFO pruning of conversation_history"""
        excess = (
            len(self.conversation_history) - self.config.max_conversation_history_size
        )
        if excess > 0:
            self.conversation_history = self.conversation_history[excess:]
            logger.debug(f"Pruned {excess} items from conversation_history")

    def _prune_history(self):
        """Prune history to size limit"""
        excess = len(self.history) - self.config.max_history_size
        if excess > 0:
            self.history = self.history[excess:]
            logger.debug(f"Pruned {excess} items from history")

    def add_tool_result(self, tool_call: ToolCall, result: Any):
        """Record tool execution and result in conversation history"""
        self.step_count += 1
        self.last_tool_result = result

        # Add tool execution to conversation history
        new_items = [
            {
                "role": "assistant",
                "content": f"I'll help you with that using the {tool_call.name} tool.",
            },
            {"role": "tool", "name": tool_call.name, "content": result},
        ]

        self.conversation_history.extend(new_items)

        # Mark that pruning might be needed (lazy evaluation)
        if len(self.conversation_history) > self.config.max_conversation_history_size:
            self._conversation_history_needs_pruning = True

    def get_context_window(self, max_items: int = None) -> List[Tuple[Any, Any]]:
        """Gets recent history for context window with size limit"""
        if max_items is None:
            max_items = self.config.context_window_size

        return self.history[-max_items:]

    def get_optimized_context(self) -> dict:
        """Get optimized context for LLM injection"""
        # Apply pruning if needed before returning context
        self._apply_size_limits()

        return {
            "memory_context": self._get_optimized_memory_context(),
            "conversation_history": self._get_optimized_conversation_history(),
            "focus": self.focus,
            "step_count": self.step_count,
        }

    def _get_optimized_memory_context(self) -> List[dict]:
        """Get optimized memory context for injection"""
        # Apply pruning if needed
        if self._memory_context_needs_pruning:
            self._apply_size_limits()

        # Score and prioritize context items
        scored_items = self._score_memory_context_items()
        return [
            item
            for _, item in sorted(scored_items, reverse=True)[
                : self.config.max_memory_context_size
            ]
        ]

    def _get_optimized_conversation_history(self) -> List[dict]:
        """Get optimized conversation history for injection"""
        # Apply pruning if needed
        if self._conversation_history_needs_pruning:
            self._apply_size_limits()

        # Return fixed window size
        if len(self.conversation_history) <= self.config.context_window_size:
            return self.conversation_history
        return self.conversation_history[-self.config.context_window_size :]

    # Override list methods to set pruning flags instead of immediate pruning
    def _extend_memory_context(self, items: List[dict]):
        """Extend memory_context and mark for potential pruning"""
        self.memory_context.extend(items)
        if len(self.memory_context) > self.config.max_memory_context_size:
            self._memory_context_needs_pruning = True

    def _append_memory_context(self, item: dict):
        """Append to memory_context and mark for potential pruning"""
        self.memory_context.append(item)
        if len(self.memory_context) > self.config.max_memory_context_size:
            self._memory_context_needs_pruning = True

    def _extend_conversation_history(self, items: List[dict]):
        """Extend conversation_history and mark for potential pruning"""
        self.conversation_history.extend(items)
        if len(self.conversation_history) > self.config.max_conversation_history_size:
            self._conversation_history_needs_pruning = True

    def _append_conversation_history(self, item: dict):
        """Append to conversation_history and mark for potential pruning"""
        self.conversation_history.append(item)
        if len(self.conversation_history) > self.config.max_conversation_history_size:
            self._conversation_history_needs_pruning = True

    def reset_for_new_message(self, user_input: str) -> None:
        """
        Reset the state for a new user message.

        This method safely resets the agent state for a new conversation turn, ensuring
        that force finish resets for each individual user message rather than persisting
        across the conversation cycle.

        Args:
            user_input (str): The new user input message

        Raises:
            ValueError: If user_input is empty, None, or not a string

        Example:
            >>> state.reset_for_new_message("Hello, how can you help me today?")
            >>> print(f"State reset with {state.step_count} steps and focus: {state.focus}")
        """
        # Input validation
        if not user_input or not isinstance(user_input, str):
            logger.error(
                f"reset_for_new_message called with invalid user_input: {type(user_input)} - {user_input}"
            )
            raise ValueError(
                f"user_input must be a non-empty string, got: {type(user_input)}"
            )

        if user_input.strip() == "":
            logger.error(
                "reset_for_new_message called with empty or whitespace-only user_input"
            )
            raise ValueError("user_input cannot be empty or contain only whitespace")

        try:
            # Store original values for potential rollback
            original_user_input = self.user_input
            original_step_count = self.step_count
            original_last_tool_result = self.last_tool_result
            original_focus = self.focus.copy() if self.focus else []

            # Reset core state attributes
            self.user_input = user_input
            self.step_count = 0
            self.last_tool_result = None

            logger.debug(
                f"Reset state attributes for new message: step_count={self.step_count}, last_tool_result={self.last_tool_result}"
            )

            # Update focus areas based on new user input
            try:
                self._update_focus_areas(user_input)
                logger.debug(f"Successfully updated focus areas: {self.focus}")
            except Exception as e:
                logger.warning(f"Failed to update focus areas for '{user_input}': {e}")
                # Rollback focus areas to original state
                self.focus = original_focus
                logger.info(
                    "Rolled back focus areas to previous state due to update failure"
                )

            logger.info(
                f"Successfully reset state for new user message: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'"
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during state reset for message '{user_input[:50]}...': {e}"
            )
            # Attempt to rollback to previous state
            try:
                self.user_input = original_user_input
                self.step_count = original_step_count
                self.last_tool_result = original_last_tool_result
                self.focus = original_focus
                logger.info(
                    "Successfully rolled back state to previous values due to reset failure"
                )
            except Exception as rollback_error:
                logger.error(
                    f"Failed to rollback state after reset error: {rollback_error}"
                )
                # Set to safe defaults if rollback fails
                self.user_input = user_input
                self.step_count = 0
                self.last_tool_result = None
                self.focus = ["general"]
                logger.warning("Set state to safe defaults after rollback failure")

            # Re-raise the original error for caller to handle
            raise

    def _update_focus_areas(self, user_input: str):
        """
        Update focus areas based on user input to improve LTM retrieval.

        Args:
            user_input: The user's input message
        """
        try:
            # Try to import tag suggestions
            try:
                from ..constants.tags import get_tag_suggestions

                suggested_tags = get_tag_suggestions(user_input)
                logger.debug(f"Tag suggestions for '{user_input}': {suggested_tags}")

                # Update focus areas with relevant tags
                if suggested_tags:
                    # Keep only the most relevant tags (max 5)
                    self.focus = suggested_tags[:5]
                    logger.debug(f"Updated focus areas: {self.focus}")
                else:
                    # Fallback to general focus if no specific tags found
                    self.focus = ["general"]
                    logger.debug("No tag suggestions found, using general focus")

            except ImportError:
                logger.debug("Tag system not available, using basic keyword extraction")
                self._extract_basic_focus(user_input)

        except Exception as e:
            logger.warning(f"Error updating focus areas: {e}")
            # Fallback to basic extraction
            self._extract_basic_focus(user_input)

    def _extract_basic_focus(self, user_input: str):
        """
        Basic focus area extraction when tag system is not available.

        Args:
            user_input: The user's input message
        """
        input_lower = user_input.lower()
        basic_focus = []

        # Simple keyword-based focus extraction
        if any(word in input_lower for word in ["email", "mail", "gmail"]):
            basic_focus.append("email")
        if any(word in input_lower for word in ["meeting", "appointment", "call"]):
            basic_focus.append("meeting")
        if any(word in input_lower for word in ["work", "job", "office"]):
            basic_focus.append("work")
        if any(word in input_lower for word in ["personal", "private", "family"]):
            basic_focus.append("personal")
        if any(word in input_lower for word in ["important", "urgent", "critical"]):
            basic_focus.append("important")
        if any(word in input_lower for word in ["delete", "remove", "trash"]):
            basic_focus.append("delete")
        if any(word in input_lower for word in ["create", "make", "add"]):
            basic_focus.append("create")
        if any(word in input_lower for word in ["schedule", "calendar", "time"]):
            basic_focus.append("schedule")

        # Always add general if no specific focus areas found
        if not basic_focus:
            basic_focus.append("general")

        self.focus = basic_focus[:5]  # Limit to 5 focus areas
        logger.debug(f"Extracted basic focus areas: {basic_focus}")

    def add_focus_area(self, focus_area: str):
        """
        Add a focus area to the current focus list.

        Args:
            focus_area: The focus area to add
        """
        if focus_area not in self.focus:
            self.focus.append(focus_area)
            # Keep focus areas manageable
            if len(self.focus) > 5:
                self.focus = self.focus[-5:]
            logger.debug(f"Added focus area: {focus_area}")

    def remove_focus_area(self, focus_area: str):
        """
        Remove a focus area from the current focus list.

        Args:
            focus_area: The focus area to remove
        """
        if focus_area in self.focus:
            self.focus.remove(focus_area)
            logger.debug(f"Removed focus area: {focus_area}")

    def get_focus_summary(self) -> str:
        """
        Get a summary of current focus areas for logging/debugging.

        Returns:
            String summary of focus areas
        """
        if not self.focus:
            return "No focus areas set"
        return f"Focus areas: {', '.join(self.focus)}"

    @classmethod
    def from_summary(cls, summary: str) -> "AgentState":
        """
        Create an AgentState from a fallback summary.

        This method safely reconstructs an AgentState from either a comprehensive JSON summary
        or a basic string summary, with proper error handling and validation.

        Args:
            summary (str): Summary of previous conversation (can be JSON or string)

        Returns:
            AgentState: Reconstructed state with summary context, or default state on error

        Raises:
            ValueError: If summary is empty, None, or contains invalid data

        Example:
            >>> state = AgentState.from_summary('{"user_input": "Hello", "focus": ["greeting"]}')
            >>> print(f"State created with {len(state.memory_context)} memory items")
        """
        # Input validation
        if not summary or not isinstance(summary, str):
            logger.error(
                f"from_summary called with invalid summary: {type(summary)} - {summary}"
            )
            raise ValueError(
                f"summary must be a non-empty string, got: {type(summary)}"
            )

        if summary.strip() == "":
            logger.error("from_summary called with empty or whitespace-only summary")
            raise ValueError("summary cannot be empty or contain only whitespace")

        try:
            # Try to parse as comprehensive summary JSON
            summary_data = json.loads(summary)

            if not isinstance(summary_data, dict):
                logger.warning(
                    f"from_summary: JSON summary is not a dict, treating as basic summary. Type: {type(summary_data)}"
                )
                # Fallback to basic summary
                return cls._create_basic_summary_state(summary)

            if "user_input" in summary_data:
                # This is a comprehensive summary
                logger.debug("from_summary: Parsing comprehensive JSON summary")

                # Handle backward compatibility for old state format

                # Validate critical fields before creating state
                validated_data = cls._validate_summary_data(summary_data)
                return cls.from_dict(validated_data)
            else:
                # Fallback to basic summary
                logger.debug(
                    "from_summary: JSON summary missing user_input, treating as basic summary"
                )
                return cls._create_basic_summary_state(summary)

        except json.JSONDecodeError as e:
            # This is a basic summary string
            logger.debug(
                f"from_summary: Summary is not valid JSON, treating as basic string: {e}"
            )
            return cls._create_basic_summary_state(summary)
        except Exception as e:
            logger.error(f"from_summary: Unexpected error parsing summary: {e}")
            # Return a safe default state
            return cls._create_basic_summary_state(summary)

    @classmethod
    def _create_basic_summary_state(cls, summary: str) -> "AgentState":
        """
        Create a basic AgentState from a string summary.

        Args:
            summary (str): Basic string summary

        Returns:
            AgentState: Basic state with summary in memory context
        """
        logger.debug(f"Creating basic summary state with content: {summary[:100]}...")
        return cls(
            user_input="",  # will be overwritten by the new input
            memory_context=[{"role": "system", "content": summary}],
            history=[],
            step_count=0,
            focus=[],
            conversation_history=[],
        )

    @classmethod
    def _validate_summary_data(cls, data: dict) -> dict:
        """
        Validate and sanitize summary data before creating AgentState.

        Args:
            data (dict): Raw summary data

        Returns:
            dict: Validated and sanitized data
        """
        logger.debug("Validating summary data structure")

        # Ensure required fields are present with proper types
        validated_data = data.copy()

        # Validate and set default for user_input
        if "user_input" not in validated_data or not isinstance(
            validated_data["user_input"], str
        ):
            logger.warning(
                "Summary data missing or invalid user_input, setting to empty string"
            )
            validated_data["user_input"] = ""

        # Validate and set defaults for list fields
        for field_name, default_value in [
            ("memory_context", []),
            ("history", []),
            ("focus", []),
            ("conversation_history", []),
        ]:
            if field_name not in validated_data or not isinstance(
                validated_data[field_name], list
            ):
                logger.warning(
                    f"Summary data missing or invalid {field_name}, setting to default"
                )
                validated_data[field_name] = default_value

        # Validate and set defaults for scalar fields
        if "step_count" not in validated_data or not isinstance(
            validated_data["step_count"], int
        ):
            logger.warning("Summary data missing or invalid step_count, setting to 0")
            validated_data["step_count"] = 0

        if "last_tool_result" not in validated_data:
            validated_data["last_tool_result"] = None

        logger.debug("Summary data validation completed successfully")
        return validated_data

    @classmethod
    def from_dict(cls, data: dict) -> "AgentState":
        """
        Create an AgentState from a dictionary with config.

        This method safely creates an AgentState from a dictionary, with proper validation
        and error handling for all required fields.

        Args:
            data (dict): Dictionary containing state data

        Returns:
            AgentState: Reconstructed state from dictionary, or default state on error

        Raises:
            ValueError: If data is not a dictionary or contains invalid data types

        Example:
            >>> state_data = {"user_input": "Hello", "focus": ["greeting"]}
            >>> state = AgentState.from_dict(state_data)
        """
        # Input validation
        if not isinstance(data, dict):
            logger.error(f"from_dict called with invalid data type: {type(data)}")
            raise ValueError(f"data must be a dictionary, got: {type(data)}")

        try:
            # Extract and validate config
            config_data = data.get("config", {})
            if not isinstance(config_data, dict):
                logger.warning("from_dict: Invalid config data type, using defaults")
                config_data = {}

            config = StateConfig(
                max_memory_context_size=config_data.get(
                    "max_memory_context_size", DEFAULT_MAX_MEMORY_CONTEXT_SIZE
                ),
                max_conversation_history_size=config_data.get(
                    "max_conversation_history_size",
                    DEFAULT_MAX_CONVERSATION_HISTORY_SIZE,
                ),
                max_history_size=config_data.get(
                    "max_history_size", DEFAULT_MAX_HISTORY_SIZE
                ),
                context_window_size=config_data.get(
                    "context_window_size", DEFAULT_CONTEXT_WINDOW_SIZE
                ),
                enable_smart_pruning=config_data.get("enable_smart_pruning", True),
            )

            # Remove config from data to avoid conflicts
            state_data = {k: v for k, v in data.items() if k != "config"}
            state_data["config"] = config

            # Ensure required fields are present with proper types
            if "user_input" not in state_data or not isinstance(
                state_data["user_input"], str
            ):
                logger.warning(
                    "from_dict: Missing or invalid user_input, setting to empty string"
                )
                state_data["user_input"] = ""

            if "memory_context" not in state_data or not isinstance(
                state_data["memory_context"], list
            ):
                logger.warning(
                    "from_dict: Missing or invalid memory_context, setting to empty list"
                )
                state_data["memory_context"] = []

            if "history" not in state_data or not isinstance(
                state_data["history"], list
            ):
                logger.warning(
                    "from_dict: Missing or invalid history, setting to empty list"
                )
                state_data["history"] = []

            if "step_count" not in state_data or not isinstance(
                state_data["step_count"], int
            ):
                logger.warning("from_dict: Missing or invalid step_count, setting to 0")
                state_data["step_count"] = 0

            if "focus" not in state_data or not isinstance(state_data["focus"], list):
                logger.warning(
                    "from_dict: Missing or invalid focus, setting to empty list"
                )
                state_data["focus"] = []

            if "conversation_history" not in state_data or not isinstance(
                state_data["conversation_history"], list
            ):
                logger.warning(
                    "from_dict: Missing or invalid conversation_history, setting to empty list"
                )
                state_data["conversation_history"] = []

            if "last_tool_result" not in state_data:
                state_data["last_tool_result"] = None

            logger.debug("from_dict: Successfully validated all required fields")
            return cls(**state_data)

        except (TypeError, ValueError) as e:
            logger.error(f"from_dict: Data type or value error: {e}")
            # Return a default AgentState if creation fails due to data issues
            return cls(user_input="")
        except Exception as e:
            logger.error(f"from_dict: Unexpected error creating AgentState: {e}")
            # Return a default AgentState if creation fails
            return cls(user_input="")

    def _make_json_safe(self, value: Any) -> Any:
        """Convert a value to JSON-safe format for serialization."""
        if value is None:
            return None

        try:
            # Test if the value is JSON-serializable
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            # If not serializable, convert to string
            try:
                return str(value)
            except Exception:
                # If even string conversion fails, return None
                return None

    def to_dict(self) -> dict:
        """Convert state to dictionary with size limits applied"""
        self._apply_size_limits()

        return {
            "user_input": self.user_input,
            "memory_context": self.memory_context,
            "step_count": self.step_count,
            "focus": self.focus,
            "conversation_history": self.conversation_history,
            "timestamp": datetime.now().isoformat(),  # Add timestamp
        }
