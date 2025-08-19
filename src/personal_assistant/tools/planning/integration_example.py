"""
Example integration of the LLM Planner Tool with the prompt builder and tool registry.
This shows how to set up and use the planning tool in your system.
"""

from .llm_planner import LLMPlannerTool


def integrate_planner_with_prompt_builder():
    """
    Example of how to integrate the LLM planner with your prompt builder.
    """

    # 1. Initialize the planner tool
    planner = LLMPlannerTool()

    # 2. Set the LLM client (you'll need to provide your actual LLM client)
    # planner.set_llm_client(your_llm_client)

    # 3. Add to your tool registry
    # tool_registry.register_tool(planner.planning_tool)

    return planner


def integrate_planner_with_tool_registry(tool_registry):
    """
    Example of how to integrate the planner with your existing tool registry.

    Args:
        tool_registry: Your existing tool registry instance
    """

    # Create planner instance
    planner = LLMPlannerTool()

    # Add the planning tool to your registry
    for tool in planner:
        tool_registry.register_tool(tool)

    return planner


def use_planner_in_prompt_builder(prompt_builder, tool_registry):
    """
    Example of how to use the planner in your prompt builder.

    Args:
        prompt_builder: Your prompt builder instance
        tool_registry: Your tool registry instance
    """

    # Add planning context to your prompt builder
    planning_context = """
🎯 TASK PLANNING RECOMMENDATION:

For complex tasks, consider using the `create_intelligent_plan` tool to:
• Break down requests into clear, manageable steps
• Identify the most appropriate tools for each step
• Get context-specific guidance for tool usage
• Create a structured approach to completion
• Receive ADHD-friendly execution guidance

This will help ensure efficient and effective task completion.
"""

    # You can add this to your prompt builder's build method
    return planning_context


# Example usage in your main application:
"""
# In your main.py or wherever you initialize tools:

from .tools.planning import LLMPlannerTool

# Initialize the planner
planner = LLMPlannerTool()

# Set your LLM client
planner.set_llm_client(your_llm_client)

# Add to tool registry
for tool in planner:
    tool_registry.register_tool(tool)

# Now users can call:
# create_intelligent_plan(user_request="Help me organize my project notes")
"""
