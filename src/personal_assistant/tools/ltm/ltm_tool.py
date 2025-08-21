"""
Long-Term Memory (LTM) Tool

This tool provides functionality for managing Long-Term Memory (LTM) entries,
which store insights, patterns, and preferences separate from calendar events
and notes.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

from ...constants.tags import LTM_TAGS, validate_tags, get_tag_suggestions
from ..base import Tool
from .ltm_storage import (
    add_ltm_memory,
    delete_ltm_memory,
    get_ltm_memory_stats,
    get_relevant_ltm_memories,
    search_ltm_memories,
)

logger = logging.getLogger(__name__)


class LTMTool:
    """
    Long-Term Memory (LTM) tool for managing insights, patterns, and preferences.

    This tool provides a clean separation between LTM and other data types
    (calendar events, notes, etc.) by using a dedicated datatable.
    """

    def __init__(self):
        # Create individual tools
        self.add_memory_tool = Tool(
            name="add_ltm_memory",
            func=self.add_memory,
            description="Add a new Long-Term Memory (LTM) entry for insights, patterns, or preferences. This is NOT for creating notes - use create_note or create_note_page for that. LTM memories store user insights, behavioral patterns, preferences, and learning moments.",
            parameters={
                "content": {
                    "type": "string",
                    "description": "The memory content (insight, pattern, preference) - what should be remembered about the user"
                },
                "tags": {
                    "type": "string",
                    "description": f"Comma-separated list of tags from the allowed list: {', '.join(LTM_TAGS[:10])}... (see full list in constants)"
                },
                "importance_score": {
                    "type": "integer",
                    "description": "Importance score from 1-10 (higher = more important)"
                },
                "context": {
                    "type": "string",
                    "description": "Optional context about when/why this memory was created"
                },
                "memory_type": {
                    "type": "string",
                    "description": "Type of memory: preference, insight, pattern, fact, goal, habit, routine, relationship, skill, knowledge",
                    "enum": ["preference", "insight", "pattern", "fact", "goal", "habit", "routine", "relationship", "skill", "knowledge"]
                },
                "category": {
                    "type": "string",
                    "description": "High-level category: work, personal, health, finance, travel, education, entertainment, general"
                },
                "confidence_score": {
                    "type": "number",
                    "description": "Confidence in accuracy from 0.0 to 1.0 (default: 1.0)"
                },
                "source_type": {
                    "type": "string",
                    "description": "Source of the memory: conversation, tool_usage, manual, pattern_detection, automated, import"
                },
                "source_id": {
                    "type": "string",
                    "description": "ID of the source (conversation_id, tool_name, etc.)"
                },
                "created_by": {
                    "type": "string",
                    "description": "Who/what created this memory (default: system)"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional flexible metadata as key-value pairs"
                }
            }
        )

        self.search_memories_tool = Tool(
            name="search_ltm_memories",
            func=self.search_memories,
            description="Search Long-Term Memory (LTM) entries by content",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant memories"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)"
                },
                "min_importance": {
                    "type": "integer",
                    "description": "Minimum importance score to include (default: 1)"
                }
            }
        )

        self.get_relevant_memories_tool = Tool(
            name="get_relevant_ltm_memories",
            func=self.get_relevant_memories,
            description="Get LTM memories relevant to the current conversation context",
            parameters={
                "context": {
                    "type": "string",
                    "description": "Current conversation context to find relevant memories"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 3)"
                }
            }
        )

        self.delete_memory_tool = Tool(
            name="delete_ltm_memory",
            func=self.delete_memory,
            description="Delete a Long-Term Memory (LTM) entry",
            parameters={
                "memory_id": {
                    "type": "integer",
                    "description": "ID of the memory to delete"
                }
            }
        )

        self.get_stats_tool = Tool(
            name="get_ltm_stats",
            func=self.get_stats,
            description="Get statistics about LTM memories",
            parameters={}
        )

        self.get_enhanced_memories_tool = Tool(
            name="get_enhanced_ltm_memories",
            func=self.get_enhanced_memories,
            description="Get LTM memories with enhanced context and filtering capabilities",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant memories (optional - if not provided, returns recent memories)"
                },
                "memory_type": {
                    "type": "string",
                    "description": "Filter by memory type (preference, insight, pattern, etc.)",
                    "enum": ["preference", "insight", "pattern", "fact", "goal", "habit", "routine", "relationship", "skill", "knowledge"]
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category (work, personal, health, etc.)"
                },
                "min_importance": {
                    "type": "integer",
                    "description": "Minimum importance score to include (default: 1)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)"
                },
                "include_context": {
                    "type": "boolean",
                    "description": "Whether to include enhanced context information (default: true)"
                }
            }
        )

        self.get_memory_relationships_tool = Tool(
            name="get_memory_relationships",
            func=self.get_memory_relationships,
            description="Get relationships between LTM memories",
            parameters={
                "memory_id": {
                    "type": "integer",
                    "description": "ID of the memory to find relationships for"
                }
            }
        )

        self.get_memory_analytics_tool = Tool(
            name="get_memory_analytics",
            func=self.get_memory_analytics,
            description="Get comprehensive analytics about LTM memories",
            parameters={}
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        yield self.add_memory_tool
        yield self.search_memories_tool
        yield self.get_relevant_memories_tool
        yield self.delete_memory_tool
        yield self.get_stats_tool
        yield self.get_enhanced_memories_tool
        yield self.get_memory_relationships_tool
        yield self.get_memory_analytics_tool

    async def add_memory(
        self,
        content: str,
        tags: str,
        importance_score: int = 5,
        context: str = None,
        memory_type: str = None,
        category: str = None,
        confidence_score: float = 1.0,
        source_type: str = None,
        source_id: str = None,
        created_by: str = "system",
        metadata: dict = None,
        **kwargs  # Accept additional kwargs to handle unexpected parameters gracefully
    ) -> str:
        """
        Add a new LTM memory entry.

        Args:
            content: The memory content (insight, pattern, preference)
            tags: Comma-separated list of tags
            importance_score: Importance score (1-10)
            context: Optional legacy context about when/why this memory was created
            memory_type: Type of memory (preference, insight, pattern, etc.)
            category: High-level category (work, personal, health, etc.)
            confidence_score: Confidence in accuracy (0.0-1.0)
            source_type: Source of the memory (conversation, tool_usage, etc.)
            source_id: ID of the source
            created_by: Who/what created this memory
            metadata: Additional flexible metadata
            **kwargs: Additional parameters (ignored gracefully for compatibility)

        Returns:
            Success/error message
        """
        try:
            # Log any unexpected parameters for debugging
            if kwargs:
                unexpected_params = list(kwargs.keys())
                logger.info(
                    f"LTM tool received unexpected parameters: {unexpected_params}. These will be ignored.")

                # Log specific unexpected parameters that might indicate confusion with other tools
                if 'title' in kwargs:
                    logger.warning(
                        "LTM tool received 'title' parameter - this suggests the LLM may be confusing it with a note creation tool")
                if 'body' in kwargs:
                    logger.warning(
                        "LTM tool received 'body' parameter - this suggests the LLM may be confusing it with a note creation tool")

            # Parse tags from comma-separated string
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

            # Validate tags against allowed list
            valid_tags, invalid_tags = validate_tags(tag_list)

            if invalid_tags:
                logger.warning(
                    f"Invalid tags provided: {invalid_tags}. Using only valid tags: {valid_tags}")
                if not valid_tags:
                    # If no valid tags, suggest some based on content
                    suggested_tags = get_tag_suggestions(content)
                    logger.info(
                        f"No valid tags provided. Using suggested tags: {suggested_tags}")
                    valid_tags = suggested_tags

            # Validate importance score
            if not 1 <= importance_score <= 10:
                return f"Error: Importance score must be between 1 and 10, got {importance_score}"

            # Validate confidence score
            if not 0.0 <= confidence_score <= 1.0:
                return f"Error: Confidence score must be between 0.0 and 1.0, got {confidence_score}"

            # Get user ID from context or use default
            user_id = "126"  # Default user ID - should be dynamic
            logger.warning(
                f"Using hardcoded user_id: {user_id}. This should be passed from agent context.")

            # Create enhanced context if we have additional information
            enhanced_context = None
            if any([memory_type, category, source_type, source_id, metadata]):
                try:
                    from ...memory.ltm_optimization.context_structures import EnhancedContext, create_default_context

                    enhanced_context = create_default_context()

                    # Add custom context for memory type and category
                    if memory_type:
                        enhanced_context.add_custom_context(
                            "memory_type", value=memory_type)
                    if category:
                        enhanced_context.add_custom_context(
                            "category", value=category)
                    if source_type:
                        enhanced_context.add_custom_context(
                            "source_type", value=source_type)
                    if source_id:
                        enhanced_context.add_custom_context(
                            "source_id", value=source_id)
                    if metadata:
                        for key, value in metadata.items():
                            enhanced_context.add_custom_context(
                                key, value=value)

                except ImportError:
                    logger.info(
                        "Enhanced context features not available, using legacy mode")

            result = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=valid_tags,
                importance_score=importance_score,
                context=context,
                enhanced_context=enhanced_context,
                memory_type=memory_type,
                category=category,
                confidence_score=confidence_score,
                source_type=source_type,
                source_id=source_id,
                created_by=created_by,
                metadata=metadata
            )

            logger.info(f"Successfully created LTM memory: {result}")
            return f"Successfully created LTM memory with ID: {result.get('id', 'unknown')}"

        except Exception as e:
            logger.error(f"Error creating LTM memory: {e}")
            return f"Error creating LTM memory: {str(e)}"

    async def search_memories(
        self,
        query: str,
        limit: int = 5,
        min_importance: int = 1
    ) -> str:
        """
        Search LTM memories by content.

        Args:
            query: Search query
            limit: Maximum number of results
            min_importance: Minimum importance score to include

        Returns:
            Formatted search results
        """
        try:
            # For now, use a default user_id
            user_id = "126"  # Default user ID

            memories = await search_ltm_memories(
                user_id=user_id,
                query=query,
                limit=limit,
                min_importance=min_importance
            )

            if not memories:
                return f"No LTM memories found matching '{query}'"

            # Format results
            result_lines = [
                f"Found {len(memories)} LTM memories matching '{query}':"]
            for i, memory in enumerate(memories, 1):
                result_lines.append(
                    f"{i}. [ID: {memory['id']}, Importance: {memory['importance_score']}] "
                    f"{memory['content'][:100]}... "
                    f"(Tags: {', '.join(memory['tags'])})"
                )

            return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error searching LTM memories: {e}")
            return f"Error searching LTM memories: {str(e)}"

    async def get_relevant_memories(
        self,
        context: str,
        limit: int = 3
    ) -> str:
        """
        Get LTM memories relevant to the current context.

        Args:
            context: Current conversation context
            limit: Maximum number of results

        Returns:
            Formatted relevant memories
        """
        try:
            # For now, use a default user_id
            user_id = "126"  # Default user ID
            logger.info(
                f"Getting relevant memories for user {user_id} with context: {context[:100]}...")

            memories = await get_relevant_ltm_memories(
                user_id=user_id,
                context=context,
                limit=limit
            )

            logger.info(
                f"get_relevant_ltm_memories returned {len(memories) if memories else 0} memories")

            if not memories:
                logger.info(
                    "No memories found, returning 'No relevant LTM memories found' message")
                return f"No relevant LTM memories found for the current context"

            # Format results
            result_lines = [f"Found {len(memories)} relevant LTM memories:"]
            for i, memory in enumerate(memories, 1):
                result_lines.append(
                    f"{i}. [ID: {memory['id']}, Importance: {memory['importance_score']}] "
                    f"{memory['content'][:100]}... "
                    f"(Tags: {', '.join(memory['tags'])})"
                )

            formatted_result = "\n".join(result_lines)
            logger.info(f"Formatted result: {formatted_result[:200]}...")
            return formatted_result

        except Exception as e:
            logger.error(f"Error getting relevant LTM memories: {e}")
            return f"Error getting relevant LTM memories: {str(e)}"

    async def delete_memory(self, memory_id: int) -> str:
        """
        Delete an LTM memory entry.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            Success/error message
        """
        try:
            # For now, use a default user_id
            user_id = "126"  # Default user ID

            success = await delete_ltm_memory(
                user_id=user_id,
                memory_id=memory_id
            )

            if success:
                return f"Successfully deleted LTM memory with ID {memory_id}"
            else:
                return f"Failed to delete LTM memory with ID {memory_id} (not found or access denied)"

        except Exception as e:
            logger.error(f"Error deleting LTM memory: {e}")
            return f"Error deleting LTM memory: {str(e)}"

    async def get_stats(self) -> str:
        """
        Get statistics about LTM memories.

        Returns:
            Formatted statistics
        """
        try:
            # For now, use a default user_id
            user_id = "126"  # Default user ID

            stats = await get_ltm_memory_stats(user_id=user_id)

            result_lines = ["LTM Memory Statistics:"]
            result_lines.append(f"- Total memories: {stats['total_memories']}")
            result_lines.append(
                f"- Average importance: {stats['average_importance']}")

            if stats['top_tags']:
                result_lines.append("- Top tags:")
                for tag, count in stats['top_tags']:
                    result_lines.append(f"  • {tag}: {count}")
            else:
                result_lines.append("- No tags found")

            return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error getting LTM stats: {e}")
            return f"Error getting LTM stats: {str(e)}"

    async def get_enhanced_memories(
        self,
        query: str = None,
        memory_type: str = None,
        category: str = None,
        min_importance: int = 1,
        limit: int = 5,
        include_context: bool = True
    ) -> str:
        """
        Get LTM memories with enhanced context and filtering capabilities.
        """
        try:
            # TODO: Get user_id from agent context - for now use a default
            user_id = "126"  # Default user ID - should be dynamic
            logger.warning(
                f"Using hardcoded user_id: {user_id}. This should be passed from agent context.")

            # If no query provided, use a default to get recent memories
            if not query:
                query = "recent memories"
                logger.info(
                    "No query provided, using default 'recent memories'")

            # Import enhanced storage functions
            try:
                from .enhanced_ltm_storage import search_enhanced_ltm_memories

                memories = await search_enhanced_ltm_memories(
                    user_id=user_id,
                    query=query,
                    limit=limit,
                    min_importance=min_importance,
                    memory_type=memory_type,
                    category=category,
                    include_context=include_context
                )

                if not memories:
                    return f"No memories found matching query: '{query}'"

                # Format results
                result_lines = [
                    f"Found {len(memories)} memories matching '{query}':"]
                for i, memory in enumerate(memories, 1):
                    result_lines.append(f"\n{i}. ID: {memory['id']}")
                    result_lines.append(
                        f"   Content: {memory['content'][:100]}...")
                    result_lines.append(
                        f"   Type: {memory.get('memory_type', 'unknown')}")
                    result_lines.append(
                        f"   Category: {memory.get('category', 'unknown')}")
                    result_lines.append(
                        f"   Importance: {memory.get('importance_score', 'unknown')}")
                    result_lines.append(
                        f"   Tags: {', '.join(memory.get('tags', []))}")

                    if include_context and memory.get('enhanced_context'):
                        context_summary = self._format_context_summary(
                            memory['enhanced_context'])
                        if context_summary:
                            result_lines.append(
                                f"   Context: {context_summary}")

                return "\n".join(result_lines)

            except ImportError:
                logger.info(
                    "Enhanced storage not available, using legacy search")
                # Fall back to legacy search
                return "Enhanced search not available. Please use the basic search function."

        except Exception as e:
            logger.error(f"Error searching enhanced memories: {e}")
            return f"Error searching memories: {str(e)}"

    async def get_memory_relationships(
        self,
        memory_id: int
    ) -> str:
        """
        Get relationships between LTM memories.
        """
        try:
            # TODO: Get user_id from agent context - for now use a default
            user_id = "126"  # Default user ID - should be dynamic
            logger.warning(
                f"Using hardcoded user_id: {user_id}. This should be passed from agent context.")

            # Import enhanced storage functions
            try:
                from .enhanced_ltm_storage import get_memory_relationships

                relationships = await get_memory_relationships(
                    memory_id=memory_id,
                    user_id=user_id
                )

                if not relationships:
                    return f"No relationships found for memory {memory_id}"

                # Format results
                result_lines = [f"Relationships for memory {memory_id}:"]
                for i, rel in enumerate(relationships, 1):
                    result_lines.append(
                        f"\n{i}. Type: {rel['relationship_type']}")
                    result_lines.append(f"   Strength: {rel['strength']}")
                    if rel.get('description'):
                        result_lines.append(
                            f"   Description: {rel['description']}")

                    related_memory = rel.get('related_memory', {})
                    if related_memory:
                        result_lines.append(
                            f"   Related Memory ID: {related_memory['id']}")
                        result_lines.append(
                            f"   Content: {related_memory['content'][:100]}...")
                        result_lines.append(
                            f"   Type: {related_memory.get('memory_type', 'unknown')}")

                return "\n".join(result_lines)

            except ImportError:
                logger.info("Enhanced storage not available")
                return "Enhanced relationship features not available."

        except Exception as e:
            logger.error(f"Error getting memory relationships: {e}")
            return f"Error getting relationships: {str(e)}"

    async def get_memory_analytics(
        self
    ) -> str:
        """
        Get comprehensive analytics about LTM memories.
        """
        try:
            # TODO: Get user_id from agent context - for now use a default
            user_id = "126"  # Default user ID - should be dynamic
            logger.warning(
                f"Using hardcoded user_id: {user_id}. This should be passed from agent context.")

            # Import enhanced storage functions
            try:
                from .enhanced_ltm_storage import get_memory_analytics

                analytics = await get_memory_analytics(user_id=user_id)

                if not analytics:
                    return "No analytics available"

                # Format results
                result_lines = ["LTM Memory Analytics:"]
                result_lines.append(
                    f"\nTotal Memories: {analytics.get('total_memories', 0)}")

                if analytics.get('type_distribution'):
                    result_lines.append("\nMemory Type Distribution:")
                    for mem_type, count in analytics['type_distribution'].items():
                        result_lines.append(f"  {mem_type}: {count}")

                if analytics.get('category_distribution'):
                    result_lines.append("\nCategory Distribution:")
                    for category, count in analytics['category_distribution'].items():
                        result_lines.append(f"  {category}: {count}")

                result_lines.append(
                    f"\nAverage Importance: {analytics.get('average_importance', 0)}")
                result_lines.append(
                    f"Average Dynamic Importance: {analytics.get('average_dynamic_importance', 0)}")

                if analytics.get('most_accessed_memories'):
                    result_lines.append("\nMost Accessed Memories:")
                    for i, memory in enumerate(analytics['most_accessed_memories'][:3], 1):
                        result_lines.append(
                            f"  {i}. ID: {memory['id']} (accessed {memory['access_count']} times)")
                        result_lines.append(
                            f"     Content: {memory['content'][:80]}...")

                return "\n".join(result_lines)

            except ImportError:
                logger.info("Enhanced storage not available")
                return "Enhanced analytics features not available."

        except Exception as e:
            logger.error(f"Error getting memory analytics: {e}")
            return f"Error getting analytics: {str(e)}"

    def _format_context_summary(self, context: dict) -> str:
        """Format context information for display"""
        if not context:
            return ""

        parts = []
        for context_type, context_data in context.items():
            if isinstance(context_data, dict):
                for key, value in context_data.items():
                    if value:
                        parts.append(f"{context_type}.{key}: {value}")

        return "; ".join(parts) if parts else ""
