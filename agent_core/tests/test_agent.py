from agent_core.memory.client import MockVectorDBClient
from agent_core.memory.memory import VectorMemory
from agent_core.tools import ToolRegistry, WeatherTool, CalculatorTool
from agent_core.llm.gemini import GeminiLLM
from agent_core.config import GEMINI_API_KEY
from agent_core.core import AgentCore
import sys

# Add the project root directory to Python path
project_root = "/Users/ianleblanc/Desktop/personal_assistant"
if project_root not in sys.path:
    sys.path.append(project_root)


def main():
    # Initialize components
    memory = VectorMemory(MockVectorDBClient())
    tool_registry = ToolRegistry()

    # Register tools from the tools package
    tool_registry.register(WeatherTool)
    tool_registry.register(CalculatorTool)

    # Create LLM client
    llm_client = GeminiLLM(api_key=GEMINI_API_KEY)

    # Create agent
    agent = AgentCore(
        memory=memory,
        tools=tool_registry,
        llm=llm_client
    )

    response = agent.run("What 2 times 15")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
