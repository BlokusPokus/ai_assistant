"""
Internal functions for Internet Tool.

This module contains internal utility functions and helper methods
that are used by the main InternetTool class.
"""

import logging
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def check_rate_limit(last_request_time: float, min_delay: float = 1.0) -> tuple[bool, float]:
    """Check if we're within rate limits and update timing"""
    current_time = time.time()
    time_since_last = current_time - last_request_time

    if time_since_last < min_delay:
        sleep_time = min_delay - time_since_last
        time.sleep(sleep_time)
        current_time = time.time()

    return True, current_time


def validate_safe_search(safe_search: str) -> str:
    """Validate and normalize safe search parameter"""
    valid_levels = ["strict", "moderate", "off"]
    if safe_search not in valid_levels:
        logger.warning(
            f"Invalid safe_search value: {safe_search}, defaulting to moderate")
        return "moderate"
    return safe_search


def validate_max_results(max_results: int, min_val: int = 1, max_val: int = 20, default: int = 5) -> int:
    """Validate and normalize max_results parameter"""
    if max_results < min_val or max_results > max_val:
        logger.warning(
            f"Invalid max_results: {max_results}, defaulting to {default}")
        return default
    return max_results


def validate_language_code(language: str, default: str = "en") -> str:
    """Validate and normalize language code parameter"""
    if not language or len(language) != 2:
        logger.warning(
            f"Invalid language: {language}, defaulting to {default}")
        return default
    return language


def validate_query(query: str) -> tuple[bool, str]:
    """Validate search query parameter"""
    if not query or not query.strip():
        return False, "Error: Search query is required"
    return True, ""


def validate_topic(topic: str) -> tuple[bool, str]:
    """Validate topic parameter"""
    if not topic or not topic.strip():
        return False, "Error: Topic is required"
    return True, ""


def format_web_search_results(query: str, search_results: List[Dict[str, str]], safe_search: str) -> str:
    """Format web search results for display"""
    if not search_results:
        return f"No search results found for '{query}'. Try refining your search terms."

    response = f"🔍 Web Search Results for '{query}':\n"
    response += f"📊 Found {len(search_results)} results\n"
    response += f"🔒 Safe Search: {safe_search}\n\n"

    for i, result in enumerate(search_results, 1):
        response += f"{i}. **{result['title']}**\n"
        response += f"   📍 {result['link']}\n"
        response += f"   📝 {result['snippet']}\n\n"

    response += f"⏱️ Response Time: <3 seconds (target)"
    return response


def format_image_search_results(query: str, image_results: List[Dict[str, str]], safe_search: str) -> str:
    """Format image search results for display"""
    if not image_results:
        return f"No image results found for '{query}'. Try refining your search terms."

    response = f"🖼️ Image Search Results for '{query}':\n"
    response += f"📊 Found {len(image_results)} images\n"
    response += f"🔒 Safe Search: {safe_search}\n\n"

    for i, result in enumerate(image_results, 1):
        response += f"{i}. **{result['title']}**\n"
        response += f"   🖼️ {result['image_url']}\n"
        response += f"   📍 {result['source_url']}\n\n"

    response += f"⏱️ Response Time: <3 seconds (target)"
    return response


def format_news_articles_response(category: str = None, topic: str = None, max_articles: int = 5) -> str:
    """Format news articles response"""
    if category and topic:
        search_desc = f"category '{category}' and topic '{topic}'"
    elif category:
        search_desc = f"category '{category}'"
    elif topic:
        search_desc = f"topic '{topic}'"
    else:
        search_desc = "general news"

    return f"📰 Latest news articles for {search_desc}:\n" \
           f"📊 Max Articles: {max_articles}\n" \
           f"🔍 This is a placeholder response. Implement News API integration.\n" \
           f"📝 Search Criteria: {search_desc}\n" \
           f"⏱️ Response Time: <3 seconds (target)"


def format_wikipedia_response(topic: str, language: str = "en", summary_only: bool = True) -> str:
    """Format Wikipedia response"""
    return f"📚 Wikipedia information for '{topic}':\n" \
           f"🌐 Language: {language}\n" \
           f"📝 Summary Only: {summary_only}\n" \
           f"🔍 This is a placeholder response. Implement Wikipedia API integration.\n" \
           f"📖 Topic: {topic}\n" \
           f"⏱️ Response Time: <3 seconds (target)"


def extract_search_result_info(result: Dict[str, Any]) -> Dict[str, str]:
    """Extract and clean search result information"""
    title = result.get('title', 'No title')
    # Try different possible link keys based on test results
    link = result.get('href') or result.get(
        'link') or result.get('url') or 'No link'
    snippet = result.get('body', 'No description')

    # Clean and format the snippet
    if snippet and len(snippet) > 200:
        snippet = snippet[:200] + "..."

    return {
        'title': title,
        'link': link,
        'snippet': snippet
    }


def extract_image_result_info(result: Dict[str, Any]) -> Dict[str, str]:
    """Extract and clean image result information"""
    title = result.get('title', 'No title')
    image_url = result.get('image', 'No image URL')
    source_url = result.get('link', 'No source URL')

    return {
        'title': title,
        'image_url': image_url,
        'source_url': source_url
    }


def get_duckduckgo_availability_message() -> str:
    """Get message about DuckDuckGo availability"""
    return "Error: DuckDuckGo search is not available. Please install the required library:\n" \
           "pip install ddgs"


def get_rate_limit_message() -> str:
    """Get rate limit exceeded message"""
    return "Error: Rate limit exceeded. Please try again later."


def process_duckduckgo_text_results(ddgs_client, query: str, max_results: int, use_ddgs: bool) -> List[Dict[str, str]]:
    """Process DuckDuckGo text search results"""
    search_results = []

    try:
        if use_ddgs:
            # New ddgs API (synchronous)
            results = ddgs_client.text(query, max_results=max_results)
            for result in results:
                if len(search_results) >= max_results:
                    break
                search_results.append(extract_search_result_info(result))
        else:
            # Old duckduckgo-search API (async)
            # Note: This would need to be handled differently in the async context
            logger.warning(
                "Async DuckDuckGo API not fully implemented in internal function")
            return []

        return search_results

    except Exception as e:
        logger.error(f"Error processing DuckDuckGo text results: {e}")
        return []


def process_duckduckgo_image_results(ddgs_client, query: str, max_results: int, use_ddgs: bool) -> List[Dict[str, str]]:
    """Process DuckDuckGo image search results"""
    image_results = []

    try:
        if use_ddgs:
            # New ddgs API (synchronous)
            results = ddgs_client.images(query, max_results=max_results)
            for result in results:
                if len(image_results) >= max_results:
                    break
                image_results.append(extract_image_result_info(result))
        else:
            # Old duckduckgo-search API (async)
            # Note: This would need to be handled differently in the async context
            logger.warning(
                "Async DuckDuckGo API not fully implemented in internal function")
            return []

        return image_results

    except Exception as e:
        logger.error(f"Error processing DuckDuckGo image results: {e}")
        return []


def validate_news_parameters(max_articles: int) -> int:
    """Validate news article parameters"""
    return validate_max_results(max_articles, min_val=1, max_val=20, default=5)


def validate_image_search_parameters(max_results: int) -> int:
    """Validate image search parameters"""
    return validate_max_results(max_results, min_val=1, max_val=50, default=10)
