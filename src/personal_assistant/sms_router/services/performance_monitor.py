"""
SMS Performance Monitor for real-time metrics and SLA compliance monitoring.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...monitoring import get_metrics_service
from ..models.sms_models import SMSUsageLog

logger = logging.getLogger(__name__)


class SMSPerformanceMonitor:
    """Service for SMS performance monitoring and SLA compliance."""

    def __init__(self, db_session: AsyncSession):
        """Initialize the performance monitor with a database session."""
        self.db = db_session

        # SLA thresholds
        self.sla_thresholds = {
            "response_time_ms": 1000,  # 1 second
            "success_rate_percent": 99.5,  # 99.5%
            "availability_percent": 99.9,  # 99.9%
            "error_rate_percent": 0.5,  # 0.5%
            "max_concurrent_users": 1000,  # Maximum concurrent users
            "max_daily_messages": 10000,  # Maximum daily messages
        }

        # Alert thresholds
        self.alert_thresholds = {
            "critical_response_time_ms": 2000,  # 2 seconds
            "critical_success_rate_percent": 95.0,  # 95%
            "warning_response_time_ms": 1500,  # 1.5 seconds
            "warning_success_rate_percent": 98.0,  # 98%
        }

        # Performance history cache
        self._performance_cache = {}
        self._cache_ttl = 300  # 5 minutes in seconds
        self._last_cache_update = 0

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Get real-time performance metrics.

        Returns:
            Dictionary containing current performance metrics
        """
        try:
            # Check if cache is still valid
            current_time = datetime.utcnow().timestamp()
            if (
                current_time - self._last_cache_update
            ) < self._cache_ttl and self._performance_cache:
                logger.debug("Using cached performance metrics")
                return self._performance_cache

            # Get metrics for the last hour
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=1)

            # Get recent usage data
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                )
            )

            result = await self.db.execute(query)
            recent_logs = result.scalars().all()

            if not recent_logs:
                metrics = self._create_empty_real_time_metrics()
            else:
                metrics = await self._calculate_real_time_metrics(recent_logs)

            # Update cache
            self._performance_cache = metrics
            self._last_cache_update = current_time

            # Update Prometheus metrics
            try:
                metrics_service = get_metrics_service()

                # Update SMS metrics
                if "total_messages" in metrics:
                    # Update success/failure counts
                    success_count = metrics.get("successful_messages", 0)
                    failure_count = metrics.get("failed_messages", 0)

                    if success_count > 0:
                        metrics_service.sms_messages_total.labels(
                            status="success", provider="twilio"
                        ).inc(success_count)

                    if failure_count > 0:
                        metrics_service.sms_messages_total.labels(
                            status="failure", provider="twilio"
                        ).inc(failure_count)

                # Update processing time metrics
                if "average_response_time_ms" in metrics:
                    avg_time_seconds = metrics["average_response_time_ms"] / 1000.0
                    metrics_service.sms_processing_duration_seconds.labels(
                        provider="twilio"
                    ).observe(avg_time_seconds)

                # Update success rate
                if "success_rate_percent" in metrics:
                    metrics_service.sms_success_rate.set(
                        metrics["success_rate_percent"]
                    )

                # Update queue length (if available)
                if "queue_length" in metrics:
                    metrics_service.sms_queue_length.set(metrics["queue_length"])

                # Update cost metrics (if available)
                if "total_cost" in metrics:
                    metrics_service.sms_cost_total.labels(provider="twilio").inc(
                        metrics["total_cost"]
                    )

            except Exception as metrics_error:
                logger.warning(
                    f"Failed to update Prometheus SMS metrics: {metrics_error}"
                )

            return metrics

        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return self._create_empty_real_time_metrics()

    async def get_historical_performance(
        self, time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get historical performance data.

        Args:
            time_range: Time range for analysis

        Returns:
            Dictionary containing historical performance data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get daily performance data
            daily_performance = await self._get_daily_performance_data(
                start_date, end_date
            )

            # Calculate trends and patterns
            trend_analysis = self._analyze_performance_trends(daily_performance)
            pattern_analysis = self._analyze_performance_patterns(daily_performance)

            return {
                "time_range": time_range,
                "daily_performance": daily_performance,
                "trend_analysis": trend_analysis,
                "pattern_analysis": pattern_analysis,
                "summary": {
                    "total_days": len(daily_performance),
                    "average_success_rate": self._calculate_average_success_rate(
                        daily_performance
                    ),
                    "average_response_time": self._calculate_average_response_time(
                        daily_performance
                    ),
                    "best_performance_day": self._find_best_performance_day(
                        daily_performance
                    ),
                    "worst_performance_day": self._find_worst_performance_day(
                        daily_performance
                    ),
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting historical performance: {e}")
            raise

    async def check_sla_compliance(self) -> Dict[str, Any]:
        """
        Check SLA compliance for the SMS service.

        Returns:
            Dictionary containing SLA compliance status
        """
        try:
            # Get current metrics
            current_metrics = await self.get_real_time_metrics()

            # Check each SLA metric
            sla_checks = {}
            compliance_score = 0
            total_metrics = 0

            # Response time SLA
            response_time = current_metrics.get("average_response_time_ms", 0)
            response_time_compliant = (
                response_time <= self.sla_thresholds["response_time_ms"]
            )
            sla_checks["response_time"] = {
                "metric": "response_time",
                "threshold_ms": self.sla_thresholds["response_time_ms"],
                "current_ms": response_time,
                "compliant": response_time_compliant,
                "severity": "critical"
                if response_time > self.alert_thresholds["critical_response_time_ms"]
                else "warning"
                if response_time > self.alert_thresholds["warning_response_time_ms"]
                else "normal",
            }
            if response_time_compliant:
                compliance_score += 25
            total_metrics += 1

            # Success rate SLA
            success_rate = current_metrics.get("success_rate_percent", 100)
            success_rate_compliant = (
                success_rate >= self.sla_thresholds["success_rate_percent"]
            )
            sla_checks["success_rate"] = {
                "metric": "success_rate",
                "threshold_percent": self.sla_thresholds["success_rate_percent"],
                "current_percent": success_rate,
                "compliant": success_rate_compliant,
                "severity": "critical"
                if success_rate < self.alert_thresholds["critical_success_rate_percent"]
                else "warning"
                if success_rate < self.alert_thresholds["warning_success_rate_percent"]
                else "normal",
            }
            if success_rate_compliant:
                compliance_score += 25
            total_metrics += 1

            # Availability SLA (simplified - in production this would come from uptime monitoring)
            availability = 100.0  # Assume 100% for now
            availability_compliant = (
                availability >= self.sla_thresholds["availability_percent"]
            )
            sla_checks["availability"] = {
                "metric": "availability",
                "threshold_percent": self.sla_thresholds["availability_percent"],
                "current_percent": availability,
                "compliant": availability_compliant,
                "severity": "normal",
            }
            if availability_compliant:
                compliance_score += 25
            total_metrics += 1

            # Error rate SLA
            error_rate = 100 - success_rate
            error_rate_compliant = (
                error_rate <= self.sla_thresholds["error_rate_percent"]
            )
            sla_checks["error_rate"] = {
                "metric": "error_rate",
                "threshold_percent": self.sla_thresholds["error_rate_percent"],
                "current_percent": error_rate,
                "compliant": error_rate_compliant,
                "severity": "critical"
                if error_rate
                > (100 - self.alert_thresholds["critical_success_rate_percent"])
                else "warning"
                if error_rate
                > (100 - self.alert_thresholds["warning_success_rate_percent"])
                else "normal",
            }
            if error_rate_compliant:
                compliance_score += 25
            total_metrics += 1

            # Calculate overall compliance percentage
            overall_compliance = (
                (compliance_score / total_metrics) if total_metrics > 0 else 0
            )

            return {
                "sla_status": "compliant"
                if overall_compliance >= 100
                else "non_compliant",
                "compliance_percentage": round(overall_compliance, 2),
                "overall_health": self._determine_overall_health(sla_checks),
                "sla_checks": sla_checks,
                "thresholds": self.sla_thresholds,
                "last_checked": datetime.utcnow().isoformat(),
                "period": {
                    "start_date": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error checking SLA compliance: {e}")
            raise

    async def generate_performance_alerts(self) -> List[Dict[str, Any]]:
        """
        Generate performance alerts based on current metrics.

        Returns:
            List of performance alerts
        """
        try:
            alerts = []

            # Get current SLA status
            sla_status = await self.check_sla_compliance()

            # Generate alerts for SLA violations
            for check_name, check_data in sla_status.get("sla_checks", {}).items():
                if not check_data.get("compliant", True):
                    alert = {
                        "id": f"sla_violation_{check_name}_{datetime.utcnow().timestamp()}",
                        "type": "sla_violation",
                        "severity": check_data.get("severity", "warning"),
                        "metric": check_data.get("metric"),
                        "message": f"SLA violation: {check_data['metric']} is {check_data.get('current_percent', check_data.get('current_ms', 'unknown'))} (threshold: {check_data.get('threshold_percent', check_data.get('threshold_ms', 'unknown'))})",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actionable": True,
                        "recommendation": self._get_alert_recommendation(check_data),
                        "sla_check": check_data,
                    }
                    alerts.append(alert)

            # Check for performance degradation
            current_metrics = await self.get_real_time_metrics()
            historical_metrics = await self.get_historical_performance("7d")

            if current_metrics.get("total_messages", 0) > 0:
                # Check for sudden drops in success rate
                current_success_rate = current_metrics.get("success_rate_percent", 100)
                historical_success_rate = historical_metrics.get("summary", {}).get(
                    "average_success_rate", current_success_rate
                )

                if (
                    historical_success_rate > 0
                    and current_success_rate < historical_success_rate - 5
                ):
                    alert = {
                        "id": f"performance_degradation_success_rate_{datetime.utcnow().timestamp()}",
                        "type": "performance_degradation",
                        "severity": "warning",
                        "metric": "success_rate",
                        "message": f"Performance degradation detected: success rate dropped from {historical_success_rate}% to {current_success_rate}%",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actionable": True,
                        "recommendation": "Investigate recent system changes, increased load, or external service issues",
                        "current_value": current_success_rate,
                        "historical_value": historical_success_rate,
                    }
                    alerts.append(alert)

                # Check for sudden increases in response time
                current_response_time = current_metrics.get(
                    "average_response_time_ms", 0
                )
                historical_response_time = historical_metrics.get("summary", {}).get(
                    "average_response_time", current_response_time
                )

                if (
                    historical_response_time > 0
                    and current_response_time > historical_response_time * 1.5
                ):
                    alert = {
                        "id": f"performance_degradation_response_time_{datetime.utcnow().timestamp()}",
                        "type": "performance_degradation",
                        "severity": "warning",
                        "metric": "response_time",
                        "message": f"Performance degradation detected: response time increased from {historical_response_time}ms to {current_response_time}ms",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actionable": True,
                        "recommendation": "Check system resources, database performance, and external service response times",
                        "current_value": current_response_time,
                        "historical_value": historical_response_time,
                    }
                    alerts.append(alert)

            # Check for unusual activity patterns
            activity_alerts = await self._check_activity_patterns()
            alerts.extend(activity_alerts)

            # Sort alerts by severity
            severity_order = {"critical": 3, "warning": 2, "normal": 1}
            alerts.sort(
                key=lambda x: severity_order.get(x.get("severity", "normal"), 0),
                reverse=True,
            )

            return alerts

        except Exception as e:
            logger.error(f"Error generating performance alerts: {e}")
            return []

    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system health metrics.

        Returns:
            Dictionary containing system health information
        """
        try:
            # Get real-time metrics
            real_time_metrics = await self.get_real_time_metrics()

            # Get SLA compliance
            sla_compliance = await self.check_sla_compliance()

            # Get performance alerts
            alerts = await self.generate_performance_alerts()

            # Calculate system health score
            health_score = self._calculate_system_health_score(
                real_time_metrics, sla_compliance, alerts
            )

            # Determine overall system status
            overall_status = self._determine_system_status(health_score, alerts)

            return {
                "system_status": overall_status,
                "health_score": health_score,
                "real_time_metrics": real_time_metrics,
                "sla_compliance": sla_compliance,
                "active_alerts": len(alerts),
                "critical_alerts": len(
                    [a for a in alerts if a.get("severity") == "critical"]
                ),
                "warning_alerts": len(
                    [a for a in alerts if a.get("severity") == "warning"]
                ),
                "last_updated": datetime.utcnow().isoformat(),
                "uptime": await self._get_system_uptime(),
                "performance_summary": {
                    "current_load": real_time_metrics.get("active_users", 0),
                    "peak_load_today": real_time_metrics.get("peak_users_today", 0),
                    "average_response_time": real_time_metrics.get(
                        "average_response_time_ms", 0
                    ),
                    "success_rate": real_time_metrics.get("success_rate_percent", 100),
                },
            }

        except Exception as e:
            logger.error(f"Error getting system health metrics: {e}")
            raise

    async def get_performance_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get performance optimization recommendations.

        Returns:
            List of performance recommendations
        """
        try:
            recommendations = []

            # Get current metrics
            current_metrics = await self.get_real_time_metrics()
            await self.check_sla_compliance()

            # Check response time
            response_time = current_metrics.get("average_response_time_ms", 0)
            if response_time > self.sla_thresholds["response_time_ms"]:
                recommendations.append(
                    {
                        "category": "performance",
                        "priority": "high",
                        "title": "Optimize Response Time",
                        "description": f"Current response time ({response_time}ms) exceeds SLA threshold ({self.sla_thresholds['response_time_ms']}ms)",
                        "actions": [
                            "Check database query performance",
                            "Review external service response times",
                            "Consider implementing caching",
                            "Optimize message processing logic",
                        ],
                        "estimated_impact": "high",
                        "effort_required": "medium",
                    }
                )

            # Check success rate
            success_rate = current_metrics.get("success_rate_percent", 100)
            if success_rate < self.sla_thresholds["success_rate_percent"]:
                recommendations.append(
                    {
                        "category": "reliability",
                        "priority": "high",
                        "title": "Improve Success Rate",
                        "description": f"Current success rate ({success_rate}%) below SLA threshold ({self.sla_thresholds['success_rate_percent']}%)",
                        "actions": [
                            "Review error logs for common failures",
                            "Check Twilio service status",
                            "Verify phone number configurations",
                            "Implement retry logic for failed messages",
                        ],
                        "estimated_impact": "high",
                        "effort_required": "medium",
                    }
                )

            # Check for high error rates
            error_rate = 100 - success_rate
            if error_rate > 5:  # More than 5% error rate
                recommendations.append(
                    {
                        "category": "reliability",
                        "priority": "medium",
                        "title": "Reduce Error Rate",
                        "description": f"High error rate ({error_rate}%) detected",
                        "actions": [
                            "Analyze error patterns",
                            "Implement better error handling",
                            "Add input validation",
                            "Review external service integrations",
                        ],
                        "estimated_impact": "medium",
                        "effort_required": "low",
                    }
                )

            # Check for usage patterns
            active_users = current_metrics.get("active_users", 0)
            if active_users > self.sla_thresholds["max_concurrent_users"] * 0.8:
                recommendations.append(
                    {
                        "category": "scalability",
                        "priority": "medium",
                        "title": "Plan for Scaling",
                        "description": f"High concurrent user count ({active_users}) approaching limits",
                        "actions": [
                            "Monitor user growth trends",
                            "Consider horizontal scaling",
                            "Implement rate limiting",
                            "Review resource allocation",
                        ],
                        "estimated_impact": "medium",
                        "effort_required": "high",
                    }
                )

            # Add general recommendations
            recommendations.extend(
                [
                    {
                        "category": "monitoring",
                        "priority": "low",
                        "title": "Enhanced Monitoring",
                        "description": "Implement comprehensive monitoring and alerting",
                        "actions": [
                            "Set up performance dashboards",
                            "Configure automated alerts",
                            "Implement log aggregation",
                            "Add business metrics tracking",
                        ],
                        "estimated_impact": "medium",
                        "effort_required": "medium",
                    },
                    {
                        "category": "optimization",
                        "priority": "low",
                        "title": "Performance Optimization",
                        "description": "Continuous performance improvement",
                        "actions": [
                            "Regular performance reviews",
                            "Database query optimization",
                            "Code profiling and optimization",
                            "Infrastructure tuning",
                        ],
                        "estimated_impact": "low",
                        "effort_required": "medium",
                    },
                ]
            )

            # Sort by priority
            priority_order = {"high": 3, "medium": 2, "low": 1}
            recommendations.sort(
                key=lambda x: priority_order.get(x.get("priority", "low"), 0),
                reverse=True,
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error getting performance recommendations: {e}")
            return []

    # Helper methods
    def _calculate_start_date(self, end_date: datetime, time_range: str) -> datetime:
        """Calculate start date based on time range."""
        if time_range == "7d":
            return end_date - timedelta(days=7)
        elif time_range == "30d":
            return end_date - timedelta(days=30)
        elif time_range == "90d":
            return end_date - timedelta(days=90)
        elif time_range == "1y":
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)  # Default to 30 days

    async def _calculate_real_time_metrics(
        self, recent_logs: List[SMSUsageLog]
    ) -> Dict[str, Any]:
        """Calculate real-time metrics from recent logs."""
        try:
            total_messages = len(recent_logs)
            successful_messages = len([log for log in recent_logs if log.success])
            failed_messages = total_messages - successful_messages

            # Calculate success rate
            success_rate = (
                (successful_messages / total_messages * 100)
                if total_messages > 0
                else 100
            )

            # Calculate response time metrics
            processing_times = [
                log.processing_time_ms for log in recent_logs if log.processing_time_ms
            ]
            avg_response_time = (
                sum(processing_times) / len(processing_times) if processing_times else 0
            )
            min_response_time = min(processing_times) if processing_times else 0
            max_response_time = max(processing_times) if processing_times else 0

            # Calculate user activity
            unique_users = len(set(log.user_id for log in recent_logs))

            # Calculate hourly activity
            hourly_counts = {}
            for log in recent_logs:
                if log.created_at and hasattr(log.created_at, "hour"):
                    hour = log.created_at.hour
                else:
                    hour = 0
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

            peak_hour = (
                max(hourly_counts.items(), key=lambda x: x[1])[0]
                if hourly_counts
                else None
            )
            peak_users = max(hourly_counts.values()) if hourly_counts else 0

            # Get today's peak users
            today_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_logs = [
                log
                for log in recent_logs
                if log.created_at and log.created_at >= today_start
            ]
            today_hourly_counts = {}
            for log in today_logs:
                if log.created_at and hasattr(log.created_at, "hour"):
                    hour = log.created_at.hour
                else:
                    hour = 0
                today_hourly_counts[hour] = today_hourly_counts.get(hour, 0) + 1
            peak_users_today = (
                max(today_hourly_counts.values()) if today_hourly_counts else 0
            )

            return {
                "total_messages": total_messages,
                "successful_messages": successful_messages,
                "failed_messages": failed_messages,
                "success_rate_percent": round(success_rate, 2),
                "error_rate_percent": round(100 - success_rate, 2),
                "average_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": min_response_time,
                "max_response_time_ms": max_response_time,
                "active_users": unique_users,
                "peak_users": peak_users,
                "peak_users_today": peak_users_today,
                "peak_hour": peak_hour,
                "hourly_activity": hourly_counts,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error calculating real-time metrics: {e}")
            return self._create_empty_real_time_metrics()

    async def _get_daily_performance_data(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily performance data for the specified period."""
        daily_data = []
        current_date = start_date.date()

        while current_date <= end_date.date():
            next_date = current_date + timedelta(days=1)

            # Get data for this day
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.created_at
                    >= datetime.combine(current_date, datetime.min.time()),
                    SMSUsageLog.created_at
                    < datetime.combine(next_date, datetime.min.time()),
                )
            )

            result = await self.db.execute(query)
            day_logs = result.scalars().all()

            if day_logs:
                total = len(day_logs)
                successful = len([log for log in day_logs if log.success])
                success_rate = (successful / total * 100) if total > 0 else 0

                processing_times = [
                    log.processing_time_ms for log in day_logs if log.processing_time_ms
                ]
                avg_processing_time = (
                    sum(processing_times) / len(processing_times)
                    if processing_times
                    else 0
                )

                unique_users = len(set(log.user_id for log in day_logs))

                daily_data.append(
                    {
                        "date": current_date.isoformat(),
                        "total_messages": total,
                        "successful_messages": successful,
                        "failed_messages": total - successful,
                        "success_rate": round(success_rate, 2),
                        "average_response_time_ms": round(avg_processing_time, 2),
                        "unique_users": unique_users,
                    }
                )
            else:
                daily_data.append(
                    {
                        "date": current_date.isoformat(),
                        "total_messages": 0,
                        "successful_messages": 0,
                        "failed_messages": 0,
                        "success_rate": 0,
                        "average_response_time_ms": 0,
                        "unique_users": 0,
                    }
                )

            current_date = next_date

        return daily_data

    def _analyze_performance_trends(
        self, daily_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze performance trends from daily data."""
        if len(daily_performance) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0}

        # Calculate trends for success rate and response time
        first_half = daily_performance[: len(daily_performance) // 2]
        second_half = daily_performance[len(daily_performance) // 2 :]

        # Success rate trend
        first_success_avg = (
            sum(day["success_rate"] for day in first_half) / len(first_half)
            if first_half
            else 0
        )
        second_success_avg = (
            sum(day["success_rate"] for day in second_half) / len(second_half)
            if second_half
            else 0
        )

        if first_success_avg == 0:
            success_change = 100 if second_success_avg > 0 else 0
        else:
            success_change = (
                (second_success_avg - first_success_avg) / first_success_avg
            ) * 100

        # Response time trend
        first_time_avg = (
            sum(day["average_response_time_ms"] for day in first_half) / len(first_half)
            if first_half
            else 0
        )
        second_time_avg = (
            sum(day["average_response_time_ms"] for day in second_half)
            / len(second_half)
            if second_half
            else 0
        )

        if first_time_avg == 0:
            time_change = 100 if second_time_avg > 0 else 0
        else:
            time_change = ((second_time_avg - first_time_avg) / first_time_avg) * 100

        return {
            "success_rate_trend": {
                "trend": "improving"
                if success_change > 5
                else "degrading"
                if success_change < -5
                else "stable",
                "change_percentage": round(success_change, 2),
            },
            "response_time_trend": {
                "trend": "improving"
                if time_change < -5
                else "degrading"
                if time_change > 5
                else "stable",
                "change_percentage": round(time_change, 2),
            },
        }

    def _analyze_performance_patterns(
        self, daily_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze performance patterns from daily data."""
        if not daily_performance:
            return {"patterns": "insufficient_data"}

        # Find best and worst performing days
        best_day = max(daily_performance, key=lambda x: x.get("success_rate", 0))
        worst_day = min(daily_performance, key=lambda x: x.get("success_rate", 0))

        # Calculate weekly patterns (simplified)
        weekly_averages = {}
        for day in daily_performance:
            date_obj = datetime.fromisoformat(day["date"]).date()
            weekday = date_obj.weekday()
            if weekday not in weekly_averages:
                weekly_averages[weekday] = {"success_rates": [], "response_times": []}
            weekly_averages[weekday]["success_rates"].append(day["success_rate"])
            weekly_averages[weekday]["response_times"].append(
                day["average_response_time_ms"]
            )

        # Calculate weekday averages
        weekday_performance = {}
        for weekday, data in weekly_averages.items():
            weekday_performance[weekday] = {
                "avg_success_rate": sum(data["success_rates"])
                / len(data["success_rates"])
                if data["success_rates"]
                else 0,
                "avg_response_time": sum(data["response_times"])
                / len(data["response_times"])
                if data["response_times"]
                else 0,
            }

        return {
            "best_performing_day": {
                "date": best_day["date"],
                "success_rate": best_day["success_rate"],
                "response_time": best_day["average_response_time_ms"],
            },
            "worst_performing_day": {
                "date": worst_day["date"],
                "success_rate": worst_day["success_rate"],
                "response_time": worst_day["average_response_time_ms"],
            },
            "weekly_patterns": weekday_performance,
        }

    async def _check_activity_patterns(self) -> List[Dict[str, Any]]:
        """Check for unusual activity patterns."""
        alerts = []

        try:
            # Get current metrics
            current_metrics = await self.get_real_time_metrics()

            # Check for unusual message volume
            total_messages = current_metrics.get("total_messages", 0)
            # More than 10% of daily limit in 1 hour
            if total_messages > self.sla_thresholds["max_daily_messages"] * 0.1:
                alerts.append(
                    {
                        "id": f"high_activity_{datetime.utcnow().timestamp()}",
                        "type": "high_activity",
                        "severity": "warning",
                        "metric": "message_volume",
                        "message": f"High message volume detected: {total_messages} messages in the last hour",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actionable": True,
                        "recommendation": "Monitor for potential abuse or system issues",
                    }
                )

            # Check for unusual user activity
            active_users = current_metrics.get("active_users", 0)
            if active_users > self.sla_thresholds["max_concurrent_users"] * 0.8:
                alerts.append(
                    {
                        "id": f"high_concurrent_users_{datetime.utcnow().timestamp()}",
                        "type": "high_concurrent_users",
                        "severity": "warning",
                        "metric": "concurrent_users",
                        "message": f"High concurrent user count: {active_users} users",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actionable": True,
                        "recommendation": "Monitor system performance and consider scaling",
                    }
                )

        except Exception as e:
            logger.error(f"Error checking activity patterns: {e}")

        return alerts

    def _get_alert_recommendation(self, check_data: Dict[str, Any]) -> str:
        """Get recommendation for an alert."""
        metric = check_data.get("metric")
        severity = check_data.get("severity", "normal")

        if metric == "response_time":
            if severity == "critical":
                return "Immediate investigation required. Check system resources, database performance, and external service response times."
            else:
                return "Monitor system performance and consider optimization. Check for increased load or resource constraints."
        elif metric == "success_rate":
            if severity == "critical":
                return "Critical issue detected. Check error logs, Twilio service status, and system health immediately."
            else:
                return "Investigate recent changes and monitor error rates. Review phone number configurations and external integrations."
        elif metric == "availability":
            return "Check system status and infrastructure health. Verify all services are running and accessible."
        elif metric == "error_rate":
            return "Review error patterns and implement better error handling. Check for configuration issues or external service problems."
        else:
            return "Review system metrics and investigate root cause. Check logs and monitoring data for patterns."

    def _determine_overall_health(self, sla_checks: Dict[str, Any]) -> str:
        """Determine overall health based on SLA checks."""
        critical_count = sum(
            1 for check in sla_checks.values() if check.get("severity") == "critical"
        )
        warning_count = sum(
            1 for check in sla_checks.values() if check.get("severity") == "warning"
        )

        if critical_count > 0:
            return "critical"
        elif warning_count > 0:
            return "warning"
        else:
            return "healthy"

    def _calculate_system_health_score(
        self,
        real_time_metrics: Dict[str, Any],
        sla_compliance: Dict[str, Any],
        alerts: List[Dict[str, Any]],
    ) -> float:
        """Calculate overall system health score."""
        try:
            score = 100.0

            # Deduct points for SLA violations
            sla_checks = sla_compliance.get("sla_checks", {})
            for check in sla_checks.values():
                if not check.get("compliant", True):
                    severity = check.get("severity", "normal")
                    if severity == "critical":
                        score -= 25
                    elif severity == "warning":
                        score -= 10

            # Deduct points for active alerts
            critical_alerts = len(
                [a for a in alerts if a.get("severity") == "critical"]
            )
            warning_alerts = len([a for a in alerts if a.get("severity") == "warning"])

            score -= critical_alerts * 15
            score -= warning_alerts * 5

            # Ensure score doesn't go below 0
            return max(0.0, score)

        except Exception as e:
            logger.error(f"Error calculating system health score: {e}")
            return 50.0  # Return neutral score on error

    def _determine_system_status(
        self, health_score: float, alerts: List[Dict[str, Any]]
    ) -> str:
        """Determine overall system status."""
        if health_score >= 90:
            return "healthy"
        elif health_score >= 70:
            return "degraded"
        elif health_score >= 50:
            return "unhealthy"
        else:
            return "critical"

    async def _get_system_uptime(self) -> Dict[str, Any]:
        """Get system uptime information (simplified)."""
        try:
            # In a real system, this would come from uptime monitoring
            # For now, we'll return a simplified version
            return {
                "current_uptime": "99.9%",
                "last_restart": "2024-01-01T00:00:00Z",
                "total_uptime": "365 days",
            }
        except Exception as e:
            logger.error(f"Error getting system uptime: {e}")
            return {
                "current_uptime": "unknown",
                "last_restart": "unknown",
                "total_uptime": "unknown",
            }

    def _calculate_average_success_rate(
        self, daily_performance: List[Dict[str, Any]]
    ) -> float:
        """Calculate average success rate from daily performance data."""
        if not daily_performance:
            return 0.0

        total_rate = sum(day.get("success_rate", 0) for day in daily_performance)
        return round(total_rate / len(daily_performance), 2)

    def _calculate_average_response_time(
        self, daily_performance: List[Dict[str, Any]]
    ) -> float:
        """Calculate average response time from daily performance data."""
        if not daily_performance:
            return 0.0

        total_time = sum(
            day.get("average_response_time_ms", 0) for day in daily_performance
        )
        return round(total_time / len(daily_performance), 2)

    def _find_best_performance_day(
        self, daily_performance: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find the best performing day."""
        if not daily_performance:
            return None

        best_day = max(daily_performance, key=lambda x: x.get("success_rate", 0))
        return {
            "date": best_day["date"],
            "success_rate": best_day["success_rate"],
            "response_time": best_day["average_response_time_ms"],
        }

    def _find_worst_performance_day(
        self, daily_performance: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find the worst performing day."""
        if not daily_performance:
            return None

        worst_day = min(daily_performance, key=lambda x: x.get("success_rate", 0))
        return {
            "date": worst_day["date"],
            "success_rate": worst_day["success_rate"],
            "response_time": worst_day["average_response_time_ms"],
        }

    # Empty response creators
    def _create_empty_real_time_metrics(self) -> Dict[str, Any]:
        """Create empty real-time metrics response."""
        return {
            "total_messages": 0,
            "successful_messages": 0,
            "failed_messages": 0,
            "success_rate_percent": 100,
            "error_rate_percent": 0,
            "average_response_time_ms": 0,
            "min_response_time_ms": 0,
            "max_response_time_ms": 0,
            "active_users": 0,
            "peak_users": 0,
            "peak_users_today": 0,
            "peak_hour": None,
            "hourly_activity": {},
            "last_updated": datetime.utcnow().isoformat(),
        }
