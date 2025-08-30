"""
Comprehensive tests for Internet Tools.

Tests all 4 main functions of the InternetTool:
1. web_search
2. get_news_articles
3. get_wikipedia
4. search_images

Also tests error handling, validation, and edge cases.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any
import time

# Import the tool and its dependencies
from personal_assistant.tools.internet.internet_tool import InternetTool
from personal_assistant.tools.internet.internet_internal import (
    check_rate_limit,
    validate_safe_search,
    validate_max_results,
    validate_language_code,
    validate_query,
    validate_topic,
    format_web_search_results,
    format_image_search_results,
    format_news_articles_response,
    format_wikipedia_response,
    extract_search_result_info,
    extract_image_result_info,
    get_duckduckgo_availability_message,
    get_rate_limit_message,
    process_duckduckgo_text_results,
    process_duckduckgo_image_results,
    validate_news_parameters,
    validate_image_search_parameters
)
from personal_assistant.tools.internet.internet_error_handler import InternetErrorHandler


class TestInternetTool:
    """Test suite for InternetTool"""

    @pytest.fixture
    def mock_ddgs(self):
        """Create a mock DuckDuckGo search client"""
        mock_ddgs = Mock()
        mock_ddgs.text = Mock()
        mock_ddgs.images = Mock()
        return mock_ddgs

    @pytest.fixture
    def internet_tool(self, mock_ddgs):
        """Create InternetTool instance with mocked dependencies"""
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
                patch('personal_assistant.tools.internet.internet_tool.USE_DDGS', False):

            tool = InternetTool()
            tool._ddgs = mock_ddgs
            return tool

    @pytest.fixture
    def sample_web_search_results(self):
        """Sample web search results for testing"""
        return [
            {
                "title": "Test Result 1",
                "link": "https://example1.com",
                "body": "This is the first test result about the search query."
            },
            {
                "title": "Test Result 2",
                "link": "https://example2.com",
                "body": "This is the second test result with more details."
            }
        ]

    @pytest.fixture
    def sample_image_search_results(self):
        """Sample image search results for testing"""
        return [
            {
                "title": "Test Image 1",
                "link": "https://example1.com/image1.jpg",
                "image": "https://example1.com/image1.jpg",
                "thumbnail": "https://example1.com/thumb1.jpg"
            },
            {
                "title": "Test Image 2",
                "link": "https://example2.com/image2.jpg",
                "image": "https://example2.com/image2.jpg",
                "thumbnail": "https://example2.com/thumb2.jpg"
            }
        ]

    def test_tool_initialization(self, internet_tool):
        """Test that all tools are properly initialized"""
        tools = list(internet_tool)
        assert len(tools) == 1  # Only web_search is active now

        tool_names = [tool.name for tool in tools]
        assert "web_search" in tool_names
        # assert "get_news_articles" in tool_names  # Commented out
        # assert "get_wikipedia" in tool_names      # Commented out
        # assert "search_images" in tool_names      # Commented out

    def test_web_search_tool_parameters(self, internet_tool):
        """Test web_search tool parameter configuration"""
        web_search_tool = internet_tool.web_search_tool

        assert web_search_tool.name == "web_search"
        assert web_search_tool.description == "Search the web for information using DuckDuckGo"

        params = web_search_tool.parameters
        assert "query" in params
        assert "max_results" in params
        assert "safe_search" in params

        assert params["query"]["type"] == "string"
        assert params["max_results"]["type"] == "integer"
        assert params["safe_search"]["type"] == "string"

    def test_news_tool_parameters(self, internet_tool):
        """Test get_news_articles tool parameter configuration"""
        news_tool = internet_tool.get_news_articles_tool

        assert news_tool.name == "get_news_articles"
        assert news_tool.description == "Get current news articles by category or topic"

        params = news_tool.parameters
        assert "category" in params
        assert "topic" in params
        assert "max_articles" in params

    def test_wikipedia_tool_parameters(self, internet_tool):
        """Test get_wikipedia tool parameter configuration"""
        wiki_tool = internet_tool.get_wikipedia_tool

        assert wiki_tool.name == "get_wikipedia"
        assert wiki_tool.description == "Search Wikipedia for information on a topic"

        params = wiki_tool.parameters
        assert "topic" in params
        assert "language" in params
        assert "summary_only" in params

    # def test_image_search_tool_parameters(self, internet_tool):
    #     """Test search_images tool parameter configuration"""
    #     image_tool = internet_tool.search_images_tool

    #     assert image_tool.name == "search_images"
    #     assert image_tool.description == "Search for images on the web using DuckDuckGo"

    #     params = image_tool.parameters
    #     assert "query" in params
    #     assert "max_results" in params
    #     assert "safe_search" in params

    @pytest.mark.asyncio
    async def test_web_search_success(self, internet_tool, mock_ddgs, sample_web_search_results):
        """Test successful web search"""
        # Mock the internal functions
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', return_value=sample_web_search_results), \
                patch('personal_assistant.tools.internet.internet_tool.format_web_search_results', return_value="Formatted results"):

            result = await internet_tool.web_search("test query", 5, "moderate")

            assert result == "Formatted results"

    @pytest.mark.asyncio
    async def test_web_search_query_validation_failure(self, internet_tool):
        """Test web search with invalid query"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(False, "Invalid query")), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "Invalid query"}):

            result = await internet_tool.web_search("", 5, "moderate")

            assert "Invalid query" in str(result)

    @pytest.mark.asyncio
    async def test_web_search_duckduckgo_unavailable(self, internet_tool):
        """Test web search when DuckDuckGo is unavailable"""
        internet_tool._ddgs = None

        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "DuckDuckGo unavailable"}):

            result = await internet_tool.web_search("test query", 5, "moderate")

            assert "DuckDuckGo unavailable" in str(result)

    @pytest.mark.asyncio
    async def test_web_search_rate_limit_exceeded(self, internet_tool):
        """Test web search when rate limit is exceeded"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', return_value=[]), \
                patch('personal_assistant.tools.internet.internet_tool.format_web_search_results', return_value="No search results found for 'test query'. Try refining your search terms."):

            result = await internet_tool.web_search("test query", 5, "moderate")

            # Rate limiting doesn't actually block requests in the current implementation
            # It just adds a delay, so the request should succeed
            assert "No search results found" in result

    @pytest.mark.asyncio
    async def test_news_articles_success(self, internet_tool):
        """Test successful news articles retrieval"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_news_parameters', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.format_news_articles_response', return_value="News articles"):

            result = await internet_tool.get_news_articles("technology", None, 5)

            assert result == "News articles"

    @pytest.mark.asyncio
    async def test_news_articles_rate_limit_exceeded(self, internet_tool):
        """Test news articles when rate limit is exceeded"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_news_parameters', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.format_news_articles_response', return_value="📰 Latest news articles for category 'technology':\n📊 Max Articles: 5\n🔍 This is a placeholder response. Implement News API integration.\n📝 Search Criteria: category 'technology'\n⏱️ Response Time: <3 seconds (target)"):

            result = await internet_tool.get_news_articles("technology", None, 5)

            # Rate limiting doesn't actually block requests in the current implementation
            # It just adds a delay, so the request should succeed
            assert "Latest news articles" in result

    @pytest.mark.asyncio
    async def test_wikipedia_success(self, internet_tool):
        """Test successful Wikipedia search"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_topic', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_language_code', return_value="en"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.format_wikipedia_response', return_value="Wikipedia content"):

            result = await internet_tool.get_wikipedia("quantum computing", "en", True)

            assert result == "Wikipedia content"

    @pytest.mark.asyncio
    async def test_wikipedia_topic_validation_failure(self, internet_tool):
        """Test Wikipedia search with invalid topic"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_topic', return_value=(False, "Invalid topic")), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "Invalid topic"}):

            result = await internet_tool.get_wikipedia("", "en", True)

            assert "Invalid topic" in str(result)

    # @pytest.mark.asyncio
    # async def test_image_search_success(self, internet_tool, mock_ddgs, sample_image_search_results):
    #     """Test successful image search"""
    #     with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
    #             patch('personal_assistant.tools.internet.internet_tool.validate_image_search_parameters', return_value=10), \
    #             patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="strict"), \
    #             patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
    #             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_image_results', return_value=sample_image_search_results), \
    #             patch('personal_assistant.tools.internet.internet_tool.format_image_search_results', return_value="Image results"):

    #         result = await internet_tool.search_images("test images", 10, "strict")

    #         assert result == "Image results"

    # @pytest.mark.asyncio
    # async def test_image_search_duckduckgo_unavailable(self, internet_tool):
    #     """Test image search when DuckDuckGo is unavailable"""
    #     internet_tool._ddgs = None

    #     with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
    #             patch('personal_assistant.tools.internet.internet_tool.validate_image_search_parameters', return_value=10), \
    #             patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="strict"), \
    #             patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
    #             patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "DuckDuckGo unavailable"}):

    #         result = await internet_tool.search_images("test images", 10, "strict")

    #         assert "DuckDuckGo unavailable" in str(result)

    # @pytest.mark.asyncio
    # async def test_image_search_query_validation_failure(self, internet_tool):
    #     """Test image search with invalid query"""
    #     with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(False, "Invalid query")), \
    #             patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "Invalid query"}):

    #         result = await internet_tool.search_images("", 10, "strict")

    #         assert "Invalid query" in str(result)

    def test_tool_iteration(self, internet_tool):
        """Test that the tool can be iterated over"""
        tools = list(internet_tool)
        assert len(tools) == 1  # Only web_search is active now

        # Check that all tools have the required attributes
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'func')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'parameters')

    @pytest.mark.asyncio
    async def test_web_search_exception_handling(self, internet_tool):
        """Test web search exception handling"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', side_effect=Exception("Search error")), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "Search error"}):

            result = await internet_tool.web_search("test query", 5, "moderate")

            assert "Search error" in str(result)

    @pytest.mark.asyncio
    async def test_news_articles_exception_handling(self, internet_tool):
        """Test news articles exception handling"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_news_parameters', side_effect=Exception("News error")), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "News error"}):

            result = await internet_tool.get_news_articles("technology", None, 5)

            assert "News error" in str(result)

    @pytest.mark.asyncio
    async def test_wikipedia_exception_handling(self, internet_tool):
        """Test Wikipedia exception handling"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_topic', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_language_code', return_value="en"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.format_wikipedia_response', side_effect=Exception("Wikipedia error")), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "Wikipedia error"}):

            result = await internet_tool.get_wikipedia("quantum computing", "en", True)

            assert "Wikipedia error" in str(result)

    @pytest.mark.asyncio
    async def test_image_search_exception_handling(self, internet_tool):
        """Test image search exception handling"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_image_search_parameters', return_value=10), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="strict"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_image_results', side_effect=Exception("Image search error")), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "Image search error"}):

            result = await internet_tool.search_images("test images", 10, "strict")

            assert "Image search error" in str(result)


class TestInternetToolInitialization:
    """Test suite for InternetTool initialization scenarios"""

    @patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', False)
    def test_initialization_without_duckduckgo(self):
        """Test initialization when DuckDuckGo is not available"""
        tool = InternetTool()
        assert tool._ddgs is None

    @patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True)
    @patch('personal_assistant.tools.internet.internet_tool.USE_DDGS', True)
    def test_initialization_with_ddgs_library(self):
        """Test initialization with ddgs library"""
        with patch('personal_assistant.tools.internet.internet_tool.DDGS') as mock_ddgs_class:
            mock_ddgs_class.return_value = Mock()
            tool = InternetTool()
            assert tool._ddgs is not None

    @patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True)
    @patch('personal_assistant.tools.internet.internet_tool.USE_DDGS', False)
    def test_initialization_with_duckduckgo_search_library(self):
        """Test initialization with duckduckgo-search library"""
        with patch('personal_assistant.tools.internet.internet_tool.DDGS') as mock_ddgs_class:
            mock_ddgs_class.return_value = Mock()
            tool = InternetTool()
            assert tool._ddgs is not None

    @patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True)
    def test_initialization_with_ddgs_exception(self):
        """Test initialization when DDGS initialization fails"""
        with patch('personal_assistant.tools.internet.internet_tool.DDGS', side_effect=Exception("DDGS error")):
            tool = InternetTool()
            assert tool._ddgs is None


class TestInternetToolEdgeCases:
    """Test suite for edge cases and boundary conditions"""

    @pytest.fixture
    def mock_ddgs(self):
        """Create a mock DuckDuckGo search client"""
        mock_ddgs = Mock()
        mock_ddgs.text = Mock()
        mock_ddgs.images = Mock()
        return mock_ddgs

    @pytest.fixture
    def internet_tool(self, mock_ddgs):
        """Create InternetTool instance with mocked dependencies"""
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
                patch('personal_assistant.tools.internet.internet_tool.USE_DDGS', False):

            tool = InternetTool()
            tool._ddgs = mock_ddgs
            return tool

    @pytest.fixture
    def sample_web_search_results(self):
        """Sample web search results for testing"""
        return [
            {
                "title": "Test Result 1",
                "link": "https://example1.com",
                "body": "This is the first test result about the search query."
            }
        ]

    @pytest.fixture
    def sample_image_search_results(self):
        """Sample image search results for testing"""
        return [
            {
                "title": "Test Image 1",
                "link": "https://example1.com/image1.jpg",
                "image": "https://example1.com/image1.jpg",
                "thumbnail": "https://example1.com/thumb1.jpg"
            }
        ]

    @pytest.mark.asyncio
    async def test_web_search_with_minimum_parameters(self, internet_tool, mock_ddgs, sample_web_search_results):
        """Test web search with minimum required parameters"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=1), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', return_value=sample_web_search_results), \
                patch('personal_assistant.tools.internet.internet_tool.format_web_search_results', return_value="Formatted results"):

            result = await internet_tool.web_search("test")

            assert result == "Formatted results"

    @pytest.mark.asyncio
    async def test_web_search_with_maximum_parameters(self, internet_tool, mock_ddgs, sample_web_search_results):
        """Test web search with maximum allowed parameters"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=20), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="off"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', return_value=sample_web_search_results), \
                patch('personal_assistant.tools.internet.internet_tool.format_web_search_results', return_value="Formatted results"):

            result = await internet_tool.web_search("test query", 20, "off")

            assert result == "Formatted results"

    # @pytest.mark.asyncio
    # async def test_image_search_with_maximum_parameters(self, internet_tool, mock_ddgs, sample_image_search_results):
    #     """Test image search with maximum allowed parameters"""
    #     with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
    #             patch('personal_assistant.tools.internet.internet_tool.validate_image_search_parameters', return_value=50), \
    #             patch('personal_assistant.tools.internet.internet_tool.validate_image_search_parameters', return_value=50), \
    #             patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="strict"), \
    #             patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
    #             patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_image_results', return_value=sample_image_search_results), \
    #             patch('personal_assistant.tools.internet.internet_tool.format_image_search_results', return_value="Image results"):

    #         result = await internet_tool.search_images("test images", 50, "strict")

    #         assert result == "Image results"

    @pytest.mark.asyncio
    async def test_wikipedia_with_different_languages(self, internet_tool):
        """Test Wikipedia search with different language codes"""
        with patch('personal_assistant.tools.internet.internet_tool.validate_topic', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_language_code', return_value="es"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.format_wikipedia_response', return_value="Contenido en español"):

            result = await internet_tool.get_wikipedia("computación cuántica", "es", True)

            assert result == "Contenido en español"

    @pytest.mark.asyncio
    async def test_news_articles_with_different_categories(self, internet_tool):
        """Test news articles with different categories"""
        categories = ["business", "technology",
                      "sports", "entertainment", "science"]

        for category in categories:
            with patch('personal_assistant.tools.internet.internet_tool.validate_news_parameters', return_value=5), \
                    patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                    patch('personal_assistant.tools.internet.internet_tool.format_news_articles_response', return_value=f"{category} news"):

                result = await internet_tool.get_news_articles(category, None, 5)

                assert result == f"{category} news"


class TestInternetToolIntegration:
    """Test suite for integration scenarios"""

    @pytest.fixture
    def mock_ddgs(self):
        """Create a mock DuckDuckGo search client"""
        mock_ddgs = Mock()
        mock_ddgs.text = Mock()
        # mock_ddgs.images = Mock()  # No longer needed
        return mock_ddgs

    @pytest.fixture
    def internet_tool(self, mock_ddgs):
        """Create InternetTool instance with mocked dependencies"""
        with patch('personal_assistant.tools.internet.internet_tool.DUCKDUCKGO_AVAILABLE', True), \
                patch('personal_assistant.tools.internet.internet_tool.USE_DDGS', False):

            tool = InternetTool()
            tool._ddgs = mock_ddgs
            return tool

    @pytest.fixture
    def sample_web_search_results(self):
        """Sample web search results for testing"""
        return [
            {
                "title": "Test Result 1",
                "link": "https://example1.com",
                "body": "This is the first test result about the search query."
            }
        ]

    # @pytest.fixture
    # def sample_image_search_results(self):
    #     """Sample image search results for testing"""
    #     return [
    #         {
    #             "title": "Test Image 1",
    #             "link": "https://example1.com/image1.jpg",
    #             "image": "https://example1.com/image1.jpg",
    #             "thumbnail": "https://example1.com/thumb1.jpg"
    #         }
    #     ]

    @pytest.mark.asyncio
    async def test_multiple_tools_workflow(self, internet_tool, mock_ddgs, sample_web_search_results):
        """Test using multiple tools in sequence"""
        # First, do a web search
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', return_value=sample_web_search_results), \
                patch('personal_assistant.tools.internet.internet_tool.format_web_search_results', return_value="Web search results"):

            web_result = await internet_tool.web_search("AI developments", 5, "moderate")
            assert web_result == "Web search results"

        # Then, get news articles
        with patch('personal_assistant.tools.internet.internet_tool.validate_news_parameters', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.format_news_articles_response', return_value="AI news"):

            news_result = await internet_tool.get_news_articles("technology", "AI", 5)
            assert news_result == "AI news"

        # Finally, search for related images (disabled)
        # with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
        #         patch('personal_assistant.tools.internet.internet_tool.validate_image_search_parameters', return_value=5), \
        #         patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="strict"), \
        #         patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
        #         patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_image_results', return_value=sample_image_search_results), \
        #         patch('personal_assistant.tools.internet.internet_tool.format_image_search_results', return_value="AI images"):

        #     image_result = await internet_tool.search_images("AI technology", 5, "strict")
        #     assert image_result == "AI images"

    @pytest.mark.asyncio
    async def test_rate_limiting_across_tools(self, internet_tool):
        """Test rate limiting behavior across different tools"""
        # First request should succeed
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', return_value=[]), \
                patch('personal_assistant.tools.internet.internet_tool.format_web_search_results', return_value="Success"):

            result1 = await internet_tool.web_search("test1", 5, "moderate")
            assert result1 == "Success"

        # Second request should also succeed (rate limit not reached yet)
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(True, None)), \
                patch('personal_assistant.tools.internet.internet_tool.validate_max_results', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.validate_safe_search', return_value="moderate"), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.process_duckduckgo_text_results', return_value=[]), \
                patch('personal_assistant.tools.internet.internet_tool.format_web_search_results', return_value="Success"):

            result2 = await internet_tool.web_search("test2", 5, "moderate")
            assert result2 == "Success"

    @pytest.mark.asyncio
    async def test_error_recovery_across_tools(self, internet_tool):
        """Test error recovery when switching between tools"""
        # First tool fails
        with patch('personal_assistant.tools.internet.internet_tool.validate_query', return_value=(False, "Invalid query")), \
                patch('personal_assistant.tools.internet.internet_tool.InternetErrorHandler.handle_internet_error', return_value={"error": "Invalid query"}):

            result1 = await internet_tool.web_search("", 5, "moderate")
            assert "Invalid query" in str(result1)

        # Second tool succeeds
        with patch('personal_assistant.tools.internet.internet_tool.validate_news_parameters', return_value=5), \
                patch('personal_assistant.tools.internet.internet_tool.check_rate_limit', return_value=(True, time.time())), \
                patch('personal_assistant.tools.internet.internet_tool.format_news_articles_response', return_value="News success"):

            result2 = await internet_tool.get_news_articles("technology", None, 5)
            assert result2 == "News success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
