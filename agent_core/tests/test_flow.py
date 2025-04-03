from agent_core.llm.gemini import GeminiLLM
from agent_core.tools import create_tool_registry
from agent_core.core import AgentCore
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Create tool registry
tools = create_tool_registry()
print("Registered tools:", tools.tools.keys())
print("Tool categories:", tools._categories)

# Initialize Gemini LLM with API key
llm = GeminiLLM(api_key=api_key, model="gemini-1.5-pro")

# Initialize core with tools and LLM
core = AgentCore(tools, llm)


async def test():
    user_input = "what is the next event on my calendar?"
    user_id = "+1234567890"
    response = await core.run(user_input, user_id)
    print("Final response:", response)

if __name__ == "__main__":
    asyncio.run(test())
