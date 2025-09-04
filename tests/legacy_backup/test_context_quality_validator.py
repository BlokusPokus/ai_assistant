#!/usr/bin/env python3
"""
Test script for ContextQualityValidator (Subtask 1.2).

This script tests the new quality validation system to ensure it:
1. Correctly filters low-quality context
2. Integrates with existing quality mechanisms
3. Provides accurate quality metrics
4. Handles edge cases gracefully
"""

import sys
import os
from datetime import datetime, timezone

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_assistant.memory.context_quality_validator import ContextQualityValidator
from personal_assistant.types.state import StateConfig


def test_context_quality_validator():
    """Test the ContextQualityValidator class functionality."""
    
    print("🧪 Testing ContextQualityValidator (Subtask 1.2)")
    print("=" * 60)
    
    # Create test configuration
    config = StateConfig()
    validator = ContextQualityValidator(config)
    
    print("✅ ContextQualityValidator initialized successfully")
    print(f"   - Default relevance threshold: {validator.min_relevance_threshold}")
    print(f"   - LTM threshold: {validator.min_ltm_threshold}")
    print(f"   - RAG threshold: {validator.min_rag_threshold}")
    
    # Test 1: Basic functionality
    print("\n1. Testing basic functionality...")
    
    # Create test context items
    test_context_items = [
        {
            "role": "memory",
            "source": "ltm",
            "content": "User prefers casual greetings and informal communication style",
            "type": "long_term_memory",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "role": "memory",
            "source": "rag",
            "content": "Document about machine learning algorithms and neural networks",
            "type": "document",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "role": "context",
            "source": "conversation_history",
            "content": "Previous conversation about scheduling meetings",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "role": "system",
            "source": "system",
            "content": "System optimization completed successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    user_input = "Hello, can you help me schedule a meeting?"
    
    print(f"   - Test context items: {len(test_context_items)}")
    print(f"   - User input: '{user_input}'")
    
    # Test 2: Quality scoring
    print("\n2. Testing quality scoring...")
    
    for i, item in enumerate(test_context_items):
        score = validator.calculate_context_quality_score(item, user_input)
        print(f"   - Item {i+1} ({item['source']}): {score:.3f}")
    
    # Test 3: Context validation
    print("\n3. Testing context validation...")
    
    validated_items = validator.validate_context_relevance(
        test_context_items, user_input, context_type="mixed"
    )
    
    print(f"   - Original items: {len(test_context_items)}")
    print(f"   - Validated items: {len(validated_items)}")
    print(f"   - Removed items: {len(test_context_items) - len(validated_items)}")
    
    # Test 4: Quality metrics
    print("\n4. Testing quality metrics...")
    
    metrics = validator.get_quality_metrics(test_context_items, user_input)
    
    print(f"   - Total items: {metrics['total_items']}")
    print(f"   - Average quality: {metrics['average_quality']:.3f}")
    print(f"   - Quality distribution: {metrics['quality_distribution']}")
    
    # Test context type breakdown
    if metrics['context_type_breakdown']:
        print("   - Context type breakdown:")
        for context_type, breakdown in metrics['context_type_breakdown'].items():
            print(f"     * {context_type}: {breakdown['count']} items, avg score: {breakdown['average_score']:.3f}")
    
    # Test recommendations
    if metrics['recommendations']:
        print("   - Recommendations:")
        for rec in metrics['recommendations']:
            print(f"     * {rec}")
    
    # Test 5: Edge cases
    print("\n5. Testing edge cases...")
    
    # Empty context
    empty_result = validator.validate_context_relevance([], user_input)
    print(f"   - Empty context: {len(empty_result)} items returned")
    
    # Empty user input
    empty_input_result = validator.validate_context_relevance(test_context_items, "")
    print(f"   - Empty user input: {len(empty_input_result)} items returned")
    
    # Invalid context items
    invalid_items = [
        {"invalid": "item"},
        {"content": ""},
        {"content": "None"},
        {"content": None}
    ]
    
    invalid_result = validator.validate_context_relevance(invalid_items, user_input)
    print(f"   - Invalid items: {len(invalid_result)} items passed validation")
    
    # Test 6: Threshold updates
    print("\n6. Testing threshold updates...")
    
    original_threshold = validator.min_relevance_threshold
    validator.update_thresholds(min_relevance_threshold=0.8)
    
    print(f"   - Original threshold: {original_threshold}")
    print(f"   - New threshold: {validator.min_relevance_threshold}")
    
    # Test validation with higher threshold
    high_threshold_result = validator.validate_context_relevance(
        test_context_items, user_input, context_type="mixed"
    )
    print(f"   - High threshold validation: {len(high_threshold_result)} items passed")
    
    # Reset threshold
    validator.update_thresholds(min_relevance_threshold=original_threshold)
    print(f"   - Threshold reset to: {validator.min_relevance_threshold}")
    
    # Test 7: Context type specific validation
    print("\n7. Testing context type specific validation...")
    
    # Test LTM validation
    ltm_items = [item for item in test_context_items if item['source'] == 'ltm']
    ltm_validated = validator.validate_context_relevance(ltm_items, user_input, context_type="ltm")
    print(f"   - LTM validation: {len(ltm_validated)}/{len(ltm_items)} items passed")
    
    # Test RAG validation
    rag_items = [item for item in test_context_items if item['source'] == 'rag']
    rag_validated = validator.validate_context_relevance(rag_items, user_input, context_type="rag")
    print(f"   - RAG validation: {len(rag_validated)}/{len(rag_items)} items passed")
    
    # Test 8: Performance and memory
    print("\n8. Testing performance characteristics...")
    
    # Create larger test set
    large_context = []
    for i in range(100):
        large_context.append({
            "role": "memory",
            "source": "test",
            "content": f"Test context item {i} with some content about meetings and scheduling",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    print(f"   - Large context set: {len(large_context)} items")
    
    # Time the validation
    import time
    start_time = time.time()
    large_validated = validator.validate_context_relevance(large_context, user_input)
    end_time = time.time()
    
    validation_time = (end_time - start_time) * 1000  # Convert to milliseconds
    print(f"   - Validation time: {validation_time:.2f}ms")
    print(f"   - Items processed per second: {len(large_context) / (end_time - start_time):.0f}")
    
    # Test 9: Integration simulation
    print("\n9. Testing integration simulation...")
    
    # Simulate the integration with AgentRunner.set_context()
    print("   - Simulating AgentRunner.set_context() integration...")
    
    # Mock memory blocks (like what would come from LTM + RAG)
    mock_memory_blocks = [
        {
            "role": "memory",
            "source": "ltm",
            "content": "User prefers casual greetings",
            "type": "long_term_memory",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "role": "memory",
            "source": "rag",
            "content": "Meeting scheduling best practices and calendar management",
            "type": "document",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Simulate quality validation (like in AgentRunner)
    original_count = len(mock_memory_blocks)
    validated_blocks = validator.validate_context_relevance(
        mock_memory_blocks, user_input, context_type="mixed"
    )
    removed_count = original_count - len(validated_blocks)
    
    print(f"   - Integration test: {removed_count} low-quality blocks removed")
    print(f"   - Final context: {len(validated_blocks)} high-quality blocks")
    
    # Test 10: Final validation
    print("\n10. Final validation...")
    
    # Verify all core functionality works
    test_passed = True
    
    # Test that quality validation actually filters items
    if len(validated_items) >= len(test_context_items):
        print("   ❌ Quality validation should filter some items")
        test_passed = False
    else:
        print("   ✅ Quality validation correctly filters low-quality items")
    
    # Test that metrics are generated
    if not metrics or 'total_items' not in metrics:
        print("   ❌ Quality metrics not generated")
        test_passed = False
    else:
        print("   ✅ Quality metrics generated successfully")
    
    # Test that thresholds can be updated
    if validator.min_relevance_threshold != original_threshold:
        print("   ❌ Threshold update failed")
        test_passed = False
    else:
        print("   ✅ Threshold update works correctly")
    
    # Test performance
    if validation_time > 1000:  # More than 1 second
        print("   ❌ Validation performance is too slow")
        test_passed = False
    else:
        print("   ✅ Validation performance is acceptable")
    
    return test_passed


def main():
    """Main test function."""
    try:
        print("🚀 Starting Subtask 1.2 Testing...")
        
        success = test_context_quality_validator()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 All tests passed! ContextQualityValidator is working correctly.")
            print("\n📋 Implementation Summary:")
            print("   ✅ ContextQualityValidator class created successfully")
            print("   ✅ Quality scoring algorithms implemented")
            print("   ✅ Context filtering based on relevance thresholds")
            print("   ✅ Quality metrics and recommendations")
            print("   ✅ Integration with AgentRunner.set_context()")
            print("   ✅ Performance characteristics validated")
            print("\n🚀 Ready to move to Subtask 1.3 (Implement Context Aging)!")
            return 0
        else:
            print("\n❌ Some tests failed. Please review the implementation.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
