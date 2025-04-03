import asyncio
from tests.mock_database import MockMemoryDBClient
from agent_core.tools import ToolRegistry
from agent_core.tools.emails.email_tool import EmailTool
from agent_core.llm.gemini import GeminiLLM
from agent_core.config import GEMINI_API_KEY
from agent_core.core import AgentCore
import os
from dotenv import load_dotenv
from memory.interface import MemoryInterface


async def main():
    # Load environment variables
    load_dotenv()

    # Initialize components
    memory = MemoryInterface(MockMemoryDBClient())
    tool_registry = ToolRegistry()

    # Register the EmailTool
    email_tool = EmailTool()
    tool_registry.register(email_tool)

    # Create LLM client
    llm_client = GeminiLLM(api_key=GEMINI_API_KEY)

    # Create agent
    agent = AgentCore(
        tools=tool_registry,
        llm=llm_client
    )

    # Test the agent with email-related queries
    test_queries = [
        "Can you read my most recent emails?",
        "Show me my last 3 emails",
        "how many new messages did i receive yesterday?"
    ]

    for query in test_queries:
        print(f"\nUser Query: {query}")
        print("-" * 50)
        response = await agent.run(query)
        print(f"Agent Response: {response}")
        print("-" * 50)

    # New test case for email tool integration
    email_query = "Read my emails"
    print(f"\nUser Query: {email_query}")
    print("-" * 50)
    email_response = await agent.run(email_query)
    print(f"Agent Response: {email_response}")
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
