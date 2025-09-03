"""
SMS Cost Calculator for Twilio pricing integration and cost analysis.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models.users import User
from ..models.sms_models import SMSUsageLog

logger = logging.getLogger(__name__)


class SMSCostCalculator:
    """Service for SMS cost calculation and analysis."""

    def __init__(self, db_session: AsyncSession):
        """Initialize the cost calculator with a database session."""
        self.db = db_session
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        # Default Twilio pricing (US rates as fallback)
        self.default_pricing = {
            "inbound": 0.0075,  # $0.0075 per message
            "outbound": 0.0079,  # $0.0079 per message
            # $0.15 per message (varies by country)
            "international_outbound": 0.15,
            "mms": 0.02,  # $0.02 per MMS
            "long_code_monthly": 1.00,  # $1.00 per month per long code
            "toll_free_monthly": 2.00,  # $2.00 per month per toll-free number
        }

        # Cache for pricing data
        self._pricing_cache = {}
        self._cache_ttl = 24 * 60 * 60  # 24 hours in seconds
        self._last_cache_update = 0

    async def calculate_user_costs(
        self, user_id: int, time_range: str = "30d"
    ) -> Dict[str, float]:
        """
        Calculate SMS costs for a specific user.

        Args:
            user_id: User ID to calculate costs for
            time_range: Time range for cost calculation

        Returns:
            Dictionary containing cost breakdown
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get usage data for the user
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
                return self._create_empty_cost_breakdown()

            # Get current pricing
            pricing = await self.get_twilio_pricing()

            # Calculate costs
            total_cost = 0.0
            inbound_cost = 0.0
            outbound_cost = 0.0
            mms_cost = 0.0

            for log in usage_logs:
                message_cost = 0.0

                if log.message_direction == "inbound":
                    message_cost = pricing["inbound"]
                    inbound_cost += message_cost
                elif log.message_direction == "outbound":
                    # Check if it's international
                    if self._is_international_number(log.phone_number):
                        message_cost = pricing["international_outbound"]
                    else:
                        message_cost = pricing["outbound"]
                    outbound_cost += message_cost

                # Add MMS cost if applicable (simplified detection)
                if log.message_length > 160:  # Assume MMS for long messages
                    mms_cost += pricing["mms"]

                total_cost += message_cost

            # Add monthly number costs
            # Assuming one number per user
            monthly_number_cost = pricing["long_code_monthly"]

            return {
                "total_cost_usd": round(total_cost, 4),
                "inbound_cost_usd": round(inbound_cost, 4),
                "outbound_cost_usd": round(outbound_cost, 4),
                "mms_cost_usd": round(mms_cost, 4),
                "monthly_number_cost_usd": monthly_number_cost,
                "total_with_monthly_fees": round(total_cost + monthly_number_cost, 4),
                "cost_per_message": round(total_cost / len(usage_logs), 4)
                if usage_logs
                else 0,
                "message_count": len(usage_logs),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error calculating user costs for user {user_id}: {e}")
            raise

    async def get_twilio_pricing(self) -> Dict[str, float]:
        """
        Get current Twilio pricing information.

        Returns:
            Dictionary containing current pricing rates
        """
        try:
            # Check if cache is still valid
            current_time = datetime.utcnow().timestamp()
            if (
                current_time - self._last_cache_update
            ) < self._cache_ttl and self._pricing_cache:
                logger.debug("Using cached Twilio pricing data")
                return self._pricing_cache

            # Try to fetch from Twilio API
            pricing = await self._fetch_twilio_pricing()

            if pricing:
                self._pricing_cache = pricing
                self._last_cache_update = current_time
                logger.info("Successfully updated Twilio pricing cache")
                return pricing
            else:
                # Use default pricing if API call fails
                logger.warning("Using default Twilio pricing due to API failure")
                return self.default_pricing

        except Exception as e:
            logger.error(f"Error getting Twilio pricing: {e}")
            return self.default_pricing

    async def estimate_monthly_costs(self, user_id: int) -> float:
        """
        Estimate monthly SMS costs for a user based on current usage patterns.

        Args:
            user_id: User ID to estimate costs for

        Returns:
            Estimated monthly cost in USD
        """
        try:
            # Get current month usage
            current_month_cost = await self.calculate_user_costs(user_id, "30d")

            # Get previous month usage for trend analysis
            previous_month_cost = await self.calculate_user_costs(user_id, "60d")

            if not current_month_cost.get("message_count", 0):
                return 0.0

            # Calculate trend
            current_avg = current_month_cost["cost_per_message"]
            previous_avg = previous_month_cost.get("cost_per_message", current_avg)

            # Estimate based on trend (simplified)
            if previous_avg > 0:
                trend_factor = current_avg / previous_avg
            else:
                trend_factor = 1.0

            # Project to full month
            days_in_month = 30
            current_days = min(
                30, (datetime.utcnow() - (datetime.utcnow() - timedelta(days=30))).days
            )

            if current_days > 0:
                daily_cost = current_month_cost["total_cost_usd"] / current_days
                estimated_monthly = daily_cost * days_in_month * trend_factor
            else:
                estimated_monthly = current_month_cost["total_cost_usd"] * trend_factor

            # Add monthly number fees
            pricing = await self.get_twilio_pricing()
            monthly_fees = pricing["long_code_monthly"]

            return round(estimated_monthly + monthly_fees, 4)

        except Exception as e:
            logger.error(f"Error estimating monthly costs for user {user_id}: {e}")
            return 0.0

    async def get_cost_breakdown(self, user_id: int) -> Dict[str, Any]:
        """
        Get detailed cost breakdown for a user.

        Args:
            user_id: User ID to get breakdown for

        Returns:
            Dictionary containing detailed cost analysis
        """
        try:
            # Get costs for different time periods
            costs_7d = await self.calculate_user_costs(user_id, "7d")
            costs_30d = await self.calculate_user_costs(user_id, "30d")
            costs_90d = await self.calculate_user_costs(user_id, "90d")

            # Get usage trends
            usage_trends = await self._get_usage_trends_for_cost_analysis(user_id)

            # Calculate cost trends
            cost_trends = self._calculate_cost_trends([costs_7d, costs_30d, costs_90d])

            # Get optimization recommendations
            optimization_tips = await self._get_cost_optimization_tips(
                user_id, costs_30d
            )

            return {
                "user_id": user_id,
                "current_period_costs": costs_30d,
                "historical_costs": {
                    "7_days": costs_7d,
                    "30_days": costs_30d,
                    "90_days": costs_90d,
                },
                "cost_trends": cost_trends,
                "usage_trends": usage_trends,
                "optimization_tips": optimization_tips,
                "estimated_monthly_cost": await self.estimate_monthly_costs(user_id),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting cost breakdown for user {user_id}: {e}")
            raise

    async def get_cost_trends(self, user_id: int) -> Dict[str, Any]:
        """
        Get cost trends over time for a user.

        Args:
            user_id: User ID to get trends for

        Returns:
            Dictionary containing cost trend analysis
        """
        try:
            # Get daily cost data for the last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            daily_costs = []
            current_date = start_date.date()

            while current_date <= end_date.date():
                next_date = current_date + timedelta(days=1)

                # Calculate cost for this day
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(next_date, datetime.min.time())

                query = select(SMSUsageLog).where(
                    and_(
                        SMSUsageLog.user_id == user_id,
                        SMSUsageLog.created_at >= day_start,
                        SMSUsageLog.created_at < day_end,
                    )
                )

                result = await self.db.execute(query)
                day_logs = result.scalars().all()

                if day_logs:
                    day_cost = await self._calculate_day_cost(day_logs)
                    daily_costs.append(
                        {
                            "date": current_date.isoformat(),
                            "cost_usd": day_cost,
                            "message_count": len(day_logs),
                        }
                    )
                else:
                    daily_costs.append(
                        {
                            "date": current_date.isoformat(),
                            "cost_usd": 0.0,
                            "message_count": 0,
                        }
                    )

                current_date = next_date

            # Analyze trends
            trend_analysis = self._analyze_cost_trends(daily_costs)

            return {
                "user_id": user_id,
                "daily_costs": daily_costs,
                "trend_analysis": trend_analysis,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting cost trends for user {user_id}: {e}")
            raise

    async def get_cost_optimization_tips(self, user_id: int) -> List[str]:
        """
        Get cost optimization recommendations for a user.

        Args:
            user_id: User ID to get tips for

        Returns:
            List of optimization recommendations
        """
        try:
            tips = []

            # Get current usage patterns
            usage_summary = await self._get_usage_summary_for_optimization(user_id)
            cost_breakdown = await self.calculate_user_costs(user_id, "30d")

            # Analyze usage patterns and provide tips
            if usage_summary.get("total_messages", 0) == 0:
                tips.append(
                    "No SMS usage detected. Consider testing the service to ensure it's working properly."
                )
                return tips

            # Check for high outbound usage
            outbound_ratio = usage_summary.get(
                "outbound_messages", 0
            ) / usage_summary.get("total_messages", 1)
            if outbound_ratio > 0.8:
                tips.append(
                    "High outbound message ratio detected. Consider implementing inbound-only features to reduce costs."
                )

            # Check for long messages
            avg_length = usage_summary.get(
                "total_message_length", 0
            ) / usage_summary.get("total_messages", 1)
            if avg_length > 160:
                tips.append(
                    "Long messages detected. Consider breaking messages into shorter segments to optimize delivery."
                )

            # Check for international messages
            international_count = await self._count_international_messages(user_id)
            if international_count > 0:
                tips.append(
                    f"{international_count} international messages detected. International SMS costs are significantly higher."
                )

            # Check for MMS usage
            mms_count = await self._count_mms_messages(user_id)
            if mms_count > 0:
                tips.append(
                    f"{mms_count} MMS messages detected. Consider using text-only messages when possible to reduce costs."
                )

            # Check for error rates
            success_rate = usage_summary.get("success_rate", 100)
            if success_rate < 95:
                tips.append(
                    f"Low success rate ({success_rate}%). Investigate failed messages to avoid unnecessary costs."
                )

            # Check for usage patterns
            usage_patterns = usage_summary.get("usage_patterns", {})
            peak_hour = usage_patterns.get("peak_hour")
            if peak_hour is not None:
                tips.append(
                    f"Peak usage detected at {peak_hour}:00. Consider implementing rate limiting during peak hours."
                )

            # Add general optimization tips
            tips.extend(
                [
                    "Monitor your usage regularly to identify cost drivers.",
                    "Consider implementing message queuing for non-urgent communications.",
                    "Use webhooks to track delivery status and avoid duplicate messages.",
                    "Implement message templates to reduce message length and improve delivery rates.",
                ]
            )

            return tips

        except Exception as e:
            logger.error(
                f"Error getting cost optimization tips for user {user_id}: {e}"
            )
            return ["Unable to generate optimization tips at this time."]

    async def get_system_cost_summary(self, time_range: str = "30d") -> Dict[str, Any]:
        """
        Get system-wide cost summary.

        Args:
            time_range: Time range for cost analysis

        Returns:
            Dictionary containing system cost summary
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)

            # Get all usage data for the period
            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                )
            )

            result = await self.db.execute(query)
            all_logs = result.scalars().all()

            if not all_logs:
                return self._create_empty_system_cost_summary(time_range)

            # Get pricing
            pricing = await self.get_twilio_pricing()

            # Calculate system-wide costs
            total_cost = 0.0
            inbound_cost = 0.0
            outbound_cost = 0.0
            mms_cost = 0.0
            international_cost = 0.0

            user_costs = {}

            for log in all_logs:
                message_cost = 0.0

                if log.message_direction == "inbound":
                    message_cost = pricing["inbound"]
                    inbound_cost += message_cost
                elif log.message_direction == "outbound":
                    if self._is_international_number(log.phone_number):
                        message_cost = pricing["international_outbound"]
                        international_cost += message_cost
                    else:
                        message_cost = pricing["outbound"]
                    outbound_cost += message_cost

                # Add MMS cost if applicable
                if log.message_length > 160:
                    mms_cost += pricing["mms"]

                total_cost += message_cost

                # Track per-user costs
                if log.user_id not in user_costs:
                    user_costs[log.user_id] = 0.0
                user_costs[log.user_id] += message_cost

            # Calculate per-user averages
            unique_users = len(user_costs)
            avg_cost_per_user = total_cost / unique_users if unique_users > 0 else 0

            # Get top cost users
            top_cost_users = sorted(
                user_costs.items(), key=lambda x: x[1], reverse=True
            )[:5]

            return {
                "time_range": time_range,
                "total_cost_usd": round(total_cost, 4),
                "inbound_cost_usd": round(inbound_cost, 4),
                "outbound_cost_usd": round(outbound_cost, 4),
                "mms_cost_usd": round(mms_cost, 4),
                "international_cost_usd": round(international_cost, 4),
                "total_messages": len(all_logs),
                "unique_users": unique_users,
                "average_cost_per_user": round(avg_cost_per_user, 4),
                "top_cost_users": [
                    {"user_id": user_id, "cost_usd": round(cost, 4)}
                    for user_id, cost in top_cost_users
                ],
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting system cost summary: {e}")
            raise

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

    async def _fetch_twilio_pricing(self) -> Optional[Dict[str, float]]:
        """Fetch current pricing from Twilio API."""
        try:
            if not self.twilio_account_sid or not self.twilio_auth_token:
                logger.warning(
                    "Twilio credentials not configured, using default pricing"
                )
                return None

            # Note: Twilio doesn't have a public pricing API, so we'll use default rates
            # In a production environment, you might want to implement a pricing service
            # that periodically updates rates based on your Twilio account information

            logger.info("Using default Twilio pricing (no public API available)")
            return self.default_pricing

        except Exception as e:
            logger.error(f"Error fetching Twilio pricing: {e}")
            return None

    def _is_international_number(self, phone_number: str) -> bool:
        """Check if a phone number is international (simplified)."""
        if not phone_number:
            return False

        # Remove all non-digit characters
        clean_number = "".join(filter(str.isdigit, phone_number))

        # Check if it starts with country code (simplified logic)
        if clean_number.startswith("1") and len(clean_number) == 11:  # US/Canada
            return False
        elif len(clean_number) > 10:  # Likely international
            return True

        return False

    async def _calculate_day_cost(self, day_logs: List[SMSUsageLog]) -> float:
        """Calculate cost for a specific day's logs."""
        try:
            pricing = await self.get_twilio_pricing()
            total_cost = 0.0

            for log in day_logs:
                if log.message_direction == "inbound":
                    total_cost += pricing["inbound"]
                elif log.message_direction == "outbound":
                    if self._is_international_number(log.phone_number):
                        total_cost += pricing["international_outbound"]
                    else:
                        total_cost += pricing["outbound"]

                # Add MMS cost if applicable
                if log.message_length > 160:
                    total_cost += pricing["mms"]

            return round(total_cost, 4)

        except Exception as e:
            logger.error(f"Error calculating day cost: {e}")
            return 0.0

    async def _get_usage_trends_for_cost_analysis(self, user_id: int) -> Dict[str, Any]:
        """Get usage trends for cost analysis."""
        try:
            # Get usage for different periods
            end_date = datetime.utcnow()
            periods = {
                "7d": end_date - timedelta(days=7),
                "30d": end_date - timedelta(days=30),
                "90d": end_date - timedelta(days=90),
            }

            trends = {}
            for period_name, start_date in periods.items():
                query = select(func.count(SMSUsageLog.id)).where(
                    and_(
                        SMSUsageLog.user_id == user_id,
                        SMSUsageLog.created_at >= start_date,
                        SMSUsageLog.created_at <= end_date,
                    )
                )

                result = await self.db.execute(query)
                count = result.scalar() or 0
                trends[period_name] = count

            return trends

        except Exception as e:
            logger.error(f"Error getting usage trends for cost analysis: {e}")
            return {}

    def _calculate_cost_trends(self, cost_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate cost trends from multiple periods."""
        if len(cost_data) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0}

        # Calculate trend based on cost per message
        current_cpm = cost_data[0].get("cost_per_message", 0)
        previous_cpm = (
            cost_data[1].get("cost_per_message", 0)
            if len(cost_data) > 1
            else current_cpm
        )

        if previous_cpm == 0:
            change_percentage = 100 if current_cpm > 0 else 0
        else:
            change_percentage = ((current_cpm - previous_cpm) / previous_cpm) * 100

        if change_percentage > 10:
            trend = "increasing"
        elif change_percentage < -10:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_percentage": round(change_percentage, 2),
            "current_cost_per_message": current_cpm,
            "previous_cost_per_message": previous_cpm,
        }

    def _analyze_cost_trends(self, daily_costs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cost trends from daily data."""
        if len(daily_costs) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0}

        # Calculate trend
        first_half = daily_costs[: len(daily_costs) // 2]
        second_half = daily_costs[len(daily_costs) // 2 :]

        first_avg = (
            sum(day["cost_usd"] for day in first_half) / len(first_half)
            if first_half
            else 0
        )
        second_avg = (
            sum(day["cost_usd"] for day in second_half) / len(second_half)
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
            "first_half_average": round(first_avg, 4),
            "second_half_average": round(second_avg, 4),
        }

    async def _get_cost_optimization_tips(
        self, user_id: int, cost_data: Dict[str, Any]
    ) -> List[str]:
        """Get cost optimization tips based on cost data."""
        tips = []

        # Check for high costs
        total_cost = cost_data.get("total_cost_usd", 0)
        if total_cost > 10:  # High cost threshold
            tips.append(
                "High SMS costs detected. Consider implementing usage limits and monitoring."
            )

        # Check for high outbound costs
        outbound_cost = cost_data.get("outbound_cost_usd", 0)
        if outbound_cost > total_cost * 0.8:
            tips.append(
                "High outbound message costs. Consider implementing inbound-only features."
            )

        # Check for MMS costs
        mms_cost = cost_data.get("mms_cost_usd", 0)
        if mms_cost > 0:
            tips.append(
                "MMS messages detected. Consider using text-only messages when possible."
            )

        return tips

    async def _get_usage_summary_for_optimization(self, user_id: int) -> Dict[str, Any]:
        """Get usage summary for optimization analysis."""
        try:
            # Get usage for last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

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
                return {}

            total_messages = len(usage_logs)
            inbound_messages = len(
                [log for log in usage_logs if log.message_direction == "inbound"]
            )
            outbound_messages = len(
                [log for log in usage_logs if log.message_direction == "outbound"]
            )
            successful_messages = len([log for log in usage_logs if log.success])
            total_length = sum(log.message_length for log in usage_logs)

            # Calculate usage patterns
            hourly_counts = {}
            for log in usage_logs:
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

            return {
                "total_messages": total_messages,
                "inbound_messages": inbound_messages,
                "outbound_messages": outbound_messages,
                "success_rate": (successful_messages / total_messages * 100)
                if total_messages > 0
                else 0,
                "total_message_length": total_length,
                "usage_patterns": {"peak_hour": peak_hour},
            }

        except Exception as e:
            logger.error(f"Error getting usage summary for optimization: {e}")
            return {}

    async def _count_international_messages(self, user_id: int) -> int:
        """Count international messages for a user."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.user_id == user_id,
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                    SMSUsageLog.message_direction == "outbound",
                )
            )

            result = await self.db.execute(query)
            outbound_logs = result.scalars().all()

            international_count = 0
            for log in outbound_logs:
                if self._is_international_number(log.phone_number):
                    international_count += 1

            return international_count

        except Exception as e:
            logger.error(f"Error counting international messages: {e}")
            return 0

    async def _count_mms_messages(self, user_id: int) -> int:
        """Count MMS messages for a user."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            query = select(SMSUsageLog).where(
                and_(
                    SMSUsageLog.user_id == user_id,
                    SMSUsageLog.created_at >= start_date,
                    SMSUsageLog.created_at <= end_date,
                    SMSUsageLog.message_length > 160,
                )
            )

            result = await self.db.execute(query)
            mms_logs = result.scalars().all()

            return len(mms_logs)

        except Exception as e:
            logger.error(f"Error counting MMS messages: {e}")
            return 0

    # Empty response creators
    def _create_empty_cost_breakdown(self) -> Dict[str, float]:
        """Create empty cost breakdown response."""
        return {
            "total_cost_usd": 0.0,
            "inbound_cost_usd": 0.0,
            "outbound_cost_usd": 0.0,
            "mms_cost_usd": 0.0,
            "monthly_number_cost_usd": 0.0,
            "total_with_monthly_fees": 0.0,
            "cost_per_message": 0.0,
            "message_count": 0,
            "period": {
                "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
        }

    def _create_empty_system_cost_summary(self, time_range: str) -> Dict[str, Any]:
        """Create empty system cost summary response."""
        return {
            "time_range": time_range,
            "total_cost_usd": 0.0,
            "inbound_cost_usd": 0.0,
            "outbound_cost_usd": 0.0,
            "mms_cost_usd": 0.0,
            "international_cost_usd": 0.0,
            "total_messages": 0,
            "unique_users": 0,
            "average_cost_per_user": 0.0,
            "top_cost_users": [],
            "period": {
                "start_date": self._calculate_start_date(
                    datetime.utcnow(), time_range
                ).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
        }
