"""
ContextInjectionService handles LTM and RAG context processing and injection.
"""

import json
from typing import Dict, List, Optional, Union

from personal_assistant.config.logging_config import get_logger
from personal_assistant.memory import apply_context_limits
from personal_assistant.memory.context_quality_validator import ContextQualityValidator
from personal_assistant.memory.ltm_optimization import DynamicContextManager, EnhancedLTMConfig
from personal_assistant.rag.document_processor import DocumentProcessor
from personal_assistant.types.state import AgentState
from personal_assistant.utils.metrics import MetricsLogger

logger = get_logger("context_injection_service")


class ContextInjectionService:
    """Service for processing and injecting LTM and RAG context into agent state."""
    
    def __init__(self, context_injection_limit: int = 1000):
        """
        Initialize the context injection service.
        
        Args:
            context_injection_limit: Maximum characters for context injection
        """
        self.context_injection_limit = context_injection_limit
        self.quality_validator: Optional[ContextQualityValidator] = None
        
        # Initialize enhanced context manager
        try:
            self.ltm_config = EnhancedLTMConfig()
            self.dynamic_context_manager: Optional[DynamicContextManager] = DynamicContextManager(
                config=self.ltm_config
            )
            logger.info("Enhanced dynamic context manager initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize dynamic context manager: {e}")
            self.dynamic_context_manager = None
    
    async def inject_context(
        self,
        agent_state: AgentState,
        rag_context: Optional[List[dict]] = None,
        ltm_context: Optional[str] = None,
    ) -> None:
        """
        Inject LTM and RAG context into AgentState's memory_context with limits.
        
        Args:
            agent_state: The active state object
            rag_context: List of semantic documents from RAG
            ltm_context: Long-term memory context string
        """

        try:
            memory_blocks: List[Dict[str, Union[str, Dict[str, str]]]] = []

            # Process LTM context
            await self._process_ltm_context(agent_state, ltm_context, memory_blocks)
            
            # Process RAG context
            await self._process_rag_context(rag_context, memory_blocks)
            
            # Apply quality validation and injection
            await self._apply_quality_validation_and_injection(agent_state, memory_blocks)
            
            # Apply size limits and log metrics
            agent_state._apply_size_limits()
            MetricsLogger.log_context_metrics(memory_blocks, agent_state)

            logger.info(
                f"Context injected successfully: {len([b for b in memory_blocks if b['source'] == 'ltm'])} LTM blocks, "
                f"{len([b for b in memory_blocks if b['source'] == 'rag'])} RAG blocks. "
                f"Total memory_context size: {len(agent_state.memory_context)}"
            )

        except Exception as e:
            logger.error(f"Error injecting context: {e}")
            logger.warning("Continuing without context injection due to error")
    
    async def _process_ltm_context(
        self, 
        agent_state: AgentState, 
        ltm_context: Optional[str], 
        memory_blocks: List[Dict[str, Union[str, Dict[str, str]]]]
    ):
        """Process LTM context with enhanced optimization."""
        if not ltm_context or not ltm_context.strip():
            logger.debug("LTM context provided but empty, skipping")
            return

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
                    focus_areas=agent_state.focus if hasattr(agent_state, "focus") else None,
                    query_complexity="medium",
                )

                if optimized_ltm_context:
                    memory_blocks.append({
                        "role": "memory",
                        "source": "ltm_enhanced",
                        "content": optimized_ltm_context,
                        "type": "long_term_memory_optimized",
                    })
                    logger.debug("Enhanced LTM context added with dynamic optimization")
                else:
                    # Fallback to original context
                    memory_blocks.append({
                        "role": "memory",
                        "source": "ltm",
                        "content": ltm_context.strip(),
                        "type": "long_term_memory",
                    })
            except Exception as e:
                logger.warning(f"Dynamic LTM context optimization failed: {e}, using original context")
                memory_blocks.append({
                    "role": "memory",
                    "source": "ltm",
                    "content": ltm_context.strip(),
                    "type": "long_term_memory",
                })
        else:
            # Fallback to original LTM context processing
            memory_blocks.append({
                "role": "memory",
                "source": "ltm",
                "content": ltm_context.strip(),
                "type": "long_term_memory",
            })
    
    async def _process_rag_context(
        self, 
        rag_context: Optional[List[dict]], 
        memory_blocks: List[Dict[str, Union[str, Dict[str, str]]]]
    ):
        """Process RAG context with validation and limits."""
        if not rag_context:
            logger.debug("RAG context provided but empty, skipping")
            return

        logger.debug(f"Processing {len(rag_context)} RAG documents")
        valid_rag_blocks = 0
        
        for i, doc in enumerate(rag_context):
            if not isinstance(doc, dict):
                logger.warning(f"Skipping invalid RAG document at index {i}: {type(doc)}")
                continue

            # Extract content with fallback for different document structures
            content = DocumentProcessor.extract_content(doc)
            if content:
                memory_blocks.append({
                    "role": "memory",
                    "source": "rag",
                    "content": content,
                    "type": "document",
                    "metadata": {
                        k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                        for k, v in doc.items()
                        if k != "content" and k != "document"
                    },
                })
                valid_rag_blocks += 1
            else:
                logger.warning(f"Skipping RAG document at index {i} - no valid content found")

        logger.debug(f"Successfully processed {valid_rag_blocks} out of {len(rag_context)} RAG documents")
    
    async def _apply_quality_validation_and_injection(
        self, 
        agent_state: AgentState, 
        memory_blocks: List[Dict[str, Union[str, Dict[str, str]]]]
    ):
        """Apply quality validation and inject validated blocks into agent state."""
        if not memory_blocks:
            logger.debug("No valid context blocks to add")
            return

        # Initialize quality validator if not already done
        if self.quality_validator is None:
            self.quality_validator = ContextQualityValidator(agent_state.config)
            logger.debug("Context quality validator initialized")

        # Apply quality validation to memory blocks
        if self.quality_validator:
            original_count = len(memory_blocks)

            # Validate context quality before injection
            validated_blocks = self.quality_validator.validate_context_relevance(
                memory_blocks, agent_state.user_input, context_type="mixed"
            )

            removed_count = original_count - len(validated_blocks)
            if removed_count > 0:
                logger.info(f"🔍 Quality validation removed {removed_count} low-quality context blocks")

            # Get quality metrics for logging
            quality_metrics = self.quality_validator.get_quality_metrics(
                validated_blocks, agent_state.user_input
            )

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
            logger.debug(f"Successfully added {len(validated_blocks)} validated context blocks to memory")
        else:
            # No quality validator, add all blocks
            agent_state.memory_context.extend(memory_blocks)
            logger.debug(f"Added {len(memory_blocks)} context blocks without quality validation")
    
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
            return [{
                "id": "ltm_context_fallback",
                "content": ltm_context,
                "tags": [],
                "importance_score": 5,
                "memory_type": "general",
                "created_at": "2024-01-01T00:00:00Z",
                "last_accessed": "2024-01-01T00:00:00Z",
            }]
