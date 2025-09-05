#!/usr/bin/env python3
"""
Debug entry point for the personal assistant agent.
This script properly sets up the Python path for debugging.
"""
import asyncio
import os
import sys

# Add src to Python path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run the agent
from personal_assistant.core.agent import AgentCore

async def debug_agent():
    """Debug function for the agent."""
    # Initialize the agent
    print("Initializing agent for debugging...")
    agent = AgentCore()
    print("Agent initialized successfully!")
    
    # Test with a simple message
    test_message = "Hello, how are you?"
    user_id = 1  # Test user ID
    
    print(f"Sending message: {test_message}")
    response = await agent.run(test_message, user_id)
    print(f"Agent response: {response}")
    
    # Add a breakpoint here for debugging
    breakpoint()  # This will pause execution for debugging

if __name__ == "__main__":
    asyncio.run(debug_agent())

