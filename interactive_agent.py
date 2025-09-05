#!/usr/bin/env python3
"""
Interactive Personal Assistant Agent
Run this script to interact with the agent directly in the terminal.
"""
import asyncio
import os
import sys

# Add src to Python path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from personal_assistant.core.agent import AgentCore

async def interactive_agent():
    """Interactive agent session."""
    print("🤖 Personal Assistant Agent - Interactive Mode")
    print("=" * 50)
    
    # Initialize the agent
    print("Initializing agent...")
    agent = AgentCore()
    print("✅ Agent initialized successfully!")
    print()
    
    # Get user ID (you can change this)
    user_id = 1
    
    print(f"Ready to chat! (User ID: {user_id})")
    print("Type 'quit', 'exit', or 'q' to stop")
    print("Type 'clear' to clear conversation history")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Check for clear command
            if user_input.lower() == 'clear':
                print("🧹 Conversation cleared!")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Process the message
            print("🤖 Assistant: ", end="", flush=True)
            response = await agent.run(user_input, user_id)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again...")

if __name__ == "__main__":
    asyncio.run(interactive_agent())
