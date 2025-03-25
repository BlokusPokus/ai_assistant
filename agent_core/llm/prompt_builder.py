"""
Prompt construction utilities.

📁 llm/prompt_builder.py
Builds agent prompts from memory, recent actions, tools, and user input. 
Injects into Gemini calls.
"""


def build_prompt(user_input: str, memory_context: list, history: list) -> str:
    """
    Builds the final prompt for the LLM.

    Args:
        user_input (str): User message
        memory_context (list): List of memory results
        history (list): Previous tool calls and results

    Returns:
        str: LLM-ready prompt
    """
    pass
