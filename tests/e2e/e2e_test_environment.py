"""
E2E Test Environment Setup

This module provides comprehensive environment setup for End-to-End testing,
including test data management, external service mocking, and environment configuration.
"""

import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import asyncio
from unittest.mock import Mock, patch
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.personal_assistant.database.database import get_database_url
from src.personal_assistant.models.user import User
from src.personal_assistant.models.task import Task
from src.personal_assistant.models.memory import Memory


@dataclass
class E2ETestConfig:
    """Configuration for E2E test environment."""
    environment: str  # "development", "staging", "production"
    database_url: str
    external_services_mocked: bool
    test_data_path: str
    log_level: str
    timeout_seconds: int
    retry_attempts: int
    parallel_execution: bool
    max_parallel_tests: int


@dataclass
class TestUser:
    """Test user data for E2E tests."""
    username: str
    email: str
    password: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    preferences: Dict[str, Any]


@dataclass
class TestTask:
    """Test task data for E2E tests."""
    title: str
    description: str
    task_type: str
    parameters: Dict[str, Any]
    status: str
    priority: str
    created_at: datetime
    scheduled_at: Optional[datetime]


@dataclass
class TestMemory:
    """Test memory data for E2E tests."""
    content: str
    memory_type: str
    tags: List[str]
    importance: int
    created_at: datetime
    last_accessed: datetime


class E2ETestEnvironment:
    """Manages E2E test environment setup and teardown."""
    
    def __init__(self, config: E2ETestConfig):
        self.config = config
        self.temp_dir = None
        self.database_engine = None
        self.database_session = None
        self.test_users = []
        self.test_tasks = []
        self.test_memories = []
        self.mocked_services = {}
        self.cleanup_tasks = []
        
    async def setup(self):
        """Set up the E2E test environment."""
        print("🔧 Setting up E2E test environment...")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="e2e_test_")
        print(f"📁 Created temp directory: {self.temp_dir}")
        
        # Set up database
        await self._setup_database()
        
        # Set up external services
        await self._setup_external_services()
        
        # Load test data
        await self._load_test_data()
        
        # Set up monitoring
        await self._setup_monitoring()
        
        print("✅ E2E test environment setup complete")
    
    async def teardown(self):
        """Tear down the E2E test environment."""
        print("🧹 Tearing down E2E test environment...")
        
        # Clean up database
        await self._cleanup_database()
        
        # Clean up external services
        await self._cleanup_external_services()
        
        # Clean up test data
        await self._cleanup_test_data()
        
        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"🗑️  Removed temp directory: {self.temp_dir}")
        
        # Execute cleanup tasks
        for cleanup_task in self.cleanup_tasks:
            try:
                await cleanup_task()
            except Exception as e:
                print(f"⚠️  Cleanup task failed: {e}")
        
        print("✅ E2E test environment teardown complete")
    
    async def _setup_database(self):
        """Set up test database."""
        print("🗄️  Setting up test database...")
        
        # Create test database URL
        test_db_url = self.config.database_url.replace(
            "personal_assistant.db", 
            f"e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        
        # Create database engine
        self.database_engine = create_engine(test_db_url, echo=False)
        
        # Create database session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.database_engine)
        self.database_session = SessionLocal()
        
        # Create tables
        from src.personal_assistant.database.database import Base
        Base.metadata.create_all(bind=self.database_engine)
        
        print("✅ Test database setup complete")
    
    async def _setup_external_services(self):
        """Set up mocked external services."""
        print("🌐 Setting up external services...")
        
        if self.config.external_services_mocked:
            # Mock YouTube API
            self.mocked_services['youtube'] = await self._mock_youtube_api()
            
            # Mock Notion API
            self.mocked_services['notion'] = await self._mock_notion_api()
            
            # Mock Email Service
            self.mocked_services['email'] = await self._mock_email_service()
            
            # Mock Calendar API
            self.mocked_services['calendar'] = await self._mock_calendar_api()
            
            # Mock Internet Search API
            self.mocked_services['internet'] = await self._mock_internet_api()
        
        print("✅ External services setup complete")
    
    async def _mock_youtube_api(self):
        """Mock YouTube API service."""
        mock_youtube = Mock()
        
        # Mock search functionality
        mock_youtube.search.return_value = {
            'items': [
                {
                    'id': {'videoId': 'test_video_1'},
                    'snippet': {
                        'title': 'Test Video 1',
                        'description': 'Test video description',
                        'thumbnails': {'default': {'url': 'https://example.com/thumb1.jpg'}}
                    }
                },
                {
                    'id': {'videoId': 'test_video_2'},
                    'snippet': {
                        'title': 'Test Video 2',
                        'description': 'Another test video',
                        'thumbnails': {'default': {'url': 'https://example.com/thumb2.jpg'}}
                    }
                }
            ]
        }
        
        # Mock video details
        mock_youtube.get_video_details.return_value = {
            'items': [{
                'id': 'test_video_1',
                'snippet': {
                    'title': 'Test Video 1',
                    'description': 'Detailed video description',
                    'channelTitle': 'Test Channel'
                },
                'statistics': {
                    'viewCount': '1000',
                    'likeCount': '50'
                }
            }]
        }
        
        return mock_youtube
    
    async def _mock_notion_api(self):
        """Mock Notion API service."""
        mock_notion = Mock()
        
        # Mock page creation
        mock_notion.create_page.return_value = {
            'id': 'test_page_id',
            'url': 'https://notion.so/test_page',
            'properties': {
                'title': 'Test Page',
                'created_time': datetime.now().isoformat()
            }
        }
        
        # Mock page retrieval
        mock_notion.get_page.return_value = {
            'id': 'test_page_id',
            'properties': {
                'title': 'Test Page',
                'content': 'Test page content'
            }
        }
        
        # Mock page update
        mock_notion.update_page.return_value = {
            'id': 'test_page_id',
            'properties': {
                'title': 'Updated Test Page',
                'content': 'Updated content'
            }
        }
        
        return mock_notion
    
    async def _mock_email_service(self):
        """Mock email service."""
        mock_email = Mock()
        
        # Mock email sending
        mock_email.send_email.return_value = {
            'message_id': 'test_message_id',
            'status': 'sent',
            'timestamp': datetime.now().isoformat()
        }
        
        # Mock email retrieval
        mock_email.get_emails.return_value = [
            {
                'id': 'test_email_1',
                'subject': 'Test Email',
                'from': 'test@example.com',
                'to': 'user@example.com',
                'body': 'Test email body',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        return mock_email
    
    async def _mock_calendar_api(self):
        """Mock calendar API service."""
        mock_calendar = Mock()
        
        # Mock event creation
        mock_calendar.create_event.return_value = {
            'id': 'test_event_id',
            'summary': 'Test Event',
            'start': {'dateTime': datetime.now().isoformat()},
            'end': {'dateTime': (datetime.now() + timedelta(hours=1)).isoformat()}
        }
        
        # Mock event retrieval
        mock_calendar.get_events.return_value = [
            {
                'id': 'test_event_1',
                'summary': 'Test Event 1',
                'start': {'dateTime': datetime.now().isoformat()},
                'end': {'dateTime': (datetime.now() + timedelta(hours=1)).isoformat()}
            }
        ]
        
        return mock_calendar
    
    async def _mock_internet_api(self):
        """Mock internet search API service."""
        mock_internet = Mock()
        
        # Mock search functionality
        mock_internet.search.return_value = {
            'results': [
                {
                    'title': 'Test Search Result 1',
                    'url': 'https://example.com/result1',
                    'snippet': 'Test search result snippet 1'
                },
                {
                    'title': 'Test Search Result 2',
                    'url': 'https://example.com/result2',
                    'snippet': 'Test search result snippet 2'
                }
            ]
        }
        
        return mock_internet
    
    async def _load_test_data(self):
        """Load test data for E2E tests."""
        print("📊 Loading test data...")
        
        # Create test users
        self.test_users = await self._create_test_users()
        
        # Create test tasks
        self.test_tasks = await self._create_test_tasks()
        
        # Create test memories
        self.test_memories = await self._create_test_memories()
        
        print("✅ Test data loaded")
    
    async def _create_test_users(self) -> List[TestUser]:
        """Create test users."""
        test_users = [
            TestUser(
                username="test_user_1",
                email="test1@example.com",
                password="test_password_123",
                full_name="Test User 1",
                is_active=True,
                is_verified=True,
                created_at=datetime.now(),
                preferences={"theme": "dark", "language": "en"}
            ),
            TestUser(
                username="test_user_2",
                email="test2@example.com",
                password="test_password_456",
                full_name="Test User 2",
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
                preferences={"theme": "light", "language": "es"}
            ),
            TestUser(
                username="admin_user",
                email="admin@example.com",
                password="admin_password_789",
                full_name="Admin User",
                is_active=True,
                is_verified=True,
                created_at=datetime.now(),
                preferences={"theme": "dark", "language": "en", "role": "admin"}
            )
        ]
        
        # Store users in database
        for test_user in test_users:
            user = User(
                username=test_user.username,
                email=test_user.email,
                full_name=test_user.full_name,
                is_active=test_user.is_active,
                is_verified=test_user.is_verified,
                created_at=test_user.created_at
            )
            user.set_password(test_user.password)
            self.database_session.add(user)
        
        self.database_session.commit()
        return test_users
    
    async def _create_test_tasks(self) -> List[TestTask]:
        """Create test tasks."""
        test_tasks = [
            TestTask(
                title="YouTube Search Task",
                description="Search for Python tutorials on YouTube",
                task_type="youtube_search",
                parameters={"query": "python tutorial", "max_results": 10},
                status="pending",
                priority="medium",
                created_at=datetime.now(),
                scheduled_at=None
            ),
            TestTask(
                title="Notion Page Creation",
                description="Create a new page in Notion",
                task_type="notion_create_page",
                parameters={"title": "Test Page", "content": "Test content"},
                status="completed",
                priority="high",
                created_at=datetime.now() - timedelta(hours=1),
                scheduled_at=None
            ),
            TestTask(
                title="Email Sending Task",
                description="Send an email to a contact",
                task_type="email_send",
                parameters={"to": "contact@example.com", "subject": "Test Email", "body": "Test email body"},
                status="in_progress",
                priority="low",
                created_at=datetime.now() - timedelta(minutes=30),
                scheduled_at=None
            )
        ]
        
        # Store tasks in database
        for test_task in test_tasks:
            task = Task(
                title=test_task.title,
                description=test_task.description,
                task_type=test_task.task_type,
                parameters=json.dumps(test_task.parameters),
                status=test_task.status,
                priority=test_task.priority,
                created_at=test_task.created_at,
                scheduled_at=test_task.scheduled_at
            )
            self.database_session.add(task)
        
        self.database_session.commit()
        return test_tasks
    
    async def _create_test_memories(self) -> List[TestMemory]:
        """Create test memories."""
        test_memories = [
            TestMemory(
                content="User prefers Python programming tutorials",
                memory_type="preference",
                tags=["programming", "python", "tutorials"],
                importance=8,
                created_at=datetime.now() - timedelta(days=1),
                last_accessed=datetime.now() - timedelta(hours=2)
            ),
            TestMemory(
                content="User frequently searches for machine learning content",
                memory_type="behavior",
                tags=["machine_learning", "ai", "search_patterns"],
                importance=7,
                created_at=datetime.now() - timedelta(days=2),
                last_accessed=datetime.now() - timedelta(hours=1)
            ),
            TestMemory(
                content="User has Notion workspace for project management",
                memory_type="tool_usage",
                tags=["notion", "project_management", "workspace"],
                importance=6,
                created_at=datetime.now() - timedelta(days=3),
                last_accessed=datetime.now() - timedelta(minutes=30)
            )
        ]
        
        # Store memories in database
        for test_memory in test_memories:
            memory = Memory(
                content=test_memory.content,
                memory_type=test_memory.memory_type,
                tags=json.dumps(test_memory.tags),
                importance=test_memory.importance,
                created_at=test_memory.created_at,
                last_accessed=test_memory.last_accessed
            )
            self.database_session.add(memory)
        
        self.database_session.commit()
        return test_memories
    
    async def _setup_monitoring(self):
        """Set up test monitoring."""
        print("📊 Setting up test monitoring...")
        
        # Set up logging
        import logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{self.temp_dir}/e2e_test.log"),
                logging.StreamHandler()
            ]
        )
        
        # Set up performance monitoring
        self.performance_monitor = {
            'start_time': datetime.now(),
            'test_count': 0,
            'pass_count': 0,
            'fail_count': 0,
            'execution_times': []
        }
        
        print("✅ Test monitoring setup complete")
    
    async def _cleanup_database(self):
        """Clean up test database."""
        if self.database_session:
            self.database_session.close()
        
        if self.database_engine:
            self.database_engine.dispose()
        
        print("🗄️  Database cleanup complete")
    
    async def _cleanup_external_services(self):
        """Clean up external services."""
        self.mocked_services.clear()
        print("🌐 External services cleanup complete")
    
    async def _cleanup_test_data(self):
        """Clean up test data."""
        self.test_users.clear()
        self.test_tasks.clear()
        self.test_memories.clear()
        print("📊 Test data cleanup complete")
    
    def get_test_user(self, username: str) -> Optional[TestUser]:
        """Get test user by username."""
        for user in self.test_users:
            if user.username == username:
                return user
        return None
    
    def get_test_task(self, title: str) -> Optional[TestTask]:
        """Get test task by title."""
        for task in self.test_tasks:
            if task.title == title:
                return task
        return None
    
    def get_test_memory(self, content: str) -> Optional[TestMemory]:
        """Get test memory by content."""
        for memory in self.test_memories:
            if memory.content == content:
                return memory
        return None
    
    def add_cleanup_task(self, cleanup_task):
        """Add a cleanup task to be executed during teardown."""
        self.cleanup_tasks.append(cleanup_task)
    
    def get_mocked_service(self, service_name: str):
        """Get mocked service by name."""
        return self.mocked_services.get(service_name)
    
    def update_performance_metrics(self, test_name: str, execution_time: float, passed: bool):
        """Update performance metrics."""
        self.performance_monitor['test_count'] += 1
        if passed:
            self.performance_monitor['pass_count'] += 1
        else:
            self.performance_monitor['fail_count'] += 1
        
        self.performance_monitor['execution_times'].append({
            'test_name': test_name,
            'execution_time': execution_time,
            'passed': passed,
            'timestamp': datetime.now()
        })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report."""
        total_time = (datetime.now() - self.performance_monitor['start_time']).total_seconds()
        pass_rate = (self.performance_monitor['pass_count'] / self.performance_monitor['test_count'] * 100) if self.performance_monitor['test_count'] > 0 else 0
        
        return {
            'total_tests': self.performance_monitor['test_count'],
            'passed_tests': self.performance_monitor['pass_count'],
            'failed_tests': self.performance_monitor['fail_count'],
            'pass_rate': pass_rate,
            'total_execution_time': total_time,
            'average_execution_time': sum(t['execution_time'] for t in self.performance_monitor['execution_times']) / len(self.performance_monitor['execution_times']) if self.performance_monitor['execution_times'] else 0,
            'execution_times': self.performance_monitor['execution_times']
        }


# Global E2E test environment instance
_e2e_environment = None


def get_e2e_environment() -> E2ETestEnvironment:
    """Get the global E2E test environment."""
    return _e2e_environment


async def setup_e2e_environment(config: E2ETestConfig) -> E2ETestEnvironment:
    """Set up the global E2E test environment."""
    global _e2e_environment
    _e2e_environment = E2ETestEnvironment(config)
    await _e2e_environment.setup()
    return _e2e_environment


async def teardown_e2e_environment():
    """Tear down the global E2E test environment."""
    global _e2e_environment
    if _e2e_environment:
        await _e2e_environment.teardown()
        _e2e_environment = None


# Pytest fixtures for E2E testing
@pytest.fixture(scope="session")
async def e2e_environment():
    """Pytest fixture for E2E test environment."""
    config = E2ETestConfig(
        environment="development",
        database_url="sqlite:///e2e_test.db",
        external_services_mocked=True,
        test_data_path="tests/e2e/test_data",
        log_level="INFO",
        timeout_seconds=30,
        retry_attempts=3,
        parallel_execution=True,
        max_parallel_tests=4
    )
    
    environment = await setup_e2e_environment(config)
    yield environment
    await teardown_e2e_environment()


@pytest.fixture
async def test_user(e2e_environment):
    """Pytest fixture for test user."""
    return e2e_environment.get_test_user("test_user_1")


@pytest.fixture
async def test_task(e2e_environment):
    """Pytest fixture for test task."""
    return e2e_environment.get_test_task("YouTube Search Task")


@pytest.fixture
async def test_memory(e2e_environment):
    """Pytest fixture for test memory."""
    return e2e_environment.get_test_memory("User prefers Python programming tutorials")


@pytest.fixture
async def mocked_youtube_api(e2e_environment):
    """Pytest fixture for mocked YouTube API."""
    return e2e_environment.get_mocked_service("youtube")


@pytest.fixture
async def mocked_notion_api(e2e_environment):
    """Pytest fixture for mocked Notion API."""
    return e2e_environment.get_mocked_service("notion")


@pytest.fixture
async def mocked_email_service(e2e_environment):
    """Pytest fixture for mocked email service."""
    return e2e_environment.get_mocked_service("email")


@pytest.fixture
async def mocked_calendar_api(e2e_environment):
    """Pytest fixture for mocked calendar API."""
    return e2e_environment.get_mocked_service("calendar")


@pytest.fixture
async def mocked_internet_api(e2e_environment):
    """Pytest fixture for mocked internet API."""
    return e2e_environment.get_mocked_service("internet")
