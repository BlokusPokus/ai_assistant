"""
SMS Analytics Service for usage tracking, cost analysis, and performance monitoring.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...database.models.users import User
from ..models.sms_models import SMSUsageLog

logger = logging.getLogger(__name__)


class SMSAnalyticsService:
    """Service for SMS usage analytics and reporting."""

    def __init__(self, db_session: AsyncSession):
        """Initialize the analytics service with a database session."""
        self.db = db_session

    async def get_user_usage_summary(
        self, user_id: int, time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get comprehensive SMS usage summary for a user.

        Args:
            user_id: User ID to get analytics for
            time_range: Time range for analysis (7d, 30d, 90d, 1y)

        Returns:
            Dictionary containing usage summary and metrics
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Build query for the specified time range
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.user_id == user_id,
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                )
            )

            result = await self.db.execute(query)
            usage_logs = result.scalars().all()

            if not usage_logs:
                return self._create_empty_usage_summary(user_id, time_range)

            # Calculate metrics
            total_messages = len(usage_logs)
            inbound_messages = len(
                [log for log in usage_logs if log.message_direction == "inbound"]
            )
            outbound_messages = len(
                [log for log in usage_logs if log.message_direction == "outbound"]
            )

            successful_messages = len([log for log in usage_logs if log.success])
            success_rate = (
                (successful_messages / total_messages * 100)
                if total_messages > 0
                else 0
            )

            # Calculate average processing time
            processing_times = [
                log.processing_time_ms for log in usage_logs if log.processing_time_ms
            ]
            avg_processing_time = (
                sum(processing_times) / len(processing_times) if processing_times else 0
            )

            # Calculate total message length
            total_length = sum(log.message_length for log in usage_logs)

            # Get usage patterns by hour
            usage_patterns = self._calculate_usage_patterns(usage_logs)

            return {
                "user_id": user_id,
                "time_range": time_range,
                "total_messages": total_messages,
                "inbound_messages": inbound_messages,
                "outbound_messages": outbound_messages,
                "success_rate": round(success_rate, 2),
                "average_processing_time_ms": round(avg_processing_time, 2),
                "total_message_length": total_length,
                "usage_patterns": usage_patterns,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting user usage summary for user {user_id}: {e}")
            raise

    async def get_user_usage_trends(
        self, user_id: int, time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get usage trends over time for a user.

        Args:
            user_id: User ID to get trends for
            time_range: Time range for analysis

        Returns:
            Dictionary containing usage trends and patterns
        """
        try:
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get daily usage counts
            daily_usage = await self._get_daily_usage_counts(
                user_id, start_date, end_date
            )

            # Calculate trends
            trend_analysis = self._analyze_usage_trends(daily_usage)

            return {
                "user_id": user_id,
                "time_range": time_range,
                "daily_usage": daily_usage,
                "trend_analysis": trend_analysis,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting user usage trends for user {user_id}: {e}")
            raise

    async def get_user_performance_metrics(
        self, user_id: int, time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a user's SMS usage.

        Args:
            user_id: User ID to get metrics for
            time_range: Time range for analysis

        Returns:
            Dictionary containing performance metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get performance data
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.user_id == user_id,
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                )
            )

            result = await self.db.execute(query)
            usage_logs = result.scalars().all()

            if not usage_logs:
                return self._create_empty_performance_metrics(user_id, time_range)

            # Calculate performance metrics
            total_messages = len(usage_logs)
            successful_messages = len([log for log in usage_logs if log.success])
            failed_messages = total_messages - successful_messages

            # Processing time metrics
            processing_times = [
                log.processing_time_ms for log in usage_logs if log.processing_time_ms
            ]
            avg_processing_time = (
                sum(processing_times) / len(processing_times) if processing_times else 0
            )
            min_processing_time = min(processing_times) if processing_times else 0
            max_processing_time = max(processing_times) if processing_times else 0

            # Error analysis
            error_messages = [log for log in usage_logs if not log.success]
            error_types = {}
            for log in error_messages:
                error_type = log.error_message or "Unknown"
                error_types[error_type] = error_types.get(error_type, 0) + 1

            return {
                "user_id": user_id,
                "time_range": time_range,
                "total_messages": total_messages,
                "successful_messages": successful_messages,
                "failed_messages": failed_messages,
                "success_rate": round((successful_messages / total_messages * 100), 2)
                if total_messages > 0
                else 0,
                "processing_time_metrics": {
                    "average_ms": round(avg_processing_time, 2),
                    "minimum_ms": min_processing_time,
                    "maximum_ms": max_processing_time,
                },
                "error_analysis": {
                    "total_errors": failed_messages,
                    "error_types": error_types,
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(
                f"Error getting user performance metrics for user {user_id}: {e}"
            )
            raise

    async def get_user_message_breakdown(
        self, user_id: int, time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get detailed message breakdown for a user.

        Args:
            user_id: User ID to get breakdown for
            time_range: Time range for analysis

        Returns:
            Dictionary containing message breakdown analysis
        """
        try:
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get message breakdown data
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.user_id == user_id,
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                )
            )

            result = await self.db.execute(query)
            usage_logs = result.scalars().all()

            if not usage_logs:
                return self._create_empty_message_breakdown(user_id, time_range)

            # Analyze message breakdown
            inbound_breakdown = self._analyze_message_direction(usage_logs, "inbound")
            outbound_breakdown = self._analyze_message_direction(usage_logs, "outbound")

            # Message length analysis
            length_analysis = self._analyze_message_lengths(usage_logs)

            return {
                "user_id": user_id,
                "time_range": time_range,
                "inbound_breakdown": inbound_breakdown,
                "outbound_breakdown": outbound_breakdown,
                "length_analysis": length_analysis,
                "total_messages": len(usage_logs),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(
                f"Error getting user message breakdown for user {user_id}: {e}"
            )
            raise

    async def get_system_performance_metrics(
        self, time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get system-wide performance metrics.

        Args:
            time_range: Time range for analysis

        Returns:
            Dictionary containing system performance metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get system-wide data
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                )
            )

            result = await self.db.execute(query)
            all_logs = result.scalars().all()

            if not all_logs:
                return self._create_empty_system_metrics(time_range)

            # Calculate system metrics
            total_messages = len(all_logs)
            successful_messages = len([log for log in all_logs if log.success])
            failed_messages = total_messages - successful_messages

            # Processing time metrics
            processing_times = [
                log.processing_time_ms for log in all_logs if log.processing_time_ms
            ]
            avg_processing_time = (
                sum(processing_times) / len(processing_times) if processing_times else 0
            )

            # User activity metrics
            unique_users = len(set(log.user_id for log in all_logs))

            # Hourly activity patterns
            hourly_patterns = self._calculate_hourly_activity_patterns(all_logs)

            return {
                "time_range": time_range,
                "total_messages": total_messages,
                "successful_messages": successful_messages,
                "failed_messages": failed_messages,
                "success_rate": round((successful_messages / total_messages * 100), 2)
                if total_messages > 0
                else 0,
                "average_processing_time_ms": round(avg_processing_time, 2),
                "unique_active_users": unique_users,
                "hourly_activity_patterns": hourly_patterns,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting system performance metrics: {e}")
            raise

    async def get_sla_compliance_status(self) -> Dict[str, Any]:
        """
        Get SLA compliance status for the SMS service.

        Returns:
            Dictionary containing SLA compliance metrics
        """
        try:
            # Define SLA thresholds
            sla_thresholds = {
                "response_time_ms": 1000,  # 1 second
                "success_rate_percent": 99.5,  # 99.5%
                "availability_percent": 99.9,  # 99.9%
            }

            # Get current metrics (last 24 hours)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=24)

            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                )
            )

            result = await self.db.execute(query)
            recent_logs = result.scalars().all()

            if not recent_logs:
                return {
                    "sla_status": "insufficient_data",
                    "compliance_percentage": 0,
                    "thresholds": sla_thresholds,
                    "current_metrics": {},
                    "violations": [],
                }

            # Calculate current metrics
            total_messages = len(recent_logs)
            successful_messages = len([log for log in recent_logs if log.success])
            success_rate = (
                (successful_messages / total_messages * 100)
                if total_messages > 0
                else 0
            )

            processing_times = [
                log.processing_time_ms for log in recent_logs if log.processing_time_ms
            ]
            avg_response_time = (
                sum(processing_times) / len(processing_times) if processing_times else 0
            )

            # Check SLA compliance
            sla_violations = []
            compliance_score = 0

            if avg_response_time > sla_thresholds["response_time_ms"]:
                sla_violations.append(
                    {
                        "metric": "response_time",
                        "threshold": sla_thresholds["response_time_ms"],
                        "current": round(avg_response_time, 2),
                        "severity": "high"
                        if avg_response_time > sla_thresholds["response_time_ms"] * 2
                        else "medium",
                    }
                )
            else:
                compliance_score += 33.33

            if success_rate < sla_thresholds["success_rate_percent"]:
                sla_violations.append(
                    {
                        "metric": "success_rate",
                        "threshold": sla_thresholds["success_rate_percent"],
                        "current": round(success_rate, 2),
                        "severity": "high"
                        if success_rate < sla_thresholds["success_rate_percent"] - 5
                        else "medium",
                    }
                )
            else:
                compliance_score += 33.33

            # Availability calculation (simplified)
            availability = 100.0  # In a real system, this would be calculated from uptime monitoring
            if availability < sla_thresholds["availability_percent"]:
                sla_violations.append(
                    {
                        "metric": "availability",
                        "threshold": sla_thresholds["availability_percent"],
                        "current": availability,
                        "severity": "high",
                    }
                )
            else:
                compliance_score += 33.33

            return {
                "sla_status": "compliant"
                if compliance_score >= 100
                else "non_compliant",
                "compliance_percentage": round(compliance_score, 2),
                "thresholds": sla_thresholds,
                "current_metrics": {
                    "response_time_ms": round(avg_response_time, 2),
                    "success_rate_percent": round(success_rate, 2),
                    "availability_percent": availability,
                },
                "violations": sla_violations,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting SLA compliance status: {e}")
            raise

    async def get_performance_trends(self, time_range: str = "30d") -> Dict[str, Any]:
        """
        Get performance trends over time.

        Args:
            time_range: Time range for analysis

        Returns:
            Dictionary containing performance trends
        """
        try:
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get daily performance data
            daily_performance = await self._get_daily_performance_data(
                start_date, end_date
            )

            # Calculate trends
            trend_analysis = self._analyze_performance_trends(daily_performance)

            return {
                "time_range": time_range,
                "daily_performance": daily_performance,
                "trend_analysis": trend_analysis,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            raise

    async def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """
        Generate performance alerts based on current metrics.

        Returns:
            List of performance alerts
        """
        try:
            alerts = []

            # Get current SLA status
            sla_status = await self.get_sla_compliance_status()

            # Generate alerts for SLA violations
            for violation in sla_status.get("violations", []):
                alerts.append(
                    {
                        "type": "sla_violation",
                        "severity": violation["severity"],
                        "metric": violation["metric"],
                        "message": f"SLA violation: {violation['metric']} is {violation['current']} (threshold: {violation['threshold']})",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actionable": True,
                        "recommendation": self._get_alert_recommendation(violation),
                    }
                )

            # Check for performance degradation
            current_metrics = await self.get_system_performance_metrics("24h")
            previous_metrics = await self.get_system_performance_metrics("48h")

            if (
                current_metrics.get("total_messages", 0) > 0
                and previous_metrics.get("total_messages", 0) > 0
            ):
                current_success_rate = current_metrics.get("success_rate", 0)
                previous_success_rate = previous_metrics.get("success_rate", 0)

                if current_success_rate < previous_success_rate - 5:  # 5% degradation
                    alerts.append(
                        {
                            "type": "performance_degradation",
                            "severity": "medium",
                            "metric": "success_rate",
                            "message": f"Performance degradation detected: success rate dropped from {previous_success_rate}% to {current_success_rate}%",
                            "timestamp": datetime.utcnow().isoformat(),
                            "actionable": True,
                            "recommendation": "Investigate recent system changes or increased load",
                        }
                    )

            return alerts

        except Exception as e:
            logger.error(f"Error generating performance alerts: {e}")
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

    def _calculate_usage_patterns(
        self, usage_logs: List[SMSUsageLog]
    ) -> Dict[str, Any]:
        """Calculate usage patterns from usage logs."""
        hourly_counts = {}
        for log in usage_logs:
            if log.created_at and hasattr(log.created_at, "hour"):
                hour = log.created_at.hour
            else:
                hour = 0
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

        # Sort by hour
        sorted_hours = sorted(hourly_counts.items())

        return {
            "hourly_distribution": dict(sorted_hours),
            "peak_hour": max(hourly_counts.items(), key=lambda x: x[1])[0]
            if hourly_counts
            else None,
            "low_activity_hour": min(hourly_counts.items(), key=lambda x: x[1])[0]
            if hourly_counts
            else None,
        }

    async def _get_daily_usage_counts(
        self, user_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily usage counts for a user."""
        daily_counts = []
        current_date = start_date.date()

        while current_date <= end_date.date():
            next_date = current_date + timedelta(days=1)

            # Count messages for this day
            query = select(func.count(SMSUsageLog.id)).where(
                and_(
                    SMSUsageLog.user_id == user_id,
                    SMSUsageLog.created_at
                    >= datetime.combine(current_date, datetime.min.time()),
                    SMSUsageLog.created_at
                    < datetime.combine(next_date, datetime.min.time()),
                )
            )

            result = await self.db.execute(query)
            count = result.scalar() or 0

            daily_counts.append(
                {"date": current_date.isoformat(), "message_count": count}
            )

            current_date = next_date

        return daily_counts

    def _analyze_usage_trends(
        self, daily_usage: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze usage trends from daily data."""
        if len(daily_usage) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0}

        # Calculate trend
        first_half = daily_usage[: len(daily_usage) // 2]
        second_half = daily_usage[len(daily_usage) // 2 :]

        first_avg = (
            sum(day["message_count"] for day in first_half) / len(first_half)
            if first_half
            else 0
        )
        second_avg = (
            sum(day["message_count"] for day in second_half) / len(second_half)
            if second_half
            else 0
        )

        if first_avg == 0:
            change_percentage = 100 if second_avg > 0 else 0
        else:
            change_percentage = ((second_avg - first_avg) / first_avg) * 100

        if change_percentage > 10:
            trend = "increasing"
        elif change_percentage < -10:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_percentage": round(change_percentage, 2),
            "first_half_average": round(first_avg, 2),
            "second_half_average": round(second_avg, 2),
        }

    def _analyze_message_direction(
        self, usage_logs: List[SMSUsageLog], direction: str
    ) -> Dict[str, Any]:
        """Analyze messages for a specific direction."""
        direction_logs = [
            log for log in usage_logs if log.message_direction == direction
        ]

        if not direction_logs:
            return {
                "total_messages": 0,
                "success_rate": 0,
                "average_length": 0,
                "average_processing_time": 0,
            }

        total = len(direction_logs)
        successful = len([log for log in direction_logs if log.success])
        success_rate = (successful / total * 100) if total > 0 else 0

        lengths = [log.message_length for log in direction_logs if log.message_length]
        avg_length = sum(lengths) / len(lengths) if lengths else 0

        processing_times = [
            log.processing_time_ms for log in direction_logs if log.processing_time_ms
        ]
        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        return {
            "total_messages": total,
            "success_rate": round(success_rate, 2),
            "average_length": round(avg_length, 2),
            "average_processing_time": round(avg_processing_time, 2),
        }

    def _analyze_message_lengths(self, usage_logs: List[SMSUsageLog]) -> Dict[str, Any]:
        """Analyze message length patterns."""
        lengths = [log.message_length for log in usage_logs if log.message_length]

        if not lengths:
            return {
                "average_length": 0,
                "short_messages": 0,
                "medium_messages": 0,
                "long_messages": 0,
            }

        avg_length = sum(lengths) / len(lengths)

        # Categorize by length
        short_messages = len([l for l in lengths if l <= 160])  # Standard SMS
        medium_messages = len([l for l in lengths if 160 < l <= 320])  # Multi-part SMS
        # Very long messages
        long_messages = len([l for l in lengths if l > 320])

        return {
            "average_length": round(avg_length, 2),
            "short_messages": short_messages,
            "medium_messages": medium_messages,
            "long_messages": long_messages,
            "total_messages": len(lengths),
        }

    def _calculate_hourly_activity_patterns(
        self, usage_logs: List[SMSUsageLog]
    ) -> Dict[str, Any]:
        """Calculate hourly activity patterns for system-wide usage."""
        hourly_counts = {}
        for log in usage_logs:
            if log.created_at and hasattr(log.created_at, "hour"):
                hour = log.created_at.hour
            else:
                hour = 0
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

        # Sort by hour
        sorted_hours = sorted(hourly_counts.items())

        return {
            "hourly_distribution": dict(sorted_hours),
            "peak_hour": max(hourly_counts.items(), key=lambda x: x[1])[0]
            if hourly_counts
            else None,
            "low_activity_hour": min(hourly_counts.items(), key=lambda x: x[1])[0]
            if hourly_counts
            else None,
            "total_activity": sum(hourly_counts.values()),
        }

    async def _get_daily_performance_data(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily performance data for the system."""
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

                daily_data.append(
                    {
                        "date": current_date.isoformat(),
                        "total_messages": total,
                        "success_rate": round(success_rate, 2),
                        "average_processing_time_ms": round(avg_processing_time, 2),
                    }
                )
            else:
                daily_data.append(
                    {
                        "date": current_date.isoformat(),
                        "total_messages": 0,
                        "success_rate": 0,
                        "average_processing_time_ms": 0,
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

        # Calculate trends for success rate and processing time
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

        # Processing time trend
        first_time_avg = (
            sum(day["average_processing_time_ms"] for day in first_half)
            / len(first_half)
            if first_half
            else 0
        )
        second_time_avg = (
            sum(day["average_processing_time_ms"] for day in second_half)
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
            "processing_time_trend": {
                "trend": "improving"
                if time_change < -5
                else "degrading"
                if time_change > 5
                else "stable",
                "change_percentage": round(time_change, 2),
            },
        }

    def _get_alert_recommendation(self, violation: Dict[str, Any]) -> str:
        """Get recommendation for an alert."""
        metric = violation["metric"]
        severity = violation["severity"]

        if metric == "response_time":
            if severity == "high":
                return "Immediate investigation required. Check system resources and database performance."
            else:
                return "Monitor system performance and consider optimization."
        elif metric == "success_rate":
            if severity == "high":
                return "Critical issue detected. Check error logs and system health immediately."
            else:
                return "Investigate recent changes and monitor error rates."
        elif metric == "availability":
            return "Check system status and infrastructure health."
        else:
            return "Review system metrics and investigate root cause."

    # Empty response creators
    def _create_empty_usage_summary(
        self, user_id: int, time_range: str
    ) -> Dict[str, Any]:
        """Create empty usage summary response."""
        return {
            "user_id": user_id,
            "time_range": time_range,
            "total_messages": 0,
            "inbound_messages": 0,
            "outbound_messages": 0,
            "success_rate": 0,
            "average_processing_time_ms": 0,
            "total_message_length": 0,
            "usage_patterns": {
                "hourly_distribution": {},
                "peak_hour": None,
                "low_activity_hour": None,
            },
            "period": {
                "start_date": self._calculate_start_date(
                    datetime.utcnow(), time_range
                ).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
        }

    def _create_empty_performance_metrics(
        self, user_id: int, time_range: str
    ) -> Dict[str, Any]:
        """Create empty performance metrics response."""
        return {
            "user_id": user_id,
            "time_range": time_range,
            "total_messages": 0,
            "successful_messages": 0,
            "failed_messages": 0,
            "success_rate": 0,
            "processing_time_metrics": {
                "average_ms": 0,
                "minimum_ms": 0,
                "maximum_ms": 0,
            },
            "error_analysis": {"total_errors": 0, "error_types": {}},
            "period": {
                "start_date": self._calculate_start_date(
                    datetime.utcnow(), time_range
                ).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
        }

    def _create_empty_message_breakdown(
        self, user_id: int, time_range: str
    ) -> Dict[str, Any]:
        """Create empty message breakdown response."""
        return {
            "user_id": user_id,
            "time_range": time_range,
            "inbound_breakdown": {
                "total_messages": 0,
                "success_rate": 0,
                "average_length": 0,
                "average_processing_time": 0,
            },
            "outbound_breakdown": {
                "total_messages": 0,
                "success_rate": 0,
                "average_length": 0,
                "average_processing_time": 0,
            },
            "length_analysis": {
                "average_length": 0,
                "short_messages": 0,
                "medium_messages": 0,
                "long_messages": 0,
            },
            "total_messages": 0,
            "period": {
                "start_date": self._calculate_start_date(
                    datetime.utcnow(), time_range
                ).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
        }

    def _create_empty_system_metrics(self, time_range: str) -> Dict[str, Any]:
        """Create empty system metrics response."""
        return {
            "time_range": time_range,
            "total_messages": 0,
            "successful_messages": 0,
            "failed_messages": 0,
            "success_rate": 0,
            "average_processing_time_ms": 0,
            "unique_active_users": 0,
            "hourly_activity_patterns": {
                "hourly_distribution": {},
                "peak_hour": None,
                "low_activity_hour": None,
                "total_activity": 0,
            },
            "period": {
                "start_date": self._calculate_start_date(
                    datetime.utcnow(), time_range
                ).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
        }
