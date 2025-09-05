"""
Agent runner logic for managing the conversation workflow.

📁 agent_core/graph_runner.py
Implements the main agent loop that manages the conversation flow between
user input, planner decisions, and tool executions. Handles state transitions
and enforces loop limits.
"""

import json
from typing import Any, Dict, List, Optional, Union

from ..config.logging_config import get_logger
from ..config.settings import settings
from ..llm.planner import LLMPlanner
from ..memory import apply_context_limits
from ..memory.context_quality_validator import ContextQualityValidator
from ..memory.ltm_optimization import DynamicContextManager, EnhancedLTMConfig
from ..rag.document_processor import DocumentProcessor
from ..tools.base import ToolRegistry
from ..types.messages import FinalAnswer, ToolCall
from ..types.state import AgentState
from ..utils.metrics import MetricsLogger

# Configure module
# logger
logger = get_logger("core")


class AgentRunner:

    """
    Agent runner logic for managing the conversation workflow.

    This class handles the internal agent loop execution, distinct from AgentCore.run()
    which orchestrates the overall conversation flow. This class focuses specifically
    on running the agent loop, executing tools, and managing the conversation state
    during a single user interaction.

    Key Methods:
    - set_context(): Inject LTM and RAG context into agent state
    - execute_agent_loop(): Run the main agent loop for tool execution and planning
    """

    def __init__(self, tools: "ToolRegistry", planner: "LLMPlanner"):
        """
        Initialize the agent runner.

        Input:
            tools: Registry containing all available tools
            planner: LLM-based planner for decision making

        Output:
            None

        Description:
            Sets up the runner with tools and planner, configures max steps from LOOP_LIMIT
        """
        # self.memory = memory
        self.tools = tools

        self.planner = planner
        self.max_steps = settings.LOOP_LIMIT
        self.current_state: Optional[AgentState] = None  # Store the current state
        self.context_injection_limit = 1000  # Maximum characters for context injection

        # Initialize context quality validator (will be configured when set_context is called)
        self.quality_validator: Optional[ContextQualityValidator] = None

        # Initialize enhanced context manager
        try:
            self.ltm_config = EnhancedLTMConfig()
            self.dynamic_context_manager: Optional[
                DynamicContextManager
            ] = DynamicContextManager(config=self.ltm_config)
            logger.info("Enhanced dynamic context manager initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize dynamic context manager: {e}")
            self.dynamic_context_manager = None

        logger.info(
            "AgentRunner initialized with tools, planner, context quality validation, and dynamic context management."
        )

    async def set_context(
        self,
        agent_state: AgentState | None,
        rag_context: Optional[List[dict]] | Any = None,
        ltm_context: Optional[str] | Any = None,
    ) -> None:
        """
        Inject LTM and RAG context into AgentState's memory_context with limits.

        This method safely injects both Long-Term Memory (LTM) and RAG (Retrieval-Augmented Generation)
        context into the agent's memory context, with proper validation and error handling.

        Args:
            agent_state (AgentState): The active state object
            rag_context (Optional[List[dict]]): List of semantic documents from RAG
            ltm_context (Optional[str]): Long-term memory context string

        Raises:
            ValueError: If agent_state is None or invalid
            TypeError: If rag_context is not a list when provided
        """
        # Input validation
        if agent_state is None:
            logger.error("set_context called with None agent_state")
            raise ValueError("agent_state cannot be None")

        if not hasattr(agent_state, "memory_context"):
            logger.error(
                "set_context called with invalid agent_state - missing memory_context attribute"
            )
            raise ValueError("agent_state must have memory_context attribute")

        if rag_context is not None and not isinstance(rag_context, list):
            logger.error(
                f"set_context called with invalid rag_context type: {type(rag_context)}"
            )
            raise TypeError(
                f"rag_context must be a list or None, got: {type(rag_context)}"
            )

        if ltm_context is not None and not isinstance(ltm_context, str):
            logger.error(
                f"set_context called with invalid ltm_context type: {type(ltm_context)}"
            )
            raise TypeError(
                f"ltm_context must be a string or None, got: {type(ltm_context)}"
            )

        try:
            # Store the current state for use in run()
            self.current_state = agent_state
            memory_blocks: List[Dict[str, Union[str, Dict[str, str]]]] = []

            # Add LTM context if provided
            if ltm_context and ltm_context.strip():
                logger.debug("Adding LTM context to memory blocks")

                # Use dynamic context manager for enhanced LTM context processing if available
                if self.dynamic_context_manager:
                    try:
                        # Parse LTM context into memory objects for dynamic processing
                        ltm_memories = self._parse_ltm_context_to_memories(ltm_context)

                        # Optimize LTM context with state coordination
                        optimized_ltm_context = await self.dynamic_context_manager.optimize_context_with_state(
                            memories=ltm_memories,
                            user_input=agent_state.user_input,
                            state_context=agent_state,
                            focus_areas=agent_state.focus
                            if hasattr(agent_state, "focus")
                            else None,
                            query_complexity="medium",
                        )

                        if optimized_ltm_context:
                            memory_blocks.append(
                                {
                                    "role": "memory",
                                    "source": "ltm_enhanced",
                                    "content": optimized_ltm_context,
                                    "type": "long_term_memory_optimized",
                                }
                            )
                            logger.debug(
                                "Enhanced LTM context added with dynamic optimization"
                            )
                        else:
                            # Fallback to original context
                            memory_blocks.append(
                                {
                                    "role": "memory",
                                    "source": "ltm",
                                    "content": ltm_context.strip(),
                                    "type": "long_term_memory",
                                }
                            )
                    except Exception as e:
                        logger.warning(
                            f"Dynamic LTM context optimization failed: {e}, using original context"
                        )
                        memory_blocks.append(
                            {
                                "role": "memory",
                                "source": "ltm",
                                "content": ltm_context.strip(),
                                "type": "long_term_memory",
                            }
                        )
                else:
                    # Fallback to original LTM context processing
                    memory_blocks.append(
                        {
                            "role": "memory",
                            "source": "ltm",
                            "content": ltm_context.strip(),
                            "type": "long_term_memory",
                        }
                    )
            elif ltm_context is not None:
                logger.debug("LTM context provided but empty, skipping")

            # Add RAG context with validation and limits
            if rag_context:
                logger.debug(f"Processing {len(rag_context)} RAG documents")
                valid_rag_blocks = 0
                for i, doc in enumerate(rag_context):
                    if not isinstance(doc, dict):
                        logger.warning(
                            f"Skipping invalid RAG document at index {i}: {type(doc)}"
                        )
                        continue

                    # Extract content with fallback for different document structures
                    content = DocumentProcessor.extract_content(doc)
                    if content:
                        memory_blocks.append(
                            {
                                "role": "memory",
                                "source": "rag",
                                "content": content,
                                "type": "document",
                                "metadata": {
                                    k: json.dumps(v)
                                    if isinstance(v, (dict, list))
                                    else str(v)
                                    for k, v in doc.items()
                                    if k != "content" and k != "document"
                                },
                            }
                        )
                        valid_rag_blocks += 1
                    else:
                        logger.warning(
                            f"Skipping RAG document at index {i} - no valid content found"
                        )

                logger.debug(
                    f"Successfully processed {valid_rag_blocks} out of {len(rag_context)} RAG documents"
                )
            elif rag_context is not None:
                logger.debug("RAG context provided but empty, skipping")

            # Initialize quality validator if not already done
            if self.quality_validator is None:
                self.quality_validator = ContextQualityValidator(agent_state.config)
                logger.debug("Context quality validator initialized")

            # Apply quality validation to memory blocks
            if memory_blocks and self.quality_validator:
                original_count = len(memory_blocks)

                # Validate context quality before injection
                validated_blocks = self.quality_validator.validate_context_relevance(
                    memory_blocks, agent_state.user_input, context_type="mixed"
                )

                removed_count = original_count - len(validated_blocks)
                if removed_count > 0:
                    logger.info(
                        f"🔍 Quality validation removed {removed_count} low-quality context blocks"
                    )

                # Get quality metrics for logging
                if self.quality_validator:
                    quality_metrics = self.quality_validator.get_quality_metrics(
                        validated_blocks, agent_state.user_input
                    )
                else:
                    quality_metrics = {}

                # Safely access quality distribution with fallback
                quality_dist = quality_metrics.get("quality_distribution", {})
                excellent_count = quality_dist.get("excellent", 0)
                good_count = quality_dist.get("good", 0)
                high_quality_count = excellent_count + good_count

                logger.info(
                    f"🔍 Context quality metrics: {quality_metrics['average_quality']:.2f} average, "
                    f"{high_quality_count} high-quality items"
                )

                # Apply context limits to validated blocks
                apply_context_limits(validated_blocks, self.context_injection_limit)

                # Add validated blocks to memory context
                agent_state.memory_context.extend(validated_blocks)
                logger.debug(
                    f"Successfully added {len(validated_blocks)} validated context blocks to memory"
                )
            else:
                logger.debug("No valid context blocks to add")

            # Apply size limits after adding context
            agent_state._apply_size_limits()

            # Validate context injection and log metrics
            MetricsLogger.log_context_metrics(memory_blocks, agent_state)

            logger.info(
                f"Context set successfully: {len([b for b in memory_blocks if b['source'] == 'ltm'])} LTM blocks, "
                f"{len([b for b in memory_blocks if b['source'] == 'rag'])} RAG blocks. "
                f"Total memory_context size: {len(agent_state.memory_context)}"
            )

        except Exception as e:
            logger.error(f"Error setting context: {e}")
            # Don't raise the exception - allow the agent to continue without context
            # but log the error for debugging
            logger.warning("Continuing without context injection due to error")

    async def execute_agent_loop(self, user_input: str):
        """
        Execute the main agent loop processing user input with optimized context.

        This method runs the core agent loop that processes user input through the planner,
        executes tools, and manages the conversation flow until completion.

        Input:
            user_input: String containing the user's message or query

        Output:
            Tuple[str, AgentState]: Final response to user and the final AgentState

        Description:
            1. Uses the provided state with user input
            2. Enters main loop (limited by LOOP_LIMIT):
                - Gets next action from planner
                - If FinalAnswer, returns it
                - If ToolCall, executes tool and updates state
            3. If loop limit reached, forces finish
        """
        # Use the state that was set up by AgentCore (which includes conversation history)
        state = self.current_state
        if state is None:
            raise ValueError("No current state available. Call set_context() first.")

        logger.debug(f"Starting run with input: {user_input}")

        # Add the current user input to conversation history if not already there
        if (
            not state.conversation_history
            or state.conversation_history[-1].get("content") != user_input
        ):
            state.conversation_history.append({"role": "user", "content": user_input})

        # Apply size limits after adding new input
        state._apply_size_limits()

        while state.step_count < self.max_steps:
            logger.debug(f"Step {state.step_count}")

            # Get action from planner
            logger.debug("=== CALLING PLANNER.CHOOSE_ACTION ===")
            action = self.planner.choose_action(state)
            logger.debug(f"=== PLANNER RETURNED ACTION: {type(action).__name__} ===")
            logger.debug(f"Chosen action: {action}")

            if isinstance(action, FinalAnswer):
                logger.debug("Got final answer")
                state.conversation_history.append(
                    {"role": "assistant", "content": action.output}
                )

                # Apply size limits after adding response
                state._apply_size_limits()

                return action.output, state

            if isinstance(action, ToolCall):
                try:
                    logger.debug(f"=== EXECUTING TOOL: {action.name} ===")
                    logger.debug(f"Tool args: {action.args}")

                    # Execute tool
                    result = await self.tools.run_tool(action.name, **action.args)
                    logger.debug("=== TOOL EXECUTION COMPLETED ===")
                    logger.debug(f"Tool result: {result}")

                    # Update state (this already adds the tool result to conversation history)
                    logger.debug("=== UPDATING STATE WITH TOOL RESULT ===")
                    state.add_tool_result(action, result)
                    state.conversation_history.append(
                        {"role": "assistant", "content": result}
                    )

                    logger.debug(f"Updated state: {state}")
                except Exception as e:
                    logger.error(f"Tool execution error: {str(e)}")
                    return f"Error executing tool {action.name}: {str(e)}", state

        logger.warning("Loop limit reached, forcing finish.")
        forced_response = self.planner.force_finish(state)

        # Apply size limits before returning
        state._apply_size_limits()

        return forced_response, state

    def _parse_ltm_context_to_memories(self, ltm_context: str) -> List[dict]:
        """
        Parse LTM context string into memory objects for dynamic processing.

        Args:
            ltm_context: String containing LTM context

        Returns:
            List of memory dictionaries
        """
        memories = []

        try:
            # Split context by sections (assuming double newlines separate memories)
            sections = ltm_context.split("\n\n")

            for i, section in enumerate(sections):
                if section.strip():
                    # Create a basic memory object from the section
                    memory = {
                        "id": f"ltm_context_{i}",
                        "content": section.strip(),
                        "tags": [],  # Could be enhanced to extract tags
                        "importance_score": 5,  # Default importance
                        "memory_type": "general",
                        "created_at": "2024-01-01T00:00:00Z",  # Default timestamp
                        "last_accessed": "2024-01-01T00:00:00Z",
                    }
                    memories.append(memory)

            logger.debug(f"Parsed {len(memories)} memories from LTM context")
            return memories

        except Exception as e:
            logger.warning(f"Failed to parse LTM context: {e}")
            # Return a single memory object with the entire context
            return [
                {
                    "id": "ltm_context_fallback",
                    "content": ltm_context,
                    "tags": [],
                    "importance_score": 5,
                    "memory_type": "general",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_accessed": "2024-01-01T00:00:00Z",
                }
            ]
