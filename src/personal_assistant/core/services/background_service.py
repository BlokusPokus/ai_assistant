"""
BackgroundService handles all background processing after response is returned.
"""

import time
from typing import Optional
from personal_assistant.config.logging_config import get_logger
from personal_assistant.memory.ltm_optimization import (
    LTMLearningManager,
    EnhancedMemoryLifecycleManager,
)
from personal_assistant.memory.storage_integration import StorageIntegrationManager
from personal_assistant.types.state import AgentState
from ..logging_utils import log_performance_metrics

logger = get_logger("background_service")


class BackgroundService:
    """Service for handling background processing tasks."""
    
    def __init__(self, storage_manager: StorageIntegrationManager,
                 ltm_learning_manager: Optional[LTMLearningManager] = None,
                 lifecycle_manager: Optional[EnhancedMemoryLifecycleManager] = None):
        """
        Initialize the background service.
        
        Args:
            storage_manager: Storage integration manager
            ltm_learning_manager: LTM learning manager (optional)
            lifecycle_manager: Memory lifecycle manager (optional)
        """
        self.storage_manager = storage_manager
        self.ltm_learning_manager = ltm_learning_manager
        self.lifecycle_manager = lifecycle_manager
    
    async def process_async(self, user_id: int, user_input: str, response: str,
                          updated_state: AgentState, conversation_id: str, start_time: float):
        """
        Process all background tasks asynchronously.
        
        Args:
            user_id: User identifier
            user_input: Original user input
            response: Agent response
            updated_state: Updated agent state
            conversation_id: Conversation identifier
            start_time: Request start time
        """
        try:
            # Save state
            await self._save_state(conversation_id, updated_state, user_id)
            
            # LTM learning and optimization
            await self._process_ltm_learning(user_id, user_input, response, updated_state, conversation_id)
            
            # Memory lifecycle management
            await self._process_memory_lifecycle(user_id, updated_state)
            
            # Log interaction
            await self._log_interaction(user_id, updated_state, response)
            
            # Log performance metrics
            self._log_performance_metrics(user_id, response, start_time)
            
        except Exception as e:
            logger.error(f"Background processing failed for user {user_id}: {e}")
    
    async def _save_state(self, conversation_id: str, updated_state: AgentState, user_id: int):
        """Save agent state to storage."""
        try:
            await self.storage_manager.save_state(conversation_id, updated_state, user_id)
            logger.debug(f"State saved for conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to save state for user {user_id}: {e}")
    
    async def _process_ltm_learning(self, user_id: int, user_input: str, response: str,
                                  updated_state: AgentState, conversation_id: str):
        """Process LTM learning and optimization."""
        if not self.ltm_learning_manager:
            return
            
        try:
            # Perform comprehensive LTM optimization
            await self.ltm_learning_manager.optimize_after_interaction(
                user_id, user_input, response, updated_state
            )
            
            # Handle explicit memory requests if any
            if self.ltm_learning_manager.is_memory_request(user_input):
                await self.ltm_learning_manager.handle_explicit_memory_request(
                    user_id,
                    user_input,
                    response,
                    f"Conversation {conversation_id}",
                )
            
            logger.debug(f"LTM learning completed for user {user_id}")
        except Exception as e:
            logger.warning(f"LTM optimization failed for user {user_id}: {e}")
    
    async def _process_memory_lifecycle(self, user_id: int, updated_state: AgentState):
        """Process memory lifecycle management."""
        if not self.lifecycle_manager:
            return
            
        try:
            lifecycle_results = await self.lifecycle_manager.manage_memory_lifecycle_with_state(
                user_id, updated_state
            )
            logger.info(f"Memory lifecycle management completed for user {user_id}: {lifecycle_results}")
        except Exception as e:
            logger.warning(f"Memory lifecycle management failed for user {user_id}: {e}")
    
    async def _log_interaction(self, user_id: int, updated_state: AgentState, response: str):
        """Log agent interaction."""
        try:
            await self.storage_manager.log_agent_interaction(
                user_id=user_id,
                user_input=updated_state.user_input,
                agent_response=response,
                tool_called=None,
                tool_output=str(updated_state.last_tool_result) if updated_state.last_tool_result else None,
                memory_used=None,
            )
            logger.debug(f"Interaction logged for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to log agent interaction for user {user_id}: {e}")
    
    def _log_performance_metrics(self, user_id: int, response: str, start_time: float):
        """Log performance metrics."""
        try:
            duration = time.time() - start_time
            log_performance_metrics(
                logger,
                user_id,
                "agent_run_complete",
                duration,
                True,
                {"response_length": len(response) if response else 0},
            )
            logger.debug(f"Performance metrics logged for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to log performance metrics for user {user_id}: {e}")
