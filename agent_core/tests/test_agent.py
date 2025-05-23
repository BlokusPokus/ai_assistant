# from agent_core.memory.client import MockVectorDBClient
# from agent_core.memory.memory import VectorMemory
from agent_core.tools import ToolRegistry, EmailTool
from agent_core.llm.gemini import GeminiLLM
from agent_core.config import GEMINI_API_KEY
from agent_core.core import AgentCore
import sys
import asyncio
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = "/Users/ianleblanc/Desktop/personal_assistant"
if project_root not in sys.path:
    sys.path.append(project_root)


async def main():
    # Load environment variables
    load_dotenv()

    # Initialize components
    # memory = VectorMemory(MockVectorDBClient())
    tool_registry = ToolRegistry()

    # Create an instance of EmailTool
    email_tool = EmailTool()

    # Register the EmailTool instance
    tool_registry.register(email_tool)

    # Create LLM client
    llm_client = GeminiLLM(api_key=GEMINI_API_KEY)

    # Create agent
    agent = AgentCore(
        # memory=memory,
        tools=tool_registry,
        llm=llm_client
    )

    # Test the agent with email-related queries
    test_queries = [
        "Can you read my most recent emails?",
        "Show me my last 3 emails",
        "How many new messages did I receive yesterday?"
    ]

    for query in test_queries:
        print(f"\nUser Query: {query}")
        print("-" * 50)
        response = await agent.run(query)  # Await the run method
        print(f"Agent Response: {response}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the main coroutine
