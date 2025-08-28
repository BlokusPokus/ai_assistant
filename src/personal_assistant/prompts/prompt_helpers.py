"""
Internal helper functions for prompt building.

📁 prompts/prompt_helpers.py
Contains utility functions and helper methods used by the prompt builder
that don't contain actual prompt text or user-facing content.
"""

import re
from typing import Dict, List, Any
from ..config.logging_config import get_logger

logger = get_logger("prompts")


class PromptHelpers:
    """
    Helper class containing utility functions for prompt building.

    This class contains methods that:
    - Extract and validate information from state
    - Calculate estimates and predictions
    - Provide decision support logic
    - Handle focus area management
    - Manage note context validation

    These methods do NOT contain prompt text - they are pure utility functions.
    """

    @staticmethod
    def extract_main_task(user_input: str) -> str:
        """Extract the main task from user input."""
        if len(user_input) > 300:
            return user_input[:300] + "..."
        return user_input

    @staticmethod
    def validate_note_context(conversation_history: list, last_tool_result: Any) -> Dict[str, str]:
        """Validate and extract the note context from conversation history."""
        note_id = None
        note_topic = "Unknown"

        for entry in conversation_history[-5:]:
            if entry["role"] == "user" and "note" in entry["content"].lower():
                if "interview" in entry["content"].lower():
                    note_topic = "Master the Interview"

                # Extract note ID from tool results or assistant responses
                match = re.search(
                    r'note with ID: ([a-f0-9\-]+)', str(last_tool_result))
                if match:
                    note_id = match.group(1)
                elif "note_id" in str(entry["content"]):
                    match = re.search(
                        r'note with ID \'([a-f0-9\-]+)\'', entry["content"])
                    if match:
                        note_id = match.group(1)

        return {"note_id": note_id, "note_topic": note_topic}

    @staticmethod
    def identify_priority_tasks(step_count: int, last_tool_result: Any, note_topic: str) -> str:
        """Identify priority tasks based on current state."""
        if step_count == 0:
            return f"Complete the current request: {note_topic}"
        elif last_tool_result:
            return f"Continue working on {note_topic}"
        else:
            return f"Address the user's request: {note_topic}"

    @staticmethod
    def identify_urgent_tasks(user_input: str, note_topic: str) -> str:
        """Identify urgent tasks."""
        if "schedule" in user_input.lower() or "meeting" in user_input.lower():
            return "Scheduling and time-sensitive tasks"
        elif "email" in user_input.lower() or "message" in user_input.lower():
            return "Communication tasks"
        else:
            return f"Current user request: {note_topic}"

    @staticmethod
    def identify_deferrable_tasks(step_count: int) -> str:
        """Identify tasks that can wait."""
        if step_count > 2:
            return "Additional enhancements and optimizations"
        else:
            return "Future planning and long-term tasks"

    @staticmethod
    def estimate_task_time(step_count: int) -> int:
        """Estimate time for current task."""
        if step_count == 0:
            return 2  # Initial request
        elif step_count > 0:
            return 1  # Follow-up action
        else:
            return 3  # New task

    @staticmethod
    def estimate_total_time(step_count: int) -> int:
        """Estimate total remaining time."""
        base_time = PromptHelpers.estimate_task_time(step_count)
        if step_count > 3:
            return base_time
        else:
            return base_time + 2  # Add buffer for potential additional steps

    @staticmethod
    def present_clear_choices(step_count: int, note_topic: str) -> str:
        """Present clear choices for decision making."""
        if step_count == 0:
            return f"1. Use a tool to help with {note_topic}"
        elif step_count > 0:
            return f"1. Continue filling {note_topic}, 2. Give final answer if complete"
        else:
            return f"1. Continue with {note_topic}, 2. Ask for clarification"

    @staticmethod
    def recommend_next_action(step_count: int, last_tool_result: Any, note_topic: str) -> str:
        """Recommend the next action based on current state."""
        if step_count == 0:
            return f"Use the most appropriate tool for {note_topic}"
        elif last_tool_result:
            if "error" in str(last_tool_result).lower():
                return "Try a different approach or ask for clarification"
            else:
                return f"Check if {note_topic} is complete or use another tool"
        else:
            return f"Start working on {note_topic}"

    @staticmethod
    def predict_user_needs(user_input: str, step_count: int, note_topic: str) -> str:
        """Predict potential next user needs based on current state."""
        if "schedule" in user_input.lower():
            return "Set reminders, confirm details, or add to calendar"
        elif "email" in user_input.lower():
            return "Follow-up messages, attachments, or read receipts"
        elif step_count > 1:
            return f"Review {note_topic} results, make adjustments, or celebrate progress"
        else:
            return f"Clarify details for {note_topic} if needed, or move to next related task"

    @staticmethod
    def get_max_steps() -> int:
        """Get the maximum number of tool executions allowed in a single loop."""
        try:
            from ..config.settings import settings
            return settings.LOOP_LIMIT
        except ImportError:
            return 10  # Default fallback

    @staticmethod
    def format_memory_context(memory_context: List[dict]) -> str:
        """Format memory context with professional structure."""
        if not memory_context:
            return "💭 No additional memory context available."

        formatted = []
        context_count = 0
        max_context_items = 5

        for item in memory_context[:max_context_items]:
            source = item.get("source", "unknown")
            content = item.get("content", "")
            content_type = item.get("type", "general")

            # Truncate long content
            if len(content) > 200:
                content = content[:200] + "..."

            if source == "ltm":
                formatted.append(
                    f"💾 Long-term Memory ({content_type}): {content}")
            elif source == "rag":
                formatted.append(
                    f"📚 Knowledge Base ({content_type}): {content}")
            else:
                formatted.append(f"💭 Memory ({content_type}): {content}")

            context_count += 1
            if context_count >= max_context_items:
                break

        if len(memory_context) > max_context_items:
            remaining = len(memory_context) - max_context_items
            formatted.append(f"📋 ... and {remaining} more context items")

        return "\n".join(formatted)

    @staticmethod
    def format_conversation_history(history: list) -> str:
        """Format conversation history with professional structure."""
        if not history:
            return "📝 No previous conversation - starting fresh!"

        formatted = []
        # Show last 8 entries for better context
        for i, entry in enumerate(history[-8:], 1):
            if entry["role"] == "user":
                formatted.append(f"👤 User: {entry['content']}")
            elif entry["role"] == "assistant":
                formatted.append(f"🤖 Assistant: {entry['content']}")
            elif entry["role"] == "tool":
                tool_name = entry.get('name', 'Unknown Tool')
                formatted.append(f"🛠 {tool_name}: {entry['content']}")
            elif entry["role"] == "memory":
                # Handle memory role entries (tool execution results)
                source = entry.get("source", "unknown")
                content_type = entry.get("type", "general")
                content = entry.get("content", "")

                # Truncate long content for readability
                if len(content) > 150:
                    content = content[:150] + "..."

                if source == "ltm":
                    formatted.append(
                        f"💾 LTM Memory ({content_type}): {content}")
                elif source == "rag":
                    formatted.append(
                        f"📚 RAG Context ({content_type}): {content}")
                else:
                    formatted.append(f"💭 Memory ({content_type}): {content}")

        return "\n".join(formatted)

    @staticmethod
    def format_tools_professional(tool_registry) -> str:
        """Format available tools with professional descriptions."""
        tool_schema = tool_registry.get_schema()
        if not tool_schema:
            return "⚠️ No tools are currently available."

        # Group tools by category
        tools_by_category = {}
        for name, info in tool_schema.items():
            category = info.get('category', 'General')
            if category not in tools_by_category:
                tools_by_category[category] = []
            tools_by_category[category].append(
                (name, info.get('description', 'No description available')))

        formatted = []
        for category, tools in tools_by_category.items():
            formatted.append(f"📁 {category}:")
            for name, description in tools:
                # Truncate long descriptions
                if len(description) > 150:
                    description = description[:150] + "..."
                formatted.append(f"  • {name}: {description}")
            formatted.append("")  # Empty line between categories

        return "\n".join(formatted).strip()

    @staticmethod
    def classify_request_intent(user_input: str) -> str:
        """
        Classify the user's request intent to determine if tools are needed.

        Args:
            user_input: The user's input message

        Returns:
            str: Intent classification ('simple', 'information', 'action', 'complex')
        """
        input_lower = user_input.lower().strip()

        # Simple greetings and basic questions
        simple_patterns = [
            'hey', 'hi', 'hello', 'good morning', 'good afternoon',
            'good evening', 'how are you', 'what\'s up', 'sup',
            'thanks', 'thank you', 'bye', 'goodbye', 'see you'
        ]

        # Check for simple patterns, but exclude questions that start with "how"
        if any(pattern in input_lower for pattern in simple_patterns):
            # Special case: "how" questions are usually information requests
            if input_lower.startswith('how ') and not any(greeting in input_lower for greeting in ['how are you', 'how\'s it going']):
                return 'information'
            # Special case: "research" is usually an information request
            if 'research' in input_lower:
                return 'information'
            return 'simple'

        # Information requests (check these BEFORE simple patterns to avoid conflicts)
        info_patterns = [
            'what is', 'what\'s', 'how does', 'when is', 'where is',
            'who is', 'why does', 'tell me about', 'explain',
            'weather', 'news', 'search', 'find', 'research',
            'how does', 'research'
        ]

        if any(pattern in input_lower for pattern in info_patterns):
            return 'information'

        # Complex requests (planning, analysis, coordination) - check these FIRST
        complex_patterns = [
            'plan', 'organize', 'analyze', 'coordinate', 'manage',
            'strategy', 'workflow', 'process', 'system', 'project'
        ]

        if any(pattern in input_lower for pattern in complex_patterns):
            return 'complex'

        # Action requests
        action_patterns = [
            'send', 'create', 'schedule', 'book', 'reserve',
            'add', 'update', 'delete', 'remove', 'set',
            'email', 'meeting', 'reminder', 'note', 'task'
        ]

        if any(pattern in input_lower for pattern in action_patterns):
            return 'action'

        # Default to information if unclear
        return 'information'
