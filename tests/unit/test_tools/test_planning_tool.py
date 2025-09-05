"""
Unit tests for Planning Tool (LLM Planner).

This module tests the LLM Planner tool functionality including
plan creation, tool identification, guideline integration, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

from personal_assistant.tools.planning.llm_planner import LLMPlannerTool
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import ToolDataGenerator


class TestLLMPlannerTool:
    """Test cases for LLM Planner Tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.llm_client = Mock()
        self.llm_client.generate = AsyncMock()
        self.llm_client.chat = AsyncMock()
        
        self.planner = LLMPlannerTool(
            llm_client=self.llm_client,
            guidelines_path="test_guidelines_path"
        )
        
        self.test_request = "Create a meeting note template for project planning"
        self.test_context = "I'm a project manager organizing team documentation"
        self.test_tools = "notion_notes,codebase_search,read_file"

    def test_planner_initialization(self):
        """Test LLM planner initialization."""
        assert self.planner.llm_client == self.llm_client
        assert self.planner.guidelines_path == "test_guidelines_path"
        assert self.planner.guidelines_cache == {}
        assert hasattr(self.planner, 'planning_tool')

    def test_planner_initialization_without_llm_client(self):
        """Test LLM planner initialization without LLM client."""
        planner = LLMPlannerTool()
        assert planner.llm_client is None
        assert planner.guidelines_path == "src/personal_assistant/tools"
        assert planner.guidelines_cache == {}

    def test_planner_iteration(self):
        """Test that planner is iterable and returns all tools."""
        tools = list(self.planner)
        assert len(tools) == 1
        assert tools[0].name == "create_intelligent_plan"

    def test_planning_tool_properties(self):
        """Test planning tool properties."""
        tool = self.planner.planning_tool
        assert tool.name == "create_intelligent_plan"
        assert "intelligent, step-by-step plan" in tool.description
        assert "user_request" in tool.parameters
        assert "available_tools" in tool.parameters
        assert "user_context" in tool.parameters
        assert "planning_style" in tool.parameters
        assert "include_guidelines" in tool.parameters

    def test_set_llm_client(self):
        """Test setting LLM client."""
        new_client = Mock()
        self.planner.set_llm_client(new_client)
        assert self.planner.llm_client == new_client

    def test_load_tool_guidelines_caching(self):
        """Test that tool guidelines are cached after first load."""
        with patch('personal_assistant.tools.planning.llm_planner.load_tool_guidelines') as mock_load:
            mock_load.return_value = {"notion_notes": "guidelines content"}
            
            # First call should load and cache
            result1 = self.planner._load_tool_guidelines()
            assert result1 == {"notion_notes": "guidelines content"}
            assert self.planner.guidelines_cache == {"notion_notes": "guidelines content"}
            
            # Second call should use cache
            result2 = self.planner._load_tool_guidelines()
            assert result2 == {"notion_notes": "guidelines content"}
            mock_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_identify_relevant_tools_llm_success(self):
        """Test successful LLM-based tool identification."""
        mock_response = Mock()
        mock_response.content = "notion_notes,codebase_search"
        
        self.llm_client.generate.return_value = mock_response
        
        with patch('personal_assistant.tools.planning.llm_planner.build_tool_identification_prompt') as mock_build, \
             patch('personal_assistant.tools.planning.llm_planner.parse_tool_identification_response') as mock_parse:
            
            mock_build.return_value = "test prompt"
            mock_parse.return_value = ["notion_notes", "codebase_search"]
            
            result = await self.planner._identify_relevant_tools_llm(
                self.test_request, self.test_tools
            )
            
            assert result == ["notion_notes", "codebase_search"]
            mock_build.assert_called_once()
            mock_parse.assert_called_once_with(mock_response.content)

    @pytest.mark.asyncio
    async def test_identify_relevant_tools_llm_no_client(self):
        """Test tool identification when LLM client is not set."""
        planner = LLMPlannerTool()  # No LLM client
        
        with patch('personal_assistant.tools.planning.llm_planner.identify_relevant_tools_fallback') as mock_fallback:
            mock_fallback.return_value = ["notion_notes"]
            
            result = await planner._identify_relevant_tools_llm(
                self.test_request, self.test_tools
            )
            
            assert result == ["notion_notes"]
            mock_fallback.assert_called_once_with(self.test_request, self.test_tools)

    @pytest.mark.asyncio
    async def test_identify_relevant_tools_llm_exception(self):
        """Test tool identification when LLM call fails."""
        self.llm_client.generate.side_effect = Exception("LLM error")
        
        with patch('personal_assistant.tools.planning.llm_planner.identify_relevant_tools_fallback') as mock_fallback:
            mock_fallback.return_value = ["notion_notes"]
            
            result = await self.planner._identify_relevant_tools_llm(
                self.test_request, self.test_tools
            )
            
            assert result == ["notion_notes"]
            mock_fallback.assert_called_once_with(self.test_request, self.test_tools)

    @pytest.mark.asyncio
    async def test_get_llm_response_generate_interface(self):
        """Test LLM response with generate interface."""
        mock_response = Mock()
        mock_response.content = "Test response"
        self.llm_client.generate.return_value = mock_response
        
        result = await self.planner._get_llm_response("test prompt", max_tokens=1000, temperature=0.5)
        
        assert result == "Test response"
        self.llm_client.generate.assert_called_once_with(
            prompt="test prompt", max_tokens=1000, temperature=0.5
        )

    @pytest.mark.asyncio
    async def test_get_llm_response_chat_interface(self):
        """Test LLM response with chat interface."""
        # Mock client without generate method but with chat method
        chat_client = Mock()
        # Remove the generate attribute entirely instead of setting it to None
        del chat_client.generate
        chat_client.chat = AsyncMock()
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Chat response"
        chat_client.chat.return_value = mock_response
        
        planner = LLMPlannerTool(llm_client=chat_client)
        
        result = await planner._get_llm_response("test prompt")
        
        assert result == "Chat response"
        chat_client.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_llm_response_no_client(self):
        """Test LLM response when client is not set."""
        planner = LLMPlannerTool()  # No LLM client
        
        with pytest.raises(ValueError, match="LLM client not set"):
            await planner._get_llm_response("test prompt")

    @pytest.mark.asyncio
    async def test_get_llm_response_unknown_interface(self):
        """Test LLM response with unknown client interface."""
        unknown_client = Mock()
        # Remove both attributes entirely instead of setting them to None
        del unknown_client.generate
        del unknown_client.chat
        
        planner = LLMPlannerTool(llm_client=unknown_client)
        
        with pytest.raises(ValueError, match="Unknown LLM client interface"):
            await planner._get_llm_response("test prompt")

    @pytest.mark.asyncio
    async def test_get_llm_response_exception(self):
        """Test LLM response when generation fails."""
        self.llm_client.generate.side_effect = Exception("Generation failed")
        
        with pytest.raises(Exception, match="Generation failed"):
            await self.planner._get_llm_response("test prompt")

    @pytest.mark.asyncio
    async def test_create_intelligent_plan_success(self):
        """Test successful intelligent plan creation."""
        # Mock the internal methods
        with patch.object(self.planner, '_identify_relevant_tools_llm') as mock_identify, \
             patch.object(self.planner, '_load_tool_guidelines') as mock_load, \
             patch('personal_assistant.tools.planning.llm_planner.extract_relevant_guidelines') as mock_extract, \
             patch('personal_assistant.tools.planning.llm_planner.get_style_instructions') as mock_style, \
             patch('personal_assistant.tools.planning.llm_planner.build_planning_prompt') as mock_build, \
             patch.object(self.planner, '_get_llm_plan') as mock_get_plan:
            
            mock_identify.return_value = ["notion_notes"]
            mock_load.return_value = {"notion_notes": "guidelines"}
            mock_extract.return_value = "extracted guidelines"
            mock_style.return_value = "style instructions"
            mock_build.return_value = "planning prompt"
            mock_get_plan.return_value = "Generated plan content"
            
            result = await self.planner.create_intelligent_plan(
                user_request=self.test_request,
                available_tools=self.test_tools,
                user_context=self.test_context,
                planning_style="detailed",
                include_guidelines=True
            )
            
            assert result == "Generated plan content"
            mock_identify.assert_called_once_with(self.test_request, self.test_tools)
            mock_extract.assert_called_once_with(["notion_notes"], {"notion_notes": "guidelines"})
            mock_get_plan.assert_called_once_with("planning prompt")

    @pytest.mark.asyncio
    async def test_create_intelligent_plan_without_guidelines(self):
        """Test intelligent plan creation without guidelines."""
        with patch.object(self.planner, '_identify_relevant_tools_llm') as mock_identify, \
             patch('personal_assistant.tools.planning.llm_planner.get_style_instructions') as mock_style, \
             patch('personal_assistant.tools.planning.llm_planner.build_planning_prompt') as mock_build, \
             patch.object(self.planner, '_get_llm_plan') as mock_get_plan:
            
            mock_identify.return_value = ["notion_notes"]
            mock_style.return_value = "style instructions"
            mock_build.return_value = "planning prompt"
            mock_get_plan.return_value = "Generated plan content"
            
            result = await self.planner.create_intelligent_plan(
                user_request=self.test_request,
                include_guidelines=False
            )
            
            assert result == "Generated plan content"
            # Should not call extract_relevant_guidelines when include_guidelines=False

    @pytest.mark.asyncio
    async def test_create_intelligent_plan_llm_failure(self):
        """Test intelligent plan creation when LLM fails."""
        with patch.object(self.planner, '_identify_relevant_tools_llm') as mock_identify, \
             patch('personal_assistant.tools.planning.llm_planner.create_fallback_plan') as mock_fallback:
            
            mock_identify.return_value = ["notion_notes"]
            mock_fallback.return_value = "Fallback plan"
            
            # Mock _get_llm_plan to raise an exception
            with patch.object(self.planner, '_get_llm_plan', side_effect=Exception("LLM error")):
                result = await self.planner.create_intelligent_plan(
                    user_request=self.test_request
                )
            
            assert result == "Fallback plan"
            mock_fallback.assert_called_once_with(self.test_request, None)

    @pytest.mark.asyncio
    async def test_create_plan_with_tool_context_success(self):
        """Test successful plan creation with tool context."""
        mock_registry = Mock()
        mock_registry.get_schema.return_value = {"tools": [{"name": "notion_notes"}]}
        
        with patch('personal_assistant.tools.planning.llm_planner.format_tool_info_for_prompt') as mock_format, \
             patch.object(self.planner, '_identify_relevant_tools_llm') as mock_identify, \
             patch.object(self.planner, '_load_tool_guidelines') as mock_load, \
             patch('personal_assistant.tools.planning.llm_planner.extract_relevant_guidelines') as mock_extract, \
             patch('personal_assistant.tools.planning.llm_planner.get_style_instructions') as mock_style, \
             patch('personal_assistant.tools.planning.llm_planner.build_enhanced_planning_prompt') as mock_build, \
             patch.object(self.planner, '_get_llm_plan') as mock_get_plan:
            
            mock_format.return_value = "formatted tools"
            mock_identify.return_value = ["notion_notes"]
            mock_load.return_value = {"notion_notes": "guidelines"}
            mock_extract.return_value = "extracted guidelines"
            mock_style.return_value = "style instructions"
            mock_build.return_value = "enhanced prompt"
            mock_get_plan.return_value = "Enhanced plan content"
            
            result = await self.planner.create_plan_with_tool_context(
                user_request=self.test_request,
                tool_registry=mock_registry,
                user_context=self.test_context,
                planning_style="detailed",
                include_guidelines=True
            )
            
            assert result == "Enhanced plan content"
            mock_registry.get_schema.assert_called_once()
            mock_format.assert_called_once_with({"tools": [{"name": "notion_notes"}]})
            mock_get_plan.assert_called_once_with("enhanced prompt")

    @pytest.mark.asyncio
    async def test_create_plan_with_tool_context_exception(self):
        """Test plan creation with tool context when it fails."""
        mock_registry = Mock()
        mock_registry.get_schema.side_effect = Exception("Registry error")
        
        with patch.object(self.planner, 'create_intelligent_plan') as mock_fallback:
            mock_fallback.return_value = "Fallback plan"
            
            result = await self.planner.create_plan_with_tool_context(
                user_request=self.test_request,
                tool_registry=mock_registry
            )
            
            assert result == "Fallback plan"
            mock_fallback.assert_called_once()

    def test_get_planning_summary(self):
        """Test planning summary extraction."""
        test_plan = """
        # Project Planning Plan
        
        ## Step 1: Research
        - Gather requirements
        - Analyze current state
        
        ## Step 2: Design
        - Create architecture
        - Plan implementation
        """
        
        with patch('personal_assistant.tools.planning.llm_planner.get_planning_summary') as mock_summary:
            mock_summary.return_value = "Summary: Research and design project"
            
            result = self.planner.get_planning_summary(test_plan)
            
            assert result == "Summary: Research and design project"
            mock_summary.assert_called_once_with(test_plan)

    def test_planning_tool_parameter_validation(self):
        """Test that planning tool parameters are properly defined."""
        tool = self.planner.planning_tool
        params = tool.parameters
        
        # Test required parameter
        assert params["user_request"]["type"] == "string"
        assert "user's request or task to plan" in params["user_request"]["description"]
        
        # Test optional parameters
        assert params["available_tools"]["type"] == "string"
        assert params["user_context"]["type"] == "string"
        assert params["planning_style"]["type"] == "string"
        assert params["include_guidelines"]["type"] == "boolean"
        
        # Test planning style options
        assert "detailed" in params["planning_style"]["description"]
        assert "concise" in params["planning_style"]["description"]
        assert "adhd_friendly" in params["planning_style"]["description"]

    def test_planning_tool_description(self):
        """Test that planning tool description is informative."""
        tool = self.planner.planning_tool
        description = tool.description
        
        assert "intelligent" in description
        assert "step-by-step plan" in description
        assert "LLM analysis" in description
        assert "tool recommendations" in description
        assert "contextual guidance" in description

    @pytest.mark.asyncio
    async def test_create_intelligent_plan_default_parameters(self):
        """Test intelligent plan creation with default parameters."""
        with patch.object(self.planner, '_identify_relevant_tools_llm') as mock_identify, \
             patch('personal_assistant.tools.planning.llm_planner.get_style_instructions') as mock_style, \
             patch('personal_assistant.tools.planning.llm_planner.build_planning_prompt') as mock_build, \
             patch.object(self.planner, '_get_llm_plan') as mock_get_plan:
            
            mock_identify.return_value = []
            mock_style.return_value = "adhd_friendly style"
            mock_build.return_value = "planning prompt"
            mock_get_plan.return_value = "Default plan"
            
            result = await self.planner.create_intelligent_plan(
                user_request=self.test_request
            )
            
            assert result == "Default plan"
            # Should use default values: available_tools=None, user_context=None, 
            # planning_style="adhd_friendly", include_guidelines=True
            mock_identify.assert_called_once_with(self.test_request, None)

    @pytest.mark.asyncio
    async def test_create_intelligent_plan_different_styles(self):
        """Test intelligent plan creation with different planning styles."""
        styles = ["adhd_friendly", "detailed", "concise"]
        
        for style in styles:
            with patch.object(self.planner, '_identify_relevant_tools_llm') as mock_identify, \
                 patch('personal_assistant.tools.planning.llm_planner.get_style_instructions') as mock_style, \
                 patch('personal_assistant.tools.planning.llm_planner.build_planning_prompt') as mock_build, \
                 patch.object(self.planner, '_get_llm_plan') as mock_get_plan:
                
                mock_identify.return_value = []
                mock_style.return_value = f"{style} style"
                mock_build.return_value = "planning prompt"
                mock_get_plan.return_value = f"{style.title()} plan"
                
                result = await self.planner.create_intelligent_plan(
                    user_request=self.test_request,
                    planning_style=style
                )
                
                assert result == f"{style.title()} plan"
                mock_style.assert_called_with(style)

    def test_guidelines_path_configuration(self):
        """Test that guidelines path can be configured."""
        custom_path = "/custom/guidelines/path"
        planner = LLMPlannerTool(guidelines_path=custom_path)
        
        assert planner.guidelines_path == custom_path

    def test_guidelines_cache_initialization(self):
        """Test that guidelines cache is properly initialized."""
        assert isinstance(self.planner.guidelines_cache, dict)
        assert len(self.planner.guidelines_cache) == 0

    @pytest.mark.asyncio
    async def test_create_intelligent_plan_empty_request(self):
        """Test intelligent plan creation with empty request."""
        with patch.object(self.planner, '_identify_relevant_tools_llm') as mock_identify, \
             patch('personal_assistant.tools.planning.llm_planner.get_style_instructions') as mock_style, \
             patch('personal_assistant.tools.planning.llm_planner.build_planning_prompt') as mock_build, \
             patch.object(self.planner, '_get_llm_plan') as mock_get_plan:
            
            mock_identify.return_value = []
            mock_style.return_value = "style instructions"
            mock_build.return_value = "planning prompt"
            mock_get_plan.return_value = "Plan for empty request"
            
            result = await self.planner.create_intelligent_plan(
                user_request=""
            )
            
            assert result == "Plan for empty request"
            mock_identify.assert_called_once_with("", None)

    def test_tool_categories(self):
        """Test that tools can have categories set."""
        tool = self.planner.planning_tool
        tool.set_category("Planning")
        assert tool.category == "Planning"
        
        # Test that category is returned correctly
        assert tool.category == "Planning"

    def test_tool_user_intent_tracking(self):
        """Test that tools can track user intent."""
        tool = self.planner.planning_tool
        
        # Test setting user intent
        tool.set_user_intent("Create a project plan")
        assert tool.get_user_intent() == "Create a project plan"
        
        # Test default user intent
        new_tool = LLMPlannerTool().planning_tool
        assert new_tool.get_user_intent() == "Unknown user intent"
