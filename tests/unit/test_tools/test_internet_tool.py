"""
Unit tests for Internet Tool.

This module tests the Internet tool functionality including
web search, parameter validation, error handling, and rate limiting.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

from personal_assistant.tools.internet.internet_tool import InternetTool, DUCKDUCKGO_AVAILABLE, USE_DDGS
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import ToolDataGenerator


class TestInternetTool:
    """Test cases for Internet Tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.internet_tool = InternetTool()
        self.test_query = "Python programming"
        self.test_max_results = 5
        self.test_safe_search = "moderate"

    def test_internet_tool_initialization(self):
        """Test Internet tool initialization."""
        assert self.internet_tool is not None
        assert hasattr(self.internet_tool, 'web_search_tool')
        assert hasattr(self.internet_tool, '_rate_limit_counter')
        assert hasattr(self.internet_tool, '_last_request_time')
        assert self.internet_tool._rate_limit_counter == 0
        assert self.internet_tool._last_request_time == 0

    def test_internet_tool_iteration(self):
        """Test that Internet tool is iterable and returns all tools."""
        tools = list(self.internet_tool)
        assert len(tools) == 1  # Only web_search_tool is currently active
        
        tool_names = [tool.name for tool in tools]
        assert "web_search" in tool_names

    def test_web_search_tool_properties(self):
        """Test web search tool properties."""
        tool = self.internet_tool.web_search_tool
        assert tool.name == "web_search"
        assert "Search the web for information using DuckDuckGo" in tool.description
        assert "query" in tool.parameters
        assert "max_results" in tool.parameters
        assert "safe_search" in tool.parameters

    def test_web_search_tool_parameter_types(self):
        """Test web search tool parameter types."""
        tool = self.internet_tool.web_search_tool
        params = tool.parameters
        
        assert params["query"]["type"] == "string"
        assert params["max_results"]["type"] == "integer"
        assert params["safe_search"]["type"] == "string"

    def test_web_search_tool_parameter_descriptions(self):
        """Test web search tool parameter descriptions."""
        tool = self.internet_tool.web_search_tool
        params = tool.parameters
        
        assert "required" in params["query"]["description"]
        assert "default: 5" in params["max_results"]["description"]
        assert "strict, moderate, off" in params["safe_search"]["description"]

    @pytest.mark.asyncio
    async def test_web_search_empty_query(self):
        """Test web search with empty query."""
        result = await self.internet_tool.web_search("")
        
        # Check if result is a dict (error response) or string
        if isinstance(result, dict):
            assert result.get("error", False)
            assert "query" in result.get("error_message", "").lower()
        else:
            assert "Error" in result or "query" in result.lower()

    @pytest.mark.asyncio
    async def test_web_search_none_query(self):
        """Test web search with None query."""
        result = await self.internet_tool.web_search(None)
        
        # Should return error response
        if isinstance(result, dict):
            assert result.get("error", False)
        else:
            assert "Error" in result

    @pytest.mark.asyncio
    async def test_web_search_invalid_max_results(self):
        """Test web search with invalid max_results."""
        result = await self.internet_tool.web_search(
            self.test_query,
            max_results=50  # Too high
        )
        
        # Should still work but with default max_results
        assert isinstance(result, str)
        assert "Web Search Results" in result or "Search results" in result or "Error" in result

    @pytest.mark.asyncio
    async def test_web_search_invalid_safe_search(self):
        """Test web search with invalid safe_search."""
        result = await self.internet_tool.web_search(
            self.test_query,
            safe_search="invalid_level"
        )
        
        # Should still work but with default safe_search
        assert isinstance(result, str)
        assert "Web Search Results" in result or "Search results" in result or "Error" in result

    @pytest.mark.asyncio
    async def test_web_search_duckduckgo_not_available(self):
        """Test web search when DuckDuckGo is not available."""
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', False):
            result = await self.internet_tool.web_search(self.test_query)
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
                assert "not available" in result.get("error_message", "").lower()
            else:
                assert "Error" in result or "not available" in result.lower()

    @pytest.mark.asyncio
    async def test_web_search_ddgs_client_none(self):
        """Test web search when DDGS client is None."""
        # Mock DUCKDUCKGO_AVAILABLE as True but set _ddgs to None
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True):
            self.internet_tool._ddgs = None
            result = await self.internet_tool.web_search(self.test_query)
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
                assert "not available" in result.get("error_message", "").lower()
            else:
                assert "Error" in result or "not available" in result.lower()

    @pytest.mark.asyncio
    async def test_web_search_success_mocked(self):
        """Test successful web search with mocked DDGS."""
        mock_ddgs = Mock()
        mock_search_results = [
            {
                "title": "Python Programming Tutorial",
                "body": "Learn Python programming basics",
                "href": "https://example.com/python-tutorial"
            },
            {
                "title": "Python Documentation",
                "body": "Official Python documentation",
                "href": "https://docs.python.org"
            }
        ]
        
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results') as mock_process, \
             patch('personal_assistant.tools.internet.internet_tool.format_web_search_results') as mock_format:
            
            self.internet_tool._ddgs = mock_ddgs
            mock_process.return_value = mock_search_results
            mock_format.return_value = "Search results for 'Python programming':\n1. Python Programming Tutorial\n2. Python Documentation"
            
            result = await self.internet_tool.web_search(
                self.test_query,
                max_results=self.test_max_results,
                safe_search=self.test_safe_search
            )
            
            assert "Search results" in result
            assert "Python programming" in result
            mock_process.assert_called_once_with(mock_ddgs, self.test_query, self.test_max_results, USE_DDGS)
            mock_format.assert_called_once_with(self.test_query, mock_search_results, self.test_safe_search)

    @pytest.mark.asyncio
    async def test_web_search_process_error(self):
        """Test web search when process_duckduckgo_text_results fails."""
        mock_ddgs = Mock()
        
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results') as mock_process:
            
            self.internet_tool._ddgs = mock_ddgs
            mock_process.side_effect = Exception("Search processing failed")
            
            result = await self.internet_tool.web_search(self.test_query)
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_web_search_max_results_validation(self):
        """Test web search max_results parameter validation."""
        mock_ddgs = Mock()
        
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results') as mock_process, \
             patch('personal_assistant.tools.internet.internet_tool.format_web_search_results') as mock_format:
            
            self.internet_tool._ddgs = mock_ddgs
            mock_process.return_value = []
            mock_format.return_value = "No results found"
            
            # Test with float max_results (should be converted to int)
            result = await self.internet_tool.web_search(
                self.test_query,
                max_results=3.0
            )
            
            # Verify that process_duckduckgo_text_results was called with int
            mock_process.assert_called_once()
            call_args = mock_process.call_args[0]
            assert isinstance(call_args[2], int)  # max_results should be int

    @pytest.mark.asyncio
    async def test_web_search_rate_limiting(self):
        """Test web search rate limiting functionality."""
        mock_ddgs = Mock()
        
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
             patch('personal_assistant.tools.internet.internet_tool.check_rate_limit') as mock_rate_limit, \
             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results') as mock_process, \
             patch('personal_assistant.tools.internet.internet_tool.format_web_search_results') as mock_format:
            
            self.internet_tool._ddgs = mock_ddgs
            mock_rate_limit.return_value = (True, 1234567890.0)
            mock_process.return_value = []
            mock_format.return_value = "No results found"
            
            result = await self.internet_tool.web_search(self.test_query)
            
            # Verify rate limiting was checked
            mock_rate_limit.assert_called_once()
            assert self.internet_tool._last_request_time == 1234567890.0

    @pytest.mark.asyncio
    async def test_web_search_parameter_validation_chain(self):
        """Test that all parameter validation functions are called."""
        mock_ddgs = Mock()
        
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
             patch('personal_assistant.tools.internet.internet_tool.validate_query') as mock_validate_query, \
             patch('personal_assistant.tools.internet.internet_tool.validate_max_results') as mock_validate_max, \
             patch('personal_assistant.tools.internet.internet_tool.validate_safe_search') as mock_validate_safe, \
             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results') as mock_process, \
             patch('personal_assistant.tools.internet.internet_tool.format_web_search_results') as mock_format:
            
            self.internet_tool._ddgs = mock_ddgs
            mock_validate_query.return_value = (True, "")
            mock_validate_max.return_value = 5
            mock_validate_safe.return_value = "moderate"
            mock_process.return_value = []
            mock_format.return_value = "No results found"
            
            result = await self.internet_tool.web_search(
                self.test_query,
                max_results=10,
                safe_search="strict"
            )
            
            # Verify all validation functions were called
            mock_validate_query.assert_called_once_with(self.test_query)
            mock_validate_max.assert_called_once_with(10, min_val=1, max_val=20, default=5)
            mock_validate_safe.assert_called_once_with("strict")

    @pytest.mark.asyncio
    async def test_web_search_general_exception(self):
        """Test web search with general exception."""
        with patch('personal_assistant.tools.internet.internet_tool.validate_query') as mock_validate:
            mock_validate.side_effect = Exception("Unexpected error")
            
            result = await self.internet_tool.web_search(self.test_query)
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    def test_tool_categories(self):
        """Test that tools can have categories set."""
        tool = self.internet_tool.web_search_tool
        tool.set_category("Internet")
        assert tool.category == "Internet"
        
        # Test that category is returned correctly
        assert tool.category == "Internet"

    def test_tool_user_intent_tracking(self):
        """Test that tools can track user intent."""
        tool = self.internet_tool.web_search_tool
        
        # Test setting user intent
        tool.set_user_intent("Search for information")
        assert tool.get_user_intent() == "Search for information"
        
        # Test default user intent
        new_tool = InternetTool().web_search_tool
        assert new_tool.get_user_intent() == "Unknown user intent"

    def test_duckduckgo_availability_constants(self):
        """Test DuckDuckGo availability constants."""
        # These are module-level constants, so we test their existence
        assert hasattr(InternetTool, '__module__')
        
        # Test that the constants exist in the module
        import personal_assistant.tools.internet.internet_tool as internet_module
        assert hasattr(internet_module, 'DUCKDUCKGO_AVAILABLE')
        assert hasattr(internet_module, 'USE_DDGS')

    @pytest.mark.asyncio
    async def test_web_search_with_different_parameter_combinations(self):
        """Test web search with various parameter combinations."""
        mock_ddgs = Mock()
        
        test_cases = [
            {"query": "test", "max_results": 1, "safe_search": "strict"},
            {"query": "another test", "max_results": 10, "safe_search": "off"},
            {"query": "yet another", "max_results": 3, "safe_search": "moderate"},
        ]
        
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results') as mock_process, \
             patch('personal_assistant.tools.internet.internet_tool.format_web_search_results') as mock_format:
            
            self.internet_tool._ddgs = mock_ddgs
            mock_process.return_value = []
            mock_format.return_value = "Test results"
            
            for case in test_cases:
                result = await self.internet_tool.web_search(**case)
                assert isinstance(result, str)
                assert "Test results" in result

    @pytest.mark.asyncio
    async def test_web_search_logging_behavior(self):
        """Test that web search logs appropriate information."""
        mock_ddgs = Mock()
        
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
             patch('personal_assistant.tools.internet.internet_tool.logger') as mock_logger, \
             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results') as mock_process, \
             patch('personal_assistant.tools.internet.internet_tool.format_web_search_results') as mock_format:
            
            self.internet_tool._ddgs = mock_ddgs
            mock_process.return_value = []
            mock_format.return_value = "Test results"
            
            result = await self.internet_tool.web_search(self.test_query)
            
            # Verify that info logging was called
            mock_logger.info.assert_called()
            # Check that the log message contains the query
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any(self.test_query in call for call in log_calls)

    def test_internet_tool_rate_limit_properties(self):
        """Test Internet tool rate limiting properties."""
        # Test initial state
        assert self.internet_tool._rate_limit_counter == 0
        assert self.internet_tool._last_request_time == 0
        
        # Test that properties can be modified
        self.internet_tool._rate_limit_counter = 5
        self.internet_tool._last_request_time = 1234567890.0
        
        assert self.internet_tool._rate_limit_counter == 5
        assert self.internet_tool._last_request_time == 1234567890.0

    @pytest.mark.asyncio
    async def test_web_search_error_handling_consistency(self):
        """Test that error handling is consistent across different error types."""
        error_scenarios = [
            ("", "empty query"),
            (None, "None query"),
            ("test", "DuckDuckGo unavailable"),
        ]
        
        for query, scenario in error_scenarios:
            if scenario == "DuckDuckGo unavailable":
                with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', False):
                    result = await self.internet_tool.web_search(query)
            else:
                result = await self.internet_tool.web_search(query)
            
            # All error scenarios should return consistent error format
            if isinstance(result, dict):
                assert "error" in result
                assert "error_message" in result
            else:
                assert isinstance(result, str)
                assert "Error" in result or "error" in result.lower()

    def test_web_search_tool_parameter_validation(self):
        """Test that tool parameters are properly defined."""
        tool = self.internet_tool.web_search_tool
        params = tool.parameters
        
        # Test required parameters
        assert "query" in params
        assert params["query"]["type"] == "string"
        assert "required" in params["query"]["description"]
        
        # Test optional parameters
        assert "max_results" in params
        assert params["max_results"]["type"] == "integer"
        assert "default" in params["max_results"]["description"]
        
        assert "safe_search" in params
        assert params["safe_search"]["type"] == "string"
        assert "default" in params["safe_search"]["description"]

    def test_web_search_tool_description_quality(self):
        """Test that tool description is informative."""
        tool = self.internet_tool.web_search_tool
        description = tool.description
        
        # Description should contain key information
        assert "web" in description.lower()
        assert "search" in description.lower()
        assert "duckduckgo" in description.lower() or "duck" in description.lower()
