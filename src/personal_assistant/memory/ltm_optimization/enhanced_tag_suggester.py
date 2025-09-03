"""
Enhanced Tag Suggestion System

This module provides intelligent tag suggestions for LTM memories based on content analysis,
semantic similarity, and user behavior patterns.
"""

import re
from typing import Dict, List, Tuple

from ...config.logging_config import get_logger
from ...constants.tags import LTM_TAGS
from .config import LTMConfig

logger = get_logger("enhanced_tag_suggester")


class EnhancedTagSuggester:
    """Enhanced tag suggestion system with semantic analysis and pattern recognition"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()
        self._tag_patterns = self._build_tag_patterns()
        self._semantic_mappings = self._build_semantic_mappings()

    def suggest_tags_for_content(
        self,
        content: str,
        memory_type: str = None,
        category: str = None,
        existing_tags: List[str] = None,
        user_context: str = None,
    ) -> Tuple[List[str], float]:
        """
        Suggest tags for content with confidence scoring.

        Args:
            content: The content to analyze
            memory_type: Type of memory being created
            category: Category of the memory
            existing_tags: Tags already assigned
            user_context: Additional user context

        Returns:
            Tuple of (suggested_tags, confidence_score)
        """
        try:
            logger.info(f"Suggesting tags for content: {content[:100]}...")

            # Initialize suggestions
            suggested_tags = []
            confidence_scores = []

            # 1. Content-based tag suggestions
            content_tags, content_confidence = self._suggest_tags_from_content(content)
            suggested_tags.extend(content_tags)
            confidence_scores.extend([content_confidence] * len(content_tags))

            # 2. Memory type-based suggestions
            if memory_type:
                type_tags, type_confidence = self._suggest_tags_by_memory_type(
                    memory_type
                )
                suggested_tags.extend(type_tags)
                confidence_scores.extend([type_confidence] * len(type_tags))

            # 3. Category-based suggestions
            if category:
                category_tags, category_confidence = self._suggest_tags_by_category(
                    category
                )
                suggested_tags.extend(category_tags)
                confidence_scores.extend([category_confidence] * len(category_tags))

            # 4. Context-based suggestions
            if user_context:
                context_tags, context_confidence = self._suggest_tags_from_context(
                    user_context
                )
                suggested_tags.extend(context_tags)
                confidence_scores.extend([context_confidence] * len(context_tags))

            # 5. Pattern-based suggestions
            pattern_tags, pattern_confidence = self._suggest_tags_by_patterns(content)
            suggested_tags.extend(pattern_tags)
            confidence_scores.extend([pattern_confidence] * len(pattern_tags))

            # Remove duplicates while preserving order
            unique_tags = []
            unique_confidences = []
            seen_tags = set()

            for tag, confidence in zip(suggested_tags, confidence_scores):
                if tag not in seen_tags and tag in LTM_TAGS:
                    unique_tags.append(tag)
                    unique_confidences.append(confidence)
                    seen_tags.add(tag)

            # Limit to maximum suggested tags
            max_tags = self.config.max_suggested_tags_per_memory
            if len(unique_tags) > max_tags:
                # Sort by confidence and take top tags
                tag_confidence_pairs = list(zip(unique_tags, unique_confidences))
                tag_confidence_pairs.sort(key=lambda x: x[1], reverse=True)
                unique_tags = [tag for tag, _ in tag_confidence_pairs[:max_tags]]
                unique_confidences = [
                    conf for _, conf in tag_confidence_pairs[:max_tags]
                ]

            # Calculate overall confidence
            overall_confidence = (
                sum(unique_confidences) / len(unique_confidences)
                if unique_confidences
                else 0.0
            )

            # Add fallback tags if confidence is too low
            if overall_confidence < self.config.tag_suggestion_confidence_threshold:
                fallback_tags = self.config.tag_suggestion_fallback_tags[:2]
                unique_tags.extend(fallback_tags)
                logger.info(
                    f"Added fallback tags due to low confidence: {fallback_tags}"
                )

            logger.info(
                f"Suggested {len(unique_tags)} tags with confidence {overall_confidence:.2f}"
            )
            return unique_tags, overall_confidence

        except Exception as e:
            logger.error(f"Error suggesting tags: {e}")
            # Return safe fallback tags
            fallback_tags = self.config.tag_suggestion_fallback_tags[:3]
            return fallback_tags, 0.5

    def _suggest_tags_from_content(self, content: str) -> Tuple[List[str], float]:
        """Suggest tags based on content analysis"""

        content_lower = content.lower()
        suggested_tags = []

        # Topic-based suggestions
        topic_keywords = {
            "work": [
                "work",
                "project",
                "meeting",
                "deadline",
                "office",
                "job",
                "career",
            ],
            "health": ["health", "exercise", "diet", "wellness", "fitness", "medical"],
            "personal": ["personal", "family", "home", "life", "private"],
            "finance": ["finance", "money", "budget", "expense", "investment"],
            "education": ["education", "learning", "course", "study", "knowledge"],
            "entertainment": ["entertainment", "movie", "music", "game", "hobby"],
            "travel": ["travel", "trip", "vacation", "hotel", "flight"],
            "shopping": ["shopping", "purchase", "buy", "order", "delivery"],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                suggested_tags.append(topic)

        # Behavior-based suggestions
        if any(
            word in content_lower
            for word in ["prefer", "like", "want", "need", "favorite"]
        ):
            suggested_tags.append("preference")

        if any(
            word in content_lower
            for word in ["always", "usually", "typically", "habit", "routine"]
        ):
            suggested_tags.append("habit")
            suggested_tags.append("pattern")

        if any(
            word in content_lower
            for word in ["learn", "understand", "figure out", "discover"]
        ):
            suggested_tags.append("learning")

        # Communication-based suggestions
        if any(
            word in content_lower
            for word in ["explain", "tell me more", "detailed", "conversation"]
        ):
            suggested_tags.append("conversation")

        # Priority-based suggestions
        if any(word in content_lower for word in ["important", "urgent", "critical"]):
            suggested_tags.append("important")
            suggested_tags.append("urgent")

        # Calculate confidence based on keyword matches
        total_keywords = sum(len(keywords) for keywords in topic_keywords.values())
        matched_keywords = sum(
            1
            for keywords in topic_keywords.values()
            if any(keyword in content_lower for keyword in keywords)
        )

        confidence = min(0.9, 0.3 + (matched_keywords / total_keywords) * 0.6)

        return suggested_tags, confidence

    def _suggest_tags_by_memory_type(self, memory_type: str) -> Tuple[List[str], float]:
        """Suggest tags based on memory type"""

        type_tag_mappings = {
            "preference": ["preference", "personal", "conversation"],
            "pattern": ["pattern", "habit", "routine"],
            "habit": ["habit", "pattern", "routine"],
            "communication": ["conversation", "preference"],
            "learning": ["learning", "education"],
            "tool_usage": ["tool_execution", "user_request"],
            "interest": ["general", "conversation"],
            "general": ["general", "miscellaneous"],
        }

        suggested_tags = type_tag_mappings.get(memory_type, ["general"])
        confidence = 0.8  # High confidence for type-based suggestions

        return suggested_tags, confidence

    def _suggest_tags_by_category(self, category: str) -> Tuple[List[str], float]:
        """Suggest tags based on category"""

        category_tag_mappings = {
            "work": ["work", "project", "meeting", "deadline"],
            "personal": ["personal", "family", "home"],
            "health": ["health", "exercise", "wellness"],
            "finance": ["finance", "money", "budget"],
            "education": ["education", "learning", "course"],
            "entertainment": ["entertainment", "hobby"],
            "travel": ["travel", "trip", "vacation"],
            "general": ["general", "miscellaneous"],
        }

        suggested_tags = category_tag_mappings.get(category, ["general"])
        confidence = 0.8  # High confidence for category-based suggestions

        return suggested_tags, confidence

    def _suggest_tags_from_context(self, user_context: str) -> Tuple[List[str], float]:
        """Suggest tags based on user context"""

        context_lower = user_context.lower()
        suggested_tags = []

        # Time-based suggestions
        if any(
            word in context_lower for word in ["morning", "evening", "daily", "weekly"]
        ):
            suggested_tags.append("routine")

        # Location-based suggestions
        if any(word in context_lower for word in ["home", "office", "work", "gym"]):
            suggested_tags.append("personal" if "home" in context_lower else "work")

        # Activity-based suggestions
        if any(word in context_lower for word in ["meeting", "call", "appointment"]):
            suggested_tags.append("meeting")

        confidence = 0.7 if suggested_tags else 0.5
        return suggested_tags, confidence

    def _suggest_tags_by_patterns(self, content: str) -> Tuple[List[str], float]:
        """Suggest tags based on content patterns"""

        suggested_tags = []

        # Check for specific patterns
        patterns = {
            "email": r"\b(email|mail|inbox|send|receive)\b",
            "meeting": r"\b(meeting|appointment|call|schedule|calendar)\b",
            "project": r"\b(project|task|deadline|milestone|deliverable)\b",
            "health": r"\b(exercise|workout|diet|medication|doctor)\b",
            "finance": r"\b(budget|expense|money|cost|payment)\b",
        }

        for tag, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                suggested_tags.append(tag)

        confidence = 0.6 if suggested_tags else 0.4
        return suggested_tags, confidence

    def _build_tag_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for tag matching"""

        return {
            "communication": ["email", "meeting", "conversation", "call"],
            "action": ["create", "delete", "update", "search", "schedule"],
            "priority": ["important", "urgent", "critical", "low_priority"],
            "behavior": ["preference", "habit", "pattern", "routine"],
            "system": ["tool_execution", "user_request", "system_response"],
        }

    def _build_semantic_mappings(self) -> Dict[str, List[str]]:
        """Build semantic mappings for tag suggestions"""

        return {
            "communication_style": ["conversation", "preference", "communication"],
            "work_management": ["work", "project", "task", "deadline"],
            "health_wellness": ["health", "exercise", "wellness", "diet"],
            "personal_life": ["personal", "family", "home", "life"],
            "financial_management": ["finance", "money", "budget", "expense"],
            "learning_development": ["education", "learning", "course", "study"],
        }

    def get_tag_similarity_score(self, tags1: List[str], tags2: List[str]) -> float:
        """Calculate similarity score between two sets of tags"""

        if not tags1 or not tags2:
            return 0.0

        # Convert to sets for easier comparison
        set1 = set(tags1)
        set2 = set(tags2)

        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def suggest_related_tags(self, base_tags: List[str], limit: int = 5) -> List[str]:
        """Suggest related tags based on existing tags"""

        related_tags = []

        for base_tag in base_tags:
            # Find semantically related tags
            for semantic_group, group_tags in self._semantic_mappings.items():
                if base_tag in group_tags:
                    related_tags.extend(
                        [tag for tag in group_tags if tag not in base_tags]
                    )

        # Remove duplicates and limit results
        unique_related = list(dict.fromkeys(related_tags))  # Preserve order
        return unique_related[:limit]
