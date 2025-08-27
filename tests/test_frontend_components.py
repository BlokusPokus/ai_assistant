"""
Simple tests for frontend components.

Tests that the frontend component files exist and have the expected structure.
"""

import pytest
import os

def test_sms_analytics_widget_file_exists():
    """Test that SMSAnalyticsWidget file exists."""
    file_path = "src/apps/frontend/src/components/dashboard/SMSAnalyticsWidget.tsx"
    assert os.path.exists(file_path), f"File {file_path} does not exist"
    print("✅ SMSAnalyticsWidget.tsx file exists")

def test_sms_analytics_panel_file_exists():
    """Test that SMSAnalyticsPanel file exists."""
    file_path = "src/apps/frontend/src/components/admin/SMSAnalyticsPanel.tsx"
    assert os.path.exists(file_path), f"File {file_path} does not exist"
    print("✅ SMSAnalyticsPanel.tsx file exists")

def test_sms_analytics_page_file_exists():
    """Test that SMSAnalyticsPage file exists."""
    file_path = "src/apps/frontend/src/pages/dashboard/SMSAnalyticsPage.tsx"
    assert os.path.exists(file_path), f"File {file_path} does not exist"
    print("✅ SMSAnalyticsPage.tsx file exists")

def test_admin_analytics_page_file_exists():
    """Test that AdminAnalyticsPage file exists."""
    file_path = "src/apps/frontend/src/pages/dashboard/AdminAnalyticsPage.tsx"
    assert os.path.exists(file_path), f"File {file_path} does not exist"
    print("✅ AdminAnalyticsPage.tsx file exists")

def test_component_file_content():
    """Test that component files have expected content structure."""
    files_to_check = [
        "src/apps/frontend/src/components/dashboard/SMSAnalyticsWidget.tsx",
        "src/apps/frontend/src/components/admin/SMSAnalyticsPanel.tsx",
        "src/apps/frontend/src/pages/dashboard/SMSAnalyticsPage.tsx",
        "src/apps/frontend/src/pages/dashboard/AdminAnalyticsPage.tsx"
    ]
    
    for file_path in files_to_check:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for React component structure
            assert "import React" in content, f"Missing React import in {file_path}"
            assert "export default" in content, f"Missing export default in {file_path}"
            assert "const" in content or "function" in content, f"Missing component definition in {file_path}"
            
        print(f"✅ {file_path} has correct React component structure")

def test_dashboard_integration():
    """Test that dashboard integration files are properly updated."""
    # Check DashboardHome.tsx has SMS analytics widget
    dashboard_home_path = "src/apps/frontend/src/pages/dashboard/DashboardHome.tsx"
    with open(dashboard_home_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "SMSAnalyticsWidget" in content, "DashboardHome.tsx missing SMSAnalyticsWidget import"
        assert "SMS Analytics & Usage" in content, "DashboardHome.tsx missing SMS analytics section"
    
    # Check Sidebar.tsx has SMS analytics navigation
    sidebar_path = "src/apps/frontend/src/components/dashboard/Sidebar.tsx"
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "SMS Analytics" in content, "Sidebar.tsx missing SMS Analytics navigation item"
        assert "Admin Analytics" in content, "Sidebar.tsx missing Admin Analytics navigation item"
    
    # Check App.tsx has new routes
    app_path = "src/apps/frontend/src/App.tsx"
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "sms-analytics" in content, "App.tsx missing sms-analytics route"
        assert "admin-analytics" in content, "App.tsx missing admin-analytics route"
    
    print("✅ Dashboard integration files are properly updated")

def test_routing_configuration():
    """Test that routing configuration is properly set up."""
    # Check dashboard pages index exports
    index_path = "src/apps/frontend/src/pages/dashboard/index.ts"
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "SMSAnalyticsPage" in content, "Dashboard index missing SMSAnalyticsPage export"
        assert "AdminAnalyticsPage" in content, "Dashboard index missing AdminAnalyticsPage export"
    
    print("✅ Routing configuration is properly set up")

if __name__ == "__main__":
    # Run basic file existence tests
    test_sms_analytics_widget_file_exists()
    test_sms_analytics_panel_file_exists()
    test_sms_analytics_page_file_exists()
    test_admin_analytics_page_file_exists()
    
    # Run content structure tests
    test_component_file_content()
    test_dashboard_integration()
    test_routing_configuration()
    
    print("🎉 All frontend component tests passed!")
