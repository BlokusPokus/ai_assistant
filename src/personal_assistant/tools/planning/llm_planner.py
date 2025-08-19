"""
LLM-powered task planning tool that creates intelligent step-by-step plans.
Uses LLM to analyze requests and generate contextual guidance.
Automatically includes relevant tool guidelines for better execution.
"""

import logging
from typing import Dict, List, Optional, Any

from ..base import Tool
from .llm_planner_internal import (
    load_tool_guidelines,
    identify_relevant_tools_fallback,
    build_tool_identification_prompt,
    parse_tool_identification_response,
    extract_relevant_guidelines,
    build_planning_prompt,
    get_style_instructions,
    create_fallback_plan,
    build_enhanced_planning_prompt,
    get_planning_summary,
    format_tool_info_for_prompt
)

logger = logging.getLogger(__name__)


class LLMPlannerTool:
    """Creates intelligent task plans using LLM analysis with tool guidelines."""

    def __init__(self, llm_client=None, guidelines_path: str = "src/personal_assistant/tools"):
        """
        Initialize the LLM planner tool.

        Args:
            llm_client: LLM client for generating plans (optional, can be set later)
            guidelines_path: Path to tool guidelines directory
        """
        self.llm_client = llm_client
        self.guidelines_path = guidelines_path
        self.guidelines_cache = {}

        self.planning_tool = Tool(
            name="create_intelligent_plan",
            func=self.create_intelligent_plan,
            description="Create an intelligent, step-by-step plan for completing a user request using LLM analysis. Provides tool recommendations, best practices, and contextual guidance.",
            parameters={
                "user_request": {
                    "type": "string",
                    "description": "The user's request or task to plan"
                },
                "available_tools": {
                    "type": "string",
                    "description": "Comma-separated list of available tools (optional)"
                },
                "user_context": {
                    "type": "string",
                    "description": "Additional context about the user's situation (optional)"
                },
                "planning_style": {
                    "type": "string",
                    "description": "Planning style: 'detailed', 'concise', or 'adhd_friendly' (default: 'adhd_friendly')"
                },
                "include_guidelines": {
                    "type": "boolean",
                    "description": "Whether to include relevant tool guidelines in the plan (default: True)"
                }
            }
        )

    def __iter__(self):
        """Makes the class iterable to return all tools."""
        return iter([self.planning_tool])

    def set_llm_client(self, llm_client):
        """Set the LLM client for plan generation."""
        self.llm_client = llm_client

    def _load_tool_guidelines(self) -> Dict[str, str]:
        """Load available tool guidelines from the guidelines directory."""
        if self.guidelines_cache:
            return self.guidelines_cache

        self.guidelines_cache = load_tool_guidelines(self.guidelines_path)
        return self.guidelines_cache

    async def _identify_relevant_tools_llm(self, user_request: str, available_tools: Optional[str] = None) -> List[str]:
        """Use LLM to intelligently identify which tools are relevant to the task."""
        if not self.llm_client:
            logger.warning("LLM client not set, using fallback tool detection")
            return identify_relevant_tools_fallback(user_request, available_tools)

        try:
            # Get available guidelines for context
            guidelines = self._load_tool_guidelines()
            available_guidelines = list(guidelines.keys())

            # Build prompt for tool identification
            tool_identification_prompt = build_tool_identification_prompt(
                user_request, available_tools, available_guidelines)

            # Get LLM response for tool identification
            response = await self._get_llm_response(tool_identification_prompt, max_tokens=500)

            # Parse the response to extract tool names
            relevant_tools = parse_tool_identification_response(response)

            logger.info(f"LLM identified relevant tools: {relevant_tools}")
            return relevant_tools

        except Exception as e:
            logger.error(
                f"LLM tool identification failed: {e}, using fallback")
            return identify_relevant_tools_fallback(user_request, available_tools)

    async def create_intelligent_plan(
        self,
        user_request: str,
        available_tools: Optional[str] = None,
        user_context: Optional[str] = None,
        planning_style: str = "adhd_friendly",
        include_guidelines: bool = True
    ) -> str:
        """
        Create an intelligent plan using LLM analysis with tool guidelines.

        Args:
            user_request: The user's request or task to plan
            available_tools: Comma-separated list of available tools
            user_context: Additional context about the user's situation
            planning_style: Style of planning to use
            include_guidelines: Whether to include relevant tool guidelines

        Returns:
            A comprehensive, step-by-step plan with tool guidance
        """

        # Use LLM to identify relevant tools for the task
        relevant_tools = await self._identify_relevant_tools_llm(user_request, available_tools)

        # Extract relevant guidelines if requested
        tool_guidelines = ""
        if include_guidelines and relevant_tools:
            guidelines = self._load_tool_guidelines()
            tool_guidelines = extract_relevant_guidelines(
                relevant_tools, guidelines)

        # Build the planning prompt
        style_instructions = get_style_instructions(planning_style)
        planning_prompt = build_planning_prompt(
            user_request, available_tools, user_context, planning_style, tool_guidelines, relevant_tools, style_instructions
        )

        # Get LLM response
        try:
            plan = await self._get_llm_plan(planning_prompt)
            return plan
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return create_fallback_plan(user_request, available_tools)

    async def _get_llm_response(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Get response from LLM for tool identification or other purposes."""
        if not self.llm_client:
            raise ValueError("LLM client not set. Use set_llm_client() first.")

        try:
            # Try to use the LLM client to generate the response
            if hasattr(self.llm_client, 'generate'):
                response = await self.llm_client.generate(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.content
            elif hasattr(self.llm_client, 'chat'):
                # Alternative LLM client interface
                response = await self.llm_client.chat(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            else:
                # Fallback for unknown LLM client interface
                logger.warning("Unknown LLM client interface, using fallback")
                raise ValueError("Unknown LLM client interface")

        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            raise

    async def _get_llm_plan(self, prompt: str) -> str:
        """Get plan from LLM."""
        return await self._get_llm_response(prompt, max_tokens=2000, temperature=0.7)

    async def create_plan_with_tool_context(
        self,
        user_request: str,
        tool_registry,
        user_context: Optional[str] = None,
        planning_style: str = "adhd_friendly",
        include_guidelines: bool = True
    ) -> str:
        """
        Create a plan with detailed tool context from the tool registry and guidelines.

        Args:
            user_request: The user's request or task to plan
            tool_registry: Tool registry to get detailed tool information
            user_context: Additional context about the user's situation
            planning_style: Style of planning to use
            include_guidelines: Whether to include relevant tool guidelines

        Returns:
            A comprehensive plan with tool-specific guidance and guidelines
        """

        try:
            # Get detailed tool information
            tool_schemas = tool_registry.get_schema()
            tools_text = format_tool_info_for_prompt(tool_schemas)

            # Use LLM to identify relevant tools and get guidelines
            relevant_tools = await self._identify_relevant_tools_llm(user_request)
            tool_guidelines = ""
            if include_guidelines and relevant_tools:
                guidelines = self._load_tool_guidelines()
                tool_guidelines = extract_relevant_guidelines(
                    relevant_tools, guidelines)

            # Build enhanced prompt with tool details and guidelines
            style_instructions = get_style_instructions(planning_style)
            enhanced_prompt = build_enhanced_planning_prompt(
                user_request, tools_text, user_context, relevant_tools, tool_guidelines, planning_style, style_instructions
            )

            return await self._get_llm_plan(enhanced_prompt)

        except Exception as e:
            logger.error(f"Error creating plan with tool context: {e}")
            return await self.create_intelligent_plan(user_request, "", user_context, planning_style, include_guidelines)

    def get_planning_summary(self, plan: str) -> str:
        """Extract a summary of the plan for quick reference."""
        return get_planning_summary(plan)
