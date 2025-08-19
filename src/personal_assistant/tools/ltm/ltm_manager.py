"""
LTM (Long-Term Memory) management utilities.

This module contains standalone functions for managing LTM operations,
extracted from the AgentCore class for better code organization.
"""

from ...constants.tags import get_tag_suggestions
from ...prompts.templates.ltm.tag_selection import get_tag_selection_prompt
from ...config.logging_config import get_logger

# Import the new LTM optimization components
try:
    from ...memory.ltm_optimization import (
        SmartLTMRetriever,
        ContextOptimizationManager,
        LTMConfig
    )
    logger = get_logger("ltm_manager")
    logger.info("LTM optimization components available, using smart LTM system")
except ImportError:
    logger = get_logger("ltm_manager")
    logger.warning(
        "LTM optimization components not available, using fallback implementation")


# Set up logging
logger = get_logger("ltm_manager")


async def get_ltm_context_with_tags(ltm_tool, logger, user_id: str, user_input: str, focus_areas: list = None) -> str:
    """
    Get optimized LTM context using the new smart LTM optimization system.

    Args:
        ltm_tool: The LTM tool instance (can be None - will use smart system)
        logger: Logger instance
        user_id: User ID
        user_input: Current user input
        focus_areas: Optional focus areas for tag-based filtering

    Returns:
        Formatted LTM context string
    """
    try:
        logger.info(
            f"Getting smart LTM context for user {user_id} with input: {user_input[:100]}...")
        logger.info(f"Focus areas provided: {focus_areas}")

        # Always try to use the smart system first
        try:
            return await _get_smart_ltm_context(user_id, user_input, focus_areas, logger)
        except Exception as e:
            logger.warning(f"Smart LTM system failed: {e}, using fallback")
            # Only use fallback if ltm_tool is provided
            if ltm_tool:
                return await _get_fallback_ltm_context(ltm_tool, user_id, user_input, focus_areas, logger)
            else:
                logger.warning(
                    "No LTM tool provided and smart system failed, returning empty context")
                return ""

    except Exception as e:
        logger.warning(f"Error getting LTM context: {e}")
        return ""


async def _get_smart_ltm_context(user_id: str, user_input: str, focus_areas: list, logger) -> str:
    """
    Get LTM context using the smart optimization system.

    Args:
        user_id: User ID
        user_input: Current user input
        focus_areas: Optional focus areas for tag-based filtering
        logger: Logger instance

    Returns:
        Optimized LTM context string
    """
    try:
        # Step 1: Get relevant memories using smart retriever
        smart_retriever = SmartLTMRetriever()
        relevant_memories = await smart_retriever.get_relevant_memories(
            user_id=user_id,
            context=user_input,
            limit=5  # Limit to top 5 most relevant memories
        )

        if not relevant_memories:
            logger.info("No relevant memories found by smart retriever")
            return ""

        # Step 2: Optimize context for injection
        context_optimizer = ContextOptimizationManager()
        optimized_context = await context_optimizer.optimize_ltm_context(
            memories=relevant_memories,
            user_input=user_input,
            max_length=800  # Keep context concise for LLM injection
        )

        if optimized_context:
            logger.info(
                f"Smart LTM context generated: {len(optimized_context)} chars")
            return f"**Smart Long-Term Memory Context:**\n{optimized_context}\n"
        else:
            logger.info("No optimized context generated")
            return ""

    except Exception as e:
        logger.warning(f"Error in smart LTM context generation: {e}")
        return ""


async def _get_fallback_ltm_context(ltm_tool, user_id: str, user_input: str, focus_areas: list, logger) -> str:
    """
    Fallback LTM context retrieval using the original implementation.

    Args:
        ltm_tool: The LTM tool instance
        user_id: User ID
        user_input: Current user input
        focus_areas: Optional focus areas for tag-based filtering
        logger: Logger instance

    Returns:
        Formatted LTM context string
    """
    try:
        # If no focus areas provided, suggest tags based on user input
        if not focus_areas:
            suggested_tags = get_tag_suggestions(user_input)
            focus_areas = suggested_tags
            logger.info(
                f"Generated focus areas from user input: {focus_areas}")

        # Get relevant LTM memories using the LTM tool
        logger.info(
            f"Calling ltm_tool.get_relevant_memories with context: {user_input[:100]}...")
        ltm_context = await ltm_tool.get_relevant_memories(
            context=user_input,
            limit=10
        )

        logger.info(
            f"LTM tool returned: {ltm_context[:200] if ltm_context else 'None'}...")

        if ltm_context and "No relevant LTM memories found" not in ltm_context:
            logger.info(f"Found LTM context, returning formatted result")
            return f"**Long-Term Memory Context:**\n{ltm_context}\n"
        else:
            logger.info("No LTM memories found or empty result")
            return ""

    except Exception as e:
        logger.warning(f"Error in fallback LTM context retrieval: {e}")
        return ""


async def should_create_ltm_memory(user_input: str, response: str, importance_threshold: int = 7) -> bool:
    """
    Determine if an LTM memory should be created based on content analysis.

    Args:
        user_input: User's input
        response: Agent's response
        importance_threshold: Minimum importance score to consider

    Returns:
        True if LTM memory should be created
    """
    logger.info(
        f"Evaluating if LTM memory should be created for: {user_input[:100]}...")

    # Check for explicit memory requests
    memory_keywords = [
        "remember this", "save this", "note this", "keep this in mind",
        "important", "urgent", "critical", "preference", "habit", "pattern"
    ]

    combined_text = f"{user_input} {response}".lower()
    logger.info(f"Combined text to analyze: {combined_text[:200]}...")

    # Check for explicit memory requests
    explicit_matches = [
        keyword for keyword in memory_keywords if keyword in combined_text]
    if explicit_matches:
        logger.info(f"Explicit memory keywords found: {explicit_matches}")
        return True

    # Check for personal information or preferences
    personal_keywords = [
        "i prefer", "i like", "i dislike", "i always", "i never",
        "my preference", "my habit", "my routine", "i work", "i live"
    ]

    personal_matches = [
        keyword for keyword in personal_keywords if keyword in combined_text]
    if personal_matches:
        logger.info(f"Personal preference keywords found: {personal_matches}")
        return True

    # Check for behavioral patterns
    pattern_keywords = [
        "every day", "every week", "every month", "usually", "typically",
        "always", "never", "often", "sometimes", "routine"
    ]

    pattern_matches = [
        keyword for keyword in pattern_keywords if keyword in combined_text]
    if pattern_matches:
        logger.info(f"Behavioral pattern keywords found: {pattern_matches}")
        return True

    logger.info("No LTM memory creation criteria met")
    return False


async def create_ltm_memory_if_needed(ltm_tool, llm, logger, user_id: str, user_input: str, response: str, conversation_context: str = None):
    """
    Create LTM memory if the content warrants it.

    Args:
        ltm_tool: The LTM tool instance (can be None)
        llm: The LLM instance
        logger: Logger instance
        user_id: User ID
        user_input: User's input
        response: Agent's response
        conversation_context: Optional conversation context
    """
    try:
        # If no LTM tool is provided, skip memory creation
        if not ltm_tool:
            logger.info("No LTM tool provided, skipping memory creation")
            return

        logger.info(
            f"Checking if LTM memory should be created for user {user_id}")
        logger.info(f"User input: {user_input[:100]}...")
        logger.info(f"Response: {response[:100]}...")

        if await should_create_ltm_memory(user_input, response):
            logger.info("LTM memory creation triggered - content warrants it")

            # Generate content for LTM memory
            ltm_content = f"User: {user_input}\nAgent: {response}"

            # Get tag suggestions from the LLM using our prompt template
            tag_prompt = get_tag_selection_prompt(
                content=ltm_content,
                context=conversation_context or "Conversation insight"
            )

            # Get LLM to select appropriate tags
            logger.info("Getting tag suggestions from LLM...")
            tag_response = await llm.generate(tag_prompt)
            logger.info(f"LLM tag response: {tag_response}")

            # Parse tags from LLM response (should be comma-separated)
            if tag_response and "," in tag_response:
                tags = tag_response.strip()
                logger.info(f"Using LLM-suggested tags: {tags}")
            else:
                # Fallback to automatic tag suggestions
                tags = ",".join(get_tag_suggestions(ltm_content))
                logger.info(f"Using fallback tags: {tags}")

            # Determine importance score based on content
            importance_score = 7  # Default for insights
            if any(word in ltm_content.lower() for word in ["urgent", "critical", "important"]):
                importance_score = 9
            elif any(word in ltm_content.lower() for word in ["preference", "habit", "routine"]):
                importance_score = 8

            logger.info(
                f"Creating LTM memory with importance score: {importance_score}")

            # Create LTM memory
            result = await ltm_tool.add_memory(
                content=ltm_content,
                tags=tags,
                importance_score=importance_score,
                context=conversation_context or "Automatically created from conversation"
            )

            logger.info(f"LTM memory creation result: {result}")
        else:
            logger.info(
                "LTM memory creation not triggered - content doesn't warrant it")

    except Exception as e:
        logger.warning(f"Error creating LTM memory: {e}")
