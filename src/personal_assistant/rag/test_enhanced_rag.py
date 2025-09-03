#!/usr/bin/env python3
"""
Test script for enhanced RAG system.
Tests real embedding generation, caching, and Notion content extraction.
"""

import asyncio
import logging
import os
import sys

from personal_assistant.config.logging_config import setup_logging
from personal_assistant.config.settings import settings
from personal_assistant.rag.embeddings.cache import EmbeddingCache, LRUCache
from personal_assistant.rag.embeddings.gemini_embeddings import GeminiEmbeddings
from personal_assistant.rag.notion_extractor import NotionContentExtractor
from personal_assistant.rag.retriever import (
    embed_text,
    get_embedding_stats,
    query_knowledge_base,
)

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def test_embeddings():
    """Test real embedding generation."""
    print("🧪 Testing Real Embeddings...")

    try:
        # Test text embedding
        test_text = "This is a test document for embedding generation."
        embedding = await embed_text(test_text)

        if embedding:
            print(f"✅ Embedding generated successfully!")
            print(f"   Length: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
            print(f"   Type: {type(embedding)}")
        else:
            print("❌ Failed to generate embedding")
            return False

    except Exception as e:
        print(f"❌ Error testing embeddings: {e}")
        return False

    return True


async def test_embedding_stats():
    """Test embedding statistics."""
    print("\n📊 Testing Embedding Statistics...")

    try:
        stats = await get_embedding_stats()
        print(f"✅ Embedding stats retrieved:")
        print(f"   Model: {stats.get('embedding_model', 'Unknown')}")
        print(f"   Cache stats: {stats.get('cache_stats', {})}")
        print(f"   Fallback used: {stats.get('fallback_used', False)}")

    except Exception as e:
        print(f"❌ Error getting embedding stats: {e}")
        return False

    return True


async def test_content_extractor():
    """Test Notion content extractor."""
    print("\n📝 Testing Notion Content Extractor...")

    try:
        extractor = NotionContentExtractor()
        stats = extractor.get_extraction_stats()

        print(f"✅ Content extractor initialized:")
        print(f"   Type: {stats.get('extractor_type', 'Unknown')}")
        print(f"   Notion tool available: {stats.get('notion_tool_available', False)}")

        # Test content parsing with sample text
        sample_content = """# Meeting Notes
        Important meeting about project planning.
        Tags: #work #planning
        Status: In Progress
        Category: Work
        
        Discussion points:
        1. Timeline review
        2. Resource allocation
        3. Risk assessment"""

        structured = extractor._parse_note_content(sample_content)
        if structured:
            print(f"✅ Content parsing successful:")
            print(f"   Title: {structured.get('title', 'N/A')}")
            print(f"   Tags: {structured.get('tags', [])}")
            print(f"   Category: {structured.get('category', 'N/A')}")
            print(f"   Status: {structured.get('status', 'N/A')}")
        else:
            print("❌ Content parsing failed")
            return False

    except Exception as e:
        print(f"❌ Error testing content extractor: {e}")
        return False

    return True


async def test_rag_query():
    """Test RAG query functionality."""
    print("\n🔍 Testing RAG Query...")

    try:
        # Test with a simple query
        test_query = "project planning meeting"
        user_id = "1"  # Test user ID

        results = await query_knowledge_base(user_id, test_query)

        print(f"✅ RAG query completed:")
        print(f"   Query: '{test_query}'")
        print(f"   Results returned: {len(results)}")

        if results:
            print(
                f"   First result source: {results[0].get('metadata', {}).get('source', 'Unknown')}"
            )

    except Exception as e:
        print(f"❌ Error testing RAG query: {e}")
        return False

    return True


async def main():
    """Run all tests."""
    print("🚀 Enhanced RAG System Test Suite")
    print("=" * 50)

    # Check configuration
    print(f"🔧 Configuration:")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Google API Key: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Not Set'}")
    print(f"   RAG Max Results: {settings.RAG_MAX_RESULTS}")
    print(f"   RAG Context Length: {settings.RAG_MAX_CONTEXT_LENGTH}")

    if not settings.GOOGLE_API_KEY:
        print("\n⚠️  Warning: GOOGLE_API_KEY not set. Some tests may fail.")
        print("   Set the environment variable or add to your .env file.")

    print("\n" + "=" * 50)

    # Run tests
    tests = [
        ("Real Embeddings", test_embeddings),
        ("Embedding Statistics", test_embedding_stats),
        ("Content Extractor", test_content_extractor),
        ("RAG Query", test_rag_query),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Enhanced RAG system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
