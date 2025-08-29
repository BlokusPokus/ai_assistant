"""
Pytest configuration for tools tests.

This file provides common fixtures and configuration for testing tools.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Configure pytest for async tests


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'NOTION_API_KEY': 'test-api-key',
        'NOTION_ROOT_PAGE_ID': 'test-root-page-id',
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'GOOGLE_API_KEY': 'test-google-key'
    }):
        yield


@pytest.fixture(autouse=True)
def mock_logging():
    """Mock logging to avoid noise during tests."""
    with patch('personal_assistant.config.logging_config.get_logger') as mock_logger:
        mock_logger.return_value = Mock()
        yield mock_logger


@pytest.fixture
def mock_notion_client():
    """Create a mock Notion client for testing."""
    mock_client = Mock()
    mock_client.pages = Mock()
    mock_client.blocks = Mock()
    mock_client.search = Mock()
    return mock_client


@pytest.fixture
def sample_notion_page_data():
    """Sample Notion page data for testing."""
    return {
        "id": "test-page-id-123",
        "properties": {
            "title": {
                "title": [{"plain_text": "Test Note"}]
            },
            "Tags": {
                "multi_select": [
                    {"name": "test"},
                    {"name": "example"}
                ]
            },
            "Category": {
                "select": {"name": "Work"}
            }
        }
    }


@pytest.fixture
def sample_notion_blocks_data():
    """Sample Notion blocks data for testing."""
    return {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "This is test content"}]
                }
            },
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "Test Heading"}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"plain_text": "Test list item"}]
                }
            }
        ]
    }


@pytest.fixture
def mock_tool_registry():
    """Create a mock tool registry for testing."""
    mock_registry = Mock()
    mock_registry.get_tool = Mock()
    mock_registry.list_tools = Mock(return_value=[])
    return mock_registry


@pytest.fixture
def mock_agent_state():
    """Create a mock agent state for testing."""
    mock_state = Mock()
    mock_state.user_input = "Test user input"
    mock_state.last_tool_result = None
    mock_state.focus = ["general"]
    mock_state.step_count = 0
    mock_state.memory_context = []
    mock_state.conversation_history = []
    return mock_state


# Configure pytest options
def pytest_configure(config):
    """Configure pytest with custom options."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add asyncio marker to async tests
        if "async" in item.name or "async" in str(item.function):
            item.add_marker(pytest.mark.asyncio)

        # Add unit marker to unit tests
        if "test_" in item.name and "integration" not in item.name:
            item.add_marker(pytest.mark.unit)
