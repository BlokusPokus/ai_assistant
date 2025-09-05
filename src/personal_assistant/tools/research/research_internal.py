"""
Internal functions for Research Tool.

This module contains internal utility functions and helper methods
that are used by the main ResearchTool class.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def validate_sources(sources: str) -> List[str]:
    """Validate and normalize source parameters"""
    valid_sources = ["web", "youtube", "news", "wikipedia"]
    if sources.lower() == "both":
        return ["web", "youtube"]
    elif sources.lower() == "all":
        return valid_sources
    else:
        source_list = [s.strip().lower() for s in sources.split(",")]
        return [s for s in source_list if s in valid_sources]


def validate_analysis_type(analysis_type: str) -> str:
    """Validate and normalize analysis type"""
    valid_types = ["summary", "comparison", "synthesis"]
    if analysis_type.lower() not in valid_types:
        logger.warning(
            f"Invalid analysis_type: {analysis_type}, defaulting to synthesis"
        )
        return "synthesis"
    return analysis_type.lower()


def validate_report_format(report_format: str) -> str:
    """Validate and normalize report format"""
    valid_formats = ["summary", "detailed", "academic"]
    if report_format.lower() not in valid_formats:
        logger.warning(f"Invalid report_format: {report_format}, defaulting to summary")
        return "summary"
    return report_format.lower()


def validate_relevance_threshold(threshold: str) -> str:
    """Validate and normalize relevance threshold"""
    valid_thresholds = ["high", "medium", "low"]
    if threshold.lower() not in valid_thresholds:
        logger.warning(
            f"Invalid relevance_threshold: {threshold}, defaulting to medium"
        )
        return "medium"
    return threshold.lower()


def validate_search_parameters(
    max_results: int, max_results_per_platform: int, max_related_items: int
) -> tuple[int, int, int]:
    """Validate and normalize search parameters"""
    if max_results < 1 or max_results > 20:
        max_results = 5
        logger.warning(f"Invalid max_results: {max_results}, defaulting to 5")

    if max_results_per_platform < 1 or max_results_per_platform > 10:
        max_results_per_platform = 3
        logger.warning(
            f"Invalid max_results_per_platform: {max_results_per_platform}, defaulting to 3"
        )

    if max_related_items < 1 or max_related_items > 50:
        max_related_items = 10
        logger.warning(
            f"Invalid max_related_items: {max_related_items}, defaulting to 10"
        )

    return max_results, max_results_per_platform, max_related_items


def format_research_response(
    topic: str,
    sources_list: List[str],
    max_results: int,
    research_results: dict,
    include_summary: bool = True,
) -> str:
    """Format the research response in a consistent way"""
    response = f"🔬 **Research Results for '{topic}'**\n\n"
    response += f"📝 **Topic**: {topic}\n"
    response += f"🌐 **Sources**: {', '.join(sources_list)}\n"
    response += f"📊 **Max Results per Source**: {max_results}\n\n"

    # Add web results
    if "web" in sources_list and research_results.get("web"):
        response += f"🌐 **Web Search Results**\n"
        if isinstance(research_results["web"], str):
            response += f"{research_results['web']}\n\n"
        else:
            response += f"Found web results (see details above)\n\n"

    # Add YouTube results
    if "youtube" in sources_list and research_results.get("youtube"):
        response += f"🎬 **YouTube Search Results**\n"
        if isinstance(research_results["youtube"], str):
            response += f"{research_results['youtube']}\n\n"
        else:
            response += f"Found YouTube results (see details above)\n\n"

    # Add research summary
    if include_summary and research_results.get("summary"):
        response += f"📋 **Research Summary**\n{research_results['summary']}\n\n"

    response += f"⏱️ **Response Time**: <3 seconds (target)"
    return response


def format_combined_search_response(
    query: str,
    platforms_list: List[str],
    max_results_per_platform: int,
    search_results: dict,
    correlation_insights: List[str] | None = None,
) -> str:
    """Format the combined search response in a consistent way"""
    response = f"🔍 **Combined Search Results for '{query}'**\n\n"
    response += f"📝 **Query**: {query}\n"
    response += f"🌐 **Platforms**: {', '.join(platforms_list)}\n"
    response += f"📊 **Max Results per Platform**: {max_results_per_platform}\n\n"

    # Add results from each platform
    for platform, results in search_results.items():
        if results:
            response += f"🌐 **{platform.title()} Results**\n"
            if isinstance(results, str):
                response += f"{results}\n\n"
            else:
                response += f"Found {platform} results (see details above)\n\n"

    # Add correlation insights if available
    if correlation_insights:
        response += f"🔗 **Cross-Platform Insights**\n"
        for insight in correlation_insights:
            response += f"• {insight}\n"
        response += "\n"

    response += f"⏱️ **Response Time**: <3 seconds (target)"
    return response


def generate_correlation_insights(
    search_results: dict, platforms_list: List[str]
) -> List[str]:
    """Generate insights about correlations between different platforms"""
    insights = []

    # Count available platforms
    available_platforms = [
        p
        for p, c in search_results.items()
        if isinstance(c, list)
        or ("Error" not in str(c) and "failed" not in str(c).lower())
    ]

    if available_platforms:
        insights.append(
            f"Results found on {len(available_platforms)} platforms: {', '.join(available_platforms)}"
        )

        # Cross-platform insights
        if len(available_platforms) > 1:
            insights.append(
                "Cross-platform content available for comprehensive analysis"
            )
            insights.append("Consider comparing perspectives across different sources")
    else:
        insights.append("Limited results found - consider adjusting search parameters")

    return insights


def generate_research_summary(topic: str, research_results: Dict[str, Any]) -> str:
    """Generate a summary of research results"""
    try:
        summary_parts = []
        summary_parts.append(f"Research Summary for '{topic}':")

        # Analyze web results
        if research_results.get("web"):
            if isinstance(research_results["web"], str):
                if (
                    "Error" not in research_results["web"]
                    and "unavailable" not in research_results["web"].lower()
                ):
                    summary_parts.append("• Web search completed successfully")
                else:
                    summary_parts.append("• Web search encountered issues")
            else:
                summary_parts.append("• Web search returned structured results")

        # Analyze YouTube results
        if research_results.get("youtube"):
            if isinstance(research_results["youtube"], str):
                if (
                    "Error" not in research_results["youtube"]
                    and "unavailable" not in research_results["youtube"].lower()
                ):
                    summary_parts.append("• YouTube search completed successfully")
                else:
                    summary_parts.append("• YouTube search encountered issues")
            else:
                summary_parts.append("• YouTube search returned structured results")

        # Overall assessment
        successful_searches = sum(
            1
            for source in ["web", "youtube"]
            if research_results.get(source)
            and isinstance(research_results[source], str)
            and "Error" not in research_results[source]
            and "unavailable" not in research_results[source].lower()
        )

        if successful_searches > 0:
            summary_parts.append(
                f"• Research completed with {successful_searches} successful source(s)"
            )
        else:
            summary_parts.append("• Research encountered issues with all sources")

        return "\n".join(summary_parts)

    except Exception as e:
        logger.error(f"Error generating research summary: {e}")
        return f"Error generating research summary: {str(e)}"


def generate_content_summary(sources_analyzed: List[Dict[str, Any]]) -> str:
    """Generate a summary of analyzed content"""
    try:
        if not sources_analyzed:
            return "No content sources analyzed"

        summary_parts = []
        summary_parts.append("Content Analysis Summary:")

        # Count successful analyses
        successful_analyses = sum(
            1 for source in sources_analyzed if source.get("status") == "success"
        )

        summary_parts.append(
            f"• Successfully analyzed {successful_analyses} out of {len(sources_analyzed)} sources"
        )

        # Identify content types
        content_types = set()
        for source in sources_analyzed:
            if source.get("content_type"):
                content_types.add(source["content_type"])

        if content_types:
            summary_parts.append(f"• Content types found: {', '.join(content_types)}")

        # Overall assessment
        if successful_analyses > 0:
            summary_parts.append("• Content analysis completed successfully")
        else:
            summary_parts.append(
                "• Content analysis encountered issues with all sources"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        logger.error(f"Error generating content summary: {e}")
        return f"Error generating content summary: {str(e)}"


def generate_summary_report(
    topic: str, research_data: Dict[str, Any], include_citations: bool
) -> str:
    """Generate a summary research report"""
    try:
        report = f"📋 **Research Report Summary: {topic}**\n\n"

        # Key findings
        if research_data.get("key_findings"):
            report += "🔍 **Key Findings**\n"
            for finding in research_data["key_findings"][:3]:  # Top 3 findings
                report += f"• {finding}\n"
            report += "\n"

        # Sources used
        if research_data.get("sources"):
            report += "📚 **Sources Used**\n"
            for source in research_data["sources"][:5]:  # Top 5 sources
                report += f"• {source}\n"
            report += "\n"

        # Citations if requested
        if include_citations and research_data.get("citations"):
            report += "📖 **Citations**\n"
            for citation in research_data["citations"][:3]:  # Top 3 citations
                report += f"• {citation}\n"
            report += "\n"

        report += "📝 **Report Type**: Summary\n"
        report += "⏱️ **Generated**: <3 seconds (target)"

        return report

    except Exception as e:
        logger.error(f"Error generating summary report: {e}")
        return f"Error generating summary report: {str(e)}"


def generate_detailed_report(
    topic: str, research_data: Dict[str, Any], include_citations: bool
) -> str:
    """Generate a detailed research report"""
    try:
        report = f"📋 **Detailed Research Report: {topic}**\n\n"

        # Executive summary
        if research_data.get("executive_summary"):
            report += "📊 **Executive Summary**\n"
            report += f"{research_data['executive_summary']}\n\n"

        # Methodology
        report += "🔬 **Methodology**\n"
        report += "• Multi-source research approach\n"
        report += "• Cross-platform content analysis\n"
        report += "• Automated synthesis and correlation\n\n"

        # Detailed findings
        if research_data.get("detailed_findings"):
            report += "🔍 **Detailed Findings**\n"
            for finding in research_data["detailed_findings"]:
                report += f"• {finding}\n"
            report += "\n"

        # Sources and citations
        if research_data.get("sources"):
            report += "📚 **Sources**\n"
            for source in research_data["sources"]:
                report += f"• {source}\n"
            report += "\n"

        if include_citations and research_data.get("citations"):
            report += "📖 **Citations**\n"
            for citation in research_data["citations"]:
                report += f"• {citation}\n"
            report += "\n"

        report += "📝 **Report Type**: Detailed\n"
        report += "⏱️ **Generated**: <3 seconds (target)"

        return report

    except Exception as e:
        logger.error(f"Error generating detailed report: {e}")
        return f"Error generating detailed report: {str(e)}"


def generate_academic_report(
    topic: str, research_data: Dict[str, Any], include_citations: bool
) -> str:
    """Generate an academic-style research report"""
    try:
        report = f"📋 **Academic Research Report: {topic}**\n\n"

        # Abstract
        if research_data.get("abstract"):
            report += "📝 **Abstract**\n"
            report += f"{research_data['abstract']}\n\n"

        # Introduction
        report += "📖 **Introduction**\n"
        report += f"This report presents a comprehensive analysis of '{topic}' based on multi-source research.\n\n"

        # Literature review
        if research_data.get("sources"):
            report += "📚 **Literature Review**\n"
            report += "The research draws from multiple sources including:\n"
            for source in research_data["sources"]:
                report += f"• {source}\n"
            report += "\n"

        # Methodology
        report += "🔬 **Methodology**\n"
        report += "• Systematic literature review\n"
        report += "• Cross-platform content analysis\n"
        report += "• Automated synthesis and correlation\n"
        report += "• Quality assessment and validation\n\n"

        # Results and discussion
        if research_data.get("key_findings"):
            report += "🔍 **Results and Discussion**\n"
            for finding in research_data["key_findings"]:
                report += f"• {finding}\n"
            report += "\n"

        # Conclusion
        report += "📋 **Conclusion**\n"
        report += f"This research provides a comprehensive understanding of '{topic}' through multi-source analysis.\n\n"

        # References
        if include_citations and research_data.get("citations"):
            report += "📖 **References**\n"
            for i, citation in enumerate(research_data["citations"], 1):
                report += f"{i}. {citation}\n"
            report += "\n"

        report += "📝 **Report Type**: Academic\n"
        report += "⏱️ **Generated**: <3 seconds (target)"

        return report

    except Exception as e:
        logger.error(f"Error generating academic report: {e}")
        return f"Error generating academic report: {str(e)}"
