"""
Context Quality Validator for intelligent context filtering.

This module provides centralized quality validation for context injection,
ensuring only relevant, high-quality context reaches the LLM.

Features:
- Relevance threshold validation for all context types
- Integration with existing LTM and RAG quality mechanisms
- Intelligent filtering based on content quality and relevance
- Fallback mechanisms for low-quality context scenarios
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..config.logging_config import get_logger
from ..types.state import StateConfig

logger = get_logger("context_quality_validator")


class ContextQualityValidator:
    """
    Centralized context quality validation for preventing irrelevant context injection.

    This class integrates existing quality mechanisms (LTM relevance scoring,
    quality monitoring) and adds missing quality validation for RAG context
    and overall context injection.
    """

    def __init__(self, config: StateConfig):
        """
        Initialize the context quality validator.

        Args:
            config: State configuration containing quality thresholds
        """
        self.config = config

        # Quality thresholds (configurable)
        self.min_relevance_threshold = 0.6  # Minimum relevance score (0.0-1.0)
        self.min_ltm_threshold = 0.1  # LTM relevance threshold (existing)
        self.min_rag_threshold = 0.5  # RAG relevance threshold (new)
        self.min_conversation_threshold = 0.4  # Conversation relevance threshold

        # Content quality thresholds
        self.min_content_length = 10  # Minimum content length
        self.max_content_length = 2000  # Maximum content length

        # Context type weights for scoring
        self.context_type_weights = {
            "ltm": 1.0,  # Long-term memory (highest priority)
            "rag": 0.8,  # RAG documents (high priority)
            "conversation": 0.7,  # Conversation history (medium priority)
            "focus": 0.9,  # Focus areas (very high priority)
            "system": 0.5,  # System messages (lower priority)
            "tool": 0.6,  # Tool results (medium priority)
            "memory": 0.7,  # General memory (medium priority)
        }

        logger.info(
            f"🔍 ContextQualityValidator initialized with relevance threshold: {self.min_relevance_threshold}"
        )

    def validate_context_relevance(
        self, context_items: List[dict], user_input: str, context_type: str = "mixed"
    ) -> List[dict]:
        """
        Filter context items based on relevance threshold.

        Args:
            context_items: List of context items to validate
            user_input: Current user input for relevance calculation
            context_type: Type of context being validated ("ltm", "rag", "conversation", "mixed")

        Returns:
            List of context items that meet quality thresholds
        """
        if not context_items:
            logger.debug("No context items to validate")
            return []

        if not user_input or not user_input.strip():
            logger.warning("Empty user input provided for context validation")
            return context_items  # Return all items if no user input to compare against

        logger.info(
            f"🔍 Validating {len(context_items)} context items for relevance (type: {context_type})"
        )

        # Calculate quality scores for all items
        scored_items = []
        for item in context_items:
            quality_score = self.calculate_context_quality_score(
                item, user_input, context_type
            )
            scored_items.append((quality_score, item))

        # Sort by quality score (highest first)
        scored_items.sort(key=lambda x: x[0], reverse=True)

        # Filter by relevance threshold
        threshold = self._get_threshold_for_context_type(context_type)
        filtered_items = [item for score, item in scored_items if score >= threshold]

        # Log validation results
        removed_count = len(context_items) - len(filtered_items)
        logger.info(
            f"✅ Context validation complete: {len(filtered_items)}/{len(context_items)} items passed "
            f"quality threshold {threshold:.2f} (removed {removed_count} low-quality items)"
        )

        # Log details about removed items for debugging
        if removed_count > 0:
            removed_items = [
                (score, item) for score, item in scored_items if score < threshold
            ]
            for score, item in removed_items[:3]:  # Log first 3 removed items
                content = item.get("content", "")
                content_preview = str(content)[:100] if content else "None"
                logger.debug(
                    f"❌ Removed low-quality context: {content_preview}... (score: {score:.2f})"
                )

        return filtered_items

    def calculate_context_quality_score(
        self, context_item: dict, user_input: str, context_type: str = "mixed"
    ) -> float:
        """
        Calculate comprehensive quality score for a context item.

        Args:
            context_item: Context item to score
            user_input: Current user input for relevance calculation
            context_type: Type of context being scored

        Returns:
            Quality score between 0.0 and 1.0
        """
        if not context_item or not user_input:
            return 0.0

        # Base relevance score
        relevance_score = self._calculate_relevance_score(context_item, user_input)

        # Content quality score
        content_quality_score = self._calculate_content_quality_score(context_item)

        # Context type weight
        item_type = context_item.get("source", context_item.get("type", "unknown"))
        type_weight = self.context_type_weights.get(item_type.lower(), 0.5)

        # Timestamp-based freshness score
        freshness_score = self._calculate_freshness_score(context_item)

        # Combine scores with weights
        final_score = (
            relevance_score * 0.5
            + content_quality_score * 0.3  # 50% weight for relevance
            + type_weight * 0.1  # 30% weight for content quality
            + freshness_score  # 10% weight for context type
            * 0.1  # 10% weight for freshness
        )

        # Ensure score is within bounds
        return max(0.0, min(1.0, final_score))

    def filter_low_quality_context(
        self, context_items: List[dict], user_input: str, context_type: str = "mixed"
    ) -> List[dict]:
        """
        Remove context items below quality threshold.

        This is a convenience method that combines validation and filtering.

        Args:
            context_items: List of context items to filter
            user_input: Current user input for relevance calculation
            context_type: Type of context being filtered

        Returns:
            List of high-quality context items
        """
        return self.validate_context_relevance(context_items, user_input, context_type)

    def get_quality_metrics(
        self, context_items: List[dict], user_input: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive quality metrics for context items.

        Args:
            context_items: List of context items to analyze
            user_input: Current user input for relevance calculation

        Returns:
            Dictionary containing quality metrics
        """
        if not context_items:
            return {
                "total_items": 0,
                "average_quality": 0.0,
                "quality_distribution": {},
                "context_type_breakdown": {},
                "recommendations": [],
            }

        # Calculate scores for all items
        scored_items = []
        context_type_scores: dict[str, list[float]] = {}

        for item in context_items:
            score = self.calculate_context_quality_score(item, user_input)
            scored_items.append(score)

            # Track scores by context type
            item_type = item.get("source", item.get("type", "unknown"))
            if item_type not in context_type_scores:
                context_type_scores[item_type] = []
            context_type_scores[item_type].append(score)

        # Calculate metrics
        total_items = len(context_items)
        average_quality = sum(scored_items) / total_items

        # Quality distribution
        quality_distribution = {
            "excellent": len([s for s in scored_items if s >= 0.9]),
            "good": len([s for s in scored_items if 0.7 <= s < 0.9]),
            "fair": len([s for s in scored_items if 0.5 <= s < 0.7]),
            "poor": len([s for s in scored_items if s < 0.5]),
        }

        # Context type breakdown
        type_breakdown = {}
        for context_type, scores in context_type_scores.items():
            type_breakdown[context_type] = {
                "count": len(scores),
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
            }

        # Generate recommendations
        recommendations = self._generate_quality_recommendations(
            scored_items, context_type_scores, average_quality
        )

        return {
            "total_items": total_items,
            "average_quality": average_quality,
            "quality_distribution": quality_distribution,
            "context_type_breakdown": type_breakdown,
            "recommendations": recommendations,
        }

    def _calculate_relevance_score(self, context_item: dict, user_input: str) -> float:
        """
        Calculate relevance score between context item and user input.

        Args:
            context_item: Context item to score
            user_input: User input to compare against

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not context_item or not user_input:
            return 0.0

        content = str(context_item.get("content", ""))
        if not content:
            return 0.0

        # Extract keywords from user input
        input_keywords = set(re.findall(r"\b\w+\b", user_input.lower()))
        if not input_keywords:
            return 0.5  # Neutral score if no keywords

        # Extract keywords from context content
        content_keywords = set(re.findall(r"\b\w+\b", content.lower()))
        if not content_keywords:
            return 0.0

        # Calculate keyword overlap
        keyword_overlap = len(input_keywords & content_keywords)
        total_keywords = len(input_keywords)

        if total_keywords == 0:
            return 0.0

        # Base relevance from keyword overlap
        base_relevance = keyword_overlap / total_keywords

        # Boost for exact phrase matches
        if user_input.lower() in content.lower():
            base_relevance += 0.3

        # Boost for high-frequency keyword matches
        if keyword_overlap >= total_keywords * 0.7:  # 70% keyword match
            base_relevance += 0.2

        return min(1.0, base_relevance)

    def _calculate_content_quality_score(self, context_item: dict) -> float:
        """
        Calculate content quality score based on various factors.

        Args:
            context_item: Context item to score

        Returns:
            Content quality score between 0.0 and 1.0
        """
        content = str(context_item.get("content", ""))
        if not content:
            return 0.0

        score = 1.0

        # Length-based scoring
        content_length = len(content)
        if content_length < self.min_content_length:
            score *= 0.5  # Penalty for very short content
        elif content_length > self.max_content_length:
            score *= 0.8  # Penalty for very long content

        # Content structure scoring
        if content.strip() == content:  # No leading/trailing whitespace
            score += 0.1

        # Penalty for system-generated content that might be less useful
        if context_item.get("role") == "system":
            score *= 0.8

        # Penalty for empty or placeholder content
        if content.lower() in ["", "none", "null", "undefined"]:
            score *= 0.1

        return min(1.0, score)

    def _calculate_freshness_score(self, context_item: dict) -> float:
        """
        Calculate freshness score based on timestamp.

        Args:
            context_item: Context item to score

        Returns:
            Freshness score between 0.0 and 1.0
        """
        timestamp = context_item.get("timestamp")
        if not timestamp:
            return 0.5  # Neutral score if no timestamp

        try:
            # Parse timestamp
            if isinstance(timestamp, str):
                if timestamp.endswith("Z"):
                    timestamp = timestamp[:-1] + "+00:00"
                item_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                item_time = timestamp

            # Calculate age in hours
            now = datetime.now(timezone.utc)
            age_hours = (now - item_time).total_seconds() / 3600

            # Freshness scoring (decay over time)
            if age_hours <= 1:
                return 1.0  # Very fresh (last hour)
            elif age_hours <= 24:
                return 0.9  # Fresh (last day)
            elif age_hours <= 168:  # 1 week
                return 0.7  # Recent
            elif age_hours <= 720:  # 1 month
                return 0.5  # Somewhat recent
            else:
                return 0.3  # Old

        except Exception as e:
            logger.warning(f"Error calculating freshness score: {e}")
            return 0.5  # Neutral score on error

    def _get_threshold_for_context_type(self, context_type: str) -> float:
        """
        Get appropriate quality threshold for context type.

        Args:
            context_type: Type of context being validated

        Returns:
            Quality threshold for the context type
        """
        thresholds = {
            "ltm": self.min_ltm_threshold,
            "rag": self.min_rag_threshold,
            "conversation": self.min_conversation_threshold,
            "mixed": self.min_relevance_threshold,
        }

        return thresholds.get(context_type.lower(), self.min_relevance_threshold)

    def _generate_quality_recommendations(
        self,
        scores: List[float],
        context_type_scores: Dict[str, List[float]],
        average_quality: float,
    ) -> List[str]:
        """
        Generate recommendations for improving context quality.

        Args:
            scores: List of all quality scores
            context_type_scores: Scores broken down by context type
            average_quality: Overall average quality score

        Returns:
            List of improvement recommendations
        """
        recommendations = []

        # Overall quality recommendations
        if average_quality < 0.5:
            recommendations.append(
                "Overall context quality is poor. Consider improving LTM and RAG retrieval."
            )
        elif average_quality < 0.7:
            recommendations.append(
                "Context quality could be improved. Review relevance thresholds."
            )

        # Context type specific recommendations
        for context_type, type_scores in context_type_scores.items():
            type_avg = sum(type_scores) / len(type_scores)
            if type_avg < 0.5:
                recommendations.append(
                    f"Low quality {context_type} context. Review {context_type} retrieval logic."
                )

        # Threshold recommendations
        if len([s for s in scores if s < 0.3]) > len(scores) * 0.5:
            recommendations.append(
                "Many context items have very low quality. Consider lowering relevance thresholds."
            )

        if not recommendations:
            recommendations.append(
                "Context quality is good. No immediate improvements needed."
            )

        return recommendations

    def update_thresholds(self, **kwargs):
        """
        Update quality thresholds dynamically.

        Args:
            **kwargs: Threshold values to update
        """
        valid_thresholds = [
            "min_relevance_threshold",
            "min_ltm_threshold",
            "min_rag_threshold",
            "min_conversation_threshold",
        ]

        for key, value in kwargs.items():
            if key in valid_thresholds and isinstance(value, (int, float)):
                if 0.0 <= value <= 1.0:
                    setattr(self, key, value)
                    logger.info(f"🔧 Updated {key} to {value}")
                else:
                    logger.warning(
                        f"Invalid threshold value for {key}: {value} (must be 0.0-1.0)"
                    )
            else:
                logger.warning(f"Invalid threshold key: {key}")

    def get_current_thresholds(self) -> Dict[str, float]:
        """
        Get current quality thresholds.

        Returns:
            Dictionary of current threshold values
        """
        return {
            "min_relevance_threshold": self.min_relevance_threshold,
            "min_ltm_threshold": self.min_ltm_threshold,
            "min_rag_threshold": self.min_rag_threshold,
            "min_conversation_threshold": self.min_conversation_threshold,
        }
