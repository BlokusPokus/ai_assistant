"""
Research Tool for combined internet and YouTube search and analysis.
"""
import logging
from typing import Any, Dict, List, Union

from ..base import Tool
from ..internet.internet_tool import InternetTool
from ..youtube.youtube_tool import YouTubeTool
from .research_internal import (
    format_combined_search_response,
    format_research_response,
    generate_academic_report,
    generate_content_summary,
    generate_correlation_insights,
    generate_detailed_report,
    generate_research_summary,
    generate_summary_report,
    validate_analysis_type,
    validate_search_parameters,
    validate_sources,
)

logger = logging.getLogger(__name__)


class ResearchTool:
    """
    Comprehensive research tool that provides:
    - Combined internet and YouTube search
    - Multi-source information synthesis
    - Research result organization and formatting
    - Cross-platform content correlation
    - Research summary generation
    """

    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube URL using proper URL parsing."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc in [
                "www.youtube.com",
                "youtube.com",
                "youtu.be",
                "m.youtube.com",
            ]
        except Exception:
            return False

    def __init__(self):
        # Initialize any shared resources, tokens, clients, etc.
        self._research_cache = {}
        self._last_research_time = 0

        # Create individual tools
        self.research_topic_tool = Tool(
            name="research_topic",
            func=self.research_topic,
            description="Comprehensive research combining web and YouTube sources",
            parameters={
                "topic": {"type": "string", "description": "Research topic (required)"},
                "sources": {
                    "type": "string",
                    "description": "Sources to include: web, youtube, both (default: both)",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results per source (default: 5)",
                },
                "include_summary": {
                    "type": "boolean",
                    "description": "Generate research summary (default: true)",
                },
            },
        )

        self.combined_search_tool = Tool(
            name="combined_search",
            func=self.combined_search,
            description="Search across multiple platforms simultaneously",
            parameters={
                "query": {"type": "string", "description": "Search query (required)"},
                "platforms": {
                    "type": "string",
                    "description": "Platforms to search: web, youtube, news, wikipedia (default: all)",
                },
                "max_results_per_platform": {
                    "type": "integer",
                    "description": "Maximum results per platform (default: 3)",
                },
                "correlate_results": {
                    "type": "boolean",
                    "description": "Correlate results across platforms (default: true)",
                },
            },
        )

        self.analyze_content_tool = Tool(
            name="analyze_content",
            func=self.analyze_content,
            description="Analyze and synthesize content from multiple sources",
            parameters={
                "content_sources": {
                    "type": "string",
                    "description": "Comma-separated list of content sources or URLs (required)",
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Type of analysis: summary, comparison, synthesis (default: synthesis)",
                },
                "include_insights": {
                    "type": "boolean",
                    "description": "Include key insights and patterns (default: true)",
                },
            },
        )

        self.generate_research_report_tool = Tool(
            name="generate_research_report",
            func=self.generate_research_report,
            description="Generate a comprehensive research report from multiple sources",
            parameters={
                "topic": {"type": "string", "description": "Research topic (required)"},
                "sources": {
                    "type": "string",
                    "description": "Sources to include in report (default: all available)",
                },
                "report_format": {
                    "type": "string",
                    "description": "Report format: summary, detailed, academic (default: summary)",
                },
                "include_citations": {
                    "type": "boolean",
                    "description": "Include source citations (default: true)",
                },
            },
        )

        self.find_related_content_tool = Tool(
            name="find_related_content",
            func=self.find_related_content,
            description="Find related content across different platforms",
            parameters={
                "seed_content": {
                    "type": "string",
                    "description": "Seed content or topic to find related items for (required)",
                },
                "platforms": {
                    "type": "string",
                    "description": "Platforms to search for related content (default: all)",
                },
                "max_related_items": {
                    "type": "integer",
                    "description": "Maximum number of related items (default: 10)",
                },
                "relevance_threshold": {
                    "type": "string",
                    "description": "Relevance threshold: high, medium, low (default: medium)",
                },
            },
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter(
            [
                self.research_topic_tool,
                self.combined_search_tool,
                self.analyze_content_tool,
                self.generate_research_report_tool,
                self.find_related_content_tool,
            ]
        )

    async def research_topic(
        self,
        topic: str,
        sources: str = "both",
        max_results: int = 5,
        include_summary: bool = True,
    ) -> str:
        """Comprehensive research combining web and YouTube sources"""
        try:
            # Validate parameters
            if not topic or not topic.strip():
                return "Error: Research topic is required"

            # Validate and normalize parameters
            max_results, _, _ = validate_search_parameters(max_results, 3, 10)
            sources_list = validate_sources(sources)

            logger.info(
                f"Research request for: {topic} (sources: {sources_list}, max: {max_results}, summary: {include_summary})"
            )

            # Initialize results storage
            research_results: Dict[str, Any] = {"web": [], "youtube": [], "summary": ""}

            # Perform web search if requested
            if "web" in sources_list:
                try:
                    internet_tool = InternetTool()
                    web_results = await internet_tool.web_search(
                        topic, max_results=max_results
                    )
                    # Handle Union[str, dict] return type
                    if isinstance(web_results, str):
                        research_results["web"] = [web_results]
                    else:
                        research_results["web"] = web_results
                except Exception as e:
                    logger.warning(f"Web search failed: {e}")
                    research_results["web"] = f"Web search unavailable: {str(e)}"

            # Perform YouTube search if requested
            if "youtube" in sources_list:
                try:
                    youtube_tool = YouTubeTool()
                    youtube_results = await youtube_tool.search_videos(
                        topic, max_results=max_results
                    )
                    # Handle Union[str, dict] return type
                    if isinstance(youtube_results, str):
                        research_results["youtube"] = [youtube_results]
                    else:
                        research_results["youtube"] = youtube_results
                except Exception as e:
                    logger.warning(f"YouTube search failed: {e}")
                    research_results[
                        "youtube"
                    ] = f"YouTube search unavailable: {str(e)}"

            # Generate research summary if requested
            if include_summary:
                research_results["summary"] = generate_research_summary(
                    topic, research_results
                )

            # Format the response using internal function
            return format_research_response(
                topic, sources_list, max_results, research_results, include_summary
            )

        except Exception as e:
            logger.error(f"Error in research topic: {e}")
            return f"Error researching topic: {str(e)}"

    async def combined_search(
        self,
        query: str,
        platforms: str = "all",
        max_results_per_platform: int = 3,
        correlate_results: bool = True,
    ) -> str:
        """Search across multiple platforms simultaneously"""
        try:
            # Validate parameters
            if not query or not query.strip():
                return "Error: Search query is required"

            # Validate and normalize parameters
            _, max_results_per_platform, _ = validate_search_parameters(
                5, max_results_per_platform, 10
            )
            platforms_list = validate_sources(platforms)

            logger.info(
                f"Combined search for: {query} (platforms: {platforms_list}, max: {max_results_per_platform}, correlate: {correlate_results})"
            )

            # Initialize results storage
            search_results: Dict[str, Any] = {}
            correlation_insights: List[str] = []

            # Perform searches across platforms
            for platform in platforms_list:
                try:
                    if platform == "web":
                        internet_tool = InternetTool()
                        results = await internet_tool.web_search(
                            query, max_results=max_results_per_platform
                        )
                        # Handle Union[str, dict] return type
                        if isinstance(results, str):
                            search_results[platform] = [results]
                        else:
                            search_results[platform] = results
                    elif platform == "youtube":
                        youtube_tool = YouTubeTool()
                        youtube_results: Union[str, dict, list] = await youtube_tool.search_videos(
                            query, max_results=max_results_per_platform
                        )
                        # Handle Union[str, dict] return type
                        if isinstance(youtube_results, str):
                            search_results[platform] = [youtube_results]
                        elif isinstance(youtube_results, list):
                            search_results[platform] = youtube_results
                        else:
                            search_results[platform] = [str(youtube_results)]
                    elif platform == "news":
                        # Placeholder for news search
                        search_results[
                            platform
                        ] = f"News search not yet implemented for: {query}"
                    elif platform == "wikipedia":
                        # Placeholder for Wikipedia search
                        search_results[
                            platform
                        ] = f"Wikipedia search not yet implemented for: {query}"
                except Exception as e:
                    logger.warning(f"Search on {platform} failed: {e}")
                    search_results[platform] = f"Search on {platform} failed: {str(e)}"

            # Generate correlation insights if requested
            if correlate_results:
                correlation_insights = generate_correlation_insights(
                    search_results, platforms_list
                )

            # Format the response using internal function
            return format_combined_search_response(
                query,
                platforms_list,
                max_results_per_platform,
                search_results,
                correlation_insights,
            )

        except Exception as e:
            logger.error(f"Error in combined search: {e}")
            return f"Error performing combined search: {str(e)}"

    async def analyze_content(
        self,
        content_sources: str,
        analysis_type: str = "synthesis",
        include_insights: bool = True,
    ) -> str:
        """Analyze and synthesize content from multiple sources"""
        try:
            # Validate parameters
            if not content_sources or not content_sources.strip():
                return "Error: Content sources are required"

            analysis_type = validate_analysis_type(analysis_type)

            logger.info(
                f"Content analysis request (sources: {content_sources}, type: {analysis_type}, insights: {include_insights})"
            )

            # Parse content sources
            sources = [s.strip() for s in content_sources.split(",")]

            # Initialize analysis results
            analysis_results: Dict[str, Any] = {
                "sources_analyzed": [],
                "content_summary": "",
                "key_insights": [],
                "analysis_type": analysis_type,
            }

            # Analyze each source
            for source in sources:
                try:
                    if source.startswith("http"):
                        # Analyze web content
                        source_analysis = await self._analyze_web_content(source)
                        analysis_results["sources_analyzed"].append(
                            {
                                "source": source,
                                "type": "web",
                                "analysis": source_analysis,
                            }
                        )
                    elif self._is_youtube_url(source):
                        # Analyze YouTube content
                        source_analysis = await self._analyze_youtube_content(source)
                        analysis_results["sources_analyzed"].append(
                            {
                                "source": source,
                                "type": "youtube",
                                "analysis": source_analysis,
                            }
                        )
                    else:
                        # Treat as text content
                        source_analysis = self._analyze_text_content(source)
                        analysis_results["sources_analyzed"].append(
                            {
                                "source": source,
                                "type": "text",
                                "analysis": source_analysis,
                            }
                        )
                except Exception as e:
                    logger.warning(f"Analysis of {source} failed: {e}")
                    analysis_results["sources_analyzed"].append(
                        {
                            "source": source,
                            "type": "unknown",
                            "analysis": f"Analysis failed: {str(e)}",
                        }
                    )

            # Generate content summary
            analysis_results["content_summary"] = generate_content_summary(
                analysis_results["sources_analyzed"]
            )

            # Generate key insights if requested
            if include_insights:
                analysis_results["key_insights"] = self._extract_key_insights(
                    analysis_results["sources_analyzed"]
                )

            # Format the response
            response = f"📊 **Content Analysis Results**\n\n"
            response += f"📝 **Sources**: {content_sources}\n"
            response += f"🔬 **Analysis Type**: {analysis_type}\n"
            response += f"📊 **Sources Analyzed**: {len(analysis_results['sources_analyzed'])}\n\n"

            # Add content summary
            if analysis_results["content_summary"]:
                response += (
                    f"📋 **Content Summary**\n{analysis_results['content_summary']}\n\n"
                )

            # Add key insights
            if include_insights and analysis_results["key_insights"]:
                response += f"💡 **Key Insights**\n"
                for i, insight in enumerate(analysis_results["key_insights"], 1):
                    response += f"{i}. {insight}\n"
                response += "\n"

            # Add source analysis details
            response += f"🔍 **Source Analysis Details**\n"
            for source_analysis in analysis_results["sources_analyzed"]:
                response += f"**{source_analysis['type'].upper()}**: {source_analysis['source']}\n"
                if isinstance(source_analysis["analysis"], str):
                    response += f"{source_analysis['analysis'][:100]}...\n\n"
                else:
                    response += f"Analysis completed\n\n"

            response += f"⏱️ **Response Time**: <3 seconds (target)"
            return response

        except Exception as e:
            logger.error(f"Error in content analysis: {e}")
            return f"Error analyzing content: {str(e)}"

    async def generate_research_report(
        self,
        topic: str,
        sources: str = "all available",
        report_format: str = "summary",
        include_citations: bool = True,
    ) -> str:
        """Generate a comprehensive research report from multiple sources"""
        try:
            # Validate parameters
            if not topic or not topic.strip():
                return "Error: Research topic is required"

            valid_formats = ["summary", "detailed", "academic"]
            if report_format.lower() not in valid_formats:
                report_format = "summary"
                logger.warning(
                    f"Invalid report_format: {report_format}, defaulting to summary"
                )

            logger.info(
                f"Research report request for: {topic} (format: {report_format}, citations: {include_citations})"
            )

            # Determine sources to use
            if sources == "all available":
                sources_list = ["web", "youtube", "news", "wikipedia"]
            else:
                sources_list = validate_sources(sources)

            # Collect research data
            research_data = await self._collect_research_data(topic, sources_list)

            # Generate report based on format
            if report_format == "summary":
                report_content = generate_summary_report(
                    topic, research_data, include_citations
                )
            elif report_format == "detailed":
                report_content = generate_detailed_report(
                    topic, research_data, include_citations
                )
            elif report_format == "academic":
                report_content = generate_academic_report(
                    topic, research_data, include_citations
                )

            # Format the response
            response = f"📋 **Research Report for '{topic}'**\n\n"
            response += f"📝 **Topic**: {topic}\n"
            response += f"🌐 **Sources**: {', '.join(sources_list)}\n"
            response += f"📄 **Format**: {report_format}\n"
            response += f"📚 **Citations**: {'Included' if include_citations else 'Not included'}\n\n"
            response += f"📊 **Report Content**\n{report_content}\n\n"
            response += f"⏱️ **Response Time**: <3 seconds (target)"

            return response

        except Exception as e:
            logger.error(f"Error generating research report: {e}")
            return f"Error generating research report: {str(e)}"

    async def find_related_content(
        self,
        seed_content: str,
        platforms: str = "all",
        max_related_items: int = 10,
        relevance_threshold: str = "medium",
    ) -> str:
        """Find related content across different platforms"""
        try:
            # Validate parameters
            if not seed_content or not seed_content.strip():
                return "Error: Seed content is required"

            if max_related_items < 1 or max_related_items > 50:
                max_related_items = 10
                logger.warning(
                    f"Invalid max_related_items: {max_related_items}, defaulting to 10"
                )

            valid_thresholds = ["high", "medium", "low"]
            if relevance_threshold.lower() not in valid_thresholds:
                relevance_threshold = "medium"
                logger.warning(
                    f"Invalid relevance_threshold: {relevance_threshold}, defaulting to medium"
                )

            platforms_list = validate_sources(platforms)

            logger.info(
                f"Related content search for: {seed_content} (platforms: {platforms_list}, max: {max_related_items}, threshold: {relevance_threshold})"
            )

            # Find related content on each platform
            related_content: Dict[str, Any] = {}

            for platform in platforms_list:
                try:
                    if platform == "web":
                        # Find related web content
                        related_web = await self._find_related_web_content(
                            seed_content, max_related_items, relevance_threshold
                        )
                        related_content["web"] = related_web
                    elif platform == "youtube":
                        # Find related YouTube content
                        related_youtube = await self._find_related_youtube_content(
                            seed_content, max_related_items, relevance_threshold
                        )
                        related_content["youtube"] = related_youtube
                    elif platform == "news":
                        # Find related news content
                        related_news = await self._find_related_news_content(
                            seed_content, max_related_items, relevance_threshold
                        )
                        related_content["news"] = related_news
                except Exception as e:
                    logger.warning(f"Finding related content on {platform} failed: {e}")
                    related_content[
                        platform
                    ] = f"Related content search unavailable: {str(e)}"

            # Generate relevance analysis
            relevance_analysis = self._analyze_content_relevance(
                seed_content, related_content, relevance_threshold
            )

            # Format the response
            response = f"🔗 **Related Content for '{seed_content}'**\n\n"
            response += f"📝 **Seed Content**: {seed_content}\n"
            response += f"🌐 **Platforms**: {', '.join(platforms_list)}\n"
            response += f"📊 **Max Related Items**: {max_related_items}\n"
            response += f"🎯 **Relevance Threshold**: {relevance_threshold}\n\n"

            # Add related content from each platform
            for platform, content in related_content.items():
                response += f"**{platform.upper()} Related Content**:\n"
                if isinstance(content, str):
                    response += f"{content}\n\n"
                else:
                    response += f"Found {len(content) if isinstance(content, list) else 'some'} related items\n\n"

            # Add relevance analysis
            if relevance_analysis:
                response += f"🎯 **Relevance Analysis**\n"
                for insight in relevance_analysis:
                    response += f"• {insight}\n"
                response += "\n"

            response += f"⏱️ **Response Time**: <3 seconds (target)"
            return response

        except Exception as e:
            logger.error(f"Error finding related content: {e}")
            return f"Error finding related content: {str(e)}"

    async def _analyze_web_content(self, url: str) -> str:
        """Analyze web content from URL"""
        try:
            internet_tool = InternetTool()
            result = await internet_tool.web_search(url, max_results=1)
            if isinstance(result, str):
                return result
            else:
                return f"Web content analysis completed for: {url}"
        except Exception as e:
            return f"Failed to analyze web content: {str(e)}"

    async def _analyze_youtube_content(self, url: str) -> str:
        """Analyze YouTube content from URL"""
        try:
            youtube_tool = YouTubeTool()
            result = await youtube_tool.get_video_info(url)
            if isinstance(result, str):
                return result
            else:
                return f"YouTube content analysis completed for: {url}"
        except Exception as e:
            return f"Failed to analyze YouTube content: {str(e)}"

    def _analyze_text_content(self, text: str) -> str:
        """Analyze text content"""
        try:
            # Simple text analysis
            word_count = len(text.split())
            char_count = len(text)
            return f"Text analysis: {word_count} words, {char_count} characters"
        except Exception as e:
            return f"Failed to analyze text content: {str(e)}"

    def _extract_key_insights(self, sources_analyzed: List[Dict[str, Any]]) -> List[str]:
        """Extract key insights from analyzed sources"""
        try:
            insights = []
            for source in sources_analyzed:
                if source.get("type") == "web":
                    insights.append(f"Web source: {source.get('source', 'Unknown')}")
                elif source.get("type") == "youtube":
                    insights.append(f"YouTube source: {source.get('source', 'Unknown')}")
                elif source.get("type") == "text":
                    insights.append(f"Text content analyzed: {len(source.get('source', ''))} characters")
            return insights
        except Exception as e:
            logger.warning(f"Failed to extract key insights: {e}")
            return ["Key insights extraction failed"]

    async def _collect_research_data(self, topic: str, sources_list: List[str]) -> Dict[str, Any]:
        """Collect research data from multiple sources"""
        try:
            research_data: Dict[str, Any] = {
                "topic": topic,
                "sources": {},
                "summary": "",
                "timestamp": "2024-01-01T00:00:00Z"  # Placeholder
            }
            
            for source in sources_list:
                if source == "web":
                    internet_tool = InternetTool()
                    result = await internet_tool.web_search(topic, max_results=3)
                    # Handle Union[str, dict] return type
                    if isinstance(result, str):
                        research_data["sources"]["web"] = [result]
                    else:
                        research_data["sources"]["web"] = result
                elif source == "youtube":
                    youtube_tool = YouTubeTool()
                    youtube_result: Union[str, dict, list] = await youtube_tool.search_videos(topic, max_results=3)
                    # Handle Union[str, dict] return type
                    if isinstance(youtube_result, str):
                        research_data["sources"]["youtube"] = [youtube_result]
                    elif isinstance(youtube_result, list):
                        research_data["sources"]["youtube"] = youtube_result
                    else:
                        research_data["sources"]["youtube"] = [str(youtube_result)]
                else:
                    research_data["sources"][source] = f"Data collection not implemented for {source}"
            
            return research_data
        except Exception as e:
            logger.warning(f"Failed to collect research data: {e}")
            return {"topic": topic, "sources": {}, "summary": "Data collection failed", "timestamp": "2024-01-01T00:00:00Z"}

    async def _find_related_web_content(self, seed_content: str, max_items: int, threshold: str) -> List[str]:
        """Find related web content"""
        try:
            internet_tool = InternetTool()
            result = await internet_tool.web_search(seed_content, max_results=max_items)
            if isinstance(result, str):
                return [result]
            elif isinstance(result, list):
                return result
            else:
                return [str(result)]
        except Exception as e:
            return [f"Related web content search failed: {str(e)}"]

    async def _find_related_youtube_content(self, seed_content: str, max_items: int, threshold: str) -> List[str]:
        """Find related YouTube content"""
        try:
            youtube_tool = YouTubeTool()
            result = await youtube_tool.search_videos(seed_content, max_results=max_items)
            if isinstance(result, str):
                return [result]
            elif isinstance(result, list):
                return result
            else:
                return [str(result)]
        except Exception as e:
            return [f"Related YouTube content search failed: {str(e)}"]

    async def _find_related_news_content(self, seed_content: str, max_items: int, threshold: str) -> List[str]:
        """Find related news content"""
        try:
            # Placeholder for news search
            return [f"News search not yet implemented for: {seed_content}"]
        except Exception as e:
            return [f"Related news content search failed: {str(e)}"]

    def _analyze_content_relevance(self, seed_content: str, related_content: Dict[str, Any], threshold: str) -> List[str]:
        """Analyze content relevance"""
        try:
            insights = []
            for platform, content in related_content.items():
                if isinstance(content, list) and content:
                    insights.append(f"{platform.title()}: Found {len(content)} related items")
                elif isinstance(content, str):
                    insights.append(f"{platform.title()}: {content}")
            return insights
        except Exception as e:
            return [f"Relevance analysis failed: {str(e)}"]
