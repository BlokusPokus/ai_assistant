"""
LLM-based Memory Creator

This module uses LLM intelligence to decide what memories to create from user interactions.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...config.logging_config import get_logger
from ...constants.tags import LTM_TAGS, validate_tags
from ...tools.ltm.ltm_storage import add_ltm_memory
from ...types.state import AgentState
from ...utils.ai_tag_validator import validate_ai_generated_tags
from .config import EnhancedLTMConfig, LTMConfig
from .enhanced_tag_suggester import EnhancedTagSuggester

logger = get_logger("llm_memory_creator")


class LLMMemoryCreator:
    """Uses LLM to intelligently create memories from interactions"""

    def __init__(self, config: LTMConfig, llm):
        self.config = config
        self.llm = llm
        self.tag_suggester = EnhancedTagSuggester(config)

    async def create_memories_from_interaction(
        self,
        user_id: int,
        user_input: str,
        agent_response: str,
        tool_result: str = None,
        conversation_context: str = None,
    ) -> List[dict]:
        """Use LLM to intelligently create memories from interaction"""

        try:
            logger.info(f"Starting LLM memory creation for user {user_id}")
            logger.info(f"User input: {user_input[:100]}...")
            logger.info(f"Agent response: {agent_response[:100]}...")

            # Prepare the prompt for the LLM
            prompt = self._create_memory_creation_prompt(
                user_input, agent_response, tool_result, conversation_context
            )

            logger.info(f"Created prompt with {len(prompt)} characters")

            # Get LLM response
            logger.info("Calling LLM for memory creation...")
            llm_response = await self._get_llm_response(prompt)
            logger.info(f"LLM response received: {llm_response[:200]}...")

            # Parse the LLM response
            memory_specs = self._parse_llm_response(llm_response)
            logger.info(f"Parsed {len(memory_specs)} memory specifications")

            # Create actual memories
            created_memories = []
            for spec in memory_specs:
                memory = await self._create_memory_from_spec(user_id, spec)
                if memory:
                    created_memories.append(memory)

            logger.info(f"LLM created {len(memory_specs)} memory specifications")
            return created_memories

        except Exception as e:
            logger.error(f"Error in LLM memory creation: {e}")
            return []

    async def create_memories_from_interaction_with_state(
        self,
        user_id: int,
        user_input: str,
        agent_response: str,
        state_data: AgentState,
        tool_result: str = None,
        conversation_context: str = None,
    ) -> List[dict]:
        """
        Use LLM to intelligently create memories from interaction with state data integration.

        This enhanced method incorporates state management data for richer context
        and better memory quality.

        Args:
            user_id: User ID for memory creation
            user_input: Current user input
            agent_response: Current agent response
            state_data: Complete agent state for context
            tool_result: Tool execution result if applicable
            conversation_context: Additional conversation context

        Returns:
            List of created memories with enhanced quality
        """
        try:
            logger.info(
                f"Starting enhanced LLM memory creation with state for user {user_id}"
            )

            # Prepare enhanced prompt with state data
            prompt = self._create_enhanced_memory_creation_prompt(
                user_input,
                agent_response,
                state_data,
                tool_result,
                conversation_context,
            )

            logger.info(f"Created enhanced prompt with {len(prompt)} characters")

            # Get LLM response
            logger.info("Calling LLM for enhanced memory creation...")
            llm_response = await self._get_llm_response(prompt)
            logger.info(f"LLM response received: {llm_response[:200]}...")

            # Parse the LLM response
            memory_specs = self._parse_enhanced_llm_response(llm_response)
            logger.info(f"Parsed {len(memory_specs)} enhanced memory specifications")

            # Validate and score memory quality
            validated_specs = []
            for spec in memory_specs:
                quality_score = await self._validate_memory_quality(spec, state_data)
                if quality_score >= self._get_quality_threshold():
                    spec["quality_score"] = quality_score
                    validated_specs.append(spec)
                else:
                    logger.info(
                        f"Memory spec rejected due to low quality: {spec.get('content', '')[:50]}..."
                    )

            # Create actual memories with quality validation
            created_memories = []
            for spec in validated_specs:
                memory = await self._create_enhanced_memory_from_spec(
                    user_id, spec, state_data
                )
                if memory:
                    created_memories.append(memory)

            logger.info(
                f"Enhanced LLM created {len(created_memories)} quality-validated memories"
            )
            return created_memories

        except Exception as e:
            logger.error(f"Error in enhanced LLM memory creation: {e}")
            return []

    def _create_memory_creation_prompt(
        self,
        user_input: str,
        agent_response: str,
        tool_result: str = None,
        conversation_context: str = None,
    ) -> str:
        """Create an enhanced prompt for LLM memory creation"""

        # Get available tags and organize them by category
        available_tags = LTM_TAGS
        tag_categories = self._categorize_tags_for_prompt(available_tags)

        # Analyze the interaction for context clues
        interaction_analysis = self._analyze_interaction_context(
            user_input, agent_response, tool_result
        )

        # Get suggested tags based on content analysis
        suggested_tags = self._get_suggested_tags_from_content(
            user_input, agent_response
        )

        # Determine potential memory types based on content
        potential_memory_types = self._identify_potential_memory_types(
            user_input, agent_response, tool_result
        )

        prompt = f"""You are an advanced AI memory creation system for a personal AI assistant. Your job is to intelligently analyze user interactions and create high-quality, actionable memories that will help the AI better understand and serve the user.

**INTERACTION TO ANALYZE:**
User Input: {user_input}
Agent Response: {agent_response}
{f"Tool Result: {tool_result}" if tool_result else ""}
{f"Conversation Context: {conversation_context}" if conversation_context else ""}

**INTERACTION ANALYSIS:**
{interaction_analysis}

**AVAILABLE TAGS (EXACT LIST - USE ONLY THESE):**
{', '.join(LTM_TAGS)}

**AVAILABLE TAGS (by category):**
{tag_categories}

**SUGGESTED TAGS:**
{suggested_tags}

**POTENTIAL MEMORY TYPES:**
{potential_memory_types}

**MEMORY CREATION GUIDELINES:**
1. Create 2-4 high-quality memories that capture different aspects of the interaction
2. Focus on user preferences, patterns, insights, and learning moments
3. Use appropriate tags from the available list
4. Ensure memories are specific, actionable, and relevant
5. Avoid creating redundant or overly general memories
6. Consider the user's communication style and preferences

**OUTPUT FORMAT:**
Return a JSON array of memory objects with these fields:
- content: Clear, concise description of what to remember
- tags: Array of relevant tags from the available list
- importance_score: 1-10 score (higher = more important)
- memory_type: One of: preference, pattern, insight, learning, tool_usage, general
- category: One of: work, personal, health, finance, education, general
- confidence_score: 0.0-1.0 confidence in accuracy
- context: Additional context or explanation

**EXAMPLE OUTPUT:**
```json
[
  {{
    "content": "User prefers detailed explanations for technical topics",
    "tags": ["preference", "communication", "technical"],
    "importance_score": 7,
    "memory_type": "preference",
    "category": "communication",
    "confidence_score": 0.8,
    "context": "User asked for detailed explanation of tool functionality"
  }}
]
```

Analyze the interaction and create high-quality memories:"""

        return prompt

    def _create_enhanced_memory_creation_prompt(
        self,
        user_input: str,
        agent_response: str,
        state_data: AgentState,
        tool_result: str = None,
        conversation_context: str = None,
    ) -> str:
        """
        Create an enhanced prompt for LLM memory creation with state data integration.

        This method incorporates state management data for richer context analysis
        and better memory quality.
        """

        # Get available tags and organize them by category
        available_tags = LTM_TAGS
        tag_categories = self._categorize_tags_for_prompt(available_tags)

        # Analyze the interaction for context clues
        interaction_analysis = self._analyze_interaction_context(
            user_input, agent_response, tool_result
        )

        # Get suggested tags based on content analysis
        suggested_tags = self._get_suggested_tags_from_content(
            user_input, agent_response
        )

        # Determine potential memory types based on content
        potential_memory_types = self._identify_potential_memory_types(
            user_input, agent_response, tool_result
        )

        # Analyze state data for additional context
        state_analysis = self._analyze_state_data_for_context(state_data)

        # Get context-aware tag suggestions
        context_aware_tags = self._get_context_aware_tag_suggestions(
            user_input, agent_response, state_data
        )

        prompt = f"""You are an advanced AI memory creation system for a personal AI assistant with access to comprehensive user state data. Your job is to intelligently analyze user interactions and create high-quality, actionable memories that will help the AI better understand and serve the user.

**CURRENT INTERACTION:**
User Input: {user_input}
Agent Response: {agent_response}
{f"Tool Result: {tool_result}" if tool_result else ""}
{f"Conversation Context: {conversation_context}" if conversation_context else ""}

**USER STATE ANALYSIS:**
{state_analysis}

**INTERACTION ANALYSIS:**
{interaction_analysis}

**AVAILABLE TAGS (EXACT LIST - USE ONLY THESE):**
{', '.join(LTM_TAGS)}

**AVAILABLE TAGS (by category):**
{tag_categories}

**SUGGESTED TAGS:**
{suggested_tags}

**CONTEXT-AWARE TAG SUGGESTIONS:**
{context_aware_tags}

**POTENTIAL MEMORY TYPES:**
{potential_memory_types}

**MEMORY CREATION GUIDELINES:**
1. Create 3-5 high-quality memories that capture different aspects of the interaction
2. Consider the user's current state, conversation history, and focus areas
3. Focus on user preferences, patterns, insights, and learning moments
4. Use appropriate tags from the available list
5. Ensure memories are specific, actionable, and relevant to the user's current context
6. Avoid creating redundant or overly general memories
7. Consider how this memory relates to existing user patterns and preferences
8. Use state data to enhance memory relevance and accuracy

**OUTPUT FORMAT:**
Return a JSON array of memory objects with these fields:
- content: Clear, concise description of what to remember
- tags: Array of relevant tags from the available list
- importance_score: 1-10 score (higher = more important)
- memory_type: One of: preference, pattern, insight, learning, tool_usage, general
- category: One of: work, personal, health, finance, education, general
- confidence_score: 0.0-1.0 confidence in accuracy
- context: Additional context or explanation
- state_relevance: How this memory relates to current user state
- cross_reference: Any connections to existing patterns or preferences

**EXAMPLE OUTPUT:**
```json
[
  {{
    "content": "User prefers detailed explanations for technical topics",
    "tags": ["preference", "communication", "technical"],
    "importance_score": 7,
    "memory_type": "preference",
    "category": "communication",
    "confidence_score": 0.8,
    "context": "User asked for detailed explanation of tool functionality",
    "state_relevance": "Consistent with user's focus on learning and understanding",
    "cross_reference": "Reinforces existing pattern of seeking detailed explanations"
  }}
]
```

Analyze the interaction with state context and create high-quality memories:"""

        return prompt

    def _analyze_state_data_for_context(self, state_data: AgentState) -> str:
        """Analyze state data to provide context for memory creation"""

        try:
            analysis_parts = []

            # Analyze conversation history
            if state_data.conversation_history:
                history_length = len(state_data.conversation_history)
                analysis_parts.append(
                    f"Conversation History: {history_length} exchanges"
                )

                # Analyze recent conversation patterns
                # Last 3 exchanges
                recent_exchanges = state_data.conversation_history[-3:]
                if recent_exchanges:
                    topics = []
                    for exchange in recent_exchanges:
                        user_input = exchange.get("user_input", "")
                        if user_input:
                            # Extract potential topics (simplified)
                            if any(
                                word in user_input.lower()
                                for word in ["work", "project", "meeting"]
                            ):
                                topics.append("work")
                            elif any(
                                word in user_input.lower()
                                for word in ["health", "exercise", "diet"]
                            ):
                                topics.append("health")
                            elif any(
                                word in user_input.lower()
                                for word in ["family", "personal", "home"]
                            ):
                                topics.append("personal")

                    if topics:
                        analysis_parts.append(
                            f"Recent Topics: {', '.join(set(topics))}"
                        )

            # Analyze focus areas
            if state_data.focus:
                analysis_parts.append(
                    f"Current Focus Areas: {', '.join(state_data.focus)}"
                )

            # Analyze tool usage
            if hasattr(state_data, "last_tool_result") and state_data.last_tool_result:
                analysis_parts.append("Recent Tool Usage: Yes")

            # Analyze step count (conversation complexity)
            if state_data.step_count > 1:
                analysis_parts.append(
                    f"Conversation Complexity: {state_data.step_count} steps"
                )

            if not analysis_parts:
                return "Limited state data available for analysis"

            return "\n".join(analysis_parts)

        except Exception as e:
            logger.error(f"Error analyzing state data: {e}")
            return "Error analyzing state data"

    def _get_context_aware_tag_suggestions(
        self, user_input: str, agent_response: str, state_data: AgentState
    ) -> str:
        """Get context-aware tag suggestions based on state data"""

        try:
            suggestions = []

            # Analyze focus areas for tag suggestions
            if state_data.focus:
                for focus in state_data.focus:
                    if focus.lower() in ["work", "job", "career"]:
                        suggestions.extend(["work", "professional", "career"])
                    elif focus.lower() in ["health", "wellness", "fitness"]:
                        suggestions.extend(["health", "wellness", "fitness"])
                    elif focus.lower() in ["family", "personal", "home"]:
                        suggestions.extend(["personal", "family", "home"])
                    elif focus.lower() in ["finance", "money", "budget"]:
                        suggestions.extend(["finance", "money", "budget"])

            # Analyze conversation history for patterns
            if state_data.conversation_history:
                # Look for communication style patterns
                formal_count = 0
                casual_count = 0

                # Last 5 exchanges
                for exchange in state_data.conversation_history[-5:]:
                    user_input = exchange.get("user_input", "").lower()
                    if any(
                        word in user_input
                        for word in ["please", "thank you", "would you mind"]
                    ):
                        formal_count += 1
                    elif any(word in user_input for word in ["hey", "cool", "awesome"]):
                        casual_count += 1

                if formal_count > casual_count:
                    suggestions.append("formal_communication")
                elif casual_count > formal_count:
                    suggestions.append("casual_communication")

            # Analyze tool usage patterns
            if hasattr(state_data, "last_tool_result") and state_data.last_tool_result:
                suggestions.append("tool_usage")

                # Add specific tool-related tags
                tool_result = str(state_data.last_tool_result).lower()
                if "success" in tool_result or "created" in tool_result:
                    suggestions.append("successful_automation")
                elif "error" in tool_result or "failed" in tool_result:
                    suggestions.append("learning_from_failure")

            if not suggestions:
                return "No specific context-aware tag suggestions"

            return f"Context-Aware Tags: {', '.join(set(suggestions))}"

        except Exception as e:
            logger.error(f"Error getting context-aware tag suggestions: {e}")
            return "Error generating context-aware tag suggestions"

    async def _validate_memory_quality(
        self, memory_spec: Dict[str, Any], state_data: AgentState
    ) -> float:
        """
        Validate memory quality and return a quality score.

        Args:
            memory_spec: Memory specification from LLM
            state_data: Current agent state for context validation

        Returns:
            Quality score between 0.0 and 1.0
        """

        try:
            quality_score = 0.0

            # Content quality (30%)
            content_score = self._score_content_quality(memory_spec.get("content", ""))
            quality_score += content_score * 0.3

            # Tag relevance (25%)
            tag_score = self._score_tag_relevance(memory_spec.get("tags", []))
            quality_score += tag_score * 0.25

            # State relevance (25%)
            state_score = self._score_state_relevance(memory_spec, state_data)
            quality_score += state_score * 0.25

            # Memory type appropriateness (20%)
            type_score = self._score_memory_type_appropriateness(memory_spec)
            quality_score += type_score * 0.2

            logger.info(
                f"Memory quality score: {quality_score:.2f} for content: {memory_spec.get('content', '')[:50]}..."
            )

            return quality_score

        except Exception as e:
            logger.error(f"Error validating memory quality: {e}")
            return 0.0

    def _score_content_quality(self, content: str) -> float:
        """Score content quality based on clarity and specificity"""

        if not content or len(content.strip()) < 10:
            return 0.0

        score = 0.5  # Base score

        # Length bonus (not too short, not too long)
        if 20 <= len(content) <= 100:
            score += 0.2
        elif 100 < len(content) <= 200:
            score += 0.1

        # Specificity bonus
        if any(
            word in content.lower()
            for word in ["prefers", "likes", "always", "usually", "tends to"]
        ):
            score += 0.2

        # Actionability bonus
        if any(
            word in content.lower()
            for word in ["should", "will", "can", "help", "improve"]
        ):
            score += 0.1

        return min(1.0, score)

    def _score_tag_relevance(self, tags: List[str]) -> float:
        """Score tag relevance and appropriateness"""

        if not tags:
            return 0.0

        score = 0.5  # Base score

        # Tag count bonus (not too few, not too many)
        if 2 <= len(tags) <= 5:
            score += 0.2
        elif len(tags) == 1:
            score += 0.1

        # Tag quality bonus
        valid_tags = [tag for tag in tags if tag in LTM_TAGS]
        if valid_tags:
            score += 0.2

        # Tag diversity bonus
        if len(set(tags)) == len(tags):  # No duplicates
            score += 0.1

        return min(1.0, score)

    def _score_state_relevance(
        self, memory_spec: Dict[str, Any], state_data: AgentState
    ) -> float:
        """Score how well the memory relates to current user state"""

        try:
            score = 0.5  # Base score

            # Focus area relevance
            if state_data.focus and memory_spec.get("category"):
                category = memory_spec["category"].lower()
                focus_lower = [f.lower() for f in state_data.focus]

                if any(focus in category or category in focus for focus in focus_lower):
                    score += 0.3

            # Conversation history relevance
            if state_data.conversation_history and memory_spec.get("content"):
                content_lower = memory_spec["content"].lower()
                recent_topics = []

                for exchange in state_data.conversation_history[-3:]:
                    user_input = exchange.get("user_input", "").lower()
                    if any(
                        word in user_input
                        for word in ["work", "health", "family", "finance"]
                    ):
                        recent_topics.append(user_input)

                if any(topic in content_lower for topic in recent_topics):
                    score += 0.2

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error scoring state relevance: {e}")
            return 0.5

    def _score_memory_type_appropriateness(self, memory_spec: Dict[str, Any]) -> float:
        """Score if the memory type is appropriate for the content"""

        try:
            memory_type = memory_spec.get("memory_type", "").lower()
            content = memory_spec.get("content", "").lower()

            score = 0.5  # Base score

            # Type-content alignment
            if memory_type == "preference":
                if any(
                    word in content for word in ["prefers", "likes", "wants", "needs"]
                ):
                    score += 0.3
            elif memory_type == "pattern":
                if any(
                    word in content
                    for word in ["always", "usually", "tends to", "typically"]
                ):
                    score += 0.3
            elif memory_type == "learning":
                if any(
                    word in content
                    for word in ["learned", "discovered", "figured out", "understood"]
                ):
                    score += 0.3
            elif memory_type == "tool_usage":
                if any(
                    word in content
                    for word in ["tool", "used", "executed", "automated"]
                ):
                    score += 0.3

            # Confidence alignment
            confidence = memory_spec.get("confidence_score", 0.5)
            if confidence >= 0.7 and score >= 0.7:
                score += 0.2

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error scoring memory type appropriateness: {e}")
            return 0.5

    def _get_quality_threshold(self) -> float:
        """Get the quality threshold for memory acceptance"""

        if isinstance(self.config, EnhancedLTMConfig):
            return self.config.min_memory_quality_score
        else:
            return 0.5  # Default threshold

    async def _create_enhanced_memory_from_spec(
        self, user_id: int, spec: Dict[str, Any], state_data: AgentState
    ) -> Optional[dict]:
        """
        Create an enhanced memory from specification with state data integration.

        This method creates memories with additional state context and
        enhanced metadata for better retrieval and relevance.
        """

        try:
            # Extract basic fields
            content = spec.get("content", "")
            tags = spec.get("tags", [])
            importance_score = spec.get("importance_score", 5)
            memory_type = spec.get("memory_type", "general")
            category = spec.get("category", "general")
            confidence_score = spec.get("confidence_score", 0.7)

            # Create enhanced context
            enhanced_context = {
                "memory_type": memory_type,
                "category": category,
                "confidence_score": confidence_score,
                "source_type": "llm_enhanced",
                "quality_score": spec.get("quality_score", 0.7),
                "state_relevance": spec.get("state_relevance", ""),
                "cross_reference": spec.get("cross_reference", ""),
                "metadata": {
                    "llm_generated": True,
                    "state_integrated": True,
                    "quality_validated": True,
                    "creation_timestamp": datetime.now().isoformat(),
                },
            }

            # Create memory
            memory = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context=f"LLM-generated memory with state integration. {spec.get('context', '')}",
                enhanced_context=enhanced_context,
                memory_type=memory_type,
                category=category,
                confidence_score=confidence_score,
                source_type="llm_enhanced",
                created_by="llm_memory_creator_enhanced",
            )

            return memory

        except Exception as e:
            logger.error(f"Failed to create enhanced memory: {e}")
            return None

    def _parse_llm_response(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract memory specifications"""

        try:
            logger.info(f"Parsing LLM response: {llm_response[:500]}...")

            # Try to extract JSON from the response
            # Look for JSON array in the response
            start_idx = llm_response.find("[")
            end_idx = llm_response.rfind("]")

            if start_idx != -1 and end_idx != -1:
                json_str = llm_response[start_idx : end_idx + 1]
                logger.info(f"Extracted JSON string: {json_str}")

                memory_specs = json.loads(json_str)
                logger.info(
                    f"Successfully parsed JSON, got {len(memory_specs)} memory specs"
                )

                # Validate the structure
                validated_specs = []
                for i, spec in enumerate(memory_specs):
                    logger.info(f"Validating spec {i}: {spec}")
                    if self._validate_memory_spec(spec):
                        validated_specs.append(spec)
                        logger.info(f"Spec {i} is valid")
                    else:
                        logger.warning(f"Spec {i} is invalid: {spec}")

                logger.info(
                    f"Validation complete: {len(validated_specs)} valid specs out of {len(memory_specs)}"
                )
                return validated_specs
            else:
                logger.warning("No JSON array found in LLM response")
                logger.warning(f"Response content: {llm_response}")
                return []

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"LLM response: {llm_response}")
            return []
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return []

    def _parse_enhanced_llm_response(self, llm_response: str) -> List[Dict[str, Any]]:
        """
        Parse enhanced LLM response with additional fields for state integration.

        This method handles the enhanced output format that includes
        state relevance and cross-reference information.
        """

        try:
            # Extract JSON from response
            json_start = llm_response.find("[")
            json_end = llm_response.rfind("]") + 1

            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in LLM response")
                return []

            json_str = llm_response[json_start:json_end]
            memory_specs = json.loads(json_str)

            # Validate and enhance specifications
            enhanced_specs = []
            for spec in memory_specs:
                if self._validate_memory_spec(spec):
                    # Add default values for missing fields
                    enhanced_spec = {
                        "content": spec.get("content", ""),
                        "tags": spec.get("tags", []),
                        "importance_score": spec.get("importance_score", 5),
                        "memory_type": spec.get("memory_type", "general"),
                        "category": spec.get("category", "general"),
                        "confidence_score": spec.get("confidence_score", 0.7),
                        "context": spec.get("context", ""),
                        "state_relevance": spec.get("state_relevance", ""),
                        "cross_reference": spec.get("cross_reference", ""),
                    }
                    enhanced_specs.append(enhanced_spec)

            return enhanced_specs

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing enhanced LLM response: {e}")
            return []

    def _validate_memory_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate memory specification has required fields"""

        required_fields = ["content", "tags"]
        for field in required_fields:
            if field not in spec or not spec[field]:
                return False

        # Validate content length
        if len(spec["content"].strip()) < 10:
            return False

        # Validate tags
        if not isinstance(spec["tags"], list) or len(spec["tags"]) == 0:
            return False

        return True

    def _categorize_tags_for_prompt(self, tags: List[str]) -> str:
        """Organize tags by category for better prompt structure"""

        categories = {
            "Communication & Information": [
                "email",
                "meeting",
                "conversation",
                "document",
                "note",
            ],
            "Actions & Operations": [
                "create",
                "delete",
                "update",
                "search",
                "schedule",
                "remind",
            ],
            "Importance & Priority": [
                "important",
                "urgent",
                "critical",
                "low_priority",
            ],
            "Context & Categories": [
                "work",
                "personal",
                "health",
                "finance",
                "travel",
                "shopping",
                "entertainment",
                "education",
            ],
            "User Behavior": [
                "preference",
                "habit",
                "pattern",
                "routine",
                "dislike",
                "favorite",
            ],
            "Tool & System": [
                "tool_execution",
                "user_request",
                "system_response",
                "error",
                "success",
            ],
            "Time & Frequency": ["daily", "weekly", "monthly", "one_time", "recurring"],
            "Health & Wellness": ["exercise", "diet", "medication", "wellness"],
            "Social": ["friend", "family", "event", "birthday"],
            "Learning": ["course", "lesson", "reading", "research"],
        }

        result = []
        for category, category_tags in categories.items():
            available_in_category = [tag for tag in category_tags if tag in tags]
            if available_in_category:
                result.append(f"**{category}:** {', '.join(available_in_category)}")

        return "\n".join(result)

    def _analyze_interaction_context(
        self, user_input: str, agent_response: str, tool_result: str = None
    ) -> str:
        """Analyze the interaction for context clues"""

        analysis_parts = []

        # Analyze user input patterns
        user_lower = user_input.lower()

        # Communication style analysis
        if any(
            word in user_lower for word in ["please", "thank you", "would you mind"]
        ):
            analysis_parts.append("• User shows formal communication style")
        elif any(word in user_lower for word in ["hey", "cool", "awesome"]):
            analysis_parts.append("• User shows casual communication style")

        # Information needs analysis
        if any(
            word in user_lower for word in ["explain", "how does", "what do you mean"]
        ):
            analysis_parts.append("• User seeks detailed explanations")
        elif any(word in user_lower for word in ["just", "simple", "quick"]):
            analysis_parts.append("• User prefers concise information")

        # Tool usage analysis
        if tool_result:
            if "Error" in str(tool_result):
                analysis_parts.append(
                    "• Tool usage encountered an error - learning opportunity"
                )
            elif "success" in str(tool_result).lower():
                analysis_parts.append("• Tool usage was successful")

        # Topic analysis
        topics = []
        if any(word in user_lower for word in ["work", "project", "meeting"]):
            topics.append("work")
        if any(word in user_lower for word in ["health", "exercise", "diet"]):
            topics.append("health")
        if any(word in user_lower for word in ["family", "personal", "home"]):
            topics.append("personal")
        if any(word in user_lower for word in ["money", "budget", "finance"]):
            topics.append("finance")

        if topics:
            analysis_parts.append(f"• Topics discussed: {', '.join(topics)}")

        if not analysis_parts:
            analysis_parts.append("• General conversation - look for subtle patterns")

        return "\n".join(analysis_parts)

    def _get_suggested_tags_from_content(
        self, user_input: str, agent_response: str
    ) -> List[str]:
        """Get suggested tags based on content analysis using enhanced tag suggester"""

        combined_content = f"{user_input} {agent_response}"

        # Use the enhanced tag suggester
        suggested_tags, confidence = self.tag_suggester.suggest_tags_for_content(
            content=combined_content,
            memory_type=None,  # We don't know the memory type yet
            category=None,  # We don't know the category yet
            existing_tags=None,
            user_context=None,
        )

        logger.info(
            f"Enhanced tag suggester suggested {len(suggested_tags)} tags with confidence {confidence:.2f}"
        )

        return suggested_tags

    def _identify_potential_memory_types(
        self, user_input: str, agent_response: str, tool_result: str = None
    ) -> str:
        """Identify potential memory types based on interaction content"""

        potential_types = []
        combined_text = f"{user_input} {agent_response}".lower()

        # Preference detection
        if any(
            word in combined_text
            for word in ["prefer", "like", "want", "need", "favorite"]
        ):
            potential_types.append(
                "• **Preference**: User expressing likes/dislikes or needs"
            )

        # Pattern detection
        if any(
            word in combined_text
            for word in ["always", "usually", "typically", "habit", "routine"]
        ):
            potential_types.append(
                "• **Pattern**: User describing recurring behaviors or routines"
            )

        # Interest detection
        if any(
            word in combined_text
            for word in ["interested in", "curious about", "want to learn"]
        ):
            potential_types.append(
                "• **Interest**: User showing curiosity or interest in topics"
            )

        # Communication style detection
        if any(
            word in combined_text
            for word in ["explain", "tell me more", "detailed", "simple", "quick"]
        ):
            potential_types.append(
                "• **Communication**: User showing communication preferences"
            )

        # Learning pattern detection
        if any(
            word in combined_text
            for word in ["learn", "understand", "figure out", "now I know"]
        ):
            potential_types.append(
                "• **Learning**: User showing learning patterns or moments"
            )

        # Tool usage detection
        if tool_result:
            potential_types.append(
                "• **Tool Usage**: Interaction involved tool execution"
            )

        if not potential_types:
            potential_types.append(
                "• **General**: Look for subtle insights in the conversation"
            )

        return "\n".join(potential_types)

    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM"""

        try:
            # Handle different LLM interfaces
            if hasattr(self.llm, "acall"):
                response = await self.llm.acall(prompt)
            elif hasattr(self.llm, "agenerate"):
                response = await self.llm.agenerate(prompt)
            elif hasattr(self.llm, "aask"):
                response = await self.llm.aask(prompt)
            elif hasattr(self.llm, "complete"):
                # Handle GeminiLLM.complete method
                response = self.llm.complete(prompt, functions={})
                logger.info(f"GeminiLLM.complete response type: {type(response)}")
                logger.info(f"GeminiLLM.complete response: {response}")

                # Extract content from response
                if isinstance(response, dict) and "content" in response:
                    response = response["content"]
                    logger.info(f"Extracted content from dict: {response}")
                elif hasattr(response, "candidates") and response.candidates:
                    # Handle Gemini response object
                    candidate = response.candidates[0]
                    if hasattr(candidate, "content") and candidate.content:
                        content_parts = candidate.content.parts
                        text_parts = [
                            part.text for part in content_parts if hasattr(part, "text")
                        ]
                        response = "\n".join(text_parts)
                        logger.info(
                            f"Extracted content from Gemini response: {response[:200]}..."
                        )
                    else:
                        response = str(candidate.content)
                        logger.info(
                            f"Used string representation of candidate content: {response[:200]}..."
                        )
                else:
                    response = str(response)
                    logger.info(
                        f"Used string representation of response: {response[:200]}..."
                    )
            elif hasattr(self.llm, "generate"):
                # Handle sync generate method
                response = self.llm.generate(prompt)
            elif hasattr(self.llm, "ask"):
                # Handle sync ask method
                response = self.llm.ask(prompt)
            elif hasattr(self.llm, "call"):
                # Handle sync call method
                response = self.llm.call(prompt)
            else:
                # Last resort: try to get response from the LLM object
                logger.warning(
                    f"Unknown LLM interface for {type(self.llm)}, attempting to get response"
                )
                if hasattr(self.llm, "response"):
                    response = self.llm.response
                else:
                    raise AttributeError(
                        f"LLM object {type(self.llm)} has no known response method"
                    )

            return str(response)

        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            raise

    def _extract_tool_name_from_result(self, tool_result: str) -> Optional[str]:
        """Extract tool name from tool result"""

        # Common patterns in tool results
        tool_patterns = [
            r"Tool (\w+) result:",
            r"(\w+)_tool result:",
            r"(\w+) tool result:",
            r"(\w+) result:",
        ]

        import re

        for pattern in tool_patterns:
            match = re.search(pattern, tool_result, re.IGNORECASE)
            if match:
                return match.group(1).lower()

        return None

    async def _create_memory_from_spec(
        self, user_id: int, memory_spec: dict
    ) -> Optional[dict]:
        """
        Create a memory from a memory specification.

        Args:
            user_id: User ID for the memory
            memory_spec: Memory specification from LLM

        Returns:
            Created memory dict or None if creation failed
        """
        try:
            # Extract memory data from specification
            content = memory_spec.get("content", "")
            tags = memory_spec.get("tags", [])
            importance_score = memory_spec.get("importance_score", 5)
            memory_type = memory_spec.get("memory_type", "general")
            category = memory_spec.get("category", "personal")
            confidence_score = memory_spec.get("confidence_score", 0.8)
            context = memory_spec.get("context", "")

            # Validate and clean tags using the AI tag validator
            if tags:
                # Convert tags list to comma-separated string for validation
                tags_string = ",".join(tags) if isinstance(tags, list) else str(tags)
                (
                    valid_tags,
                    invalid_tags,
                    correction_explanation,
                ) = validate_ai_generated_tags(tags_string, content, context)
                tags = valid_tags

                if invalid_tags:
                    logger.warning(f"Invalid tags in memory spec: {invalid_tags}")
                    logger.info(f"Correction: {correction_explanation}")
            else:
                # If no tags provided, get suggestions based on content
                tags = validate_ai_generated_tags("", content, context)[0]

            # Create memory data
            memory_data = {
                "user_id": user_id,
                "content": content,
                "tags": tags,
                # Clamp between 1-10
                "importance_score": min(max(importance_score, 1), 10),
                "memory_type": memory_type,
                "category": category,
                # Clamp between 0-1
                "confidence_score": min(max(confidence_score, 0.0), 1.0),
                "context": context,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
            }

            # Add memory to storage with correct parameter order
            memory_result = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context=context,
                memory_type=memory_type,
                category=category,
                confidence_score=confidence_score,
                created_by="llm_memory_creator",
            )

            if memory_result and memory_result.get("id"):
                memory_id = memory_result["id"]
                logger.info(
                    f"Successfully created memory {memory_id} for user {user_id}"
                )
                memory_data["id"] = memory_id
                return memory_data
            else:
                logger.warning(f"Failed to create memory for user {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error creating memory from spec: {e}")
            return None
