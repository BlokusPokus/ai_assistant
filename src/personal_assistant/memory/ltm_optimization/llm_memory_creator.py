"""
LLM-based Memory Creator

This module uses LLM intelligence to decide what memories to create from user interactions.
"""

import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import add_ltm_memory
from ...constants.tags import LTM_TAGS, validate_tags
from .config import LTMConfig
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
        conversation_context: str = None
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

            logger.info(
                f"LLM created {len(created_memories)} memory specifications")
            return created_memories

        except Exception as e:
            logger.error(f"Error in LLM memory creation: {e}")
            return []

    def _create_memory_creation_prompt(
        self,
        user_input: str,
        agent_response: str,
        tool_result: str = None,
        conversation_context: str = None
    ) -> str:
        """Create an enhanced prompt for LLM memory creation"""

        # Get available tags and organize them by category
        available_tags = LTM_TAGS
        tag_categories = self._categorize_tags_for_prompt(available_tags)

        # Analyze the interaction for context clues
        interaction_analysis = self._analyze_interaction_context(
            user_input, agent_response, tool_result)

        # Get suggested tags based on content analysis
        suggested_tags = self._get_suggested_tags_from_content(
            user_input, agent_response)

        # Determine potential memory types based on content
        potential_memory_types = self._identify_potential_memory_types(
            user_input, agent_response, tool_result)

        prompt = f"""You are an advanced AI memory creation system for a personal AI assistant. Your job is to intelligently analyze user interactions and create high-quality, actionable memories that will help the AI better understand and serve the user.

**INTERACTION ANALYSIS:**
{interaction_analysis}

**CURRENT INTERACTION:**
- User Input: "{user_input}"
- Agent Response: "{agent_response}"
- Tool Result: {tool_result if tool_result else "None"}
- Conversation Context: {conversation_context if conversation_context else "None"}

**SUGGESTED MEMORY TYPES:**
{potential_memory_types}

**SUGGESTED TAGS (based on content analysis):**
{', '.join(suggested_tags) if suggested_tags else "None - use your judgment"}

**AVAILABLE TAGS (organized by category):**
{tag_categories}

**MEMORY CREATION GUIDELINES:**

1. **Memory Types to Create:**
   - **User Preferences**: Communication style, response format, tool usage patterns
   - **Behavioral Patterns**: Routines, habits, decision-making patterns
   - **Topic Interests**: Areas of focus, recurring subjects, expertise domains
   - **Communication Style**: How the user prefers to interact and receive information
   - **Learning Patterns**: How the user processes and retains information
   - **Tool Usage**: Patterns in how the user works with different tools

2. **Quality Standards:**
   - Each memory should be **specific and actionable**
   - Content should be **clear and descriptive**
   - Tags should be **relevant and precise**
   - Importance scores should reflect **real value for future interactions**

3. **Importance Scoring (1-10):**
   - **9-10**: Critical preferences, strong patterns, important habits
   - **7-8**: Clear preferences, useful patterns, moderate importance
   - **5-6**: General insights, mild preferences, learning moments
   - **3-4**: Minor observations, weak patterns
   - **1-2**: Very minor details (avoid unless highly specific)

4. **Memory Count:**
   - Create 2-4 memories per interaction
   - Focus on quality over quantity
   - Each memory should capture a distinct insight

**OUTPUT FORMAT:**
Return a JSON array of memory objects. Each memory should have:
{{
    "type": "preference|pattern|interest|communication|learning|tool_usage",
    "content": "Clear, specific description of what to remember about the user",
    "importance_score": 1-10 (justify the score in context field),
    "tags": ["tag1", "tag2", "tag3"] (use tags from available list),
    "context": "Why this memory is valuable and how to use it",
    "confidence": 0.0-1.0 (how confident you are in this observation),
    "category": "work|personal|health|finance|education|entertainment|general"
}}

**EXAMPLE MEMORIES:**
[
    {{
        "type": "preference",
        "content": "User prefers detailed, step-by-step explanations when learning new concepts, as evidenced by asking 'can you explain how this works' and 'tell me more about the process'",
        "importance_score": 8,
        "tags": ["preference", "education", "conversation"],
        "context": "This helps provide appropriately detailed responses in future learning scenarios",
        "confidence": 0.9,
        "category": "education"
    }},
    {{
        "type": "pattern",
        "content": "User frequently asks about project deadlines and scheduling, indicating a focus on time management and project planning",
        "importance_score": 7,
        "tags": ["project", "deadline", "schedule", "work"],
        "context": "This suggests prioritizing time-sensitive and project-related information in responses",
        "confidence": 0.8,
        "category": "work"
    }}
]

Analyze the interaction and create 2-4 high-quality memories. Focus on insights that will genuinely improve future interactions with this user."""

        return prompt

    def _categorize_tags_for_prompt(self, tags: List[str]) -> str:
        """Organize tags by category for better prompt structure"""

        categories = {
            "Communication & Information": ["email", "meeting", "conversation", "document", "note"],
            "Actions & Operations": ["create", "delete", "update", "search", "schedule", "remind"],
            "Importance & Priority": ["important", "urgent", "critical", "low_priority"],
            "Context & Categories": ["work", "personal", "health", "finance", "travel", "shopping", "entertainment", "education"],
            "User Behavior": ["preference", "habit", "pattern", "routine", "dislike", "favorite"],
            "Tool & System": ["tool_execution", "user_request", "system_response", "error", "success"],
            "Time & Frequency": ["daily", "weekly", "monthly", "one_time", "recurring"],
            "Health & Wellness": ["exercise", "diet", "medication", "wellness"],
            "Social": ["friend", "family", "event", "birthday"],
            "Learning": ["course", "lesson", "reading", "research"]
        }

        result = []
        for category, category_tags in categories.items():
            available_in_category = [
                tag for tag in category_tags if tag in tags]
            if available_in_category:
                result.append(
                    f"**{category}:** {', '.join(available_in_category)}")

        return "\n".join(result)

    def _analyze_interaction_context(self, user_input: str, agent_response: str, tool_result: str = None) -> str:
        """Analyze the interaction for context clues"""

        analysis_parts = []

        # Analyze user input patterns
        user_lower = user_input.lower()

        # Communication style analysis
        if any(word in user_lower for word in ["please", "thank you", "would you mind"]):
            analysis_parts.append("• User shows formal communication style")
        elif any(word in user_lower for word in ["hey", "cool", "awesome"]):
            analysis_parts.append("• User shows casual communication style")

        # Information needs analysis
        if any(word in user_lower for word in ["explain", "how does", "what do you mean"]):
            analysis_parts.append("• User seeks detailed explanations")
        elif any(word in user_lower for word in ["just", "simple", "quick"]):
            analysis_parts.append("• User prefers concise information")

        # Tool usage analysis
        if tool_result:
            if "Error" in str(tool_result):
                analysis_parts.append(
                    "• Tool usage encountered an error - learning opportunity")
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
            analysis_parts.append(
                "• General conversation - look for subtle patterns")

        return "\n".join(analysis_parts)

    def _get_suggested_tags_from_content(self, user_input: str, agent_response: str) -> List[str]:
        """Get suggested tags based on content analysis using enhanced tag suggester"""

        combined_content = f"{user_input} {agent_response}"

        # Use the enhanced tag suggester
        suggested_tags, confidence = self.tag_suggester.suggest_tags_for_content(
            content=combined_content,
            memory_type=None,  # We don't know the memory type yet
            category=None,      # We don't know the category yet
            existing_tags=None,
            user_context=None
        )

        logger.info(
            f"Enhanced tag suggester suggested {len(suggested_tags)} tags with confidence {confidence:.2f}")

        return suggested_tags

    def _identify_potential_memory_types(self, user_input: str, agent_response: str, tool_result: str = None) -> str:
        """Identify potential memory types based on interaction content"""

        potential_types = []
        combined_text = f"{user_input} {agent_response}".lower()

        # Preference detection
        if any(word in combined_text for word in ["prefer", "like", "want", "need", "favorite"]):
            potential_types.append(
                "• **Preference**: User expressing likes/dislikes or needs")

        # Pattern detection
        if any(word in combined_text for word in ["always", "usually", "typically", "habit", "routine"]):
            potential_types.append(
                "• **Pattern**: User describing recurring behaviors or routines")

        # Interest detection
        if any(word in combined_text for word in ["interested in", "curious about", "want to learn"]):
            potential_types.append(
                "• **Interest**: User showing curiosity or interest in topics")

        # Communication style detection
        if any(word in combined_text for word in ["explain", "tell me more", "detailed", "simple", "quick"]):
            potential_types.append(
                "• **Communication**: User showing communication preferences")

        # Learning pattern detection
        if any(word in combined_text for word in ["learn", "understand", "figure out", "now I know"]):
            potential_types.append(
                "• **Learning**: User showing learning patterns or moments")

        # Tool usage detection
        if tool_result:
            potential_types.append(
                "• **Tool Usage**: Interaction involved tool execution")

        if not potential_types:
            potential_types.append(
                "• **General**: Look for subtle insights in the conversation")

        return "\n".join(potential_types)

    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM"""

        try:
            # Handle different LLM interfaces
            if hasattr(self.llm, 'acall'):
                response = await self.llm.acall(prompt)
            elif hasattr(self.llm, 'agenerate'):
                response = await self.llm.agenerate(prompt)
            elif hasattr(self.llm, 'aask'):
                response = await self.llm.aask(prompt)
            elif hasattr(self.llm, 'complete'):
                # Handle GeminiLLM.complete method
                response = self.llm.complete(prompt, functions={})
                logger.info(
                    f"GeminiLLM.complete response type: {type(response)}")
                logger.info(f"GeminiLLM.complete response: {response}")

                # Extract content from response
                if isinstance(response, dict) and 'content' in response:
                    response = response['content']
                    logger.info(f"Extracted content from dict: {response}")
                elif hasattr(response, 'candidates') and response.candidates:
                    # Handle Gemini response object
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        content_parts = candidate.content.parts
                        text_parts = [
                            part.text for part in content_parts if hasattr(part, 'text')]
                        response = '\n'.join(text_parts)
                        logger.info(
                            f"Extracted content from Gemini response: {response[:200]}...")
                    else:
                        response = str(candidate.content)
                        logger.info(
                            f"Used string representation of candidate content: {response[:200]}...")
                else:
                    response = str(response)
                    logger.info(
                        f"Used string representation of response: {response[:200]}...")
            elif hasattr(self.llm, 'generate'):
                # Handle sync generate method
                response = self.llm.generate(prompt)
            elif hasattr(self.llm, 'ask'):
                # Handle sync ask method
                response = self.llm.ask(prompt)
            elif hasattr(self.llm, 'call'):
                # Handle sync call method
                response = self.llm.call(prompt)
            else:
                # Last resort: try to get response from the LLM object
                logger.warning(
                    f"Unknown LLM interface for {type(self.llm)}, attempting to get response")
                if hasattr(self.llm, 'response'):
                    response = self.llm.response
                else:
                    raise AttributeError(
                        f"LLM object {type(self.llm)} has no known response method")

            return str(response)

        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            raise

    def _parse_llm_response(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract memory specifications"""

        try:
            logger.info(f"Parsing LLM response: {llm_response[:500]}...")

            # Try to extract JSON from the response
            # Look for JSON array in the response
            start_idx = llm_response.find('[')
            end_idx = llm_response.rfind(']')

            if start_idx != -1 and end_idx != -1:
                json_str = llm_response[start_idx:end_idx + 1]
                logger.info(f"Extracted JSON string: {json_str}")

                memory_specs = json.loads(json_str)
                logger.info(
                    f"Successfully parsed JSON, got {len(memory_specs)} memory specs")

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
                    f"Validation complete: {len(validated_specs)} valid specs out of {len(memory_specs)}")
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

    def _validate_memory_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate a memory specification"""

        required_fields = ["type", "content", "importance_score", "tags"]

        # Check required fields
        for field in required_fields:
            if field not in spec:
                return False

        # Validate importance score
        if not isinstance(spec["importance_score"], int) or not 1 <= spec["importance_score"] <= 10:
            return False

        # Validate tags
        if not isinstance(spec["tags"], list) or len(spec["tags"]) == 0:
            return False

        # Validate content
        if not isinstance(spec["content"], str) or len(spec["content"].strip()) == 0:
            return False

        return True

    async def _create_memory_from_spec(self, user_id: int, spec: Dict[str, Any]) -> Optional[dict]:
        """Create an actual memory from a specification with enhanced features"""

        try:
            logger.info(f"Creating enhanced memory from spec: {spec}")

            # Validate and normalize tags before creating memory
            raw_tags = spec.get("tags", [])
            if isinstance(raw_tags, str):
                # Handle case where tags might be comma-separated string
                raw_tags = [tag.strip() for tag in raw_tags.split(",")]

            logger.info(f"Raw tags: {raw_tags}")

            # Validate tags against allowed list
            valid_tags, invalid_tags = validate_tags(raw_tags)

            if invalid_tags:
                logger.warning(
                    f"LLM generated invalid tags: {invalid_tags}. Using valid tags: {valid_tags}")

            # If no valid tags, use suggested tags from content
            if not valid_tags:
                suggested_tags = self._get_suggested_tags_from_content(
                    spec.get("content", ""), "")
                valid_tags = suggested_tags if suggested_tags else [
                    "general", "miscellaneous"]
                logger.info(
                    f"No valid tags found, using content-suggested tags: {valid_tags}")

            logger.info(f"Final tags for memory creation: {valid_tags}")
            logger.info(f"Content: {spec.get('content', 'No content')}")
            logger.info(
                f"Importance score: {spec.get('importance_score', 'No score')}")
            logger.info(f"Context: {spec.get('context', 'No context')}")

            # Extract enhanced fields
            memory_type = spec.get("type", "insight")
            category = spec.get("category", "general")
            confidence_score = spec.get("confidence", 0.8)
            context = spec.get(
                "context", f"LLM-generated {memory_type} memory")

            # Apply dynamic importance scoring
            final_importance_score = self._calculate_dynamic_importance(
                spec.get("importance_score", 5),
                confidence_score,
                memory_type,
                category,
                valid_tags
            )

            # Create the memory using the storage system
            memory = await add_ltm_memory(
                user_id=user_id,
                content=spec["content"],
                tags=valid_tags,
                importance_score=final_importance_score,
                context=context,
                memory_type=memory_type,
                category=category,
                confidence_score=confidence_score,
                source_type="llm_generated",
                source_id=f"llm_memory_{memory_type}",
                created_by="llm_memory_creator",
                metadata={
                    "llm_generated": True,
                    "original_spec": spec,
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "dynamic_importance_adjustment": final_importance_score - spec.get("importance_score", 5),
                    "tag_suggestions_used": len(suggested_tags) if 'suggested_tags' in locals() else 0
                }
            )

            logger.info(
                f"Created enhanced LLM-generated memory: {memory_type} for user {user_id} with tags: {valid_tags}, importance: {final_importance_score}")
            return memory

        except Exception as e:
            logger.error(f"Error creating memory from spec: {e}")
            logger.error(f"Spec that caused error: {spec}")
            return None

    def _calculate_dynamic_importance(
        self,
        base_importance: int,
        confidence: float,
        memory_type: str,
        category: str,
        tags: List[str]
    ) -> int:
        """Calculate dynamic importance score based on multiple factors"""

        # Start with base importance
        dynamic_score = float(base_importance)

        # Confidence adjustment (higher confidence = higher importance)
        confidence_adjustment = (confidence - 0.5) * 2  # -1 to +1 range
        dynamic_score += confidence_adjustment

        # Memory type adjustment
        type_adjustments = {
            "preference": 1.0,      # User preferences are important
            "pattern": 0.8,          # Behavioral patterns are valuable
            "habit": 0.7,            # Habits show consistency
            "communication": 0.6,    # Communication style is useful
            "learning": 0.5,         # Learning patterns are helpful
            "tool_usage": 0.4,       # Tool usage patterns are moderate
            "interest": 0.3,         # Topic interests are lower priority
            "general": 0.0           # General insights get no boost
        }
        dynamic_score += type_adjustments.get(memory_type, 0.0)

        # Category adjustment
        category_adjustments = {
            "work": 0.5,             # Work-related memories are important
            "health": 0.4,           # Health-related memories are valuable
            "finance": 0.3,           # Finance-related memories are useful
            "personal": 0.2,          # Personal memories are moderate
            "education": 0.1,         # Education-related memories are helpful
            "general": 0.0            # General category gets no boost
        }
        dynamic_score += category_adjustments.get(category, 0.0)

        # Tag-based adjustment
        priority_tags = ["important", "urgent",
                         "critical", "preference", "habit"]
        tag_boost = sum(0.2 for tag in tags if tag in priority_tags)
        dynamic_score += tag_boost

        # Ensure score stays within 1-10 range
        dynamic_score = max(1, min(10, dynamic_score))

        # Round to nearest integer
        return round(dynamic_score)

    def _extract_tool_name_from_result(self, tool_result: str) -> Optional[str]:
        """Extract tool name from tool result"""

        # Common patterns in tool results
        tool_patterns = [
            r"Tool (\w+) result:",
            r"(\w+)_tool result:",
            r"(\w+) tool result:",
            r"(\w+) result:"
        ]

        import re
        for pattern in tool_patterns:
            match = re.search(pattern, tool_result, re.IGNORECASE)
            if match:
                return match.group(1).lower()

        return None
