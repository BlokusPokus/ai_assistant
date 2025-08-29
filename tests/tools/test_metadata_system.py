"""
Test the Tool Metadata System

This module tests the enhanced metadata system for tools.
"""

import pytest
import sys
import os
from datetime import datetime

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_assistant.tools.metadata.tool_metadata import (
    ToolMetadata, ToolMetadataManager, ToolUseCase, ToolExample,
    ToolComplexity, ToolCategory
)
from personal_assistant.tools.metadata.ai_enhancements import (
    AIEnhancement, AIEnhancementManager, EnhancementType, EnhancementPriority
)


class TestToolMetadata:
    """Test the ToolMetadata class."""
    
    def test_tool_metadata_creation(self):
        """Test creating a basic ToolMetadata instance."""
        metadata = ToolMetadata(
            tool_name="test_tool",
            description="A test tool for testing",
            category=ToolCategory.PRODUCTIVITY,
            complexity=ToolComplexity.SIMPLE
        )
        
        assert metadata.tool_name == "test_tool"
        assert metadata.description == "A test tool for testing"
        assert metadata.category == ToolCategory.PRODUCTIVITY
        assert metadata.complexity == ToolComplexity.SIMPLE
        assert metadata.tool_version == "1.0.0"
        assert metadata.isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.updated_at, datetime)
    
    def test_tool_metadata_with_use_cases(self):
        """Test ToolMetadata with use cases."""
        use_case = ToolUseCase(
            name="Basic Usage",
            description="Basic usage of the tool",
            example_request="Use the test tool",
            example_parameters={"param1": "value1"},
            expected_outcome="Tool executes successfully",
            success_indicators=["success"],
            failure_modes=["error"],
            prerequisites=["setup"]
        )
        
        metadata = ToolMetadata(
            tool_name="test_tool",
            use_cases=[use_case]
        )
        
        assert len(metadata.use_cases) == 1
        assert metadata.use_cases[0].name == "Basic Usage"
        assert metadata.use_cases[0].prerequisites == ["setup"]
    
    def test_tool_metadata_with_examples(self):
        """Test ToolMetadata with examples."""
        example = ToolExample(
            description="A test example",
            user_request="Test the tool",
            parameters={"param1": "value1"},
            expected_result="Success",
            notes="This is a test"
        )
        
        metadata = ToolMetadata(
            tool_name="test_tool",
            examples=[example]
        )
        
        assert len(metadata.examples) == 1
        assert metadata.examples[0].description == "A test example"
        assert metadata.examples[0].notes == "This is a test"
    
    def test_tool_metadata_to_dict(self):
        """Test converting ToolMetadata to dictionary."""
        metadata = ToolMetadata(
            tool_name="test_tool",
            description="Test description",
            category=ToolCategory.COMMUNICATION,
            complexity=ToolComplexity.MODERATE
        )
        
        data = metadata.to_dict()
        
        assert data["tool_name"] == "test_tool"
        assert data["description"] == "Test description"
        assert data["category"] == "communication"
        assert data["complexity"] == "moderate"
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_tool_metadata_to_json(self):
        """Test converting ToolMetadata to JSON."""
        metadata = ToolMetadata(
            tool_name="test_tool",
            description="Test description"
        )
        
        json_str = metadata.to_json()
        
        assert isinstance(json_str, str)
        assert "test_tool" in json_str
        assert "Test description" in json_str
    
    def test_tool_metadata_update(self):
        """Test updating ToolMetadata."""
        metadata = ToolMetadata(
            tool_name="test_tool",
            description="Original description"
        )
        
        original_updated = metadata.updated_at
        
        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        metadata.update_metadata(description="Updated description")
        
        assert metadata.description == "Updated description"
        assert metadata.updated_at > original_updated
    
    def test_tool_metadata_add_use_case(self):
        """Test adding use cases to ToolMetadata."""
        metadata = ToolMetadata(tool_name="test_tool")
        
        use_case = ToolUseCase(
            name="New Use Case",
            description="A new use case",
            example_request="Use the tool",
            example_parameters={},
            expected_outcome="Success",
            success_indicators=["success"],
            failure_modes=["failure"]
        )
        
        metadata.add_use_case(use_case)
        
        assert len(metadata.use_cases) == 1
        assert metadata.use_cases[0].name == "New Use Case"
    
    def test_tool_metadata_add_example(self):
        """Test adding examples to ToolMetadata."""
        metadata = ToolMetadata(tool_name="test_tool")
        
        example = ToolExample(
            description="New Example",
            user_request="Test request",
            parameters={},
            expected_result="Success"
        )
        
        metadata.add_example(example)
        
        assert len(metadata.examples) == 1
        assert metadata.examples[0].description == "New Example"
    
    def test_tool_metadata_get_ai_guidance(self):
        """Test getting AI guidance from ToolMetadata."""
        metadata = ToolMetadata(
            tool_name="test_tool",
            description="Test tool",
            category=ToolCategory.PRODUCTIVITY,
            complexity=ToolComplexity.SIMPLE,
            ai_instructions="Use this tool for testing",
            parameter_guidance={"param1": "Use value1"},
            best_practices=["Test thoroughly"]
        )
        
        guidance = metadata.get_ai_guidance()
        
        assert guidance["tool_name"] == "test_tool"
        assert guidance["description"] == "Test tool"
        assert guidance["category"] == "productivity"
        assert guidance["complexity"] == "simple"
        assert guidance["ai_instructions"] == "Use this tool for testing"
        assert guidance["parameter_guidance"] == {"param1": "Use value1"}
        assert guidance["best_practices"] == ["Test thoroughly"]


class TestToolMetadataManager:
    """Test the ToolMetadataManager class."""
    
    def test_manager_initialization(self):
        """Test ToolMetadataManager initialization."""
        manager = ToolMetadataManager()
        
        assert len(manager.metadata_store) == 0
        assert len(manager.category_index) == 0
    
    def test_register_tool_metadata(self):
        """Test registering tool metadata."""
        manager = ToolMetadataManager()
        
        metadata = ToolMetadata(
            tool_name="test_tool",
            category=ToolCategory.PRODUCTIVITY
        )
        
        manager.register_tool_metadata(metadata)
        
        assert "test_tool" in manager.metadata_store
        assert ToolCategory.PRODUCTIVITY in manager.category_index
        assert "test_tool" in manager.category_index[ToolCategory.PRODUCTIVITY]
    
    def test_get_tool_metadata(self):
        """Test getting tool metadata."""
        manager = ToolMetadataManager()
        
        metadata = ToolMetadata(tool_name="test_tool")
        manager.register_tool_metadata(metadata)
        
        retrieved = manager.get_tool_metadata("test_tool")
        
        assert retrieved is not None
        assert retrieved.tool_name == "test_tool"
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        manager = ToolMetadataManager()
        
        metadata1 = ToolMetadata(
            tool_name="tool1",
            category=ToolCategory.PRODUCTIVITY
        )
        metadata2 = ToolMetadata(
            tool_name="tool2",
            category=ToolCategory.PRODUCTIVITY
        )
        metadata3 = ToolMetadata(
            tool_name="tool3",
            category=ToolCategory.COMMUNICATION
        )
        
        manager.register_tool_metadata(metadata1)
        manager.register_tool_metadata(metadata2)
        manager.register_tool_metadata(metadata3)
        
        productivity_tools = manager.get_tools_by_category(ToolCategory.PRODUCTIVITY)
        communication_tools = manager.get_tools_by_category(ToolCategory.COMMUNICATION)
        
        assert len(productivity_tools) == 2
        assert len(communication_tools) == 1
        assert "tool1" in [t.tool_name for t in productivity_tools]
        assert "tool2" in [t.tool_name for t in productivity_tools]
        assert "tool3" in [t.tool_name for t in communication_tools]
    
    def test_get_tools_by_complexity(self):
        """Test getting tools by complexity."""
        manager = ToolMetadataManager()
        
        metadata1 = ToolMetadata(
            tool_name="simple_tool",
            complexity=ToolComplexity.SIMPLE
        )
        metadata2 = ToolMetadata(
            tool_name="complex_tool",
            complexity=ToolComplexity.COMPLEX
        )
        
        manager.register_tool_metadata(metadata1)
        manager.register_tool_metadata(metadata2)
        
        simple_tools = manager.get_tools_by_complexity(ToolComplexity.SIMPLE)
        complex_tools = manager.get_tools_by_complexity(ToolComplexity.COMPLEX)
        
        assert len(simple_tools) == 1
        assert len(complex_tools) == 1
        assert simple_tools[0].tool_name == "simple_tool"
        assert complex_tools[0].tool_name == "complex_tool"
    
    def test_search_tools(self):
        """Test searching tools."""
        manager = ToolMetadataManager()
        
        metadata = ToolMetadata(
            tool_name="email_tool",
            description="Tool for sending emails"
        )
        
        manager.register_tool_metadata(metadata)
        
        # Search by tool name
        results = manager.search_tools("email")
        assert len(results) == 1
        assert results[0].tool_name == "email_tool"
        
        # Search by description
        results = manager.search_tools("sending")
        assert len(results) == 1
        assert results[0].tool_name == "email_tool"
        
        # Search with no results
        results = manager.search_tools("nonexistent")
        assert len(results) == 0
    
    def test_get_metadata_summary(self):
        """Test getting metadata summary."""
        manager = ToolMetadataManager()
        
        metadata1 = ToolMetadata(
            tool_name="tool1",
            category=ToolCategory.PRODUCTIVITY,
            complexity=ToolComplexity.SIMPLE
        )
        metadata2 = ToolMetadata(
            tool_name="tool2",
            category=ToolCategory.COMMUNICATION,
            complexity=ToolComplexity.MODERATE
        )
        
        manager.register_tool_metadata(metadata1)
        manager.register_tool_metadata(metadata2)
        
        summary = manager.get_metadata_summary()
        
        assert summary["total_tools"] == 2
        assert summary["category_distribution"]["productivity"] == 1
        assert summary["category_distribution"]["communication"] == 1
        assert summary["complexity_distribution"]["simple"] == 1
        assert summary["complexity_distribution"]["moderate"] == 1


class TestAIEnhancement:
    """Test the AIEnhancement class."""
    
    def test_ai_enhancement_creation(self):
        """Test creating a basic AIEnhancement instance."""
        enhancement = AIEnhancement(
            enhancement_id="test_enhancement",
            tool_name="test_tool",
            enhancement_type=EnhancementType.PARAMETER_SUGGESTION,
            priority=EnhancementPriority.MEDIUM
        )
        
        assert enhancement.enhancement_id == "test_enhancement"
        assert enhancement.tool_name == "test_tool"
        assert enhancement.enhancement_type == EnhancementType.PARAMETER_SUGGESTION
        assert enhancement.priority == EnhancementPriority.MEDIUM
        assert enhancement.is_active is True
    
    def test_ai_enhancement_to_dict(self):
        """Test converting AIEnhancement to dictionary."""
        enhancement = AIEnhancement(
            enhancement_id="test_enhancement",
            tool_name="test_tool",
            enhancement_type=EnhancementType.INTENT_RECOGNITION,
            priority=EnhancementPriority.HIGH,
            title="Test Enhancement",
            description="A test enhancement"
        )
        
        data = enhancement.to_dict()
        
        assert data["enhancement_id"] == "test_enhancement"
        assert data["tool_name"] == "test_tool"
        assert data["enhancement_type"] == "intent_recognition"
        assert data["priority"] == "high"
        assert data["title"] == "Test Enhancement"
        assert data["description"] == "A test enhancement"
    
    def test_ai_enhancement_update(self):
        """Test updating AIEnhancement."""
        enhancement = AIEnhancement(
            enhancement_id="test_enhancement",
            tool_name="test_tool",
            enhancement_type=EnhancementType.PARAMETER_SUGGESTION
        )
        
        original_updated = enhancement.updated_at
        
        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        enhancement.update_enhancement(title="Updated Title")
        
        assert enhancement.title == "Updated Title"
        assert enhancement.updated_at > original_updated
    
    def test_ai_enhancement_get_ai_guidance(self):
        """Test getting AI guidance from AIEnhancement."""
        enhancement = AIEnhancement(
            enhancement_id="test_enhancement",
            tool_name="test_tool",
            enhancement_type=EnhancementType.WORKFLOW_SUGGESTION,
            priority=EnhancementPriority.CRITICAL,
            title="Workflow Enhancement",
            description="Suggests workflows",
            ai_instructions="Use this enhancement for workflow suggestions",
            examples=[{"example": "test"}],
            trigger_conditions=["User requests complex task"],
            success_criteria=["AI suggests workflow"]
        )
        
        guidance = enhancement.get_ai_guidance()
        
        assert guidance["enhancement_id"] == "test_enhancement"
        assert guidance["tool_name"] == "test_tool"
        assert guidance["type"] == "workflow_suggestion"
        assert guidance["priority"] == "critical"
        assert guidance["title"] == "Workflow Enhancement"
        assert guidance["ai_instructions"] == "Use this enhancement for workflow suggestions"


class TestAIEnhancementManager:
    """Test the AIEnhancementManager class."""
    
    def test_manager_initialization(self):
        """Test AIEnhancementManager initialization."""
        manager = AIEnhancementManager()
        
        assert len(manager.enhancements) == 0
        assert len(manager.tool_enhancements) == 0
        assert len(manager.type_enhancements) == 0
    
    def test_register_enhancement(self):
        """Test registering an enhancement."""
        manager = AIEnhancementManager()
        
        enhancement = AIEnhancement(
            enhancement_id="test_enhancement",
            tool_name="test_tool",
            enhancement_type=EnhancementType.PARAMETER_SUGGESTION
        )
        
        manager.register_enhancement(enhancement)
        
        assert "test_enhancement" in manager.enhancements
        assert "test_tool" in manager.tool_enhancements
        assert EnhancementType.PARAMETER_SUGGESTION in manager.type_enhancements
    
    def test_get_tool_enhancements(self):
        """Test getting enhancements for a tool."""
        manager = AIEnhancementManager()
        
        enhancement1 = AIEnhancement(
            enhancement_id="enh1",
            tool_name="test_tool",
            enhancement_type=EnhancementType.PARAMETER_SUGGESTION
        )
        enhancement2 = AIEnhancement(
            enhancement_id="enh2",
            tool_name="test_tool",
            enhancement_type=EnhancementType.INTENT_RECOGNITION
        )
        
        manager.register_enhancement(enhancement1)
        manager.register_enhancement(enhancement2)
        
        tool_enhancements = manager.get_tool_enhancements("test_tool")
        
        assert len(tool_enhancements) == 2
        assert "enh1" in [e.enhancement_id for e in tool_enhancements]
        assert "enh2" in [e.enhancement_id for e in tool_enhancements]
    
    def test_create_parameter_suggestion_enhancement(self):
        """Test creating a parameter suggestion enhancement."""
        manager = AIEnhancementManager()
        
        examples = [
            {"user_request": "Send email", "suggested_value": "user@example.com"}
        ]
        
        enhancement = manager.create_parameter_suggestion_enhancement(
            tool_name="email_tool",
            parameter_name="recipient",
            suggestion_logic="Extract email from user request",
            examples=examples
        )
        
        assert enhancement.enhancement_id == "email_tool_recipient_param_suggestion"
        assert enhancement.tool_name == "email_tool"
        assert enhancement.enhancement_type == EnhancementType.PARAMETER_SUGGESTION
        assert enhancement.title == "Smart recipient suggestions for email_tool"
        assert len(enhancement.examples) == 1
    
    def test_create_intent_recognition_enhancement(self):
        """Test creating an intent recognition enhancement."""
        manager = AIEnhancementManager()
        
        examples = [
            {"user_request": "Send an email", "detected_intent": "email_sending"}
        ]
        
        enhancement = manager.create_intent_recognition_enhancement(
            tool_name="email_tool",
            intent_patterns=["send email", "compose email", "write email"],
            recognition_logic="Look for email-related verbs",
            examples=examples
        )
        
        assert enhancement.enhancement_id == "email_tool_intent_recognition"
        assert enhancement.tool_name == "email_tool"
        assert enhancement.enhancement_type == EnhancementType.INTENT_RECOGNITION
        assert enhancement.priority == EnhancementPriority.HIGH
        assert "send email" in enhancement.trigger_conditions[1]


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
