"""
Phase 2 State Management Features

This module implements advanced state management features for Phase 2:
- Semantic similarity detection for deduplication
- Advanced context scoring with ML-based relevance
- Hierarchical summarization for complex conversations
- Adaptive context windows based on conversation complexity

📁 types/state_phase2.py
Advanced state management features for Phase 2 of state explosion fix.
"""

import hashlib
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SemanticSimilarityConfig:
    """Configuration for semantic similarity detection"""
    similarity_threshold: float = 0.85  # Threshold for considering items similar
    min_content_length: int = 10  # Minimum content length for similarity check
    enable_semantic_deduplication: bool = True
    enable_content_normalization: bool = True
    max_similarity_cache_size: int = 1000


@dataclass
class AdvancedScoringConfig:
    """Configuration for advanced context scoring"""
    enable_ml_scoring: bool = True
    enable_semantic_scoring: bool = True
    enable_complexity_scoring: bool = True
    enable_importance_scoring: bool = True
    scoring_weights: Dict[str, float] = field(default_factory=lambda: {
        "relevance": 0.3,
        "recency": 0.2,
        "complexity": 0.2,
        "importance": 0.15,
        "semantic": 0.15
    })


@dataclass
class HierarchicalSummarizationConfig:
    """Configuration for hierarchical summarization"""
    enable_hierarchical_summarization: bool = True
    max_summary_levels: int = 3
    summary_compression_ratio: float = 0.7  # Target compression ratio
    enable_topic_clustering: bool = True
    min_cluster_size: int = 3


@dataclass
class AdaptiveContextConfig:
    """Configuration for adaptive context windows"""
    enable_adaptive_windows: bool = True
    base_context_size: int = 10
    max_context_size: int = 50
    complexity_threshold: float = 0.6
    enable_dynamic_sizing: bool = True


class SemanticSimilarityDetector:
    """Detects semantic similarity between context items for deduplication"""

    def __init__(self, config: SemanticSimilarityConfig):
        self.config = config
        self.similarity_cache: Dict[str, Set[str]] = {}
        self.content_hashes: Dict[str, str] = {}

    def normalize_content(self, content: str) -> str:
        """Normalize content for similarity comparison"""
        if not self.config.enable_content_normalization:
            return content

        # Remove extra whitespace and normalize
        normalized = re.sub(r'\s+', ' ', content.strip().lower())

        # Remove common stop words (basic implementation)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but',
                      'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = normalized.split()
        filtered_words = [word for word in words if word not in stop_words]

        return ' '.join(filtered_words)

    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash of normalized content"""
        normalized = self.normalize_content(content)
        return hashlib.md5(normalized.encode()).hexdigest()

    def calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        if len(content1) < self.config.min_content_length or len(content2) < self.config.min_content_length:
            return 0.0

        # Simple Jaccard similarity implementation
        # In a production system, this would use more sophisticated NLP techniques
        words1 = set(self.normalize_content(content1).split())
        words2 = set(self.normalize_content(content2).split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def find_similar_items(self, items: List[Dict[str, Any]]) -> List[Tuple[int, int, float]]:
        """Find pairs of similar items in the list"""
        similar_pairs = []

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                content1 = items[i].get('content', '')
                content2 = items[j].get('content', '')

                similarity = self.calculate_similarity(content1, content2)

                if similarity >= self.config.similarity_threshold:
                    similar_pairs.append((i, j, similarity))

        return similar_pairs

    def deduplicate_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate items based on semantic similarity"""
        if not self.config.enable_semantic_deduplication:
            return items

        if len(items) <= 1:
            return items

        # Find similar pairs
        similar_pairs = self.find_similar_items(items)

        if not similar_pairs:
            return items

        # Sort by similarity score (highest first)
        similar_pairs.sort(key=lambda x: x[2], reverse=True)

        # Track items to remove
        items_to_remove = set()

        for i, j, similarity in similar_pairs:
            if i not in items_to_remove and j not in items_to_remove:
                # Keep the item with higher relevance score, remove the other
                score_i = self._calculate_item_score(items[i])
                score_j = self._calculate_item_score(items[j])

                if score_i >= score_j:
                    items_to_remove.add(j)
                else:
                    items_to_remove.add(i)

        # Remove duplicate items
        deduplicated = [item for idx, item in enumerate(
            items) if idx not in items_to_remove]

        logger.debug(
            f"Deduplicated {len(items)} items to {len(deduplicated)} items")
        return deduplicated

    def _calculate_item_score(self, item: Dict[str, Any]) -> float:
        """Calculate a simple score for an item based on its properties"""
        score = 0.0

        # Score based on role
        role_scores = {
            'user': 1.0,
            'assistant': 0.8,
            'tool': 0.6,
            'memory': 0.7,
            'system': 0.5,
            'rag': 0.6,
            'ltm': 0.7
        }

        role = item.get('role', 'unknown')
        score += role_scores.get(role, 0.5)

        # Score based on content length (longer content might be more important)
        content = item.get('content', '')
        if len(content) > 50:
            score += 0.1

        return score


class AdvancedContextScorer:
    """Advanced context scoring with multiple scoring dimensions"""

    def __init__(self, config: AdvancedScoringConfig):
        self.config = config

    def calculate_advanced_score(self, item: Dict[str, Any], position: int, user_input: str = "") -> float:
        """Calculate advanced score using multiple dimensions"""
        scores = {}

        # Relevance scoring
        if self.config.enable_ml_scoring:
            scores['relevance'] = self._calculate_relevance_score(
                item, user_input)

        # Recency scoring
        scores['recency'] = self._calculate_recency_score(position)

        # Complexity scoring
        if self.config.enable_complexity_scoring:
            scores['complexity'] = self._calculate_complexity_score(item)

        # Importance scoring
        if self.config.enable_importance_scoring:
            scores['importance'] = self._calculate_importance_score(item)

        # Semantic scoring
        if self.config.enable_semantic_scoring:
            scores['semantic'] = self._calculate_semantic_score(
                item, user_input)

        # Combine scores using weights
        final_score = 0.0
        for dimension, score in scores.items():
            weight = self.config.scoring_weights.get(dimension, 0.0)
            final_score += weight * score

        return final_score

    def _calculate_relevance_score(self, item: Dict[str, Any], user_input: str) -> float:
        """Calculate relevance score based on content matching"""
        content = item.get('content', '').lower()
        user_input_lower = user_input.lower()

        if not user_input_lower or not content:
            return 0.5

        # Simple keyword matching
        user_words = set(user_input_lower.split())
        content_words = set(content.split())

        if not user_words:
            return 0.5

        intersection = len(user_words.intersection(content_words))
        relevance = intersection / len(user_words)

        return min(relevance, 1.0)

    def _calculate_recency_score(self, position: int) -> float:
        """Calculate recency score based on position"""
        return 1.0 / (position + 1)

    def _calculate_complexity_score(self, item: Dict[str, Any]) -> float:
        """Calculate complexity score based on content complexity"""
        content = item.get('content', '')

        if not content:
            return 0.5

        # Simple complexity metrics
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Complexity increases with longer sentences and more words
        complexity = min((avg_sentence_length / 20.0) +
                         (word_count / 100.0), 1.0)

        return complexity

    def _calculate_importance_score(self, item: Dict[str, Any]) -> float:
        """Calculate importance score based on content indicators"""
        content = item.get('content', '').lower()
        role = item.get('role', '')

        importance = 0.5  # Base importance

        # Role-based importance
        role_importance = {
            'user': 1.0,
            'assistant': 0.8,
            'tool': 0.6,
            'memory': 0.7,
            'system': 0.5,
            'rag': 0.6,
            'ltm': 0.7
        }
        importance += role_importance.get(role, 0.5) * 0.3

        # Content-based importance indicators
        importance_keywords = [
            'important', 'critical', 'urgent', 'priority', 'essential',
            'delete', 'schedule', 'meeting', 'email', 'calendar'
        ]

        for keyword in importance_keywords:
            if keyword in content:
                importance += 0.2
                break

        return min(importance, 1.0)

    def _calculate_semantic_score(self, item: Dict[str, Any], user_input: str) -> float:
        """Calculate semantic score based on semantic similarity to user input"""
        if not user_input:
            return 0.5

        content = item.get('content', '')

        # Simple semantic scoring using word overlap
        user_words = set(user_input.lower().split())
        content_words = set(content.lower().split())

        if not user_words or not content_words:
            return 0.5

        intersection = len(user_words.intersection(content_words))
        union = len(user_words.union(content_words))

        return intersection / union if union > 0 else 0.5


class HierarchicalSummarizer:
    """Creates hierarchical summaries for complex conversations"""

    def __init__(self, config: HierarchicalSummarizationConfig):
        self.config = config

    def create_hierarchical_summary(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a hierarchical summary of conversation items"""
        if not self.config.enable_hierarchical_summarization:
            return self._create_simple_summary(items)

        if len(items) <= self.config.min_cluster_size:
            return self._create_simple_summary(items)

        # Group items by topics
        topic_clusters = self._cluster_by_topics(items)

        # Create summaries for each cluster
        cluster_summaries = []
        for topic, cluster_items in topic_clusters.items():
            cluster_summary = self._create_cluster_summary(
                topic, cluster_items)
            cluster_summaries.append(cluster_summary)

        # Create hierarchical summary
        hierarchical_summary = {
            "role": "system",
            "content": self._create_hierarchical_content(cluster_summaries),
            "type": "hierarchical_summary",
            "clusters": len(topic_clusters),
            "total_items": len(items)
        }

        return hierarchical_summary

    def _cluster_by_topics(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Cluster items by detected topics"""
        if not self.config.enable_topic_clustering:
            return {"general": items}

        # Simple topic clustering based on keywords
        topic_keywords = {
            "email": ["email", "mail", "inbox", "send", "delete"],
            "calendar": ["calendar", "schedule", "meeting", "event", "appointment"],
            "tasks": ["task", "todo", "reminder", "deadline", "project"],
            "search": ["search", "find", "look", "query", "information"]
        }

        clusters = defaultdict(list)

        for item in items:
            content = item.get('content', '').lower()
            assigned_topic = "general"

            for topic, keywords in topic_keywords.items():
                if any(keyword in content for keyword in keywords):
                    assigned_topic = topic
                    break

            clusters[assigned_topic].append(item)

        return dict(clusters)

    def _create_cluster_summary(self, topic: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary for a topic cluster"""
        user_messages = [item for item in items if item.get('role') == 'user']
        assistant_messages = [
            item for item in items if item.get('role') == 'assistant']
        tool_calls = [item for item in items if item.get('role') == 'tool']

        summary_content = f"Topic '{topic}': {len(user_messages)} user messages, {len(assistant_messages)} responses, {len(tool_calls)} tool calls"

        return {
            "topic": topic,
            "summary": summary_content,
            "item_count": len(items),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "tool_calls": len(tool_calls)
        }

    def _create_hierarchical_content(self, cluster_summaries: List[Dict[str, Any]]) -> str:
        """Create hierarchical content from cluster summaries"""
        if not cluster_summaries:
            return "No conversation history available."

        content_parts = ["Hierarchical conversation summary:"]

        for cluster_summary in cluster_summaries:
            content_parts.append(f"- {cluster_summary['summary']}")

        return " ".join(content_parts)

    def _create_simple_summary(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a simple summary when hierarchical summarization is disabled"""
        user_messages = [item for item in items if item.get('role') == 'user']
        assistant_messages = [
            item for item in items if item.get('role') == 'assistant']
        tool_calls = [item for item in items if item.get('role') == 'tool']

        summary_content = f"Previous conversation: {len(user_messages)} user messages, {len(assistant_messages)} assistant responses, {len(tool_calls)} tool calls"

        return {
            "role": "system",
            "content": summary_content,
            "type": "conversation_summary"
        }


class AdaptiveContextManager:
    """Manages adaptive context windows based on conversation complexity"""

    def __init__(self, config: AdaptiveContextConfig):
        self.config = config

    def calculate_adaptive_context_size(self, items: List[Dict[str, Any]], user_input: str = "") -> int:
        """Calculate adaptive context size based on conversation complexity"""
        if not self.config.enable_adaptive_windows:
            return self.config.base_context_size

        complexity_score = self._calculate_conversation_complexity(
            items, user_input)

        # Adjust context size based on complexity
        if complexity_score > self.config.complexity_threshold:
            # High complexity - use larger context
            adaptive_size = min(
                int(self.config.base_context_size * (1 + complexity_score)),
                self.config.max_context_size
            )
        else:
            # Low complexity - use smaller context
            adaptive_size = max(
                int(self.config.base_context_size * complexity_score),
                1
            )

        return adaptive_size

    def _calculate_conversation_complexity(self, items: List[Dict[str, Any]], user_input: str) -> float:
        """Calculate conversation complexity score"""
        if not items:
            return 0.5

        complexity_factors = []

        # Factor 1: Number of items
        item_count_factor = min(len(items) / 20.0, 1.0)
        complexity_factors.append(item_count_factor)

        # Factor 2: Content complexity
        total_content_length = sum(
            len(item.get('content', '')) for item in items)
        content_complexity = min(total_content_length / 1000.0, 1.0)
        complexity_factors.append(content_complexity)

        # Factor 3: Tool usage complexity
        tool_calls = [item for item in items if item.get('role') == 'tool']
        tool_complexity = min(len(tool_calls) / 5.0, 1.0)
        complexity_factors.append(tool_complexity)

        # Factor 4: User input complexity
        user_complexity = min(len(user_input) / 100.0,
                              1.0) if user_input else 0.5
        complexity_factors.append(user_complexity)

        # Average complexity factors
        avg_complexity = sum(complexity_factors) / len(complexity_factors)

        return avg_complexity

    def get_adaptive_context(self, items: List[Dict[str, Any]], user_input: str = "") -> List[Dict[str, Any]]:
        """Get context items with adaptive sizing"""
        if not self.config.enable_dynamic_sizing:
            return items[-self.config.base_context_size:] if len(items) > self.config.base_context_size else items

        adaptive_size = self.calculate_adaptive_context_size(items, user_input)

        return items[-adaptive_size:] if len(items) > adaptive_size else items
