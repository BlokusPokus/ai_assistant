"""
Tool Metadata System

This module provides enhanced metadata for tools to improve AI understanding,
tool selection, and parameter suggestions.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ...config.logging_config import get_logger

logger = get_logger("tools.metadata")


class ToolComplexity(Enum):
    """Tool complexity levels for AI understanding."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class ToolCategory(Enum):
    """Tool categories for organization and AI selection."""

    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    INFORMATION = "information"
    AUTOMATION = "automation"
    INTEGRATION = "integration"


@dataclass
class ToolUseCase:
    """Represents a specific use case for a tool."""

    name: str
    description: str
    example_request: str
    example_parameters: Dict[str, Any]
    expected_outcome: str
    success_indicators: List[str]
    failure_modes: List[str]
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class ToolExample:
    """Represents a concrete example of tool usage."""

    description: str
    user_request: str
    parameters: Dict[str, Any]
    expected_result: str
    notes: Optional[str] = None


@dataclass
class ToolMetadata:
    """Enhanced metadata for a tool to improve AI understanding."""

    # Basic tool information
    tool_name: str
    tool_version: str = "1.0.0"
    description: str = ""
    category: ToolCategory = ToolCategory.PRODUCTIVITY
    complexity: ToolComplexity = ToolComplexity.SIMPLE

    # AI understanding enhancements
    use_cases: List[ToolUseCase] = field(default_factory=list)
    examples: List[ToolExample] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

    # Tool relationships
    related_tools: List[str] = field(default_factory=list)
    complementary_tools: List[str] = field(default_factory=list)
    conflicting_tools: List[str] = field(default_factory=list)

    # Performance and reliability
    execution_time: str = "1-5 seconds"
    success_rate: float = 0.95
    rate_limits: Optional[str] = None
    retry_strategy: Optional[str] = None

    # AI guidance
    ai_instructions: str = ""
    parameter_guidance: Dict[str, str] = field(default_factory=dict)
    common_mistakes: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)

    # Metadata management
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "description": self.description,
            "category": self.category.value,
            "complexity": self.complexity.value,
            "use_cases": [
                {
                    "name": uc.name,
                    "description": uc.description,
                    "example_request": uc.example_request,
                    "example_parameters": uc.example_parameters,
                    "expected_outcome": uc.expected_outcome,
                    "success_indicators": uc.success_indicators,
                    "failure_modes": uc.failure_modes,
                    "prerequisites": uc.prerequisites,
                }
                for uc in self.use_cases
            ],
            "examples": [
                {
                    "description": ex.description,
                    "user_request": ex.user_request,
                    "parameters": ex.parameters,
                    "expected_result": ex.expected_result,
                    "notes": ex.notes,
                }
                for ex in self.examples
            ],
            "prerequisites": self.prerequisites,
            "related_tools": self.related_tools,
            "complementary_tools": self.complementary_tools,
            "conflicting_tools": self.conflicting_tools,
            "execution_time": self.execution_time,
            "success_rate": self.success_rate,
            "rate_limits": self.rate_limits,
            "retry_strategy": self.retry_strategy,
            "ai_instructions": self.ai_instructions,
            "parameter_guidance": self.parameter_guidance,
            "common_mistakes": self.common_mistakes,
            "best_practices": self.best_practices,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata_version": self.metadata_version,
        }

    def to_json(self) -> str:
        """Convert metadata to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def update_metadata(self, **kwargs):
        """Update metadata fields and set updated timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.updated_at = datetime.now()
        logger.info(f"Updated metadata for tool: {self.tool_name}")

    def add_use_case(self, use_case: ToolUseCase):
        """Add a new use case to the tool."""
        self.use_cases.append(use_case)
        self.updated_at = datetime.now()
        logger.info(f"Added use case '{use_case.name}' to tool: {self.tool_name}")

    def add_example(self, example: ToolExample):
        """Add a new example to the tool."""
        self.examples.append(example)
        self.updated_at = datetime.now()
        logger.info(f"Added example to tool: {self.tool_name}")

    def get_ai_guidance(self) -> Dict[str, Any]:
        """Get AI-specific guidance for this tool."""
        return {
            "tool_name": self.tool_name,
            "description": self.description,
            "category": self.category.value,
            "complexity": self.complexity.value,
            "use_cases": [uc.name for uc in self.use_cases],
            "examples": [
                {
                    "description": ex.description,
                    "user_request": ex.user_request,
                    "parameters": ex.parameters,
                }
                for ex in self.examples
            ],
            "prerequisites": self.prerequisites,
            "related_tools": self.related_tools,
            "ai_instructions": self.ai_instructions,
            "parameter_guidance": self.parameter_guidance,
            "best_practices": self.best_practices,
        }


class ToolMetadataManager:
    """Manages tool metadata across the system."""

    def __init__(self):
        self.metadata_store: Dict[str, ToolMetadata] = {}
        self.category_index: Dict[ToolCategory, List[str]] = {}
        self.logger = get_logger("tools.metadata.manager")

    def register_tool_metadata(self, metadata: ToolMetadata):
        """Register metadata for a tool."""
        self.metadata_store[metadata.tool_name] = metadata

        # Update category index
        if metadata.category not in self.category_index:
            self.category_index[metadata.category] = []
        self.category_index[metadata.category].append(metadata.tool_name)

        self.logger.info(f"Registered metadata for tool: {metadata.tool_name}")

    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self.metadata_store.get(tool_name)

    def get_tools_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """Get all tools in a specific category."""
        tool_names = self.category_index.get(category, [])
        return [
            self.metadata_store[name]
            for name in tool_names
            if name in self.metadata_store
        ]

    def get_tools_by_complexity(self, complexity: ToolComplexity) -> List[ToolMetadata]:
        """Get all tools with a specific complexity level."""
        return [
            metadata
            for metadata in self.metadata_store.values()
            if metadata.complexity == complexity
        ]

    def search_tools(self, query: str) -> List[ToolMetadata]:
        """Search tools by query in name, description, or use cases."""
        query_lower = query.lower()
        results = []

        for metadata in self.metadata_store.values():
            # Search in tool name
            if query_lower in metadata.tool_name.lower():
                results.append(metadata)
                continue

            # Search in description
            if query_lower in metadata.description.lower():
                results.append(metadata)
                continue

            # Search in use cases
            for use_case in metadata.use_cases:
                if (
                    query_lower in use_case.name.lower()
                    or query_lower in use_case.description.lower()
                ):
                    results.append(metadata)
                    break

        return results

    def get_ai_guidance_for_tools(self, tool_names: List[str]) -> Dict[str, Any]:
        """Get AI guidance for multiple tools."""
        guidance = {}
        for tool_name in tool_names:
            metadata = self.get_tool_metadata(tool_name)
            if metadata:
                guidance[tool_name] = metadata.get_ai_guidance()

        return guidance

    def export_metadata(self, tool_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export metadata for specified tools or all tools."""
        if tool_names is None:
            tools_to_export = list(self.metadata_store.keys())
        else:
            tools_to_export = [
                name for name in tool_names if name in self.metadata_store
            ]

        export_data: dict[str, Any] = {
            "export_timestamp": datetime.now().isoformat(),
            "metadata_version": "1.0.0",
            "tools": {},
        }

        for tool_name in tools_to_export:
            metadata = self.metadata_store[tool_name]
            export_data["tools"][tool_name] = metadata.to_dict()

        return export_data

    def import_metadata(self, metadata_data: Dict[str, Any]) -> List[str]:
        """Import metadata from exported data."""
        imported_tools = []

        for tool_name, tool_data in metadata_data.get("tools", {}).items():
            try:
                # Create ToolUseCase objects
                use_cases = []
                for uc_data in tool_data.get("use_cases", []):
                    use_case = ToolUseCase(
                        name=uc_data["name"],
                        description=uc_data["description"],
                        example_request=uc_data["example_request"],
                        example_parameters=uc_data["example_parameters"],
                        expected_outcome=uc_data["expected_outcome"],
                        success_indicators=uc_data["success_indicators"],
                        failure_modes=uc_data["failure_modes"],
                        prerequisites=uc_data.get("prerequisites", []),
                    )
                    use_cases.append(use_case)

                # Create ToolExample objects
                examples = []
                for ex_data in tool_data.get("examples", []):
                    example = ToolExample(
                        description=ex_data["description"],
                        user_request=ex_data["user_request"],
                        parameters=ex_data["parameters"],
                        expected_result=ex_data["expected_result"],
                        notes=ex_data.get("notes"),
                    )
                    examples.append(example)

                # Create ToolMetadata object
                metadata = ToolMetadata(
                    tool_name=tool_data["tool_name"],
                    tool_version=tool_data.get("tool_version", "1.0.0"),
                    description=tool_data.get("description", ""),
                    category=ToolCategory(tool_data.get("category", "productivity")),
                    complexity=ToolComplexity(tool_data.get("complexity", "simple")),
                    use_cases=use_cases,
                    examples=examples,
                    prerequisites=tool_data.get("prerequisites", []),
                    related_tools=tool_data.get("related_tools", []),
                    complementary_tools=tool_data.get("complementary_tools", []),
                    conflicting_tools=tool_data.get("conflicting_tools", []),
                    execution_time=tool_data.get("execution_time", "1-5 seconds"),
                    success_rate=tool_data.get("success_rate", 0.95),
                    rate_limits=tool_data.get("rate_limits"),
                    retry_strategy=tool_data.get("retry_strategy"),
                    ai_instructions=tool_data.get("ai_instructions", ""),
                    parameter_guidance=tool_data.get("parameter_guidance", {}),
                    common_mistakes=tool_data.get("common_mistakes", []),
                    best_practices=tool_data.get("best_practices", []),
                )

                self.register_tool_metadata(metadata)
                imported_tools.append(tool_name)

            except Exception as e:
                self.logger.error(
                    f"Failed to import metadata for tool {tool_name}: {e}"
                )

        return imported_tools

    def get_metadata_summary(self) -> Dict[str, Any]:
        """Get a summary of all registered metadata."""
        total_tools = len(self.metadata_store)
        category_counts = {
            cat.value: len(tools) for cat, tools in self.category_index.items()
        }
        complexity_counts: dict[str, int] = {}

        for metadata in self.metadata_store.values():
            complexity = metadata.complexity.value
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1

        return {
            "total_tools": total_tools,
            "category_distribution": category_counts,
            "complexity_distribution": complexity_counts,
            "last_updated": max(
                [metadata.updated_at for metadata in self.metadata_store.values()],
                default=datetime.now(),
            ).isoformat(),
        }
