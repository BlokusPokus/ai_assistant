"""
ContextService handles all context retrieval (LTM + RAG) for the agent.
"""

from typing import Optional, Dict, Any
from personal_assistant.config.logging_config import get_logger
from personal_assistant.memory.ltm_optimization import (
    DynamicContextManager,
    SmartLTMRetriever,
)
from personal_assistant.rag.retriever import query_knowledge_base
from personal_assistant.tools.ltm.ltm_manager import get_ltm_context_with_tags
from personal_assistant.types.state import AgentState

logger = get_logger("context_service")


class ContextService:
    """Service for retrieving and optimizing context from LTM and RAG systems."""
    
    def __init__(self, ltm_retriever: Optional[SmartLTMRetriever] = None,
                 context_manager: Optional[DynamicContextManager] = None):
        """
        Initialize the context service.
        
        Args:
            ltm_retriever: Enhanced LTM retriever (optional)
            context_manager: Dynamic context manager (optional)
        """
        self.ltm_retriever = ltm_retriever
        self.context_manager = context_manager
        
    async def get_enhanced_context(self, user_id: int, user_input: str, 
                                 agent_state: AgentState) -> Dict[str, Any]:
        """
        Get enhanced context from both LTM and RAG systems.
        
        Args:
            user_id: User identifier
            user_input: User's input message
            agent_state: Current agent state
            
        Returns:
            Dict containing ltm_context and rag_context
        """
        # Get LTM context
        ltm_context = await self._get_ltm_context(user_id, user_input, agent_state)
        
        # Get RAG context
        rag_context = await self._get_rag_context(user_id, user_input)
        
        return {
            "ltm_context": ltm_context,
            "rag_context": rag_context
        }
    
    async def _get_ltm_context(self, user_id: int, user_input: str, 
                             agent_state: AgentState) -> Optional[str]:
        """Get LTM context with enhanced fallback logic."""
        try:
            # Try enhanced LTM retriever first
            if self.ltm_retriever:
                relevant_memories = await self.ltm_retriever.get_relevant_memories(
                    user_id=user_id,
                    context=user_input,
                    state_context=agent_state,
                    query_complexity="medium",
                )
                
                if relevant_memories and self.context_manager:
                    # Use dynamic context manager for optimization
                    ltm_context = await self.context_manager.optimize_context_with_state(
                        memories=relevant_memories,
                        user_input=user_input,
                        state_context=agent_state,
                        focus_areas=agent_state.focus if hasattr(agent_state, "focus") else None,
                        query_complexity="medium",
                    )
                else:
                    # Simple context formatting
                    ltm_context = "\n".join(
                        [mem.get("content", "") for mem in relevant_memories[:5]]
                    )
                
                logger.debug(f"Enhanced LTM context retrieved: {len(ltm_context)} chars")
                return ltm_context
                
        except Exception as e:
            logger.warning(f"Enhanced LTM context retrieval failed: {e}")
        
        # Fallback to legacy LTM method
        try:
            ltm_context = await get_ltm_context_with_tags(
                None,
                logger,
                user_id,
                user_input,
                list(agent_state.focus) if hasattr(agent_state, "focus") and agent_state.focus else None,
            )
            logger.debug(f"Legacy LTM context retrieved: {len(ltm_context) if ltm_context else 0} chars")
            return ltm_context
            
        except Exception as e:
            logger.warning(f"Legacy LTM context retrieval also failed: {e}")
            return None
    
    async def _get_rag_context(self, user_id: int, user_input: str) -> list:
        """Get RAG context from knowledge base."""
        try:
            rag_context = await query_knowledge_base(user_id, user_input)
            logger.debug(f"RAG context retrieved: {len(rag_context)} items")
            return rag_context
        except Exception as e:
            logger.warning(f"RAG context retrieval failed: {e}")
            return []
