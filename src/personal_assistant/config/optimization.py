"""
Database performance optimization and analysis module.

This module provides:
- Table performance analysis
- Index usage analysis
- Query optimization recommendations
- Performance threshold configuration
- Performance monitoring and alerting
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from personal_assistant.config.database import db_config
from personal_assistant.config.settings import settings
import os

logger = logging.getLogger(__name__)


@dataclass
class TablePerformance:
    """Table performance metrics."""
    table_name: str
    row_count: int
    table_size_mb: float
    index_size_mb: float
    total_size_mb: float
    last_vacuum: Optional[datetime]
    last_analyze: Optional[datetime]
    bloat_percentage: float
    performance_score: float


@dataclass
class IndexUsage:
    """Index usage statistics."""
    index_name: str
    table_name: str
    index_size_mb: float
    scans: int
    tuples_read: int
    tuples_fetched: int
    usage_percentage: float
    efficiency_score: float


@dataclass
class QueryPerformance:
    """Query performance metrics."""
    query_hash: str
    query_text: str
    execution_count: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    stddev_time_ms: float
    calls_per_minute: float
    performance_category: str


class DatabaseOptimizer:
    """Database performance optimization and analysis service."""

    def __init__(self, auto_start_monitoring: bool = False):
        self.performance_thresholds = {
            "slow_query_threshold_ms": float(os.getenv("DB_SLOW_QUERY_THRESHOLD_MS", "100")),
            "table_bloat_threshold": float(os.getenv("DB_TABLE_BLOAT_THRESHOLD", "20.0")),
            "index_usage_threshold": float(os.getenv("DB_INDEX_USAGE_THRESHOLD", "10.0")),
            "connection_pool_efficiency": float(os.getenv("DB_POOL_EFFICIENCY_THRESHOLD", "80.0")),
            "query_response_time_p95": float(os.getenv("DB_QUERY_RESPONSE_P95_THRESHOLD", "100"))
        }

        self.performance_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        self._monitoring_task = None
        self._monitoring_started = False

        # Start performance monitoring if requested
        if auto_start_monitoring:
            self._start_monitoring()

    def _start_monitoring(self):
        """Start performance monitoring in a safe way."""
        try:
            # Check if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create the task
                self._monitoring_task = asyncio.create_task(
                    self._start_performance_monitoring())
                self._monitoring_started = True
                logger.info("Performance monitoring started")
            except RuntimeError:
                # No event loop, will start when first used
                logger.debug(
                    "No event loop available, monitoring will start when first used")
                self._monitoring_started = False
        except Exception as e:
            logger.warning(f"Failed to start performance monitoring: {e}")
            self._monitoring_started = False

    async def _ensure_monitoring_started(self):
        """Ensure performance monitoring is started."""
        if not self._monitoring_started:
            try:
                self._monitoring_task = asyncio.create_task(
                    self._start_performance_monitoring())
                self._monitoring_started = True
                logger.info("Performance monitoring started")
            except Exception as e:
                logger.warning(f"Failed to start performance monitoring: {e}")

    async def analyze_table_performance(self, session: AsyncSession) -> List[TablePerformance]:
        """Analyze performance of all tables in the database."""
        try:
            # Ensure monitoring is started
            await self._ensure_monitoring_started()

            # Get table statistics
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze,
                    vacuum_count,
                    autovacuum_count,
                    analyze_count,
                    autoanalyze_count
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """)

            result = await session.execute(query)
            table_stats = result.fetchall()

            # Get table sizes
            size_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size_pretty,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                    pg_relation_size(schemaname||'.'||tablename) as table_size_bytes,
                    pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename) as index_size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)

            size_result = await session.execute(size_query)
            size_stats = {row.tablename: row for row in size_result.fetchall()}

            table_performance = []

            for stat in table_stats:
                table_name = stat.tablename
                size_info = size_stats.get(table_name)

                if not size_info:
                    continue

                # Calculate bloat percentage
                total_size_mb = size_info.size_bytes / (1024 * 1024)
                table_size_mb = size_info.table_size_bytes / (1024 * 1024)
                index_size_mb = size_info.index_size_bytes / (1024 * 1024)

                # Estimate bloat (simplified calculation)
                bloat_percentage = (
                    stat.dead_rows / max(stat.live_rows, 1)) * 100 if stat.live_rows > 0 else 0

                # Calculate performance score (0-100)
                performance_score = max(0, 100 - bloat_percentage)

                # Adjust score based on maintenance
                if stat.last_vacuum:
                    days_since_vacuum = (
                        datetime.now() - stat.last_vacuum).days
                    if days_since_vacuum > 7:
                        performance_score -= min(20, days_since_vacuum - 7)

                performance_score = max(0, min(100, performance_score))

                table_performance.append(TablePerformance(
                    table_name=table_name,
                    row_count=stat.live_rows,
                    table_size_mb=table_size_mb,
                    index_size_mb=index_size_mb,
                    total_size_mb=total_size_mb,
                    last_vacuum=stat.last_vacuum,
                    last_analyze=stat.last_analyze,
                    bloat_percentage=bloat_percentage,
                    performance_score=performance_score
                ))

            return table_performance

        except Exception as e:
            logger.error(f"Failed to analyze table performance: {e}")
            return []

    async def analyze_index_usage(self, session: AsyncSession) -> List[IndexUsage]:
        """Analyze index usage and efficiency."""
        try:
            # Ensure monitoring is started
            await self._ensure_monitoring_started()

            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size_pretty,
                    pg_relation_size(indexrelid) as size_bytes
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
            """)

            result = await session.execute(query)
            index_stats = result.fetchall()

            index_usage = []

            for stat in index_stats:
                index_size_mb = stat.size_bytes / (1024 * 1024)

                # Calculate usage percentage
                total_operations = stat.scans + stat.tuples_read + stat.tuples_fetched
                usage_percentage = (
                    stat.scans / max(total_operations, 1)) * 100 if total_operations > 0 else 0

                # Calculate efficiency score
                efficiency_score = 100
                if stat.scans == 0:
                    efficiency_score = 0  # Unused index
                elif usage_percentage < self.performance_thresholds["index_usage_threshold"]:
                    efficiency_score = 50  # Low usage

                index_usage.append(IndexUsage(
                    index_name=stat.indexname,
                    table_name=stat.tablename,
                    index_size_mb=index_size_mb,
                    scans=stat.scans,
                    tuples_read=stat.tuples_read,
                    tuples_fetched=stat.tuples_fetched,
                    usage_percentage=usage_percentage,
                    efficiency_score=efficiency_score
                ))

            return index_usage

        except Exception as e:
            logger.error(f"Failed to analyze index usage: {e}")
            return []

    async def analyze_query_performance(self, session: AsyncSession) -> List[QueryPerformance]:
        """Analyze query performance from pg_stat_statements."""
        try:
            # Ensure monitoring is started
            await self._ensure_monitoring_started()

            # Check if pg_stat_statements extension is available
            check_query = text("""
                SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
            """)

            result = await session.execute(check_query)
            if not result.fetchone():
                logger.warning(
                    "pg_stat_statements extension not available. Query performance analysis disabled.")
                return []

            query = text("""
                SELECT 
                    queryid,
                    query,
                    calls,
                    total_time,
                    mean_time,
                    min_time,
                    max_time,
                    stddev_time,
                    calls_per_minute
                FROM pg_stat_statements
                WHERE calls > 0
                ORDER BY total_time DESC
                LIMIT 100
            """)

            result = await session.execute(query)
            query_stats = result.fetchall()

            query_performance = []

            for stat in query_stats:
                # Categorize performance
                if stat.mean_time < self.performance_thresholds["slow_query_threshold_ms"]:
                    performance_category = "fast"
                elif stat.mean_time < self.performance_thresholds["slow_query_threshold_ms"] * 2:
                    performance_category = "moderate"
                else:
                    performance_category = "slow"

                query_performance.append(QueryPerformance(
                    query_hash=str(stat.queryid),
                    query_text=stat.query[:200] +
                    "..." if len(stat.query) > 200 else stat.query,
                    execution_count=stat.calls,
                    total_time_ms=stat.total_time,
                    avg_time_ms=stat.mean_time,
                    min_time_ms=stat.min_time,
                    max_time_ms=stat.max_time,
                    stddev_time_ms=stat.stddev_time or 0,
                    calls_per_minute=stat.calls_per_minute or 0,
                    performance_category=performance_category
                ))

            return query_performance

        except Exception as e:
            logger.error(f"Failed to analyze query performance: {e}")
            return []

    async def get_optimization_recommendations(self, session: AsyncSession) -> Dict[str, Any]:
        """Generate optimization recommendations based on analysis."""
        try:
            # Ensure monitoring is started
            await self._ensure_monitoring_started()

            recommendations = {
                "tables": [],
                "indexes": [],
                "queries": [],
                "maintenance": [],
                "priority": "low"
            }

            # Analyze tables
            table_performance = await self.analyze_table_performance(session)
            for table in table_performance:
                if table.bloat_percentage > self.performance_thresholds["table_bloat_threshold"]:
                    recommendations["tables"].append({
                        "table": table.table_name,
                        "issue": f"High bloat: {table.bloat_percentage:.1f}%",
                        "action": "Run VACUUM ANALYZE",
                        "priority": "high" if table.bloat_percentage > 50 else "medium"
                    })

                if not table.last_vacuum or (datetime.now() - table.last_vacuum).days > 7:
                    recommendations["maintenance"].append({
                        "table": table.table_name,
                        "issue": "Table not vacuumed recently",
                        "action": "Schedule regular VACUUM",
                        "priority": "medium"
                    })

            # Analyze indexes
            index_usage = await self.analyze_index_usage(session)
            for index in index_usage:
                if index.efficiency_score < 50:
                    recommendations["indexes"].append({
                        "index": index.index_name,
                        "table": index.table_name,
                        "issue": "Unused or inefficient index",
                        "action": "Consider dropping or optimizing",
                        "priority": "medium"
                    })

            # Analyze queries
            query_performance = await self.analyze_query_performance(session)
            slow_queries = [
                q for q in query_performance if q.performance_category == "slow"]

            if slow_queries:
                recommendations["queries"].extend([
                    {
                        "query": query.query_text,
                        "issue": f"Slow query: {query.avg_time_ms:.2f}ms average",
                        "action": "Optimize query or add indexes",
                        "priority": "high"
                    }
                    for query in slow_queries[:5]  # Top 5 slowest
                ])

            # Determine overall priority
            high_priority = sum(1 for rec in recommendations["tables"] + recommendations["indexes"] + recommendations["queries"]
                                if rec.get("priority") == "high")

            if high_priority > 0:
                recommendations["priority"] = "high"
            elif any(rec.get("priority") == "medium" for rec in recommendations["tables"] + recommendations["indexes"] + recommendations["queries"]):
                recommendations["priority"] = "medium"

            return recommendations

        except Exception as e:
            logger.error(
                f"Failed to generate optimization recommendations: {e}")
            return {"error": str(e)}

    async def get_performance_summary(self, session: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        try:
            # Ensure monitoring is started
            await self._ensure_monitoring_started()

            # Get pool stats
            pool_stats = await db_config.get_pool_stats()

            # Analyze tables
            table_performance = await self.analyze_table_performance(session)

            # Analyze indexes
            index_usage = await self.analyze_index_usage(session)

            # Analyze queries
            query_performance = await self.analyze_query_performance(session)

            # Calculate summary metrics
            total_table_size = sum(t.total_size_mb for t in table_performance)
            avg_table_performance = sum(t.performance_score for t in table_performance) / len(
                table_performance) if table_performance else 0
            total_index_size = sum(i.index_size_mb for i in index_usage)
            avg_index_efficiency = sum(
                i.efficiency_score for i in index_usage) / len(index_usage) if index_usage else 0

            # Count slow queries
            slow_query_count = sum(
                1 for q in query_performance if q.performance_category == "slow")

            summary = {
                "timestamp": datetime.now().isoformat(),
                "overall_performance": {
                    "score": round((avg_table_performance + avg_index_efficiency) / 2, 2),
                    "status": "healthy" if avg_table_performance > 80 and avg_index_efficiency > 80 else "degraded"
                },
                "storage": {
                    "total_table_size_mb": round(total_table_size, 2),
                    "total_index_size_mb": round(total_index_size, 2),
                    "total_database_size_mb": round(total_table_size + total_index_size, 2)
                },
                "tables": {
                    "count": len(table_performance),
                    "avg_performance_score": round(avg_table_performance, 2),
                    "high_bloat_count": sum(1 for t in table_performance if t.bloat_percentage > self.performance_thresholds["table_bloat_threshold"])
                },
                "indexes": {
                    "count": len(index_usage),
                    "avg_efficiency_score": round(avg_index_efficiency, 2),
                    "unused_count": sum(1 for i in index_usage if i.efficiency_score < 50)
                },
                "queries": {
                    "total_analyzed": len(query_performance),
                    "slow_query_count": slow_query_count,
                    "avg_response_time_ms": round(sum(q.avg_time_ms for q in query_performance) / len(query_performance), 2) if query_performance else 0
                },
                "connection_pool": {
                    "utilization_percentage": round(pool_stats.utilization_percentage, 2),
                    "efficiency_status": "efficient" if pool_stats.utilization_percentage > self.performance_thresholds["connection_pool_efficiency"] else "inefficient"
                }
            }

            # Store in history
            self._add_to_history(summary)

            return summary

        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {"error": str(e)}

    def _add_to_history(self, performance_data: Dict[str, Any]):
        """Add performance data to history."""
        self.performance_history.append(performance_data)

        # Keep only recent history
        if len(self.performance_history) > self.max_history_size:
            self.performance_history = self.performance_history[-self.max_history_size:]

    async def _start_performance_monitoring(self):
        """Start background performance monitoring."""
        while True:
            try:
                # Get a session and run performance analysis
                async with db_config.get_session_context() as session:
                    await self.get_performance_summary(session)

                # Run every 5 minutes
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)  # Shorter interval on error


# Global optimizer instance - don't auto-start monitoring to avoid import issues
db_optimizer = DatabaseOptimizer(auto_start_monitoring=False)
