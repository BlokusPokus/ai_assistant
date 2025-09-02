"""
LTM Analytics and Insights

This module provides comprehensive analytics and insights for the LTM system,
including memory creation metrics, retrieval performance, quality assessment,
and state-LTM integration metrics.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import statistics

from ...config.logging_config import get_logger
from ...types.state import AgentState
from .config import EnhancedLTMConfig

logger = get_logger("analytics")


class LTMAnalytics:
    """
    Provides comprehensive analytics and insights for the LTM system.

    This class offers:
    - Memory creation metrics and trends
    - Retrieval performance statistics
    - Quality assessment metrics
    - Usage pattern insights
    - State-LTM integration metrics
    """

    def __init__(self, config: EnhancedLTMConfig = None):
        """Initialize the LTM analytics system"""
        self.config = config or EnhancedLTMConfig()
        self.logger = get_logger("analytics")

        # Analytics data storage
        self.memory_creation_data = defaultdict(list)
        self.retrieval_performance_data = defaultdict(list)
        self.quality_metrics_data = defaultdict(list)
        self.usage_patterns_data = defaultdict(list)
        self.state_integration_data = defaultdict(list)

        # Sampling settings
        self.sampling_rate = getattr(
            self.config, 'analytics_sampling_rate', 0.1)
        self.performance_metrics_enabled = getattr(
            self.config, 'performance_metrics_enabled', True)

    async def get_memory_creation_metrics(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get memory creation performance metrics.

        Args:
            user_id: Optional user ID for user-specific metrics

        Returns:
            Dictionary containing memory creation metrics
        """

        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'overall_metrics': {},
                'user_metrics': {},
                'trends': {},
                'recommendations': []
            }

            # Overall memory creation metrics
            overall_metrics = await self._calculate_overall_memory_metrics()
            metrics['overall_metrics'] = overall_metrics

            # User-specific metrics if requested
            if user_id:
                user_metrics = await self._calculate_user_memory_metrics(user_id)
                metrics['user_metrics'] = user_metrics

            # Memory creation trends
            trends = await self._analyze_memory_creation_trends()
            metrics['trends'] = trends

            # Generate recommendations
            recommendations = await self._generate_memory_creation_recommendations(metrics)
            metrics['recommendations'] = recommendations

            self.logger.info(
                f"Memory creation metrics generated: {len(overall_metrics)} overall metrics")

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting memory creation metrics: {e}")
            return {}

    async def get_retrieval_performance_stats(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get retrieval performance statistics.

        Args:
            user_id: Optional user ID for user-specific stats

        Returns:
            Dictionary containing retrieval performance statistics
        """

        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'overall_performance': {},
                'user_performance': {},
                'performance_trends': {},
                'optimization_opportunities': []
            }

            # Overall retrieval performance
            overall_performance = await self._calculate_overall_retrieval_performance()
            stats['overall_performance'] = overall_performance

            # User-specific performance if requested
            if user_id:
                user_performance = await self._calculate_user_retrieval_performance(user_id)
                stats['user_performance'] = user_performance

            # Performance trends
            performance_trends = await self._analyze_retrieval_performance_trends()
            stats['performance_trends'] = performance_trends

            # Optimization opportunities
            optimization_opportunities = await self._identify_retrieval_optimization_opportunities(stats)
            stats['optimization_opportunities'] = optimization_opportunities

            self.logger.info(
                f"Retrieval performance stats generated: {len(overall_performance)} performance metrics")

            return stats

        except Exception as e:
            self.logger.error(
                f"Error getting retrieval performance stats: {e}")
            return {}

    async def get_quality_assessment_metrics(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get memory quality assessment metrics.

        Args:
            user_id: Optional user ID for user-specific quality metrics

        Returns:
            Dictionary containing quality assessment metrics
        """

        try:
            quality_metrics = {
                'timestamp': datetime.now().isoformat(),
                'overall_quality': {},
                'user_quality': {},
                'quality_trends': {},
                'improvement_suggestions': []
            }

            # Overall quality metrics
            overall_quality = await self._calculate_overall_quality_metrics()
            quality_metrics['overall_quality'] = overall_quality

            # User-specific quality if requested
            if user_id:
                user_quality = await self._calculate_user_quality_metrics(user_id)
                quality_metrics['user_quality'] = user_quality

            # Quality trends
            quality_trends = await self._analyze_quality_trends()
            quality_metrics['quality_trends'] = quality_trends

            # Improvement suggestions
            improvement_suggestions = await self._generate_quality_improvement_suggestions(quality_metrics)
            quality_metrics['improvement_suggestions'] = improvement_suggestions

            self.logger.info(
                f"Quality assessment metrics generated: {len(overall_quality)} quality metrics")

            return quality_metrics

        except Exception as e:
            self.logger.error(f"Error getting quality assessment metrics: {e}")
            return {}

    async def get_usage_pattern_insights(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get usage pattern insights and analysis.

        Args:
            user_id: Optional user ID for user-specific insights

        Returns:
            Dictionary containing usage pattern insights
        """

        try:
            insights = {
                'timestamp': datetime.now().isoformat(),
                'overall_patterns': {},
                'user_patterns': {},
                'pattern_analysis': {},
                'behavioral_insights': []
            }

            # Overall usage patterns
            overall_patterns = await self._analyze_overall_usage_patterns()
            insights['overall_patterns'] = overall_patterns

            # User-specific patterns if requested
            if user_id:
                user_patterns = await self._analyze_user_usage_patterns(user_id)
                insights['user_patterns'] = user_patterns

            # Pattern analysis
            pattern_analysis = await self._perform_pattern_analysis(insights)
            insights['pattern_analysis'] = pattern_analysis

            # Behavioral insights
            behavioral_insights = await self._generate_behavioral_insights(insights)
            insights['behavioral_insights'] = behavioral_insights

            self.logger.info(
                f"Usage pattern insights generated: {len(overall_patterns)} pattern categories")

            return insights

        except Exception as e:
            self.logger.error(f"Error getting usage pattern insights: {e}")
            return {}

    async def get_state_ltm_integration_metrics(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get state-LTM integration metrics and coordination insights.

        Args:
            user_id: Optional user ID for user-specific integration metrics

        Returns:
            Dictionary containing state-LTM integration metrics
        """

        try:
            integration_metrics = {
                'timestamp': datetime.now().isoformat(),
                'integration_efficiency': {},
                'coordination_metrics': {},
                'state_ltm_synergy': {},
                'optimization_recommendations': []
            }

            # Integration efficiency metrics
            integration_efficiency = await self._calculate_integration_efficiency()
            integration_metrics['integration_efficiency'] = integration_efficiency

            # Coordination metrics
            coordination_metrics = await self._calculate_coordination_metrics()
            integration_metrics['coordination_metrics'] = coordination_metrics

            # State-LTM synergy analysis
            state_ltm_synergy = await self._analyze_state_ltm_synergy()
            integration_metrics['state_ltm_synergy'] = state_ltm_synergy

            # Optimization recommendations
            optimization_recommendations = await self._generate_integration_optimization_recommendations(integration_metrics)
            integration_metrics['optimization_recommendations'] = optimization_recommendations

            self.logger.info(
                f"State-LTM integration metrics generated: {len(integration_efficiency)} efficiency metrics")

            return integration_metrics

        except Exception as e:
            self.logger.error(
                f"Error getting state-LTM integration metrics: {e}")
            return {}

    async def record_memory_creation_event(
        self,
        user_id: int,
        memory_data: Dict[str, Any],
        creation_time: float = None
    ):
        """Record a memory creation event for analytics"""

        try:
            if not self._should_sample_event():
                return

            event_data = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'memory_type': memory_data.get('memory_type', 'unknown'),
                'category': memory_data.get('category', 'unknown'),
                'importance_score': memory_data.get('importance_score', 1),
                'confidence_score': memory_data.get('confidence_score', 0.5),
                'creation_time': creation_time or 0.0,
                'tags_count': len(memory_data.get('tags', [])),
                'content_length': len(memory_data.get('content', ''))
            }

            self.memory_creation_data[user_id].append(event_data)

            # Limit data storage
            if len(self.memory_creation_data[user_id]) > 1000:
                self.memory_creation_data[user_id] = self.memory_creation_data[user_id][-500:]

        except Exception as e:
            self.logger.error(f"Error recording memory creation event: {e}")

    async def record_retrieval_event(
        self,
        user_id: int,
        query_type: str,
        retrieval_time: float,
        result_count: int,
        quality_score: float = None
    ):
        """Record a retrieval event for analytics"""

        try:
            if not self._should_sample_event():
                return

            event_data = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'query_type': query_type,
                'retrieval_time': retrieval_time,
                'result_count': result_count,
                'quality_score': quality_score or 0.0
            }

            self.retrieval_performance_data[user_id].append(event_data)

            # Limit data storage
            if len(self.retrieval_performance_data[user_id]) > 1000:
                self.retrieval_performance_data[user_id] = self.retrieval_performance_data[user_id][-500:]

        except Exception as e:
            self.logger.error(f"Error recording retrieval event: {e}")

    async def record_quality_assessment(
        self,
        user_id: int,
        memory_id: int,
        quality_score: float,
        assessment_type: str
    ):
        """Record a quality assessment for analytics"""

        try:
            if not self._should_sample_event():
                return

            event_data = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'memory_id': memory_id,
                'quality_score': quality_score,
                'assessment_type': assessment_type
            }

            self.quality_metrics_data[user_id].append(event_data)

            # Limit data storage
            if len(self.quality_metrics_data[user_id]) > 1000:
                self.quality_metrics_data[user_id] = self.quality_metrics_data[user_id][-500:]

        except Exception as e:
            self.logger.error(f"Error recording quality assessment: {e}")

    async def record_usage_pattern(
        self,
        user_id: int,
        pattern_type: str,
        pattern_data: Dict[str, Any]
    ):
        """Record a usage pattern for analytics"""

        try:
            if not self._should_sample_event():
                return

            event_data = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'pattern_type': pattern_type,
                'pattern_data': pattern_data
            }

            self.usage_patterns_data[user_id].append(event_data)

            # Limit data storage
            if len(self.usage_patterns_data[user_id]) > 1000:
                self.usage_patterns_data[user_id] = self.usage_patterns_data[user_id][-500:]

        except Exception as e:
            self.logger.error(f"Error recording usage pattern: {e}")

    async def record_state_integration_event(
        self,
        user_id: int,
        integration_type: str,
        success: bool,
        performance_metrics: Dict[str, Any] = None
    ):
        """Record a state integration event for analytics"""

        try:
            if not self._should_sample_event():
                return

            event_data = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'integration_type': integration_type,
                'success': success,
                'performance_metrics': performance_metrics or {}
            }

            self.state_integration_data[user_id].append(event_data)

            # Limit data storage
            if len(self.state_integration_data[user_id]) > 1000:
                self.state_integration_data[user_id] = self.state_integration_data[user_id][-500:]

        except Exception as e:
            self.logger.error(f"Error recording state integration event: {e}")

    def _should_sample_event(self) -> bool:
        """Determine if an event should be sampled based on sampling rate"""

        try:
            import random
            return random.random() < self.sampling_rate

        except Exception as e:
            self.logger.error(f"Error in event sampling: {e}")
            return True  # Default to recording all events

    async def _calculate_overall_memory_metrics(self) -> Dict[str, Any]:
        """Calculate overall memory creation metrics"""

        try:
            metrics = {
                'total_memories_created': 0,
                'memories_by_type': {},
                'memories_by_category': {},
                'average_importance': 0.0,
                'average_confidence': 0.0,
                'creation_rate_per_hour': 0.0
            }

            # Aggregate data from all users
            all_memories = []
            for user_memories in self.memory_creation_data.values():
                all_memories.extend(user_memories)

            if not all_memories:
                return metrics

            # Calculate basic metrics
            metrics['total_memories_created'] = len(all_memories)

            # Memories by type
            type_counts = Counter(memory['memory_type']
                                  for memory in all_memories)
            metrics['memories_by_type'] = dict(type_counts)

            # Memories by category
            category_counts = Counter(memory['category']
                                      for memory in all_memories)
            metrics['memories_by_category'] = dict(category_counts)

            # Average scores
            importance_scores = [memory['importance_score']
                                 for memory in all_memories]
            confidence_scores = [memory['confidence_score']
                                 for memory in all_memories]

            if importance_scores:
                metrics['average_importance'] = statistics.mean(
                    importance_scores)
            if confidence_scores:
                metrics['average_confidence'] = statistics.mean(
                    confidence_scores)

            # Creation rate (simplified calculation)
            if len(all_memories) > 1:
                timestamps = [datetime.fromisoformat(
                    memory['timestamp']) for memory in all_memories]
                time_span = max(timestamps) - min(timestamps)
                if time_span.total_seconds() > 0:
                    metrics['creation_rate_per_hour'] = len(
                        all_memories) / (time_span.total_seconds() / 3600)

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating overall memory metrics: {e}")
            return {}

    async def _calculate_user_memory_metrics(self, user_id: int) -> Dict[str, Any]:
        """Calculate user-specific memory creation metrics"""

        try:
            user_memories = self.memory_creation_data.get(user_id, [])

            if not user_memories:
                return {'error': 'No data available for user'}

            metrics = {
                'user_id': user_id,
                'total_memories': len(user_memories),
                'memories_by_type': {},
                'memories_by_category': {},
                'average_importance': 0.0,
                'average_confidence': 0.0,
                'recent_activity': {}
            }

            # Type and category breakdown
            type_counts = Counter(memory['memory_type']
                                  for memory in user_memories)
            metrics['memories_by_type'] = dict(type_counts)

            category_counts = Counter(memory['category']
                                      for memory in user_memories)
            metrics['memories_by_category'] = dict(category_counts)

            # Average scores
            importance_scores = [memory['importance_score']
                                 for memory in user_memories]
            confidence_scores = [memory['confidence_score']
                                 for memory in user_memories]

            if importance_scores:
                metrics['average_importance'] = statistics.mean(
                    importance_scores)
            if confidence_scores:
                metrics['average_confidence'] = statistics.mean(
                    confidence_scores)

            # Recent activity (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_memories = [
                memory for memory in user_memories
                if datetime.fromisoformat(memory['timestamp']) > recent_cutoff
            ]

            metrics['recent_activity'] = {
                'memories_last_24h': len(recent_memories),
                'active_hours': self._calculate_active_hours(recent_memories)
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating user memory metrics: {e}")
            return {'error': str(e)}

    async def _calculate_user_retrieval_performance(self, user_id: int) -> Dict[str, Any]:
        """Calculate user-specific retrieval performance metrics"""

        try:
            user_retrievals = self.retrieval_performance_data.get(user_id, [])

            if not user_retrievals:
                return {'error': 'No data available for user'}

            metrics = {
                'user_id': user_id,
                'total_retrievals': len(user_retrievals),
                'retrieval_by_type': {},
                'average_retrieval_time': 0.0,
                'quality_metrics': {},
                'recent_performance': {}
            }

            # Retrieval by type
            type_counts = Counter(retrieval['query_type']
                                  for retrieval in user_retrievals)
            metrics['retrieval_by_type'] = dict(type_counts)

            # Performance metrics
            retrieval_times = [retrieval['retrieval_time']
                               for retrieval in user_retrievals]
            if retrieval_times:
                metrics['average_retrieval_time'] = statistics.mean(
                    retrieval_times)
                metrics['performance_distribution'] = {
                    'min_time': min(retrieval_times),
                    'max_time': max(retrieval_times),
                    'p95_time': self._calculate_percentile(retrieval_times, 95)
                }

            # Quality metrics
            quality_scores = [r['quality_score']
                              for r in user_retrievals if r['quality_score'] > 0]
            if quality_scores:
                metrics['quality_metrics'] = {
                    'average_quality': statistics.mean(quality_scores),
                    'quality_distribution': {
                        'high_quality': len([q for q in quality_scores if q > 0.8]),
                        'medium_quality': len([q for q in quality_scores if 0.5 <= q <= 0.8]),
                        'low_quality': len([q for q in quality_scores if q < 0.5])
                    }
                }

            # Recent performance (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_retrievals = [
                retrieval for retrieval in user_retrievals
                if datetime.fromisoformat(retrieval['timestamp']) > recent_cutoff
            ]

            if recent_retrievals:
                recent_times = [r['retrieval_time'] for r in recent_retrievals]
                metrics['recent_performance'] = {
                    'retrievals_last_24h': len(recent_retrievals),
                    'average_time_recent': statistics.mean(recent_times)
                }

            return metrics

        except Exception as e:
            self.logger.error(
                f"Error calculating user retrieval performance: {e}")
            return {'error': str(e)}

    async def _calculate_user_quality_metrics(self, user_id: int) -> Dict[str, Any]:
        """Calculate user-specific quality assessment metrics"""

        try:
            user_assessments = self.quality_metrics_data.get(user_id, [])

            if not user_assessments:
                return {'error': 'No data available for user'}

            metrics = {
                'user_id': user_id,
                'total_assessments': len(user_assessments),
                'average_quality_score': 0.0,
                'quality_by_type': {},
                'quality_trends': {}
            }

            # Quality scores
            quality_scores = [assessment['quality_score']
                              for assessment in user_assessments]
            if quality_scores:
                metrics['average_quality_score'] = statistics.mean(
                    quality_scores)

                # Quality distribution
                metrics['quality_distribution'] = {
                    'excellent': len([q for q in quality_scores if q > 0.9]),
                    'good': len([q for q in quality_scores if 0.7 <= q <= 0.9]),
                    'fair': len([q for q in quality_scores if 0.5 <= q < 0.7]),
                    'poor': len([q for q in quality_scores if q < 0.5])
                }

            # Quality by assessment type
            type_quality = defaultdict(list)
            for assessment in user_assessments:
                type_quality[assessment['assessment_type']].append(
                    assessment['quality_score'])

            for assessment_type, scores in type_quality.items():
                metrics['quality_by_type'][assessment_type] = {
                    'count': len(scores),
                    'average_score': statistics.mean(scores)
                }

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating user quality metrics: {e}")
            return {'error': str(e)}

    async def _analyze_user_usage_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user-specific usage patterns"""

        try:
            user_patterns = self.usage_patterns_data.get(user_id, [])

            if not user_patterns:
                return {'error': 'No data available for user'}

            patterns = {
                'user_id': user_id,
                'pattern_categories': {},
                'common_patterns': {},
                'behavioral_insights': []
            }

            # Pattern categories
            pattern_types = Counter(pattern['pattern_type']
                                    for pattern in user_patterns)
            patterns['pattern_categories'] = dict(pattern_types)

            # Common patterns
            pattern_data = defaultdict(list)
            for pattern in user_patterns:
                pattern_data[pattern['pattern_type']].append(
                    pattern['pattern_data'])

            for pattern_type, data_list in pattern_data.items():
                patterns['common_patterns'][pattern_type] = self._extract_common_patterns(
                    data_list)

            return patterns

        except Exception as e:
            self.logger.error(f"Error analyzing user usage patterns: {e}")
            return {'error': str(e)}

    async def _calculate_overall_retrieval_performance(self) -> Dict[str, Any]:
        """Calculate overall retrieval performance statistics"""

        try:
            metrics = {
                'total_retrievals': 0,
                'average_retrieval_time': 0.0,
                'retrieval_by_type': {},
                'performance_distribution': {},
                'quality_metrics': {}
            }

            # Aggregate data from all users
            all_retrievals = []
            for user_retrievals in self.retrieval_performance_data.values():
                all_retrievals.extend(user_retrievals)

            if not all_retrievals:
                return metrics

            metrics['total_retrievals'] = len(all_retrievals)

            # Retrieval by type
            type_counts = Counter(retrieval['query_type']
                                  for retrieval in all_retrievals)
            metrics['retrieval_by_type'] = dict(type_counts)

            # Performance metrics
            retrieval_times = [retrieval['retrieval_time']
                               for retrieval in all_retrievals]
            if retrieval_times:
                metrics['average_retrieval_time'] = statistics.mean(
                    retrieval_times)
                metrics['performance_distribution'] = {
                    'min_time': min(retrieval_times),
                    'max_time': max(retrieval_times),
                    'p95_time': self._calculate_percentile(retrieval_times, 95),
                    'slow_queries': len([t for t in retrieval_times if t > 1.0])
                }

            # Quality metrics
            quality_scores = [r['quality_score']
                              for r in all_retrievals if r['quality_score'] > 0]
            if quality_scores:
                metrics['quality_metrics'] = {
                    'average_quality': statistics.mean(quality_scores),
                    'quality_distribution': {
                        'high_quality': len([q for q in quality_scores if q > 0.8]),
                        'medium_quality': len([q for q in quality_scores if 0.5 <= q <= 0.8]),
                        'low_quality': len([q for q in quality_scores if q < 0.5])
                    }
                }

            return metrics

        except Exception as e:
            self.logger.error(
                f"Error calculating overall retrieval performance: {e}")
            return {}

    async def _calculate_overall_quality_metrics(self) -> Dict[str, Any]:
        """Calculate overall quality assessment metrics"""

        try:
            metrics = {
                'total_assessments': 0,
                'average_quality_score': 0.0,
                'quality_by_type': {},
                'quality_trends': {},
                'improvement_areas': []
            }

            # Aggregate data from all users
            all_assessments = []
            for user_assessments in self.quality_metrics_data.values():
                all_assessments.extend(user_assessments)

            if not all_assessments:
                return metrics

            metrics['total_assessments'] = len(all_assessments)

            # Quality scores
            quality_scores = [assessment['quality_score']
                              for assessment in all_assessments]
            if quality_scores:
                metrics['average_quality_score'] = statistics.mean(
                    quality_scores)

                # Quality distribution
                metrics['quality_distribution'] = {
                    'excellent': len([q for q in quality_scores if q > 0.9]),
                    'good': len([q for q in quality_scores if 0.7 <= q <= 0.9]),
                    'fair': len([q for q in quality_scores if 0.5 <= q < 0.7]),
                    'poor': len([q for q in quality_scores if q < 0.5])
                }

            # Quality by assessment type
            type_quality = defaultdict(list)
            for assessment in all_assessments:
                type_quality[assessment['assessment_type']].append(
                    assessment['quality_score'])

            for assessment_type, scores in type_quality.items():
                metrics['quality_by_type'][assessment_type] = {
                    'count': len(scores),
                    'average_score': statistics.mean(scores)
                }

            return metrics

        except Exception as e:
            self.logger.error(
                f"Error calculating overall quality metrics: {e}")
            return {}

    async def _analyze_overall_usage_patterns(self) -> Dict[str, Any]:
        """Analyze overall usage patterns"""

        try:
            patterns = {
                'pattern_categories': {},
                'common_patterns': {},
                'pattern_frequency': {},
                'behavioral_insights': []
            }

            # Aggregate data from all users
            all_patterns = []
            for user_patterns in self.usage_patterns_data.values():
                all_patterns.extend(user_patterns)

            if not all_patterns:
                return patterns

            # Pattern categories
            pattern_types = Counter(pattern['pattern_type']
                                    for pattern in all_patterns)
            patterns['pattern_categories'] = dict(pattern_types)

            # Common patterns
            pattern_data = defaultdict(list)
            for pattern in all_patterns:
                pattern_data[pattern['pattern_type']].append(
                    pattern['pattern_data'])

            for pattern_type, data_list in pattern_data.items():
                patterns['common_patterns'][pattern_type] = self._extract_common_patterns(
                    data_list)

            return patterns

        except Exception as e:
            self.logger.error(f"Error analyzing overall usage patterns: {e}")
            return {}

    async def _calculate_integration_efficiency(self) -> Dict[str, Any]:
        """Calculate state-LTM integration efficiency metrics"""

        try:
            metrics = {
                'total_integration_events': 0,
                'success_rate': 0.0,
                'efficiency_by_type': {},
                'performance_impact': {}
            }

            # Aggregate data from all users
            all_events = []
            for user_events in self.state_integration_data.values():
                all_events.extend(user_events)

            if not all_events:
                return metrics

            metrics['total_integration_events'] = len(all_events)

            # Success rate
            successful_events = [
                event for event in all_events if event['success']]
            if all_events:
                metrics['success_rate'] = len(
                    successful_events) / len(all_events)

            # Efficiency by type
            type_efficiency = defaultdict(
                lambda: {'total': 0, 'successful': 0})
            for event in all_events:
                event_type = event['integration_type']
                type_efficiency[event_type]['total'] += 1
                if event['success']:
                    type_efficiency[event_type]['successful'] += 1

            for event_type, counts in type_efficiency.items():
                metrics['efficiency_by_type'][event_type] = {
                    'total_events': counts['total'],
                    'successful_events': counts['successful'],
                    'success_rate': counts['successful'] / counts['total'] if counts['total'] > 0 else 0.0
                }

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating integration efficiency: {e}")
            return {}

    async def _calculate_coordination_metrics(self) -> Dict[str, Any]:
        """Calculate state-LTM coordination metrics"""

        try:
            metrics = {
                'coordination_events': 0,
                'coordination_success_rate': 0.0,
                'coordination_by_type': {},
                'performance_impact': {}
            }

            # Aggregate data from all users
            all_events = []
            for user_events in self.state_integration_data.values():
                all_events.extend(user_events)

            if not all_events:
                return metrics

            # Filter for coordination events
            coordination_events = [
                event for event in all_events
                if 'coordination' in event.get('integration_type', '').lower()
            ]

            metrics['coordination_events'] = len(coordination_events)

            if coordination_events:
                successful_coordinations = [
                    e for e in coordination_events if e['success']]
                metrics['coordination_success_rate'] = len(
                    successful_coordinations) / len(coordination_events)

                # Coordination by type
                type_coordination = defaultdict(
                    lambda: {'total': 0, 'successful': 0})
                for event in coordination_events:
                    event_type = event['integration_type']
                    type_coordination[event_type]['total'] += 1
                    if event['success']:
                        type_coordination[event_type]['successful'] += 1

                for event_type, counts in type_coordination.items():
                    metrics['coordination_by_type'][event_type] = {
                        'total_events': counts['total'],
                        'successful_events': counts['successful'],
                        'success_rate': counts['successful'] / counts['total'] if counts['total'] > 0 else 0.0
                    }

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating coordination metrics: {e}")
            return {}

    async def _analyze_memory_creation_trends(self) -> Dict[str, Any]:
        """Analyze memory creation trends over time"""

        try:
            trends = {
                'hourly_trends': {},
                'daily_trends': {},
                'weekly_trends': {},
                'trend_analysis': {}
            }

            # This would implement actual trend analysis
            # For now, return basic structure

            return trends

        except Exception as e:
            self.logger.error(f"Error analyzing memory creation trends: {e}")
            return {}

    async def _analyze_retrieval_performance_trends(self) -> Dict[str, Any]:
        """Analyze retrieval performance trends over time"""

        try:
            trends = {
                'performance_trends': {},
                'quality_trends': {},
                'trend_analysis': {}
            }

            # This would implement actual trend analysis
            # For now, return basic structure

            return trends

        except Exception as e:
            self.logger.error(
                f"Error analyzing retrieval performance trends: {e}")
            return {}

    async def _analyze_quality_trends(self) -> Dict[str, Any]:
        """Analyze quality trends over time"""

        try:
            trends = {
                'quality_trends': {},
                'improvement_trends': {},
                'trend_analysis': {}
            }

            # This would implement actual trend analysis
            # For now, return basic structure

            return trends

        except Exception as e:
            self.logger.error(f"Error analyzing quality trends: {e}")
            return {}

    async def _perform_pattern_analysis(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed pattern analysis"""

        try:
            analysis = {
                'pattern_correlation': {},
                'behavioral_clusters': {},
                'anomaly_detection': {}
            }

            # This would implement actual pattern analysis
            # For now, return basic structure

            return analysis

        except Exception as e:
            self.logger.error(f"Error performing pattern analysis: {e}")
            return {}

    async def _analyze_state_ltm_synergy(self) -> Dict[str, Any]:
        """Analyze state-LTM synergy and coordination effectiveness"""

        try:
            synergy = {
                'coordination_effectiveness': {},
                'synergy_metrics': {},
                'optimization_opportunities': {}
            }

            # This would implement actual synergy analysis
            # For now, return basic structure

            return synergy

        except Exception as e:
            self.logger.error(f"Error analyzing state-LTM synergy: {e}")
            return {}

    async def _generate_memory_creation_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations for memory creation improvement"""

        try:
            recommendations = []

            overall_metrics = metrics.get('overall_metrics', {})

            # Memory type diversity recommendations
            memories_by_type = overall_metrics.get('memories_by_type', {})
            if memories_by_type:
                dominant_type = max(
                    memories_by_type.items(), key=lambda x: x[1])
                if dominant_type[1] > sum(memories_by_type.values()) * 0.6:
                    recommendations.append(
                        f"Consider diversifying memory types - {dominant_type[0]} dominates at {dominant_type[1]}")

            # Quality recommendations
            avg_importance = overall_metrics.get('average_importance', 0)
            if avg_importance < 5:
                recommendations.append(
                    "Consider improving memory importance scoring - current average is low")

            avg_confidence = overall_metrics.get('average_confidence', 0)
            if avg_confidence < 0.6:
                recommendations.append(
                    "Consider improving memory confidence scoring - current average is low")

            return recommendations

        except Exception as e:
            self.logger.error(
                f"Error generating memory creation recommendations: {e}")
            return []

    async def _identify_retrieval_optimization_opportunities(self, stats: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities for retrieval performance"""

        try:
            opportunities = []

            overall_performance = stats.get('overall_performance', {})

            # Performance optimization opportunities
            avg_retrieval_time = overall_performance.get(
                'average_retrieval_time', 0)
            if avg_retrieval_time > 0.5:
                opportunities.append(
                    f"Consider optimizing retrieval performance - average time: {avg_retrieval_time:.2f}s")

            # Quality optimization opportunities
            quality_metrics = overall_performance.get('quality_metrics', {})
            if quality_metrics:
                avg_quality = quality_metrics.get('average_quality', 0)
                if avg_quality < 0.7:
                    opportunities.append(
                        f"Consider improving retrieval quality - current average: {avg_quality:.2f}")

            return opportunities

        except Exception as e:
            self.logger.error(
                f"Error identifying retrieval optimization opportunities: {e}")
            return []

    async def _generate_quality_improvement_suggestions(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Generate suggestions for quality improvement"""

        try:
            suggestions = []

            overall_quality = quality_metrics.get('overall_quality', {})

            # Quality score suggestions
            avg_quality = overall_quality.get('average_quality_score', 0)
            if avg_quality < 0.7:
                suggestions.append(
                    f"Focus on improving overall quality - current average: {avg_quality:.2f}")

            # Quality by type suggestions
            quality_by_type = overall_quality.get('quality_by_type', {})
            for assessment_type, type_metrics in quality_by_type.items():
                type_avg = type_metrics.get('average_score', 0)
                if type_avg < 0.6:
                    suggestions.append(
                        f"Improve {assessment_type} quality assessment - current average: {type_avg:.2f}")

            return suggestions

        except Exception as e:
            self.logger.error(
                f"Error generating quality improvement suggestions: {e}")
            return []

    async def _generate_behavioral_insights(self, insights: Dict[str, Any]) -> List[str]:
        """Generate behavioral insights from usage patterns"""

        try:
            behavioral_insights = []

            overall_patterns = insights.get('overall_patterns', {})

            # Pattern frequency insights
            pattern_categories = overall_patterns.get('pattern_categories', {})
            if pattern_categories:
                most_common = max(pattern_categories.items(),
                                  key=lambda x: x[1])
                behavioral_insights.append(
                    f"Most common usage pattern: {most_common[0]} ({most_common[1]} occurrences)")

            return behavioral_insights

        except Exception as e:
            self.logger.error(f"Error generating behavioral insights: {e}")
            return []

    async def _generate_integration_optimization_recommendations(self, integration_metrics: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations for state-LTM integration"""

        try:
            recommendations = []

            integration_efficiency = integration_metrics.get(
                'integration_efficiency', {})

            # Success rate recommendations
            success_rate = integration_efficiency.get('success_rate', 0)
            if success_rate < 0.9:
                recommendations.append(
                    f"Improve integration success rate - current: {success_rate:.2%}")

            # Type-specific recommendations
            efficiency_by_type = integration_efficiency.get(
                'efficiency_by_type', {})
            for event_type, type_metrics in efficiency_by_type.items():
                type_success_rate = type_metrics.get('success_rate', 0)
                if type_success_rate < 0.8:
                    recommendations.append(
                        f"Optimize {event_type} integration - success rate: {type_success_rate:.2%}")

            return recommendations

        except Exception as e:
            self.logger.error(
                f"Error generating integration optimization recommendations: {e}")
            return []

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value from a list of numbers"""

        try:
            if not values:
                return 0.0

            sorted_values = sorted(values)
            # For 50th percentile (median), we want the middle value
            if percentile == 50:
                n = len(sorted_values)
                if n % 2 == 0:
                    # Even number of elements, average the two middle values
                    return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
                else:
                    # Odd number of elements, return the middle value
                    return sorted_values[n//2]
            else:
                # For other percentiles, use the standard method
                # For high percentiles (90+, 95+), we want to round up to get the expected value
                # For 95th percentile of 10 elements: we want value 10 (index 9)
                raw_index = (percentile / 100) * (len(sorted_values) - 1)
                index = int(round(raw_index))  # Round to nearest integer
                if index >= len(sorted_values):
                    index = len(sorted_values) - 1
                return sorted_values[index]

        except Exception as e:
            self.logger.error(f"Error calculating percentile: {e}")
            return 0.0

    def _calculate_active_hours(self, memories: List[Dict[str, Any]]) -> List[int]:
        """Calculate active hours from memory creation timestamps"""

        try:
            active_hours = []

            for memory in memories:
                try:
                    timestamp = datetime.fromisoformat(memory['timestamp'])
                    active_hours.append(timestamp.hour)
                except (ValueError, KeyError):
                    continue

            # Return most common active hours
            if active_hours:
                hour_counts = Counter(active_hours)
                return [hour for hour, count in hour_counts.most_common(5)]

            return []

        except Exception as e:
            self.logger.error(f"Error calculating active hours: {e}")
            return []

    def _extract_common_patterns(self, pattern_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common patterns from pattern data"""

        try:
            common_patterns = {
                'pattern_summary': {},
                'frequency_analysis': {}
            }

            # This would implement actual pattern extraction
            # For now, return basic structure

            return common_patterns

        except Exception as e:
            self.logger.error(f"Error extracting common patterns: {e}")
            return {}
