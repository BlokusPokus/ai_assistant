import asyncio
# from agent_core.memory.client import MockMemoryDBClient
# from agent_core.memory.memory import Memory
from agent_core.tools import ToolRegistry
from agent_core.tools.calendar.calendar_tool import CalendarEventsTool, CreateEventTool, GetEventDetailsTool
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

    # Register the Calendar Tools
    tool_registry.register(CalendarEventsTool())
    tool_registry.register(CreateEventTool())
    tool_registry.register(GetEventDetailsTool())

    # Create LLM client
    llm_client = GeminiLLM(api_key=GEMINI_API_KEY)

    # Create agent
    agent = AgentCore(
        tools=tool_registry,
        llm=llm_client,
        # memory=memory
    )

    # Test queries that should trigger calendar tool usage
    test_queries = [
        "What meetings do I have coming up this week?",
        "Schedule a project planning meeting tomorrow at 2pm for 1 hour",
        "Create a dentist appointment for April 5th at 9am for 45 minutes",
        "What's my schedule for tomorrow?",
        "Set up a meeting with John about quarterly review next Monday at 11am"
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"User: {query}")
        print(f"{'-'*50}")
        response = await agent.run(query)
        print(f"Agent: {response}")
        print(f"{'='*50}")

        # Add a pause to make the console output more readable
        await asyncio.sleep(1)

        # Optionally, ask user if they want to continue with the next query
        user_input = input(
            "\nPress Enter to continue to the next query, or type 'q' to quit: ")
        if user_input.lower() == 'q':
            break


if __name__ == "__main__":
    asyncio.run(main())
