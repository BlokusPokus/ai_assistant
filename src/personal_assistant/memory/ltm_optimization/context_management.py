"""
Consolidated Context Management Module

This module combines context optimization and context data structures
into a single, manageable interface for LTM context management.
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional

from ...config.logging_config import get_logger
from ...types.state import AgentState
from .config import LTMConfig

logger = get_logger("context_management")


# ============================================================================
# CONTEXT DATA STRUCTURES
# ============================================================================


class ContextType(Enum):
    """Types of context information"""

    TEMPORAL = "temporal"  # Time-based context
    SPATIAL = "spatial"  # Location-based context
    SOCIAL = "social"  # People and relationships
    ENVIRONMENTAL = "environmental"  # Environmental factors
    EMOTIONAL = "emotional"  # Emotional state
    COGNITIVE = "cognitive"  # Mental state and focus
    TECHNICAL = "technical"  # Technical context
    CUSTOM = "custom"  # Custom context types


class SourceType(Enum):
    """Types of memory sources"""

    CONVERSATION = "conversation"
    TOOL_USAGE = "tool_usage"
    MANUAL = "manual"
    PATTERN_DETECTION = "pattern_detection"
    AUTOMATED = "automated"
    IMPORT = "import"


class MemoryType(Enum):
    """Types of memories"""

    PREFERENCE = "preference"
    INSIGHT = "insight"
    PATTERN = "pattern"
    FACT = "fact"
    GOAL = "goal"
    HABIT = "habit"
    ROUTINE = "routine"
    RELATIONSHIP = "relationship"
    SKILL = "skill"
    KNOWLEDGE = "knowledge"


@dataclass
class TemporalContext:
    """Temporal context information"""

    timestamp: datetime
    time_of_day: Optional[time] = None
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None
    month: Optional[int] = None
    season: Optional[str] = None
    is_weekend: Optional[bool] = None
    is_holiday: Optional[bool] = None
    timezone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "time_of_day": self.time_of_day.isoformat() if self.time_of_day else None,
            "day_of_week": self.day_of_week,
            "day_of_month": self.day_of_month,
            "month": self.month,
            "season": self.season,
            "is_weekend": self.is_weekend,
            "is_holiday": self.is_holiday,
            "timezone": self.timezone,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemporalContext":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            time_of_day=time.fromisoformat(data["time_of_day"])
            if data.get("time_of_day")
            else None,
            day_of_week=data.get("day_of_week"),
            day_of_month=data.get("day_of_month"),
            month=data.get("month"),
            season=data.get("season"),
            is_weekend=data.get("is_weekend"),
            is_holiday=data.get("is_holiday"),
            timezone=data.get("timezone"),
        )


@dataclass
class SpatialContext:
    """Spatial context information"""

    location: Optional[str] = None
    coordinates: Optional[tuple] = None  # (lat, lon)
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "location": self.location,
            "coordinates": self.coordinates,
            "venue": self.venue,
            "city": self.city,
            "country": self.country,
            "timezone": self.timezone,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpatialContext":
        """Create from dictionary"""
        return cls(
            location=data.get("location"),
            coordinates=data.get("coordinates"),
            venue=data.get("venue"),
            city=data.get("city"),
            country=data.get("country"),
            timezone=data.get("timezone"),
        )


@dataclass
class SocialContext:
    """Social context information"""

    people_present: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    group_size: Optional[int] = None
    interaction_type: Optional[str] = None
    mood: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "people_present": self.people_present,
            "relationships": self.relationships,
            "group_size": self.group_size,
            "interaction_type": self.interaction_type,
            "mood": self.mood,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialContext":
        """Create from dictionary"""
        return cls(
            people_present=data.get("people_present", []),
            relationships=data.get("relationships", {}),
            group_size=data.get("group_size"),
            interaction_type=data.get("interaction_type"),
            mood=data.get("mood"),
        )


@dataclass
class EnvironmentalContext:
    """Environmental context information"""

    weather: Optional[str] = None
    temperature: Optional[float] = None
    lighting: Optional[str] = None
    noise_level: Optional[str] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "weather": self.weather,
            "temperature": self.temperature,
            "lighting": self.lighting,
            "noise_level": self.noise_level,
            "device_type": self.device_type,
            "platform": self.platform,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentalContext":
        """Create from dictionary"""
        return cls(
            weather=data.get("weather"),
            temperature=data.get("temperature"),
            lighting=data.get("lighting"),
            noise_level=data.get("noise_level"),
            device_type=data.get("device_type"),
            platform=data.get("platform"),
        )


@dataclass
class MemoryContext:
    """Complete context for a memory"""

    temporal: Optional[TemporalContext] = None
    spatial: Optional[SpatialContext] = None
    social: Optional[SocialContext] = None
    environmental: Optional[EnvironmentalContext] = None
    custom: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "temporal": self.temporal.to_dict() if self.temporal else None,
            "spatial": self.spatial.to_dict() if self.spatial else None,
            "social": self.social.to_dict() if self.social else None,
            "environmental": self.environmental.to_dict()
            if self.environmental
            else None,
            "custom": self.custom,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryContext":
        """Create from dictionary"""
        return cls(
            temporal=TemporalContext.from_dict(data["temporal"])
            if data.get("temporal")
            else None,
            spatial=SpatialContext.from_dict(data["spatial"])
            if data.get("spatial")
            else None,
            social=SocialContext.from_dict(data["social"])
            if data.get("social")
            else None,
            environmental=EnvironmentalContext.from_dict(data["environmental"])
            if data.get("environmental")
            else None,
            custom=data.get("custom", {}),
        )


# ============================================================================
# CONTEXT OPTIMIZATION
# ============================================================================


class ContextOptimizationManager:
    """Optimizes LTM context for injection into agent"""

    def __init__(self, config: Optional[LTMConfig] = None):
        self.config = config or LTMConfig()

    async def optimize_ltm_context(
        self, memories: List[dict], user_input: str, max_length: Optional[int] = None
    ) -> str:
        """Optimize LTM context for injection"""

        if not memories:
            return ""

        if max_length is None:
            max_length = self.config.max_context_length

        # Step 1: Prioritize memories by relevance and importance
        prioritized_memories = self._prioritize_memories(memories, user_input)

        # Step 2: Format memories efficiently
        formatted_context = self._format_memories_efficiently(prioritized_memories)

        # Step 3: Truncate if too long
        if len(formatted_context) > max_length:
            formatted_context = self._truncate_context(formatted_context, max_length)

        logger.info(
            f"Optimized context: {len(formatted_context)} chars from {len(memories)} memories"
        )
        return formatted_context

    def _prioritize_memories(self, memories: List[dict], user_input: str) -> List[dict]:
        """Prioritize memories by relevance and importance"""

        # Score each memory
        scored_memories = []
        for memory in memories:
            score = self._calculate_memory_score(memory, user_input)
            scored_memories.append((memory, score))

        # Sort by score (highest first)
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        return [memory for memory, score in scored_memories]

    def _calculate_memory_score(self, memory: dict, user_input: str) -> float:
        """Calculate overall score for memory prioritization"""

        # Base score from importance
        base_score = memory.get("importance_score", 1) / 10.0

        # Relevance boost
        relevance_boost = self._calculate_relevance_boost(memory, user_input)

        # Recency boost
        recency_boost = self._calculate_recency_boost(memory.get("last_accessed") or "")

        # Type-specific boost
        type_boost = self._calculate_type_boost(memory.get("type", "general"))

        total_score = base_score + relevance_boost + recency_boost + type_boost
        return min(1.0, total_score)

    def _calculate_relevance_boost(self, memory: dict, user_input: str) -> float:
        """Calculate relevance boost for memory"""

        memory_tags = set(memory.get("tags", []))
        context_words = set(user_input.lower().split())

        # Check tag overlap
        tag_matches = sum(1 for tag in memory_tags if tag.lower() in context_words)
        if memory_tags:
            tag_score = tag_matches / len(memory_tags)
            return tag_score * 0.3  # 30% weight for relevance

        return 0.0

    def _calculate_recency_boost(self, last_accessed: str) -> float:
        """Calculate recency boost for memory"""

        if not last_accessed:
            return 0.0

        try:
            last_accessed_dt = datetime.fromisoformat(last_accessed)
            days_ago = (datetime.now() - last_accessed_dt).days

            if days_ago <= 1:
                return 0.4  # Very recent
            elif days_ago <= 7:
                return 0.2  # Recent
            elif days_ago <= 30:
                return 0.1  # Somewhat recent
            else:
                return 0.0  # Old
        except (ValueError, TypeError):
            return 0.0

    def _calculate_type_boost(self, memory_type: str) -> float:
        """Calculate type-specific boost for memory"""

        type_boosts = {
            "preference": 0.2,
            "insight": 0.15,
            "pattern": 0.1,
            "fact": 0.05,
            "goal": 0.1,
            "habit": 0.15,
            "routine": 0.1,
            "relationship": 0.1,
            "skill": 0.1,
            "knowledge": 0.05,
            "general": 0.0,
        }

        return type_boosts.get(memory_type, 0.0)

    def _format_memories_efficiently(self, memories: List[dict]) -> str:
        """Format memories into efficient context string"""

        if not memories:
            return ""

        context_parts = []
        for memory in memories:
            # Format each memory efficiently
            formatted = self._format_single_memory(memory)
            if formatted:
                context_parts.append(formatted)

        return "\n".join(context_parts)

    def _format_single_memory(self, memory: dict) -> str:
        """Format a single memory efficiently"""

        memory_type = memory.get("type", "general")
        content = memory.get("content", "")
        tags = memory.get("tags", [])

        # Type-specific formatting
        if memory_type == "preference":
            return f"Pref: {content} [{' '.join(tags[:3])}]"
        elif memory_type == "insight":
            return f"Insight: {content} [{' '.join(tags[:3])}]"
        elif memory_type == "pattern":
            return f"Pattern: {content} [{' '.join(tags[:3])}]"
        else:
            return f"{content} [{' '.join(tags[:3])}]"

    def _truncate_context(self, context: str, max_length: int) -> str:
        """Truncate context to fit within length limits"""

        if len(context) <= max_length:
            return context

        # Try to truncate at sentence boundaries
        sentences = context.split(". ")
        truncated = ""

        for sentence in sentences:
            if len(truncated + sentence + ". ") <= max_length:
                truncated += sentence + ". "
            else:
                break

        if not truncated:
            # Fallback: truncate at word boundaries
            words = context.split()
            truncated = ""
            for word in words:
                if len(truncated + word + " ") <= max_length:
                    truncated += word + " "
                else:
                    break

        return truncated.strip()


class DynamicContextManager:
    """
    Dynamic Context Manager with State Coordination

    This class provides intelligent context optimization with dynamic sizing,
    state context integration, and focus area coordination.
    """

    def __init__(self, config: Optional[LTMConfig] = None):
        self.config = config or LTMConfig()
        self.logger = get_logger("dynamic_context_manager")

        # Context sizing configuration
        self.min_context_length = getattr(self.config, "min_context_length", 100)
        self.max_context_length = getattr(self.config, "max_context_length", 2000)
        self.optimal_context_length = getattr(
            self.config, "optimal_context_length", 800
        )

        # Complexity thresholds
        self.simple_query_threshold = getattr(self.config, "simple_query_threshold", 50)
        self.complex_query_threshold = getattr(
            self.config, "complex_query_threshold", 200
        )

        # Focus area configuration
        self.focus_boost_multiplier = getattr(
            self.config, "focus_boost_multiplier", 1.5
        )
        self.state_context_weight = getattr(self.config, "state_context_weight", 0.3)

    async def optimize_context_with_state(
        self,
        memories: List[dict],
        user_input: str,
        state_context: Optional["AgentState"] = None,
        focus_areas: Optional[List[str]] = None,
        query_complexity: str = "medium",
    ) -> str:
        """
        Optimize context with state coordination and dynamic sizing

        Args:
            memories: List of memories to optimize
            user_input: User's input for relevance calculation
            state_context: Current agent state for context coordination
            focus_areas: Current focus areas for prioritization
            query_complexity: Query complexity level (simple, medium, complex)

        Returns:
            Optimized context string
        """

        if not memories:
            return ""

        # Step 1: Calculate dynamic context size based on input complexity
        dynamic_max_length = self._calculate_dynamic_context_size(
            user_input, query_complexity, state_context
        )

        # Step 2: Prioritize memories with state context consideration
        prioritized_memories = await self._prioritize_memories_with_state(
            memories, user_input, state_context, focus_areas
        )

        # Step 3: Apply intelligent memory selection
        selected_memories = self._select_memories_intelligently(
            prioritized_memories, dynamic_max_length
        )

        # Step 4: Format and summarize context
        formatted_context = self._format_context_with_summarization(
            selected_memories, dynamic_max_length
        )

        # Step 5: Apply final length optimization
        final_context = self._apply_length_optimization(
            formatted_context, dynamic_max_length
        )

        self.logger.info(
            f"Dynamic context optimization: {len(final_context)} chars from {len(memories)} memories "
            f"(complexity: {query_complexity}, state: {state_context is not None})"
        )

        return final_context

    def _calculate_dynamic_context_size(
        self, user_input: str, query_complexity: str, state_context: Optional["AgentState"] = None
    ) -> int:
        """Calculate dynamic context size based on input complexity and state"""

        base_length = self.optimal_context_length

        # Adjust based on query complexity
        complexity_multipliers = {
            "simple": 0.6,  # Simple queries need less context
            "medium": 1.0,  # Standard queries
            "complex": 1.4,  # Complex queries need more context
        }

        multiplier = complexity_multipliers.get(query_complexity, 1.0)

        # Adjust based on input length
        input_length = len(user_input)
        if input_length < self.simple_query_threshold:
            length_multiplier = 0.8  # Short inputs
        elif input_length < self.complex_query_threshold:
            length_multiplier = 1.0  # Medium inputs
        else:
            length_multiplier = 1.3  # Long inputs

        # Adjust based on state context availability
        state_multiplier = 1.2 if state_context else 1.0

        # Calculate final length
        dynamic_length = int(
            base_length * multiplier * length_multiplier * state_multiplier
        )

        # Ensure within bounds
        return max(
            self.min_context_length, min(dynamic_length, self.max_context_length)
        )

    async     def _prioritize_memories_with_state(
        self,
        memories: List[dict],
        user_input: str,
        state_context: Optional["AgentState"] = None,
        focus_areas: Optional[List[str]] = None,
    ) -> List[dict]:
        """Prioritize memories with state context consideration"""

        # Score each memory
        scored_memories = []
        for memory in memories:
            score = self._calculate_comprehensive_memory_score(
                memory, user_input, state_context, focus_areas
            )
            scored_memories.append((memory, score))

        # Sort by score (highest first)
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        return [memory for memory, score in scored_memories]

    def _calculate_comprehensive_memory_score(
        self,
        memory: dict,
        user_input: str,
        state_context: Optional["AgentState"] = None,
        focus_areas: Optional[List[str]] = None,
    ) -> float:
        """Calculate comprehensive memory score with state context"""

        # Base score from importance
        base_score = memory.get("importance_score", 1) / 10.0

        # Relevance boost
        relevance_boost = self._calculate_enhanced_relevance_boost(memory, user_input)

        # Recency boost
        recency_boost = self._calculate_enhanced_recency_boost(
            memory.get("last_accessed") or "", memory.get("created_at")
        )

        # Type-specific boost
        type_boost = self._calculate_enhanced_type_boost(
            memory.get("memory_type", "general")
        )

        # State context boost
        state_boost = self._calculate_state_context_boost(memory, state_context)

        # Focus area boost
        focus_boost = self._calculate_focus_area_boost(memory, focus_areas or [])

        # Confidence boost
        confidence_boost = memory.get("confidence_score", 0.5) * 0.1

        total_score = (
            base_score
            + relevance_boost
            + recency_boost
            + type_boost
            + state_boost
            + focus_boost
            + confidence_boost
        )

        return min(1.0, total_score)

    def _calculate_enhanced_relevance_boost(
        self, memory: dict, user_input: str
    ) -> float:
        """Calculate enhanced relevance boost"""

        memory_tags = set(memory.get("tags", []))
        memory_content = memory.get("content", "").lower()
        context_words = set(user_input.lower().split())

        # Tag overlap
        tag_matches = sum(1 for tag in memory_tags if tag.lower() in context_words)
        tag_score = tag_matches / len(memory_tags) if memory_tags else 0

        # Content overlap
        content_words = set(memory_content.split())
        word_overlap = len(content_words & context_words) / max(
            len(content_words | context_words), 1
        )

        # Phrase matching
        context_phrases = self._extract_phrases(user_input)
        memory_phrases = self._extract_phrases(memory_content)
        phrase_overlap = len(context_phrases & memory_phrases) / max(
            len(context_phrases | memory_phrases), 1
        )

        return (tag_score * 0.4 + word_overlap * 0.4 + phrase_overlap * 0.2) * 0.3

    def _calculate_enhanced_recency_boost(
        self, last_accessed: str, created_at: Optional[str] = None
    ) -> float:
        """Calculate enhanced recency boost"""

        try:
            time_str = last_accessed or created_at
            if not time_str:
                return 0.0

            time_dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            days_ago = (datetime.now() - time_dt).days

            if days_ago <= 1:
                return 0.4  # Very recent
            elif days_ago <= 7:
                return 0.3  # Recent
            elif days_ago <= 30:
                return 0.2  # Somewhat recent
            elif days_ago <= 90:
                return 0.1  # Older
            else:
                return 0.0  # Very old

        except Exception:
            return 0.0

    def _calculate_enhanced_type_boost(self, memory_type: str) -> float:
        """Calculate enhanced type-specific boost"""

        type_boosts = {
            "user_preference": 0.25,
            "explicit_request": 0.3,
            "tool_usage": 0.2,
            "conversation": 0.1,
            "automation": 0.2,
            "preference": 0.25,
            "insight": 0.2,
            "pattern": 0.15,
            "fact": 0.05,
            "goal": 0.15,
            "habit": 0.2,
            "routine": 0.15,
            "relationship": 0.15,
            "skill": 0.15,
            "knowledge": 0.1,
            "general": 0.0,
        }

        return type_boosts.get(memory_type, 0.0)

    def _calculate_state_context_boost(
        self, memory: dict, state_context: Optional["AgentState"] = None
    ) -> float:
        """Calculate boost based on state context relevance"""

        if not state_context:
            return 0.0

        boost = 0.0

        # Focus area matching
        if hasattr(state_context, "focus") and state_context.focus:
            focus_areas = (
                state_context.focus
                if isinstance(state_context.focus, list)
                else [state_context.focus]
            )
            memory_tags = set(memory.get("tags", []))
            memory_content = memory.get("content", "").lower()

            for focus in focus_areas:
                focus_lower = focus.lower()
                if focus_lower in memory_content:
                    boost += 0.2
                if any(focus_lower in tag.lower() for tag in memory_tags):
                    boost += 0.15

        # Tool usage context matching
        if (
            hasattr(state_context, "last_tool_result")
            and state_context.last_tool_result
        ):
            str(state_context.last_tool_result).lower()
            memory_content = memory.get("content", "").lower()

            if any(
                tool_word in memory_content
                for tool_word in ["tool", "function", "api", "automation"]
            ):
                boost += 0.15

        return min(0.4, boost) * self.state_context_weight

    def _calculate_focus_area_boost(
        self, memory: dict, focus_areas: Optional[List[str]] = None
    ) -> float:
        """Calculate boost based on focus areas"""

        if not focus_areas:
            return 0.0

        memory_tags = set(memory.get("tags", []))
        memory_content = memory.get("content", "").lower()

        focus_matches = 0
        for focus in focus_areas:
            focus_lower = focus.lower()
            if focus_lower in memory_content:
                focus_matches += 1
            if any(focus_lower in tag.lower() for tag in memory_tags):
                focus_matches += 1

        if focus_matches > 0:
            return min(0.3, focus_matches * 0.1) * self.focus_boost_multiplier

        return 0.0

    def _extract_phrases(
        self, text: str, min_length: int = 2, max_length: int = 4
    ) -> set:
        """Extract meaningful phrases from text"""

        words = text.lower().split()
        phrases = set()

        for length in range(min_length, min(max_length + 1, len(words) + 1)):
            for i in range(len(words) - length + 1):
                phrase = " ".join(words[i : i + length])
                if len(phrase) > 3:  # Filter out very short phrases
                    phrases.add(phrase)

        return phrases

    def _select_memories_intelligently(
        self, prioritized_memories: List[dict], target_length: int
    ) -> List[dict]:
        """Intelligently select memories to fit within target length"""

        selected_memories = []
        current_length = 0

        for memory in prioritized_memories:
            # Estimate memory length
            estimated_length = self._estimate_memory_length(memory)

            # Check if adding this memory would exceed target
            if current_length + estimated_length <= target_length:
                selected_memories.append(memory)
                current_length += estimated_length
            else:
                # Try to add a shorter version if possible
                shortened_memory = self._create_shortened_memory(
                    memory, target_length - current_length
                )
                if shortened_memory:
                    selected_memories.append(shortened_memory)
                break

        return selected_memories

    def _estimate_memory_length(self, memory: dict) -> int:
        """Estimate the length of a memory when formatted"""

        content = memory.get("content", "")
        tags = memory.get("tags", [])
        memory_type = memory.get("memory_type", "general")

        # Base length from content
        base_length = len(content)

        # Add length for tags
        tags_length = len(" ".join(tags)) if tags else 0

        # Add length for type prefix
        type_prefix_length = (
            len(f"{memory_type.title()}: ") if memory_type != "general" else 0
        )

        return (
            base_length + tags_length + type_prefix_length + 20
        )  # Buffer for formatting

    def _create_shortened_memory(self, memory: dict, max_length: int) -> Optional[dict]:
        """Create a shortened version of a memory"""

        if max_length < 50:  # Too short to be useful
            return None

        content = memory.get("content", "")
        if len(content) <= max_length:
            return memory

        # Try to truncate at sentence boundaries
        sentences = content.split(". ")
        shortened_content = ""

        for sentence in sentences:
            if len(shortened_content + sentence + ". ") <= max_length:
                shortened_content += sentence + ". "
            else:
                break

        if shortened_content:
            shortened_memory = memory.copy()
            shortened_memory["content"] = shortened_content.strip()
            shortened_memory["_shortened"] = True
            return shortened_memory

        return None

    def _format_context_with_summarization(
        self, memories: List[dict], target_length: int
    ) -> str:
        """Format context with intelligent summarization"""

        if not memories:
            return ""

        # Group memories by type for better organization
        grouped_memories = self._group_memories_by_type(memories)

        # Format each group
        context_parts = []
        for memory_type, type_memories in grouped_memories.items():
            if type_memories:
                type_context = self._format_memory_group(memory_type, type_memories)
                if type_context:
                    context_parts.append(type_context)

        # Join all parts
        full_context = "\n\n".join(context_parts)

        # If still too long, apply summarization
        if len(full_context) > target_length:
            full_context = self._summarize_context(full_context, target_length)

        return full_context

    def _group_memories_by_type(self, memories: List[dict]) -> Dict[str, List[dict]]:
        """Group memories by type for better organization"""

        grouped: Dict[str, List[dict]] = {}
        for memory in memories:
            memory_type = memory.get("memory_type", "general")
            if memory_type not in grouped:
                grouped[memory_type] = []
            grouped[memory_type].append(memory)

        return grouped

    def _format_memory_group(self, memory_type: str, memories: List[dict]) -> str:
        """Format a group of memories of the same type"""

        if not memories:
            return ""

        # Type header
        type_header = f"**{memory_type.replace('_', ' ').title()}:**"

        # Format individual memories
        memory_lines = []
        for memory in memories:
            content = memory.get("content", "")
            tags = memory.get("tags", [])
            importance = memory.get("importance_score", 1)

            # Format based on importance
            if importance >= 8:
                prefix = "🔴 "  # High importance
            elif importance >= 6:
                prefix = "🟡 "  # Medium importance
            else:
                prefix = "🟢 "  # Lower importance

            # Add tags if available
            tag_suffix = f" [{' '.join(tags[:3])}]" if tags else ""

            memory_lines.append(f"{prefix}{content}{tag_suffix}")

        return f"{type_header}\n" + "\n".join(memory_lines)

    def _summarize_context(self, context: str, target_length: int) -> str:
        """Summarize context to fit within target length"""

        if len(context) <= target_length:
            return context

        # Try to keep the most important parts
        lines = context.split("\n")
        summarized_lines = []
        current_length = 0

        for line in lines:
            line_length = len(line) + 1  # +1 for newline

            if current_length + line_length <= target_length:
                summarized_lines.append(line)
                current_length += line_length
            else:
                # Add summary indicator
                remaining_length = target_length - current_length
                if remaining_length > 20:
                    summarized_lines.append(
                        f"... and {len(lines) - len(summarized_lines)} more memories"
                    )
                break

        return "\n".join(summarized_lines)

    def _apply_length_optimization(self, context: str, target_length: int) -> str:
        """Apply final length optimization"""

        if len(context) <= target_length:
            return context

        # Apply intelligent truncation
        return self._truncate_context_intelligently(context, target_length)

    def _truncate_context_intelligently(self, context: str, max_length: int) -> str:
        """Intelligently truncate context while preserving meaning"""

        if len(context) <= max_length:
            return context

        # Try to truncate at section boundaries first
        sections = context.split("\n\n")
        truncated_sections = []
        current_length = 0

        for section in sections:
            section_length = len(section) + 2  # +2 for double newline

            if current_length + section_length <= max_length:
                truncated_sections.append(section)
                current_length += section_length
            else:
                # Try to truncate this section
                remaining_length = max_length - current_length
                if remaining_length > 30:
                    truncated_section = self._truncate_section(
                        section, remaining_length
                    )
                    truncated_sections.append(truncated_section)
                break

        result = "\n\n".join(truncated_sections)

        # If still too long, apply aggressive truncation
        if len(result) > max_length:
            result = result[: max_length - 3] + "..."

        return result

    def _truncate_section(self, section: str, max_length: int) -> str:
        """Truncate a section while preserving meaning"""

        if len(section) <= max_length:
            return section

        # Try to keep the header and first few lines
        lines = section.split("\n")
        if len(lines) == 1:
            return section[: max_length - 3] + "..."

        header = lines[0]
        content_lines = lines[1:]

        # Keep header and as many content lines as possible
        available_length = max_length - len(header) - 3  # -3 for "..." and newlines

        truncated_lines = [header]
        current_length = 0

        for line in content_lines:
            if current_length + len(line) + 1 <= available_length:
                truncated_lines.append(line)
                current_length += len(line) + 1
            else:
                break

        if truncated_lines != [header]:
            truncated_lines.append("...")

        return "\n".join(truncated_lines)

    def get_context_stats(self, context: str) -> Dict[str, Any]:
        """Get statistics about the generated context"""

        return {
            "length": len(context),
            "lines": len(context.split("\n")),
            "sections": len(context.split("\n\n")),
            # Avoid division by zero
            "efficiency": len(context) / max(len(context), 1),
            "compression_ratio": 1.0,  # Placeholder for future compression metrics
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def create_temporal_context(timestamp: Optional[datetime] = None) -> TemporalContext:
    """Create temporal context from current time or specified timestamp"""
    if timestamp is None:
        timestamp = datetime.now()

    return TemporalContext(
        timestamp=timestamp,
        time_of_day=timestamp.time(),
        day_of_week=timestamp.weekday(),
        day_of_month=timestamp.day,
        month=timestamp.month,
        season=_get_season(timestamp.month),
        is_weekend=timestamp.weekday() >= 5,
        timezone="UTC",  # Default to UTC
    )


def _get_season(month: int) -> str:
    """Get season based on month"""
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"


def get_context_manager(config: Optional[LTMConfig] = None) -> ContextOptimizationManager:
    """Get context optimization manager with configuration"""
    return ContextOptimizationManager(config)
