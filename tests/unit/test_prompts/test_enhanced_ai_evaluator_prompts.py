"""
Unit tests for enhanced AI evaluator prompts with sophisticated architecture.

This module tests the enhanced AI evaluator prompts functionality including:
- Enhanced evaluation prompt creation
- Modular prompt building
- Context-aware variations
- JSON response enhancement
- Professional guidelines integration
- Error handling and validation
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from personal_assistant.prompts.ai_evaluator_prompts import AIEvaluatorPrompts


@pytest.mark.asyncio
class TestEnhancedAIEvaluatorPrompts:
    """Test class for enhanced AI evaluator prompts with sophisticated architecture."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_ai_context = {
            'event': {
                'title': 'Project Review Meeting',
                'type': 'meeting',
                'priority': 'high',
                'location': 'Conference Room A',
                'start_time': '2024-01-15T14:00:00Z',
                'end_time': '2024-01-15T15:00:00Z',
                'description': 'Quarterly project review with stakeholders'
            },
            'timing': {
                'time_until_start_hours': 2.5,
                'is_urgent': False,
                'is_soon': True
            },
            'recurrence': {
                'hint': 'weekly',
                'is_recurring': True,
                'pattern': 'Every Monday at 2 PM'
            },
            'processing': {
                'status': 'pending',
                'last_processed': '2024-01-08T14:00:00Z',
                'days_since_last_processed': 7
            }
        }

    def test_create_evaluation_prompt_enhanced_structure(self):
        """Test enhanced evaluation prompt structure."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check for enhanced structure elements
        assert "🎯 AI CALENDAR EVENT EVALUATOR" in prompt
        assert "📅 Current time:" in prompt
        assert "🎯 EVALUATION REQUEST:" in prompt
        assert "📊 EVALUATION CONTEXT:" in prompt
        assert "📋 EVENT DETAILS:" in prompt
        assert "⏰ TIMING ANALYSIS:" in prompt
        assert "🔄 RECURRENCE ANALYSIS:" in prompt
        assert "📚 PROCESSING HISTORY:" in prompt
        assert "🎯 EVALUATION GUIDANCE:" in prompt
        assert "📋 RESPONSE FORMAT:" in prompt
        assert "🎯 **PROFESSIONAL EVALUATION GUIDELINES**:" in prompt

    def test_create_evaluation_prompt_event_details(self):
        """Test event details section in evaluation prompt."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check event details are included
        assert "Project Review Meeting" in prompt
        assert "meeting" in prompt
        assert "high" in prompt
        assert "Conference Room A" in prompt
        assert "2024-01-15T14:00:00Z" in prompt
        assert "2024-01-15T15:00:00Z" in prompt
        assert "Quarterly project review with stakeholders" in prompt

    def test_create_evaluation_prompt_timing_analysis(self):
        """Test timing analysis section in evaluation prompt."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check timing analysis
        assert "2.5" in prompt  # time_until_start_hours
        assert "MEDIUM" in prompt  # urgency level
        assert "False" in prompt  # is_urgent
        assert "True" in prompt  # is_soon
        assert "Plan ahead" in prompt  # timing context

    def test_create_evaluation_prompt_urgency_levels(self):
        """Test different urgency levels in timing analysis."""
        # Test urgent event
        urgent_context = self.sample_ai_context.copy()
        urgent_context['timing'] = {
            'time_until_start_hours': 0.5,
            'is_urgent': True,
            'is_soon': True
        }
        
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(urgent_context)
        assert "HIGH" in prompt
        assert "Immediate attention required" in prompt
        
        # Test low urgency event
        low_urgency_context = self.sample_ai_context.copy()
        low_urgency_context['timing'] = {
            'time_until_start_hours': 48.0,
            'is_urgent': False,
            'is_soon': False
        }
        
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(low_urgency_context)
        assert "LOW" in prompt
        assert "Future consideration" in prompt

    def test_create_evaluation_prompt_recurrence_analysis(self):
        """Test recurrence analysis section in evaluation prompt."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check recurrence analysis
        assert "weekly" in prompt
        assert "True" in prompt  # is_recurring
        assert "Every Monday at 2 PM" in prompt
        assert "Regular event - check if this occurrence needs attention" in prompt

    def test_create_evaluation_prompt_processing_history(self):
        """Test processing history section in evaluation prompt."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check processing history
        assert "pending" in prompt
        assert "2024-01-08T14:00:00Z" in prompt
        assert "7" in prompt  # days_since_last_processed
        assert "Not recently processed - may need attention" in prompt

    def test_create_evaluation_prompt_recent_processing(self):
        """Test processing history for recently processed event."""
        recent_context = self.sample_ai_context.copy()
        recent_context['processing'] = {
            'status': 'completed',
            'last_processed': '2024-01-15T10:00:00Z',
            'days_since_last_processed': 0.2
        }
        
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(recent_context)
        assert "Recently handled - may not need re-processing" in prompt

    def test_create_evaluation_prompt_evaluation_guidance(self):
        """Test evaluation guidance section in evaluation prompt."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check evaluation guidance elements
        assert "🚨 **CRITICAL DECISION FACTORS**:" in prompt
        assert "Event Importance" in prompt
        assert "Timing Relevance" in prompt
        assert "Recurrence Context" in prompt
        assert "Processing History" in prompt
        assert "User Value" in prompt
        
        assert "💡 **EVALUATION CRITERIA**:" in prompt
        assert "High Priority" in prompt
        assert "Medium Priority" in prompt
        assert "Low Priority" in prompt
        assert "Skip" in prompt
        
        assert "🔄 **RECURRENCE LOGIC**:" in prompt
        assert "First occurrence" in prompt
        assert "Regular occurrence" in prompt
        assert "Recent processing" in prompt
        assert "Pattern changes" in prompt
        
        assert "⚖️ **DECISION WEIGHTING**:" in prompt
        assert "Urgency (40%)" in prompt
        assert "Importance (30%)" in prompt
        assert "Context (20%)" in prompt
        assert "History (10%)" in prompt

    def test_create_evaluation_prompt_response_format(self):
        """Test response format section in evaluation prompt."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check response format elements
        assert "📋 RESPONSE FORMAT:" in prompt
        assert "should_process" in prompt
        assert "reason" in prompt
        assert "confidence" in prompt
        assert "suggested_actions" in prompt
        assert "event_type_analysis" in prompt
        assert "priority_score" in prompt
        assert "processing_urgency" in prompt
        
        assert "🎯 **RESPONSE QUALITY REQUIREMENTS**:" in prompt
        assert "specific, actionable reasons" in prompt
        assert "concrete suggested actions" in prompt
        assert "detailed analysis" in prompt
        assert "appropriate priority and urgency scores" in prompt

    def test_create_evaluation_prompt_professional_guidelines(self):
        """Test professional guidelines section in evaluation prompt."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Check professional guidelines elements
        assert "🎯 **PROFESSIONAL EVALUATION GUIDELINES**:" in prompt
        assert "🚨 **CRITICAL RULES**:" in prompt
        assert "Make intelligent, context-aware decisions" in prompt
        assert "Consider all available information" in prompt
        assert "Provide clear, specific reasoning" in prompt
        
        assert "💡 **EVALUATION QUALITY**:" in prompt
        assert "Be thorough in your analysis" in prompt
        assert "Consider both immediate and long-term implications" in prompt
        assert "Balance urgency with importance" in prompt
        
        assert "🔄 **DECISION CONSISTENCY**:" in prompt
        assert "Apply consistent criteria" in prompt
        assert "Consider the broader context" in prompt
        assert "Balance efficiency with thoroughness" in prompt

    def test_create_recurrence_analysis_prompt_enhanced(self):
        """Test enhanced recurrence analysis prompt creation."""
        event_title = "Weekly Team Standup"
        last_processed = datetime(2024, 1, 8, 14, 0, 0)
        
        prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt(event_title, last_processed)
        
        # Check enhanced structure
        assert "🎯 AI RECURRENCE PATTERN ANALYZER" in prompt
        assert "📅 Current time:" in prompt
        assert "🎯 ANALYSIS REQUEST:" in prompt
        assert "📊 ANALYSIS CONTEXT:" in prompt
        assert "📋 EVENT ANALYSIS:" in prompt
        assert "🔄 PATTERN ANALYSIS GUIDANCE:" in prompt
        assert "🎯 DECISION CRITERIA:" in prompt
        assert "📋 RESPONSE FORMAT:" in prompt

    def test_create_recurrence_analysis_prompt_event_analysis(self):
        """Test event analysis section in recurrence prompt."""
        event_title = "Daily Standup Meeting"
        last_processed = datetime(2024, 1, 14, 9, 0, 0)
        
        prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt(event_title, last_processed)
        
        # Check event analysis
        assert "Daily Standup Meeting" in prompt
        assert "2024-01-14T09:00:00Z" in prompt
        assert "Recently processed" in prompt  # Less than 24 hours ago

    def test_create_recurrence_analysis_prompt_no_last_processed(self):
        """Test recurrence analysis prompt without last processed time."""
        event_title = "New Weekly Meeting"
        
        prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt(event_title, None)
        
        # Check event analysis for never processed
        assert "New Weekly Meeting" in prompt
        assert "Never" in prompt
        assert "N/A" in prompt  # time_since_last_processed
        assert "Never processed" in prompt

    def test_create_recurrence_analysis_prompt_pattern_guidance(self):
        """Test pattern guidance section in recurrence prompt."""
        prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt("Test Event", None)
        
        # Check pattern guidance
        assert "🚨 **PATTERN DETECTION**:" in prompt
        assert "Daily patterns" in prompt
        assert "Weekly patterns" in prompt
        assert "Monthly patterns" in prompt
        assert "Custom intervals" in prompt
        assert "Time-based" in prompt
        
        assert "💡 **PROCESSING TIMING LOGIC**:" in prompt
        assert "First occurrence" in prompt
        assert "Regular occurrence" in prompt
        assert "Recent processing" in prompt
        assert "Pattern changes" in prompt
        assert "Context changes" in prompt
        
        assert "⚖️ **DECISION FACTORS**:" in prompt
        assert "Pattern frequency" in prompt
        assert "Processing interval" in prompt
        assert "Last processing" in prompt
        assert "Context relevance" in prompt
        assert "User value" in prompt

    def test_create_recurrence_analysis_prompt_decision_criteria(self):
        """Test decision criteria section in recurrence prompt."""
        prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt("Test Event", None)
        
        # Check decision criteria
        assert "🎯 DECISION CRITERIA:" in prompt
        assert "🚨 **SHOULD PROCESS NOW IF**:" in prompt
        assert "first occurrence" in prompt
        assert "significant time has passed" in prompt
        assert "event context or importance has changed" in prompt
        
        assert "🚫 **SKIP PROCESSING IF**:" in prompt
        assert "Recently processed" in prompt
        assert "Pattern suggests" in prompt
        assert "Context hasn't changed" in prompt
        assert "Processing would provide no additional value" in prompt
        
        assert "💡 **PATTERN-SPECIFIC RULES**:" in prompt
        assert "Daily events" in prompt
        assert "Weekly events" in prompt
        assert "Monthly events" in prompt
        assert "Custom intervals" in prompt

    def test_create_recurrence_analysis_prompt_response_format(self):
        """Test response format section in recurrence prompt."""
        prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt("Test Event", None)
        
        # Check response format
        assert "📋 RESPONSE FORMAT:" in prompt
        assert "pattern" in prompt
        assert "should_process_now" in prompt
        assert "reason" in prompt
        assert "next_occurrence" in prompt
        assert "pattern_confidence" in prompt
        assert "processing_interval" in prompt
        assert "pattern_type" in prompt
        
        assert "🎯 **RESPONSE QUALITY REQUIREMENTS**:" in prompt
        assert "specific pattern identification" in prompt
        assert "detailed reasoning" in prompt
        assert "appropriate next processing time" in prompt
        assert "recommended processing interval" in prompt

    def test_build_base_evaluation_prompt(self):
        """Test base evaluation prompt building."""
        prompt = AIEvaluatorPrompts._build_base_evaluation_prompt()
        
        assert "🎯 AI CALENDAR EVENT EVALUATOR" in prompt
        assert "📅 Current time:" in prompt
        assert "🎯 EVALUATION REQUEST:" in prompt
        assert "📊 EVALUATION CONTEXT:" in prompt
        assert "intelligent calendar assistant" in prompt
        assert "sophisticated decision-making capabilities" in prompt

    def test_build_event_details_section(self):
        """Test event details section building."""
        event = {
            'title': 'Test Meeting',
            'type': 'meeting',
            'priority': 'medium',
            'location': 'Room 101',
            'start_time': '2024-01-15T10:00:00Z',
            'end_time': '2024-01-15T11:00:00Z',
            'description': 'Test meeting description'
        }
        
        section = AIEvaluatorPrompts._build_event_details_section(event)
        
        assert "📋 EVENT DETAILS:" in section
        assert "Test Meeting" in section
        assert "meeting" in section
        assert "medium" in section
        assert "Room 101" in section
        assert "2024-01-15T10:00:00Z" in section
        assert "2024-01-15T11:00:00Z" in section
        assert "Test meeting description" in section

    def test_build_event_details_section_with_none_values(self):
        """Test event details section with None values."""
        event = {
            'title': 'Test Meeting',
            'type': 'meeting',
            'priority': 'medium',
            'location': None,
            'start_time': '2024-01-15T10:00:00Z',
            'end_time': None,
            'description': None
        }
        
        section = AIEvaluatorPrompts._build_event_details_section(event)
        
        assert "Not specified" in section  # for location and end_time
        assert "No description" in section  # for description

    def test_build_timing_analysis_section(self):
        """Test timing analysis section building."""
        timing = {
            'time_until_start_hours': 1.5,
            'is_urgent': True,
            'is_soon': True
        }
        
        section = AIEvaluatorPrompts._build_timing_analysis_section(timing)
        
        assert "⏰ TIMING ANALYSIS:" in section
        assert "1.5" in section
        assert "HIGH" in section  # urgency level
        assert "True" in section  # is_urgent
        assert "True" in section  # is_soon
        assert "Immediate attention required" in section

    def test_build_timing_analysis_section_medium_urgency(self):
        """Test timing analysis section with medium urgency."""
        timing = {
            'time_until_start_hours': 4.0,
            'is_urgent': False,
            'is_soon': True
        }
        
        section = AIEvaluatorPrompts._build_timing_analysis_section(timing)
        
        assert "MEDIUM" in section
        assert "Plan ahead" in section

    def test_build_timing_analysis_section_low_urgency(self):
        """Test timing analysis section with low urgency."""
        timing = {
            'time_until_start_hours': 24.0,
            'is_urgent': False,
            'is_soon': False
        }
        
        section = AIEvaluatorPrompts._build_timing_analysis_section(timing)
        
        assert "LOW" in section
        assert "Future consideration" in section

    def test_build_recurrence_analysis_section(self):
        """Test recurrence analysis section building."""
        recurrence = {
            'hint': 'daily',
            'is_recurring': True,
            'pattern': 'Every weekday at 9 AM'
        }
        
        section = AIEvaluatorPrompts._build_recurrence_analysis_section(recurrence)
        
        assert "🔄 RECURRENCE ANALYSIS:" in section
        assert "daily" in section
        assert "True" in section
        assert "Every weekday at 9 AM" in section
        assert "Regular event - check if this occurrence needs attention" in section

    def test_build_recurrence_analysis_section_non_recurring(self):
        """Test recurrence analysis section for non-recurring event."""
        recurrence = {
            'hint': None,
            'is_recurring': False,
            'pattern': None
        }
        
        section = AIEvaluatorPrompts._build_recurrence_analysis_section(recurrence)
        
        assert "None" in section
        assert "False" in section
        assert "One-time event - evaluate based on importance" in section

    def test_build_processing_history_section(self):
        """Test processing history section building."""
        processing = {
            'status': 'completed',
            'last_processed': '2024-01-14T10:00:00Z',
            'days_since_last_processed': 1
        }
        
        section = AIEvaluatorPrompts._build_processing_history_section(processing)
        
        assert "📚 PROCESSING HISTORY:" in section
        assert "completed" in section
        assert "2024-01-14T10:00:00Z" in section
        assert "1" in section
        assert "Not recently processed - may need attention" in section

    def test_build_processing_history_section_recent(self):
        """Test processing history section for recently processed event."""
        processing = {
            'status': 'completed',
            'last_processed': '2024-01-15T08:00:00Z',
            'days_since_last_processed': 0.1
        }
        
        section = AIEvaluatorPrompts._build_processing_history_section(processing)
        
        assert "Recently handled - may not need re-processing" in section

    def test_build_processing_history_section_never_processed(self):
        """Test processing history section for never processed event."""
        processing = {
            'status': 'pending',
            'last_processed': None,
            'days_since_last_processed': None
        }
        
        section = AIEvaluatorPrompts._build_processing_history_section(processing)
        
        assert "Never" in section
        assert "N/A" in section

    def test_build_evaluation_guidance(self):
        """Test evaluation guidance section building."""
        guidance = AIEvaluatorPrompts._build_evaluation_guidance()
        
        assert "🎯 EVALUATION GUIDANCE:" in guidance
        assert "🚨 **CRITICAL DECISION FACTORS**:" in guidance
        assert "💡 **EVALUATION CRITERIA**:" in guidance
        assert "🔄 **RECURRENCE LOGIC**:" in guidance
        assert "⚖️ **DECISION WEIGHTING**:" in guidance

    def test_build_response_format_section(self):
        """Test response format section building."""
        format_section = AIEvaluatorPrompts._build_response_format_section()
        
        assert "📋 RESPONSE FORMAT:" in format_section
        assert "should_process" in format_section
        assert "reason" in format_section
        assert "confidence" in format_section
        assert "suggested_actions" in format_section
        assert "event_type_analysis" in format_section
        assert "priority_score" in format_section
        assert "processing_urgency" in format_section

    def test_build_professional_guidelines(self):
        """Test professional guidelines section building."""
        guidelines = AIEvaluatorPrompts._build_professional_guidelines()
        
        assert "🎯 **PROFESSIONAL EVALUATION GUIDELINES**:" in guidelines
        assert "🚨 **CRITICAL RULES**:" in guidelines
        assert "💡 **EVALUATION QUALITY**:" in guidelines
        assert "🔄 **DECISION CONSISTENCY**:" in guidelines

    def test_prompt_consistency_across_methods(self):
        """Test that all prompt building methods maintain consistent structure."""
        # Test evaluation prompt
        eval_prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Test recurrence prompt
        recur_prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt("Test Event", None)
        
        # Both should have professional structure
        for prompt in [eval_prompt, recur_prompt]:
            assert "🎯" in prompt  # Should have emoji headers
            assert "📅" in prompt  # Should have time information
            assert "📋" in prompt  # Should have structured sections
            assert "🚨" in prompt  # Should have critical rules
            assert "💡" in prompt  # Should have guidance

    def test_error_handling_in_prompt_creation(self):
        """Test error handling in prompt creation methods."""
        # Test with invalid context
        invalid_context = {"invalid": "data"}
        
        # Should not raise exception, should handle gracefully
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(invalid_context)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_prompt_length_and_completeness(self):
        """Test that prompts are comprehensive and complete."""
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Should be substantial in length
        assert len(prompt) > 1000
        
        # Should contain all major sections
        sections = [
            "🎯 AI CALENDAR EVENT EVALUATOR",
            "📋 EVENT DETAILS:",
            "⏰ TIMING ANALYSIS:",
            "🔄 RECURRENCE ANALYSIS:",
            "📚 PROCESSING HISTORY:",
            "🎯 EVALUATION GUIDANCE:",
            "📋 RESPONSE FORMAT:",
            "🎯 **PROFESSIONAL EVALUATION GUIDELINES**:"
        ]
        
        for section in sections:
            assert section in prompt, f"Missing section: {section}"

    def test_recurrence_prompt_time_calculation(self):
        """Test time calculation in recurrence analysis prompt."""
        last_processed = datetime(2024, 1, 14, 10, 0, 0)
        current_time = datetime(2024, 1, 15, 10, 0, 0)
        
        with patch('personal_assistant.prompts.ai_evaluator_prompts.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = current_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            prompt = AIEvaluatorPrompts.create_recurrence_analysis_prompt("Test Event", last_processed)
            
            # Should calculate time difference correctly
            assert "24.0 hours" in prompt  # 24 hours difference

    def test_prompt_encoding_and_special_characters(self):
        """Test that prompts handle special characters correctly."""
        special_context = self.sample_ai_context.copy()
        special_context['event']['title'] = "Meeting with José & María (Project Alpha-Beta)"
        special_context['event']['description'] = "Discuss project details & requirements (50% complete)"
        
        prompt = AIEvaluatorPrompts.create_evaluation_prompt(special_context)
        
        # Should handle special characters correctly
        assert "José & María" in prompt
        assert "Alpha-Beta" in prompt
        assert "50% complete" in prompt
        assert "&" in prompt
        assert "(" in prompt
        assert ")" in prompt
