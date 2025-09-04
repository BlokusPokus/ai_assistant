"""
Unit tests for SMS Analytics Service.

Tests the SMSAnalyticsService, SMSCostCalculator, and SMSPerformanceMonitor classes.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.sms_router.services.analytics import SMSAnalyticsService
from personal_assistant.sms_router.services.cost_calculator import SMSCostCalculator
from personal_assistant.sms_router.services.performance_monitor import SMSPerformanceMonitor
from personal_assistant.sms_router.models.sms_models import SMSUsageLog


class TestSMSAnalyticsService:
    """Test cases for SMSAnalyticsService."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def analytics_service(self, mock_db_session):
        """Create an SMSAnalyticsService instance with mock session."""
        return SMSAnalyticsService(mock_db_session)

    @pytest.mark.asyncio
    async def test_init(self, mock_db_session):
        """Test service initialization."""
        service = SMSAnalyticsService(mock_db_session)
        assert service.db == mock_db_session

    @pytest.mark.asyncio
    async def test_get_user_usage_summary(self, analytics_service, mock_db_session):
        """Test getting user usage summary."""
        # Mock query results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(message_direction="inbound", success=True, message_length=160),
            MagicMock(message_direction="outbound", success=True, message_length=140),
            MagicMock(message_direction="inbound", success=False, message_length=160),
        ]
        
        mock_db_session.execute.return_value = mock_result
        
        result = await analytics_service.get_user_usage_summary(1, "30d")
        
        assert result["user_id"] == 1
        assert result["time_range"] == "30d"
        assert result["total_messages"] == 3
        assert result["inbound_messages"] == 2
        assert result["outbound_messages"] == 1
        assert result["success_rate"] == pytest.approx(0.67, 0.01)
        assert result["total_cost_usd"] >= 0

    @pytest.mark.asyncio
    async def test_get_user_usage_trends(self, analytics_service, mock_db_session):
        """Test getting user usage trends."""
        # Mock query results for daily trends
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(date=datetime.now().date(), count=5),
            MagicMock(date=(datetime.now() - timedelta(days=1)).date(), count=3),
        ]
        
        mock_db_session.execute.return_value = mock_result
        
        result = await analytics_service.get_user_usage_trends(1, "7d")
        
        assert result["user_id"] == 1
        assert result["time_range"] == "7d"
        assert "daily_trends" in result
        assert "peak_usage_day" in result
        assert "usage_pattern" in result

    @pytest.mark.asyncio
    async def test_get_user_performance_metrics(self, analytics_service, mock_db_session):
        """Test getting user performance metrics."""
        # Mock query results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(processing_time_ms=100, success=True),
            MagicMock(processing_time_ms=150, success=True),
            MagicMock(processing_time_ms=200, success=False),
        ]
        
        mock_db_session.execute.return_value = mock_result
        
        result = await analytics_service.get_user_performance_metrics(1, "30d")
        
        assert result["user_id"] == 1
        assert result["time_range"] == "30d"
        assert result["success_rate"] == pytest.approx(0.67, 0.01)
        assert result["average_processing_time_ms"] == pytest.approx(150, 0.01)
        assert "performance_score" in result

    @pytest.mark.asyncio
    async def test_get_user_message_breakdown(self, analytics_service, mock_db_session):
        """Test getting user message breakdown."""
        # Mock query results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(message_direction="inbound", count=10),
            MagicMock(message_direction="outbound", count=15),
        ]
        
        mock_db_session.execute.return_value = mock_result
        
        result = await analytics_service.get_user_message_breakdown(1, "30d")
        
        assert result["user_id"] == 1
        assert result["time_range"] == "30d"
        assert result["inbound_count"] == 10
        assert result["outbound_count"] == 15
        assert result["total_messages"] == 25

    @pytest.mark.asyncio
    async def test_get_system_performance_metrics(self, analytics_service, mock_db_session):
        """Test getting system performance metrics."""
        # Mock query results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(processing_time_ms=120, success=True),
            MagicMock(processing_time_ms=180, success=True),
        ]
        
        mock_db_session.execute.return_value = mock_result
        
        result = await analytics_service.get_system_performance_metrics("30d")
        
        assert result["time_range"] == "30d"
        assert result["total_messages"] == 2
        assert result["success_rate"] == 1.0
        assert result["average_processing_time_ms"] == pytest.approx(150, 0.01)

    @pytest.mark.asyncio
    async def test_get_sla_compliance_status(self, analytics_service, mock_db_session):
        """Test getting SLA compliance status."""
        result = await analytics_service.get_sla_compliance_status()
        
        assert "overall_compliance" in result
        assert "response_time_compliance" in result
        assert "success_rate_compliance" in result
        assert "availability_compliance" in result

    @pytest.mark.asyncio
    async def test_get_performance_trends(self, analytics_service, mock_db_session):
        """Test getting performance trends."""
        result = await analytics_service.get_performance_trends("30d")
        
        assert "time_range" in result
        assert "response_time_trend" in result
        assert "success_rate_trend" in result
        assert "volume_trend" in result

    @pytest.mark.asyncio
    async def test_get_performance_alerts(self, analytics_service, mock_db_session):
        """Test getting performance alerts."""
        result = await analytics_service.get_performance_alerts()
        
        assert isinstance(result, list)
        # Check that all alerts have required fields
        for alert in result:
            assert "type" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "timestamp" in alert


class TestSMSCostCalculator:
    """Test cases for SMSCostCalculator."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def cost_calculator(self, mock_db_session):
        """Create an SMSCostCalculator instance with mock session."""
        return SMSCostCalculator(mock_db_session)

    @pytest.mark.asyncio
    async def test_init(self, mock_db_session):
        """Test calculator initialization."""
        calculator = SMSCostCalculator(mock_db_session)
        assert calculator.db == mock_db_session
        assert "US" in calculator.default_pricing
        assert "CA" in calculator.default_pricing

    @pytest.mark.asyncio
    async def test_calculate_user_costs(self, cost_calculator, mock_db_session):
        """Test calculating user costs."""
        # Mock query results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(message_direction="inbound", message_length=160, country_code="US"),
            MagicMock(message_direction="outbound", message_length=140, country_code="US"),
        ]
        
        mock_db_session.execute.return_value = mock_result
        
        result = await cost_calculator.calculate_user_costs(1, "30d")
        
        assert result["total_cost"] >= 0
        assert result["inbound_cost"] >= 0
        assert result["outbound_cost"] >= 0
        assert result["cost_per_message"] >= 0

    @pytest.mark.asyncio
    async def test_get_twilio_pricing(self, cost_calculator):
        """Test getting Twilio pricing."""
        result = await cost_calculator.get_twilio_pricing()
        
        assert "US" in result
        assert "CA" in result
        assert result["US"]["inbound"] > 0
        assert result["US"]["outbound"] > 0

    @pytest.mark.asyncio
    async def test_estimate_monthly_costs(self, cost_calculator, mock_db_session):
        """Test estimating monthly costs."""
        # Mock query results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(message_direction="inbound", message_length=160),
            MagicMock(message_direction="outbound", message_length=140),
        ]
        
        mock_db_session.execute.return_value = mock_result
        
        result = await cost_calculator.estimate_monthly_costs(1)
        
        assert result >= 0

    @pytest.mark.asyncio
    async def test_get_cost_breakdown(self, cost_calculator, mock_db_session):
        """Test getting cost breakdown."""
        result = await cost_calculator.get_cost_breakdown(1)
        
        assert "total_cost" in result
        assert "cost_by_direction" in result
        assert "cost_by_country" in result
        assert "cost_by_length" in result

    @pytest.mark.asyncio
    async def test_get_cost_trends(self, cost_calculator, mock_db_session):
        """Test getting cost trends."""
        result = await cost_calculator.get_cost_trends(1)
        
        assert "daily_costs" in result
        assert "weekly_costs" in result
        assert "monthly_costs" in result
        assert "trend_direction" in result

    @pytest.mark.asyncio
    async def test_get_cost_optimization_tips(self, cost_calculator):
        """Test getting cost optimization tips."""
        result = await cost_calculator.get_cost_optimization_tips(1)
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Check that all tips are strings
        for tip in result:
            assert isinstance(tip, str)

    @pytest.mark.asyncio
    async def test_get_system_cost_summary(self, cost_calculator, mock_db_session):
        """Test getting system cost summary."""
        result = await cost_calculator.get_system_cost_summary("30d")
        
        assert "total_system_cost" in result
        assert "cost_by_user" in result
        assert "average_cost_per_user" in result
        assert "cost_distribution" in result


class TestSMSPerformanceMonitor:
    """Test cases for SMSPerformanceMonitor."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def performance_monitor(self, mock_db_session):
        """Create an SMSPerformanceMonitor instance with mock session."""
        return SMSPerformanceMonitor(mock_db_session)

    @pytest.mark.asyncio
    async def test_init(self, mock_db_session):
        """Test monitor initialization."""
        monitor = SMSPerformanceMonitor(mock_db_session)
        assert monitor.db == mock_db_session
        assert "response_time_threshold" in monitor.sla_thresholds
        assert "success_rate_threshold" in monitor.sla_thresholds

    @pytest.mark.asyncio
    async def test_get_real_time_metrics(self, performance_monitor, mock_db_session):
        """Test getting real-time metrics."""
        result = await performance_monitor.get_real_time_metrics()
        
        assert "active_connections" in result
        assert "current_throughput" in result
        assert "system_load" in result
        assert "last_updated" in result

    @pytest.mark.asyncio
    async def test_get_historical_performance(self, performance_monitor, mock_db_session):
        """Test getting historical performance."""
        result = await performance_monitor.get_historical_performance("30d")
        
        assert "time_range" in result
        assert "performance_data" in result
        assert "trends" in result
        assert "anomalies" in result

    @pytest.mark.asyncio
    async def test_check_sla_compliance(self, performance_monitor, mock_db_session):
        """Test checking SLA compliance."""
        result = await performance_monitor.check_sla_compliance()
        
        assert "overall_compliance" in result
        assert "response_time_compliance" in result
        assert "success_rate_compliance" in result
        assert "availability_compliance" in result

    @pytest.mark.asyncio
    async def test_generate_performance_alerts(self, performance_monitor, mock_db_session):
        """Test generating performance alerts."""
        result = await performance_monitor.generate_performance_alerts()
        
        assert isinstance(result, list)
        # Check that all alerts have required fields
        for alert in result:
            assert "type" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "timestamp" in alert

    @pytest.mark.asyncio
    async def test_get_system_health_metrics(self, performance_monitor, mock_db_session):
        """Test getting system health metrics."""
        result = await performance_monitor.get_system_health_metrics()
        
        assert "overall_health" in result
        assert "cpu_usage" in result
        assert "memory_usage" in result
        assert "disk_usage" in result
        assert "network_status" in result

    @pytest.mark.asyncio
    async def test_get_performance_recommendations(self, performance_monitor):
        """Test getting performance recommendations."""
        result = await performance_monitor.get_performance_recommendations()
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Check that all recommendations are strings
        for rec in result:
            assert isinstance(rec, str)


if __name__ == "__main__":
    pytest.main([__file__])
