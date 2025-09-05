"""
Example usage of the enhanced LLM Planner Tool with automatic tool guidelines.
This demonstrates how the planner automatically includes relevant tool guidelines.
"""


from .llm_planner import LLMPlannerTool


async def demonstrate_enhanced_planning():
    """Demonstrate how the enhanced planner automatically includes tool guidelines."""

    # Initialize the planner
    planner = LLMPlannerTool(guidelines_path="src/personal_assistant/tools")

    # Example 1: Planning a note creation task
    print("🎯 Example 1: Planning Note Creation")
    print("=" * 50)

    note_plan = await planner.create_intelligent_plan(
        user_request="Help me create a meeting note template for my development team",
        planning_style="adhd_friendly",
        include_guidelines=True,  # This will automatically include Notion notes guidelines
    )

    print(note_plan)
    print("\n" + "=" * 50 + "\n")

    # Example 2: Planning a search task
    print("🔍 Example 2: Planning Information Search")
    print("=" * 50)

    search_plan = await planner.create_intelligent_plan(
        user_request="I need to find information about API design patterns in my codebase",
        planning_style="detailed",
        include_guidelines=True,  # This will include search tool guidelines
    )

    print(search_plan)
    print("\n" + "=" * 50 + "\n")

    # Example 3: Planning without guidelines (for comparison)
    print("📝 Example 3: Planning Without Guidelines")
    print("=" * 50)

    basic_plan = await planner.create_intelligent_plan(
        user_request="Help me organize my project files",
        planning_style="concise",
        include_guidelines=False,  # This will NOT include tool guidelines
    )

    print(basic_plan)


def show_guideline_integration():
    """Show how the planner integrates tool guidelines."""

    planner = LLMPlannerTool(guidelines_path="src/personal_assistant/tools")

    # Show what guidelines are available
    print("📚 Available Tool Guidelines:")
    print("=" * 30)

    guidelines = planner._load_tool_guidelines()
    for tool_name, content in guidelines.items():
        print(f"• {tool_name}: {len(content)} characters")

    print(f"\nTotal guidelines loaded: {len(guidelines)}")

    # Show tool detection examples (fallback method)
    print("\n🔍 Tool Detection Examples (Fallback Method):")
    print("=" * 50)

    test_requests = [
        "Create a meeting note about our sprint planning",
        "Search for authentication code in my project",
        "Edit the main configuration file",
        "Run the test suite for my application",
    ]

    for request in test_requests:
        relevant_tools = planner._identify_relevant_tools_fallback(request)
        print(f"Request: '{request}'")
        print(f"  → Relevant tools (fallback): {relevant_tools}")
        print()


async def demonstrate_llm_tool_identification():
    """Demonstrate the new LLM-driven tool identification."""

    print("🤖 LLM-Driven Tool Identification Demo")
    print("=" * 50)

    # Initialize planner with mock LLM client for demo
    planner = LLMPlannerTool(guidelines_path="src/personal_assistant/tools")

    # Mock LLM client that simulates tool identification
    class MockLLMClient:
        async def generate(self, prompt, max_tokens, temperature):
            class MockResponse:
                def __init__(self, content):
                    self.content = content

            return MockResponse("notion_notes, codebase_search")

    planner.set_llm_client(MockLLMClient())

    # Test LLM tool identification
    test_request = (
        "I need to research API design patterns and create notes about my findings"
    )

    print(f"User Request: '{test_request}'")
    print("\n🤖 LLM Analysis:")
    print("The LLM will analyze this request and identify relevant tools...")

    try:
        relevant_tools = await planner._identify_relevant_tools_llm(test_request)
        print(f"✅ LLM identified tools: {relevant_tools}")

        # Show what guidelines would be included
        if relevant_tools:
            print("\n📚 Guidelines that would be included:")
            guidelines = planner._extract_relevant_guidelines(
                relevant_tools, max_length=200
            )
            print(guidelines[:500] + "..." if len(guidelines) > 500 else guidelines)

    except Exception as e:
        print(f"❌ LLM tool identification failed: {e}")
        print("This would fall back to pattern-based detection")


def show_tool_identification_prompt():
    """Show what the tool identification prompt looks like."""

    planner = LLMPlannerTool(guidelines_path="src/personal_assistant/tools")

    print("📝 Tool Identification Prompt Example:")
    print("=" * 50)

    prompt = planner._build_tool_identification_prompt(
        "Help me create a meeting note template for my development team"
    )

    print(prompt)


if __name__ == "__main__":
    # Show available guidelines
    show_guideline_integration()

    # Show tool identification prompt
    show_tool_identification_prompt()

    # Run examples (uncomment when you have an LLM client set up)
    # asyncio.run(demonstrate_enhanced_planning())
    # asyncio.run(demonstrate_llm_tool_identification())
