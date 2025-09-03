"""
Unit tests for internal internet tool functions.

Tests validation, formatting, extraction, and utility functions
used by the internet tools.
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

# Import the functions to test
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
    process_duckduckgo_text_results,
    process_duckduckgo_image_results,
    validate_news_parameters,
    validate_image_search_parameters
)


class TestRateLimitFunctions:
    """Test suite for rate limiting functions"""

    def test_check_rate_limit_allowed(self):
        """Test rate limit check when enough time has passed"""
        last_request_time = time.time() - 2  # 2 seconds ago
        is_allowed, new_time = check_rate_limit(last_request_time)

        assert is_allowed is True
        assert new_time > last_request_time

    def test_check_rate_limit_blocked(self):
        """Test rate limit check when not enough time has passed"""
        last_request_time = time.time() - 0.1  # 0.1 seconds ago (too recent)
        is_allowed, new_time = check_rate_limit(last_request_time)

        assert is_allowed is False
        assert new_time == last_request_time

    def test_check_rate_limit_first_request(self):
        """Test rate limit check for first request (no previous time)"""
        is_allowed, new_time = check_rate_limit(0)

        assert is_allowed is True
        assert new_time > 0

    def test_get_rate_limit_message(self):
        """Test rate limit message generation"""
        message = get_rate_limit_message()

        assert "rate limit" in message.lower()
        assert "exceeded" in message.lower()


class TestValidationFunctions:
    """Test suite for validation functions"""

    def test_validate_safe_search_valid_values(self):
        """Test safe search validation with valid values"""
        valid_values = ["strict", "moderate", "off"]

        for value in valid_values:
            result = validate_safe_search(value)
            assert result == value

    def test_validate_safe_search_invalid_values(self):
        """Test safe search validation with invalid values"""
        invalid_values = ["invalid", "high", "low", "", None]

        for value in invalid_values:
            result = validate_safe_search(value)
            assert result == "moderate"  # Default fallback

    def test_validate_max_results_within_range(self):
        """Test max results validation within valid range"""
        result = validate_max_results(5, min_val=1, max_val=20, default=5)
        assert result == 5

    def test_validate_max_results_below_minimum(self):
        """Test max results validation below minimum"""
        result = validate_max_results(0, min_val=1, max_val=20, default=5)
        assert result == 5  # Default fallback

    def test_validate_max_results_above_maximum(self):
        """Test max results validation above maximum"""
        result = validate_max_results(25, min_val=1, max_val=20, default=5)
        assert result == 5  # Default fallback

    def test_validate_max_results_none_value(self):
        """Test max results validation with None value"""
        result = validate_max_results(None, min_val=1, max_val=20, default=5)
        assert result == 5  # Default fallback

    def test_validate_language_code_valid(self):
        """Test language code validation with valid codes"""
        valid_codes = ["en", "es", "fr", "de",
                       "it", "pt", "ru", "ja", "ko", "zh"]

        for code in valid_codes:
            result = validate_language_code(code)
            assert result == code

    def test_validate_language_code_invalid(self):
        """Test language code validation with invalid codes"""
        invalid_codes = ["invalid", "123", "", None, "EN", "En"]

        for code in invalid_codes:
            result = validate_language_code(code)
            assert result == "en"  # Default fallback

    def test_validate_query_valid(self):
        """Test query validation with valid queries"""
        valid_queries = [
            "test query",
            "AI development",
            "python programming",
            "a" * 100  # 100 character query
        ]

        for query in valid_queries:
            is_valid, error_msg = validate_query(query)
            assert is_valid is True
            assert error_msg == ""  # Empty string, not None

    def test_validate_query_invalid(self):
        """Test query validation with invalid queries"""
        invalid_queries = [
            "",
            "   ",
            None
        ]

        for query in invalid_queries:
            is_valid, error_msg = validate_query(query)
            assert is_valid is False
            assert "empty" in error_msg.lower()

    def test_validate_topic_valid(self):
        """Test topic validation with valid topics"""
        valid_topics = [
            "AI",
            "quantum computing",
            "machine learning",
            "a" * 100  # 100 character topic
        ]

        for topic in valid_topics:
            is_valid, error_msg = validate_topic(topic)
            assert is_valid is True
            assert error_msg == ""  # Empty string, not None

    def test_validate_topic_invalid(self):
        """Test topic validation with invalid topics"""
        invalid_topics = [
            "",
            "   ",
            None
        ]

        for topic in invalid_topics:
            is_valid, error_msg = validate_topic(topic)
            assert is_valid is False
            assert "empty" in error_msg.lower()

    def test_validate_news_parameters_valid(self):
        """Test news parameters validation with valid values"""
        valid_values = [1, 5, 10, 20, 50]

        for value in valid_values:
            result = validate_news_parameters(value)
            assert result == 5  # Default fallback for values > 20

    def test_validate_news_parameters_invalid(self):
        """Test news parameters validation with invalid values"""
        invalid_values = [0, -1, 51, 100, None]

        for value in invalid_values:
            result = validate_news_parameters(value)
            assert result == 5  # Default fallback

    def test_validate_image_search_parameters_valid(self):
        """Test image search parameters validation with valid values"""
        valid_values = [1, 5, 10, 20, 50]

        for value in valid_values:
            result = validate_image_search_parameters(value)
            assert result == value

    def test_validate_image_search_parameters_invalid(self):
        """Test image search parameters validation with invalid values"""
        invalid_values = [0, -1, 51, 100, None]

        for value in invalid_values:
            result = validate_image_search_parameters(value)
            assert result == 10  # Default fallback


class TestFormattingFunctions:
    """Test suite for formatting functions"""

    def test_format_web_search_results(self):
        """Test web search results formatting"""
        query = "test query"
        results = [
            {
                "title": "Test Result 1",
                "link": "https://example1.com",
                "body": "This is a test result body."
            },
            {
                "title": "Test Result 2",
                "link": "https://example2.com",
                "body": "This is the second test result."
            }
        ]
        safe_search = "moderate"

        formatted = format_web_search_results(query, results, safe_search)

        assert query in formatted
        assert "Test Result 1" in formatted
        assert "Test Result 2" in formatted
        assert "example1.com" in formatted
        assert "example2.com" in formatted
        assert "This is a test result body" in formatted
        assert safe_search in formatted

    def test_format_web_search_results_empty(self):
        """Test web search results formatting with empty results"""
        query = "test query"
        results = []
        safe_search = "moderate"

        formatted = format_web_search_results(query, results, safe_search)

        assert query in formatted
        assert "no results" in formatted.lower() or "no matches" in formatted.lower()

    def test_format_image_search_results(self):
        """Test image search results formatting"""
        query = "test images"
        results = [
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
        safe_search = "strict"

        formatted = format_image_search_results(query, results, safe_search)

        assert query in formatted
        assert "Test Image 1" in formatted
        assert "Test Image 2" in formatted
        assert "https://example1.com/image1.jpg" in formatted
        assert "https://example2.com/image2.jpg" in formatted
        assert safe_search in formatted

    def test_format_image_search_results_empty(self):
        """Test image search results formatting with empty results"""
        query = "test images"
        results = []
        safe_search = "strict"

        formatted = format_image_search_results(query, results, safe_search)

        assert query in formatted
        assert "no images" in formatted.lower() or "no matches" in formatted.lower()

    def test_format_news_articles_response(self):
        """Test news articles response formatting"""
        category = "technology"
        topic = "AI"
        max_articles = 5

        formatted = format_news_articles_response(
            category, topic, max_articles)

        assert category in formatted
        assert topic in formatted
        assert str(max_articles) in formatted

    def test_format_news_articles_response_no_topic(self):
        """Test news articles response formatting without topic"""
        category = "business"
        topic = None
        max_articles = 10

        formatted = format_news_articles_response(
            category, topic, max_articles)

        assert category in formatted
        assert str(max_articles) in formatted

    def test_format_wikipedia_response(self):
        """Test Wikipedia response formatting"""
        topic = "artificial intelligence"
        language = "en"
        summary_only = True

        formatted = format_wikipedia_response(topic, language, summary_only)

        assert topic in formatted
        assert language in formatted
        assert "summary only" in formatted.lower()

    def test_format_wikipedia_response_full_content(self):
        """Test Wikipedia response formatting for full content"""
        topic = "artificial intelligence"
        language = "es"
        summary_only = False

        formatted = format_wikipedia_response(topic, language, summary_only)

        assert topic in formatted
        assert language in formatted
        assert "summary only" in formatted.lower()


class TestExtractionFunctions:
    """Test suite for data extraction functions"""

    def test_extract_search_result_info(self):
        """Test search result information extraction"""
        result = {
            "title": "Test Title",
            "link": "https://example.com",
            "body": "This is a test result body."
        }

        extracted = extract_search_result_info(result)

        assert "title" in extracted
        assert "link" in extracted
        assert "snippet" in extracted  # Note: body becomes snippet
        assert extracted["title"] == "Test Title"
        assert extracted["link"] == "https://example.com"
        assert extracted["snippet"] == "This is a test result body."

    def test_extract_search_result_info_missing_fields(self):
        """Test search result information extraction with missing fields"""
        result = {
            "title": "Test Title"
            # Missing link and body
        }

        extracted = extract_search_result_info(result)

        assert "title" in extracted
        assert "link" in extracted
        assert "snippet" in extracted
        assert extracted["title"] == "Test Title"
        assert extracted["link"] == "No link"
        assert extracted["snippet"] == "No description"

    def test_extract_image_result_info(self):
        """Test image result information extraction"""
        result = {
            "title": "Test Image",
            "link": "https://example.com/image.jpg",
            "image": "https://example.com/image.jpg",
            "thumbnail": "https://example.com/thumb.jpg"
        }

        extracted = extract_image_result_info(result)

        assert "title" in extracted
        assert "image_url" in extracted
        assert "source_url" in extracted
        assert extracted["title"] == "Test Image"
        assert extracted["image_url"] == "https://example.com/image.jpg"
        assert extracted["source_url"] == "https://example.com/image.jpg"

    def test_extract_image_result_info_missing_fields(self):
        """Test image result information extraction with missing fields"""
        result = {
            "title": "Test Image"
            # Missing other fields
        }

        extracted = extract_image_result_info(result)

        assert "title" in extracted
        assert "image_url" in extracted
        assert "source_url" in extracted
        assert extracted["title"] == "Test Image"
        assert extracted["image_url"] == "No image URL"
        assert extracted["source_url"] == "No source URL"


class TestProcessingFunctions:
    """Test suite for DuckDuckGo processing functions"""

    @patch('personal_assistant.tools.internet.internet_internal.DDGS')
    def test_process_duckduckgo_text_results(self, mock_ddgs_class):
        """Test DuckDuckGo text results processing"""
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = [
            {"title": "Result 1", "link": "https://example1.com",
                "body": "Description 1"},
            {"title": "Result 2", "link": "https://example2.com",
                "body": "Description 2"}
        ]
        mock_ddgs_class.return_value = mock_ddgs

        query = "test query"
        max_results = 2
        use_ddgs = False

        results = process_duckduckgo_text_results(
            mock_ddgs, query, max_results, use_ddgs)

        assert len(results) == 2
        assert results[0]["title"] == "Result 1"
        assert results[1]["title"] == "Result 2"

    @patch('personal_assistant.tools.internet.internet_internal.DDGS')
    def test_process_duckduckgo_image_results(self, mock_ddgs_class):
        """Test DuckDuckGo image results processing"""
        mock_ddgs = Mock()
        mock_ddgs.images.return_value = [
            {"title": "Image 1", "link": "https://example1.com/img1.jpg",
             "image": "https://example1.com/img1.jpg"},
            {"title": "Image 2", "link": "https://example2.com/img2.jpg",
             "image": "https://example2.com/img2.jpg"}
        ]
        mock_ddgs_class.return_value = mock_ddgs

        query = "test images"
        max_results = 2
        use_ddgs = False

        results = process_duckduckgo_image_results(
            mock_ddgs, query, max_results, use_ddgs)

        assert len(results) == 2
        assert results[0]["title"] == "Image 1"
        assert results[1]["title"] == "Image 2"

    @patch('personal_assistant.tools.internet.internet_internal.DDGS')
    def test_process_duckduckgo_text_results_exception(self, mock_ddgs_class):
        """Test DuckDuckGo text processing with exception"""
        mock_ddgs = Mock()
        mock_ddgs.text.side_effect = Exception("API error")

        query = "test query"
        max_results = 2
        use_ddgs = False

        # The function should handle exceptions gracefully
        results = process_duckduckgo_text_results(
            mock_ddgs, query, max_results, use_ddgs)
        assert results == []

    @patch('personal_assistant.tools.internet.internet_internal.DDGS')
    def test_process_duckduckgo_image_results_exception(self, mock_ddgs_class):
        """Test DuckDuckGo image processing with exception"""
        mock_ddgs = Mock()
        mock_ddgs.images.side_effect = Exception("API error")

        query = "test images"
        max_results = 2
        use_ddgs = False

        # The function should handle exceptions gracefully
        results = process_duckduckgo_image_results(
            mock_ddgs, query, max_results, use_ddgs)
        assert results == []


class TestUtilityFunctions:
    """Test suite for utility functions"""

    def test_get_duckduckgo_availability_message(self):
        """Test DuckDuckGo availability message"""
        message = get_duckduckgo_availability_message()

        assert "duckduckgo" in message.lower()
        assert "available" in message.lower() or "unavailable" in message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
