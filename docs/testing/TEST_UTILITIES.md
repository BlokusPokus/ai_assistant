# Test Utilities Documentation

## Overview

This document provides comprehensive documentation for the Personal Assistant application's test utilities, including data generators, fixtures, common utilities, and testing helpers.

## Table of Contents

1. [Common Test Utilities](#common-test-utilities)
2. [Test Fixtures](#test-fixtures)
3. [Data Generators](#data-generators)
4. [Environment Setup](#environment-setup)
5. [Cleanup Utilities](#cleanup-utilities)
6. [Performance Helpers](#performance-helpers)
7. [Mock Utilities](#mock-utilities)
8. [Usage Examples](#usage-examples)

## Common Test Utilities

### Location: `tests/utils/common_test_utilities.py`

The common test utilities provide a comprehensive set of helper functions and classes for consistent testing across the application.

### Core Classes

#### `TestDataGenerator`

Generates realistic test data for various scenarios.

```python
from tests.utils.common_test_utilities import TestDataGenerator

# Generate user data
user_data = TestDataGenerator.generate_user_data()
# Returns: {'username': 'test_user_123', 'email': 'test@example.com', ...}

# Generate API response data
api_data = TestDataGenerator.generate_api_response(status_code=200)
# Returns: {'status_code': 200, 'data': {...}, 'message': 'Success'}

# Generate database record
db_record = TestDataGenerator.generate_database_record('users')
# Returns: {'id': 1, 'username': 'test_user', 'created_at': '2024-01-01', ...}
```

#### `AssertionHelper`

Enhanced assertion functions with better error messages.

```python
from tests.utils.common_test_utilities import AssertionHelper

# Assert API response success
response = {'status_code': 200, 'data': {'user_id': 1}}
AssertionHelper.assert_response_success(response)

# Assert database record exists
record = {'id': 1, 'username': 'test_user'}
AssertionHelper.assert_record_exists(record, 'users')

# Assert error handling
with AssertionHelper.assert_raises_with_message(ValueError, "Invalid input"):
    validate_input("")
```

#### `PerformanceHelper`

Utilities for performance testing and measurement.

```python
from tests.utils.common_test_utilities import PerformanceHelper

# Measure execution time
with PerformanceHelper.measure_time() as timer:
    # Your code here
    pass
print(f"Execution time: {timer.elapsed_time:.2f}s")

# Assert performance threshold
PerformanceHelper.assert_execution_time_under(1.0, lambda: your_function())
```

### Utility Functions

#### Data Generation Functions

```python
from tests.utils.common_test_utilities import (
    generate_test_user,
    generate_test_api_request,
    generate_test_database_query,
    generate_test_json_data
)

# Generate test user
user = generate_test_user()
# Returns: User object with realistic test data

# Generate API request
request = generate_test_api_request('POST', '/api/users')
# Returns: {'method': 'POST', 'url': '/api/users', 'headers': {...}, 'data': {...}}

# Generate database query
query = generate_test_database_query('SELECT * FROM users WHERE id = ?')
# Returns: {'sql': 'SELECT * FROM users WHERE id = ?', 'params': [1]}

# Generate JSON data
json_data = generate_test_json_data()
# Returns: {'id': 1, 'name': 'Test Item', 'value': 42, ...}
```

#### Validation Functions

```python
from tests.utils.common_test_utilities import (
    validate_test_data,
    validate_api_response,
    validate_database_record
)

# Validate test data
is_valid = validate_test_data(user_data, 'user')
# Returns: True if data matches expected schema

# Validate API response
is_valid = validate_api_response(response, expected_status=200)
# Returns: True if response is valid

# Validate database record
is_valid = validate_database_record(record, 'users')
# Returns: True if record matches expected structure
```

## Test Fixtures

### Location: `tests/fixtures/common_fixtures.py`

Test fixtures provide reusable setup and teardown functionality for tests.

### Database Fixtures

#### `database_fixture`

Sets up and tears down database connections for tests.

```python
import pytest
from tests.fixtures.common_fixtures import database_fixture

@pytest.fixture
def db_session(database_fixture):
    """Provide database session for tests."""
    return database_fixture.get_session()

def test_user_creation(db_session):
    """Test user creation with database fixture."""
    user = User(username="test_user", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "test_user"
```

#### `test_database_fixture`

Provides isolated test database for each test.

```python
import pytest
from tests.fixtures.common_fixtures import test_database_fixture

@pytest.fixture
def test_db(test_database_fixture):
    """Provide isolated test database."""
    return test_database_fixture

def test_database_operations(test_db):
    """Test database operations with isolated database."""
    # Test operations here
    pass
```

### API Fixtures

#### `api_client_fixture`

Provides mocked API client for testing.

```python
import pytest
from tests.fixtures.common_fixtures import api_client_fixture

@pytest.fixture
def api_client(api_client_fixture):
    """Provide mocked API client."""
    return api_client_fixture

def test_api_request(api_client):
    """Test API request with mocked client."""
    response = api_client.get('/api/users')
    assert response.status_code == 200
```

#### `mock_http_client_fixture`

Provides mocked HTTP client for external API testing.

```python
import pytest
from tests.fixtures.common_fixtures import mock_http_client_fixture

@pytest.fixture
def http_client(mock_http_client_fixture):
    """Provide mocked HTTP client."""
    return mock_http_client_fixture

def test_external_api_call(http_client):
    """Test external API call with mocked client."""
    http_client.mock_response(200, {'data': 'test'})
    response = http_client.get('https://api.example.com/data')
    assert response.status_code == 200
```

### File System Fixtures

#### `temp_file_fixture`

Provides temporary files for testing.

```python
import pytest
from tests.fixtures.common_fixtures import temp_file_fixture

@pytest.fixture
def temp_file(temp_file_fixture):
    """Provide temporary file."""
    return temp_file_fixture

def test_file_operations(temp_file):
    """Test file operations with temporary file."""
    temp_file.write("test content")
    assert temp_file.read() == "test content"
```

#### `mock_file_system_fixture`

Provides mocked file system for testing.

```python
import pytest
from tests.fixtures.common_fixtures import mock_file_system_fixture

@pytest.fixture
def mock_fs(mock_file_system_fixture):
    """Provide mocked file system."""
    return mock_file_system_fixture

def test_file_system_operations(mock_fs):
    """Test file system operations with mocked FS."""
    mock_fs.create_file('/test/file.txt', 'content')
    assert mock_fs.exists('/test/file.txt')
```

## Data Generators

### Location: `tests/utils/test_data_generators.py`

Data generators provide realistic test data for various scenarios.

### User Data Generator

```python
from tests.utils.test_data_generators import UserDataGenerator

# Generate user profile
user_profile = UserDataGenerator.generate_user_profile()
# Returns: {'username': 'john_doe_123', 'email': 'john@example.com', 'full_name': 'John Doe', ...}

# Generate authentication data
auth_data = UserDataGenerator.generate_auth_data()
# Returns: {'username': 'test_user', 'password': 'secure_password', 'token': 'jwt_token', ...}

# Generate user preferences
preferences = UserDataGenerator.generate_user_preferences()
# Returns: {'theme': 'dark', 'language': 'en', 'notifications': True, ...}
```

### API Data Generator

```python
from tests.utils.test_data_generators import APIDataGenerator

# Generate API request
request = APIDataGenerator.generate_request('POST', '/api/users')
# Returns: {'method': 'POST', 'url': '/api/users', 'headers': {...}, 'body': {...}}

# Generate API response
response = APIDataGenerator.generate_response(200, {'user_id': 1})
# Returns: {'status_code': 200, 'headers': {...}, 'data': {'user_id': 1}, ...}

# Generate error response
error_response = APIDataGenerator.generate_error_response(400, 'Invalid input')
# Returns: {'status_code': 400, 'error': 'Invalid input', 'details': {...}}
```

### Database Data Generator

```python
from tests.utils.test_data_generators import DatabaseDataGenerator

# Generate database record
record = DatabaseDataGenerator.generate_record('users')
# Returns: {'id': 1, 'username': 'test_user', 'email': 'test@example.com', 'created_at': '2024-01-01', ...}

# Generate database query
query = DatabaseDataGenerator.generate_query('SELECT * FROM users WHERE active = ?')
# Returns: {'sql': 'SELECT * FROM users WHERE active = ?', 'params': [True], 'result': [...]}

# Generate migration data
migration = DatabaseDataGenerator.generate_migration('001_create_users_table')
# Returns: {'version': '001', 'name': 'create_users_table', 'up': 'CREATE TABLE...', 'down': 'DROP TABLE...'}
```

### Tool Data Generator

```python
from tests.utils.test_data_generators import ToolDataGenerator

# Generate tool configuration
config = ToolDataGenerator.generate_tool_config('youtube')
# Returns: {'name': 'youtube', 'api_key': 'test_key', 'enabled': True, 'settings': {...}}

# Generate tool execution data
execution = ToolDataGenerator.generate_execution_data('youtube', 'search')
# Returns: {'tool': 'youtube', 'action': 'search', 'params': {'query': 'test'}, 'result': {...}}

# Generate tool error data
error = ToolDataGenerator.generate_error_data('youtube', 'API_ERROR')
# Returns: {'tool': 'youtube', 'error_type': 'API_ERROR', 'message': 'API key invalid', 'details': {...}}
```

## Environment Setup

### Location: `tests/utils/test_environment_setup.py`

Environment setup utilities provide consistent test environment configuration.

### Environment Manager

```python
from tests.utils.test_environment_setup import TestEnvironmentManager

# Set up test environment
env_manager = TestEnvironmentManager()
env_manager.setup_test_environment()

# Configure environment variables
env_manager.set_env_var('TEST_MODE', 'true')
env_manager.set_env_var('DATABASE_URL', 'sqlite:///test.db')

# Clean up environment
env_manager.cleanup_environment()
```

### Database Setup

```python
from tests.utils.test_environment_setup import DatabaseSetupManager

# Set up test database
db_setup = DatabaseSetupManager()
db_setup.create_test_database()
db_setup.run_migrations()

# Clean up database
db_setup.drop_test_database()
```

### Configuration Setup

```python
from tests.utils.test_environment_setup import ConfigurationSetupManager

# Set up test configuration
config_setup = ConfigurationSetupManager()
config_setup.load_test_config()
config_setup.set_test_settings()

# Reset configuration
config_setup.reset_configuration()
```

## Cleanup Utilities

### Location: `tests/utils/test_cleanup_utilities.py`

Cleanup utilities ensure proper test isolation and resource cleanup.

### File Cleanup

```python
from tests.utils.test_cleanup_utilities import FileCleanupManager

# Clean up test files
file_cleanup = FileCleanupManager()
file_cleanup.cleanup_temp_files()
file_cleanup.cleanup_test_directories()
```

### Database Cleanup

```python
from tests.utils.test_cleanup_utilities import DatabaseCleanupManager

# Clean up test database
db_cleanup = DatabaseCleanupManager()
db_cleanup.cleanup_test_data()
db_cleanup.reset_database_state()
```

### Mock Cleanup

```python
from tests.utils.test_cleanup_utilities import MockCleanupManager

# Clean up mocks
mock_cleanup = MockCleanupManager()
mock_cleanup.reset_all_mocks()
mock_cleanup.clear_mock_history()
```

### External Resource Cleanup

```python
from tests.utils.test_cleanup_utilities import ExternalResourceCleanupManager

# Clean up external resources
resource_cleanup = ExternalResourceCleanupManager()
resource_cleanup.cleanup_network_mocks()
resource_cleanup.cleanup_external_services()
```

## Performance Helpers

### Location: `tests/utils/common_test_utilities.py`

Performance helpers provide utilities for performance testing and measurement.

### Execution Time Measurement

```python
from tests.utils.common_test_utilities import PerformanceHelper

# Measure function execution time
@PerformanceHelper.measure_execution_time
def test_function():
    # Your test code here
    pass

# Assert execution time
PerformanceHelper.assert_execution_time_under(1.0, test_function)
```

### Memory Usage Measurement

```python
from tests.utils.common_test_utilities import PerformanceHelper

# Measure memory usage
with PerformanceHelper.measure_memory() as memory_tracker:
    # Your code here
    pass

print(f"Memory usage: {memory_tracker.peak_memory}MB")
```

### Performance Benchmarking

```python
from tests.utils.common_test_utilities import PerformanceHelper

# Benchmark function performance
benchmark_results = PerformanceHelper.benchmark_function(
    test_function,
    iterations=100
)

print(f"Average execution time: {benchmark_results.average_time:.3f}s")
print(f"Standard deviation: {benchmark_results.std_deviation:.3f}s")
```

## Mock Utilities

### Location: `tests/mocks/`

Mock utilities provide comprehensive mocking capabilities for external dependencies.

### API Mock Utilities

```python
from tests.mocks.api_mock_utilities import APIMockManager

# Create API mock manager
api_mock = APIMockManager()

# Mock API response
api_mock.mock_response('/api/users', 200, {'users': []})

# Mock API error
api_mock.mock_error('/api/users', 500, 'Internal Server Error')

# Verify API calls
api_mock.assert_called_with('/api/users', method='GET')
```

### Database Mock Utilities

```python
from tests.mocks.database_mock_utilities import DatabaseMockManager

# Create database mock manager
db_mock = DatabaseMockManager()

# Mock database query
db_mock.mock_query('SELECT * FROM users', [{'id': 1, 'username': 'test'}])

# Mock database error
db_mock.mock_error('INSERT INTO users', 'Duplicate key error')

# Verify database calls
db_mock.assert_query_called('SELECT * FROM users')
```

### File System Mock Utilities

```python
from tests.mocks.filesystem_mock_utilities import FileSystemMockManager

# Create file system mock manager
fs_mock = FileSystemMockManager()

# Mock file operations
fs_mock.mock_file_exists('/test/file.txt', True)
fs_mock.mock_file_read('/test/file.txt', 'test content')

# Mock file system error
fs_mock.mock_error('/test/file.txt', 'Permission denied')

# Verify file operations
fs_mock.assert_file_read('/test/file.txt')
```

## Usage Examples

### Complete Test Example

```python
import pytest
from tests.utils.common_test_utilities import TestDataGenerator, AssertionHelper
from tests.fixtures.common_fixtures import database_fixture, api_client_fixture

@pytest.fixture
def test_data():
    """Provide test data for tests."""
    return TestDataGenerator.generate_user_data()

@pytest.fixture
def db_session(database_fixture):
    """Provide database session."""
    return database_fixture.get_session()

@pytest.fixture
def api_client(api_client_fixture):
    """Provide API client."""
    return api_client_fixture

def test_user_creation_and_api_call(test_data, db_session, api_client):
    """Test complete user creation and API call workflow."""
    # Arrange
    user_data = test_data

    # Act - Create user in database
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    # Act - Make API call
    response = api_client.post('/api/users', json=user_data)

    # Assert
    AssertionHelper.assert_response_success(response)
    AssertionHelper.assert_record_exists(user, 'users')
    assert user.id is not None
    assert response.json()['user_id'] == user.id
```

### Performance Test Example

```python
import pytest
from tests.utils.common_test_utilities import PerformanceHelper

def test_user_creation_performance():
    """Test user creation performance."""
    # Arrange
    user_data = TestDataGenerator.generate_user_data()

    # Act & Assert
    PerformanceHelper.assert_execution_time_under(
        0.1,  # 100ms threshold
        lambda: create_user(user_data)
    )

@PerformanceHelper.measure_execution_time
def test_bulk_user_creation():
    """Test bulk user creation with performance measurement."""
    users = [TestDataGenerator.generate_user_data() for _ in range(100)]

    for user_data in users:
        create_user(user_data)

    # Performance measurement is automatic with decorator
```

### Mock Test Example

```python
import pytest
from tests.mocks.api_mock_utilities import APIMockManager

def test_external_api_integration():
    """Test external API integration with mocks."""
    # Arrange
    api_mock = APIMockManager()
    api_mock.mock_response('/api/external/data', 200, {'data': 'test'})

    # Act
    result = call_external_api('/api/external/data')

    # Assert
    assert result == {'data': 'test'}
    api_mock.assert_called_with('/api/external/data', method='GET')
```

## Best Practices

1. **Use Appropriate Fixtures**: Choose the right fixture for your test needs
2. **Generate Realistic Data**: Use data generators for consistent, realistic test data
3. **Clean Up Resources**: Always clean up resources after tests
4. **Mock External Dependencies**: Use mocks for external services and APIs
5. **Measure Performance**: Use performance helpers for performance-critical tests
6. **Validate Assertions**: Use assertion helpers for better error messages
7. **Isolate Tests**: Ensure tests are independent and can run in any order

## Troubleshooting

### Common Issues

1. **Fixture Not Found**: Ensure fixtures are properly imported and decorated
2. **Mock Not Working**: Check mock configuration and call verification
3. **Data Generation Issues**: Verify data generator parameters and schemas
4. **Cleanup Failures**: Ensure proper cleanup order and error handling
5. **Performance Issues**: Check performance thresholds and measurement accuracy

### Debug Tips

1. **Use Debug Mode**: Run tests with `-v -s` flags for verbose output
2. **Check Fixture Scope**: Ensure fixture scope matches test requirements
3. **Verify Mock Calls**: Use mock assertion methods to verify calls
4. **Monitor Performance**: Use performance helpers to identify slow tests
5. **Review Cleanup**: Ensure all resources are properly cleaned up
