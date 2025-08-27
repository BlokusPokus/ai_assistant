"""
Test database connection and SMSUsageLog table access.
"""

import pytest
import asyncio
from sqlalchemy import select, text
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.sms_router.models.sms_models import SMSUsageLog

async def test_database_connection():
    """Test that we can connect to the database."""
    try:
        async with AsyncSessionLocal() as session:
            # Test basic connection
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            print("✅ Database connection successful")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

async def test_sms_usage_log_table_exists():
    """Test that the SMSUsageLog table exists."""
    try:
        async with AsyncSessionLocal() as session:
            # Check if table exists by trying to select from it
            result = await session.execute(select(SMSUsageLog).limit(1))
            print("✅ SMSUsageLog table exists and is accessible")
    except Exception as e:
        pytest.fail(f"SMSUsageLog table access failed: {e}")

async def test_sms_usage_log_structure():
    """Test that SMSUsageLog has the expected structure."""
    try:
        # Check that the model has the expected attributes
        expected_columns = [
            'id', 'user_id', 'phone_number', 'message_direction', 
            'message_length', 'message_content', 'success', 'processing_time_ms',
            'error_message', 'country_code', 'sms_metadata', 'created_at'
        ]
        
        for column in expected_columns:
            assert hasattr(SMSUsageLog, column), f"Missing column: {column}"
        
        print("✅ SMSUsageLog model has expected structure")
    except Exception as e:
        pytest.fail(f"SMSUsageLog structure check failed: {e}")

async def test_insert_sample_data():
    """Test inserting sample data into SMSUsageLog."""
    try:
        async with AsyncSessionLocal() as session:
            # Create a sample log entry
            sample_log = SMSUsageLog(
                user_id=1,
                phone_number="+1234567890",
                message_direction="outbound",
                message_length=160,
                message_content="Test message",
                success=True,
                processing_time_ms=120,
                country_code="US"
            )
            
            session.add(sample_log)
            await session.commit()
            
            # Verify it was inserted
            result = await session.execute(
                select(SMSUsageLog).where(SMSUsageLog.id == sample_log.id)
            )
            inserted_log = result.scalar_one()
            assert inserted_log.user_id == 1
            assert inserted_log.phone_number == "+1234567890"
            
            # Clean up
            await session.delete(inserted_log)
            await session.commit()
            
            print("✅ Sample data insertion and cleanup successful")
    except Exception as e:
        pytest.fail(f"Sample data insertion failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Database Connection and SMSUsageLog Table...")
    
    # Run tests
    asyncio.run(test_database_connection())
    asyncio.run(test_sms_usage_log_table_exists())
    asyncio.run(test_sms_usage_log_structure())
    asyncio.run(test_insert_sample_data())
    
    print("🎉 All database tests passed!")
