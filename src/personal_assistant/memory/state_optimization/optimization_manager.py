"""
State optimization manager for intelligent memory management.

This module provides the main orchestrator for state optimization that:
- Coordinates all optimization components
- Manages the optimization pipeline
- Creates intelligent summaries
- Applies final size limits
"""

import copy
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ...types.state import AgentState, StateConfig

from .context_manager import ContextManager
from .conversation_compressor import ConversationCompressor
from .error_analyzer import ErrorPatternAnalyzer

logger = logging.getLogger(__name__)


class StateOptimizationManager:
    """Manages state optimization before saving to database"""

    def __init__(self, config: "StateConfig"):
        """
        Initialize the state optimization manager.

        Args:
            config: State configuration object
        """
        self.config = config
        self.compressor = ConversationCompressor()
        self.context_manager = ContextManager(
            max_context_items=config.max_memory_context_size
        )
        self.error_analyzer = ErrorPatternAnalyzer()

        logger.info("StateOptimizationManager initialized with configuration")

    async def optimize_state_for_saving(self, state: "AgentState") -> "AgentState":
        """
        Optimize state before saving to database.

        Args:
            state: Original agent state to optimize

        Returns:
            Optimized agent state
        """
        logger.info(
            f"Starting state optimization for conversation with {len(state.conversation_history)} history items"
        )

        # Create a copy to avoid modifying the original
        optimized_state = copy.deepcopy(state)

        # Track optimization statistics
        optimization_stats = {
            "original_conversation_length": len(state.conversation_history),
            "original_memory_context_length": len(state.memory_context),
            "optimization_steps": [],
        }

        # Step 1: Compress conversation history
        logger.info("Step 1: Compressing conversation history")
        original_history = optimized_state.conversation_history.copy()
        optimized_state.conversation_history = (
            self.compressor.compress_conversation_history(state.conversation_history)
        )

        compression_stats = self.compressor.get_compression_stats(
            original_history, optimized_state.conversation_history
        )
        optimization_stats["compression_stats"] = compression_stats
        optimization_stats["optimization_steps"].append("conversation_compression")

        logger.info(
            f"Conversation history compressed: {compression_stats['reduction_percentage']:.1f}% reduction"
        )

        # Step 2: Optimize memory context
        logger.info("Step 2: Optimizing memory context")
        original_context = optimized_state.memory_context.copy()
        optimized_state.memory_context = self.context_manager.optimize_memory_context(
            optimized_state, state.user_input
        )

        context_stats = self.context_manager.get_context_stats(
            original_context, optimized_state.memory_context
        )
        optimization_stats["context_stats"] = context_stats
        optimization_stats["optimization_steps"].append("memory_context_optimization")

        logger.info(
            f"Memory context optimized: {len(optimized_state.memory_context)} items"
        )

        # Step 3: Analyze and learn from errors
        logger.info("Step 3: Analyzing error patterns")
        error_analysis = self.error_analyzer.analyze_error_patterns(
            optimized_state.conversation_history
        )
        optimization_stats["error_analysis"] = error_analysis
        optimization_stats["optimization_steps"].append("error_pattern_analysis")

        if error_analysis["total_errors"] > 0:
            logger.info(
                f"Error analysis complete: {error_analysis['total_errors']} errors found"
            )
            error_summary = self.error_analyzer.get_error_summary(error_analysis)
            logger.info(f"Error summary: {error_summary}")

        # Step 4: Create intelligent summaries for old content
        if (
            len(optimized_state.conversation_history)
            > self.config.max_conversation_history_size * 0.8
        ):
            logger.info("Step 4: Creating intelligent summaries for old content")
            optimized_state = self._create_intelligent_summaries(optimized_state)
            optimization_stats["optimization_steps"].append("intelligent_summarization")

        # Step 5: Apply final size limits
        logger.info("Step 5: Applying final size limits")
        optimized_state._apply_size_limits()
        optimization_stats["optimization_steps"].append("size_limit_enforcement")

        # Calculate final optimization statistics
        final_stats = self._calculate_final_optimization_stats(
            state, optimized_state, optimization_stats
        )

        logger.info(
            f"State optimization complete: {final_stats['overall_reduction_percentage']:.1f}% total reduction"
        )
        logger.info(
            f"Final state size: {len(optimized_state.conversation_history)} conversation items, {len(optimized_state.memory_context)} context items"
        )

        # Store optimization metadata in the state
        optimized_state.memory_context.append(
            {
                "role": "system",
                "content": f"State optimization applied: {final_stats['overall_reduction_percentage']:.1f}% reduction",
                "source": "state_optimization",
                "optimization_stats": final_stats,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return optimized_state

    def _create_intelligent_summaries(self, state: "AgentState") -> "AgentState":
        """
        Create intelligent summaries for old conversation content.

        Args:
            state: Agent state to optimize

        Returns:
            State with intelligent summaries
        """
        # Keep recent items
        recent_items = state.conversation_history[-self.config.context_window_size :]

        # Create summary of older items
        older_items = state.conversation_history[: -self.config.context_window_size]

        if older_items:
            summary = self._generate_intelligent_summary(older_items)
            state.conversation_history = [summary] + recent_items

            logger.info(
                f"Created intelligent summary: {len(older_items)} items summarized into 1 summary item"
            )

        return state

    def _generate_intelligent_summary(self, items: List[dict]) -> dict:
        """
        Generate intelligent summary of conversation items.

        Args:
            items: List of conversation items to summarize

        Returns:
            Summary item
        """
        # Group by tool usage
        tool_groups = self._group_by_tool_usage(items)

        # Create summary content
        summary_parts = []

        for tool_name, tool_items in tool_groups.items():
            success_count = len(
                [
                    item
                    for item in tool_items
                    if "Error" not in str(item.get("content", ""))
                ]
            )
            total_count = len(tool_items)

            if success_count > 0:
                summary_parts.append(
                    f"Successfully used {tool_name} {success_count} times"
                )
            else:
                summary_parts.append(
                    f"Attempted {tool_name} {total_count} times (failed)"
                )

        # Add user interaction summary
        user_messages = [item for item in items if item.get("role") == "user"]
        if user_messages:
            summary_parts.append(f"User made {len(user_messages)} requests")

        # Add assistant response summary
        assistant_messages = [item for item in items if item.get("role") == "assistant"]
        if assistant_messages:
            summary_parts.append(
                f"Assistant provided {len(assistant_messages)} responses"
            )

        summary_content = ". ".join(summary_parts)

        return {
            "role": "system",
            "content": f"Conversation Summary: {summary_content}",
            "type": "intelligent_summary",
            "original_length": len(items),
            # 1 summary replaces many items
            "compression_ratio": len(items) / 1,
            "timestamp": datetime.now().isoformat(),
            "summary_metadata": {
                "tool_groups": {
                    name: len(items) for name, items in tool_groups.items()
                },
                "user_message_count": len(user_messages),
                "assistant_message_count": len(assistant_messages),
            },
        }

    def _group_by_tool_usage(self, items: List[dict]) -> Dict[str, List[dict]]:
        """
        Group conversation items by tool usage.

        Args:
            items: List of conversation items

        Returns:
            Dictionary of items grouped by tool
        """
        tool_groups = {}

        for item in items:
            if item.get("role") == "tool":
                tool_name = item.get("name", "unknown")
                if tool_name not in tool_groups:
                    tool_groups[tool_name] = []
                tool_groups[tool_name].append(item)

        return tool_groups

    def _calculate_final_optimization_stats(
        self,
        original_state: "AgentState",
        optimized_state: "AgentState",
        optimization_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate final optimization statistics.

        Args:
            original_state: Original agent state
            optimized_state: Optimized agent state
            optimization_stats: Intermediate optimization statistics

        Returns:
            Final optimization statistics
        """
        # Calculate overall reduction
        original_total = len(original_state.conversation_history) + len(
            original_state.memory_context
        )
        optimized_total = len(optimized_state.conversation_history) + len(
            optimized_state.memory_context
        )

        if original_total == 0:
            overall_reduction_percentage = 0.0
        else:
            overall_reduction_percentage = (
                (original_total - optimized_total) / original_total
            ) * 100

        # Calculate memory usage reduction
        original_memory_size = self._estimate_memory_size(original_state)
        optimized_memory_size = self._estimate_memory_size(optimized_state)

        if original_memory_size == 0:
            memory_reduction_percentage = 0.0
        else:
            memory_reduction_percentage = (
                (original_memory_size - optimized_memory_size) / original_memory_size
            ) * 100

        final_stats = {
            **optimization_stats,
            "final_conversation_length": len(optimized_state.conversation_history),
            "final_memory_context_length": len(optimized_state.memory_context),
            "overall_reduction_percentage": overall_reduction_percentage,
            "memory_reduction_percentage": memory_reduction_percentage,
            "optimization_timestamp": datetime.now().isoformat(),
        }

        return final_stats

    def _estimate_memory_size(self, state: "AgentState") -> int:
        """
        Estimate memory size of state object.

        Args:
            state: Agent state object

        Returns:
            Estimated memory size in bytes
        """
        # Simple estimation based on content length
        total_size = 0

        # Estimate conversation history size
        for item in state.conversation_history:
            content = str(item.get("content", ""))
            total_size += len(content.encode("utf-8"))

        # Estimate memory context size
        for item in state.memory_context:
            content = str(item.get("content", ""))
            total_size += len(content.encode("utf-8"))

        return total_size

    def get_optimization_report(
        self, original_state: "AgentState", optimized_state: "AgentState"
    ) -> str:
        """
        Generate a human-readable optimization report.

        Args:
            original_state: Original agent state
            optimized_state: Optimized agent state

        Returns:
            Formatted optimization report
        """
        # Calculate basic metrics
        conv_reduction = len(original_state.conversation_history) - len(
            optimized_state.conversation_history
        )
        context_reduction = len(original_state.memory_context) - len(
            optimized_state.memory_context
        )

        report_parts = [
            "=== State Optimization Report ===",
            f"Conversation History: {len(original_state.conversation_history)} → {len(optimized_state.conversation_history)} items ({conv_reduction:+d})",
            f"Memory Context: {len(original_state.memory_context)} → {len(optimized_state.memory_context)} items ({context_reduction:+d})",
            "",
            "Optimization Steps Applied:",
        ]

        # Get optimization metadata from memory context
        optimization_metadata = None
        for item in optimized_state.memory_context:
            if item.get("source") == "state_optimization":
                optimization_metadata = item.get("optimization_stats", {})
                break

        if optimization_metadata:
            steps = optimization_metadata.get("optimization_steps", [])
            for step in steps:
                report_parts.append(f"  ✓ {step.replace('_', ' ').title()}")

            # Add detailed statistics
            if "compression_stats" in optimization_metadata:
                comp_stats = optimization_metadata["compression_stats"]
                report_parts.append(f"\nCompression Results:")
                report_parts.append(
                    f"  Reduction: {comp_stats.get('reduction_percentage', 0):.1f}%"
                )
                report_parts.append(
                    f"  Ratio: {comp_stats.get('compression_ratio', 1.0):.2f}x"
                )

            if "error_analysis" in optimization_metadata:
                error_stats = optimization_metadata["error_analysis"]
                total_errors = error_stats.get("total_errors", 0)
                if total_errors > 0:
                    report_parts.append(f"\nError Analysis:")
                    report_parts.append(f"  Total Errors: {total_errors}")
                    report_parts.append(
                        f"  Tools with Errors: {len(error_stats.get('tools_with_errors', {}))}"
                    )
        else:
            report_parts.append("  No optimization metadata found")

        report_parts.append(
            f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return "\n".join(report_parts)
