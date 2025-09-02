"""
AI Enhancements for Tool Metadata

This module provides AI-specific enhancements and guidance to improve
AI understanding and tool selection capabilities.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

from ...config.logging_config import get_logger

logger = get_logger("tools.ai_enhancements")


class EnhancementType(Enum):
    """Types of AI enhancements available."""
    PARAMETER_SUGGESTION = "parameter_suggestion"
    INTENT_RECOGNITION = "intent_recognition"
    TOOL_SELECTION = "tool_selection"
    WORKFLOW_SUGGESTION = "workflow_suggestion"
    ERROR_PREVENTION = "error_prevention"
    ERROR_LEARNING = "error_learning"
    VALIDATION = "validation"
    CONVERSATIONAL_GUIDANCE = "conversational_guidance"


class EnhancementPriority(Enum):
    """Priority levels for AI enhancements."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AIEnhancement:
    """Represents an AI enhancement for a tool."""

    enhancement_id: str
    tool_name: str
    enhancement_type: EnhancementType
    priority: EnhancementPriority = EnhancementPriority.MEDIUM

    # Enhancement content
    title: str = ""
    description: str = ""
    ai_instructions: str = ""
    examples: List[Dict[str, Any]] = field(default_factory=list)

    # Enhancement logic
    trigger_conditions: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    failure_handling: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert enhancement to dictionary for serialization."""
        return {
            "enhancement_id": self.enhancement_id,
            "tool_name": self.tool_name,
            "enhancement_type": self.enhancement_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "ai_instructions": self.ai_instructions,
            "examples": self.examples,
            "trigger_conditions": self.trigger_conditions,
            "success_criteria": self.success_criteria,
            "failure_handling": self.failure_handling,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "is_active": self.is_active
        }

    def to_json(self) -> str:
        """Convert enhancement to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def get_ai_guidance(self) -> Dict[str, Any]:
        """Get AI guidance for this enhancement."""
        return {
            "enhancement_id": self.enhancement_id,
            "tool_name": self.tool_name,
            "type": self.enhancement_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "ai_instructions": self.ai_instructions,
            "examples": self.examples,
            "trigger_conditions": self.trigger_conditions,
            "success_criteria": self.success_criteria
        }


class AIEnhancementManager:
    """Manages AI enhancements across all tools."""

    def __init__(self):
        self.enhancements: Dict[str, AIEnhancement] = {}
        self.tool_enhancements: Dict[str, List[str]] = {}
        self.type_enhancements: Dict[EnhancementType, List[str]] = {}
        self.logger = get_logger("tools.ai_enhancements.manager")

    def register_enhancement(self, enhancement: AIEnhancement):
        """Register an AI enhancement."""
        self.enhancements[enhancement.enhancement_id] = enhancement

        # Update tool index
        if enhancement.tool_name not in self.tool_enhancements:
            self.tool_enhancements[enhancement.tool_name] = []
        self.tool_enhancements[enhancement.tool_name].append(
            enhancement.enhancement_id)

        # Update type index
        if enhancement.enhancement_type not in self.type_enhancements:
            self.type_enhancements[enhancement.enhancement_type] = []
        self.type_enhancements[enhancement.enhancement_type].append(
            enhancement.enhancement_id)

        self.logger.info(
            f"Registered enhancement {enhancement.enhancement_id} for tool: {enhancement.tool_name}")

    def get_tool_enhancements(self, tool_name: str) -> List[AIEnhancement]:
        """Get all enhancements for a specific tool."""
        enhancement_ids = self.tool_enhancements.get(tool_name, [])
        return [
            self.enhancements[enh_id] for enh_id in enhancement_ids
            if enh_id in self.enhancements and self.enhancements[enh_id].is_active
        ]

    def get_enhancements_by_type(self, enhancement_type: EnhancementType) -> List[AIEnhancement]:
        """Get all enhancements of a specific type."""
        enhancement_ids = self.type_enhancements.get(enhancement_type, [])
        return [
            self.enhancements[enh_id] for enh_id in enhancement_ids
            if enh_id in self.enhancements and self.enhancements[enh_id].is_active
        ]

    def get_enhancements_by_priority(self, priority: EnhancementPriority) -> List[AIEnhancement]:
        """Get all enhancements with a specific priority level."""
        return [
            enhancement for enhancement in self.enhancements.values()
            if enhancement.priority == priority and enhancement.is_active
        ]

    def search_enhancements(self, query: str) -> List[AIEnhancement]:
        """Search enhancements by query in title, description, or instructions."""
        query_lower = query.lower()
        results = []

        for enhancement in self.enhancements.values():
            if not enhancement.is_active:
                continue

            # Search in title
            if query_lower in enhancement.title.lower():
                results.append(enhancement)
                continue

            # Search in description
            if query_lower in enhancement.description.lower():
                results.append(enhancement)
                continue

            # Search in AI instructions
            if query_lower in enhancement.ai_instructions.lower():
                results.append(enhancement)
                continue

        return results

    def get_ai_guidance_for_tool(self, tool_name: str) -> Dict[str, Any]:
        """Get comprehensive AI guidance for a specific tool."""
        enhancements = self.get_tool_enhancements(tool_name)

        guidance = {
            "tool_name": tool_name,
            "enhancements": {},
            "enhancement_summary": {
                "total_enhancements": len(enhancements),
                "by_type": {},
                "by_priority": {}
            }
        }

        # Group enhancements by type and priority
        for enhancement in enhancements:
            enh_type = enhancement.enhancement_type.value
            enh_priority = enhancement.priority.value

            if enh_type not in guidance["enhancements"]:
                guidance["enhancements"][enh_type] = []

            guidance["enhancements"][enh_type].append(
                enhancement.get_ai_guidance())

            # Update summary
            if enh_type not in guidance["enhancement_summary"]["by_type"]:
                guidance["enhancement_summary"]["by_type"][enh_type] = 0
            guidance["enhancement_summary"]["by_type"][enh_type] += 1

            if enh_priority not in guidance["enhancement_summary"]["by_priority"]:
                guidance["enhancement_summary"]["by_priority"][enh_priority] = 0
            guidance["enhancement_summary"]["by_priority"][enh_priority] += 1

        return guidance

    def get_ai_guidance_for_tools(self, tool_names: List[str]) -> Dict[str, Any]:
        """Get AI guidance for multiple tools."""
        guidance = {}
        for tool_name in tool_names:
            guidance[tool_name] = self.get_ai_guidance_for_tool(tool_name)

        return guidance

    def create_parameter_suggestion_enhancement(
        self,
        tool_name: str,
        parameter_name: str,
        suggestion_logic: str,
        examples: List[Dict[str, Any]],
        priority: EnhancementPriority = EnhancementPriority.MEDIUM
    ) -> AIEnhancement:
        """Create a parameter suggestion enhancement for a tool."""
        enhancement_id = f"{tool_name}_{parameter_name}_param_suggestion"

        enhancement = AIEnhancement(
            enhancement_id=enhancement_id,
            tool_name=tool_name,
            enhancement_type=EnhancementType.PARAMETER_SUGGESTION,
            priority=priority,
            title=f"Smart {parameter_name} suggestions for {tool_name}",
            description=f"Provides intelligent suggestions for the {parameter_name} parameter in {tool_name}",
            ai_instructions=f"When using {tool_name}, analyze the user's request and suggest optimal values for {parameter_name}. Use the provided examples and logic to make intelligent suggestions.",
            examples=examples,
            trigger_conditions=[
                f"User requests to use {tool_name}", f"Parameter {parameter_name} needs to be specified"],
            success_criteria=[
                f"AI suggests appropriate {parameter_name} values",
                f"Suggestions are contextually relevant",
                f"User accepts the suggested {parameter_name} values"
            ],
            failure_handling=[
                f"If {parameter_name} suggestion fails, ask user for clarification",
                f"Provide fallback options for {parameter_name}",
                f"Log suggestion failures for improvement"
            ]
        )

        self.register_enhancement(enhancement)
        return enhancement

    def create_error_learning_enhancement(
        self,
        tool_name: str,
        description: str,
        ai_instructions: str,
        examples: List[Dict[str, Any]],
        priority: EnhancementPriority = EnhancementPriority.CRITICAL
    ) -> AIEnhancement:
        """Create an error learning enhancement for a tool."""
        enhancement_id = f"{tool_name}_error_learning"

        enhancement = AIEnhancement(
            enhancement_id=enhancement_id,
            tool_name=tool_name,
            enhancement_type=EnhancementType.ERROR_LEARNING,
            priority=priority,
            title=f"Error learning for {tool_name}",
            description=description,
            ai_instructions=ai_instructions,
            examples=examples,
            trigger_conditions=[
                f"Tool {tool_name} execution fails", f"Error occurs during {tool_name} usage"],
            success_criteria=[
                f"AI learns from {tool_name} errors",
                f"Subsequent attempts are improved",
                f"Error patterns are recognized and avoided"
            ],
            failure_handling=[
                f"If error learning fails, log the failure for analysis",
                f"Provide fallback error handling strategies",
                f"Ask user for guidance on error resolution"
            ]
        )

        self.register_enhancement(enhancement)
        return enhancement

    def create_validation_enhancement(
        self,
        tool_name: str,
        description: str,
        ai_instructions: str,
        examples: List[Dict[str, Any]],
        priority: EnhancementPriority = EnhancementPriority.CRITICAL
    ) -> AIEnhancement:
        """Create a validation enhancement for a tool."""
        enhancement_id = f"{tool_name}_validation"

        enhancement = AIEnhancement(
            enhancement_id=enhancement_id,
            tool_name=tool_name,
            enhancement_type=EnhancementType.VALIDATION,
            priority=priority,
            title=f"Validation for {tool_name}",
            description=description,
            ai_instructions=ai_instructions,
            examples=examples,
            trigger_conditions=[
                f"Tool {tool_name} execution completes", f"Result from {tool_name} needs verification"],
            success_criteria=[
                f"AI validates {tool_name} results",
                f"Success/failure is accurately determined",
                f"User receives accurate status information"
            ],
            failure_handling=[
                f"If validation fails, ask user for confirmation",
                f"Provide alternative validation methods",
                f"Log validation failures for improvement"
            ]
        )

        self.register_enhancement(enhancement)
        return enhancement

    def create_conversational_guidance_enhancement(
        self,
        tool_name: str,
        description: str,
        ai_instructions: str,
        examples: List[Dict[str, Any]],
        priority: EnhancementPriority = EnhancementPriority.HIGH
    ) -> AIEnhancement:
        """Create a conversational guidance enhancement for a tool."""
        enhancement_id = f"{tool_name}_conversational_guidance"

        enhancement = AIEnhancement(
            enhancement_id=enhancement_id,
            tool_name=tool_name,
            enhancement_type=EnhancementType.CONVERSATIONAL_GUIDANCE,
            priority=priority,
            title=f"Conversational guidance for {tool_name}",
            description=description,
            ai_instructions=ai_instructions,
            examples=examples,
            trigger_conditions=[
                f"User requests to use {tool_name}", f"Missing information for {tool_name}"],
            success_criteria=[
                f"AI engages in helpful conversation to gather information",
                f"User provides necessary details through conversation",
                f"Tool execution proceeds with complete information"
            ],
            failure_handling=[
                f"If conversation fails, ask user to provide information directly",
                f"Suggest alternative approaches if information cannot be gathered",
                f"Provide clear examples of what information is needed"
            ]
        )

        self.register_enhancement(enhancement)
        return enhancement

    def create_intent_recognition_enhancement(
        self,
        tool_name: str,
        intent_patterns: List[str],
        recognition_logic: str,
        examples: List[Dict[str, Any]],
        priority: EnhancementPriority = EnhancementPriority.HIGH
    ) -> AIEnhancement:
        """Create an intent recognition enhancement for a tool."""
        enhancement_id = f"{tool_name}_intent_recognition"

        enhancement = AIEnhancement(
            enhancement_id=enhancement_id,
            tool_name=tool_name,
            enhancement_type=EnhancementType.INTENT_RECOGNITION,
            priority=priority,
            title=f"Intent recognition for {tool_name}",
            description=f"Recognizes when users want to use {tool_name} based on their requests",
            ai_instructions=f"Analyze user requests to identify when they want to use {tool_name}. Look for patterns like: {', '.join(intent_patterns)}. Use the recognition logic: {recognition_logic}",
            examples=examples,
            trigger_conditions=["User makes a request",
                                "Request might involve tool usage"],
            success_criteria=[
                f"AI correctly identifies when to use {tool_name}",
                f"Intent recognition is accurate and timely",
                f"User confirms the tool selection"
            ],
            failure_handling=[
                f"If intent is unclear, ask for clarification",
                f"Suggest alternative tools if {tool_name} is not appropriate",
                f"Learn from user corrections to improve recognition"
            ]
        )

        self.register_enhancement(enhancement)
        return enhancement

    def create_workflow_suggestion_enhancement(
        self,
        tool_names: List[str],
        workflow_description: str,
        workflow_steps: List[Dict[str, Any]],
        examples: List[Dict[str, Any]],
        priority: EnhancementPriority = EnhancementPriority.HIGH
    ) -> AIEnhancement:
        """Create a workflow suggestion enhancement for multiple tools."""
        enhancement_id = f"workflow_{'_'.join(tool_names)}"

        enhancement = AIEnhancement(
            enhancement_id=enhancement_id,
            tool_name=", ".join(tool_names),
            enhancement_type=EnhancementType.WORKFLOW_SUGGESTION,
            priority=priority,
            title=f"Workflow: {workflow_description}",
            description=f"Suggests using {', '.join(tool_names)} together for complex tasks",
            ai_instructions=f"When users request complex tasks, suggest using {', '.join(tool_names)} in sequence. Follow the workflow steps: {workflow_description}",
            examples=examples,
            trigger_conditions=["User requests complex task",
                                "Task requires multiple tools"],
            success_criteria=[
                "AI suggests appropriate tool combination",
                "Workflow is executed successfully",
                "User achieves desired outcome efficiently"
            ],
            failure_handling=[
                "If workflow fails, provide alternative approaches",
                "Handle errors gracefully in each step",
                "Suggest manual completion if automation fails"
            ]
        )

        self.register_enhancement(enhancement)
        return enhancement

    def export_enhancements(self, tool_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export enhancements for specified tools or all tools."""
        if tool_names is None:
            tools_to_export = list(self.tool_enhancements.keys())
        else:
            tools_to_export = [
                name for name in tool_names if name in self.tool_enhancements]

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "enhancements_version": "1.0.0",
            "enhancements": {}
        }

        for tool_name in tools_to_export:
            enhancements = self.get_tool_enhancements(tool_name)
            export_data["enhancements"][tool_name] = [
                enhancement.to_dict() for enhancement in enhancements
            ]

        return export_data

    def import_enhancements(self, enhancements_data: Dict[str, Any]) -> List[str]:
        """Import enhancements from exported data."""
        imported_enhancements = []

        for tool_name, tool_enhancements in enhancements_data.get("enhancements", {}).items():
            for enh_data in tool_enhancements:
                try:
                    enhancement = AIEnhancement(
                        enhancement_id=enh_data["enhancement_id"],
                        tool_name=enh_data["tool_name"],
                        enhancement_type=EnhancementType(
                            enh_data["enhancement_type"]),
                        priority=EnhancementPriority(enh_data["priority"]),
                        title=enh_data.get("title", ""),
                        description=enh_data.get("description", ""),
                        ai_instructions=enh_data.get("ai_instructions", ""),
                        examples=enh_data.get("examples", []),
                        trigger_conditions=enh_data.get(
                            "trigger_conditions", []),
                        success_criteria=enh_data.get("success_criteria", []),
                        failure_handling=enh_data.get("failure_handling", []),
                        version=enh_data.get("version", "1.0.0"),
                        is_active=enh_data.get("is_active", True)
                    )

                    self.register_enhancement(enhancement)
                    imported_enhancements.append(enhancement.enhancement_id)

                except Exception as e:
                    self.logger.error(
                        f"Failed to import enhancement {enh_data.get('enhancement_id', 'unknown')}: {e}")

        return imported_enhancements

    def get_enhancements_summary(self) -> Dict[str, Any]:
        """Get a summary of all registered enhancements."""
        total_enhancements = len(self.enhancements)
        active_enhancements = len(
            [e for e in self.enhancements.values() if e.is_active])

        type_counts = {}
        priority_counts = {}
        tool_counts = {}

        for enhancement in self.enhancements.values():
            if not enhancement.is_active:
                continue

            # Count by type
            enh_type = enhancement.enhancement_type.value
            type_counts[enh_type] = type_counts.get(enh_type, 0) + 1

            # Count by priority
            enh_priority = enhancement.priority.value
            priority_counts[enh_priority] = priority_counts.get(
                enh_priority, 0) + 1

            # Count by tool
            tool_counts[enhancement.tool_name] = tool_counts.get(
                enhancement.tool_name, 0) + 1

        return {
            "total_enhancements": total_enhancements,
            "active_enhancements": active_enhancements,
            "type_distribution": type_counts,
            "priority_distribution": priority_counts,
            "tool_distribution": tool_counts,
            "last_updated": max(
                [enhancement.updated_at for enhancement in self.enhancements.values()],
                default=datetime.now()
            ).isoformat()
        }
