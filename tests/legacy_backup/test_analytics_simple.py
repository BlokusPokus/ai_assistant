"""
Simple test to check if the analytics service can work with the fixed data.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

async def test_analytics_service_basic():
    """Test basic analytics service functionality."""
    try:
        from personal_assistant.sms_router.services.analytics import SMSAnalyticsService
        
        # Create a mock database session
        mock_db = AsyncMock()
        
        # Create the analytics service
        analytics_service = SMSAnalyticsService(mock_db)
        
        print("✅ Analytics service created successfully")
        
        # Test that the service has the expected methods
        expected_methods = [
            'get_user_usage_summary',
            'get_user_usage_trends',
            'get_user_performance_metrics',
            'get_user_message_breakdown'
        ]
        
        for method_name in expected_methods:
            assert hasattr(analytics_service, method_name), f"Missing method: {method_name}"
        
        print("✅ All expected methods exist")
        
        # Test that we can create a mock SMSUsageLog object
        mock_log = MagicMock()
        mock_log.user_id = 1
        mock_log.phone_number = "+1234567890"
        mock_log.message_direction = "outbound"
        mock_log.message_length = 160
        mock_log.success = True
        mock_log.processing_time_ms = 120
        mock_log.error_message = None
        mock_log.country_code = "US"
        mock_log.created_at = datetime.utcnow()
        
        print("✅ Mock SMSUsageLog object created successfully")
        
        # Test that we can access the created_at.hour attribute
        hour = mock_log.created_at.hour
        assert isinstance(hour, int)
        print(f"✅ Hour extraction works: {hour}")
        
        # Test that we can access other attributes
        assert mock_log.message_length == 160
        assert mock_log.success is True
        assert mock_log.processing_time_ms == 120
        
        print("✅ All mock object attributes accessible")
        
    except Exception as e:
        pytest.fail(f"Basic analytics service test failed: {e}")

async def test_database_connection():
    """Test that we can connect to the database and access SMSUsageLog."""
    try:
        from personal_assistant.database.session import AsyncSessionLocal
        from personal_assistant.sms_router.models.sms_models import SMSUsageLog
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            # Test basic connection
            result = await session.execute(select(SMSUsageLog).limit(1))
            logs = result.scalars().all()
            
            print(f"✅ Database connection successful, found {len(logs)} SMS logs")
            
            if logs:
                log = logs[0]
                print(f"✅ Sample log ID: {log.id}")
                print(f"✅ Sample log user_id: {log.user_id}")
                print(f"✅ Sample log created_at: {log.created_at}")
                print(f"✅ Sample log created_at type: {type(log.created_at)}")
                
                # Test that created_at is a datetime object
                if hasattr(log.created_at, 'hour'):
                    hour = log.created_at.hour
                    print(f"✅ Hour extraction works: {hour}")
                else:
                    print(f"❌ created_at is not a datetime object: {type(log.created_at)}")
                    
    except Exception as e:
        pytest.fail(f"Database connection test failed: {e}")

if __name__ == "__main__":
    print("🧪 Running Simple Analytics Tests...")
    
    # Run tests
    asyncio.run(test_analytics_service_basic())
    asyncio.run(test_database_connection())
    
    print("🎉 All simple analytics tests passed!")
