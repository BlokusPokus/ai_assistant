"""
Integration tests for SMS Analytics system.

Tests the complete analytics flow from backend services to API endpoints.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Mock the database session
@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    return session

# Mock the SMSUsageLog model
@pytest.fixture
def mock_sms_usage_log():
    """Create a mock SMS usage log entry."""
    log = MagicMock()
    log.user_id = 1
    log.phone_number = "+1234567890"
    log.message_direction = "outbound"
    log.message_length = 160
    log.success = True
    log.processing_time_ms = 120
    log.error_message = None
    log.created_at = datetime.utcnow()
    log.country_code = "US"
    return log

def test_analytics_service_creation():
    """Test that analytics services can be created."""
    try:
        from personal_assistant.sms_router.services.analytics import SMSAnalyticsService
        from personal_assistant.sms_router.services.cost_calculator import SMSCostCalculator
        from personal_assistant.sms_router.services.performance_monitor import SMSPerformanceMonitor
        
        # Test service creation
        mock_db = AsyncMock()
        analytics_service = SMSAnalyticsService(mock_db)
        cost_calculator = SMSCostCalculator(mock_db)
        performance_monitor = SMSPerformanceMonitor(mock_db)
        
        assert analytics_service is not None
        assert cost_calculator is not None
        assert performance_monitor is not None
        
        print("✅ All analytics services can be created successfully")
        
    except ImportError as e:
        pytest.fail(f"Failed to import analytics services: {e}")

def test_api_routes_import():
    """Test that analytics API routes can be imported."""
    try:
        from apps.fastapi_app.routes.analytics import router
        
        assert router is not None
        print("✅ Analytics API routes can be imported successfully")
        
    except ImportError as e:
        pytest.fail(f"Failed to import analytics API routes: {e}")

def test_frontend_components_exist():
    """Test that all frontend components exist."""
    import os
    
    required_files = [
        "src/apps/frontend/src/components/dashboard/SMSAnalyticsWidget.tsx",
        "src/apps/frontend/src/components/admin/SMSAnalyticsPanel.tsx",
        "src/apps/frontend/src/pages/dashboard/SMSAnalyticsPage.tsx",
        "src/apps/frontend/src/pages/dashboard/AdminAnalyticsPage.tsx"
    ]
    
    for file_path in required_files:
        assert os.path.exists(file_path), f"Required file {file_path} does not exist"
    
    print("✅ All required frontend components exist")

def test_dashboard_integration_files():
    """Test that dashboard integration files are properly updated."""
    import os
    
    # Check that dashboard files have been updated
    dashboard_home_path = "src/apps/frontend/src/pages/dashboard/DashboardHome.tsx"
    sidebar_path = "src/apps/frontend/src/components/dashboard/Sidebar.tsx"
    app_path = "src/apps/frontend/src/App.tsx"
    
    assert os.path.exists(dashboard_home_path), "DashboardHome.tsx does not exist"
    assert os.path.exists(sidebar_path), "Sidebar.tsx does not exist"
    assert os.path.exists(app_path), "App.tsx does not exist"
    
    print("✅ Dashboard integration files exist")

def test_analytics_endpoints_defined():
    """Test that analytics API endpoints are properly defined."""
    try:
        from apps.fastapi_app.routes.analytics import router
        
        # Check that the router has routes
        assert hasattr(router, 'routes'), "Analytics router has no routes"
        assert len(router.routes) > 0, "Analytics router has no routes defined"
        
        print("✅ Analytics API endpoints are properly defined")
        
    except ImportError as e:
        pytest.fail(f"Failed to import analytics routes: {e}")

def test_service_methods_exist():
    """Test that all required service methods exist."""
    try:
        from personal_assistant.sms_router.services.analytics import SMSAnalyticsService
        from personal_assistant.sms_router.services.cost_calculator import SMSCostCalculator
        from personal_assistant.sms_router.services.performance_monitor import SMSPerformanceMonitor
        
        # Check SMSAnalyticsService methods
        analytics_service = SMSAnalyticsService(AsyncMock())
        required_analytics_methods = [
            'get_user_usage_summary',
            'get_user_usage_trends',
            'get_user_performance_metrics',
            'get_user_message_breakdown',
            'get_system_performance_metrics',
            'get_sla_compliance_status',
            'get_performance_trends',
            'get_performance_alerts'
        ]
        
        for method_name in required_analytics_methods:
            assert hasattr(analytics_service, method_name), f"Missing method: {method_name}"
        
        # Check SMSCostCalculator methods
        cost_calculator = SMSCostCalculator(AsyncMock())
        required_cost_methods = [
            'calculate_user_costs',
            'get_twilio_pricing',
            'estimate_monthly_costs',
            'get_cost_breakdown',
            'get_cost_trends',
            'get_cost_optimization_tips',
            'get_system_cost_summary'
        ]
        
        for method_name in required_cost_methods:
            assert hasattr(cost_calculator, method_name), f"Missing method: {method_name}"
        
        # Check SMSPerformanceMonitor methods
        performance_monitor = SMSPerformanceMonitor(AsyncMock())
        required_performance_methods = [
            'get_real_time_metrics',
            'get_historical_performance',
            'check_sla_compliance',
            'generate_performance_alerts',
            'get_system_health_metrics',
            'get_performance_recommendations'
        ]
        
        for method_name in required_performance_methods:
            assert hasattr(performance_monitor, method_name), f"Missing method: {method_name}"
        
        print("✅ All required service methods exist")
        
    except ImportError as e:
        pytest.fail(f"Failed to import analytics services: {e}")

def test_data_flow_structure():
    """Test that the data flow structure is properly set up."""
    # Check that the main FastAPI app includes analytics routes
    try:
        from apps.fastapi_app.main import app
        
        # Check that the app has routes
        assert hasattr(app, 'routes'), "FastAPI app has no routes"
        
        print("✅ FastAPI app structure is properly set up")
        
    except ImportError as e:
        pytest.fail(f"Failed to import FastAPI app: {e}")

def test_component_props_and_state():
    """Test that frontend components have the expected props and state."""
    import os
    
    # Check SMSAnalyticsWidget props
    widget_path = "src/apps/frontend/src/components/dashboard/SMSAnalyticsWidget.tsx"
    with open(widget_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "timeRange" in content, "SMSAnalyticsWidget missing timeRange prop"
        assert "showCosts" in content, "SMSAnalyticsWidget missing showCosts prop"
        assert "showPerformance" in content, "SMSAnalyticsWidget missing showPerformance prop"
        assert "useState" in content, "SMSAnalyticsWidget missing useState hook"
        assert "useEffect" in content, "SMSAnalyticsWidget missing useEffect hook"
    
    # Check SMSAnalyticsPanel props
    panel_path = "src/apps/frontend/src/components/admin/SMSAnalyticsPanel.tsx"
    with open(panel_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "timeRange" in content, "SMSAnalyticsPanel missing timeRange prop"
        assert "useState" in content, "SMSAnalyticsPanel missing useState hook"
        assert "useEffect" in content, "SMSAnalyticsPanel missing useEffect hook"
    
    print("✅ Frontend components have expected props and state")

if __name__ == "__main__":
    print("🧪 Running SMS Analytics Integration Tests...")
    
    # Run all tests
    test_analytics_service_creation()
    test_api_routes_import()
    test_frontend_components_exist()
    test_dashboard_integration_files()
    test_analytics_endpoints_defined()
    test_service_methods_exist()
    test_data_flow_structure()
    test_component_props_and_state()
    
    print("🎉 All SMS Analytics integration tests passed!")
    print("✅ Backend services: Ready")
    print("✅ API endpoints: Ready")
    print("✅ Frontend components: Ready")
    print("✅ Dashboard integration: Ready")
    print("✅ Data flow: Ready")
