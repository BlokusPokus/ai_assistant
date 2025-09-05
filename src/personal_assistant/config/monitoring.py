"""
Monitoring configuration for database health checks and performance metrics.

This module provides:
- Database health check endpoints
- Connection pool status monitoring
- Performance metrics collection
- Health status aggregation
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from personal_assistant.config.database import db_config
from personal_assistant.config.settings import settings
from personal_assistant.monitoring import get_metrics_service

logger = logging.getLogger(__name__)

# Create monitoring router
monitoring_router = APIRouter(prefix="/health", tags=["monitoring"])


class HealthMonitor:
    """Database health monitoring service."""

    def __init__(self):
        self.last_check: Optional[datetime] = None
        self.health_history: list = []
        self.max_history_size = 100

    async def get_database_health(self) -> Dict[str, Any]:
        """Get comprehensive database health status."""
        try:
            health_data = await db_config.check_health()
            health_data = dict(health_data) if health_data else {}

            # Add timestamp
            health_data["timestamp"] = datetime.now().isoformat()
            health_data["service"] = "database"

            # Update Prometheus metrics
            try:
                metrics_service = get_metrics_service()
                is_healthy = health_data.get("status") == "healthy"
                response_time = health_data.get("response_time", 0)

                # Update database health metrics
                metrics_service.database_health_status.set(1 if is_healthy else 0)
                if response_time:
                    metrics_service.database_response_time_seconds.observe(
                        response_time
                    )

            except Exception as metrics_error:
                logger.warning(f"Failed to update Prometheus metrics: {metrics_error}")

            # Store in history
            self._add_to_history(health_data)

            return health_data

        except Exception as e:
            logger.error(f"Failed to get database health: {e}")
            return {
                "status": "error",
                "service": "database",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status and statistics."""
        try:
            pool_stats = await db_config.get_pool_stats()
            performance_metrics = await db_config.get_performance_metrics()

            # Update Prometheus metrics
            try:
                metrics_service = get_metrics_service()
                metrics_service.database_connections_active.set(pool_stats.checked_out)
                metrics_service.database_connection_pool_utilization.set(
                    pool_stats.utilization_percentage
                )
            except Exception as metrics_error:
                logger.warning(
                    f"Failed to update Prometheus pool metrics: {metrics_error}"
                )

            return {
                "pool_statistics": {
                    "pool_size": pool_stats.pool_size,
                    "max_overflow": pool_stats.max_overflow,
                    "checked_in": pool_stats.checked_in,
                    "checked_out": pool_stats.checked_out,
                    "overflow": pool_stats.overflow,
                    "invalid": pool_stats.invalid,
                    "total_connections": pool_stats.total_connections,
                    "utilization_percentage": pool_stats.utilization_percentage,
                    "last_updated": pool_stats.last_updated.isoformat(),
                },
                "performance_metrics": performance_metrics,
                "timestamp": datetime.now().isoformat(),
                "service": "database_pool",
            }

        except Exception as e:
            logger.error(f"Failed to get pool status: {e}")
            return {
                "status": "error",
                "service": "database_pool",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        try:
            performance_data = await db_config.get_performance_metrics()
            performance_data = dict(performance_data) if performance_data else {}

            # Add additional metrics
            performance_data.update(
                {
                    "timestamp": datetime.now().isoformat(),
                    "service": "database_performance",
                    "system_info": {
                        "environment": settings.ENVIRONMENT,
                        "debug_mode": settings.DEBUG,
                        "log_level": settings.LOG_LEVEL,
                    },
                }
            )

            return performance_data

        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {
                "status": "error",
                "service": "database_performance",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Get database health
            db_health = await self.get_database_health()

            # Determine overall status
            overall_status = "healthy"
            if db_health.get("status") == "error":
                overall_status = "unhealthy"
            elif db_health.get("status") == "degraded":
                overall_status = "degraded"

            # Get pool status
            pool_status = await self.get_pool_status()

            # Get performance metrics
            performance = await self.get_performance_metrics()

            # Update Prometheus application health metrics
            try:
                metrics_service = get_metrics_service()
                is_healthy = overall_status == "healthy"
                metrics_service.application_health_status.set(1 if is_healthy else 0)
            except Exception as metrics_error:
                logger.warning(
                    f"Failed to update Prometheus application health metrics: {metrics_error}"
                )

            overall_health = {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "database": {
                        "status": db_health.get("status", "unknown"),
                        "response_time": db_health.get("response_time"),
                        "last_check": db_health.get("last_check"),
                    },
                    "connection_pool": {
                        "status": "healthy"
                        if pool_status.get("status") != "error"
                        else "unhealthy",
                        "utilization": pool_status.get("pool_statistics", {}).get(
                            "utilization_percentage", 0
                        ),
                    },
                },
                "performance_summary": {
                    "database_response_time": db_health.get("response_time"),
                    "pool_utilization": pool_status.get("pool_statistics", {}).get(
                        "utilization_percentage", 0
                    ),
                    "slow_query_threshold": performance.get("thresholds", {}).get(
                        "slow_query_threshold"
                    ),
                },
            }

            return overall_health

        except Exception as e:
            logger.error(f"Failed to get overall health: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _add_to_history(self, health_data: Dict[str, Any]):
        """Add health data to history for trending analysis."""
        self.health_history.append(health_data)

        # Keep only recent history
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size :]

    def get_health_history(self, hours: int = 24) -> list:
        """Get health history for the specified number of hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [
            entry
            for entry in self.health_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]


# Create global health monitor instance
health_monitor = HealthMonitor()


# Health check endpoints
@monitoring_router.get("/database")
async def database_health():
    """Database health check endpoint."""
    try:
        health_data = await health_monitor.get_database_health()

        # Return appropriate HTTP status
        if health_data.get("status") == "healthy":
            return JSONResponse(content=health_data, status_code=200)
        elif health_data.get("status") == "degraded":
            return JSONResponse(content=health_data, status_code=200)
        else:
            return JSONResponse(content=health_data, status_code=503)

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=500,
        )


@monitoring_router.get("/database/pool")
async def database_pool_status():
    """Connection pool status endpoint."""
    try:
        pool_data = await health_monitor.get_pool_status()

        if pool_data.get("status") == "error":
            return JSONResponse(content=pool_data, status_code=503)

        return JSONResponse(content=pool_data, status_code=200)

    except Exception as e:
        logger.error(f"Pool status check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=500,
        )


@monitoring_router.get("/database/performance")
async def database_performance():
    """Database performance metrics endpoint."""
    try:
        performance_data = await health_monitor.get_performance_metrics()

        if performance_data.get("status") == "error":
            return JSONResponse(content=performance_data, status_code=503)

        return JSONResponse(content=performance_data, status_code=200)

    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=500,
        )


@monitoring_router.get("/overall")
async def overall_health():
    """Overall system health endpoint."""
    try:
        overall_data = await health_monitor.get_overall_health()

        # Return appropriate HTTP status
        if overall_data.get("status") == "healthy":
            return JSONResponse(content=overall_data, status_code=200)
        elif overall_data.get("status") == "degraded":
            return JSONResponse(content=overall_data, status_code=200)
        else:
            return JSONResponse(content=overall_data, status_code=503)

    except Exception as e:
        logger.error(f"Overall health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=500,
        )


@monitoring_router.get("/history")
async def health_history(hours: int = 24):
    """Get health history for trending analysis."""
    try:
        if hours < 1 or hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=400, detail="Hours must be between 1 and 168"
            )

        history = health_monitor.get_health_history(hours)

        return {
            "history": history,
            "hours_requested": hours,
            "records_returned": len(history),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health history request failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=500,
        )
