"""
Analytics API endpoints for SMS usage analytics, cost analysis, and performance monitoring.
"""

import csv
import io
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.sms_router.services.analytics import SMSAnalyticsService
from personal_assistant.sms_router.services.cost_calculator import SMSCostCalculator
from personal_assistant.sms_router.services.performance_monitor import (
    SMSPerformanceMonitor,
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    from personal_assistant.database.session import _get_session_factory

    session = _get_session_factory()()
    try:
        yield session
    finally:
        await session.close()


def create_permission_checker(resource_type: str, action: str):
    """Create a permission checker dependency for a specific resource and action."""

    async def check_permission(
        request: Request, db: AsyncSession = Depends(get_db)
    ) -> bool:
        """Check if the current user has the required permission."""
        try:
            # Check if user is authenticated
            if (
                not hasattr(request.state, "authenticated")
                or not request.state.authenticated
            ):
                raise HTTPException(status_code=401, detail="Authentication required")

            user_id = request.state.user_id

            # Import here to avoid circular imports
            from personal_assistant.auth.permission_service import PermissionService

            permission_service = PermissionService(db)

            # Check permission
            has_permission = await permission_service.check_permission(
                user_id=user_id, resource_type=resource_type, action=action
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {resource_type}:{action}",
                )

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking permission {resource_type}:{action}: {e}")
            raise HTTPException(status_code=500, detail="Permission check failed")

    return check_permission


# User Analytics Endpoints
@router.get("/me/sms-analytics")
async def get_user_sms_analytics(
    request: Request,
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("user", "read_sms_analytics")),
):
    """Get SMS usage analytics for the current user."""
    try:
        user_id = request.state.user_id

        # Validate time range
        valid_ranges = ["7d", "30d", "90d", "1y"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}",
            )

        analytics_service = SMSAnalyticsService(db)

        # Get usage summary
        usage_summary = await analytics_service.get_user_usage_summary(
            user_id, time_range
        )

        # Get usage trends
        usage_trends = await analytics_service.get_user_usage_trends(
            user_id, time_range
        )

        # Get performance metrics
        performance_metrics = await analytics_service.get_user_performance_metrics(
            user_id, time_range
        )

        # Get message breakdown
        message_breakdown = await analytics_service.get_user_message_breakdown(
            user_id, time_range
        )

        return {
            "user_id": user_id,
            "time_range": time_range,
            "usage_summary": usage_summary,
            "usage_trends": usage_trends,
            "performance_metrics": performance_metrics,
            "message_breakdown": message_breakdown,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting user SMS analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SMS analytics")


@router.get("/me/sms-costs")
async def get_user_sms_costs(
    request: Request,
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("user", "read_sms_costs")),
):
    """Get SMS cost analysis for the current user."""
    try:
        user_id = request.state.user_id

        # Validate time range
        valid_ranges = ["7d", "30d", "90d", "1y"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}",
            )

        cost_calculator = SMSCostCalculator(db)

        # Get cost breakdown
        cost_breakdown = await cost_calculator.get_cost_breakdown(user_id)

        # Get cost trends
        cost_trends = await cost_calculator.get_cost_trends(user_id)

        # Get optimization tips
        optimization_tips = await cost_calculator.get_cost_optimization_tips(user_id)

        return {
            "user_id": user_id,
            "time_range": time_range,
            "cost_breakdown": cost_breakdown,
            "cost_trends": cost_trends,
            "optimization_tips": optimization_tips,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting user SMS costs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SMS cost analysis")


@router.get("/me/sms-usage-report")
async def download_user_usage_report(
    request: Request,
    format: str = Query("csv", description="Report format: csv, json"),
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("user", "read_sms_analytics")),
):
    """Download SMS usage report for the current user."""
    try:
        user_id = request.state.user_id

        # Validate parameters
        valid_formats = ["csv", "json"]
        valid_ranges = ["7d", "30d", "90d", "1y"]

        if format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}",
            )

        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}",
            )

        analytics_service = SMSAnalyticsService(db)
        cost_calculator = SMSCostCalculator(db)

        # Get comprehensive data
        usage_summary = await analytics_service.get_user_usage_summary(
            user_id, time_range
        )
        performance_metrics = await analytics_service.get_user_performance_metrics(
            user_id, time_range
        )
        cost_breakdown = await cost_calculator.calculate_user_costs(user_id, time_range)

        # Generate report based on format
        if format == "csv":
            return await _generate_csv_report(
                user_id, time_range, usage_summary, performance_metrics, cost_breakdown
            )
        else:  # JSON
            return await _generate_json_report(
                user_id, time_range, usage_summary, performance_metrics, cost_breakdown
            )

    except Exception as e:
        logger.error(f"Error generating user SMS usage report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate usage report")


# Admin Analytics Endpoints
@router.get("/admin/sms-analytics/system")
async def get_system_sms_analytics(
    request: Request,
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("system", "view_sms_analytics")),
):
    """Get system-wide SMS analytics."""
    try:
        # Validate time range
        valid_ranges = ["7d", "30d", "90d", "1y"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}",
            )

        analytics_service = SMSAnalyticsService(db)
        cost_calculator = SMSCostCalculator(db)

        # Get system metrics
        system_performance = await analytics_service.get_system_performance_metrics(
            time_range
        )
        system_costs = await cost_calculator.get_system_cost_summary(time_range)
        performance_trends = await analytics_service.get_performance_trends(time_range)

        return {
            "time_range": time_range,
            "system_performance": system_performance,
            "system_costs": system_costs,
            "performance_trends": performance_trends,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting system SMS analytics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get system SMS analytics"
        )


@router.get("/admin/sms-analytics/users")
async def get_users_sms_analytics(
    request: Request,
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("system", "view_sms_analytics")),
):
    """Get SMS analytics for multiple users."""
    try:
        # Validate time range
        valid_ranges = ["7d", "30d", "90d", "1y"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}",
            )

        analytics_service = SMSAnalyticsService(db)
        cost_calculator = SMSCostCalculator(db)

        # Get user analytics (simplified - in production you'd want pagination)
        # For now, we'll return a summary of top users
        system_costs = await cost_calculator.get_system_cost_summary(time_range)
        top_cost_users = system_costs.get("top_cost_users", [])

        # Get detailed analytics for top users
        user_analytics = []
        for user_data in top_cost_users[:limit]:
            user_id = user_data["user_id"]

            try:
                usage_summary = await analytics_service.get_user_usage_summary(
                    user_id, time_range
                )
                cost_breakdown = await cost_calculator.calculate_user_costs(
                    user_id, time_range
                )

                user_analytics.append(
                    {
                        "user_id": user_id,
                        "usage_summary": usage_summary,
                        "cost_breakdown": cost_breakdown,
                    }
                )
            except Exception as e:
                logger.warning(f"Error getting analytics for user {user_id}: {e}")
                continue

        return {
            "time_range": time_range,
            "total_users": len(user_analytics),
            "limit": limit,
            "offset": offset,
            "user_analytics": user_analytics,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting users SMS analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users SMS analytics")


@router.get("/admin/sms-performance")
async def get_sms_performance_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("system", "view_sms_performance")),
):
    """Get SMS performance monitoring metrics."""
    try:
        performance_monitor = SMSPerformanceMonitor(db)

        # Get real-time metrics
        real_time_metrics = await performance_monitor.get_real_time_metrics()

        # Get SLA compliance
        sla_compliance = await performance_monitor.check_sla_compliance()

        # Get performance alerts
        performance_alerts = await performance_monitor.generate_performance_alerts()

        # Get system health
        system_health = await performance_monitor.get_system_health_metrics()

        # Get performance recommendations
        recommendations = await performance_monitor.get_performance_recommendations()

        return {
            "real_time_metrics": real_time_metrics,
            "sla_compliance": sla_compliance,
            "performance_alerts": performance_alerts,
            "system_health": system_health,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting SMS performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


@router.get("/admin/sms-performance/historical")
async def get_historical_performance(
    request: Request,
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("system", "view_sms_performance")),
):
    """Get historical SMS performance data."""
    try:
        # Validate time range
        valid_ranges = ["7d", "30d", "90d", "1y"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}",
            )

        performance_monitor = SMSPerformanceMonitor(db)

        # Get historical performance
        historical_performance = await performance_monitor.get_historical_performance(
            time_range
        )

        return {
            "time_range": time_range,
            "historical_performance": historical_performance,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting historical performance: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get historical performance"
        )


@router.get("/admin/sms-performance/alerts")
async def get_performance_alerts(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(create_permission_checker("system", "view_sms_performance")),
):
    """Get current performance alerts."""
    try:
        performance_monitor = SMSPerformanceMonitor(db)

        # Get performance alerts
        alerts = await performance_monitor.generate_performance_alerts()

        return {"alerts": alerts, "generated_at": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"Error getting performance alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance alerts")


# Helper functions for report generation
async def _generate_csv_report(
    user_id: int,
    time_range: str,
    usage_summary: Dict[str, Any],
    performance_metrics: Dict[str, Any],
    cost_breakdown: Dict[str, Any],
) -> StreamingResponse:
    """Generate CSV report for SMS usage."""
    try:
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "SMS Usage Report",
                f"User ID: {user_id}",
                f"Time Range: {time_range}",
                f"Generated: {datetime.utcnow().isoformat()}",
            ]
        )
        writer.writerow([])

        # Usage Summary Section
        writer.writerow(["USAGE SUMMARY"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Messages", usage_summary.get("total_messages", 0)])
        writer.writerow(["Inbound Messages", usage_summary.get("inbound_messages", 0)])
        writer.writerow(
            ["Outbound Messages", usage_summary.get("outbound_messages", 0)]
        )
        writer.writerow(["Success Rate (%)", usage_summary.get("success_rate", 0)])
        writer.writerow(
            [
                "Average Processing Time (ms)",
                usage_summary.get("average_processing_time_ms", 0),
            ]
        )
        writer.writerow([])

        # Performance Metrics Section
        writer.writerow(["PERFORMANCE METRICS"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(
            ["Successful Messages", performance_metrics.get("successful_messages", 0)]
        )
        writer.writerow(
            ["Failed Messages", performance_metrics.get("failed_messages", 0)]
        )
        writer.writerow(
            ["Success Rate (%)", performance_metrics.get("success_rate", 0)]
        )
        writer.writerow(
            [
                "Average Response Time (ms)",
                performance_metrics.get("processing_time_metrics", {}).get(
                    "average_ms", 0
                ),
            ]
        )
        writer.writerow(
            [
                "Min Response Time (ms)",
                performance_metrics.get("processing_time_metrics", {}).get(
                    "minimum_ms", 0
                ),
            ]
        )
        writer.writerow(
            [
                "Max Response Time (ms)",
                performance_metrics.get("processing_time_metrics", {}).get(
                    "maximum_ms", 0
                ),
            ]
        )
        writer.writerow([])

        # Cost Analysis Section
        writer.writerow(["COST ANALYSIS"])
        writer.writerow(["Metric", "Value (USD)"])
        writer.writerow(["Total Cost", cost_breakdown.get("total_cost_usd", 0)])
        writer.writerow(["Inbound Cost", cost_breakdown.get("inbound_cost_usd", 0)])
        writer.writerow(["Outbound Cost", cost_breakdown.get("outbound_cost_usd", 0)])
        writer.writerow(["MMS Cost", cost_breakdown.get("mms_cost_usd", 0)])
        writer.writerow(
            ["Monthly Number Cost", cost_breakdown.get("monthly_number_cost_usd", 0)]
        )
        writer.writerow(
            [
                "Total with Monthly Fees",
                cost_breakdown.get("total_with_monthly_fees", 0),
            ]
        )
        writer.writerow(["Cost per Message", cost_breakdown.get("cost_per_message", 0)])

        # Get CSV content
        csv_content = output.getvalue()
        output.close()

        # Create response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=sms_usage_report_{user_id}_{time_range}.csv"
            },
        )

    except Exception as e:
        logger.error(f"Error generating CSV report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate CSV report")


async def _generate_json_report(
    user_id: int,
    time_range: str,
    usage_summary: Dict[str, Any],
    performance_metrics: Dict[str, Any],
    cost_breakdown: Dict[str, Any],
) -> Response:
    """Generate JSON report for SMS usage."""
    try:
        report_data = {
            "user_id": user_id,
            "time_range": time_range,
            "generated_at": datetime.utcnow().isoformat(),
            "usage_summary": usage_summary,
            "performance_metrics": performance_metrics,
            "cost_breakdown": cost_breakdown,
        }

        # Create response
        return Response(
            content=json.dumps(report_data, indent=2, default=str),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=sms_usage_report_{user_id}_{time_range}.json"
            },
        )

    except Exception as e:
        logger.error(f"Error generating JSON report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate JSON report")
