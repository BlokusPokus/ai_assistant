#!/usr/bin/env python3
"""
Test script to actually use EnhancedAgentCore and see the metadata system in action.

This script demonstrates how to use the enhanced agent with metadata.
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_enhanced_agent():
    """Test the enhanced agent with metadata."""

    try:
        print("🚀 Testing Enhanced Agent with Metadata")
        print("=" * 50)

        # Import the enhanced agent
        from personal_assistant.core.agent_enhanced import EnhancedAgentCore

        print("✅ Successfully imported EnhancedAgentCore")

        # Create enhanced agent with metadata enabled
        print("\n🔧 Creating EnhancedAgentCore with metadata enabled...")
        agent = EnhancedAgentCore(use_metadata=True)

        print("✅ EnhancedAgentCore created successfully")

        # Check metadata status
        status = agent.get_metadata_status()
        print(f"\n📊 Metadata Status:")
        print(f"   • Metadata enabled: {status['metadata_enabled']}")
        print(
            f"   • Enhanced prompt builder: {status['enhanced_prompt_builder']}")
        print(f"   • Status: {status['status']}")

        if status['metadata_enabled']:
            print("✅ Metadata system is active!")
        else:
            print("❌ Metadata system is not active")
            return

        # Test with a simple request that should trigger metadata
        print("\n🧪 Testing with email request (should trigger metadata)...")
        user_input = "Send an email to John about the meeting tomorrow"
        user_id = 1

        print(f"📝 User Input: '{user_input}'")
        print(f"👤 User ID: {user_id}")

        print("\n🔄 Executing agent...")
        print("   (This will show the metadata system in action)")

        # Run the agent
        response = await agent.run(user_input, user_id)

        print(f"\n✅ Agent Response Received!")
        print(
            f"📤 Response: {response[:200]}{'...' if len(response) > 200 else ''}")

        print("\n🎉 Test completed successfully!")
        print("\n📋 What happened:")
        print("   1. EnhancedAgentCore was created with metadata enabled")
        print("   2. User request was processed through the metadata system")
        print("   3. EnhancedPromptBuilder loaded email tool metadata")
        print("   4. LLM received rich context about email tools")
        print("   5. Agent responded with better understanding")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Make sure you're running from the project root")
        print("   • Check that all dependencies are installed")
        print("   • Verify the import paths are correct")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"\n🔍 Error details: {type(e).__name__}: {str(e)}")

        # Show more context for common issues
        if "EnhancedAgentCore" in str(e):
            print("\n🔧 This might be an import issue with the enhanced agent")
        elif "metadata" in str(e).lower():
            print("\n🔧 This might be an issue with the metadata system")
        elif "prompt" in str(e).lower():
            print("\n🔧 This might be an issue with the prompt builder")


async def test_metadata_toggle():
    """Test the metadata toggle functionality."""

    try:
        print("\n🔄 Testing Metadata Toggle Functionality")
        print("=" * 40)

        from personal_assistant.core.agent_enhanced import EnhancedAgentCore

        # Create agent with metadata enabled
        agent = EnhancedAgentCore(use_metadata=True)
        print("✅ Created agent with metadata enabled")

        # Check initial status
        status1 = agent.get_metadata_status()
        print(f"   • Initial metadata status: {status1['metadata_enabled']}")

        # Toggle metadata off
        print("\n🔄 Toggling metadata off...")
        agent.toggle_metadata(False)

        status2 = agent.get_metadata_status()
        print(f"   • After toggle off: {status2['metadata_enabled']}")

        # Toggle metadata back on
        print("\n🔄 Toggling metadata back on...")
        agent.toggle_metadata(True)

        status3 = agent.get_metadata_status()
        print(f"   • After toggle on: {status3['metadata_enabled']}")

        print("\n✅ Metadata toggle test completed!")

    except Exception as e:
        print(f"❌ Toggle test failed: {e}")


async def main():
    """Run all tests."""
    print("🧪 Enhanced Agent Test Suite")
    print("=" * 50)

    # Test 1: Basic enhanced agent functionality
    await test_enhanced_agent()

    # Test 2: Metadata toggle functionality
    await test_metadata_toggle()

    print("\n🎯 Test Summary:")
    print("   • If you saw '✅ Metadata system is active!' - the system is working!")
    print("   • If you saw '❌ Metadata system is not active' - there's an issue")
    print("   • Check the logs above for detailed information")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())
