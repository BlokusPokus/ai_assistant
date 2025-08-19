"""
Internet Tool for web search, news, weather, and content processing.
"""
import logging
from typing import Any, Dict, List, Optional

from ...config.settings import settings
from ..base import Tool
from .internet_internal import (
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

# Import internet-specific error handling
from .internet_error_handler import InternetErrorHandler

logger = logging.getLogger(__name__)

# Import DuckDuckGo search library (try both names)
try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
    USE_DDGS = False
    logger.info("Using duckduckgo-search library")
except ImportError:
    try:
        from ddgs import DDGS
        DUCKDUCKGO_AVAILABLE = True
        USE_DDGS = True
        logger.info("Using ddgs library")
    except ImportError:
        DUCKDUCKGO_AVAILABLE = False
        USE_DDGS = False
        logger.warning(
            "Neither duckduckgo-search nor ddgs library available. Install with: pip install ddgs")


class InternetTool:
    """
    Comprehensive internet tool that provides:
    - Web search capabilities using DuckDuckGo
    - News retrieval with category filtering
    - Wikipedia content search
    - Content processing and validation
    """

    def __init__(self):
        # Initialize any shared resources, tokens, clients, etc.
        self._rate_limit_counter = 0
        self._last_request_time = 0

        # Initialize DuckDuckGo search client
        self._ddgs = None
        if DUCKDUCKGO_AVAILABLE:
            try:
                self._ddgs = DDGS()
                logger.info(
                    "DuckDuckGo search client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DuckDuckGo client: {e}")
                self._ddgs = None

        # Create individual tools
        self.web_search_tool = Tool(
            name="web_search",
            func=self.web_search,
            description="Search the web for information using DuckDuckGo",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query (required)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 5)"
                },
                "safe_search": {
                    "type": "string",
                    "description": "Safe search level: strict, moderate, off (default: moderate)"
                }
            }
        )

        self.get_news_articles_tool = Tool(
            name="get_news_articles",
            func=self.get_news_articles,
            description="Get current news articles by category or topic",
            parameters={
                "category": {
                    "type": "string",
                    "description": "News category: business, technology, sports, etc. (optional)"
                },
                "topic": {
                    "type": "string",
                    "description": "Specific topic to search for (optional)"
                },
                "max_articles": {
                    "type": "integer",
                    "description": "Maximum number of articles (default: 5)"
                }
            }
        )

        self.get_wikipedia_tool = Tool(
            name="get_wikipedia",
            func=self.get_wikipedia,
            description="Search Wikipedia for information on a topic",
            parameters={
                "topic": {
                    "type": "string",
                    "description": "Topic to search for (required)"
                },
                "language": {
                    "type": "string",
                    "description": "Language code (default: en)"
                },
                "summary_only": {
                    "type": "boolean",
                    "description": "Return only summary (default: true)"
                }
            }
        )

        self.search_images_tool = Tool(
            name="search_images",
            func=self.search_images,
            description="Search for images on the web using DuckDuckGo",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Image search query (required)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of images (default: 10)"
                },
                "safe_search": {
                    "type": "string",
                    "description": "Safe search level: strict, moderate, off (default: strict)"
                }
            }
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([
            self.web_search_tool,
            self.get_news_articles_tool,
            self.get_wikipedia_tool,
            self.search_images_tool
        ])

    async def web_search(self, query: str, max_results: int = 5, safe_search: str = "moderate") -> str:
        """Search the web using DuckDuckGo"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_query(query)
            if not is_valid:
                return InternetErrorHandler.handle_internet_error(
                    ValueError(error_msg),
                    "web_search",
                    {"query": query, "max_results": max_results,
                        "safe_search": safe_search}
                )

            max_results = validate_max_results(
                max_results, min_val=1, max_val=20, default=5)
            safe_search = validate_safe_search(safe_search)

            # Check rate limits
            is_valid, new_time = check_rate_limit(self._last_request_time)
            self._last_request_time = new_time

            logger.info(
                f"Web search requested for: {query} (max: {max_results}, safe: {safe_search})")

            # Check if DuckDuckGo is available
            if not DUCKDUCKGO_AVAILABLE or not self._ddgs:
                return InternetErrorHandler.handle_internet_error(
                    Exception("DuckDuckGo search is not available"),
                    "web_search",
                    {"query": query, "max_results": max_results,
                        "safe_search": safe_search}
                )

            # Perform the search
            try:
                search_results = process_duckduckgo_text_results(
                    self._ddgs, query, max_results, USE_DDGS)

                return format_web_search_results(query, search_results, safe_search)

            except Exception as search_error:
                logger.error(f"DuckDuckGo search error: {search_error}")
                return InternetErrorHandler.handle_internet_error(
                    search_error,
                    "web_search",
                    {"query": query, "max_results": max_results,
                        "safe_search": safe_search}
                )

        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return InternetErrorHandler.handle_internet_error(e, "web_search", {"query": query, "max_results": max_results, "safe_search": safe_search})

    async def get_news_articles(self, category: Optional[str] = None, topic: Optional[str] = None, max_articles: int = 5) -> str:
        """Get current news articles by category or topic"""
        try:
            # Validate parameters using internal functions
            max_articles = validate_news_parameters(max_articles)

            logger.info(
                f"News articles request - Category: {category}, Topic: {topic}, Max: {max_articles}")

            # Check rate limits
            is_valid, new_time = check_rate_limit(self._last_request_time)
            self._last_request_time = new_time

            # TODO: Implement News API integration
            # For now, return a placeholder response
            return format_news_articles_response(category, topic, max_articles)

        except Exception as e:
            logger.error(f"Error getting news articles: {e}")
            return InternetErrorHandler.handle_internet_error(e, "get_news_articles", {"category": category, "topic": topic, "max_articles": max_articles})

    async def get_wikipedia(self, topic: str, language: str = "en", summary_only: bool = True) -> str:
        """Search Wikipedia for information on a topic"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_topic(topic)
            if not is_valid:
                return InternetErrorHandler.handle_internet_error(
                    ValueError(error_msg),
                    "get_wikipedia",
                    {"topic": topic, "language": language,
                        "summary_only": summary_only}
                )

            language = validate_language_code(language)

            logger.info(
                f"Wikipedia request - Topic: {topic}, Language: {language}, Summary: {summary_only}")

            # Check rate limits
            is_valid, new_time = check_rate_limit(self._last_request_time)
            self._last_request_time = new_time

            # TODO: Implement Wikipedia API integration
            # For now, return a placeholder response
            return format_wikipedia_response(topic, language, summary_only)

        except Exception as e:
            logger.error(f"Error getting Wikipedia info: {e}")
            return InternetErrorHandler.handle_internet_error(e, "get_wikipedia", {"topic": topic, "language": language, "summary_only": summary_only})

    async def search_images(self, query: str, max_results: int = 10, safe_search: str = "strict") -> str:
        """Search for images on the web using DuckDuckGo"""
        try:
            # Validate parameters using internal functions
            is_valid, error_msg = validate_query(query)
            if not is_valid:
                return InternetErrorHandler.handle_internet_error(
                    ValueError(error_msg),
                    "search_images",
                    {"query": query, "max_results": max_results,
                        "safe_search": safe_search}
                )

            max_results = validate_image_search_parameters(max_results)
            safe_search = validate_safe_search(safe_search)

            # Check rate limits
            is_valid, new_time = check_rate_limit(self._last_request_time)
            self._last_request_time = new_time

            logger.info(
                f"Image search requested for: {query} (max: {max_results}, safe: {safe_search})")

            # Check if DuckDuckGo is available
            if not DUCKDUCKGO_AVAILABLE or not self._ddgs:
                return InternetErrorHandler.handle_internet_error(
                    Exception("DuckDuckGo search is not available"),
                    "search_images",
                    {"query": query, "max_results": max_results,
                        "safe_search": safe_search}
                )

            # Perform image search
            try:
                image_results = process_duckduckgo_image_results(
                    self._ddgs, query, max_results, USE_DDGS)

                return format_image_search_results(query, image_results, safe_search)

            except Exception as search_error:
                logger.error(f"DuckDuckGo image search error: {search_error}")
                return InternetErrorHandler.handle_internet_error(
                    search_error,
                    "search_images",
                    {"query": query, "max_results": max_results,
                        "safe_search": safe_search}
                )

        except Exception as e:
            logger.error(f"Error in image search: {e}")
            return InternetErrorHandler.handle_internet_error(e, "search_images", {"query": query, "max_results": max_results, "safe_search": safe_search})
