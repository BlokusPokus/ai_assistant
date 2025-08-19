"""
Consolidated Context Management Module

This module combines context optimization and context data structures
into a single, manageable interface for LTM context management.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Dict, Optional, Any, Union
from enum import Enum

from ...config.logging_config import get_logger
from .config import LTMConfig

logger = get_logger("context_management")


# ============================================================================
# CONTEXT DATA STRUCTURES
# ============================================================================

class ContextType(Enum):
    """Types of context information"""
    TEMPORAL = "temporal"           # Time-based context
    SPATIAL = "spatial"             # Location-based context
    SOCIAL = "social"               # People and relationships
    ENVIRONMENTAL = "environmental"  # Environmental factors
    EMOTIONAL = "emotional"         # Emotional state
    COGNITIVE = "cognitive"         # Mental state and focus
    TECHNICAL = "technical"         # Technical context
    CUSTOM = "custom"               # Custom context types


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
            "timezone": self.timezone
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporalContext':
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            time_of_day=time.fromisoformat(
                data["time_of_day"]) if data.get("time_of_day") else None,
            day_of_week=data.get("day_of_week"),
            day_of_month=data.get("day_of_month"),
            month=data.get("month"),
            season=data.get("season"),
            is_weekend=data.get("is_weekend"),
            is_holiday=data.get("is_holiday"),
            timezone=data.get("timezone")
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
            "timezone": self.timezone
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpatialContext':
        """Create from dictionary"""
        return cls(
            location=data.get("location"),
            coordinates=data.get("coordinates"),
            venue=data.get("venue"),
            city=data.get("city"),
            country=data.get("country"),
            timezone=data.get("timezone")
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
            "mood": self.mood
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialContext':
        """Create from dictionary"""
        return cls(
            people_present=data.get("people_present", []),
            relationships=data.get("relationships", {}),
            group_size=data.get("group_size"),
            interaction_type=data.get("interaction_type"),
            mood=data.get("mood")
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
            "platform": self.platform
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentalContext':
        """Create from dictionary"""
        return cls(
            weather=data.get("weather"),
            temperature=data.get("temperature"),
            lighting=data.get("lighting"),
            noise_level=data.get("noise_level"),
            device_type=data.get("device_type"),
            platform=data.get("platform")
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
            "environmental": self.environmental.to_dict() if self.environmental else None,
            "custom": self.custom
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryContext':
        """Create from dictionary"""
        return cls(
            temporal=TemporalContext.from_dict(
                data["temporal"]) if data.get("temporal") else None,
            spatial=SpatialContext.from_dict(
                data["spatial"]) if data.get("spatial") else None,
            social=SocialContext.from_dict(
                data["social"]) if data.get("social") else None,
            environmental=EnvironmentalContext.from_dict(
                data["environmental"]) if data.get("environmental") else None,
            custom=data.get("custom", {})
        )


# ============================================================================
# CONTEXT OPTIMIZATION
# ============================================================================

class ContextOptimizationManager:
    """Optimizes LTM context for injection into agent"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()

    async def optimize_ltm_context(self, memories: List[dict], user_input: str, max_length: int = None) -> str:
        """Optimize LTM context for injection"""

        if not memories:
            return ""

        if max_length is None:
            max_length = self.config.max_context_length

        # Step 1: Prioritize memories by relevance and importance
        prioritized_memories = self._prioritize_memories(memories, user_input)

        # Step 2: Format memories efficiently
        formatted_context = self._format_memories_efficiently(
            prioritized_memories)

        # Step 3: Truncate if too long
        if len(formatted_context) > max_length:
            formatted_context = self._truncate_context(
                formatted_context, max_length)

        logger.info(
            f"Optimized context: {len(formatted_context)} chars from {len(memories)} memories")
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
        recency_boost = self._calculate_recency_boost(
            memory.get("last_accessed"))

        # Type-specific boost
        type_boost = self._calculate_type_boost(memory.get("type", "general"))

        total_score = base_score + relevance_boost + recency_boost + type_boost
        return min(1.0, total_score)

    def _calculate_relevance_boost(self, memory: dict, user_input: str) -> float:
        """Calculate relevance boost for memory"""

        memory_tags = set(memory.get("tags", []))
        context_words = set(user_input.lower().split())

        # Check tag overlap
        tag_matches = sum(
            1 for tag in memory_tags if tag.lower() in context_words)
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
        except:
            return 0.0

    def _calculate_type_boost(self, memory_type: str) -> float:
        """Calculate type-specific boost for memory"""

        type_boosts = {
            "preference": 0.3,
            "insight": 0.2,
            "pattern": 0.2,
            "fact": 0.1,
            "goal": 0.3,
            "habit": 0.2,
            "routine": 0.1,
            "relationship": 0.3,
            "skill": 0.2,
            "knowledge": 0.1
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
        sentences = context.split('. ')
        truncated = ""

        for sentence in sentences:
            if len(truncated + sentence + '. ') <= max_length:
                truncated += sentence + '. '
            else:
                break

        if not truncated:
            # Fallback: truncate at word boundaries
            words = context.split()
            truncated = ""
            for word in words:
                if len(truncated + word + ' ') <= max_length:
                    truncated += word + ' '
                else:
                    break

        return truncated.strip()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_temporal_context(timestamp: datetime = None) -> TemporalContext:
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
        timezone="UTC"  # Default to UTC
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


def get_context_manager(config: LTMConfig = None) -> ContextOptimizationManager:
    """Get context optimization manager with configuration"""
    return ContextOptimizationManager(config)
