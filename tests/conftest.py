"""
Global test configuration and fixtures for the Personal Assistant TDAH test suite.
"""
import os
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Test environment configuration
os.environ.setdefault("TEST_MODE", "true")
os.environ.setdefault("MOCK_EXTERNAL_SERVICES", "true")
os.environ.setdefault("MOCK_TWILIO", "true")
os.environ.setdefault("MOCK_OAUTH", "true")

# Test database configuration
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", 
    "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
)

# Test Redis configuration
TEST_REDIS_URL = os.environ.get(
    "TEST_REDIS_URL", 
    "redis://localhost:6379"
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Ensure test mode is enabled
    os.environ["TEST_MODE"] = "true"
    os.environ["MOCK_EXTERNAL_SERVICES"] = "true"
    
    # Mock external services
    os.environ["MOCK_TWILIO"] = "true"
    os.environ["MOCK_OAUTH"] = "true"
    os.environ["MOCK_GOOGLE"] = "true"
    os.environ["MOCK_NOTION"] = "true"
    
    yield
    
    # Cleanup (if needed)
    pass

@pytest.fixture
def mock_redis():
    """Mock Redis connection for tests."""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        async def get(self, key):
            return self.data.get(key)
        
        async def set(self, key, value, ex=None):
            self.data[key] = value
            return True
        
        async def delete(self, key):
            return self.data.pop(key, None) is not None
    
    return MockRedis()

@pytest.fixture
def mock_twilio():
    """Mock Twilio service for tests."""
    class MockTwilio:
        def __init__(self):
            self.messages_sent = []
        
        async def send_verification_sms(self, phone_number, code):
            self.messages_sent.append({"phone": phone_number, "code": code})
            return {"status": "sent", "sid": "mock_sid"}
    
    return MockTwilio()

@pytest.fixture
def mock_oauth():
    """Mock OAuth service for tests."""
    class MockOAuth:
        def __init__(self):
            self.tokens = {}
        
        async def get_token(self, provider, user_id):
            return self.tokens.get(f"{provider}_{user_id}")
        
        async def set_token(self, provider, user_id, token):
            self.tokens[f"{provider}_{user_id}"] = token
    
    return MockOAuth()
