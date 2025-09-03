"""
Unit tests for E2E test strategy implementation.

This module tests the E2E test environment setup, test scenarios, and test execution components.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from tests.e2e.e2e_test_environment import (
    E2ETestEnvironment, E2ETestConfig, E2EUser, E2ETask, E2EMemory,
    get_e2e_environment, setup_e2e_environment, teardown_e2e_environment
)

from tests.e2e.e2e_test_scenarios import (
    AuthenticationScenarios, TaskManagementScenarios,
    ToolIntegrationScenarios, MemoryAndLearningScenarios,
    get_authentication_scenarios, get_task_management_scenarios,
    get_tool_integration_scenarios, get_memory_learning_scenarios
)

from tests.e2e.e2e_test_execution import (
    E2ETestExecutor, E2ETestResult, E2ETestSuite, E2ETestReport,
    get_e2e_executor, run_e2e_tests
)


class TestE2ETestConfig:
    """Test E2ETestConfig class."""

    def test_config_initialization(self):
        """Test E2ETestConfig initialization."""
        config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path="tests/e2e/test_data",
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )
        
        assert config.environment == "development"
        assert config.database_url == "sqlite:///test.db"
        assert config.external_services_mocked is True
        assert config.test_data_path == "tests/e2e/test_data"
        assert config.log_level == "INFO"
        assert config.timeout_seconds == 30
        assert config.retry_attempts == 3
        assert config.parallel_execution is True
        assert config.max_parallel_tests == 4


class TestE2ETestEnvironment:
    """Test E2ETestEnvironment class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )
        self.environment = E2ETestEnvironment(self.config)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_environment_initialization(self):
        """Test E2ETestEnvironment initialization."""
        assert self.environment.config == self.config
        assert self.environment.temp_dir is None
        assert self.environment.database_engine is None
        assert self.environment.database_session is None
        assert self.environment.test_users == []
        assert self.environment.test_tasks == []
        assert self.environment.test_memories == []
        assert self.environment.mocked_services == {}
        assert self.environment.cleanup_tasks == []

    @pytest.mark.asyncio
    async def test_setup_environment(self):
        """Test environment setup."""
        await self.environment.setup()
        
        assert self.environment.temp_dir is not None
        assert Path(self.environment.temp_dir).exists()
        assert self.environment.database_engine is not None
        assert self.environment.database_session is not None
        assert len(self.environment.test_users) > 0
        assert len(self.environment.test_tasks) > 0
        assert len(self.environment.test_memories) > 0
        assert len(self.environment.mocked_services) > 0

    @pytest.mark.asyncio
    async def test_teardown_environment(self):
        """Test environment teardown."""
        await self.environment.setup()
        await self.environment.teardown()
        
        # Environment should be cleaned up
        assert self.environment.database_session is None
        assert self.environment.database_engine is None
        assert self.environment.test_users == []
        assert self.environment.test_tasks == []
        assert self.environment.test_memories == []
        assert self.environment.mocked_services == {}

    @pytest.mark.asyncio
    async def test_mock_services_setup(self):
        """Test mock services setup."""
        await self.environment.setup()
        
        # Check that mock services are created
        assert 'youtube' in self.environment.mocked_services
        assert 'notion' in self.environment.mocked_services
        assert 'email' in self.environment.mocked_services
        assert 'calendar' in self.environment.mocked_services
        assert 'internet' in self.environment.mocked_services
        
        # Check that mock services have expected methods
        youtube_mock = self.environment.mocked_services['youtube']
        assert hasattr(youtube_mock, 'search')
        assert hasattr(youtube_mock, 'get_video_details')
        
        notion_mock = self.environment.mocked_services['notion']
        assert hasattr(notion_mock, 'create_page')
        assert hasattr(notion_mock, 'get_page')
        
        email_mock = self.environment.mocked_services['email']
        assert hasattr(email_mock, 'send_email')
        assert hasattr(email_mock, 'get_emails')

    def test_get_test_user(self):
        """Test getting test user."""
        # Create a test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        # Test getting user
        retrieved_user = self.environment.get_test_user("test_user")
        assert retrieved_user == test_user
        
        # Test getting non-existent user
        non_existent = self.environment.get_test_user("non_existent")
        assert non_existent is None

    def test_get_test_task(self):
        """Test getting test task."""
        # Create a test task
        test_task = TestTask(
            title="Test Task",
            description="Test task description",
            task_type="test",
            parameters={"param": "value"},
            status="pending",
            priority="medium",
            created_at=datetime.now(),
            scheduled_at=None
        )
        self.environment.test_tasks = [test_task]
        
        # Test getting task
        retrieved_task = self.environment.get_test_task("Test Task")
        assert retrieved_task == test_task
        
        # Test getting non-existent task
        non_existent = self.environment.get_test_task("Non Existent Task")
        assert non_existent is None

    def test_get_test_memory(self):
        """Test getting test memory."""
        # Create a test memory
        test_memory = TestMemory(
            content="Test memory content",
            memory_type="test",
            tags=["test", "memory"],
            importance=5,
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        self.environment.test_memories = [test_memory]
        
        # Test getting memory
        retrieved_memory = self.environment.get_test_memory("Test memory content")
        assert retrieved_memory == test_memory
        
        # Test getting non-existent memory
        non_existent = self.environment.get_test_memory("Non existent content")
        assert non_existent is None

    def test_get_mocked_service(self):
        """Test getting mocked service."""
        # Add a mock service
        mock_service = Mock()
        self.environment.mocked_services['test_service'] = mock_service
        
        # Test getting service
        retrieved_service = self.environment.get_mocked_service('test_service')
        assert retrieved_service == mock_service
        
        # Test getting non-existent service
        non_existent = self.environment.get_mocked_service('non_existent')
        assert non_existent is None

    def test_update_performance_metrics(self):
        """Test updating performance metrics."""
        self.environment.update_performance_metrics("test_scenario", 1.5, True)
        
        assert self.environment.performance_monitor['test_count'] == 1
        assert self.environment.performance_monitor['pass_count'] == 1
        assert self.environment.performance_monitor['fail_count'] == 0
        assert len(self.environment.performance_monitor['execution_times']) == 1
        
        execution_time = self.environment.performance_monitor['execution_times'][0]
        assert execution_time['test_name'] == "test_scenario"
        assert execution_time['execution_time'] == 1.5
        assert execution_time['passed'] is True

    def test_get_performance_report(self):
        """Test getting performance report."""
        # Add some test data
        self.environment.performance_monitor = {
            'start_time': datetime.now(),
            'test_count': 3,
            'pass_count': 2,
            'fail_count': 1,
            'execution_times': [
                {'test_name': 'test1', 'execution_time': 1.0, 'passed': True, 'timestamp': datetime.now()},
                {'test_name': 'test2', 'execution_time': 2.0, 'passed': True, 'timestamp': datetime.now()},
                {'test_name': 'test3', 'execution_time': 1.5, 'passed': False, 'timestamp': datetime.now()}
            ]
        }
        
        report = self.environment.get_performance_report()
        
        assert report['total_tests'] == 3
        assert report['passed_tests'] == 2
        assert report['failed_tests'] == 1
        assert report['pass_rate'] == 66.66666666666666
        assert report['average_execution_time'] == 1.5
        assert len(report['execution_times']) == 3


class TestAuthenticationScenarios:
    """Test AuthenticationScenarios class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )
        self.environment = E2ETestEnvironment(self.config)
        self.scenarios = AuthenticationScenarios(self.environment)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(self):
        """Test complete user registration flow."""
        result = await self.scenarios.complete_user_registration_flow()
        
        assert result is not None
        assert 'user_id' in result
        assert 'email' in result
        assert 'activated' in result
        assert result['activated'] is True

    @pytest.mark.asyncio
    async def test_user_login_and_session_management(self):
        """Test user login and session management."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.user_login_and_session_management()
        
        assert result is not None
        assert 'session_token' in result
        assert 'user_id' in result
        assert 'session_valid' in result
        assert result['session_valid'] is True

    @pytest.mark.asyncio
    async def test_password_reset_flow(self):
        """Test password reset flow."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.password_reset_flow()
        
        assert result is not None
        assert 'reset_token' in result
        assert 'new_password_set' in result
        assert 'login_successful' in result
        assert result['new_password_set'] is True
        assert result['login_successful'] is True


class TestTaskManagementScenarios:
    """Test TaskManagementScenarios class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )
        self.environment = E2ETestEnvironment(self.config)
        self.scenarios = TaskManagementScenarios(self.environment)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_complete_task_creation_and_execution(self):
        """Test complete task creation and execution."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.complete_task_creation_and_execution()
        
        assert result is not None
        assert 'task_id' in result
        assert 'status' in result
        assert 'results_count' in result
        assert result['status'] == 'completed'
        assert result['results_count'] > 0

    @pytest.mark.asyncio
    async def test_task_scheduling_and_reminders(self):
        """Test task scheduling and reminders."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.task_scheduling_and_reminders()
        
        assert result is not None
        assert 'task_id' in result
        assert 'scheduled_at' in result
        assert 'executed_at' in result
        assert 'notification_sent' in result
        assert result['notification_sent'] is True

    @pytest.mark.asyncio
    async def test_task_error_handling_and_recovery(self):
        """Test task error handling and recovery."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.task_error_handling_and_recovery()
        
        assert result is not None
        assert 'original_task_id' in result
        assert 'error_detected' in result
        assert 'error_logged' in result
        assert 'user_notified' in result
        assert 'retry_successful' in result
        assert result['error_detected'] is True
        assert result['error_logged'] is True
        assert result['user_notified'] is True
        assert result['retry_successful'] is True


class TestToolIntegrationScenarios:
    """Test ToolIntegrationScenarios class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )
        self.environment = E2ETestEnvironment(self.config)
        self.scenarios = ToolIntegrationScenarios(self.environment)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_youtube_tool_integration(self):
        """Test YouTube tool integration."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.youtube_tool_integration()
        
        assert result is not None
        assert 'task_id' in result
        assert 'videos_found' in result
        assert 'results_formatted' in result
        assert 'memory_saved' in result
        assert result['videos_found'] > 0
        assert result['results_formatted'] is True
        assert result['memory_saved'] is True

    @pytest.mark.asyncio
    async def test_notion_integration(self):
        """Test Notion integration."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.notion_integration()
        
        assert result is not None
        assert 'task_id' in result
        assert 'page_id' in result
        assert 'page_created' in result
        assert 'page_accessible' in result
        assert result['page_created'] is True
        assert result['page_accessible'] is True

    @pytest.mark.asyncio
    async def test_email_tool_integration(self):
        """Test email tool integration."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.email_tool_integration()
        
        assert result is not None
        assert 'task_id' in result
        assert 'message_id' in result
        assert 'email_sent' in result
        assert 'confirmation_received' in result
        assert result['email_sent'] is True
        assert result['confirmation_received'] is True


class TestMemoryAndLearningScenarios:
    """Test MemoryAndLearningScenarios class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )
        self.environment = E2ETestEnvironment(self.config)
        self.scenarios = MemoryAndLearningScenarios(self.environment)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_memory_storage_and_retrieval(self):
        """Test memory storage and retrieval."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.memory_storage_and_retrieval()
        
        assert result is not None
        assert 'memory_id' in result
        assert 'memories_found' in result
        assert 'relevance_score' in result
        assert 'response_generated' in result
        assert result['memories_found'] > 0
        assert result['relevance_score'] > 0.5
        assert result['response_generated'] is True

    @pytest.mark.asyncio
    async def test_learning_and_adaptation(self):
        """Test learning and adaptation."""
        # Set up test user
        test_user = TestUser(
            username="test_user",
            email="test@example.com",
            password="password",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            preferences={"theme": "dark"}
        )
        self.environment.test_users = [test_user]
        
        result = await self.scenarios.learning_and_adaptation()
        
        assert result is not None
        assert 'feedback_processed' in result
        assert 'learning_score' in result
        assert 'adaptation_successful' in result
        assert 'quality_improvement' in result
        assert result['feedback_processed'] is True
        assert result['learning_score'] > 0
        assert result['adaptation_successful'] is True
        assert result['quality_improvement'] > 0.8


class TestE2ETestExecutor:
    """Test E2ETestExecutor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )
        self.executor = E2ETestExecutor(self.config)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_executor_initialization(self):
        """Test E2ETestExecutor initialization."""
        assert self.executor.config == self.config
        assert self.executor.environment is None
        assert self.executor.test_results == []
        assert self.executor.logger is not None

    @pytest.mark.asyncio
    async def test_setup_environment(self):
        """Test environment setup."""
        await self.executor.setup_environment()
        
        assert self.executor.environment is not None
        assert self.executor.environment.temp_dir is not None
        assert self.executor.environment.database_engine is not None

    @pytest.mark.asyncio
    async def test_teardown_environment(self):
        """Test environment teardown."""
        await self.executor.setup_environment()
        await self.executor.teardown_environment()
        
        # Environment should be cleaned up
        assert self.executor.environment.database_session is None
        assert self.executor.environment.database_engine is None

    @pytest.mark.asyncio
    async def test_execute_single_test(self):
        """Test executing a single test."""
        await self.executor.setup_environment()
        
        # Create a simple test function
        async def test_function():
            return {"status": "success", "data": "test_data"}
        
        result = await self.executor._execute_single_test("test_suite", test_function)
        
        assert result.test_name == "test_function"
        assert result.status == "passed"
        assert result.execution_time > 0
        assert result.test_data is not None
        assert result.test_data["status"] == "success"
        
        await self.executor.teardown_environment()

    @pytest.mark.asyncio
    async def test_execute_tests_sequential(self):
        """Test executing tests sequentially."""
        await self.executor.setup_environment()
        
        # Create test functions
        async def test1():
            return {"test": "1"}
        
        async def test2():
            return {"test": "2"}
        
        test_scenarios = [test1, test2]
        results = await self.executor._execute_tests_sequential("test_suite", test_scenarios)
        
        assert len(results) == 2
        assert results[0].test_name == "test1"
        assert results[1].test_name == "test2"
        assert all(result.status == "passed" for result in results)
        
        await self.executor.teardown_environment()

    @pytest.mark.asyncio
    async def test_execute_tests_parallel(self):
        """Test executing tests in parallel."""
        await self.executor.setup_environment()
        
        # Create test functions
        async def test1():
            await asyncio.sleep(0.1)
            return {"test": "1"}
        
        async def test2():
            await asyncio.sleep(0.1)
            return {"test": "2"}
        
        test_scenarios = [test1, test2]
        results = await self.executor._execute_tests_parallel("test_suite", test_scenarios)
        
        assert len(results) == 2
        assert results[0].test_name == "test1"
        assert results[1].test_name == "test2"
        assert all(result.status == "passed" for result in results)
        
        await self.executor.teardown_environment()

    def test_collect_performance_metrics(self):
        """Test collecting performance metrics."""
        # Set up environment with performance data
        self.executor.environment = Mock()
        self.executor.environment.get_performance_report.return_value = {
            'total_tests': 5,
            'passed_tests': 4,
            'failed_tests': 1,
            'pass_rate': 80.0
        }
        
        metrics = self.executor._collect_performance_metrics()
        
        assert metrics['total_tests'] == 5
        assert metrics['passed_tests'] == 4
        assert metrics['failed_tests'] == 1
        assert metrics['pass_rate'] == 80.0

    def test_generate_recommendations(self):
        """Test generating recommendations."""
        overall_summary = {
            'pass_rate': 85.0,
            'total_tests': 20,
            'total_execution_time': 120.0
        }
        
        performance_summary = {
            'average_execution_time': 6.0,
            'tests_over_threshold': 2
        }
        
        test_suites = [
            Mock(total_tests=10, failed_tests=2, suite_name="Test Suite 1"),
            Mock(total_tests=10, failed_tests=1, suite_name="Test Suite 2")
        ]
        
        recommendations = self.executor._generate_recommendations(
            overall_summary, performance_summary, test_suites
        )
        
        assert len(recommendations) > 0
        assert any("pass rate" in rec.lower() for rec in recommendations)
        assert any("threshold" in rec.lower() for rec in recommendations)


class TestGlobalFunctions:
    """Test global functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_e2e_environment(self):
        """Test getting E2E environment."""
        environment = get_e2e_environment()
        assert environment is None  # Should be None initially

    def test_get_e2e_executor(self):
        """Test getting E2E executor."""
        executor = get_e2e_executor(self.config)
        assert isinstance(executor, E2ETestExecutor)
        assert executor.config == self.config

    def test_get_authentication_scenarios(self):
        """Test getting authentication scenarios."""
        environment = E2ETestEnvironment(self.config)
        scenarios = get_authentication_scenarios(environment)
        assert isinstance(scenarios, AuthenticationScenarios)
        assert scenarios.environment == environment

    def test_get_task_management_scenarios(self):
        """Test getting task management scenarios."""
        environment = E2ETestEnvironment(self.config)
        scenarios = get_task_management_scenarios(environment)
        assert isinstance(scenarios, TaskManagementScenarios)
        assert scenarios.environment == environment

    def test_get_tool_integration_scenarios(self):
        """Test getting tool integration scenarios."""
        environment = E2ETestEnvironment(self.config)
        scenarios = get_tool_integration_scenarios(environment)
        assert isinstance(scenarios, ToolIntegrationScenarios)
        assert scenarios.environment == environment

    def test_get_memory_learning_scenarios(self):
        """Test getting memory learning scenarios."""
        environment = E2ETestEnvironment(self.config)
        scenarios = get_memory_learning_scenarios(environment)
        assert isinstance(scenarios, MemoryAndLearningScenarios)
        assert scenarios.environment == environment


class TestIntegration:
    """Test integration of E2E test components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = E2ETestConfig(
            environment="development",
            database_url="sqlite:///test.db",
            external_services_mocked=True,
            test_data_path=self.temp_dir,
            log_level="INFO",
            timeout_seconds=30,
            retry_attempts=3,
            parallel_execution=True,
            max_parallel_tests=4
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_comprehensive_e2e_workflow(self):
        """Test comprehensive E2E workflow."""
        # Set up environment
        environment = E2ETestEnvironment(self.config)
        await environment.setup()
        
        # Test authentication scenarios
        auth_scenarios = AuthenticationScenarios(environment)
        auth_result = await auth_scenarios.complete_user_registration_flow()
        assert auth_result is not None
        
        # Test task management scenarios
        task_scenarios = TaskManagementScenarios(environment)
        task_result = await task_scenarios.complete_task_creation_and_execution()
        assert task_result is not None
        
        # Test tool integration scenarios
        tool_scenarios = ToolIntegrationScenarios(environment)
        tool_result = await tool_scenarios.youtube_tool_integration()
        assert tool_result is not None
        
        # Test memory and learning scenarios
        memory_scenarios = MemoryAndLearningScenarios(environment)
        memory_result = await memory_scenarios.memory_storage_and_retrieval()
        assert memory_result is not None
        
        # Test executor
        executor = E2ETestExecutor(self.config)
        executor.environment = environment
        
        # Test single test execution
        async def test_function():
            return {"status": "success"}
        
        test_result = await executor._execute_single_test("integration_test", test_function)
        assert test_result.status == "passed"
        
        # Clean up
        await environment.teardown()
        
        # Verify all components work together
        assert True  # Test completed successfully
