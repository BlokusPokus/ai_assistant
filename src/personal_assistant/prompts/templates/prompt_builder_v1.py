"""
Prompt construction utilities.

📁 llm/prompt_builder.py
Builds agent prompts from memory, recent actions, tools, and user input. 
Injects into Gemini calls.
"""

import re
from datetime import datetime
from typing import Dict, List

from ...config.logging_config import get_logger
from ...tools.base import ToolRegistry
from ...types.state import AgentState

logger = get_logger("llm")


class PromptBuilder:
    def __init__(self, tool_registry: "ToolRegistry"):
        """
        Initialize the prompt builder with a tool registry.

        Input:
            tool_registry: Registry containing all available tools and their metadata

        Output:
            None

        Description:
            Sets up the prompt builder with access to the tool registry for later use
            in constructing prompts that include tool descriptions and capabilities.
        """
        self.tool_registry = tool_registry

    def build(self, state: AgentState) -> str:
        """Build ADHD-optimized prompt from current state with enhanced AI reasoning."""
        current_time = datetime.now()

        # Build ADHD-optimized prompt structure with internal AI thinking guidelines
        base_prompt = f"""
🎯 ADHD-OPTIMIZED PERSONAL ASSISTANT

📅 Current time: {current_time.strftime('%Y-%m-%d %H:%M')}

🎯 YOUR REQUEST: {state.user_input}

📋 PROGRESS TRACKING:
• Steps completed: {state.step_count}
• Last action: {state.last_tool_result if state.last_tool_result else 'Starting fresh'}

{self._build_ai_reasoning_guidelines()}

{self._build_adhd_instructions(state)}

{self._format_attention_prompts(state)}

{self._add_executive_function_support(state)}

{self._build_personality_guidelines()}

💾 LONG-TERM MEMORY & KNOWLEDGE:
{self._format_memory_context(state.memory_context)}

📚 CONVERSATION HISTORY:
{self._format_history_adhd(state.conversation_history)}

🛠 AVAILABLE TOOLS:
{self._format_tools_adhd()}

🎯 NEXT ACTION:
{self._build_action_guidance(state)}
"""
        return base_prompt

    def _build_ai_reasoning_guidelines(self) -> str:
        """Build guidelines for extensive AI internal reasoning process."""
        return """
<<INTERNAL: AI Reasoning Guidelines>>
🧠 AI INTERNAL REASONING GUIDELINES (DO NOT OUTPUT THIS TO USER):

• THINK EXTENSIVELY: Before any action or response, conduct a thorough step-by-step analysis. Review the full state, conversation history, and tools. Identify key elements, potential ambiguities, and unspoken user needs.
• PRIORITIZE USER REQUEST: Always anchor your response to the user's explicit request and conversation history. The ADHD context in this prompt is for response style (simplified, motivational) and not the content unless the user explicitly mentions ADHD-related topics.
• VALIDATE CONTEXT: For note-filling or updating tasks, check the conversation history and state for the correct note ID and topic. Use the _validate_note_context helper to ensure content aligns with the user's intent (e.g., 'Master the Interview' vs. unrelated topics).
• PREDICT NEXT STEPS: Anticipate 2-3 possible future user actions or questions based on the user's request and patterns (e.g., forgetfulness, need for reminders). Plan contingencies for each.
• ANALYZE COMPREHENSIVELY: Evaluate the request in context—consider urgency, dependencies, risks, and alternatives. If tools are needed, simulate outcomes mentally. If state has relevant info, use it first to avoid unnecessary tool calls.
• STRUCTURE THINKING: Use chain-of-thought: 1. Summarize current situation. 2. Break down request into sub-tasks. 3. Evaluate options with pros/cons. 4. Select best path. 5. Predict outcomes and adjustments.
• BE PROACTIVE BUT RELEVANT: Take initiative by suggesting reasonable defaults (e.g., note titles, tags) or expanding content when asked to 'fill' or 'expand'. Generate comprehensive, relevant content using general knowledge or tools like web_search, but stay strictly aligned with the user's topic. Avoid introducing unrelated topics (e.g., ADHD) unless explicitly requested.
• TOOL USAGE: Use tools like get_relevant_ltm_memories or search_ltm_memories only when directly relevant to the user's request. If no relevant memories are found, proceed with general knowledge or other tools to fulfill the request.
• MAINTAIN FOCUS ON ADHD NEEDS: Ensure internal planning supports user-friendly outputs—simple, motivational, structured—but keep reasoning deep and proactive.
• DO NOT REVEAL THINKING: Keep all this internal; output only ADHD-optimized responses. If clarification is needed, ask in a gentle, focused way, but prefer proactive suggestions and actions.
• **NEVER refer to tool names when speaking to the USER.** Instead, just say what the tool is doing in natural language.
• If you need additional information that you can get via tool calls, prefer that over asking the user.
• If you make a plan, immediately follow it, do not wait for the user to confirm or tell you to go ahead. The only time you should stop is if you need more information from the user that you can't find any other way, or have different options that you would like the user to weigh in on.
<</INTERNAL>>

"""

    def _build_adhd_instructions(self, state: AgentState) -> str:
        """Build ADHD-specific instruction set with visual organization and structure."""
        return """
🧠 ADHD-FOCUSED GUIDELINES:

📋 TASK BREAKDOWN:
• Break complex requests into 2-3 simple steps
• Focus on ONE task at a time
• Show clear progress indicators

⏰ TIME MANAGEMENT:
• Give time estimates for each step
• Use "time boxing" for focus periods
• Include natural break reminders

🧠 EXECUTIVE FUNCTION SUPPORT:
• Prioritize tasks by importance and urgency
• Provide decision-making frameworks
• Offer memory aids and repetition

💪 MOTIVATION STRATEGIES:
• Acknowledge progress and effort
• Connect tasks to user interests
• Celebrate small wins and completions

- If not sure about the context, first look in the state and conversation history
- Use tools only when necessary to complete the user's request
- Be joyful and upbeat
"""

    def _format_attention_prompts(self, state: AgentState) -> str:
        """Add attention management to prompts."""
        main_task = self._extract_main_task(state.user_input)
        return f"""
🎯 ATTENTION FOCUS:
Current task: {main_task}
Progress: {state.step_count} steps completed

📍 FOCUS REMINDER:
• Stay on the current task
• Ignore distractions
• Take one step at a time
• Use tools to help complete tasks
"""

    def _add_executive_function_support(self, state: AgentState) -> str:
        """Add executive function support features with enhanced prediction."""
        priority_tasks = self._identify_priority_tasks(state)
        urgent_tasks = self._identify_urgent_tasks(state)
        deferrable_tasks = self._identify_deferrable_tasks(state)
        predicted_needs = self._predict_user_needs(state)

        return f"""
🧠 EXECUTIVE FUNCTION SUPPORT:

📋 PRIORITY FRAMEWORK:
• Most Important: {priority_tasks}
• Time-sensitive: {urgent_tasks}
• Can wait: {deferrable_tasks}

🔮 ANTICIPATED NEEDS:
• Possible next steps: {predicted_needs}

⏰ TIME ESTIMATES:
• Current task: ~{self._estimate_task_time(state)} minutes
• Total remaining: ~{self._estimate_total_time(state)} minutes

💡 DECISION SUPPORT:
• Clear options: {self._present_clear_choices(state)}
• Recommended action: {self._recommend_next_action(state)}
"""

    def _build_personality_guidelines(self) -> str:
        """Build guidelines for AI personality to ensure consistent, joyful, and upbeat interactions."""
        return """
😊 AI PERSONALITY GUIDELINES:

• BE JOYFUL AND UPBEAT: Infuse all responses with positive energy, enthusiasm, and encouragement. Use emojis sparingly to add fun, like 🎉 for celebrations or 👍 for affirmations.
• EMPATHETIC AND SUPPORTIVE: Acknowledge ADHD challenges gently, offer reassurance, and frame suggestions as empowering choices.
• CONVERSATIONAL TONE: Speak like a friendly coach—warm, approachable, and motivating. Avoid formal language; use contractions and simple words.
• CONSISTENT VOICE: Maintain this personality across all outputs, adapting to state but always prioritizing positivity and focus support.
• PROACTIVE INITIATIVE: Be helpful by suggesting and implementing expansions, titles, or additions proactively when it makes sense, while staying strictly aligned with the user's request. For content generation tasks, dive in and create full, detailed outputs autonomously, ensuring relevance to the topic.
"""

    def _format_history_adhd(self, history: list) -> str:
        """Format conversation history with ADHD-friendly structure."""
        if not history:
            return "📝 No previous actions - starting fresh!"

        formatted = []
        # Show last 10 entries max
        for i, entry in enumerate(history[-10:], 1):
            if entry["role"] == "user":
                formatted.append(f"👤 You: {entry['content']}")
            elif entry["role"] == "assistant":
                formatted.append(f"🤖 Assistant: {entry['content']}")
            elif entry["role"] == "tool":
                formatted.append(f"🛠 Tool ({entry['name']}): {entry['content']}")

        return "\n".join(formatted)

    def _format_tools_adhd(self) -> str:
        """Format available tools with ADHD-friendly descriptions."""
        tool_schema = self.tool_registry.get_schema()
        if not tool_schema:
            return "⚠️ No tools are currently available."
        else:
            tool_descriptions = []
            for name, info in tool_schema.items():
                description = info.get("description", "No description available")
                # Use original description instead of simplified
                tool_descriptions.append(f"• {name}: {description}")
            return "\n".join(tool_descriptions)

    def _build_action_guidance(self, state: AgentState) -> str:
        """Build clear action guidance for ADHD users with predictive elements."""
        return """
🎯 WHAT TO DO NEXT:

1️⃣ USE A TOOL if more actions are needed (check state first)
2️⃣ GIVE FINAL ANSWER if request is complete
3️⃣ ASK FOR CLARIFICATION if confused

💡 REMEMBER:
• Stay focused on the current task
• Take one step at a time
• Use tools to help complete your request
• Predict and prepare for what might come next (e.g., follow-ups, reminders)
• Be proactive: Suggest titles, expansions, or additions when appropriate, and implement them if it aligns with the request. For filling or expanding notes, generate and add detailed content directly using tools, ensuring it matches the user's topic (e.g., 'Master the Interview').
• **IMPORTANT**: When giving final answers:
  - Be concise and direct
  - Don't repeat what you just did
  - Focus on the result or next steps
  - If the task is complete, confirm completion and suggest related wins
• **COMPLETE THE FULL REQUEST**: Don't stop until you've done everything the user asked for, and anticipate if they might need more based on context
"""

    # Helper methods for ADHD optimizations

    def _extract_main_task(self, user_input: str) -> str:
        """Extract the main task from user input."""
        # Simple task extraction - can be enhanced with NLP
        if len(user_input) > 300:
            return user_input[:300] + "..."
        return user_input

    def _validate_note_context(self, state: AgentState) -> Dict[str, str]:
        """Validate and extract the note context from conversation history."""
        note_id = None
        note_topic = "Unknown"
        for entry in state.conversation_history[-5:]:  # Check recent history
            if entry["role"] == "user" and "note" in entry["content"].lower():
                if "interview" in entry["content"].lower():
                    note_topic = "Master the Interview"
                # Extract note ID from tool results or assistant responses
                match = re.search(
                    r"note with ID: ([a-f0-9\-]+)", str(state.last_tool_result)
                )
                if match:
                    note_id = match.group(1)
                elif "note_id" in str(entry["content"]):
                    match = re.search(
                        r"note with ID \'([a-f0-9\-]+)\'", entry["content"]
                    )
                    if match:
                        note_id = match.group(1)
        return {"note_id": note_id or "", "note_topic": note_topic or ""}

    def _identify_priority_tasks(self, state: AgentState) -> str:
        """Identify priority tasks based on current state."""
        note_context = self._validate_note_context(state)
        if state.step_count == 0:
            return f"Complete the current request: {note_context['note_topic']}"
        elif state.last_tool_result:
            return f"Continue working on {note_context['note_topic']}"
        else:
            return f"Address the user's request: {note_context['note_topic']}"

    def _identify_urgent_tasks(self, state: AgentState) -> str:
        """Identify urgent tasks."""
        note_context = self._validate_note_context(state)
        if (
            "schedule" in state.user_input.lower()
            or "meeting" in state.user_input.lower()
        ):
            return "Scheduling and time-sensitive tasks"
        elif (
            "email" in state.user_input.lower() or "message" in state.user_input.lower()
        ):
            return "Communication tasks"
        else:
            return f"Current user request: {note_context['note_topic']}"

    def _identify_deferrable_tasks(self, state: AgentState) -> str:
        """Identify tasks that can wait."""
        if state.step_count > 2:
            return "Additional enhancements and optimizations"
        else:
            return "Future planning and long-term tasks"

    def _estimate_task_time(self, state: AgentState) -> int:
        """Estimate time for current task."""
        if state.step_count == 0:
            return 2  # Initial request
        elif state.last_tool_result:
            return 1  # Follow-up action
        else:
            return 3  # New task

    def _estimate_total_time(self, state: AgentState) -> int:
        """Estimate total remaining time."""
        base_time = self._estimate_task_time(state)
        if state.step_count > 3:
            return base_time
        else:
            return base_time + 2  # Add buffer for potential additional steps

    def _present_clear_choices(self, state: AgentState) -> str:
        """Present clear choices for decision making."""
        note_context = self._validate_note_context(state)
        if state.step_count == 0:
            return f"1. Use a tool to help with {note_context['note_topic']}"
        elif state.last_tool_result:
            return f"1. Continue filling {note_context['note_topic']}, 2. Give final answer if complete"
        else:
            return f"1. Continue with {note_context['note_topic']}, 2. Ask for clarification"

    def _recommend_next_action(self, state: AgentState) -> str:
        """Recommend the next action based on current state."""
        note_context = self._validate_note_context(state)
        if state.step_count == 0:
            return f"Use the most appropriate tool for {note_context['note_topic']}"
        elif state.last_tool_result:
            if "error" in str(state.last_tool_result).lower():
                return "Try a different approach or ask for clarification"
            else:
                return f"Check if {note_context['note_topic']} is complete or use another tool"
        else:
            return f"Start working on {note_context['note_topic']}"

    def _predict_user_needs(self, state: AgentState) -> str:
        """Predict potential next user needs based on current state."""
        note_context = self._validate_note_context(state)
        if "schedule" in state.user_input.lower():
            return "Set reminders, confirm details, or add to calendar"
        elif "email" in state.user_input.lower():
            return "Follow-up messages, attachments, or read receipts"
        elif state.step_count > 1:
            return f"Review {note_context['note_topic']} results, make adjustments, or celebrate progress"
        else:
            return f"Clarify details for {note_context['note_topic']} if needed, or move to next related task"

    def _format_memory_context(self, memory_context: List[dict]) -> str:
        """Format memory context (LTM + RAG) for the prompt."""
        if not memory_context:
            return "💭 No additional memory context available."

        formatted = []
        context_count = 0
        max_context_items = 5  # Limit context injection

        for item in memory_context[:max_context_items]:  # Limit items
            source = item.get("source", "unknown")
            content = item.get("content", "")

            # Truncate long content to prevent context overflow
            if len(content) > 200:
                content = content[:200] + "..."

            if source == "ltm":
                formatted.append(f"💾 LTM Memory: {content}")
            elif source == "rag":
                formatted.append(f"📚 Knowledge Base: {content}")
            else:
                formatted.append(f"💭 Memory: {content}")

            context_count += 1
            if context_count >= max_context_items:
                break

        # Add context summary if we have more items
        if len(memory_context) > max_context_items:
            remaining = len(memory_context) - max_context_items
            formatted.append(f"📋 ... and {remaining} more context items (summarized)")

        return "\n".join(formatted)
