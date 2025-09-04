"""
Integration tests for Analytics API endpoints.

Tests the complete analytics API functionality including authentication, data retrieval, and error handling.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.main import app
from personal_assistant.sms_router.services.analytics import SMSAnalyticsService
from personal_assistant.sms_router.services.cost_calculator import SMSCostCalculator
from personal_assistant.sms_router.services.performance_monitor import SMSPerformanceMonitor


class TestAnalyticsAPI:
    """Test cases for Analytics API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock authentication token."""
        return "mock_jwt_token_for_testing"

    @pytest.fixture
    def mock_user_data(self):
        """Create mock user data for testing."""
        return {
            "user_id": 1,
            "email": "test@example.com",
            "full_name": "Test User",
            "permissions": ["read_sms_analytics", "view_sms_performance"]
        }

    @pytest.fixture
    def mock_analytics_data(self):
        """Create mock analytics data for testing."""
        return {
            "user_id": 1,
            "time_range": "30d",
            "total_messages": 150,
            "inbound_messages": 80,
            "outbound_messages": 70,
            "success_rate": 0.95,
            "average_processing_time_ms": 120.5,
            "total_cost_usd": 12.50,
            "cost_breakdown": {
                "inbound": 8.00,
                "outbound": 4.50
            },
            "usage_patterns": {
                "peak_hours": "9:00-17:00",
                "daily_average": 5.0
            },
            "performance_metrics": {
                "response_time_p95": 200,
                "error_rate": 0.05
            }
        }

    @pytest.fixture
    def mock_cost_data(self):
        """Create mock cost data for testing."""
        return {
            "user_id": 1,
            "time_range": "30d",
            "total_cost_usd": 12.50,
            "inbound_cost_usd": 8.00,
            "outbound_cost_usd": 4.50,
            "cost_per_message": 0.083,
            "estimated_monthly_cost": 15.00,
            "cost_optimization_tips": [
                "Consider bulk messaging for cost savings",
                "Optimize message length to reduce costs"
            ],
            "usage_trends": {
                "daily_costs": [0.5, 0.6, 0.4, 0.7],
                "weekly_costs": [3.2, 3.8, 3.1, 3.4]
            }
        }

    @pytest.fixture
    def mock_system_analytics(self):
        """Create mock system analytics data for testing."""
        return {
            "time_range": "30d",
            "system_performance": {
                "total_messages": 1500,
                "success_rate": 0.97,
                "average_response_time_ms": 135.2,
                "error_rate": 0.03
            },
            "system_costs": {
                "total_system_cost": 125.00,
                "average_cost_per_user": 12.50,
                "cost_distribution": {
                    "user_1": 12.50,
                    "user_2": 15.75
                }
            },
            "performance_trends": {
                "response_time_trend": [120, 125, 130, 135],
                "success_rate_trend": [0.95, 0.96, 0.97, 0.97],
                "volume_trend": [45, 48, 52, 55]
            }
        }

    @pytest.fixture
    def mock_performance_metrics(self):
        """Create mock performance metrics data for testing."""
        return {
            "system_health": "healthy",
            "average_response_time_ms": 135.2,
            "success_rate": 0.97,
            "error_rate": 0.03,
            "sla_compliance": {
                "response_time_compliance": True,
                "success_rate_compliance": True,
                "availability_compliance": True
            },
            "performance_trends": {
                "response_time_trend": [120, 125, 130, 135],
                "success_rate_trend": [0.95, 0.96, 0.97, 0.97]
            },
            "alert_thresholds": {
                "response_time_threshold": 500,
                "success_rate_threshold": 0.95
            }
        }

    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch('personal_assistant.auth.decorators.require_permission')
    @patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService')
    def test_get_user_sms_analytics_success(
        self, 
        mock_analytics_service, 
        mock_require_permission, 
        client, 
        mock_analytics_data
    ):
        """Test successful retrieval of user SMS analytics."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the analytics service
        mock_service_instance = MagicMock()
        mock_service_instance.get_user_usage_summary.return_value = mock_analytics_data
        mock_analytics_service.return_value = mock_service_instance
        
        # Mock the database dependency
        with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            response = client.get(
                "/api/v1/analytics/me/sms-analytics?time_range=30d",
                headers={"Authorization": "Bearer mock_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == mock_analytics_data["user_id"]
            assert data["time_range"] == mock_analytics_data["time_range"]
            assert data["total_messages"] == mock_analytics_data["total_messages"]

    @patch('personal_assistant.auth.decorators.require_permission')
    @patch('personal_assistant.sms_router.services.cost_calculator.SMSCostCalculator')
    def test_get_user_sms_costs_success(
        self, 
        mock_cost_calculator, 
        mock_require_permission, 
        client, 
        mock_cost_data
    ):
        """Test successful retrieval of user SMS costs."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the cost calculator service
        mock_service_instance = MagicMock()
        mock_service_instance.calculate_user_costs.return_value = mock_cost_data
        mock_cost_calculator.return_value = mock_service_instance
        
        # Mock the database dependency
        with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            response = client.get(
                "/api/v1/analytics/me/sms-costs?time_range=30d",
                headers={"Authorization": "Bearer mock_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == mock_cost_data["user_id"]
            assert data["total_cost_usd"] == mock_cost_data["total_cost_usd"]

    @patch('personal_assistant.auth.decorators.require_permission')
    def test_get_user_sms_analytics_invalid_time_range(
        self, 
        mock_require_permission, 
        client
    ):
        """Test user SMS analytics with invalid time range."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        response = client.get(
            "/api/v1/analytics/me/sms-analytics?time_range=invalid",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid time_range" in data["detail"]

    @patch('personal_assistant.auth.decorators.require_permission')
    @patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService')
    def test_get_system_sms_analytics_success(
        self, 
        mock_analytics_service, 
        mock_require_permission, 
        client, 
        mock_system_analytics
    ):
        """Test successful retrieval of system SMS analytics."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the analytics service
        mock_service_instance = MagicMock()
        mock_service_instance.get_system_performance_metrics.return_value = mock_system_analytics["system_performance"]
        mock_analytics_service.return_value = mock_service_instance
        
        # Mock the cost calculator service
        with patch('personal_assistant.sms_router.services.cost_calculator.SMSCostCalculator') as mock_cost_calc:
            mock_cost_instance = MagicMock()
            mock_cost_instance.get_system_cost_summary.return_value = mock_system_analytics["system_costs"]
            mock_cost_calc.return_value = mock_cost_instance
            
            # Mock the database dependency
            with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                response = client.get(
                    "/api/v1/analytics/admin/sms-analytics/system?time_range=30d",
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["time_range"] == mock_system_analytics["time_range"]

    @patch('personal_assistant.auth.decorators.require_permission')
    @patch('personal_assistant.sms_router.services.performance_monitor.SMSPerformanceMonitor')
    def test_get_sms_performance_metrics_success(
        self, 
        mock_performance_monitor, 
        mock_require_permission, 
        client, 
        mock_performance_metrics
    ):
        """Test successful retrieval of SMS performance metrics."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the performance monitor service
        mock_service_instance = MagicMock()
        mock_service_instance.get_real_time_metrics.return_value = mock_performance_metrics
        mock_performance_monitor.return_value = mock_service_instance
        
        # Mock the database dependency
        with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            response = client.get(
                "/api/v1/analytics/admin/sms-performance",
                headers={"Authorization": "Bearer mock_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["system_health"] == mock_performance_metrics["system_health"]

    def test_get_user_sms_analytics_unauthorized(self, client):
        """Test user SMS analytics without authentication."""
        response = client.get("/api/v1/analytics/me/sms-analytics")
        assert response.status_code == 401

    def test_get_system_sms_analytics_unauthorized(self, client):
        """Test system SMS analytics without authentication."""
        response = client.get("/api/v1/analytics/admin/sms-analytics/system")
        assert response.status_code == 401

    @patch('personal_assistant.auth.decorators.require_permission')
    def test_download_user_usage_report_csv(
        self, 
        mock_require_permission, 
        client
    ):
        """Test downloading user usage report in CSV format."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the analytics service
        with patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService') as mock_analytics:
            mock_service_instance = MagicMock()
            mock_service_instance.generate_usage_report.return_value = b"csv,data,here"
            mock_analytics.return_value = mock_service_instance
            
            # Mock the database dependency
            with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                response = client.get(
                    "/api/v1/analytics/me/sms-usage-report?format=csv&time_range=30d",
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/csv"
                assert response.headers["content-disposition"] == "attachment; filename=sms_usage_report.csv"

    @patch('personal_assistant.auth.decorators.require_permission')
    def test_download_user_usage_report_json(
        self, 
        mock_require_permission, 
        client
    ):
        """Test downloading user usage report in JSON format."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the analytics service
        with patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService') as mock_analytics:
            mock_service_instance = MagicMock()
            mock_service_instance.generate_usage_report.return_value = json.dumps({"data": "test"}).encode()
            mock_analytics.return_value = mock_service_instance
            
            # Mock the database dependency
            with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                response = client.get(
                    "/api/v1/analytics/me/sms-usage-report?format=json&time_range=30d",
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                assert response.status_code == 200
                assert response.headers["content-type"] == "application/json"
                assert response.headers["content-disposition"] == "attachment; filename=sms_usage_report.json"

    def test_download_user_usage_report_invalid_format(self, client):
        """Test downloading user usage report with invalid format."""
        response = client.get(
            "/api/v1/analytics/me/sms-usage-report?format=invalid&time_range=30d",
            headers={"Authorization": "Bearer mock_token"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid format" in data["detail"]

    @patch('personal_assistant.auth.decorators.require_permission')
    def test_get_users_sms_analytics_success(
        self, 
        mock_require_permission, 
        client
    ):
        """Test successful retrieval of users SMS analytics."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the analytics service
        with patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService') as mock_analytics:
            mock_service_instance = MagicMock()
            mock_service_instance.get_users_comparison.return_value = {
                "users": [
                    {"user_id": 1, "total_messages": 150, "total_cost": 12.50},
                    {"user_id": 2, "total_messages": 200, "total_cost": 18.75}
                ],
                "comparison_metrics": {
                    "average_messages_per_user": 175,
                    "average_cost_per_user": 15.63
                }
            }
            mock_analytics.return_value = mock_service_instance
            
            # Mock the database dependency
            with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                response = client.get(
                    "/api/v1/analytics/admin/sms-analytics/users?time_range=30d",
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "users" in data
                assert "comparison_metrics" in data

    @patch('personal_assistant.auth.decorators.require_permission')
    def test_get_sms_performance_historical_success(
        self, 
        mock_require_permission, 
        client
    ):
        """Test successful retrieval of historical SMS performance."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the performance monitor service
        with patch('personal_assistant.sms_router.services.performance_monitor.SMSPerformanceMonitor') as mock_monitor:
            mock_service_instance = MagicMock()
            mock_service_instance.get_historical_performance.return_value = {
                "time_range": "30d",
                "performance_data": [
                    {"date": "2024-01-01", "response_time": 120, "success_rate": 0.95},
                    {"date": "2024-01-02", "response_time": 125, "success_rate": 0.96}
                ],
                "trends": {
                    "response_time_trend": "increasing",
                    "success_rate_trend": "stable"
                }
            }
            mock_monitor.return_value = mock_service_instance
            
            # Mock the database dependency
            with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                response = client.get(
                    "/api/v1/analytics/admin/sms-performance/historical?time_range=30d",
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "time_range" in data
                assert "performance_data" in data
                assert "trends" in data

    @patch('personal_assistant.auth.decorators.require_permission')
    def test_get_sms_performance_alerts_success(
        self, 
        mock_require_permission, 
        client
    ):
        """Test successful retrieval of SMS performance alerts."""
        # Mock the permission decorator
        mock_require_permission.return_value = lambda func: func
        
        # Mock the performance monitor service
        with patch('personal_assistant.sms_router.services.performance_monitor.SMSPerformanceMonitor') as mock_monitor:
            mock_service_instance = MagicMock()
            mock_service_instance.generate_performance_alerts.return_value = [
                {
                    "type": "performance",
                    "severity": "warning",
                    "message": "Response time above threshold",
                    "timestamp": "2024-01-01T10:00:00Z"
                },
                {
                    "type": "cost",
                    "severity": "info",
                    "message": "Cost optimization opportunity detected",
                    "timestamp": "2024-01-01T09:00:00Z"
                }
            ]
            mock_monitor.return_value = mock_service_instance
            
            # Mock the database dependency
            with patch('apps.fastapi_app.routes.analytics.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                response = client.get(
                    "/api/v1/analytics/admin/sms-performance/alerts",
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) == 2
                assert data[0]["type"] == "performance"
                assert data[1]["type"] == "cost"


if __name__ == "__main__":
    pytest.main([__file__])
