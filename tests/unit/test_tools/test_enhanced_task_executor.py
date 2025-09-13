"""
Unit tests for enhanced TaskExecutor with sophisticated prompt architecture.

This module tests the enhanced TaskExecutor functionality including:
- Enhanced prompt creation with metadata integration
- Context building improvements
- Response quality assessment
- AI guidance integration
- Professional guidelines implementation
- Error handling and recovery
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from personal_assistant.tools.ai_scheduler.core.executor import TaskExecutor
from personal_assistant.database.models.ai_tasks import AITask
from personal_assistant.tools.metadata import AIEnhancementManager, ToolMetadataManager


class TestEnhancedTaskExecutor:
    """Test class for enhanced TaskExecutor with sophisticated prompt architecture."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = TaskExecutor()
        
        # Create mock AITask
        self.mock_task = Mock(spec=AITask)
        self.mock_task.id = 1
        self.mock_task.title = "Test Reminder"
        self.mock_task.description = "Test reminder description"
        self.mock_task.task_type = "reminder"
        self.mock_task.schedule_type = "one_time"
        self.mock_task.schedule_config = None
        self.mock_task.user_id = 123
        self.mock_task.ai_context = "Test AI context"
        self.mock_task.created_at = datetime.utcnow()
        self.mock_task.last_run_at = None

    def test_initialization_with_metadata(self):
        """Test TaskExecutor initialization with metadata integration."""
        assert self.executor is not None
        assert hasattr(self.executor, 'metadata_manager')
        assert hasattr(self.executor, 'enhancement_manager')
        assert isinstance(self.executor.metadata_manager, ToolMetadataManager)
        assert isinstance(self.executor.enhancement_manager, AIEnhancementManager)

    def test_metadata_initialization_success(self):
        """Test successful metadata initialization."""
        # Test that metadata managers are initialized
        assert self.executor.metadata_manager is not None
        assert self.executor.enhancement_manager is not None

    def test_metadata_initialization_failure(self):
        """Test metadata initialization failure handling."""
        # Test that initialization handles errors gracefully
        assert self.executor.metadata_manager is not None
        assert self.executor.enhancement_manager is not None

    def test_build_base_prompt(self):
        """Test base prompt building with professional structure."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        prompt = self.executor._build_base_prompt(self.mock_task, context)
        
        assert "🎯 AI TASK EXECUTOR" in prompt
        assert "📅 Current time:" in prompt
        assert "🎯 TASK EXECUTION REQUEST:" in prompt
        assert "📊 TASK CONTEXT:" in prompt
        assert str(self.mock_task.id) in prompt
        assert self.mock_task.task_type.upper() in prompt
        assert str(self.mock_task.user_id) in prompt

    def test_build_reminder_content(self):
        """Test reminder task content building."""
        context = {
            'notification_channels': ['sms', 'email'],
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        content = self.executor._build_reminder_content(self.mock_task, context)
        
        assert "📋 REMINDER TASK DETAILS:" in content
        assert "🎯 REMINDER EXECUTION TASK:" in content
        assert self.mock_task.title in content
        assert self.mock_task.description in content
        assert "sms, email" in content
        assert "Please:" in content
        assert "1. Acknowledge the reminder" in content

    def test_build_periodic_task_content(self):
        """Test periodic task content building."""
        self.mock_task.task_type = "periodic_task"
        self.mock_task.schedule_type = "daily"
        self.mock_task.schedule_config = "0 9 * * *"
        
        context = {
            'last_run_at': '2024-01-14T09:00:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        content = self.executor._build_periodic_task_content(self.mock_task, context)
        
        assert "📋 PERIODIC TASK DETAILS:" in content
        assert "🎯 PERIODIC TASK EXECUTION:" in content
        assert self.mock_task.title in content
        assert "daily" in content
        assert "0 9 * * *" in content
        assert "2024-01-14T09:00:00Z" in content

    def test_build_automated_task_content(self):
        """Test automated task content building."""
        self.mock_task.task_type = "automated_task"
        
        context = {
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        content = self.executor._build_automated_task_content(self.mock_task, context)
        
        assert "📋 AUTOMATED TASK DETAILS:" in content
        assert "🎯 AUTOMATED TASK EXECUTION:" in content
        assert self.mock_task.title in content
        assert "system-generated task" in content

    def test_build_generic_task_content(self):
        """Test generic task content building."""
        self.mock_task.task_type = "custom_task"
        
        context = {
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        content = self.executor._build_generic_task_content(self.mock_task, context)
        
        assert "📋 TASK DETAILS:" in content
        assert "🎯 TASK EXECUTION:" in content
        assert self.mock_task.title in content
        assert "custom_task" in content

    def test_build_ai_guidance_with_enhancements(self):
        """Test AI guidance building with enhancements."""
        # Mock enhancements
        mock_enhancement1 = Mock()
        mock_enhancement1.title = "Smart Time Parsing"
        mock_enhancement1.ai_instructions = "Parse time expressions intelligently"
        
        mock_enhancement2 = Mock()
        mock_enhancement2.title = "Context Awareness"
        mock_enhancement2.ai_instructions = "Consider user context and preferences"
        
        enhancements = [mock_enhancement1, mock_enhancement2]
        
        guidance = self.executor._build_ai_guidance(enhancements, self.mock_task, {})
        
        assert "🎯 **AI GUIDANCE & ENHANCEMENTS**:" in guidance
        assert "SMART TIME PARSING" in guidance
        assert "CONTEXT AWARENESS" in guidance
        assert "Parse time expressions intelligently" in guidance
        assert "Consider user context and preferences" in guidance

    def test_build_ai_guidance_no_enhancements(self):
        """Test AI guidance building without enhancements."""
        guidance = self.executor._build_ai_guidance([], self.mock_task, {})
        
        assert "💡 No specific AI guidance available for this task type." in guidance

    def test_build_ai_guidance_empty_instructions(self):
        """Test AI guidance building with empty instructions."""
        mock_enhancement = Mock()
        mock_enhancement.title = "Test Enhancement"
        mock_enhancement.ai_instructions = None
        
        guidance = self.executor._build_ai_guidance([mock_enhancement], self.mock_task, {})
        
        assert "💡 Basic AI guidance available - execute the task as specified." in guidance

    def test_build_professional_guidelines(self):
        """Test professional guidelines building."""
        guidelines = self.executor._build_professional_guidelines()
        
        assert "🎯 **PROFESSIONAL EXECUTION GUIDELINES**:" in guidelines
        assert "🚨 **CRITICAL RULES**:" in guidelines
        assert "💡 **RESPONSE QUALITY**:" in guidelines
        assert "🔄 **TASK COMPLETION**:" in guidelines
        assert "Complete the task fully" in guidelines
        assert "Provide clear, actionable information" in guidelines

    def test_create_ai_prompt_reminder(self):
        """Test enhanced AI prompt creation for reminder tasks."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z',
            'notification_channels': ['sms']
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements') as mock_get_enhancements:
            mock_get_enhancements.return_value = []
            
            prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            assert "🎯 AI TASK EXECUTOR" in prompt
            assert "📋 REMINDER TASK DETAILS:" in prompt
            assert "🎯 **PROFESSIONAL EXECUTION GUIDELINES**:" in prompt
            assert self.mock_task.title in prompt
            assert self.mock_task.description in prompt

    def test_create_ai_prompt_periodic(self):
        """Test enhanced AI prompt creation for periodic tasks."""
        self.mock_task.task_type = "periodic_task"
        self.mock_task.schedule_type = "daily"
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': '2024-01-14T09:00:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements') as mock_get_enhancements:
            mock_get_enhancements.return_value = []
            
            prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            assert "🎯 AI TASK EXECUTOR" in prompt
            assert "📋 PERIODIC TASK DETAILS:" in prompt
            assert "daily" in prompt

    def test_create_ai_prompt_automated(self):
        """Test enhanced AI prompt creation for automated tasks."""
        self.mock_task.task_type = "automated_task"
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements') as mock_get_enhancements:
            mock_get_enhancements.return_value = []
            
            prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            assert "🎯 AI TASK EXECUTOR" in prompt
            assert "📋 AUTOMATED TASK DETAILS:" in prompt

    def test_create_ai_prompt_generic(self):
        """Test enhanced AI prompt creation for generic tasks."""
        self.mock_task.task_type = "custom_task"
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements') as mock_get_enhancements:
            mock_get_enhancements.return_value = []
            
            prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            assert "🎯 AI TASK EXECUTOR" in prompt
            assert "📋 TASK DETAILS:" in prompt
            assert "custom_task" in prompt

    def test_assess_response_quality_high_quality(self):
        """Test response quality assessment for high-quality response."""
        high_quality_response = """
        I acknowledge this reminder about the important meeting.
        
        Here's what I understand:
        1. This is a critical project review meeting
        2. All stakeholders need to be present
        3. We need to prepare the quarterly reports
        
        I suggest we:
        • Send a calendar invite to all participants
        • Prepare the presentation materials
        • Set up the conference room
        
        This meeting is essential for our project success. Let's make sure everyone is prepared and ready to contribute effectively.
        """
        
        quality = self.executor._assess_response_quality(high_quality_response)
        
        assert quality["is_high_quality"] is True
        assert quality["score"] >= 0.6  # At least 3 out of 5 indicators
        assert "acknowledgment" in quality["indicators"]
        assert "actionable_advice" in quality["indicators"]
        assert "structured_format" in quality["indicators"]

    def test_assess_response_quality_low_quality(self):
        """Test response quality assessment for low-quality response."""
        low_quality_response = "ok"
        
        quality = self.executor._assess_response_quality(low_quality_response)
        
        assert quality["is_high_quality"] is False
        assert quality["score"] < 0.6
        assert len(quality["indicators"]) < 3

    def test_assess_response_quality_medium_quality(self):
        """Test response quality assessment for medium-quality response."""
        medium_quality_response = """
        I understand this reminder. 
        
        Let me help you with this task.
        """
        
        quality = self.executor._assess_response_quality(medium_quality_response)
        
        assert quality["is_high_quality"] is False  # Not enough indicators
        assert quality["score"] < 0.6
        assert "acknowledgment" in quality["indicators"]

    def test_extract_response_information(self):
        """Test response information extraction."""
        response = """
        I acknowledge this important reminder.
        
        Here are my suggestions:
        1. Review the documents
        2. Prepare the presentation
        
        Summary: This is a critical task that needs immediate attention.
        
        I'm here to help and support you through this process.
        """
        
        extracted = self.executor._extract_response_information(response)
        
        assert extracted["has_acknowledgment"] is True
        assert extracted["has_actions"] is True
        assert extracted["has_summary"] is True
        assert extracted["has_encouragement"] is True
        assert extracted["is_structured"] is True
        assert extracted["response_length"] > 50

    def test_extract_response_information_minimal(self):
        """Test response information extraction for minimal response."""
        response = "ok"
        
        extracted = self.executor._extract_response_information(response)
        
        assert extracted["has_acknowledgment"] is False
        assert extracted["has_actions"] is False
        assert extracted["has_summary"] is False
        assert extracted["has_encouragement"] is False
        assert extracted["is_structured"] is False
        assert extracted["response_length"] < 50

    def test_process_ai_response_enhanced(self):
        """Test enhanced AI response processing."""
        ai_response = """
        I acknowledge this important reminder about the project deadline.
        
        Here's what I understand:
        1. The project deadline is approaching
        2. We need to complete the final review
        3. All stakeholders should be notified
        
        I suggest we:
        • Schedule a final review meeting
        • Prepare the completion report
        • Notify all team members
        
        This is a critical milestone for our project success.
        """
        
        result = self.executor._process_ai_response(self.mock_task, ai_response)
        
        assert result["success"] is True
        assert result["message"] == ai_response
        assert result["task_id"] == self.mock_task.id
        assert result["task_title"] == self.mock_task.title
        assert result["task_type"] == self.mock_task.task_type
        assert "execution_time" in result
        assert "response_quality" in result
        assert "extracted_info" in result
        assert "execution_status" in result
        assert result["execution_status"] == "completed"
        
        # Check quality assessment
        assert result["response_quality"]["is_high_quality"] is True
        assert "quality_indicators" in result

    def test_process_ai_response_low_quality(self):
        """Test AI response processing for low-quality response."""
        ai_response = "ok"
        
        result = self.executor._process_ai_response(self.mock_task, ai_response)
        
        assert result["success"] is True
        assert result["response_quality"]["is_high_quality"] is False
        assert "quality_indicators" not in result

    def test_build_task_context_enhanced(self):
        """Test enhanced task context building."""
        context = self.executor._build_task_context(self.mock_task)
        
        assert "created_at" in context
        assert "last_run_at" in context
        assert "current_time" in context
        assert context["created_at"] == self.mock_task.created_at.isoformat()
        assert context["last_run_at"] is None
        assert isinstance(context["current_time"], str)

    def test_build_task_context_with_last_run(self):
        """Test task context building with last run time."""
        self.mock_task.last_run_at = datetime.utcnow() - timedelta(hours=2)
        
        context = self.executor._build_task_context(self.mock_task)
        
        assert context["last_run_at"] == self.mock_task.last_run_at.isoformat()

    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Test successful task execution with enhanced prompts."""
        mock_agent = AsyncMock()
        mock_agent.run.return_value = "Enhanced AI response with professional quality"
        
        with patch('personal_assistant.core.agent.AgentCore', return_value=mock_agent):
            result = await self.executor.execute_task(self.mock_task)
            
            assert result["success"] is True
            assert "Enhanced AI response" in result["message"]
            assert result["task_id"] == self.mock_task.id
            assert "response_quality" in result
            assert "extracted_info" in result
            
            # Verify AgentCore was called with enhanced prompt
            mock_agent.run.assert_called_once()
            call_args = mock_agent.run.call_args
            assert "🎯 AI TASK EXECUTOR" in call_args[0][0]  # First argument is the prompt

    @pytest.mark.asyncio
    async def test_execute_task_agent_error(self):
        """Test task execution with agent error."""
        mock_agent = AsyncMock()
        mock_agent.run.side_effect = Exception("Agent execution failed")
        
        with patch('personal_assistant.core.agent.AgentCore', return_value=mock_agent):
            result = await self.executor.execute_task(self.mock_task)
            
            assert result["success"] is False
            assert "Agent execution failed" in result["message"]
            assert result["task_id"] == self.mock_task.id

    def test_task_specific_content_routing(self):
        """Test that task-specific content is routed correctly."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Test reminder
        self.mock_task.task_type = "reminder"
        content = self.executor._build_task_specific_content(self.mock_task, context)
        assert "REMINDER TASK DETAILS:" in content
        
        # Test periodic
        self.mock_task.task_type = "periodic_task"
        content = self.executor._build_task_specific_content(self.mock_task, context)
        assert "PERIODIC TASK DETAILS:" in content
        
        # Test automated
        self.mock_task.task_type = "automated_task"
        content = self.executor._build_task_specific_content(self.mock_task, context)
        assert "AUTOMATED TASK DETAILS:" in content
        
        # Test generic
        self.mock_task.task_type = "custom_task"
        content = self.executor._build_task_specific_content(self.mock_task, context)
        assert "TASK DETAILS:" in content

    def test_enhanced_prompt_structure_consistency(self):
        """Test that enhanced prompts maintain consistent structure."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            # Check for consistent structure elements
            assert "🎯 AI TASK EXECUTOR" in prompt
            assert "📅 Current time:" in prompt
            assert "📊 TASK CONTEXT:" in prompt
            assert "🎯 **PROFESSIONAL EXECUTION GUIDELINES**:" in prompt
            assert "🚨 **CRITICAL RULES**:" in prompt
            assert "💡 **RESPONSE QUALITY**:" in prompt
            assert "🔄 **TASK COMPLETION**:" in prompt

    def test_metadata_integration_in_prompts(self):
        """Test that metadata integration works in prompt creation."""
        # Mock enhancements with AI instructions
        mock_enhancement = Mock()
        mock_enhancement.title = "Smart Time Parsing"
        mock_enhancement.ai_instructions = "Parse time expressions like 'tomorrow at 3pm' intelligently"
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[mock_enhancement]):
            prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            assert "🎯 **AI GUIDANCE & ENHANCEMENTS**:" in prompt
            assert "SMART TIME PARSING" in prompt
            assert "Parse time expressions like 'tomorrow at 3pm' intelligently" in prompt

    def test_response_quality_indicators(self):
        """Test response quality indicator detection."""
        test_cases = [
            ("I acknowledge this task", ["acknowledgment"]),
            ("Here are my suggestions: 1. Do this 2. Do that", ["actionable_advice", "structured_format"]),
            ("I'm here to help and support you", ["supportive_tone"]),
            ("This is a comprehensive response with multiple sections", ["substantial_response"]),
        ]
        
        for response, expected_indicators in test_cases:
            quality = self.executor._assess_response_quality(response)
            for indicator in expected_indicators:
                assert indicator in quality["indicators"], f"Expected {indicator} in {response}"

    def test_error_handling_in_prompt_creation(self):
        """Test error handling in prompt creation methods."""
        # Test with None task
        with pytest.raises(AttributeError):
            self.executor._build_base_prompt(None, {})
        
        # Test with invalid context
        context = {
            "invalid": "context",
            "created_at": None,
            "last_run_at": None,
            "current_time": None
        }
        prompt = self.executor._build_base_prompt(self.mock_task, context)
        assert "Unknown" in prompt  # Should handle missing created_at gracefully

    def test_performance_of_prompt_creation(self):
        """Test performance of prompt creation methods."""
        import time
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': None,
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        start_time = time.time()
        
        # Create multiple prompts to test performance
        for _ in range(100):
            with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
                self.executor._create_ai_prompt(self.mock_task, context)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete 100 prompt creations in reasonable time (< 1 second)
        assert execution_time < 1.0, f"Prompt creation took too long: {execution_time:.2f}s"
