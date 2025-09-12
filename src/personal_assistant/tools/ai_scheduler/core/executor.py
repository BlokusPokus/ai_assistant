"""
Task Executor for AI tasks.

This module handles the execution of AI tasks using the AI assistant.
Enhanced with sophisticated prompt architecture and metadata integration.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from ....database.models.ai_tasks import AITask
# from ....prompts.prompt_helpers import PromptHelpers  # Not used in executor
from ....tools.metadata import AIEnhancementManager, ToolMetadataManager

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes AI tasks using the AI assistant with enhanced prompt architecture."""

    def __init__(self):
        self.logger = logger
        self.metadata_manager = ToolMetadataManager()
        self.enhancement_manager = AIEnhancementManager()
        
        # Initialize AI task metadata and enhancements
        self._initialize_metadata()

    def _initialize_metadata(self):
        """Initialize AI task metadata and enhancements."""
        try:
            from ....tools.metadata.ai_task_metadata import (
                create_ai_task_ai_enhancements,
                create_ai_task_metadata,
            )
            
            # Register AI task metadata
            ai_task_metadata = create_ai_task_metadata()
            self.metadata_manager.register_tool_metadata(ai_task_metadata)
            
            # Register AI task enhancements
            create_ai_task_ai_enhancements(self.enhancement_manager)
            
            self.logger.info("TaskExecutor initialized with AI task metadata and enhancements")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize AI task metadata: {e}")

    async def execute_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute an AI task.

        Args:
            task: The AI task to execute

        Returns:
            Dictionary with execution results
        """
        try:
            self.logger.info(f"🔍 BREAKPOINT 11: Executing task: {task.title} (ID: {task.id})")
            print(f"🔍 BREAKPOINT 11: Executing task: {task.title} (ID: {task.id})")

            # Import AgentCore here to avoid circular imports
            from ....core import AgentCore
            from ....tools import create_tool_registry

            # Create task context
            task_context = self._build_task_context(task)
            print(f"🔍 BREAKPOINT 12: Task context created: {task_context}")

            # Create AI prompt based on task type
            ai_prompt = self._create_ai_prompt(task, task_context)
            print(f"🔍 BREAKPOINT 13: AI prompt created: {ai_prompt[:200]}...")

            # Create tool registry with all available tools
            tool_registry = create_tool_registry()
            print(f"🔍 BREAKPOINT 13.5: Created tool registry with {len(tool_registry.tools)} tools: {list(tool_registry.tools.keys())}")

            # Execute with AI assistant using proper tool registry
            agent = AgentCore(tools=tool_registry)
            print("🔍 BREAKPOINT 14: About to call AgentCore.run() - LLM CALL")
            response = await agent.run(ai_prompt, int(task.user_id))
            print(f"🔍 BREAKPOINT 15: AgentCore.run() completed, response: {response[:200]}...")

            # Process the response
            result = self._process_ai_response(task, response)
            print(f"🔍 BREAKPOINT 16: Task execution result: {result}")

            self.logger.info(f"🔍 BREAKPOINT 17: Successfully executed task: {task.title}")
            print(f"🔍 BREAKPOINT 17: Successfully executed task: {task.title}")
            return result

        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute task: {e}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _build_task_context(self, task: AITask) -> Dict[str, Any]:
        """
        Build context for task execution.

        Args:
            task: The AI task

        Returns:
            Task context dictionary
        """
        context: dict[str, Any] = {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "schedule_type": task.schedule_type,
            "ai_context": task.ai_context,
            "notification_channels": task.notification_channels or [],
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "last_run_at": task.last_run_at.isoformat() if task.last_run_at else None,
            "current_time": datetime.utcnow().isoformat(),
        }

        return context

    def _create_ai_prompt(self, task: AITask, context: Dict[str, Any]) -> str:
        """
        Create enhanced AI prompt for task execution using sophisticated prompt architecture.

        Args:
            task: The AI task
            context: Task context

        Returns:
            Enhanced AI prompt string
        """
        # Get AI enhancements for this task type
        enhancements = self.enhancement_manager.get_tool_enhancements("ai_task_scheduler")
        
        # Build base prompt with professional structure
        base_prompt = self._build_base_prompt(task, context)
        
        # Add task-specific content
        task_content = self._build_task_specific_content(task, context)
        
        # Add AI guidance from enhancements
        ai_guidance = self._build_ai_guidance(enhancements, task, context)
        
        # Add professional guidelines
        guidelines = self._build_professional_guidelines()
        
        # Combine all components
        enhanced_prompt = f"""
{base_prompt}

{task_content}

{ai_guidance}

{guidelines}
"""
        return enhanced_prompt.strip()

    def _classify_task_intent(self, task: AITask) -> str:
        """Classify the task intent based on task type and content."""
        if task.task_type == "reminder":
            return "REMINDER_EXECUTION"
        elif task.task_type == "periodic_task":
            return "PERIODIC_EXECUTION"
        elif task.task_type == "automated_task":
            return "AUTOMATED_EXECUTION"
        else:
            return "GENERIC_EXECUTION"

    def _get_task_focus_areas(self, task: AITask) -> List[str]:
        """Get focus areas for the task based on content and type."""
        focus_areas = []
        
        if task.task_type:
            focus_areas.append(task.task_type)
        
        if task.title:
            title_lower = task.title.lower()
            if any(word in title_lower for word in ["email", "message", "send"]):
                focus_areas.append("email")
            if any(word in title_lower for word in ["meeting", "schedule", "calendar"]):
                focus_areas.append("calendar")
            if any(word in title_lower for word in ["research", "search", "find"]):
                focus_areas.append("research")
            if any(word in title_lower for word in ["note", "document", "write"]):
                focus_areas.append("note")
        
        return list(set(focus_areas)) if focus_areas else ["general"]

    def _build_base_prompt(self, task: AITask, context: Dict[str, Any]) -> str:
        """Build the base prompt structure with professional formatting."""
        current_time = datetime.now()
        
        return f"""
🎯 AI TASK EXECUTOR

📅 Current time: {current_time.strftime('%Y-%m-%d %H:%M')}

🎯 TASK EXECUTION REQUEST: {task.title or 'Execute scheduled AI task'}

🔍 REQUEST INTENT: {self._classify_task_intent(task).upper()}

📊 TASK CONTEXT:
• Task ID: {task.id}
• Task Type: {task.task_type.upper()}
• Schedule Type: {task.schedule_type or 'One-time'}
• Created: {context['created_at'] or 'Unknown'}
• Last Run: {context['last_run_at'] or 'Never'}
• User ID: {task.user_id}
• Focus areas: {', '.join(self._get_task_focus_areas(task)) if self._get_task_focus_areas(task) else 'General'}

🚨 **CRITICAL: ACTION CONFIRMATION RULES (MUST FOLLOW FIRST)** 🚨
• For reminders: Execute directly using default notification channel (SMS) - no confirmation needed
• For periodic tasks: Execute based on schedule and context - provide detailed summary
• For automated tasks: Execute thoroughly and provide comprehensive analysis
• This rule takes priority over ALL other rules
"""

    def _build_task_specific_content(self, task: AITask, context: Dict[str, Any]) -> str:
        """Build task-specific content based on task type."""
        if task.task_type == "reminder":
            return self._build_reminder_content(task, context)
        elif task.task_type == "periodic_task":
            return self._build_periodic_task_content(task, context)
        elif task.task_type == "automated_task":
            return self._build_automated_task_content(task, context)
        else:
            return self._build_generic_task_content(task, context)

    def _build_reminder_content(self, task: AITask, context: Dict[str, Any]) -> str:
        """Build content for reminder tasks."""
        return f"""
<<REMINDER TASK EXECUTION>>

📋 REMINDER TASK DETAILS:
• Title: {task.title}
• Description: {task.description or 'No description provided'}
• Notification Channels: {', '.join(context.get('notification_channels', [])) or 'Default (SMS)'}
• AI Context: {task.ai_context or 'No additional context provided'}

🎯 REMINDER EXECUTION TASK:
You have a reminder task to execute. This is a scheduled reminder that has become due.

🚨 **CRITICAL: REMINDER EXECUTION RULES**
• Execute directly using default notification channel (SMS) - no confirmation needed
• Acknowledge the reminder and its importance
• Provide relevant information or context about the reminder
• Suggest any immediate actions that might be needed
• Give a brief, helpful summary of what this reminder is about
• Provide encouragement or motivation if appropriate

💡 **EXECUTION APPROACH**:
• Be helpful, actionable, and supportive in your response
• Focus on the user's needs and the reminder's purpose
• Use clear, structured formatting
• End with clear next steps or conclusions
"""

    def _build_periodic_task_content(self, task: AITask, context: Dict[str, Any]) -> str:
        """Build content for periodic tasks."""
        return f"""
<<PERIODIC TASK EXECUTION>>

📋 PERIODIC TASK DETAILS:
• Title: {task.title}
• Description: {task.description or 'No description provided'}
• Schedule Type: {task.schedule_type}
• Schedule Config: {task.schedule_config or 'Default'}
• Last Run: {context['last_run_at'] or 'Never'}
• AI Context: {task.ai_context or 'No additional context provided'}

🎯 PERIODIC TASK EXECUTION:
You have a periodic task to execute. This task runs on a recurring schedule.

🚨 **CRITICAL: PERIODIC TASK EXECUTION RULES**
• Execute based on schedule and context - provide detailed summary
• Execute the periodic task based on the context and schedule
• Provide a detailed summary of what was accomplished
• Note any important findings, updates, or changes
• Suggest any follow-up actions or adjustments needed
• Consider the recurring nature and provide relevant insights

💡 **EXECUTION APPROACH**:
• Focus on thorough execution and providing value for this recurring task
• Use tools when needed to gather information or perform actions
• Maintain consistency with previous executions
• Provide comprehensive analysis and actionable insights
"""

    def _build_automated_task_content(self, task: AITask, context: Dict[str, Any]) -> str:
        """Build content for automated tasks."""
        return f"""
<<AUTOMATED TASK EXECUTION>>

📋 AUTOMATED TASK DETAILS:
• Title: {task.title}
• Description: {task.description or 'No description provided'}
• AI Context: {task.ai_context or 'No additional context provided'}

🎯 AUTOMATED TASK EXECUTION:
You have an automated task to execute. This is a system-generated task that requires AI processing.

🚨 **CRITICAL: AUTOMATED TASK EXECUTION RULES**
• Execute thoroughly and provide comprehensive analysis
• Execute the automated task thoroughly
• LEAD WITH RESULTS: Start with the key findings/answers
• Keep the main response concise and actionable
• Note any important findings, issues, or opportunities
• Suggest any follow-up actions or improvements
• Consider the automated nature and provide insights

💡 **EXECUTION APPROACH**:
• Focus on thorough analysis and providing actionable results
• Use tools when needed to gather information or perform actions
• Lead with the essential results, then add context if needed
• Keep responses concise but complete
• Maintain high quality standards for automated processing
"""

    def _build_generic_task_content(self, task: AITask, context: Dict[str, Any]) -> str:
        """Build content for generic tasks."""
        return f"""
<<GENERIC TASK EXECUTION>>

📋 TASK DETAILS:
• Title: {task.title}
• Description: {task.description or 'No description provided'}
• Task Type: {task.task_type}
• AI Context: {task.ai_context or 'No additional context provided'}

🎯 TASK EXECUTION:
You have a task to execute. This is a scheduled task that requires AI processing.

🚨 **CRITICAL: GENERIC TASK EXECUTION RULES**
• Execute the task based on the provided context
• Provide a clear summary of what was accomplished
• Note any important findings or actions taken
• Suggest any follow-up actions if needed
• Be helpful and thorough in your response

💡 **EXECUTION APPROACH**:
• Focus on understanding the task requirements and providing valuable execution
• Use tools when needed to gather information or perform actions
• Provide clear, structured responses
• Maintain professional quality standards
• End with actionable insights or next steps
"""

    def _build_ai_guidance(self, enhancements: List[Any], task: AITask, context: Dict[str, Any]) -> str:
        """Build AI guidance from enhancements."""
        if not enhancements:
            return "💡 Basic AI guidance available - execute the task as specified."
        
        guidance_sections = []
        
        for enhancement in enhancements:
            if hasattr(enhancement, 'ai_instructions') and enhancement.ai_instructions:
                guidance_sections.append(f"""
🚨 **{enhancement.title.upper()}**:
{enhancement.ai_instructions}
""")
        
        if guidance_sections:
            return f"""
🎯 **CRITICAL: ENHANCED TOOL GUIDANCE (MUST FOLLOW)** 🎯

{''.join(guidance_sections)}
"""
        else:
            return "💡 Basic AI guidance available - execute the task as specified."

    def _build_professional_guidelines(self) -> str:
        """Build professional guidelines for task execution."""
        return """
<<CORE AGENT GUIDELINES>>

🎯 PRIMARY OBJECTIVES:
• Complete the user's task fully before ending your response
• Use tools ONLY when they add value to the task execution
• Provide clear, actionable responses
• Maintain focus on the current task

🚨 **CRITICAL: COMMUNICATION STYLE**
• DURING PROCESS: Think out loud naturally, like you're working alongside them
• FINAL ANSWER: Be conversational and warm, like talking to a good friend
• BE CONCISE: Give the essential info first, details only if needed
• KEEP IT UPBEAT: Stay friendly and encouraging in tone
• NEVER say "Based on the search results..." in final answers
• NEVER say "I will provide a summary..." in final answers
• ALWAYS end with genuine, helpful answers that feel personal and caring
• Use natural language, occasional humor, and show empathy when appropriate

🚨 **CRITICAL: EXECUTION OVER PLANNING**
• When you need information from the user, ASK IMMEDIATELY
• Don't say "I will ask..." - just ASK the question
• Don't get stuck in planning loops - execute your plans
• Use default values when available (e.g., default notification channels for reminders)
• Only ask for information when no reasonable defaults exist

💡 **PROCESS MANAGEMENT (Encouraged)**
• CAN say "Let me break this down into steps:" for complex tasks
• CAN say "I'll need to gather some information first" when explaining delays
• CAN say "This requires multiple steps to complete" for complex requests
• CAN outline the process when the user asks "How will you do this?"
• CAN think out loud during task execution and analysis

🎭 **HUMAN-LIKE RESPONSE STYLE**
• Be genuinely friendly and approachable - like a knowledgeable friend who cares
• Use natural, conversational language instead of robotic responses
• Show empathy and understanding when users are frustrated or overwhelmed
• Add personality with occasional humor, encouragement, or relatable comments
• Use contractions and informal language when appropriate ("I'll", "you're", "it's")
• Acknowledge their feelings and validate their concerns
• End responses with warmth and encouragement when appropriate

🚫 CRITICAL RULES:
• NEVER refer to tool names when speaking to the user
• NEVER ask the user for information you can get via tools
• NEVER stop mid-task unless you need clarification on options
• NEVER make assumptions about code or system behavior
• NEVER use tools for simple greetings or basic questions that don't require information

💡 TASK EXECUTION PRINCIPLES:
• SIMPLE TASKS (reminders, basic notifications): Execute directly without tools
• COMPLEX TASKS (analysis, research, planning): Use tools to gather information
• AUTOMATED TASKS (system processing): Use tools to perform actions
• PERIODIC TASKS (recurring work): Use tools with patterns for consistency

<<TASK COMPLETION GUIDELINES>>

🔄 **TASK COMPLETION**:
• Acknowledge the task completion
• Summarize what was accomplished
• Note any important findings or recommendations
• Suggest follow-up actions if appropriate
• Provide encouragement or motivation when relevant

💡 **RESPONSE QUALITY**:
• Use clear, structured formatting
• Lead with the key results/answers
• Keep explanations brief and to the point
• Stay positive and encouraging
• End with clear next steps or conclusions
"""

    def _process_ai_response(self, task: AITask, ai_response: str) -> Dict[str, Any]:
        """
        Process the AI response and create enhanced execution result.

        Args:
            task: The executed task
            ai_response: Response from AI assistant

        Returns:
            Enhanced execution result dictionary
        """
        # Enhanced response processing with quality validation
        response_quality = self._assess_response_quality(ai_response)
        
        # Extract key information from response
        extracted_info = self._extract_response_information(ai_response)
        
        # Create enhanced result
        result = {
            "success": True,
            "message": ai_response,
            "task_id": task.id,
            "task_title": task.title,
            "task_type": task.task_type,
            "execution_time": datetime.utcnow().isoformat(),
            "ai_response": ai_response,
            "response_quality": response_quality,
            "extracted_info": extracted_info,
            "execution_status": "completed",
        }
        
        # Add quality indicators
        if response_quality["is_high_quality"]:
            result["quality_indicators"] = response_quality["indicators"]
        
        return result

    def _assess_response_quality(self, ai_response: str) -> Dict[str, Any]:
        """Assess the quality of the AI response."""
        quality_indicators = []
        
        # Check for key quality indicators
        if len(ai_response.strip()) > 50:
            quality_indicators.append("substantial_response")
        
        if any(word in ai_response.lower() for word in ["acknowledge", "understand", "completed", "accomplished"]):
            quality_indicators.append("acknowledgment")
        
        if any(word in ai_response.lower() for word in ["suggest", "recommend", "action", "next step"]):
            quality_indicators.append("actionable_advice")
        
        if any(word in ai_response.lower() for word in ["helpful", "support", "encourage", "motivate"]):
            quality_indicators.append("supportive_tone")
        
        if "1." in ai_response or "2." in ai_response or "•" in ai_response:
            quality_indicators.append("structured_format")
        
        is_high_quality = len(quality_indicators) >= 3
        
        return {
            "is_high_quality": is_high_quality,
            "indicators": quality_indicators,
            "score": len(quality_indicators) / 5.0,  # Normalize to 0-1
        }

    def _extract_response_information(self, ai_response: str) -> Dict[str, Any]:
        """Extract key information from the AI response."""
        extracted = {
            "has_acknowledgment": any(word in ai_response.lower() for word in ["acknowledge", "understand", "received"]),
            "has_actions": any(word in ai_response.lower() for word in ["suggest", "recommend", "action", "step"]),
            "has_summary": any(word in ai_response.lower() for word in ["summary", "accomplished", "completed"]),
            "has_encouragement": any(word in ai_response.lower() for word in ["encourage", "motivate", "support", "helpful"]),
            "response_length": len(ai_response),
            "is_structured": "1." in ai_response or "2." in ai_response or "•" in ai_response,
        }
        
        return extracted

    async def execute_reminder_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute a reminder task specifically.

        Args:
            task: The reminder task

        Returns:
            Execution result
        """
        return await self.execute_task(task)

    async def execute_periodic_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute a periodic task specifically.

        Args:
            task: The periodic task

        Returns:
            Execution result
        """
        return await self.execute_task(task)

    async def execute_automated_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute an automated task specifically.

        Args:
            task: The automated task

        Returns:
            Execution result
        """
        return await self.execute_task(task)
