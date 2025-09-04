"""
Performance Optimization for LTM System

This module provides performance monitoring, optimization, and caching
strategies for the LTM system to ensure optimal performance with
state management integration.
"""

import statistics
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ...config.logging_config import get_logger
from ...types.state import AgentState
from .config import EnhancedLTMConfig

logger = get_logger("performance")


class PerformanceOptimizer:
    """
    Optimizes LTM system performance through monitoring, caching, and query optimization.

    This class provides:
    - Query performance monitoring
    - Memory usage optimization
    - Intelligent caching strategies
    - Database query optimization
    - State-LTM performance coordination
    """

    def __init__(self, config: Optional[EnhancedLTMConfig] = None):
        """Initialize the performance optimizer"""
        self.config = config or EnhancedLTMConfig()
        self.logger = get_logger("performance")

        # Performance tracking
        self.query_times: Dict[str, deque] = defaultdict(deque)
        self.memory_usage: Dict[str, deque] = defaultdict(deque)
        self.cache_hits: Dict[str, int] = defaultdict(int)
        self.cache_misses: Dict[str, int] = defaultdict(int)

        # Cache storage
        self.memory_cache: Dict[str, Any] = {}
        self.query_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}

        # Performance thresholds
        self.slow_query_threshold = 1.0  # seconds
        self.cache_ttl = (
            self.config.cache_ttl_seconds
            if hasattr(self.config, "cache_ttl_seconds")
            else 300
        )

        # Optimization settings
        self.enable_query_optimization = getattr(
            self.config, "enable_query_optimization", True
        )
        self.enable_caching = getattr(self.config, "enable_caching", True)

    async def monitor_query_performance(self) -> Dict[str, Any]:
        """
        Monitor query performance metrics.

        Returns:
            Dictionary containing performance metrics
        """

        try:
            metrics: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "query_performance": {},
                "cache_performance": {},
                "memory_usage": {},
                "optimization_recommendations": [],
            }
            # Ensure nested dictionaries are properly typed
            metrics["query_performance"] = {}
            metrics["cache_performance"] = {}
            metrics["memory_usage"] = {}

            # Query performance metrics
            for query_type, times in self.query_times.items():
                if times:
                    metrics["query_performance"][query_type] = {
                        "count": len(times),
                        "avg_time": statistics.mean(times),
                        "min_time": min(times),
                        "max_time": max(times),
                        "p95_time": self._calculate_percentile(list(times), 95),
                        "slow_queries": len(
                            [t for t in times if t > self.slow_query_threshold]
                        ),
                    }

            # Cache performance metrics
            total_hits = sum(self.cache_hits.values())
            total_misses = sum(self.cache_misses.values())
            total_requests = total_hits + total_misses

            if total_requests > 0:
                hit_rate = total_hits / total_requests
                metrics["cache_performance"] = {
                    "hit_rate": hit_rate,
                    "total_requests": total_requests,
                    "cache_hits": total_hits,
                    "cache_misses": total_misses,
                    "cache_by_type": dict(self.cache_hits),
                }

            # Memory usage metrics
            for usage_type, usage_data in self.memory_usage.items():
                if usage_data:
                    metrics["memory_usage"][usage_type] = {
                        "current": usage_data[-1] if usage_data else 0,
                        "avg": statistics.mean(usage_data),
                        "trend": self._calculate_trend(list(usage_data)),
                    }

            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(metrics)
            metrics["optimization_recommendations"] = recommendations

            self.logger.info(
                f"Performance monitoring completed: {len(metrics['query_performance'])} query types, {len(metrics['cache_performance'])} cache metrics"
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Error monitoring query performance: {e}")
            return {}

    async def optimize_memory_usage(self) -> Dict[str, Any]:
        """
        Optimize memory usage patterns.

        Returns:
            Dictionary containing optimization results
        """

        try:
            optimization_results: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "cache_cleanup": {},
                "memory_optimization": {},
                "performance_improvements": {},
            }

            # Clean up expired cache entries
            cache_cleanup = await self._cleanup_expired_cache()
            optimization_results["cache_cleanup"] = cache_cleanup

            # Optimize memory allocation
            memory_optimization = await self._optimize_memory_allocation()
            optimization_results["memory_optimization"] = memory_optimization

            # Analyze performance improvements
            performance_improvements = (
                await self._measure_query_performance_improvements()
            )
            optimization_results["performance_improvements"] = performance_improvements

            self.logger.info(
                f"Memory usage optimization completed: {cache_cleanup.get('removed_entries', 0)} cache entries cleaned"
            )

            return optimization_results

        except Exception as e:
            self.logger.error(f"Error optimizing memory usage: {e}")
            return {}

    async def implement_caching_strategies(self) -> Dict[str, Any]:
        """
        Implement intelligent caching strategies.

        Returns:
            Dictionary containing caching strategy results
        """

        try:
            if not self.enable_caching:
                return {"status": "caching_disabled"}

            caching_results: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "cache_strategies": {},
                "cache_optimization": {},
                "performance_impact": {},
            }
            # Ensure nested dictionaries are properly typed
            caching_results["cache_strategies"] = {}

            # Implement adaptive cache sizing
            adaptive_sizing = await self._implement_adaptive_cache_sizing()
            caching_results["cache_strategies"]["adaptive_sizing"] = adaptive_sizing

            # Implement cache warming
            cache_warming = await self._implement_cache_warming()
            caching_results["cache_strategies"]["cache_warming"] = cache_warming

            # Implement cache invalidation
            cache_invalidation = await self._implement_cache_invalidation()
            caching_results["cache_strategies"][
                "cache_invalidation"
            ] = cache_invalidation

            # Optimize cache performance
            cache_optimization = await self._optimize_cache_performance()
            caching_results["cache_optimization"] = cache_optimization

            # Measure performance impact
            performance_impact = await self._measure_caching_performance_impact()
            caching_results["performance_impact"] = performance_impact

            self.logger.info(
                f"Caching strategies implemented: {len(caching_results['cache_strategies'])} strategies active"
            )

            return caching_results

        except Exception as e:
            self.logger.error(f"Error implementing caching strategies: {e}")
            return {}

    async def optimize_database_queries(self) -> Dict[str, Any]:
        """
        Optimize database queries for better performance.

        Returns:
            Dictionary containing query optimization results
        """

        try:
            if not self.enable_query_optimization:
                return {"status": "query_optimization_disabled"}

            optimization_results: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "query_analysis": {},
                "optimization_applied": {},
                "performance_improvements": {},
            }

            # Analyze slow queries
            slow_query_analysis = await self._analyze_slow_queries()
            optimization_results["query_analysis"] = slow_query_analysis

            # Apply query optimizations
            applied_optimizations = await self._apply_query_optimizations()
            optimization_results["optimization_applied"] = applied_optimizations

            # Measure performance improvements
            performance_improvements = (
                await self._measure_query_performance_improvements()
            )
            optimization_results["performance_improvements"] = performance_improvements

            self.logger.info(
                f"Database query optimization completed: {len(applied_optimizations)} optimizations applied"
            )

            return optimization_results

        except Exception as e:
            self.logger.error(f"Error optimizing database queries: {e}")
            return {}

    async def coordinate_state_ltm_performance(
        self, state_data: AgentState
    ) -> Dict[str, Any]:
        """
        Coordinate performance optimization between state management and LTM.

        This method ensures that performance optimizations don't interfere
        with state management operations and vice versa.

        Args:
            state_data: Current agent state for coordination

        Returns:
            Dictionary containing coordination results
        """

        try:
            coordination_results = {
                "timestamp": datetime.now().isoformat(),
                "state_coordination": {},
                "ltm_optimization": {},
                "coordination_metrics": {},
            }

            # Analyze state-LTM interaction patterns
            interaction_patterns = await self._analyze_state_ltm_interactions(
                state_data
            )
            coordination_results["state_coordination"] = interaction_patterns

            # Optimize LTM operations for state coordination
            ltm_optimization = await self._optimize_ltm_for_state_coordination(
                state_data
            )
            coordination_results["ltm_optimization"] = ltm_optimization

            # Measure coordination performance
            coordination_metrics = await self._measure_coordination_performance(
                state_data
            )
            coordination_results["coordination_metrics"] = coordination_metrics

            self.logger.info(
                f"State-LTM performance coordination completed: {len(interaction_patterns)} patterns analyzed"
            )

            return coordination_results

        except Exception as e:
            self.logger.error(f"Error coordinating state-LTM performance: {e}")
            return {}

    def track_query_time(self, query_type: str, execution_time: float):
        """Track query execution time for performance monitoring"""

        try:
            if query_type not in self.query_times:
                self.query_times[query_type] = deque(
                    maxlen=100
                )  # Keep last 100 queries

            self.query_times[query_type].append(execution_time)

            # Log slow queries
            if execution_time > self.slow_query_threshold:
                self.logger.warning(
                    f"Slow query detected: {query_type} took {execution_time:.2f}s"
                )

        except Exception as e:
            self.logger.error(f"Error tracking query time: {e}")

    def track_memory_usage(self, usage_type: str, usage_amount: int):
        """Track memory usage for optimization"""

        try:
            if usage_type not in self.memory_usage:
                self.memory_usage[usage_type] = deque(
                    maxlen=50
                )  # Keep last 50 measurements

            self.memory_usage[usage_type].append(usage_amount)

        except Exception as e:
            self.logger.error(f"Error tracking memory usage: {e}")

    def record_cache_hit(self, cache_type: str):
        """Record a cache hit for performance monitoring"""

        try:
            self.cache_hits[cache_type] += 1

        except Exception as e:
            self.logger.error(f"Error recording cache hit: {e}")

    def record_cache_miss(self, cache_type: str):
        """Record a cache miss for performance monitoring"""

        try:
            self.cache_misses[cache_type] += 1

        except Exception as e:
            self.logger.error(f"Error recording cache miss: {e}")

    async def get_cached_memory(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached memory if available and not expired"""

        try:
            if not self.enable_caching:
                return None

            if cache_key in self.memory_cache:
                # Check if cache entry is expired
                if cache_key in self.cache_timestamps:
                    timestamp = self.cache_timestamps[cache_key]
                    if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                        self.record_cache_hit("memory_cache")
                        return self.memory_cache[cache_key]
                    else:
                        # Remove expired entry
                        del self.memory_cache[cache_key]
                        del self.cache_timestamps[cache_key]

            self.record_cache_miss("memory_cache")
            return None

        except Exception as e:
            self.logger.error(f"Error getting cached memory: {e}")
            return None

    async def cache_memory(self, cache_key: str, memory_data: Dict[str, Any]):
        """Cache memory data with timestamp"""

        try:
            if not self.enable_caching:
                return

            self.memory_cache[cache_key] = memory_data
            self.cache_timestamps[cache_key] = datetime.now()

            # Track memory usage
            self.track_memory_usage("cache_storage", len(self.memory_cache))

        except Exception as e:
            self.logger.error(f"Error caching memory: {e}")

    async def _cleanup_expired_cache(self) -> Dict[str, Any]:
        """Clean up expired cache entries"""

        try:
            current_time = datetime.now()
            expired_keys = []

            for cache_key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > timedelta(seconds=self.cache_ttl):
                    expired_keys.append(cache_key)

            # Remove expired entries
            for key in expired_keys:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]

            cleanup_results = {
                "removed_entries": len(expired_keys),
                "remaining_entries": len(self.memory_cache),
                "cache_size_bytes": sum(
                    len(str(v)) for v in self.memory_cache.values()
                ),
            }

            if expired_keys:
                self.logger.info(
                    f"Cleaned up {len(expired_keys)} expired cache entries"
                )

            return cleanup_results

        except Exception as e:
            self.logger.error(f"Error cleaning up expired cache: {e}")
            return {"error": str(e)}

    async def _optimize_memory_allocation(self) -> Dict[str, Any]:
        """Optimize memory allocation patterns"""

        try:
            optimization_results: Dict[str, Any] = {
                "cache_size_optimization": {},
                "memory_usage_optimization": {},
                "performance_optimization": {},
            }

            # Optimize cache size based on usage patterns
            if self.memory_cache:
                cache_size = len(self.memory_cache)
                cache_memory = sum(len(str(v)) for v in self.memory_cache.values())

                # If cache is too large, implement LRU eviction
                if cache_size > 1000:  # Arbitrary threshold
                    await self._implement_lru_eviction()
                    optimization_results["cache_size_optimization"][
                        "lru_eviction_applied"
                    ] = True

                optimization_results["cache_size_optimization"][
                    "current_size"
                ] = cache_size
                optimization_results["cache_size_optimization"][
                    "memory_usage_bytes"
                ] = cache_memory

            # Optimize memory usage tracking
            for usage_type, usage_data in self.memory_usage.items():
                if len(usage_data) > 50:  # Keep only recent data
                    # Remove old data points
                    while len(usage_data) > 25:
                        usage_data.popleft()
                    optimization_results["memory_usage_optimization"][
                        usage_type
                    ] = "trimmed_to_25_points"

            return optimization_results

        except Exception as e:
            self.logger.error(f"Error optimizing memory allocation: {e}")
            return {"error": str(e)}

    async def _implement_lru_eviction(self):
        """Implement Least Recently Used cache eviction"""

        try:
            if not self.cache_timestamps:
                return

            # Sort by timestamp (oldest first)
            sorted_entries = sorted(self.cache_timestamps.items(), key=lambda x: x[1])

            # Remove oldest 20% of entries
            entries_to_remove = len(sorted_entries) // 5

            for i in range(entries_to_remove):
                key, _ = sorted_entries[i]
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]

            self.logger.info(
                f"LRU eviction removed {entries_to_remove} oldest cache entries"
            )

        except Exception as e:
            self.logger.error(f"Error implementing LRU eviction: {e}")

    async def _implement_adaptive_cache_sizing(self) -> Dict[str, Any]:
        """Implement adaptive cache sizing based on usage patterns"""

        try:
            adaptive_results: Dict[str, Any] = {
                "current_cache_size": len(self.memory_cache),
                "hit_rate_analysis": {},
                "size_adjustments": {},
            }

            # Analyze hit rates by cache type
            for cache_type in self.cache_hits:
                hits = self.cache_hits[cache_type]
                misses = self.cache_misses.get(cache_type, 0)
                total = hits + misses

                if total > 0:
                    hit_rate = hits / total
                    adaptive_results["hit_rate_analysis"][cache_type] = {
                        "hit_rate": hit_rate,
                        "total_requests": total,
                    }

                    # Adjust cache size based on hit rate
                    if hit_rate < 0.3:  # Low hit rate
                        adaptive_results["size_adjustments"][cache_type] = "reduce_size"
                    elif hit_rate > 0.8:  # High hit rate
                        adaptive_results["size_adjustments"][
                            cache_type
                        ] = "increase_size"

            return adaptive_results

        except Exception as e:
            self.logger.error(f"Error implementing adaptive cache sizing: {e}")
            return {"error": str(e)}

    async def _implement_cache_warming(self) -> Dict[str, Any]:
        """Implement cache warming for frequently accessed data"""

        try:
            warming_results = {
                "warmed_entries": 0,
                "warming_strategy": "frequent_access_patterns",
            }

            # This would implement cache warming based on access patterns
            # For now, return basic structure

            return warming_results

        except Exception as e:
            self.logger.error(f"Error implementing cache warming: {e}")
            return {"error": str(e)}

    async def _implement_cache_invalidation(self) -> Dict[str, Any]:
        """Implement intelligent cache invalidation"""

        try:
            invalidation_results = {
                "invalidated_entries": 0,
                "invalidation_strategy": "time_based_and_pattern_based",
            }

            # This would implement cache invalidation based on data changes
            # For now, return basic structure

            return invalidation_results

        except Exception as e:
            self.logger.error(f"Error implementing cache invalidation: {e}")
            return {"error": str(e)}

    async def _optimize_cache_performance(self) -> Dict[str, Any]:
        """Optimize cache performance"""

        try:
            optimization_results: Dict[str, Any] = {
                "cache_compression": {},
                "access_patterns": {},
                "performance_metrics": {},
            }

            # This would implement cache performance optimizations
            # For now, return basic structure

            return optimization_results

        except Exception as e:
            self.logger.error(f"Error optimizing cache performance: {e}")
            return {"error": str(e)}

    async def _measure_caching_performance_impact(self) -> Dict[str, Any]:
        """Measure the performance impact of caching strategies"""

        try:
            impact_results: Dict[str, Any] = {
                "response_time_improvement": {},
                "memory_usage_impact": {},
                "overall_performance": {},
            }

            # This would measure actual performance improvements
            # For now, return basic structure

            return impact_results

        except Exception as e:
            self.logger.error(f"Error measuring caching performance impact: {e}")
            return {"error": str(e)}

    async def _analyze_slow_queries(self) -> Dict[str, Any]:
        """Analyze slow queries for optimization opportunities"""

        try:
            analysis_results: Dict[str, Any] = {
                "slow_query_types": {},
                "optimization_opportunities": {},
                "recommendations": [],
            }

            # Analyze slow queries by type
            for query_type, times in self.query_times.items():
                slow_queries = [t for t in times if t > self.slow_query_threshold]
                if slow_queries:
                    analysis_results["slow_query_types"][query_type] = {
                        "count": len(slow_queries),
                        "avg_slow_time": statistics.mean(slow_queries),
                        "percentage": len(slow_queries) / len(times) * 100,
                    }

                    # Generate recommendations
                    if len(slow_queries) > len(times) * 0.1:  # More than 10% are slow
                        analysis_results["recommendations"].append(
                            f"Consider optimizing {query_type} queries - {len(slow_queries)}/{len(times)} are slow"
                        )

            return analysis_results

        except Exception as e:
            self.logger.error(f"Error analyzing slow queries: {e}")
            return {"error": str(e)}

    async def _apply_query_optimizations(self) -> Dict[str, Any]:
        """Apply query optimizations"""

        try:
            optimization_results: Dict[str, Any] = {
                "applied_optimizations": {},
                "performance_improvements": {},
                "optimization_status": {},
            }

            # This would apply actual query optimizations
            # For now, return basic structure

            return optimization_results

        except Exception as e:
            self.logger.error(f"Error applying query optimizations: {e}")
            return {"error": str(e)}

    async def _measure_query_performance_improvements(self) -> Dict[str, Any]:
        """Measure query performance improvements"""

        try:
            improvement_results: Dict[str, Any] = {
                "before_optimization": {},
                "after_optimization": {},
                "improvement_percentage": {},
            }

            # This would measure actual improvements
            # For now, return basic structure

            return improvement_results

        except Exception as e:
            self.logger.error(f"Error measuring query performance improvements: {e}")
            return {"error": str(e)}

    async def _analyze_state_ltm_interactions(
        self, state_data: AgentState
    ) -> Dict[str, Any]:
        """Analyze interaction patterns between state management and LTM"""

        try:
            interaction_analysis: Dict[str, Any] = {
                "state_access_patterns": {},
                "ltm_usage_patterns": {},
                "coordination_efficiency": {},
            }

            # Analyze state data for interaction patterns
            if hasattr(state_data, "conversation_history"):
                interaction_analysis["state_access_patterns"][
                    "conversation_history"
                ] = len(state_data.conversation_history)

            if hasattr(state_data, "focus"):
                interaction_analysis["state_access_patterns"]["focus_areas"] = len(
                    state_data.focus
                )

            if hasattr(state_data, "step_count"):
                interaction_analysis["state_access_patterns"][
                    "conversation_complexity"
                ] = state_data.step_count

            # This would analyze actual interaction patterns
            # For now, return basic structure

            return interaction_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing state-LTM interactions: {e}")
            return {"error": str(e)}

    async def _optimize_ltm_for_state_coordination(
        self, state_data: AgentState
    ) -> Dict[str, Any]:
        """Optimize LTM operations for better state coordination"""

        try:
            optimization_results: Dict[str, Any] = {
                "coordination_optimizations": {},
                "performance_improvements": {},
                "optimization_status": {},
            }

            # This would implement actual optimizations
            # For now, return basic structure

            return optimization_results

        except Exception as e:
            self.logger.error(f"Error optimizing LTM for state coordination: {e}")
            return {"error": str(e)}

    async def _measure_coordination_performance(
        self, state_data: AgentState
    ) -> Dict[str, Any]:
        """Measure coordination performance between state and LTM"""

        try:
            performance_metrics: Dict[str, Any] = {
                "coordination_efficiency": {},
                "response_time_impact": {},
                "memory_usage_impact": {},
            }

            # This would measure actual coordination performance
            # For now, return basic structure

            return performance_metrics

        except Exception as e:
            self.logger.error(f"Error measuring coordination performance: {e}")
            return {"error": str(e)}

    async def _generate_optimization_recommendations(
        self, metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations based on performance metrics"""

        try:
            recommendations = []

            # Query performance recommendations
            for query_type, query_metrics in metrics.get(
                "query_performance", {}
            ).items():
                if query_metrics.get("avg_time", 0) > self.slow_query_threshold:
                    recommendations.append(
                        f"Optimize {query_type} queries - average time: {query_metrics['avg_time']:.2f}s"
                    )

                if query_metrics.get("slow_queries", 0) > 0:
                    recommendations.append(
                        f"Investigate slow {query_type} queries - {query_metrics['slow_queries']} slow queries detected"
                    )

            # Cache performance recommendations
            cache_metrics = metrics.get("cache_performance", {})
            if cache_metrics.get("hit_rate", 0) < 0.5:
                recommendations.append(
                    "Low cache hit rate detected - consider cache warming or size optimization"
                )

            # Memory usage recommendations
            for usage_type, usage_metrics in metrics.get("memory_usage", {}).items():
                if usage_metrics.get("trend", "stable") == "increasing":
                    recommendations.append(
                        f"Monitor {usage_type} memory usage - increasing trend detected"
                    )

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating optimization recommendations: {e}")
            return []

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value from a list of numbers"""

        try:
            if not values:
                return 0.0

            sorted_values = sorted(values)
            index = int(percentile / 100 * len(sorted_values))
            return sorted_values[min(index, len(sorted_values) - 1)]

        except Exception as e:
            self.logger.error(f"Error calculating percentile: {e}")
            return 0.0

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a list of values"""

        try:
            if len(values) < 2:
                return "stable"

            # Simple trend calculation
            recent_avg = (
                statistics.mean(values[-5:]) if len(values) >= 5 else values[-1]
            )
            older_avg = statistics.mean(values[:-5]) if len(values) >= 10 else values[0]

            if recent_avg > older_avg * 1.1:
                return "increasing"
            elif recent_avg < older_avg * 0.9:
                return "decreasing"
            else:
                return "stable"

        except Exception as e:
            self.logger.error(f"Error calculating trend: {e}")
            return "stable"
