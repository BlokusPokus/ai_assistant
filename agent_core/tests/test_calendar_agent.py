import asyncio
# from agent_core.memory.client import MockMemoryDBClient
# from agent_core.memory.memory import Memory
from agent_core.tools import ToolRegistry
from agent_core.tools.calendar.calendar_tool import CalendarTool
from agent_core.llm.gemini import GeminiLLM
from agent_core.config import GEMINI_API_KEY
from agent_core.core import AgentCore
from dotenv import load_dotenv


async def main():
    # Load environment variables
    load_dotenv()

    # Initialize components
    # memory = Memory(MockMemoryDBClient())
    tool_registry = ToolRegistry()

    # Register the CalendarTool
    calendar_tool = CalendarTool()
    tool_registry.register(calendar_tool)

    # Create LLM client
    llm_client = GeminiLLM(api_key=GEMINI_API_KEY)

    # Create agent
    agent = AgentCore(
        tools=tool_registry,
        llm=llm_client
    )

    # Test the agent with calendar-related queries
    test_queries = [
        "What's on my calendar for the next week?",
        "Show me my upcoming events",
        "Create a meeting with John tomorrow at 2pm for 1 hour about project planning",
        "Schedule a dentist appointment for April 5th at 9am 2025"
    ]

    for query in test_queries:
        print(f"\nUser Query: {query}")
        print("-" * 50)
        response = await agent.run(query)
        print(f"Agent Response: {response}")
        print("-" * 50)

    # Interactive mode
    print("\nInteractive Calendar Assistant Mode (type 'quit' to exit)")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ('quit', 'exit', 'bye'):
            break

        response = await agent.run(user_input)
        print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())
