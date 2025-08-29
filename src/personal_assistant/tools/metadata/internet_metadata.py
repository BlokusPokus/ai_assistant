"""
Internet Tool Metadata

This module provides enhanced metadata for the internet tools to improve AI understanding.
"""

from .tool_metadata import (
    ToolMetadata, ToolUseCase, ToolExample, ToolCategory, ToolComplexity
)
from .ai_enhancements import (
    AIEnhancementManager, EnhancementType, EnhancementPriority
)


def create_internet_tool_metadata() -> ToolMetadata:
    """Create comprehensive metadata for the internet tools."""

    # Define use cases for the internet tools
    use_cases = [
        ToolUseCase(
            name="Web Search for Information",
            description="Search the web for current information, facts, and data using DuckDuckGo",
            example_request="Search for the latest news about AI developments",
            example_parameters={
                "query": "latest AI developments 2024",
                "max_results": 5,
                "safe_search": "moderate"
            },
            expected_outcome="Relevant web search results with URLs and summaries",
            success_indicators=["search_results_found",
                                "relevant_information", "valid_urls"],
            failure_modes=["no_results",
                           "rate_limited", "service_unavailable"],
            prerequisites=["valid_search_query",
                           "internet_connection", "DuckDuckGo_available"]
        ),
        ToolUseCase(
            name="News Article Retrieval",
            description="Get current news articles by category or specific topic",
            example_request="Get the latest technology news articles",
            example_parameters={
                "category": "technology",
                "topic": None,
                "max_articles": 5
            },
            expected_outcome="List of current news articles with headlines and summaries",
            success_indicators=["articles_retrieved",
                                "current_information", "category_relevant"],
            failure_modes=["no_news_available",
                           "category_not_found", "api_error"],
            prerequisites=["news_api_access",
                           "valid_category", "internet_connection"]
        ),
        ToolUseCase(
            name="Wikipedia Information Search",
            description="Search Wikipedia for comprehensive information on topics",
            example_request="Find information about quantum computing on Wikipedia",
            example_parameters={
                "topic": "quantum computing",
                "language": "en",
                "summary_only": True
            },
            expected_outcome="Wikipedia article summary or full content in specified language",
            success_indicators=["article_found",
                                "relevant_content", "language_correct"],
            failure_modes=["topic_not_found",
                           "language_not_available", "api_error"],
            prerequisites=["wikipedia_api_access",
                           "valid_topic", "internet_connection"]
        ),
        ToolUseCase(
            name="Image Search and Discovery",
            description="Search for images on the web using DuckDuckGo image search",
            example_request="Find images of modern office spaces",
            example_parameters={
                "query": "modern office spaces",
                "max_results": 10,
                "safe_search": "strict"
            },
            expected_outcome="Collection of relevant images with URLs and descriptions",
            success_indicators=["images_found",
                                "relevant_results", "safe_content"],
            failure_modes=["no_images_found",
                           "inappropriate_content", "rate_limited"],
            prerequisites=["valid_image_query",
                           "internet_connection", "DuckDuckGo_available"]
        ),
        ToolUseCase(
            name="Research and Fact-Checking",
            description="Verify information and gather research data from multiple sources",
            example_request="Research the current state of renewable energy adoption",
            example_parameters={
                "query": "renewable energy adoption statistics 2024",
                "max_results": 8,
                "safe_search": "moderate"
            },
            expected_outcome="Comprehensive research results from multiple credible sources",
            success_indicators=["multiple_sources",
                                "credible_information", "current_data"],
            failure_modes=["limited_sources",
                           "outdated_information", "unreliable_sources"],
            prerequisites=["research_query",
                           "internet_connection", "search_engine_access"]
        ),
        ToolUseCase(
            name="Current Events Monitoring",
            description="Stay updated on breaking news and current events",
            example_request="What are the major headlines today?",
            example_parameters={
                "category": "general",
                "topic": "breaking news",
                "max_articles": 10
            },
            expected_outcome="Latest breaking news and current events coverage",
            success_indicators=["current_events",
                                "breaking_news", "timely_information"],
            failure_modes=["no_recent_news",
                           "delayed_information", "api_issues"],
            prerequisites=["news_api_access",
                           "internet_connection", "real_time_data"]
        )
    ]

    # Define concrete examples
    examples = [
        ToolExample(
            description="Search for current technology trends",
            user_request="What are the latest trends in artificial intelligence?",
            parameters={
                "query": "latest AI trends 2024",
                "max_results": 5,
                "safe_search": "moderate"
            },
            expected_result="Recent web search results about AI trends with URLs and summaries",
            notes="Current information gathering for technology research"
        ),
        ToolExample(
            description="Get business news updates",
            user_request="Show me the latest business news",
            parameters={
                "category": "business",
                "topic": None,
                "max_articles": 5
            },
            expected_result="Current business news articles with headlines and summaries",
            notes="Business news monitoring for professional updates"
        ),
        ToolExample(
            description="Research historical events on Wikipedia",
            user_request="Tell me about the Industrial Revolution",
            parameters={
                "topic": "Industrial Revolution",
                "language": "en",
                "summary_only": True
            },
            expected_result="Wikipedia summary of the Industrial Revolution",
            notes="Educational research using Wikipedia as a reference"
        ),
        ToolExample(
            description="Find reference images for design work",
            user_request="Find images of minimalist website designs",
            parameters={
                "query": "minimalist website design examples",
                "max_results": 10,
                "safe_search": "strict"
            },
            expected_result="Collection of minimalist website design images",
            notes="Visual reference gathering for design projects"
        ),
        ToolExample(
            description="Verify current statistics and data",
            user_request="What's the current global population?",
            parameters={
                "query": "current world population 2024",
                "max_results": 3,
                "safe_search": "moderate"
            },
            expected_result="Current population statistics from reliable sources",
            notes="Fact-checking and data verification"
        ),
        ToolExample(
            description="Research academic topics",
            user_request="Find information about machine learning algorithms",
            parameters={
                "query": "machine learning algorithms types examples",
                "max_results": 7,
                "safe_search": "moderate"
            },
            expected_result="Comprehensive information about ML algorithms from various sources",
            notes="Academic research and learning"
        ),
        ToolExample(
            description="Monitor industry developments",
            user_request="What's happening in the electric vehicle market?",
            parameters={
                "category": "business",
                "topic": "electric vehicles",
                "max_articles": 8
            },
            expected_result="Latest news about electric vehicle market developments",
            notes="Industry monitoring for business intelligence"
        ),
        ToolExample(
            description="Find educational resources",
            user_request="Search for Python programming tutorials",
            parameters={
                "query": "Python programming tutorials beginners 2024",
                "max_results": 6,
                "safe_search": "moderate"
            },
            expected_result="Educational resources and tutorials for Python programming",
            notes="Learning resource discovery"
        )
    ]

    # Create the metadata
    metadata = ToolMetadata(
        tool_name="internet_tools",
        tool_version="1.0.0",
        description="Comprehensive internet tools for web search, news retrieval, Wikipedia access, and image search using DuckDuckGo and other APIs",
        category=ToolCategory.INFORMATION,
        complexity=ToolComplexity.MODERATE,
        use_cases=use_cases,
        examples=examples,
        prerequisites=[
            "Internet connection",
            "Valid search queries or topics",
            "API access for news and Wikipedia",
            "DuckDuckGo search availability"
        ],
        related_tools=["research_tool", "notion_tool", "note_tool"],
        complementary_tools=["note_tool", "research_tool", "planning_tool"],
        conflicting_tools=[],
        execution_time="2-8 seconds",
        success_rate=0.90,
        rate_limits="100 requests per hour",
        retry_strategy="Retry failed requests with exponential backoff",
        ai_instructions=(
            "Use the internet tools when users need current information, want to research topics, "
            "need to verify facts, or want to stay updated on news and events. "
            "Analyze the user's request to determine which tool is most appropriate: "
            "web_search for general information, news_articles for current events, "
            "wikipedia for educational content, or image_search for visual references. "
            "For research requests, use web_search to gather information from multiple sources. "
            "For current events, use news_articles to get the latest updates. "
            "For educational topics, use Wikipedia for comprehensive information. "
            "For design or visual needs, use image_search to find relevant images. "
            "Always consider the user's intent and suggest the most appropriate tool combination."
        ),
        parameter_guidance={
            "query": "Clear, specific search terms that accurately describe what you're looking for",
            "max_results": "Reasonable number of results (1-20 for web search, 1-50 for images)",
            "safe_search": "Appropriate safety level (strict for images, moderate for general search)",
            "category": "News category that matches the user's interest (business, technology, sports, etc.)",
            "topic": "Specific topic or subject for focused news or Wikipedia searches",
            "language": "Language code for Wikipedia searches (en, es, fr, de, etc.)",
            "summary_only": "Whether to return full Wikipedia content or just summary"
        },
        common_mistakes=[
            "Using overly broad search queries that return irrelevant results",
            "Not specifying appropriate safe search levels for different content types",
            "Requesting too many results which can overwhelm the user",
            "Using inappropriate news categories for the requested topic",
            "Not considering language preferences for international topics",
            "Failing to validate search results for relevance and accuracy"
        ],
        best_practices=[
            "Use specific, targeted search queries for better results",
            "Set appropriate safe search levels (strict for images, moderate for text)",
            "Limit results to reasonable numbers (5-10 for most use cases)",
            "Use news categories to focus on relevant content types",
            "Consider language preferences for international topics",
            "Validate and cross-reference information from multiple sources",
            "Use appropriate tools for different types of information needs",
            "Respect rate limits and implement proper error handling"
        ]
    )

    return metadata


def create_internet_ai_enhancements(enhancement_manager: AIEnhancementManager):
    """Create AI enhancements for the internet tools."""

    # Parameter suggestion enhancement for search queries
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="internet_tools",
        parameter_name="query",
        suggestion_logic=(
            "Analyze the user's request to create effective search queries. "
            "Extract key terms, concepts, and context. "
            "Add relevant modifiers like 'latest', '2024', 'examples', 'tutorial' "
            "to improve search result quality and relevance."
        ),
        examples=[
            {
                "user_request": "What's happening with AI?",
                "suggested_value": "artificial intelligence latest developments 2024",
                "reasoning": "User wants current AI information, so add 'latest' and '2024' for timeliness"
            },
            {
                "user_request": "Find information about machine learning",
                "suggested_value": "machine learning overview examples applications",
                "reasoning": "User wants comprehensive ML information, so add descriptive terms"
            },
            {
                "user_request": "Show me news about climate change",
                "suggested_value": "climate change news current events 2024",
                "reasoning": "User wants current climate news, so add 'news' and 'current events'"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Parameter suggestion enhancement for news categories
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="internet_tools",
        parameter_name="category",
        suggestion_logic=(
            "Analyze the user's request to suggest appropriate news categories. "
            "Look for topic indicators that map to standard news categories. "
            "Suggest categories that will provide the most relevant news coverage."
        ),
        examples=[
            {
                "user_request": "What's the latest in technology?",
                "suggested_value": "technology",
                "reasoning": "User specifically mentioned technology, so use technology category"
            },
            {
                "user_request": "Show me business updates",
                "suggested_value": "business",
                "reasoning": "User wants business information, so use business category"
            },
            {
                "user_request": "What's happening in sports?",
                "suggested_value": "sports",
                "reasoning": "User wants sports news, so use sports category"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Intent recognition enhancement
    enhancement_manager.create_intent_recognition_enhancement(
        tool_name="internet_tools",
        intent_patterns=[
            "search", "find", "look up", "research", "what is", "tell me about",
            "news", "latest", "current", "breaking", "updates", "developments",
            "wikipedia", "wiki", "information about", "learn about",
            "images", "pictures", "photos", "visual", "design examples",
            "verify", "check", "fact check", "is it true", "confirm"
        ],
        recognition_logic=(
            "Look for internet-related verbs and phrases in the user's request. "
            "Consider context clues like information needs, current events, "
            "research requirements, or visual content needs. "
            "Recognize both direct search requests and indirect information needs."
        ),
        examples=[
            {
                "user_request": "I need to research quantum computing",
                "detected_intent": "information_research",
                "confidence": "high",
                "reasoning": "Direct mention of 'research' with specific topic"
            },
            {
                "user_request": "What's the latest news about AI?",
                "detected_intent": "current_news",
                "confidence": "high",
                "reasoning": "Use of 'latest news' indicating current events interest"
            },
            {
                "user_request": "Can you find images of modern architecture?",
                "detected_intent": "image_search",
                "confidence": "high",
                "reasoning": "Direct request for images with specific subject"
            },
            {
                "user_request": "Tell me about the Industrial Revolution",
                "detected_intent": "educational_research",
                "confidence": "high",
                "reasoning": "Educational request suitable for Wikipedia or general search"
            },
            {
                "user_request": "Is it true that electric cars are cheaper now?",
                "detected_intent": "fact_verification",
                "confidence": "high",
                "reasoning": "Fact-checking request requiring current information"
            }
        ],
        priority=EnhancementPriority.CRITICAL
    )

    # Tool selection enhancement
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="internet_tools",
        parameter_name="tool_selection",
        suggestion_logic=(
            "Analyze the user's request to determine the most appropriate internet tool. "
            "web_search: general information, research, fact-checking. "
            "news_articles: current events, breaking news, industry updates. "
            "wikipedia: educational topics, historical information, academic subjects. "
            "image_search: visual references, design inspiration, photo needs."
        ),
        examples=[
            {
                "user_request": "What are the latest developments in renewable energy?",
                "suggested_tool": "web_search",
                "reasoning": "User wants current developments, best served by web search for latest information"
            },
            {
                "user_request": "Show me today's business headlines",
                "suggested_tool": "news_articles",
                "reasoning": "User wants current news headlines, best served by news articles tool"
            },
            {
                "user_request": "Explain the theory of relativity",
                "suggested_tool": "wikipedia",
                "reasoning": "User wants educational explanation, best served by Wikipedia for comprehensive coverage"
            },
            {
                "user_request": "Find examples of minimalist logo designs",
                "suggested_tool": "image_search",
                "reasoning": "User wants visual examples, best served by image search tool"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Search optimization enhancement
    enhancement_manager.create_parameter_suggestion_enhancement(
        tool_name="internet_tools",
        parameter_name="search_optimization",
        suggestion_logic=(
            "Optimize search queries for better results. "
            "Add time indicators (2024, latest, current) for current information. "
            "Include descriptive terms (examples, tutorial, guide) for educational content. "
            "Use specific terminology for technical topics. "
            "Add location context when relevant."
        ),
        examples=[
            {
                "user_request": "Find information about electric cars",
                "optimized_query": "electric vehicles benefits cost comparison 2024",
                "reasoning": "Added 'vehicles' (broader term), 'benefits cost comparison' (specific aspects), '2024' (current)"
            },
            {
                "user_request": "Show me Python tutorials",
                "optimized_query": "Python programming tutorials beginners examples 2024",
                "reasoning": "Added 'programming', 'beginners', 'examples' for better tutorial results, '2024' for current content"
            },
            {
                "user_request": "What's happening in the stock market?",
                "optimized_query": "stock market news today current trends 2024",
                "reasoning": "Added 'news today', 'current trends', '2024' for latest market information"
            }
        ],
        priority=EnhancementPriority.MEDIUM
    )

    # Result validation enhancement
    enhancement_manager.create_validation_enhancement(
        tool_name="internet_tools",
        description=(
            "CRITICAL: After retrieving internet search results, validate their relevance and quality. "
            "Check if results match the user's request. "
            "Suggest additional searches if results are insufficient. "
            "Provide context about result quality and reliability."
        ),
        ai_instructions=(
            "1. Review search results for relevance to user's request\n"
            "2. Check if results provide the information the user needs\n"
            "3. Suggest additional searches if results are insufficient\n"
            "4. Provide context about result quality and source reliability\n"
            "5. Offer to refine the search if needed\n"
            "6. Never claim information is verified without proper validation"
        ),
        examples=[
            {
                "scenario": "Search results are outdated",
                "action": "Suggest refining search with current year or 'latest' terms",
                "validation": "Offer to search for more current information"
            },
            {
                "scenario": "Results are too broad",
                "action": "Suggest more specific search terms",
                "validation": "Ask user if they want to narrow down the search"
            },
            {
                "scenario": "No relevant results found",
                "action": "Suggest alternative search approaches or related topics",
                "validation": "Offer to try different search strategies"
            }
        ]
    )

    # Multi-tool workflow enhancement
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["internet_tools", "note_tool"],
        workflow_description="Research information and create organized notes",
        workflow_steps=[
            {
                "step": 1,
                "tool": "internet_tools",
                "action": "Search for information on the requested topic",
                "parameters": "query, max_results, safe_search"
            },
            {
                "step": 2,
                "tool": "note_tool",
                "action": "Create organized notes from the research findings",
                "parameters": "title, content, tags, category"
            }
        ],
        examples=[
            {
                "user_request": "Research machine learning and create notes",
                "workflow": "web_search -> note_tool",
                "reasoning": "User wants both research and note-taking, requiring two tools"
            },
            {
                "user_request": "Find current news about AI and document it",
                "workflow": "news_articles -> note_tool",
                "reasoning": "User wants news gathering and documentation"
            }
        ],
        priority=EnhancementPriority.HIGH
    )

    # Research methodology enhancement
    enhancement_manager.create_workflow_suggestion_enhancement(
        tool_names=["internet_tools"],
        workflow_description="Comprehensive research using multiple search approaches",
        workflow_steps=[
            {
                "step": 1,
                "tool": "internet_tools",
                "action": "Initial broad search for general information",
                "parameters": "query, max_results: 5, safe_search: moderate"
            },
            {
                "step": 2,
                "tool": "internet_tools",
                "action": "Refined search for specific aspects",
                "parameters": "refined_query, max_results: 3, safe_search: moderate"
            },
            {
                "step": 3,
                "tool": "internet_tools",
                "action": "Fact verification from multiple sources",
                "parameters": "verification_query, max_results: 2, safe_search: moderate"
            }
        ],
        examples=[
            {
                "user_request": "Research the impact of AI on healthcare",
                "workflow": "broad_search -> specific_search -> verification",
                "reasoning": "Comprehensive research requires multiple search approaches"
            },
            {
                "user_request": "Find information about renewable energy adoption",
                "workflow": "general_search -> statistics_search -> source_verification",
                "reasoning": "Statistical research needs multiple search strategies"
            }
        ],
        priority=EnhancementPriority.MEDIUM
    )

    # Content safety enhancement
    enhancement_manager.create_validation_enhancement(
        tool_name="internet_tools",
        description=(
            "CRITICAL: Always ensure content safety and appropriateness. "
            "Use appropriate safe search levels for different content types. "
            "Filter out inappropriate or harmful content. "
            "Consider the user's context and needs when setting safety parameters."
        ),
        ai_instructions=(
            "1. Always use 'strict' safe search for image searches\n"
            "2. Use 'moderate' safe search for general web searches\n"
            "3. Consider user context when setting safety levels\n"
            "4. Filter out inappropriate content from results\n"
            "5. Warn users about potentially sensitive content\n"
            "6. Never return harmful or inappropriate results"
        ),
        examples=[
            {
                "scenario": "User requests images for work presentation",
                "action": "Use strict safe search and professional content filters",
                "safety": "Ensure all results are workplace-appropriate"
            },
            {
                "scenario": "User searches for medical information",
                "action": "Use moderate safe search but filter for reliable medical sources",
                "safety": "Balance safety with information accuracy"
            },
            {
                "scenario": "User searches for educational content",
                "action": "Use moderate safe search with educational focus",
                "safety": "Ensure content is appropriate for learning"
            }
        ]
    )

    # Rate limiting awareness enhancement
    enhancement_manager.create_validation_enhancement(
        tool_name="internet_tools",
        description=(
            "CRITICAL: Be aware of rate limits and API restrictions. "
            "Implement proper rate limiting to avoid service disruptions. "
            "Inform users about rate limits when they make many requests. "
            "Suggest alternative approaches when rate limits are reached."
        ),
        ai_instructions=(
            "1. Monitor request frequency and respect rate limits\n"
            "2. Inform users about rate limits when approaching them\n"
            "3. Suggest batching requests when possible\n"
            "4. Offer alternative tools when rate limits are reached\n"
            "5. Implement exponential backoff for retries\n"
            "6. Never exceed service rate limits"
        ),
        examples=[
            {
                "scenario": "User makes multiple rapid searches",
                "action": "Inform about rate limits and suggest batching",
                "rate_limiting": "Explain current limits and suggest efficient search strategies"
            },
            {
                "scenario": "Rate limit reached during search",
                "action": "Inform user and suggest waiting or alternative approaches",
                "rate_limiting": "Provide clear information about when service will resume"
            },
            {
                "scenario": "User needs extensive research",
                "action": "Suggest planning searches to avoid rate limits",
                "rate_limiting": "Help user optimize their research approach"
            }
        ]
    )


def get_internet_tool_metadata() -> dict:
    """Get the complete internet tool metadata for AI consumption."""
    metadata = create_internet_tool_metadata()
    return metadata.get_ai_guidance()


def get_internet_tool_metadata_full() -> dict:
    """Get the complete internet tool metadata including all details."""
    metadata = create_internet_tool_metadata()
    return metadata.to_dict()

